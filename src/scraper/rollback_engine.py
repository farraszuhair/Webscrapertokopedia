"""
rollback_engine.py - Selenium rollback scraper.

Uses Selenium Manager first, webdriver-manager second, and returns the same
schema as Puppeteer.
"""
from __future__ import annotations

import asyncio
import random
import time
import urllib.parse
from pathlib import Path
from typing import Any

from src.scraper.normalizer import normalize_products
from src.scraper.selenium_driver import create_chrome_driver, safe_quit_driver
from src.server.progress import update_progress
from src.utils.debug import save_debug_state_sync
from src.utils.logger import log


DEBUG_DIR = Path("data/debug")


class RollbackEngine:
    name = "rollback"

    def __init__(self, search_id: str):
        self.search_id = search_id

    async def scrape(self, query: str, raw_target: int, eta_calc) -> tuple[bool, list[dict[str, Any]], str]:
        """Run blocking Selenium work in a thread so FastAPI stays responsive."""
        return await asyncio.to_thread(self._scrape_sync, query, raw_target, eta_calc)

    def _scrape_sync(self, query: str, raw_target: int, eta_calc) -> tuple[bool, list[dict[str, Any]], str]:
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

        try:
            url = f"https://www.tokopedia.com/search?navsource=search&q={urllib.parse.quote(query)}"
            update_progress(
                self.search_id,
                active_engine=self.name,
                stage="rollback_opening",
                percent=52,
                message="Membuka Tokopedia dengan Selenium...",
                elapsed_seconds=eta_calc.get_elapsed(),
            )

            driver.get(url)
            try:
                WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            except Exception:
                pass

            previous_height = 0
            stable_rounds = 0

            for round_index in range(14):
                driver.execute_script("window.scrollBy(0, Math.floor(window.innerHeight * 0.85));")
                time.sleep(random.uniform(0.75, 1.15))

                for item in self._extract_cards(driver):
                    url_key = item.get("url") or ""
                    if not url_key or url_key in seen_urls:
                        continue
                    seen_urls.add(url_key)
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
                if stable_rounds >= 3:
                    break

            normalized = normalize_products(products, self.name)
            if normalized:
                log(f"[{self.search_id}]", f"[ROLLBACK] Extracted {len(normalized)} products", "OK")
                return True, normalized, ""
            return False, [], "Rollback/Selenium tidak menemukan produk."

        except Exception as exc:
            error = str(exc)
            log(f"[{self.search_id}]", f"[ROLLBACK] Error: {error}", "ERROR")
            save_debug_state_sync(self.search_id, driver, error)
            return False, [], f"Rollback/Selenium error: {error}"
        finally:
            safe_quit_driver(driver)

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
              const url = String(href || '');
              if (!url.includes('tokopedia.com/')) return false;
              if (url.includes('/search') || url.includes('/cart') || url.includes('/help')) return false;
              if (url.includes('/p/') || url.includes('/official-store')) return false;
              return true;
            };
            const linesOf = (text) => String(text || '').split('\n').map((line) => line.trim()).filter(Boolean);
            const priceOf = (text) => {
              const match = String(text || '').match(/Rp\s*[\d.,]+(?:\s*(?:juta|jt|mio|rb|ribu|k))?/i);
              return match ? match[0].trim() : '';
            };

            const results = [];
            const anchors = Array.from(document.querySelectorAll('a[href*="tokopedia.com/"]'));
            for (const anchor of anchors) {
              const href = anchor.href || '';
              if (!isProductUrl(href)) continue;

              const card =
                anchor.closest('[data-testid="master-product-card"]') ||
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
