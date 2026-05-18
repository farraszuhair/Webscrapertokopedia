import asyncio
import time
import random
import re
import urllib.parse
from typing import Tuple, List, Dict, Any
from src.utils.logger import log
from src.server.progress import update_progress
from src.utils.debug import save_debug_state_sync

class RollbackEngine:
    name = "rollback"
    
    def __init__(self, search_id: str):
        self.search_id = search_id
        
    async def scrape(self, query: str, raw_target: int, eta_calc) -> Tuple[bool, List[Dict[str, Any]], str]:
        # Run blocking selenium code in thread so it respects asyncio
        return await asyncio.to_thread(self._scrape_sync, query, raw_target, eta_calc)
        
    def _scrape_sync(self, query: str, raw_target: int, eta_calc) -> Tuple[bool, List[Dict[str, Any]], str]:
        import undetected_chromedriver as uc
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.ui import WebDriverWait
        import tempfile
        import shutil
        import os
        
        log(f"[{self.search_id}]", "[ROLLBACK] Starting legacy scraper from ROLLBACK.rar logic", "INFO")
        
        options = uc.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--headless")
        options.add_argument("--window-size=1920,1080")
        
        temp_profile_dir = tempfile.mkdtemp(prefix="marketspy_chrome_")
        options.add_argument(f"--user-data-dir={temp_profile_dir}")
        
        driver = None
        results = []
        unique_urls = set()
        
        try:
            update_progress(self.search_id, engine=self.name, stage="rollback_starting", percent=50, message="Menyiapkan browser fallback...")
            
            # Using version 120 or similar, but uc.Chrome might fetch automatically
            driver = uc.Chrome(options=options, version_main=120)
            driver.set_page_load_timeout(30)
            
            url = f"https://www.tokopedia.com/search?navsource=search&q={urllib.parse.quote(query)}"
            update_progress(self.search_id, stage="rollback_starting", percent=55, message="Membuka Tokopedia...")
            driver.get(url)
            
            try:
                WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            except Exception:
                pass # Continue anyway
                
            update_progress(self.search_id, stage="rollback_extracting", percent=60, message="Mencari produk...")
            
            # Scroll loop
            prev_height = 0
            stable_rounds = 0
            for _ in range(15):
                driver.execute_script("window.scrollBy(0, Math.floor(window.innerHeight * 0.65));")
                time.sleep(random.uniform(1.0, 1.5))
                
                current_height = driver.execute_script("return document.body.scrollHeight || 0;")
                if current_height <= prev_height:
                    stable_rounds += 1
                else:
                    stable_rounds = 0
                prev_height = current_height
                
                if stable_rounds >= 3:
                    break
                    
                # Extraksi in each scroll
                extracted = self._extract_cards(driver)
                for item in extracted:
                    if item["url"] not in unique_urls:
                        unique_urls.add(item["url"])
                        results.append(item)
                        
                update_progress(self.search_id, stage="rollback_extracting", percent=min(70, 60 + int((len(results)/raw_target)*10)), found=len(results), elapsed_seconds=eta_calc.get_elapsed())
                if len(results) >= raw_target:
                    break
            
            if results:
                log(f"[{self.search_id}]", f"[ROLLBACK] Extracted {len(results)} raw products", "OK")
                return True, results, ""
            return False, [], "Tidak ada produk ditemukan di Tokopedia (Fallback)"
            
        except Exception as e:
            err = str(e)
            log(f"[{self.search_id}]", f"[ROLLBACK] Error: {err}", "ERROR")
            if driver:
                save_debug_state_sync(self.search_id, driver, err)
            return False, [], f"Fallback scraper error: {err}"
        finally:
            if driver:
                try:
                    driver.quit()
                except: pass
            try:
                shutil.rmtree(temp_profile_dir, ignore_errors=True)
            except: pass

    def _extract_cards(self, driver) -> List[Dict[str, Any]]:
        extracted_data = driver.execute_script(
            r"""
            const results = [];
            const anchors = Array.from(document.querySelectorAll('a[href*="tokopedia.com"]')).filter(a => a.innerText && a.innerText.includes('Rp'));
            anchors.forEach(anchor => {
                const url = (anchor.href || '').split('?')[0];
                if (!url || url.includes('/p/')) return;

                const rawText = anchor.innerText || '';
                const lines = rawText.split('\n');
                let nama = lines[0] || 'Produk Tokopedia';
                
                const priceMatch = rawText.match(/Rp\s*[0-9.,]+/);
                const harga = priceMatch ? parseInt(priceMatch[0].replace(/[^0-9]/g, ''), 10) : 0;
                if (!harga || harga < 1000) return;

                const ratingMatch = rawText.match(/([4-5]\.\d)/);
                const rating = ratingMatch ? parseFloat(ratingMatch[1]) : 0.0;

                const soldMatch = rawText.match(/(\d+(?:\.\d+)?(?:rb|jt)?\+?)\s*(?:terjual|sold)/i);
                const terjual = soldMatch ? soldMatch[1] : '0';

                // Basic shop parsing if possible, or leave as unknown
                let toko = "Official/Power Merchant";

                results.push({
                    nama: nama,
                    title: nama,
                    harga: harga,
                    price_val: harga,
                    price_text: priceMatch[0],
                    shop: toko,
                    rating_toko: rating,
                    terjual: terjual,
                    link: url,
                    url: url,
                    source: "rollback"
                });
            });
            return results;
            """
        )
        normalized = []
        for item in extracted_data or []:
            try:
                item["harga"] = int(item.get("harga", 0))
                normalized.append(item)
            except Exception:
                pass
        return normalized
