"""
Handler per Price Tracking con Supabase
Comandi per tracciare prezzi prodotti Amazon
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes
import config
from utils import supabase_manager
from handlers import amazon_affiliate
import scraper

logger = logging.getLogger(__name__)


async def track_product_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Comando /track <link Amazon>
    Aggiungi prodotto al tracking prezzi

    Esempio: /track https://www.amazon.it/dp/B08N5WRWNW/
    """
    user_id = update.effective_user.id

    # Verifica Supabase configurato
    if not config.SUPABASE_ENABLED:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⚠️ <b>Price Tracking non configurato</b>\n\n"
                 "Per usare questa funzione devi configurare Supabase.\n"
                 "Vedi: docs/SETUP_SUPABASE.md",
            parse_mode='HTML'
        )
        return

    # Verifica argomenti
    if not context.args:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="ℹ️ <b>Utilizzo</b>: /track <link Amazon>\n\n"
                 "<b>Esempio:</b>\n"
                 "/track https://www.amazon.it/dp/B08N5WRWNW/\n\n"
                 "Aggiungo il prodotto al tracking e ti avviso quando il prezzo scende! 📉",
            parse_mode='HTML'
        )
        return

    url = context.args[0]

    # Verifica link Amazon
    if not amazon_affiliate.is_amazon_link(url):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⚠️ Link Amazon non valido. Assicurati che sia un link amazon.it!"
        )
        return

    # Mostra "typing..."
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )

    # Estrai ASIN
    asin = amazon_affiliate.extract_asin(url)
    if not asin:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Non riesco a trovare il codice prodotto (ASIN) in questo link."
        )
        return

    # Scrapa prodotto da Amazon
    try:
        product_name = scraper.findProdTitle(url)
        price_str = scraper.findPrice(url)

        if not product_name or not price_str:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="⚠️ Errore nel recuperare info prodotto da Amazon. Riprova!"
            )
            return

        # Estrai prezzo numerico da stringa "Prezzo --> 99,99 €"
        price = parse_price(price_str)

        if price is None:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="⚠️ Errore nel leggere il prezzo. Riprova!"
            )
            return

    except Exception as e:
        logger.error(f"Errore scraping prodotto: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⚠️ Errore nel recuperare info prodotto. Riprova più tardi!"
        )
        return

    # Aggiungi a Supabase
    success = supabase_manager.add_tracked_product(
        user_id=user_id,
        asin=asin,
        product_name=product_name,
        current_price=price,
        url=url
    )

    if success:
        response = f"✅ <b>Prodotto aggiunto al tracking!</b>\n\n" \
                   f"📦 {product_name}\n" \
                   f"💰 Prezzo attuale: {price}€\n" \
                   f"🔗 ASIN: {asin}\n\n" \
                   f"Ti avviserò quando il prezzo cambia! 🔔\n\n" \
                   f"💡 <b>Tip</b>: Usa /setalert {asin} <prezzo> per ricevere notifica quando scende sotto un prezzo specifico"

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=response,
            parse_mode='HTML'
        )

        logger.info(f"Prodotto {asin} aggiunto al tracking per user {user_id}")
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Errore nell'aggiungere il prodotto. Riprova più tardi!"
        )


async def untrack_product_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Comando /untrack <ASIN>
    Rimuovi prodotto dal tracking

    Esempio: /untrack B08N5WRWNW
    """
    user_id = update.effective_user.id

    # Verifica Supabase configurato
    if not config.SUPABASE_ENABLED:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⚠️ Price Tracking non configurato. Vedi: docs/SETUP_SUPABASE.md",
            parse_mode='HTML'
        )
        return

    # Verifica argomenti
    if not context.args:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="ℹ️ <b>Utilizzo</b>: /untrack <ASIN>\n\n"
                 "<b>Esempio:</b>\n"
                 "/untrack B08N5WRWNW\n\n"
                 "Usa /myproducts per vedere i tuoi prodotti tracciati",
            parse_mode='HTML'
        )
        return

    asin = context.args[0].strip()

    # Rimuovi da Supabase
    success = supabase_manager.remove_tracked_product(user_id, asin)

    if success:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"✅ Prodotto {asin} rimosso dal tracking!\n\n"
                 f"Non riceverai più aggiornamenti su questo prodotto."
        )
        logger.info(f"Prodotto {asin} rimosso dal tracking per user {user_id}")
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"⚠️ Prodotto {asin} non trovato o errore nella rimozione."
        )


async def my_products_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Comando /myproducts
    Mostra lista prodotti tracciati dall'utente
    """
    user_id = update.effective_user.id

    # Verifica Supabase configurato
    if not config.SUPABASE_ENABLED:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⚠️ Price Tracking non configurato. Vedi: docs/SETUP_SUPABASE.md",
            parse_mode='HTML'
        )
        return

    # Recupera prodotti
    products = supabase_manager.get_user_tracked_products(user_id)

    if not products:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="📦 <b>Nessun prodotto tracciato</b>\n\n"
                 "Usa /track <link> per aggiungere prodotti da tracciare!",
            parse_mode='HTML'
        )
        return

    # Costruisci messaggio
    response = f"📊 <b>I tuoi prodotti tracciati</b> ({len(products)})\n\n"

    for i, product in enumerate(products[:10], 1):  # Max 10 prodotti per messaggio
        name = product.get('product_name', 'N/A')[:50]  # Tronca nome lungo
        asin = product.get('asin', 'N/A')
        initial_price = product.get('initial_price', 0)
        last_price = product.get('last_price', 0)

        # Calcola variazione prezzo
        if initial_price and last_price:
            diff = initial_price - last_price
            if diff > 0:
                price_emoji = "📉"
                price_text = f"-{diff:.2f}€"
            elif diff < 0:
                price_emoji = "📈"
                price_text = f"+{abs(diff):.2f}€"
            else:
                price_emoji = "➡️"
                price_text = "invariato"
        else:
            price_emoji = "💰"
            price_text = f"{last_price}€"

        response += f"{i}. <b>{name}</b>\n" \
                    f"   {price_emoji} {last_price}€ ({price_text})\n" \
                    f"   🔗 ASIN: <code>{asin}</code>\n\n"

    response += "\n💡 <b>Comandi utili:</b>\n" \
                "• /untrack <ASIN> - Rimuovi dal tracking\n" \
                "• /setalert <ASIN> <prezzo> - Imposta alert\n" \
                "• /history <ASIN> - Vedi storico prezzi"

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=response,
        parse_mode='HTML'
    )

    logger.info(f"Lista prodotti mostrata a user {user_id}")


