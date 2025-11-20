#!/usr/bin/env python3
"""
Price Checker Script - Da eseguire con cron job

Controlla i prezzi di tutti i prodotti tracciati e invia notifiche:
- Quando il prezzo cambia
- Quando un alert viene triggered

Setup cron (esempio - ogni 6 ore):
0 */6 * * * cd /path/to/bot && python scripts/check_prices.py >> logs/price_check.log 2>&1

Oppure con systemd timer (vedi docs/SETUP_SUPABASE.md)
"""
import sys
import os
import logging
from datetime import datetime
import asyncio

# Aggiungi parent directory al path per import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import config
from utils import supabase_manager
import scraper
from telegram import Bot

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def check_all_prices():
    """
    Controlla i prezzi di tutti i prodotti tracciati
    """
    logger.info("=== INIZIO CHECK PREZZI ===")

    # Verifica Supabase configurato
    if not config.SUPABASE_ENABLED:
        logger.error("Supabase non configurato! Controlla SUPABASE_URL e SUPABASE_KEY")
        return

    # Ottieni tutti i prodotti tracciati
    products = supabase_manager.get_all_tracked_products()

    if not products:
        logger.info("Nessun prodotto da trackare")
        return

    logger.info(f"Trovati {len(products)} prodotti da controllare")

    bot = Bot(token=config.BOT_TOKEN)

    checked_count = 0
    updated_count = 0
    error_count = 0

    for product in products:
        asin = product.get('asin')
        url = product.get('url')
        old_price = float(product.get('last_price', 0))
        product_name = product.get('product_name', 'Prodotto')

        logger.info(f"Controllo prodotto {asin} - {product_name[:30]}...")

        try:
            # Scrapa prezzo attuale da Amazon
            price_str = scraper.findPrice(url)

            if not price_str:
                logger.warning(f"Impossibile recuperare prezzo per {asin}")
                error_count += 1
                continue

            # Parse prezzo
            new_price = parse_price(price_str)

            if new_price is None:
                logger.warning(f"Errore parsing prezzo '{price_str}' per {asin}")
                error_count += 1
                continue

            checked_count += 1

            # Confronta con prezzo precedente
            price_diff = old_price - new_price

            if abs(price_diff) > 0.01:  # Cambiamento significativo
                # Aggiorna prezzo in database
                supabase_manager.update_product_price(asin, new_price)
                updated_count += 1

                logger.info(f"Prezzo cambiato per {asin}: {old_price}€ → {new_price}€ ({price_diff:+.2f}€)")

                # Invia notifica cambio prezzo a utente
                user_id = product.get('user_id')
                await send_price_change_notification(
                    bot, user_id, product_name, asin, old_price, new_price, url
                )

            else:
                # Prezzo invariato - aggiorna solo timestamp
                supabase_manager.update_product_price(asin, new_price)
                logger.debug(f"Prezzo invariato per {asin}: {new_price}€")

            # Rate limiting per evitare ban Amazon
            await asyncio.sleep(2)

        except Exception as e:
            logger.error(f"Errore controllo {asin}: {e}")
            error_count += 1
            continue

    # Check alert triggered
    triggered_alerts = supabase_manager.get_triggered_alerts()

    if triggered_alerts:
        logger.info(f"Trovati {len(triggered_alerts)} alert triggered")

        for alert in triggered_alerts:
            user_id = alert['user_id']
            asin = alert['asin']
            target_price = alert['target_price']
            current_price = alert['current_price']
            product_name = alert['product_name']
            url = alert.get('url', '')

            await send_alert_notification(
                bot, user_id, product_name, asin, target_price, current_price, url
            )

            # Disattiva alert (inviato una volta sola)
            supabase_manager.deactivate_alert(user_id, asin)

            logger.info(f"Alert inviato a user {user_id} per {asin}")

            await asyncio.sleep(1)

    logger.info(f"=== CHECK COMPLETATO ===")
    logger.info(f"Prodotti controllati: {checked_count}/{len(products)}")
    logger.info(f"Prezzi aggiornati: {updated_count}")
    logger.info(f"Errori: {error_count}")
    logger.info(f"Alert triggered: {len(triggered_alerts)}")


