import logging
import re

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept-Language': 'it-IT,it;q=0.9',
}
REQUEST_TIMEOUT = 10


def saveInFile(link):
    if link == "":
        return "Link Empty!"
    with open('file.csv', 'a') as localFile:
        localFile.write(link + '\n')
    return 'Link Saved in a CSV File!'


def _fetch(link):
    """
    Scarica la pagina SOLO se il link è un URL Amazon (anti-SSRF).
    Gli short link vengono risolti verificando ogni redirect.

    Returns:
        BeautifulSoup o None
    """
    # Import locale per evitare import circolari
    from handlers import amazon_affiliate

    if not link or not amazon_affiliate.is_amazon_url(link):
        logger.warning(f"URL non Amazon rifiutato dallo scraper: {link!r}")
        return None

    current = link
    try:
        for _ in range(5):
            if not amazon_affiliate.is_amazon_url(current):
                logger.warning(f"Redirect verso host non Amazon bloccato: {current!r}")
                return None
            page = requests.get(current, headers=HEADERS, timeout=REQUEST_TIMEOUT, allow_redirects=False)
            if page.is_redirect and page.headers.get('Location'):
                current = requests.compat.urljoin(current, page.headers['Location'])
                continue
            page.raise_for_status()
            return BeautifulSoup(page.content, "lxml")
    except requests.RequestException as e:
        logger.error(f"Errore nella richiesta: {e}")
        return None

    logger.warning(f"Troppi redirect per {link!r}")
    return None


def findProdTitle(link):
    soup = _fetch(link)
    if soup is None:
        return None

    product_title_element = soup.find(id='productTitle')
    if product_title_element is None:
        logger.warning("Elemento con ID 'productTitle' non trovato")
        return None
    return product_title_element.get_text().strip()


def findPrice(link):
    soup = _fetch(link)
    if soup is None:
        return None

    price_element = soup.find('span', class_='a-offscreen')
    if price_element is None:
        logger.warning("Prezzo non trovato nella pagina")
        return None
    return 'Prezzo --> ' + price_element.get_text().strip() + '\n'


def parse_price(price_str):
    """
    Converte una stringa prezzo in float.

    Gestisce formato italiano ("1.299,99 €"), formato con solo virgola
    ("99,99 €") e formato inglese ("1,299.99").

    Returns:
        float o None
    """
    if not price_str:
        return None

    match = re.search(r'\d[\d.,]*', price_str)
    if not match:
        return None
    num = match.group(0).rstrip('.,')

    if ',' in num and '.' in num:
        if num.rfind(',') > num.rfind('.'):
            # 1.299,99 -> 1299.99
            num = num.replace('.', '').replace(',', '.')
        else:
            # 1,299.99 -> 1299.99
            num = num.replace(',', '')
    elif ',' in num:
        num = num.replace(',', '.')
    elif num.count('.') == 1 and len(num.split('.')[1]) == 3:
        # 1.299 -> migliaia senza decimali
        num = num.replace('.', '')

    try:
        return float(num)
    except ValueError:
        logger.error(f"Errore parsing prezzo '{price_str}'")
        return None
