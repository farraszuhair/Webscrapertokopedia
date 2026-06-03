"""
rollback_engine.py - Selenium rollback scraper.

Key fixes:
1. Preflight check FIRST - detects Chrome error pages before extraction.
2. --disable-http2 via selenium_driver.py to reduce ERR_HTTP2_PROTOCOL_ERROR.
3. If opened_real_page=false -> returns False with exact error_type. No fake "selector failed".
4. No category filtering. Returns ALL raw products. AI Orchestrator filters later.
"""
from __future__ import annotations

import asyncio
import json
import random
import time
from pathlib import Path
from typing import Any

from src.scraper.normalizer import normalize_products
from src.scraper.selenium_driver import create_chrome_driver, safe_quit_driver
from src.scraper.url_builder import build_tokopedia_search_url
from src.server.progress import update_progress
from src.utils.debug import get_debug_dir, save_json_debug
from src.utils.logger import log


DEBUG_DIR = Path("data/debug")

# Chrome error strings to detect on loaded page (same as preflight.py)
_ERROR_SIGNALS = [
    "err_http2_protocol_error",
    "err_connection_reset",
    "err_connection_refused",
    "err_connection_timed_out",
    "err_name_not_resolved",
    "this site can",
    "situs ini tidak dapat",
    "dns_probe_finished",
]

_ERROR_KEYS = {
    "err_http2_protocol_error": "http2_protocol_error",
    "err_connection_reset": "connection_reset",
    "err_connection_refused": "connection_refused",
    "err_connection_timed_out": "connection_timed_out",
    "err_name_not_resolved": "name_not_resolved",
    "this site can": "site_unreachable",
    "situs ini tidak dapat": "site_unreachable_id",
    "dns_probe_finished": "dns_error",
}


def _detect_page_health_selenium(driver) -> dict[str, Any]:
    """
    Check if driver is showing a real Tokopedia page or a Chrome error page.
    Returns { opened_real_page, error_type, page_title, body_sample, current_url }.
    """
    try:
        current_url = driver.current_url or ""
        title = driver.title or ""
        body_text = driver.execute_script(
            "return document.body ? (document.body.innerText || '').slice(0, 1000) : '';"
        ) or ""
    except Exception as exc:
        return {
            "opened_real_page": False,
            "error_type": "driver_error",
            "page_title": "",
            "body_sample": "",
            "current_url": "",
            "nav_error": str(exc),
        }

    combined = f"{title} {body_text} {current_url}".lower()

    # Check for known error patterns
    error_type = None
    for signal, key in _ERROR_KEYS.items():
        if signal in combined:
            error_type = key
            break

    # about:blank = navigation never happened
    if error_type is None and current_url.strip().lower() in ("about:blank", "chrome://newtab/", ""):
        error_type = "blank_page"

    # Must have Tokopedia signal to be a real page
    is_real = "tokopedia" in combined or "toped" in combined
    if error_type is None and not is_real:
        error_type = "unknown_non_tokopedia_page"

    opened_real_page = (error_type is None) and is_real
    return {
        "opened_real_page": opened_real_page,
        "error_type": error_type,
        "page_title": title,
        "body_sample": body_text[:500],
        "current_url": current_url,
    }


