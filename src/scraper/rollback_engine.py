"""
rollback_engine.py - Selenium rollback scraper.

Uses Selenium Manager first, webdriver-manager second, and returns the same
schema as Puppeteer.
"""
from __future__ import annotations

import asyncio
import random
import time
from pathlib import Path
from typing import Any

from src.scraper.normalizer import normalize_products
from src.scraper.selenium_driver import create_chrome_driver, safe_quit_driver
from src.scraper.url_builder import build_tokopedia_search_urls_for_variant
from src.server.progress import update_progress
from src.utils.debug import get_debug_dir, save_debug_state_sync, save_text_debug, save_zero_raw_debug
from src.utils.logger import log


DEBUG_DIR = Path("data/debug")


class RollbackEngine:
    name = "rollback"

    def __init__(self, search_id: str):
        self.search_id = search_id

    async def scrape(
        self,
        query: str,
        raw_target: int,
        eta_calc,
        query_variants: list[str] | None = None,
        min_price: int | None = None,
        max_price: int | None = None,
    ) -> tuple[bool, list[dict[str, Any]], str]:
        """Run blocking Selenium work in a thread so FastAPI stays responsive."""
        return await asyncio.to_thread(
            self._scrape_sync,
            query,
            raw_target,
            eta_calc,
            query_variants or [query],
            min_price,
            max_price,
        )

    def _scrape_sync(
        self,
        query: str,
        raw_target: int,
        eta_calc,
        query_variants: list[str],
        min_price: int | None,
        max_price: int | None,
    ) -> tuple[bool, list[dict[str, Any]], str]:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.ui import WebDriverWait

        update_progress(
            self.search_id,
            active_engine=self.name,
            stage="rollback_browser_starting",
            percent=48,
            message="Menjalankan Rollback/Selenium...",
            elapsed_seconds=eta_calc.get_elapsed(),
        )

        driver, error_msg = create_chrome_driver(self.search_id, DEBUG_DIR / self.search_id)
        if not driver:
            return False, [], f"Chrome driver bootstrap failed: {error_msg}"

        products: list[dict[str, Any]] = []
        seen_urls: set[str] = set()
        urls_tried: list[str] = []
        selector_probes: list[dict[str, Any]] = []
        errors: list[str] = []
        pages_loaded = 0

        try:
            for variant_index, variant in enumerate(query_variants):
                if len(products) >= raw_target:
                    break

                for url in build_tokopedia_search_urls_for_variant(variant, min_price, max_price):
                    if len(products) >= raw_target:
                        break
                    urls_tried.append(url)
                    update_progress(
                        self.search_id,
                        active_engine=self.name,
                        stage="rollback_opening",
                        percent=min(70, 52 + variant_index),
                        message=f"Rollback/Selenium scraping {variant}",
                        elapsed_seconds=eta_calc.get_elapsed(),
                    )

                    try:
                        driver.get(url)
                        WebDriverWait(driver, 12).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                        pages_loaded += 1
                        self._scroll_and_extract(driver, raw_target, products, seen_urls, eta_calc, variant)
                        selector_probes.append(self._selector_probe(driver))
                    except Exception as variant_exc:
                        error = f"{url}: {variant_exc}"
                        errors.append(error)
                        log(f"[{self.search_id}]", f"[ROLLBACK] Query failed {variant}: {variant_exc}", "WARN")
                        continue

            normalized = normalize_products(products, self.name)
            if normalized:
                log(f"[{self.search_id}]", f"[ROLLBACK] Extracted {len(normalized)} products", "OK")
                return True, products, ""

            debug_path = self._save_zero_raw_debug(driver, query, query_variants, urls_tried, pages_loaded, selector_probes, errors)
            error_msg = "Rollback/Selenium tidak menemukan produk."
            if debug_path:
                error_msg += f" Debug: {debug_path}"
            return False, [], error_msg

        except Exception as exc:
            error = str(exc)
            log(f"[{self.search_id}]", f"[ROLLBACK] Error: {error}", "ERROR")
            save_debug_state_sync(self.search_id, driver, error)
            return False, [], f"Rollback/Selenium error: {error}"
        finally:
            safe_quit_driver(driver)

    def _scroll_and_extract(self, driver, raw_target: int, products: list[dict[str, Any]], seen_urls: set[str], eta_calc, variant: str) -> None:
        """Scroll one query page and append unique product cards."""
        previous_height = 0
        stable_rounds = 0

        for round_index in range(7):
            driver.execute_script("window.scrollBy(0, Math.floor(window.innerHeight * 0.9));")
            time.sleep(random.uniform(0.55, 0.9))

            for item in self._extract_cards(driver):
                url_key = item.get("url") or ""
                if not url_key or url_key in seen_urls:
                    continue
                seen_urls.add(url_key)
                item["source_query"] = variant
                products.append(item)

            percent = min(72, 55 + round_index)
            update_progress(
                self.search_id,
                active_engine=self.name,
                stage="rollback_extracting",
                percent=percent,
                message=f"Rollback/Selenium menemukan {len(products)} produk...",
                found=len(products),
                elapsed_seconds=eta_calc.get_elapsed(),
                eta_seconds=eta_calc.get_eta(percent),
            )

            if len(products) >= raw_target:
                break

            current_height = driver.execute_script("return document.body.scrollHeight || 0;")
            if current_height <= previous_height:
                stable_rounds += 1
            else:
                stable_rounds = 0
            previous_height = current_height
            if stable_rounds >= 2:
                break

    def _selector_probe(self, driver) -> dict[str, Any]:
        """Collect DOM counts used to debug zero extraction."""
        try:
            return driver.execute_script(
                """
                const count = (selector) => document.querySelectorAll(selector).length;
                const bodyText = document.body ? (document.body.innerText || '') : '';
                return {
                  "[data-testid='master-product-card']": count("[data-testid='master-product-card']"),
                  "[data-testid*='product']": count("[data-testid*='product']"),
                  "a[href*='tokopedia.com']": count("a[href*='tokopedia.com']"),
                  "img": count("img"),
                  "body_text_length": bodyText.length,
                  "body_text_sample": bodyText.slice(0, 1000)
                };
                """
            ) or {}
        except Exception:
            return {}

    def _save_zero_raw_debug(
        self,
        driver,
        query: str,
        query_variants: list[str],
        urls_tried: list[str],
        pages_loaded: int,
        selector_probes: list[dict[str, Any]],
        errors: list[str],
    ) -> str:
        """Save required Selenium zero-raw diagnostics. Never crash scrape."""
        html_saved = False
        screenshot_saved = False
        current_url = ""
        page_title = ""
        body_text_sample = ""
        try:
            current_url = driver.current_url
            page_title = driver.title
            page_source = driver.page_source or ""
            html_path = save_text_debug(self.search_id, "rollback_zero_raw_page.html", page_source)
            html_saved = bool(html_path)
            screenshot_path = get_debug_dir(self.search_id) / "rollback_zero_raw_screenshot.png"
            screenshot_saved = bool(driver.save_screenshot(str(screenshot_path)))
            body_text_sample = driver.execute_script("return document.body ? (document.body.innerText || '').slice(0, 1000) : '';") or ""
        except Exception as exc:
            errors.append(f"debug snapshot failed: {exc}")

        return save_zero_raw_debug(
            self.search_id,
            self.name,
            {
                "engine": self.name,
                "query": query,
                "query_variants": query_variants,
                "urls_tried": urls_tried,
                "pages_loaded": pages_loaded,
                "selector_results": selector_probes[-1] if selector_probes else {},
                "html_saved": html_saved,
                "screenshot_saved": screenshot_saved,
                "console_logs": [],
                "current_url": current_url,
                "page_title": page_title,
                "body_text_sample": body_text_sample,
                "errors": errors,
            },
        )

    def _extract_cards(self, driver) -> list[dict[str, Any]]:
        """Extract product cards in the browser so Selenium only makes one call."""
        return driver.execute_script(
            r"""
            const parseRupiah = (text) => {
              const lower = String(text || '').toLowerCase().trim();
              const unit = lower.match(/(\d+(?:[.,]\d+)?)\s*(juta|jt|mio|rb|ribu|k)\b/i);
              if (unit) {
                const number = Number(unit[1].replace(',', '.'));
                if (!Number.isFinite(number)) return null;
                return Math.round(number * (['juta', 'jt', 'mio'].includes(unit[2].toLowerCase()) ? 1000000 : 1000));
              }
              const digits = lower.replace(/[^\d]/g, '');
              if (!digits) return null;
              const parsed = Number.parseInt(digits, 10);
              return Number.isFinite(parsed) ? parsed : null;
            };

            const cleanUrl = (url) => String(url || '').split('?')[0].split('#')[0];
            const isProductUrl = (href) => {
              try {
                const url = new URL(href, location.href);
                if (!url.hostname.includes('tokopedia.com')) return false;
                if (['/search', '/cart', '/help', '/discovery', '/official-store'].some(prefix => url.pathname.startsWith(prefix))) return false;
                return url.pathname.split('/').filter(Boolean).length >= 2;
              } catch (_) {
                return false;
              }
            };
            const linesOf = (text) => String(text || '').split('\n').map((line) => line.trim()).filter(Boolean);
            const priceOf = (text) => {
              const match = String(text || '').match(/Rp\s*[\d.,]+(?:\s*(?:juta|jt|mio|rb|ribu|k))?/i);
              return match ? match[0].trim() : '';
            };

            const results = [];
            const pushProduct = (item) => {
              if (!item || !item.title || (!item.url && !item.price_raw)) return;
              results.push(item);
            };

            const productCardSelectors = [
              '[data-testid="master-product-card"]',
              'div[data-testid*="product"]',
              'div.pcv3__container',
              'div[class*="prd_container"]'
            ];

            for (const selector of productCardSelectors) {
              for (const card of Array.from(document.querySelectorAll(selector))) {
                const text = card.innerText || '';
                const priceRaw = priceOf(text);
                if (!priceRaw) continue;
                const anchor = card.querySelector('a[href*="tokopedia.com/"]');
                const lines = linesOf(text);
                const selectorTitle =
                  card.querySelector('[data-testid="spnSRPProdName"]') ||
                  card.querySelector('[data-testid*="ProdName"]') ||
                  card.querySelector('.prd_link-product-name');
                const priceIndex = lines.findIndex((line) => line.includes(priceRaw));
                const imageNode = card.querySelector('img');
                const title =
                  (selectorTitle && selectorTitle.textContent.trim()) ||
                  (priceIndex > 0 ? lines[priceIndex - 1] : '') ||
                  (anchor ? anchor.getAttribute('title') : '') ||
                  (imageNode ? imageNode.getAttribute('alt') : '') ||
                  lines.find((line) => !line.startsWith('Rp') && line.length > 4) ||
                  '';
                const afterPrice = priceIndex >= 0 ? lines.slice(priceIndex + 1) : lines;
                pushProduct({
                  title,
                  price_raw: priceRaw,
                  price_value: parseRupiah(priceRaw),
                  shop: afterPrice[0] || '',
                  location: afterPrice[1] || '',
                  rating: '',
                  sold: '',
                  url: cleanUrl(anchor ? anchor.href : ''),
                  image: imageNode ? (imageNode.currentSrc || imageNode.src || imageNode.getAttribute('data-src') || '') : '',
                  source_engine: 'rollback',
                });
              }
            }

            const anchors = Array.from(document.querySelectorAll('a[href*="tokopedia.com"]'));
            for (const anchor of anchors) {
              const href = anchor.href || '';
              if (!isProductUrl(href)) continue;

              const card =
                anchor.closest('[data-testid="master-product-card"]') ||
                anchor.closest('div[data-testid*="product"]') ||
                anchor.closest('div.pcv3__container') ||
                anchor.closest('div[class*="css-"]') ||
                anchor;
              const text = card.innerText || anchor.innerText || '';
              const priceRaw = priceOf(text);
              if (!priceRaw) continue;

              const lines = linesOf(text);
              const selectorTitle =
                card.querySelector('[data-testid="spnSRPProdName"]') ||
                card.querySelector('.prd_link-product-name');
              const priceIndex = lines.findIndex((line) => line.includes(priceRaw));
              const title =
                (selectorTitle && selectorTitle.textContent.trim()) ||
                (priceIndex > 0 ? lines[priceIndex - 1] : '') ||
                lines.find((line) => !line.startsWith('Rp') && line.length > 4) ||
                'Produk Tokopedia';

              const afterPrice = priceIndex >= 0 ? lines.slice(priceIndex + 1) : lines;
              const imageNode = card.querySelector('img');
              const soldMatch = text.match(/(\d+(?:[.,]\d+)?\s*(?:rb|jt)?\+?)\s*(?:terjual|sold)/i);
              const ratingMatch = text.match(/\b([4-5](?:[.,]\d)?)\b/);

              results.push({
                title,
                price_raw: priceRaw,
                price_value: parseRupiah(priceRaw),
                shop: afterPrice[0] || '',
                location: afterPrice[1] || '',
                rating: ratingMatch ? ratingMatch[1] : '',
                sold: soldMatch ? soldMatch[0] : '',
                url: cleanUrl(href),
                image: imageNode ? (imageNode.currentSrc || imageNode.src || imageNode.getAttribute('data-src') || '') : '',
                source_engine: 'rollback',
              });
            }
            return results;
            """
        ) or []
