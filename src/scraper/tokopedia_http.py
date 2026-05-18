"""
tokopedia_http.py - Fast HTTP-based scraper.
Attempts to extract SSR data without launching a full browser.
"""
import httpx
import json
import re
from typing import List, Dict, Any, Tuple
from bs4 import BeautifulSoup
from src.scraper.base import BaseEngine
from src.utils.logger import log
from src.utils.eta import ETACalculator
from src.server.progress import update_progress
from src.scraper.tokopedia import TokopediaConfig
from src.utils.debug import get_debug_dir

class HttpEngine(BaseEngine):
    async def scrape(self, query: str, raw_target: int, eta_calc: ETACalculator) -> Tuple[bool, List[Dict[str, Any]], str]:
        url = TokopediaConfig.build_search_url(query)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Upgrade-Insecure-Requests": "1",
        }
        
        log(f"[{self.search_id}]", f"[HTTP] Fetching {url}", "INFO")
        update_progress(
            self.search_id,
            engine="http_api",
            stage="http_fetching",
            percent=10,
            message="Fetching data via HTTP API..."
        )
        
        try:
            async with httpx.AsyncClient(headers=headers, timeout=15.0, http2=True) as client:
                response = await client.get(url)
                
            if response.status_code != 200:
                return False, [], f"HTTP returned status {response.status_code}"
                
            html = response.text
            
            # Simple check for captcha/block
            if "captcha" in html.lower() or "verifikasi" in html.lower() or "tunggu sebentar" in html.lower():
                return False, [], "HTTP blocked by anti-bot/captcha"
                
            # Attempt to extract initial state JSON from script tag
            # Often window.__INITIAL_STATE__ or similar
            # If we can't find it, we fallback to browser
            match = re.search(r'window\.__INITIAL_STATE__\s*=\s*(\{.*?\});', html, re.DOTALL)
            if not match:
                # Save debug if needed to see what we got
                debug_path = get_debug_dir(self.search_id) / "http_failed.html"
                with open(debug_path, "w", encoding="utf-8") as f:
                    f.write(html)
                return False, [], "No SSR JSON found in HTML. Tokopedia layout may require browser."
                
            try:
                data = json.loads(match.group(1))
                # Note: Tokopedia's actual data structure is highly nested and obfuscated GraphQL responses.
                # If we cannot reliably parse this here without breaking frequently, we immediately return False.
                # For this implementation, we will simulate the extraction attempt, and likely fail gracefully 
                # (since extracting from Tokopedia's complex Apollo state is brittle) to trigger Playwright.
                
                # We will try a fast regex over the HTML for product cards instead as a fallback
                products = self._parse_html(html)
                if products:
                    update_progress(self.search_id, found=len(products), percent=30)
                    return True, products, ""
                else:
                    return False, [], "Failed to parse products from HTTP response."
                    
            except Exception as e:
                return False, [], f"Error parsing JSON state: {e}"
                
        except Exception as e:
            return False, [], f"HTTP request failed: {e}"
            
    def _parse_html(self, html: str) -> List[Dict[str, Any]]:
        """Attempt to parse SSR HTML directly."""
        soup = BeautifulSoup(html, 'html.parser')
        products = []
        
        for sel in TokopediaConfig.CARD_SELECTORS:
            cards = soup.select(sel)
            if cards:
                for card in cards:
                    p = self._extract_card(card)
                    if p: products.append(p)
                if products:
                    break
        return products
        
    def _extract_card(self, card) -> Dict[str, Any]:
        def get_text(selectors):
            for sel in selectors:
                el = card.select_one(sel)
                if el: return el.get_text(strip=True)
            return None
            
        title = get_text(TokopediaConfig.TITLE_SELECTORS)
        price = get_text(TokopediaConfig.PRICE_SELECTORS)
        
        if not title or not price:
            return None
            
        link_el = card.find('a')
        link = link_el['href'] if link_el and 'href' in link_el.attrs else ""
        
        img_el = card.find('img')
        img = img_el['src'] if img_el and 'src' in img_el.attrs else ""
        
        return {
            "id": f"prod_{hash(title)}",
            "title": title,
            "price_text": price,
            "shop": get_text(TokopediaConfig.SHOP_SELECTORS) or "Unknown",
            "rating": get_text(TokopediaConfig.RATING_SELECTORS),
            "sold": get_text(TokopediaConfig.SOLD_SELECTORS),
            "image": img,
            "link": link,
            "source": "tokopedia_http"
        }
