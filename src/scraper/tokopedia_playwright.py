"""
tokopedia_playwright.py - Playwright engine for scraping.
Handles context isolation and safe retries on connection reset.
"""
import asyncio
from typing import List, Dict, Any, Tuple
from playwright.async_api import async_playwright, Page, TimeoutError as PlaywrightTimeoutError

from src.scraper.base import BaseEngine
from src.utils.logger import log
from src.utils.eta import ETACalculator
from src.server.progress import update_progress
from src.scraper.tokopedia import TokopediaConfig
from src.utils.debug import save_debug_state

class PlaywrightEngine(BaseEngine):
    def __init__(self, search_id: str):
        super().__init__(search_id)
        self.playwright = None
        self.browser = None
        self.context = None

    async def _init_browser(self):
        log(f"[{self.search_id}]", "[PW] Launching Playwright Chromium...", "INFO")
        update_progress(self.search_id, engine="playwright", stage="browser_launching", message="Membuka browser (Playwright)...")
        
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled", 
                "--disable-http2"
            ]
        )
        self.context = await self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1366, "height": 768},
            bypass_csp=True
        )
        await self.context.route("**/*", self._route_interceptor)

    async def _route_interceptor(self, route):
        if route.request.resource_type in ["image", "media", "font", "stylesheet"]:
            await route.abort()
        else:
            await route.continue_()

    async def close(self):
        try:
            if self.context: await self.context.close()
            if self.browser: await self.browser.close()
            if self.playwright: await self.playwright.stop()
        except Exception:
            pass

    async def scrape(self, query: str, raw_target: int, eta_calc: ETACalculator) -> Tuple[bool, List[Dict[str, Any]], str]:
        MAX_RETRIES = 2
        url = TokopediaConfig.build_search_url(query)
        last_error = ""
        
        for attempt in range(1, MAX_RETRIES + 1):
            page = None
            try:
                if not self.context:
                    await self._init_browser()
                
                page = await self.context.new_page()
                log(f"[{self.search_id}]", f"[PW] Opening URL (Attempt {attempt}/{MAX_RETRIES})", "INFO")
                update_progress(
                    self.search_id, 
                    stage="browser_opening", 
                    percent=12,
                    attempt=attempt,
                    max_attempts=MAX_RETRIES
                )

                # Wait for commit first (safer than waiting for full domcontentloaded on flaky servers)
                await page.goto(url, wait_until="commit", timeout=25000)
                await page.wait_for_load_state("domcontentloaded", timeout=15000)
                
                update_progress(self.search_id, stage="scrolling", percent=15)
                products = await self._auto_scroll(page, max_scrolls=15, target_raw=raw_target, eta_calc=eta_calc)
                
                if products:
                    return True, products, ""
                else:
                    last_error = "No products extracted."
                
            except Exception as e:
                last_error = str(e)
                log(f"[{self.search_id}]", f"[PW] Error on attempt {attempt}: {last_error}", "WARN")
                
                # SAFE Debug Save: Handles navigation errors inside save_debug_state
                await save_debug_state(self.search_id, page, last_error)
                
                # Force recreation on connection reset
                await self.close()
                self.context = None
                
            finally:
                if page and not page.is_closed():
                    try: await page.close()
                    except: pass
                        
            if attempt < MAX_RETRIES:
                await asyncio.sleep(2)
                
        return False, [], f"Playwright failed after {MAX_RETRIES} attempts. Last err: {last_error}"

    async def _auto_scroll(self, page: Page, max_scrolls: int, target_raw: int, eta_calc: ETACalculator) -> List[Dict[str, Any]]:
        accumulated_products = []
        last_height = 0
        
        for i in range(max_scrolls):
            products = await self._extract_products(page)
            accumulated_products = products
            
            found = len(accumulated_products)
            
            # Real ETA math calculation done in scraper engine
            pct = min(45, 15 + int((found / target_raw) * 30)) if target_raw > 0 else 15
            update_progress(
                self.search_id, 
                stage="scrolling", 
                percent=pct,
                found=found,
                elapsed_seconds=eta_calc.get_elapsed(),
                eta_seconds=eta_calc.get_eta(pct)
            )
            
            if found >= target_raw:
                break
                
            await page.mouse.wheel(0, 1500)
            await asyncio.sleep(1.5) 
            
            new_height = await page.evaluate("document.body.scrollHeight")
            if new_height == last_height:
                await page.mouse.wheel(0, -500)
                await asyncio.sleep(0.5)
                await page.mouse.wheel(0, 2000)
                await asyncio.sleep(1.5)
            last_height = new_height
            
        return accumulated_products

    async def _extract_products(self, page: Page) -> List[Dict[str, Any]]:
        js_code = """
        (selectors) => {
            const getEl = (root, selList) => {
                for (let s of selList) { let el = root.querySelector(s); if (el) return el; }
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
                if (titleEl && priceEl) {
                    let linkEl = card.querySelector('a');
                    let imgEl = getEl(card, selectors.IMAGE);
                    let shopEl = getEl(card, selectors.SHOP);
                    results.push({
                        id: 'prod_' + Math.random().toString(36).substr(2, 9),
                        title: titleEl.innerText.trim(),
                        price_text: priceEl.innerText.trim(),
                        shop: shopEl ? shopEl.innerText.trim() : 'Unknown',
                        image: imgEl ? imgEl.src : '',
                        link: linkEl ? linkEl.href : '',
                        source: 'playwright'
                    });
                }
            });
            return results;
        }
        """
        try:
            return await page.evaluate(js_code, {
                "CARD": TokopediaConfig.CARD_SELECTORS,
                "TITLE": TokopediaConfig.TITLE_SELECTORS,
                "PRICE": TokopediaConfig.PRICE_SELECTORS,
                "IMAGE": TokopediaConfig.IMAGE_SELECTORS,
                "SHOP": TokopediaConfig.SHOP_SELECTORS,
            })
        except:
            return []