async def send_price_change_notification(bot, user_id, product_name, asin, old_price, new_price, url):
    """
    Invia notifica cambio prezzo all'utente

    Args:
        bot: Bot instance
        user_id (int): ID utente Telegram
        product_name (str): Nome prodotto
        asin (str): ASIN prodotto
        old_price (float): Vecchio prezzo
        new_price (float): Nuovo prezzo
        url (str): URL prodotto
    """
    price_diff = old_price - new_price

    if price_diff > 0:
        emoji = "📉"
        change_text = f"<b>SCESO</b> di {price_diff:.2f}€!"
    else:
        emoji = "📈"
        change_text = f"<b>SALITO</b> di {abs(price_diff):.2f}€"

    # Genera link affiliato
    from handlers import amazon_affiliate
    affiliate_link = amazon_affiliate.create_affiliate_link(asin)

    message = f"{emoji} <b>Cambio Prezzo!</b>\n\n" \
              f"📦 {product_name}\n\n" \
              f"💰 Prezzo {change_text}\n" \
              f"   Prima: {old_price:.2f}€\n" \
              f"   Ora: {new_price:.2f}€\n\n" \
              f"🔗 <a href='{affiliate_link}'>Vedi su Amazon</a>\n\n" \
              f"🔕 /untrack {asin} per smettere di trackare"

    try:
        await bot.send_message(
            chat_id=user_id,
            text=message,
            parse_mode='HTML',
            disable_web_page_preview=False
        )
        logger.info(f"Notifica inviata a user {user_id} per {asin}")
    except Exception as e:
        logger.error(f"Errore invio notifica a user {user_id}: {e}")


async def send_alert_notification(bot, user_id, product_name, asin, target_price, current_price, url):
    """
    Invia notifica alert prezzo raggiunto

    Args:
        bot: Bot instance
        user_id (int): ID utente
        product_name (str): Nome prodotto
        asin (str): ASIN
        target_price (float): Prezzo target
        current_price (float): Prezzo attuale
        url (str): URL prodotto
    """
    # Genera link affiliato
    from handlers import amazon_affiliate
    affiliate_link = amazon_affiliate.create_affiliate_link(asin)

    message = f"🎯 <b>ALERT PREZZO RAGGIUNTO!</b>\n\n" \
              f"📦 {product_name}\n\n" \
              f"✅ Il prodotto è sceso sotto il tuo target!\n" \
              f"   Target: {target_price:.2f}€\n" \
              f"   Attuale: <b>{current_price:.2f}€</b>\n\n" \
              f"🔗 <a href='{affiliate_link}'>Acquista su Amazon</a>\n\n" \
              f"💡 L'alert è stato disattivato. Usa /setalert per impostarne uno nuovo."

    try:
        await bot.send_message(
            chat_id=user_id,
            text=message,
            parse_mode='HTML',
            disable_web_page_preview=False
        )
        logger.info(f"Alert inviato a user {user_id} per {asin}")
    except Exception as e:
        logger.error(f"Errore invio alert a user {user_id}: {e}")


def parse_price(price_str):
    """
    Estrae prezzo numerico da stringa

    Args:
        price_str (str): Stringa prezzo

    Returns:
        float: Prezzo numerico o None
    """
    try:
        import re
        price_clean = re.sub(r'[^\d,.]', '', price_str)
        price_clean = price_clean.replace(',', '.')
        return float(price_clean)
    except Exception as e:
        logger.error(f"Errore parsing prezzo '{price_str}': {e}")
        return None


if __name__ == "__main__":
    print(f"=== Amazon Price Checker - {datetime.now().isoformat()} ===\n")

    # Verifica configurazione
    if not config.SUPABASE_ENABLED:
        print("ERROR: Supabase non configurato!")
        print("Configura SUPABASE_URL e SUPABASE_KEY nel file .env")
        sys.exit(1)

    if config.BOT_TOKEN == 'BotToken':
        print("ERROR: BOT_TOKEN non configurato!")
        print("Configura BOT_TOKEN nel file .env")
        sys.exit(1)

    # Esegui check
    try:
        asyncio.run(check_all_prices())
        print("\n✅ Check completato con successo!")
    except KeyboardInterrupt:
        print("\n⚠️ Check interrotto dall'utente")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Errore durante check: {e}")
        logger.exception("Errore fatale")
        sys.exit(1)
