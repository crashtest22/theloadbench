"""
components.py - Component Price/Stock Tracker for The Load Bench
Scrapes powder, primer, brass, and bullet availability from major reloading suppliers.
"""

import requests
import time
import logging
import re
from bs4 import BeautifulSoup
from typing import List, Dict, Optional

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

REQUEST_DELAY = 1.5  # seconds between requests

# --- Search terms for each component category ---
POWDERS = ["H4350", "Varget", "N140", "N150", "IMR 4064", "CFE 223",
           "H4831", "H1000", "H4895", "Retumbo", "Hodgdon Extreme"]
PRIMERS = ["Federal 210M", "Federal 205M", "CCI 400", "CCI 450",
           "BR4", "BR2", "Remington 9.5M", "Federal GM210M", "Federal GM205M"]
BRASS = ["6GT brass", ".308 Win brass", ".223 Rem brass", "9mm brass", ".45 ACP brass",
         "Lapua 308", "Lapua 223", "Starline 308", "Peterson 308", "Alpha 6GT"]
BULLETS = ["6GT 105gr", "6GT 110gr", "6GT 115gr", "175gr SMK", "185gr Juggernaut",
           "77gr SMK", "308 175 grain", "Sierra MatchKing"]


def safe_get(url: str, session: requests.Session, retries: int = 2) -> Optional[requests.Response]:
    """GET with retries and error handling."""
    for attempt in range(retries):
        try:
            resp = session.get(url, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            return resp
        except requests.exceptions.HTTPError as e:
            logger.warning(f"HTTP {e.response.status_code} for {url}")
            return None
        except requests.exceptions.RequestException as e:
            logger.warning(f"Request failed ({attempt+1}/{retries}) for {url}: {e}")
            if attempt < retries - 1:
                time.sleep(2)
    return None


def normalize_price(text: str) -> Optional[str]:
    """Extract price from text."""
    if not text:
        return None
    match = re.search(r'\$[\d,]+\.?\d*', text)
    return match.group(0) if match else None


# -------------------------------------------------------
# Powder Valley
# -------------------------------------------------------
def scrape_powder_valley(session: requests.Session, search_terms: List[str]) -> List[Dict]:
    """Scrape powdervalleyinc.com for powder/primer availability."""
    results = []
    base_url = "https://www.powdervalleyinc.com"
    search_url = "https://www.powdervalleyinc.com/search?q="

    for term in search_terms[:8]:  # limit to avoid hammering
        url = f"{search_url}{requests.utils.quote(term)}"
        logger.info(f"Powder Valley: searching '{term}'")
        resp = safe_get(url, session)
        time.sleep(REQUEST_DELAY)

        if not resp:
            logger.warning(f"Powder Valley: blocked or error for '{term}'")
            results.append({
                "source": "Powder Valley",
                "name": term,
                "price": None,
                "in_stock": None,
                "url": url,
                "note": "Could not retrieve page — check site manually",
            })
            continue

        soup = BeautifulSoup(resp.text, "lxml")

        # Try common product card patterns
        products = soup.select(".product-item, .product-card, article.product, .grid-item")
        if not products:
            # Fallback: any element with price class
            products = soup.select("[class*='product']")

        found = False
        for prod in products[:3]:
            name_el = prod.select_one("h2, h3, .product-title, .product-name, a[class*='title']")
            price_el = prod.select_one(".price, .product-price, [class*='price']")
            link_el = prod.select_one("a[href]")
            stock_el = prod.select_one("[class*='stock'], [class*='inventory'], [class*='availability']")

            name = name_el.get_text(strip=True) if name_el else term
            price = normalize_price(price_el.get_text(strip=True)) if price_el else None
            href = link_el.get("href", "") if link_el else ""
            product_url = href if href.startswith("http") else base_url + href
            stock_text = stock_el.get_text(strip=True).lower() if stock_el else ""
            in_stock = None
            if stock_text:
                in_stock = "out" not in stock_text and "unavailable" not in stock_text

            results.append({
                "source": "Powder Valley",
                "name": name,
                "price": price,
                "in_stock": in_stock,
                "url": product_url or url,
                "note": None,
            })
            found = True

        if not found:
            results.append({
                "source": "Powder Valley",
                "name": term,
                "price": None,
                "in_stock": None,
                "url": url,
                "note": "No products found in search results — check site manually",
            })

    return results


# -------------------------------------------------------
# Midsouth Shooters Supply
# -------------------------------------------------------
def scrape_midsouth(session: requests.Session, search_terms: List[str]) -> List[Dict]:
    """Scrape midsouthshooterssupply.com."""
    results = []
    base_url = "https://www.midsouthshooterssupply.com"
    search_url = "https://www.midsouthshooterssupply.com/c/search?q="

    for term in search_terms[:8]:
        url = f"{search_url}{requests.utils.quote(term)}"
        logger.info(f"Midsouth: searching '{term}'")
        resp = safe_get(url, session)
        time.sleep(REQUEST_DELAY)

        if not resp:
            results.append({
                "source": "Midsouth Shooters Supply",
                "name": term,
                "price": None,
                "in_stock": None,
                "url": url,
                "note": "Could not retrieve page — check site manually",
            })
            continue

        soup = BeautifulSoup(resp.text, "lxml")
        products = soup.select(".product-tile, .product-item, .product-card, [class*='product-grid'] > div")

        found = False
        for prod in products[:3]:
            name_el = prod.select_one(".product-name, h2, h3, [class*='title']")
            price_el = prod.select_one(".product-price, .price, [class*='price']")
            link_el = prod.select_one("a[href]")
            stock_el = prod.select_one("[class*='stock'], [class*='availability'], .add-to-cart")

            name = name_el.get_text(strip=True) if name_el else term
            price = normalize_price(price_el.get_text(strip=True)) if price_el else None
            href = link_el.get("href", "") if link_el else ""
            product_url = href if href.startswith("http") else base_url + href
            stock_text = (stock_el.get_text(strip=True) or "").lower() if stock_el else ""
            in_stock = None
            if stock_text:
                in_stock = "out" not in stock_text and "sold out" not in stock_text

            results.append({
                "source": "Midsouth Shooters Supply",
                "name": name,
                "price": price,
                "in_stock": in_stock,
                "url": product_url or url,
                "note": None,
            })
            found = True

        if not found:
            results.append({
                "source": "Midsouth Shooters Supply",
                "name": term,
                "price": None,
                "in_stock": None,
                "url": url,
                "note": "No products found — check site manually",
            })

    return results


# -------------------------------------------------------
# Graf & Sons
# -------------------------------------------------------
def scrape_grafs(session: requests.Session, search_terms: List[str]) -> List[Dict]:
    """Scrape grafs.com."""
    results = []
    base_url = "https://www.grafs.com"
    search_url = "https://www.grafs.com/?s="

    for term in search_terms[:8]:
        url = f"{search_url}{requests.utils.quote(term)}"
        logger.info(f"Graf & Sons: searching '{term}'")
        resp = safe_get(url, session)
        time.sleep(REQUEST_DELAY)

        if not resp:
            results.append({
                "source": "Graf & Sons",
                "name": term,
                "price": None,
                "in_stock": None,
                "url": url,
                "note": "Could not retrieve page — check site manually",
            })
            continue

        soup = BeautifulSoup(resp.text, "lxml")
        products = soup.select(".product, .product-item, .search-result, [class*='product-card']")

        found = False
        for prod in products[:3]:
            name_el = prod.select_one("h2, h3, .product-name, .product-title, [class*='name']")
            price_el = prod.select_one(".price, .product-price, [class*='price']")
            link_el = prod.select_one("a[href]")
            stock_el = prod.select_one("[class*='stock'], [class*='avail'], .out-of-stock, .in-stock")

            name = name_el.get_text(strip=True) if name_el else term
            price = normalize_price(price_el.get_text(strip=True)) if price_el else None
            href = link_el.get("href", "") if link_el else ""
            product_url = href if href.startswith("http") else base_url + href
            stock_text = (stock_el.get_text(strip=True) or "").lower() if stock_el else ""
            in_stock = None
            if stock_text:
                in_stock = "in stock" in stock_text or ("out" not in stock_text and "unavailable" not in stock_text)

            results.append({
                "source": "Graf & Sons",
                "name": name,
                "price": price,
                "in_stock": in_stock,
                "url": product_url or url,
                "note": None,
            })
            found = True

        if not found:
            results.append({
                "source": "Graf & Sons",
                "name": term,
                "price": None,
                "in_stock": None,
                "url": url,
                "note": "No products found — check site manually",
            })

    return results


# -------------------------------------------------------
# Widener's
# -------------------------------------------------------
def scrape_wideners(session: requests.Session, search_terms: List[str]) -> List[Dict]:
    """Scrape wideners.com."""
    results = []
    base_url = "https://www.wideners.com"
    search_url = "https://www.wideners.com/?s="

    for term in search_terms[:8]:
        url = f"{search_url}{requests.utils.quote(term)}"
        logger.info(f"Widener's: searching '{term}'")
        resp = safe_get(url, session)
        time.sleep(REQUEST_DELAY)

        if not resp:
            results.append({
                "source": "Widener's",
                "name": term,
                "price": None,
                "in_stock": None,
                "url": url,
                "note": "Could not retrieve page — check site manually",
            })
            continue

        soup = BeautifulSoup(resp.text, "lxml")
        products = soup.select(".product, .woocommerce-loop-product, li.product, [class*='product-item']")

        found = False
        for prod in products[:3]:
            name_el = prod.select_one("h2, h3, .woocommerce-loop-product__title, [class*='title']")
            price_el = prod.select_one(".price, .woocommerce-Price-amount, [class*='price']")
            link_el = prod.select_one("a[href]")
            stock_el = prod.select_one("[class*='stock'], .stock, .out-of-stock")

            name = name_el.get_text(strip=True) if name_el else term
            price = normalize_price(price_el.get_text(strip=True)) if price_el else None
            href = link_el.get("href", "") if link_el else ""
            product_url = href if href.startswith("http") else base_url + href
            stock_text = (stock_el.get_text(strip=True) or "").lower() if stock_el else ""
            in_stock = None
            if stock_text:
                in_stock = "in stock" in stock_text

            results.append({
                "source": "Widener's",
                "name": name,
                "price": price,
                "in_stock": in_stock,
                "url": product_url or url,
                "note": None,
            })
            found = True

        if not found:
            results.append({
                "source": "Widener's",
                "name": term,
                "price": None,
                "in_stock": None,
                "url": url,
                "note": "No products found — check site manually",
            })

    return results


# -------------------------------------------------------
# Lucky Gunner
# -------------------------------------------------------
def scrape_lucky_gunner(session: requests.Session, search_terms: List[str]) -> List[Dict]:
    """Scrape luckygunner.com for brass and bullets."""
    results = []
    base_url = "https://www.luckygunner.com"
    search_url = "https://www.luckygunner.com/reloading-supplies?q="

    for term in search_terms[:8]:
        url = f"{search_url}{requests.utils.quote(term)}"
        logger.info(f"Lucky Gunner: searching '{term}'")
        resp = safe_get(url, session)
        time.sleep(REQUEST_DELAY)

        if not resp:
            results.append({
                "source": "Lucky Gunner",
                "name": term,
                "price": None,
                "in_stock": None,
                "url": url,
                "note": "Could not retrieve page — check site manually",
            })
            continue

        soup = BeautifulSoup(resp.text, "lxml")
        products = soup.select(".product, .product-info, .ammo-listing, [class*='product-box']")

        found = False
        for prod in products[:3]:
            name_el = prod.select_one("h2, h3, .product-name, .ammo-name, [class*='title']")
            price_el = prod.select_one(".price, .cost, [class*='price']")
            link_el = prod.select_one("a[href]")
            # Lucky Gunner typically shows in-stock items prominently
            stock_el = prod.select_one("[class*='stock'], [class*='avail'], .out-of-stock")

            name = name_el.get_text(strip=True) if name_el else term
            price = normalize_price(price_el.get_text(strip=True)) if price_el else None
            href = link_el.get("href", "") if link_el else ""
            product_url = href if href.startswith("http") else base_url + href
            stock_text = (stock_el.get_text(strip=True) or "").lower() if stock_el else ""
            in_stock = None
            if stock_text:
                in_stock = "out" not in stock_text

            results.append({
                "source": "Lucky Gunner",
                "name": name,
                "price": price,
                "in_stock": in_stock,
                "url": product_url or url,
                "note": None,
            })
            found = True

        if not found:
            results.append({
                "source": "Lucky Gunner",
                "name": term,
                "price": None,
                "in_stock": None,
                "url": url,
                "note": "No products found — check site manually",
            })

    return results


# -------------------------------------------------------
# Main runner
# -------------------------------------------------------
def run_all() -> Dict[str, List[Dict]]:
    """Run all component scrapers and return combined results."""
    session = requests.Session()
    session.headers.update(HEADERS)

    all_results = {
        "powders": [],
        "primers": [],
        "brass": [],
        "bullets": [],
    }

    logger.info("=== Starting component scraping ===")

    # Powder Valley — powders & primers
    logger.info("--- Powder Valley ---")
    pv_results = scrape_powder_valley(session, POWDERS[:6] + PRIMERS[:4])
    all_results["powders"].extend([r for r in pv_results if any(p.lower() in r["name"].lower() for p in POWDERS)] )
    all_results["primers"].extend([r for r in pv_results if any(p.lower() in r["name"].lower() for p in PRIMERS)])

    # Midsouth — powders, primers, brass
    logger.info("--- Midsouth Shooters Supply ---")
    ms_results = scrape_midsouth(session, POWDERS[:4] + PRIMERS[:3] + BRASS[:3])
    all_results["powders"].extend([r for r in ms_results if any(p.lower() in r["name"].lower() for p in POWDERS)])
    all_results["primers"].extend([r for r in ms_results if any(p.lower() in r["name"].lower() for p in PRIMERS)])
    all_results["brass"].extend([r for r in ms_results if any(b.lower() in r["name"].lower() for b in BRASS)])

    # Graf & Sons — powders, primers, brass
    logger.info("--- Graf & Sons ---")
    gr_results = scrape_grafs(session, POWDERS[:4] + PRIMERS[:3] + BRASS[:3])
    all_results["powders"].extend([r for r in gr_results if any(p.lower() in r["name"].lower() for p in POWDERS)])
    all_results["primers"].extend([r for r in gr_results if any(p.lower() in r["name"].lower() for p in PRIMERS)])
    all_results["brass"].extend([r for r in gr_results if any(b.lower() in r["name"].lower() for b in BRASS)])

    # Widener's — powders & primers
    logger.info("--- Widener's ---")
    wd_results = scrape_wideners(session, POWDERS[:4] + PRIMERS[:3])
    all_results["powders"].extend([r for r in wd_results if any(p.lower() in r["name"].lower() for p in POWDERS)])
    all_results["primers"].extend([r for r in wd_results if any(p.lower() in r["name"].lower() for p in PRIMERS)])

    # Lucky Gunner — brass & bullets
    logger.info("--- Lucky Gunner ---")
    lg_results = scrape_lucky_gunner(session, BRASS[:4] + BULLETS[:4])
    all_results["brass"].extend([r for r in lg_results if any(b.lower() in r["name"].lower() for b in BRASS)])
    all_results["bullets"].extend([r for r in lg_results if any(b.lower() in r["name"].lower() for b in BULLETS)])

    # Fallback: any unclassified results get appended appropriately
    for r in pv_results + ms_results + gr_results + wd_results + lg_results:
        if r not in all_results["powders"] + all_results["primers"] + all_results["brass"] + all_results["bullets"]:
            all_results["powders"].append(r)  # default bucket

    total = sum(len(v) for v in all_results.values())
    logger.info(f"=== Component scraping complete: {total} records ===")
    return all_results


if __name__ == "__main__":
    import json
    results = run_all()
    print(json.dumps(results, indent=2))