def _save_engine_error_debug(
    search_id: str,
    query: str,
    urls_tried: list[str],
    health: dict[str, Any],
    errors: list[str],
    driver=None,
) -> str:
    """Save data/debug/<search_id>/rollback_engine_error.json."""
    payload = {
        "engine": "rollback",
        "query": query,
        "urls_tried": urls_tried,
        "opened_real_page": health.get("opened_real_page", False),
        "error_type": health.get("error_type", "unknown"),
        "page_title": health.get("page_title", ""),
        "body_text_sample": health.get("body_sample", ""),
        "current_url": health.get("current_url", ""),
        "selector_counts": {},
        "errors": errors,
        "recommendation": (
            "Browser opened error page. Not a selector problem. "
            "Check network/proxy/HTTP2 support."
            if not health.get("opened_real_page")
            else "Page opened but no products extracted. Check selectors."
        ),
    }

    if driver and health.get("opened_real_page"):
        try:
            payload["selector_counts"] = driver.execute_script(
                """return {
                  master_product_card: document.querySelectorAll("[data-testid='master-product-card']").length,
                  product_testid: document.querySelectorAll("[data-testid*='product']").length,
                  tokopedia_anchors: document.querySelectorAll("a[href*='tokopedia.com']").length,
                  img_count: document.querySelectorAll('img').length
                };"""
            ) or {}
        except Exception:
            pass

        try:
            debug_dir = get_debug_dir(search_id)
            debug_dir.mkdir(parents=True, exist_ok=True)
            ss_path = debug_dir / "rollback_engine_error_screenshot.png"
            driver.save_screenshot(str(ss_path))
            payload["screenshot_saved"] = ss_path.exists()
        except Exception:
            pass

    return save_json_debug(search_id, "rollback_engine_error.json", payload) or ""


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

        debug_subdir = DEBUG_DIR / self.search_id
        driver, error_msg = create_chrome_driver(self.search_id, debug_subdir)
        if not driver:
            return False, [], f"Chrome driver bootstrap failed: {error_msg}"

        products: list[dict[str, Any]] = []
        seen_urls: set[str] = set()
        urls_tried: list[str] = []
        errors: list[str] = []
        preflight_health: dict[str, Any] = {}

        try:
            for variant_index, variant in enumerate(query_variants):
                if len(products) >= raw_target:
                    break

                # Rule: simple URL first, no pmin/pmax.
                url = build_tokopedia_search_url(variant)
                urls_tried.append(url)

                update_progress(
                    self.search_id,
                    active_engine=self.name,
                    stage="rollback_opening",
                    percent=min(70, 52 + variant_index),
                    message=f"Rollback/Selenium opening {variant}",
                    elapsed_seconds=eta_calc.get_elapsed(),
                )

                try:
                    driver.get(url)
                    WebDriverWait(driver, 12).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                    time.sleep(1.0)

                    # PREFLIGHT CHECK: is this a real Tokopedia page?
                    health = _detect_page_health_selenium(driver)
                    preflight_health = health

                    if not health["opened_real_page"]:
                        error_type = health["error_type"]
                        msg = (
                            f"Browser opened Chrome error page ({error_type}), "
                            f"not Tokopedia. Extraction impossible."
                        )
                        errors.append(f"{url}: {msg}")
                        log(f"[{self.search_id}]", f"[ROLLBACK] PREFLIGHT FAIL: {msg}", "WARN")

                        # Save diagnostic immediately so user sees what happened
                        _save_engine_error_debug(
                            self.search_id, query, urls_tried, health, errors, driver
                        )
                        # Continue to next variant - different query = different URL = maybe works
                        continue

                    # Real page confirmed. Extract raw products.
                    self._scroll_and_extract(driver, raw_target, products, seen_urls, eta_calc, variant)

                except Exception as variant_exc:
                    error = f"{url}: {variant_exc}"
                    errors.append(error)
                    log(f"[{self.search_id}]", f"[ROLLBACK] Query failed {variant}: {variant_exc}", "WARN")
                    continue

            if products:
                self._save_image_missing_debug(driver, query, urls_tried, products)
                normalized = normalize_products(products, self.name)
                if normalized:
                    log(f"[{self.search_id}]", f"[ROLLBACK] Extracted {len(normalized)} products", "OK")
                    return True, products, ""

            # No products - save debug with preflight context
            _save_engine_error_debug(
                self.search_id, query, urls_tried, preflight_health or {}, errors, driver
            )

            # Build a specific error message based on what actually happened
            if preflight_health and not preflight_health.get("opened_real_page"):
                error_type = preflight_health.get("error_type", "unknown")
                error_msg = (
                    f"Browser opened Chrome error page: {error_type}. "
                    f"opened_real_page=false. See data/debug/{self.search_id}/rollback_engine_error.json"
                )
            else:
                error_msg = (
                    f"Rollback/Selenium opened Tokopedia but found 0 products. "
                    f"See data/debug/{self.search_id}/rollback_engine_error.json"
                )
            return False, [], error_msg

        except Exception as exc:
            error = str(exc)
            log(f"[{self.search_id}]", f"[ROLLBACK] Error: {error}", "ERROR")
            _save_engine_error_debug(self.search_id, query, urls_tried, {}, [error], driver)
            return False, [], f"Rollback/Selenium error: {error}"
        finally:
            safe_quit_driver(driver)

    def _save_image_missing_debug(
        self,
        driver,
        query: str,
        urls_tried: list[str],
        products: list[dict[str, Any]],
    ) -> None:
        total = len(products)
        if total < 5:
            return
        missing = sum(1 for product in products if not product.get("image"))
        missing_rate = missing / total
        if missing_rate <= 0.70:
            return

        debug_dir = get_debug_dir(self.search_id)
        payload = {
            "engine": self.name,
            "query": query,
            "urls_tried": urls_tried,
            "images_extracted_count": total - missing,
            "images_missing_count": missing,
            "missing_rate": round(missing_rate, 4),
            "samples": products[:20],
        }
        try:
            debug_dir.mkdir(parents=True, exist_ok=True)
            html_path = debug_dir / "rollback_image_missing_debug.html"
            screenshot_path = debug_dir / "rollback_image_missing_debug.png"
            html_path.write_text(driver.page_source or "", encoding="utf-8")
            driver.save_screenshot(str(screenshot_path))
            payload["html_saved"] = html_path.exists()
            payload["screenshot_saved"] = screenshot_path.exists()
        except Exception as exc:
            payload["error"] = str(exc)
        save_json_debug(self.search_id, "rollback_image_missing_debug.json", payload)

    def _scroll_and_extract(
        self,
        driver,
        raw_target: int,
        products: list[dict[str, Any]],
        seen_urls: set[str],
        eta_calc,
        variant: str,
    ) -> None:
        """Scroll and collect raw product cards. No category filtering."""
        previous_height = 0
        stable_rounds = 0

        for round_index in range(7):
            driver.execute_script("window.scrollBy(0, Math.floor(window.innerHeight * 0.9));")
            time.sleep(random.uniform(0.6, 1.0))

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

    def _extract_cards(self, driver) -> list[dict[str, Any]]:
        """Extract raw product cards. Returns ALL cards regardless of category."""
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
                if (!['www.tokopedia.com', 'tokopedia.com'].includes(url.hostname)) return false;
                if (['/search', '/cart', '/help', '/discovery', '/official-store'].some(
                  prefix => url.pathname.startsWith(prefix)
                )) return false;
                return url.pathname.split('/').filter(Boolean).length >= 2;
              } catch (_) { return false; }
            };
            const linesOf = (text) => String(text || '').split('\n').map(l => l.trim()).filter(Boolean);
            const priceOf = (text) => {
              const match = String(text || '').match(/Rp\s*[\d.,]+(?:\s*(?:juta|jt|mio|rb|ribu|k))?/i);
              return match ? match[0].trim() : '';
            };
            function isBadProductImage(url = '', alt = '', className = '', parentClassName = '', contextText = '') {
              const text = `${url} ${alt} ${className} ${parentClassName} ${contextText}`.toLowerCase();
              const badKeywords = [
                'promo',
                'promo guncang',
                'banner',
                'campaign',
                'ads',
                'iklan',
                'guncang',
                'cashback',
                'voucher',
                'flash',
                'sale',
                'bebas ongkir',
                'bebas-ongkir',
                'free ongkir',
                'free-ongkir',
                'tokopedia.com/promo',
                '/promo/',
                '/campaign/',
                'assets/promo',
                'assets/campaign',
                'placeholder',
                'no-image',
                'noimage',
                'blank',
                'sprite',
                '/icon',
                'icons/',
                'icon-',
                'shop-logo',
                'store-logo',
                'avatar',
                'badge',
                '6.6',
                '7.7',
                '8.8',
                '9.9',
                '10.10',
                '11.11',
                '12.12',
              ];
              return badKeywords.some((keyword) => text.includes(keyword));
            }

            function normalizeImageUrl(raw) {
              if (typeof raw !== 'string') return '';
              let url = raw.trim();
              if (!url) return '';
              if (url.startsWith('//')) url = `https:${url}`;
              const compact = url.toLowerCase().replace(/\s+/g, '');
              if (['undefined', 'null', 'noimage', 'no-image', 'blank'].includes(compact)) return '';
              if (compact.includes('svg')) return '';
              if (url.startsWith('http://') || url.startsWith('https://') || url.startsWith('data:image/')) return url;
              return '';
            }

            function scoreProductImageCandidate(img, productTitle = '') {
              const url = normalizeImageUrl(img.src || '');
              const alt = String(img.alt || '');
              const className = String(img.className || '');
              const parentClassName = String(img.parentClassName || '');
              const contextText = String(img.contextText || '');
              if (!url) return -999;
              if (isBadProductImage(url, alt, className, parentClassName, contextText)) return -999;

              let score = 0;
              const width = Number(img.width || 0);
              const height = Number(img.height || 0);
              const ratio = width && height ? width / height : 1;
              if (width > 0 && width < 72) return -999;
              if (height > 0 && height < 72) return -999;
              if (width >= 180 && height > 0 && ratio > 2.15) return -999;
              if (height >= 180 && width > 0 && ratio < 0.35) return -999;

              if (width >= 120) score += 10;
              if (height >= 120) score += 10;
              if (width >= 250 || height >= 250) score += 8;

              if (ratio >= 0.6 && ratio <= 1.8) score += 10;

              const loweredUrl = url.toLowerCase();
              if (loweredUrl.includes('images.tokopedia.net')) score += 15;
              if (loweredUrl.includes('cache') || loweredUrl.includes('product') || loweredUrl.includes('prd')) score += 8;

              const contextLower = `${className} ${parentClassName} ${contextText}`.toLowerCase();
              if (contextLower.includes('product') || contextLower.includes('prd') || contextLower.includes('master-product-card')) score += 8;
              if (contextLower.includes('image') || contextLower.includes('thumbnail')) score += 4;

              const titleWords = String(productTitle)
                .toLowerCase()
                .split(/\s+/)
                .filter((word) => word.length >= 4)
                .slice(0, 6);
              const altLower = alt.toLowerCase();
              score += titleWords.filter((word) => altLower.includes(word)).length * 8;

              return score;
            }

            function pickBestProductImage(images, productTitle = '') {
              return pickProductImageCandidates(images, productTitle)[0] || '';
            }

            function pickProductImageCandidates(images, productTitle = '') {
              const ranked = images
                .map((img) => ({
                  src: normalizeImageUrl(img.src || ''),
                  score: scoreProductImageCandidate(img, productTitle),
                }))
                .filter((img) => img.src && img.score > 0)
                .sort((a, b) => b.score - a.score);
              const seen = new Set();
              const result = [];
              ranked.forEach((img) => {
                if (seen.has(img.src)) return;
                seen.add(img.src);
                result.push(img.src);
              });
              return result;
            }

            function getImageFromCard(card, productTitle = '') {
              const images = [];
              const pushCandidate = (src, node = {}) => {
                const url = normalizeImageUrl(src);
                if (!url) return;
                const rect = typeof node.getBoundingClientRect === 'function' ? node.getBoundingClientRect() : {};
                const parentClasses = [];
                let parent = node.parentElement;
                for (let depth = 0; depth < 4 && parent; depth += 1) {
                  parentClasses.push(parent.className || parent.getAttribute?.('class') || '');
                  parentClasses.push(parent.getAttribute?.('data-testid') || '');
                  parentClasses.push(parent.getAttribute?.('aria-label') || '');
                  parent = parent.parentElement;
                }
                images.push({
                  src: url,
                  alt: node.alt || node.getAttribute?.('alt') || node.getAttribute?.('aria-label') || '',
                  className: node.className || node.getAttribute?.('class') || '',
                  parentClassName: parentClasses.join(' '),
                  contextText: node.getAttribute?.('data-testid') || node.getAttribute?.('aria-label') || '',
                  width: node.naturalWidth || node.width || Math.round(rect.width || 0),
                  height: node.naturalHeight || node.height || Math.round(rect.height || 0),
                });
              };
              const pushSrcset = (srcset, node) => {
                if (!srcset) return;
                String(srcset)
                  .split(',')
                  .map((item) => item.trim().split(/\s+/)[0])
                  .filter(Boolean)
                  .forEach((url) => pushCandidate(url, node));
              };
              const pushBackgroundUrl = (node) => {
                if (!node) return;
                const style = window.getComputedStyle(node);
                const raw = style && style.backgroundImage;
                const match = raw && raw.match(/url\(["']?([^"')]+)["']?\)/i);
                if (match) pushCandidate(match[1], node);
              };

              card.querySelectorAll('picture source, source').forEach((source) => {
                pushSrcset(source.getAttribute('srcset'), source);
                pushSrcset(source.getAttribute('data-srcset'), source);
              });

              card.querySelectorAll('img').forEach((img) => {
                pushCandidate(img.currentSrc, img);
                pushCandidate(img.src, img);
                pushCandidate(img.getAttribute('src'), img);
                pushCandidate(img.getAttribute('data-src'), img);
                pushCandidate(img.getAttribute('data-original-src'), img);
                pushCandidate(img.getAttribute('data-original'), img);
                pushCandidate(img.getAttribute('data-lazy-src'), img);
                pushCandidate(img.getAttribute('data-lazy'), img);
                pushCandidate(img.getAttribute('data-lazy-img'), img);
                pushCandidate(img.getAttribute('data-defer-src'), img);
                pushCandidate(img.getAttribute('data-image'), img);
                pushCandidate(img.getAttribute('data-image-src'), img);
                pushCandidate(img.getAttribute('data-src-large'), img);
                pushCandidate(img.getAttribute('data-thumb'), img);
                pushCandidate(img.getAttribute('data-img'), img);
                pushCandidate(img.getAttribute('data-url'), img);
                pushSrcset(img.getAttribute('srcset'), img);
                pushSrcset(img.getAttribute('data-srcset'), img);
              });

              pushBackgroundUrl(card);
              card.querySelectorAll('[style*="background"]').forEach(pushBackgroundUrl);

              const candidates = pickProductImageCandidates(images, productTitle);
              return {
                primary: candidates[0] || '',
                fallback: candidates[1] || '',
                candidates,
                status: candidates[0] ? 'ok' : 'missing',
                sourceType: candidates[0] ? 'card_candidate' : 'placeholder',
              };
            }

            const seen = new Set();
            const results = [];
            const pushProduct = (item) => {
              if (!item || !item.title || (!item.url && !item.price_raw)) return;
              const key = `${item.url}|${item.title}|${item.price_raw}`;
              if (seen.has(key)) return;
              seen.add(key);
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
                const anchor = Array.from(card.querySelectorAll('a[href*="tokopedia.com/"]'))
                  .find(item => isProductUrl(item.href));
                const lines = linesOf(text);
                const selectorTitle =
                  card.querySelector('[data-testid="spnSRPProdName"]') ||
                  card.querySelector('[data-testid*="ProdName"]') ||
                  card.querySelector('.prd_link-product-name');
                const priceIndex = lines.findIndex(line => line.includes(priceRaw));
                const imageNode = card.querySelector('img');
                const title =
                  (selectorTitle && selectorTitle.textContent.trim()) ||
                  (priceIndex > 0 ? lines[priceIndex - 1] : '') ||
                  (anchor ? anchor.getAttribute('title') : '') ||
                  (imageNode ? imageNode.getAttribute('alt') : '') ||
                  lines.find(line => !line.startsWith('Rp') && line.length > 4) ||
                  '';
                const imageData = getImageFromCard(card, title);
                const imageUrl = imageData.primary || '';
                const afterPrice = priceIndex >= 0 ? lines.slice(priceIndex + 1) : lines;
                const soldMatch = text.match(/(\d+(?:[.,]\d+)?\s*(?:rb|jt)?\+?)\s*(?:terjual|sold)/i);
                const ratingMatch = text.match(/\b([4-5](?:[.,]\d)?)\b/);
                pushProduct({
                  title,
                  price_raw: priceRaw,
                  price_value: parseRupiah(priceRaw),
                  shop: afterPrice[0] || '',
                  location: afterPrice[1] || '',
                  rating: ratingMatch ? ratingMatch[1] : '',
                  sold: soldMatch ? soldMatch[0] : '',
                  url: cleanUrl(anchor ? anchor.href : ''),
                  image_url: imageUrl || '',
                  image: imageUrl || '',
                  thumbnail: imageUrl || '',
                  primary_image: imageUrl || '',
                  fallback_image: imageData.fallback || '',
                  image_candidates: (imageData.candidates || []).slice(0, 8),
                  image_source_type: imageData.sourceType,
                  image_status: imageData.status,
                  source_engine: 'rollback',
                });
              }
            }

            // Anchor-based fallback for non-standard card markup
            for (const anchor of Array.from(document.querySelectorAll('a[href*="tokopedia.com"]'))) {
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
              const priceIndex = lines.findIndex(line => line.includes(priceRaw));
              const title =
                (selectorTitle && selectorTitle.textContent.trim()) ||
                (priceIndex > 0 ? lines[priceIndex - 1] : '') ||
                lines.find(line => !line.startsWith('Rp') && line.length > 4) ||
                'Produk Tokopedia';
              const afterPrice = priceIndex >= 0 ? lines.slice(priceIndex + 1) : lines;
              const imageData = getImageFromCard(card, title);
              const imageUrl = imageData.primary || '';
              const soldMatch = text.match(/(\d+(?:[.,]\d+)?\s*(?:rb|jt)?\+?)\s*(?:terjual|sold)/i);
              const ratingMatch = text.match(/\b([4-5](?:[.,]\d)?)\b/);
              pushProduct({
                title,
                price_raw: priceRaw,
                price_value: parseRupiah(priceRaw),
                shop: afterPrice[0] || '',
                location: afterPrice[1] || '',
                rating: ratingMatch ? ratingMatch[1] : '',
                sold: soldMatch ? soldMatch[0] : '',
                url: cleanUrl(href),
                image_url: imageUrl || '',
                image: imageUrl || '',
                thumbnail: imageUrl || '',
                primary_image: imageUrl || '',
                fallback_image: imageData.fallback || '',
                image_candidates: (imageData.candidates || []).slice(0, 8),
                image_source_type: imageData.sourceType,
                image_status: imageData.status,
                source_engine: 'rollback',
              });
            }
            return results;
            """
        ) or []
