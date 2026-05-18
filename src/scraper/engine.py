"""
engine.py - Core scraping engine using Playwright (Python native).
Replaces Puppeteer to fix 'Frame Detached' and connection closed errors.
"""
import asyncio
import uuid
import re
from typing import List, Dict, Any, Optional
from playwright.async_api import async_playwright, Page, BrowserContext, TimeoutError as PlaywrightTimeoutError

from src.utils.logger import log
from src.utils.eta import ETACalculator
from src.utils.debug import save_debug_state
from src.server.progress import update_progress
from src.scraper.tokopedia import TokopediaConfig

class PlaywrightEngine:
    def __init__(self, search_id: str):
        self.search_id = search_id
        self.playwright = None
        self.browser = None
        self.context = None

    async def _init_browser(self):
        """Initializes a clean, isolated browser context."""
        log(f"[{self.search_id}]", "Launching Playwright Chromium...", "INFO")
        update_progress(self.search_id, stage="launching_browser", message="Membuka browser (Playwright)...")
        
        self.playwright = await async_playwright().start()
        # Launch chromium. Headless mode by default, but we can configure args for stealth.
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-http2" # Fix Tokopedia HTTP/2 protocol errors
            ]
        )
        
        # Create an isolated context to ensure no session leaking
        self.context = await self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1366, "height": 768},
            bypass_csp=True
        )

        # Abort images/fonts to speed up extraction, but only after page load
        # Wait, aborting images right away can sometimes trigger anti-bots. 
        # But for speed, let's block heavy media.
        await self.context.route("**/*", self._route_interceptor)
        log(f"[{self.search_id}]", "Browser context created.", "OK")

    async def _route_interceptor(self, route):
        """Block unnecessary resources to speed up scraping and save memory."""
        if route.request.resource_type in ["image", "media", "font", "stylesheet"]:
            await route.abort()
        else:
            await route.continue_()

    async def close(self):
        """Safely closes all browser resources."""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            log(f"[{self.search_id}]", "Browser resources cleaned up.", "INFO")
        except Exception as e:
            log(f"[{self.search_id}]", f"Error during browser cleanup: {e}", "ERROR")

    async def extract_products(self, page: Page, current_count: int) -> List[Dict[str, Any]]:
        """Extracts product data from the current DOM."""
        # Using evaluate to run JS natively in the browser for maximum speed and fallback handling
        js_code = """
        (selectors) => {
            const getEl = (root, selList) => {
                for (let s of selList) {
                    let el = root.querySelector(s);
                    if (el) return el;
                }
                return null;
            };
            
            let results = [];
            let cards = [];
            for (let s of selectors.CARD) {
                cards = document.querySelectorAll(s);
                if (cards.length > 0) break;
            }

            cards.forEach(card => {
                let titleEl = getEl(card, selectors.TITLE);
                let priceEl = getEl(card, selectors.PRICE);
                let shopEl = getEl(card, selectors.SHOP);
                let ratingEl = getEl(card, selectors.RATING);
                let soldEl = getEl(card, selectors.SOLD);
                let imgEl = getEl(card, selectors.IMAGE);
                
                // Get link - usually the closest a tag or internal
                let linkEl = card.querySelector('a');
                let link = linkEl ? linkEl.href : '';

                if (titleEl && priceEl) {
                    results.push({
                        id: 'prod_' + Math.random().toString(36).substr(2, 9),
                        title: titleEl.innerText.trim(),
                        price_text: priceEl.innerText.trim(),
                        shop: shopEl ? shopEl.innerText.trim() : 'Unknown',
                        rating: ratingEl ? ratingEl.innerText.trim() : null,
                        sold: soldEl ? soldEl.innerText.trim() : null,
                        image: imgEl ? imgEl.src : '',
                        link: link,
                        source: 'tokopedia'
                    });
                }
            });
            return results;
        }
        """
        
        selectors = {
            "CARD": TokopediaConfig.CARD_SELECTORS,
            "TITLE": TokopediaConfig.TITLE_SELECTORS,
            "PRICE": TokopediaConfig.PRICE_SELECTORS,
            "SHOP": TokopediaConfig.SHOP_SELECTORS,
            "RATING": TokopediaConfig.RATING_SELECTORS,
            "SOLD": TokopediaConfig.SOLD_SELECTORS,
            "IMAGE": TokopediaConfig.IMAGE_SELECTORS,
        }
        
        try:
            products = await page.evaluate(js_code, selectors)
            return products
        except Exception as e:
            log(f"[{self.search_id}]", f"Extraction JS error: {e}", "WARN")
            return []

    async def auto_scroll(self, page: Page, max_scrolls: int, target_raw: int, eta_calc: ETACalculator):
        """Scrolls down the page to trigger lazy loading."""
        last_height = await page.evaluate("document.body.scrollHeight")
        accumulated_products = []
        
        for i in range(max_scrolls):
            # Extract before scroll
            products = await self.extract_products(page, len(accumulated_products))
            accumulated_products = products # It gets all currently loaded
            
            found = len(accumulated_products)
            
            # Progress update
            pct = min(90, 20 + int((found / target_raw) * 70))
            update_progress(
                self.search_id, 
                stage="scrolling", 
                message=f"Scroll {i+1}/{max_scrolls} - Menemukan {found} produk...",
                percent=pct,
                found=found,
                elapsed_seconds=eta_calc.get_elapsed(),
                eta_seconds=eta_calc.get_eta(pct)
            )
            
            if found >= target_raw:
                log(f"[{self.search_id}]", f"Reached raw target ({found}/{target_raw}). Stopping scroll.", "INFO")
                break
                
            # Scroll down
            await page.mouse.wheel(0, 1500)
            await asyncio.sleep(1.5) # Wait for network/lazy load
            
            new_height = await page.evaluate("document.body.scrollHeight")
            if new_height == last_height:
                # Try a smaller scroll or break if really at bottom
                await page.mouse.wheel(0, -500)
                await asyncio.sleep(0.5)
                await page.mouse.wheel(0, 2000)
                await asyncio.sleep(1.5)
                
                check_height = await page.evaluate("document.body.scrollHeight")
                if check_height == last_height:
                    log(f"[{self.search_id}]", "Reached bottom of page.", "INFO")
                    break
            last_height = new_height
            
        return accumulated_products

    async def scrape(self, query: str, raw_target: int, eta_calc: ETACalculator) -> List[Dict[str, Any]]:
        """
        Main scraping logic.
        Implements robust retry and fresh context creation on failure.
        """
        MAX_RETRIES = 3
        url = TokopediaConfig.build_search_url(query)
        
        for attempt in range(1, MAX_RETRIES + 1):
            page = None
            try:
                # 1. Initialize fresh browser context if not exists
                if not self.context:
                    await self._init_browser()
                
                # 2. Create fresh page
                page = await self.context.new_page()
                
                log(f"[{self.search_id}]", f"Opening URL (Attempt {attempt}/{MAX_RETRIES}): {url}", "INFO")
                update_progress(
                    self.search_id, 
                    stage="opening_tokopedia", 
                    message=f"Membuka Tokopedia (Percobaan {attempt})...",
                    percent=10,
                    elapsed_seconds=eta_calc.get_elapsed(),
                    eta_seconds=eta_calc.get_eta(10)
                )

                # 3. Navigate (use domcontentloaded for speed, timeout 30s)
                # If frame detached happens, it throws here.
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                
                # Wait a bit for initial react render
                await asyncio.sleep(2)
                
                # 4. Scroll and extract
                update_progress(self.search_id, stage="scrolling", message="Mulai ekstrak data...", percent=20)
                products = await self.auto_scroll(page, max_scrolls=20, target_raw=raw_target, eta_calc=eta_calc)
                
                log(f"[{self.search_id}]", f"Extraction successful. Got {len(products)} products.", "OK")
                return products
                
            except PlaywrightTimeoutError:
                log(f"[{self.search_id}]", f"Timeout on attempt {attempt}", "WARN")
            except Exception as e:
                err_msg = str(e)
                log(f"[{self.search_id}]", f"Error on attempt {attempt}: {err_msg}", "ERROR")
                # Save debug artifacts
                await save_debug_state(self.search_id, page, err_msg)
                
                # "Frame detached" or "Connection closed" typically means the context is dead.
                # Force close context to trigger recreation on next loop.
                await self.close()
                self.context = None
                self.browser = None
                self.playwright = None
                
            finally:
                # Cleanup page object if it exists and didn't crash the whole context
                if page and not page.is_closed():
                    try:
                        await page.close()
                    except:
                        pass
                        
            if attempt < MAX_RETRIES:
                wait_time = 2 * attempt
                log(f"[{self.search_id}]", f"Waiting {wait_time}s before retry...", "INFO")
                update_progress(
                    self.search_id, 
                    stage="retrying_navigation", 
                    message=f"Koneksi gagal, mencoba ulang ({attempt}/{MAX_RETRIES})..."
                )
                await asyncio.sleep(wait_time)
                
        # If we reach here, all retries failed
        raise Exception("Gagal mengambil data dari Tokopedia setelah 3 percobaan.")
