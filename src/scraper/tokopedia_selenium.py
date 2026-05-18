"""
tokopedia_selenium.py - Selenium (undetected-chromedriver) engine.
Runs in a separate thread so it doesn't block the FastAPI async event loop.
"""
import asyncio
from typing import List, Dict, Any, Tuple
from src.scraper.base import BaseEngine
from src.utils.logger import log
from src.utils.eta import ETACalculator
from src.server.progress import update_progress
from src.scraper.tokopedia import TokopediaConfig
from src.utils.debug import save_debug_state_sync

class SeleniumEngine(BaseEngine):
    def __init__(self, search_id: str):
        super().__init__(search_id)
        self.driver = None

    async def scrape(self, query: str, raw_target: int, eta_calc: ETACalculator) -> Tuple[bool, List[Dict[str, Any]], str]:
        # Run blocking selenium code in thread
        return await asyncio.to_thread(self._scrape_sync, query, raw_target, eta_calc)
        
    def _scrape_sync(self, query: str, raw_target: int, eta_calc: ETACalculator) -> Tuple[bool, List[Dict[str, Any]], str]:
        import undetected_chromedriver as uc
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        import time

        url = TokopediaConfig.build_search_url(query)
        MAX_RETRIES = 1 # Selenium is heavy, only try once here as it's the last resort
        last_error = ""
        
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                log(f"[{self.search_id}]", "[SEL] Launching undetected-chromedriver...", "INFO")
                update_progress(self.search_id, engine="selenium", stage="browser_launching", message="Membuka browser (Selenium)...")
                
                options = uc.ChromeOptions()
                options.add_argument('--headless')
                options.add_argument('--disable-gpu')
                options.add_argument('--no-sandbox')
                
                self.driver = uc.Chrome(options=options, version_main=120) # You can adjust version if needed
                self.driver.set_page_load_timeout(30)
                
                log(f"[{self.search_id}]", f"[SEL] Opening URL: {url}", "INFO")
                update_progress(self.search_id, stage="browser_opening", percent=12)
                
                self.driver.get(url)
                time.sleep(3) # Initial render wait
                
                # Scroll loop
                accumulated_products = []
                last_height = self.driver.execute_script("return document.body.scrollHeight")
                
                for i in range(10):
                    products = self._extract_sync(self.driver)
                    accumulated_products = products
                    found = len(products)
                    
                    pct = min(45, 15 + int((found / raw_target) * 30)) if raw_target > 0 else 15
                    update_progress(
                        self.search_id, 
                        stage="scrolling", 
                        percent=pct,
                        found=found,
                        elapsed_seconds=eta_calc.get_elapsed(),
                        eta_seconds=eta_calc.get_eta(pct)
                    )
                    
                    if found >= raw_target:
                        break
                        
                    self.driver.execute_script("window.scrollBy(0, 1500);")
                    time.sleep(1.5)
                    
                    new_height = self.driver.execute_script("return document.body.scrollHeight")
                    if new_height == last_height:
                        break
                    last_height = new_height
                    
                if accumulated_products:
                    return True, accumulated_products, ""
                else:
                    last_error = "No products found by Selenium."
                    
            except Exception as e:
                last_error = str(e)
                log(f"[{self.search_id}]", f"[SEL] Error: {last_error}", "WARN")
                save_debug_state_sync(self.search_id, self.driver, last_error)
            finally:
                self.close_sync()
                
        return False, [], f"Selenium failed: {last_error}"

    def _extract_sync(self, driver) -> List[Dict[str, Any]]:
        js_code = """
        const selectors = arguments[0];
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
                    source: 'selenium'
                });
            }
        });
        return results;
        """
        try:
            return driver.execute_script(js_code, {
                "CARD": TokopediaConfig.CARD_SELECTORS,
                "TITLE": TokopediaConfig.TITLE_SELECTORS,
                "PRICE": TokopediaConfig.PRICE_SELECTORS,
                "IMAGE": TokopediaConfig.IMAGE_SELECTORS,
                "SHOP": TokopediaConfig.SHOP_SELECTORS,
            })
        except:
            return []

    async def close(self):
        await asyncio.to_thread(self.close_sync)
        
    def close_sync(self):
        try:
            if self.driver:
                self.driver.quit()
        except:
            pass
        self.driver = None
