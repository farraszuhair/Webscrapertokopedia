import logging
import os
import random
import re
import shutil
import tempfile
import time
import urllib.parse
from typing import Any, Callable, Dict, List, Optional

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

logging.basicConfig(level=logging.INFO, format='[SCRAPER] %(message)s')


def clean_temp_files() -> None:
    temp_root = tempfile.gettempdir()
    safe_markers = ("marketspy_chrome_", "scoped_dir", "tmp", "chromedriver")
    try:
        for name in os.listdir(temp_root):
            lower = name.lower()
            if not any(marker in lower for marker in safe_markers):
                continue
            path = os.path.join(temp_root, name)
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path, ignore_errors=True)
                elif os.path.isfile(path):
                    os.remove(path)
            except Exception:
                # Never crash on temp cleanup failures.
                pass
    except Exception:
        pass

class TokopediaScraper:
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.results: List[Dict[str, Any]] = []

    async def search(
        self,
        keyword: str,
        max_halaman: int = 1,
        min_rating: float = 0.0,
        max_items: int = 50,
        should_cancel: Optional[Callable[[], bool]] = None
    ) -> List[Dict[str, Any]]:
        import asyncio
        return await asyncio.to_thread(
            self._search_sync,
            keyword,
            max_halaman,
            min_rating,
            max_items,
            should_cancel
        )

    def _search_sync(
        self,
        keyword: str,
        max_halaman: int = 1,
        min_rating: float = 0.0,
        max_items: int = 50,
        should_cancel: Optional[Callable[[], bool]] = None
    ) -> List[Dict[str, Any]]:
        self.results = []
        options = uc.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-web-security")
        options.add_argument("--start-maximized")
        options.add_argument("--lang=id-ID")

        driver = None
        temp_profile_dir = tempfile.mkdtemp(prefix="marketspy_chrome_")
        options.add_argument(f"--user-data-dir={temp_profile_dir}")
        try:
            driver = uc.Chrome(options=options, version_main=147, headless=self.headless)
            driver.set_page_load_timeout(60)

            unique_urls = set()
            keyword_lower = keyword.lower()
            negative_keywords = [
                "pad", "mousepad", "stiker", "sticker", "kabel",
                "cable", "grip", "case", "cover", "feet", "baterai"
            ]

            sort_codes = ["23", "5", "3"]
            max_cycles = 12
            stalled_cycles = 0
            cycle_idx = 0

            while len(self.results) < max_items and cycle_idx < max_cycles:
                cycle_idx += 1
                before_cycle = len(self.results)
                for ob_code in sort_codes:
                    if len(self.results) >= max_items:
                        break
                    if should_cancel and should_cancel():
                        logging.info("Scraping dibatalkan oleh user.")
                        return self.results
                if should_cancel and should_cancel():
                    logging.info("Scraping dibatalkan oleh user.")
                    break

                url = f"https://www.tokopedia.com/search?navsource=search&ob={ob_code}&q={urllib.parse.quote(keyword)}"
                tipe_sort = "Paling Sesuai" if ob_code == "23" else ("Ulasan Terbanyak" if ob_code == "5" else "Termurah")
                logging.info(f"Membuka URL (Filter: {tipe_sort})...")
                driver.get(url)

                try:
                    WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                except Exception:
                    logging.warning("Body halaman lambat tampil, lanjutkan dengan retry ringan.")

                self._inject_scanner_css(driver)
                self._scroll_page(driver, should_cancel)
                if should_cancel and should_cancel():
                    logging.info("Scraping dibatalkan saat proses scroll.")
                    break
                # Visual scan tambahan: pastikan kotak biru benar-benar jalan sampai bawah.
                self._visual_scan_full_page(driver, should_cancel)

                extracted_data = self._extract_cards(driver)
                search_words = [w for w in keyword_lower.split() if len(w) > 2]

                # Pass 1: filter ketat
                for item in extracted_data:
                    nama_lower = item["nama"].lower()
                    if nama_lower == "produk tokopedia":
                        continue

                    is_aksesoris = any(neg in nama_lower for neg in negative_keywords)
                    has_relevant_keyword = any(w in nama_lower for w in search_words) if search_words else True
                    harga_wajar = (
                        item["harga"] >= 100000
                        if ("mouse" in keyword_lower or "razer" in keyword_lower or "headset" in keyword_lower or "rtx" in keyword_lower)
                        else item["harga"] >= 5000
                    )

                    if (
                        item["url"] not in unique_urls
                        and item.get("rating_toko", 0.0) >= min_rating
                        and not is_aksesoris
                        and harga_wajar
                        and has_relevant_keyword
                    ):
                        unique_urls.add(item["url"])
                        self.results.append(item)
                        if len(self.results) >= max_items:
                            logging.info(f"Target scrape tercapai ({max_items} produk).")
                            return self.results

                # Pass 2: kalau masih kurang target, longgarkan keyword filter agar muat lebih banyak.
                if len(self.results) < max_items:
                    for item in extracted_data:
                        if item["url"] in unique_urls:
                            continue
                        nama_lower = item["nama"].lower()
                        if nama_lower == "produk tokopedia":
                            continue
                        is_aksesoris = any(neg in nama_lower for neg in negative_keywords)
                        if is_aksesoris:
                            continue
                        if item.get("rating_toko", 0.0) < min_rating:
                            continue
                        unique_urls.add(item["url"])
                        self.results.append(item)
                        if len(self.results) >= max_items:
                            logging.info(f"Target scrape tercapai ({max_items} produk) [relaxed filter].")
                            return self.results
                    logging.info(f"Selesai Filter {tipe_sort}. Total terkumpul: {len(self.results)} produk.")

                if len(self.results) == before_cycle:
                    stalled_cycles += 1
                else:
                    stalled_cycles = 0
                if stalled_cycles >= 2:
                    logging.info("Tidak ada data baru setelah beberapa siklus, stop scraping.")
                    break
            return self.results
        finally:
            if driver:
                try:
                    driver.quit()
                except Exception:
                    pass
            try:
                shutil.rmtree(temp_profile_dir, ignore_errors=True)
            except Exception:
                pass
            clean_temp_files()

    def _inject_scanner_css(self, driver: uc.Chrome) -> None:
        driver.execute_script(
            """
            const oldStyle = document.getElementById('marketspy-scanner-style');
            if (oldStyle) oldStyle.remove();
            const style = document.createElement('style');
            style.id = 'marketspy-scanner-style';
            style.textContent = `
                .marketspy-scanner {
                    outline: 3px solid #99C3FF !important;
                    background-color: rgba(153, 195, 255, 0.12) !important;
                    box-shadow: 0 0 16px rgba(153, 195, 255, 0.6) !important;
                    border-radius: 6px !important;
                    position: relative !important;
                }
                .marketspy-scanner::before {
                    content: 'AI SCANNING...';
                    position: absolute;
                    top: -18px;
                    left: 0;
                    font-size: 11px;
                    font-weight: bold;
                    background: #99C3FF;
                    color: #111;
                    padding: 2px 6px;
                    border-radius: 4px;
                    z-index: 9999;
                }
            `;
            document.head.appendChild(style);
            """
        )

    def _scroll_page(self, driver: uc.Chrome, should_cancel: Optional[Callable[[], bool]]) -> None:
        # Scroll adaptif: lanjut sampai tinggi dokumen tidak bertambah lagi.
        stable_rounds = 0
        prev_height = 0
        max_rounds = 22
        for _ in range(max_rounds):
            if should_cancel and should_cancel():
                break
            driver.execute_script("window.scrollBy(0, Math.floor(window.innerHeight * 0.55));")
            self._highlight_scan_boxes(driver)
            time.sleep(random.uniform(0.95, 1.45))
            current_height = driver.execute_script("return document.body.scrollHeight || 0;")
            if current_height <= prev_height:
                stable_rounds += 1
            else:
                stable_rounds = 0
            prev_height = current_height
            if stable_rounds >= 3:
                break
        # Final pass supaya card yang baru muncul tetap kena kotak biru
        for _ in range(2):
            if should_cancel and should_cancel():
                break
            self._highlight_scan_boxes(driver)
            time.sleep(0.55)

    def _visual_scan_full_page(self, driver: uc.Chrome, should_cancel: Optional[Callable[[], bool]]) -> None:
        # Mulai dari atas agar user lihat scan "menyapu" dari atas ke bawah.
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(0.35)
        max_rounds = 24
        for _ in range(max_rounds):
            if should_cancel and should_cancel():
                break
            self._highlight_scan_boxes(driver)
            driver.execute_script("window.scrollBy(0, Math.floor(window.innerHeight * 0.45));")
            time.sleep(0.45)
            reached_bottom = driver.execute_script(
                "return (window.innerHeight + window.scrollY) >= (document.body.scrollHeight - 8);"
            )
            if reached_bottom:
                self._highlight_scan_boxes(driver)
                break

    def _highlight_scan_boxes(self, driver: uc.Chrome) -> None:
        driver.execute_script(
            """
            const pickCardContainer = (anchor) => {
                let node = anchor;
                let best = null;
                for (let i = 0; i < 9 && node; i += 1) {
                    const rect = node.getBoundingClientRect ? node.getBoundingClientRect() : null;
                    const hasImg = !!(node.querySelector && node.querySelector('img'));
                    const hasPriceText = !!(node.innerText && node.innerText.includes('Rp'));
                    if (rect && hasImg && hasPriceText) {
                        const validSize = rect.width >= 160 && rect.width <= 450 && rect.height >= 180 && rect.height <= 650;
                        if (validSize) {
                            best = node;
                            break; // gunakan card terdekat supaya tidak nyatu jadi 1 kotak besar
                        }
                    }
                    node = node.parentElement;
                }
                return best;
            };

            const anchors = Array.from(document.querySelectorAll('a[href*="tokopedia.com"]'))
                .filter(a => a.innerText && a.innerText.includes('Rp'))
                .slice(0, 120);

            anchors.forEach((anchor, idx) => {
                const node = pickCardContainer(anchor);
                if (!node) return;

                node.classList.add('marketspy-scanner');
                node.style.setProperty('border', '2px solid #99C3FF', 'important');
                node.style.setProperty('outline', '2px solid #99C3FF', 'important');
                node.style.setProperty('outline-offset', '-1px', 'important');
                node.style.setProperty('box-shadow', '0 0 16px rgba(153,195,255,0.65)', 'important');
                node.style.setProperty('position', 'relative', 'important');
                node.style.setProperty('transition', 'all .18s ease', 'important');
                node.style.setProperty('animation-delay', `${(idx % 12) * 90}ms`, 'important');
                node.setAttribute('data-marketspy-scan', String(idx));
            });
            """
        )

    def _extract_cards(self, driver: uc.Chrome) -> List[Dict[str, Any]]:
        extracted_data = driver.execute_script(
            r"""
            const results = [];
            const seenUrls = new Set();
            const pickCardContainer = (anchor) => {
                let node = anchor;
                let best = null;
                for (let i = 0; i < 9 && node; i += 1) {
                    const rect = node.getBoundingClientRect ? node.getBoundingClientRect() : null;
                    const hasImg = !!(node.querySelector && node.querySelector('img'));
                    const hasPriceText = !!(node.innerText && node.innerText.includes('Rp'));
                    if (rect && hasImg && hasPriceText) {
                        const validSize = rect.width >= 160 && rect.width <= 450 && rect.height >= 180 && rect.height <= 650;
                        if (validSize) {
                            best = node;
                            break;
                        }
                    }
                    node = node.parentElement;
                }
                return best;
            };

            const anchors = Array.from(document.querySelectorAll('a[href*="tokopedia.com"]'))
                .filter(a => a.innerText && a.innerText.includes('Rp'));

            anchors.forEach(anchor => {
                const container = pickCardContainer(anchor);
                if (!container) return;
                container.classList.add('marketspy-scanner');

                const url = (anchor.href || '').split('?')[0];
                if (!url || seenUrls.has(url) || url.includes('/p/')) return;

                const rawText = container.innerText || '';
                let nameNode = container.querySelector('[data-testid="spnSRPProdName"], [data-testid="linkProductName"], [class*="product-name"], [class*="prd_link-product-name"], h3, h2');
                let nama = nameNode ? nameNode.innerText.trim() : '';
                if (!nama || nama.length < 5) {
                    const textNodes = Array.from(container.querySelectorAll('*')).filter(el =>
                        el.children.length === 0 &&
                        el.innerText &&
                        el.innerText.length > 15 &&
                        !el.innerText.includes('Rp') &&
                        !el.innerText.toLowerCase().includes('terjual')
                    );
                    if (textNodes.length > 0) {
                        nama = textNodes.sort((a, b) => b.innerText.length - a.innerText.length)[0].innerText.trim();
                    } else {
                        nama = 'Produk Tokopedia';
                    }
                }

                const priceMatch = rawText.match(/Rp\s*[0-9.,]+/);
                const harga = priceMatch ? parseInt(priceMatch[0].replace(/[^0-9]/g, ''), 10) : 0;
                if (!harga || harga < 1000) return;

                const ratingMatch = rawText.match(/([4-5]\.\d)/);
                const rating = ratingMatch ? parseFloat(ratingMatch[1]) : 0.0;

                const soldMatch = rawText.match(/(\d+(?:\.\d+)?(?:rb|jt)?\+?)\s*(?:terjual|sold)/i);
                const terjual = soldMatch ? soldMatch[1] : '0';

                const shopNode = container.querySelector('[data-testid*="shop"], [class*="shop-name"]');
                const toko = shopNode ? shopNode.innerText.trim() : 'Official/Power Merchant';

                seenUrls.add(url);
                results.push({
                    nama,
                    harga,
                    toko,
                    rating_toko: rating,
                    terjual,
                    url,
                    image: (container.querySelector('img') || {}).src || ''
                });
            });
            return results;
            """
        )
        normalized: List[Dict[str, Any]] = []
        for item in extracted_data or []:
            try:
                item["harga"] = int(item.get("harga", 0))
                rating_raw = item.get("rating_toko", 0.0)
                rating_val = float(rating_raw) if str(rating_raw).strip() else 0.0
                item["rating_toko"] = float(re.sub(r"[^0-9.]", "", str(rating_val)) or 0.0)
                normalized.append(item)
            except Exception:
                continue
        return normalized

    def to_dict_list(self) -> List[Dict[str, Any]]:
        return self.results