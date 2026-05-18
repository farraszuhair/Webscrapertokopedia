"""
tokopedia.py - Tokopedia specific selectors and URL builders.
"""
import urllib.parse

class TokopediaConfig:
    # Multi-fallback selectors since Tokopedia changes classes often.
    CARD_SELECTORS = [
        "div.pcv3__container",
        "div.css-1asz3by",
        "div[data-testid='master-product-card']"
    ]
    
    TITLE_SELECTORS = [
        "div[data-testid='spnSRPProdName']",
        ".prd_link-product-name",
        "div.css-1b6t4dn"
    ]
    
    PRICE_SELECTORS = [
        "div[data-testid='spnSRPProdPrice']",
        ".prd_link-product-price",
        "div.css-1ksb19c"
    ]
    
    SHOP_SELECTORS = [
        "span[data-testid='spnSRPProdTabShopLoc']",
        ".prd_link-shop-loc",
        "span.prd_link-shop-name",
        ".css-1kdc32b"
    ]

    RATING_SELECTORS = [
        "span.prd_rating-average-text",
        ".css-t70b7i"
    ]

    SOLD_SELECTORS = [
        "span.prd_label-integrity",
        ".css-1duhs3e"
    ]
    
    IMAGE_SELECTORS = [
        "img[data-testid='imgSRPProdMain']",
        "img.css-1c345mg"
    ]

    @staticmethod
    def build_search_url(query: str) -> str:
        """Builds Tokopedia search URL sorted by best match or popular."""
        encoded_query = urllib.parse.quote(query)
        # sort=5 is typically newest or most relevant. 
        # For relevance, sort=23 (best match) or default is good. We use default (sort=8 or no sort).
        return f"https://www.tokopedia.com/search?q={encoded_query}"
