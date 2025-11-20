"""
Handler per conversione link Amazon in link affiliati
"""
import re
import json
import logging
import os
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
import requests
import config
from utils import user_manager

logger = logging.getLogger(__name__)


def extract_asin(url):
    """
    Estrae l'ASIN da un URL Amazon

    Supporta formati:
    - https://www.amazon.it/dp/B08N5WRWNW/
    - https://www.amazon.it/product-name/dp/B08N5WRWNW/
    - https://amazon.it/gp/product/B08N5WRWNW
    - https://amzn.eu/d/XXXXX (short link)

    Args:
        url (str): URL Amazon

    Returns:
        str: ASIN o None se non trovato
    """
    # Pattern per ASIN standard (formato dp/ o gp/product/)
    patterns = [
        r'/dp/([A-Z0-9]{10})',
        r'/gp/product/([A-Z0-9]{10})',
        r'/product/([A-Z0-9]{10})',
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    # Gestione link short amzn.eu/d/
    if 'amzn.eu' in url or 'amzn.to' in url:
        try:
            # Segui il redirect per ottenere l'URL completo
            response = requests.get(url, allow_redirects=True, timeout=5)
            full_url = response.url
            logger.info(f"Short link {url} resolved to {full_url}")

            # Riprova con l'URL completo
            for pattern in patterns:
                match = re.search(pattern, full_url)
                if match:
                    return match.group(1)
        except Exception as e:
            logger.error(f"Errore nel risolvere short link {url}: {e}")

    return None


def is_amazon_link(text):
    """
    Verifica se il testo contiene un link Amazon.it

    Args:
        text (str): Testo da verificare

    Returns:
        bool: True se contiene link Amazon.it
    """
    amazon_patterns = [
        r'amazon\.it',
        r'amzn\.eu',
        r'amzn\.to'
    ]

    for pattern in amazon_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True

    return False


def extract_urls_from_text(text):
    """
    Estrae tutti gli URL da un testo

    Args:
        text (str): Testo contenente URL

    Returns:
        list: Lista di URL trovati
    """
    url_pattern = r'https?://[^\s]+'
    return re.findall(url_pattern, text)


def create_affiliate_link(asin):
    """
    Crea un link affiliato Amazon da un ASIN

    Args:
        asin (str): ASIN del prodotto

    Returns:
        str: Link affiliato
    """
    return f"https://www.amazon.it/dp/{asin}/?tag={config.AFFILIATE_TAG}"


def _load_stats():
    """Carica statistiche dal file JSON"""
    try:
        if os.path.exists(config.STATS_FILE):
            with open(config.STATS_FILE, 'r') as f:
                return json.load(f)
        else:
            return {
                "total_conversions": 0,
                "conversions_by_user": {},
                "daily_stats": {}
            }
    except Exception as e:
        logger.error(f"Errore caricamento stats.json: {e}")
        return {"total_conversions": 0, "conversions_by_user": {}, "daily_stats": {}}


def _save_stats(data):
    """Salva statistiche nel file JSON"""
    try:
        os.makedirs(config.DATA_DIR, exist_ok=True)
        with open(config.STATS_FILE, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logger.error(f"Errore salvataggio stats.json: {e}")


def increment_stats(user_id):
    """
    Incrementa le statistiche di conversione

    Args:
        user_id (int): ID utente Telegram
    """
    stats = _load_stats()
    user_id_str = str(user_id)
    today = datetime.now().strftime('%Y-%m-%d')

    # Incrementa totale
    stats['total_conversions'] = stats.get('total_conversions', 0) + 1

    # Incrementa per utente
    if user_id_str not in stats['conversions_by_user']:
        stats['conversions_by_user'][user_id_str] = 0
    stats['conversions_by_user'][user_id_str] += 1

    # Incrementa giornaliero
    if today not in stats['daily_stats']:
        stats['daily_stats'][today] = 0
    stats['daily_stats'][today] += 1

    _save_stats(stats)


def get_user_stats(user_id):
    """
    Ottieni statistiche per un utente

    Args:
        user_id (int): ID utente Telegram

    Returns:
        dict: {'today': int, 'total': int}
    """
    stats = _load_stats()
    user_id_str = str(user_id)
    today = datetime.now().strftime('%Y-%m-%d')

    total = stats.get('conversions_by_user', {}).get(user_id_str, 0)
    today_count = stats.get('daily_stats', {}).get(today, 0)

    return {'today': today_count, 'total': total}


async def handle_message_with_amazon_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler per messaggi contenenti link Amazon
    Converte automaticamente i link in link affiliati
    """
    text = update.message.text
    user_id = update.effective_user.id

    # Registra l'utente per i reminder (se nuovo)
    user_manager.save_user(user_id)

    # Verifica se contiene link Amazon
    if not is_amazon_link(text):
        return  # Ignora messaggi senza link Amazon

    # Estrai tutti gli URL dal messaggio
    urls = extract_urls_from_text(text)
    amazon_urls = [url for url in urls if is_amazon_link(url)]

    if not amazon_urls:
        return

    # Converti tutti i link Amazon trovati
    affiliate_links = []
    for url in amazon_urls:
        asin = extract_asin(url)
        if asin:
            affiliate_link = create_affiliate_link(asin)
            affiliate_links.append(affiliate_link)
            increment_stats(user_id)
            logger.info(f"Link convertito per user {user_id}: ASIN {asin}")
        else:
            logger.warning(f"ASIN non trovato in URL: {url}")

    # Invia risposta
    if affiliate_links:
        if len(affiliate_links) == 1:
            response = config.MESSAGES['affiliate_link_response'].format(link=affiliate_links[0])
        else:
            # Multiple link
            links_formatted = '\n\n'.join([f"{i+1}. {link}" for i, link in enumerate(affiliate_links)])
            response = f"🔗 Ecco i tuoi link affiliati:\n\n{links_formatted}\n\nUsa questi link per supportarmi! 🙏"

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=response
        )
    else:
        # Nessun ASIN trovato
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=config.MESSAGES['no_asin_found']
        )


async def convert_link_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler per comando /convertlink
    Permette conversione manuale di un link Amazon

    Utilizzo: /convertlink <URL Amazon>
    """
    user_id = update.effective_user.id

    # Registra utente
    user_manager.save_user(user_id)

    # Verifica se ci sono argomenti
    if not context.args:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=config.MESSAGES['convertlink_help']
        )
        return

    # Prendi il primo argomento come URL
    url = context.args[0]

    # Verifica se è un link Amazon
    if not is_amazon_link(url):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=config.MESSAGES['invalid_link']
        )
        return

    # Estrai ASIN
    asin = extract_asin(url)

    if not asin:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=config.MESSAGES['no_asin_found']
        )
        return

    # Crea link affiliato
    affiliate_link = create_affiliate_link(asin)
    increment_stats(user_id)

    # Invia risposta
    response = config.MESSAGES['affiliate_link_response'].format(link=affiliate_link)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=response
    )

    logger.info(f"Conversione manuale per user {user_id}: ASIN {asin}")


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler per comando /stats
    Mostra statistiche conversioni per l'utente
    """
    user_id = update.effective_user.id
    stats = get_user_stats(user_id)

    response = config.MESSAGES['stats_message'].format(
        today=stats['today'],
        total=stats['total']
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=response,
        parse_mode='HTML'
    )

    logger.info(f"Stats richieste da user {user_id}")