async def set_alert_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Comando /setalert <ASIN> <prezzo>
    Imposta alert prezzo per un prodotto

    Esempio: /setalert B08N5WRWNW 50
    """
    user_id = update.effective_user.id

    # Verifica Supabase configurato
    if not config.SUPABASE_ENABLED:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⚠️ Price Tracking non configurato. Vedi: docs/SETUP_SUPABASE.md",
            parse_mode='HTML'
        )
        return

    # Verifica argomenti
    if len(context.args) < 2:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="ℹ️ <b>Utilizzo</b>: /setalert <ASIN> <prezzo>\n\n"
                 "<b>Esempio:</b>\n"
                 "/setalert B08N5WRWNW 50\n\n"
                 "Ti avviserò quando il prodotto scenderà sotto 50€!",
            parse_mode='HTML'
        )
        return

    asin = context.args[0].strip()

    try:
        target_price = float(context.args[1].replace(',', '.'))
    except ValueError:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⚠️ Prezzo non valido. Usa formato: 50 o 50.99"
        )
        return

    # Imposta alert in Supabase
    success = supabase_manager.set_price_alert(user_id, asin, target_price)

    if success:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"🔔 <b>Alert impostato!</b>\n\n"
                 f"Ti avviserò quando il prodotto {asin} scenderà sotto {target_price}€\n\n"
                 f"Puoi modificare l'alert in qualsiasi momento con /setalert",
            parse_mode='HTML'
        )
        logger.info(f"Alert impostato per user {user_id} ASIN {asin} a {target_price}€")
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Errore nell'impostare l'alert. Assicurati che il prodotto sia tracciato!"
        )


async def price_history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Comando /history <ASIN>
    Mostra storico prezzi prodotto (ultimi 30 giorni)

    Esempio: /history B08N5WRWNW
    """
    user_id = update.effective_user.id

    # Verifica Supabase configurato
    if not config.SUPABASE_ENABLED:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⚠️ Price Tracking non configurato. Vedi: docs/SETUP_SUPABASE.md",
            parse_mode='HTML'
        )
        return

    # Verifica argomenti
    if not context.args:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="ℹ️ <b>Utilizzo</b>: /history <ASIN>\n\n"
                 "<b>Esempio:</b>\n"
                 "/history B08N5WRWNW",
            parse_mode='HTML'
        )
        return

    asin = context.args[0].strip()

    # Recupera storico
    history = supabase_manager.get_price_history(asin, days=30)

    if not history:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"📊 Nessuno storico trovato per {asin}\n\n"
                 f"Il prodotto potrebbe essere stato aggiunto di recente."
        )
        return

    # Calcola statistiche
    prices = [float(h['price']) for h in history]
    min_price = min(prices)
    max_price = max(prices)
    avg_price = sum(prices) / len(prices)
    current_price = prices[-1]

    # Costruisci messaggio
    response = f"📊 <b>Storico Prezzi - {asin}</b>\n\n" \
               f"💰 Prezzo attuale: {current_price}€\n" \
               f"📉 Minimo: {min_price}€\n" \
               f"📈 Massimo: {max_price}€\n" \
               f"📊 Media: {avg_price:.2f}€\n\n" \
               f"📅 Ultimi {len(history)} rilevamenti (30 giorni)\n\n"

    # Aggiungi ultimi 5 rilevamenti
    response += "<b>Ultime variazioni:</b>\n"
    for h in reversed(history[-5:]):
        timestamp = h['timestamp'][:10]  # YYYY-MM-DD
        price = h['price']
        response += f"• {timestamp}: {price}€\n"

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=response,
        parse_mode='HTML'
    )

    logger.info(f"Storico prezzi mostrato a user {user_id} per ASIN {asin}")


def parse_price(price_str):
    """
    Estrae prezzo numerico da stringa

    Args:
        price_str (str): Stringa prezzo (es: "Prezzo --> 99,99 €")

    Returns:
        float: Prezzo numerico o None se errore
    """
    try:
        # Rimuovi tutto tranne numeri, virgola e punto
        import re
        price_clean = re.sub(r'[^\d,.]', '', price_str)

        # Sostituisci virgola con punto
        price_clean = price_clean.replace(',', '.')

        return float(price_clean)

    except Exception as e:
        logger.error(f"Errore parsing prezzo '{price_str}': {e}")
        return None
