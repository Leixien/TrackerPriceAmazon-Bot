import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, Updater, InlineQueryHandler, CallbackContext
import myFunctions as mf
import scraper
import config
from handlers import amazon_affiliate, ai_assistant, price_tracker
from utils import user_manager, scheduler, ollama_client

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

token = config.BOT_TOKEN

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Registra utente per reminder giornalieri
    user_id = update.effective_user.id
    was_new = user_manager.save_user(user_id)

    if was_new:
        message = "Hello sir, Welcome to the Amazon Tracker Bot.\nPlease write /help to see the commands available.\n\n✅ Reminder giornalieri attivi alle 11:00 e 16:00! 🔔"
    else:
        message = "Hello sir, Welcome to the Amazon Tracker Bot.\nPlease write /help to see the commands available."

    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    
async def dev(update: Update, context: ContextTypes.DEFAULT_TYPE):
    output = "🇮🇹 Bot per il tracciamento dei prezzi dei prodotti su Amazon\n🇬🇧 Price Tracker Bot for Amazon Product!\nDev: <a href='https://t.me/cringejon'>Giuseppe Scappaticci</a>"
    await context.bot.send_message(chat_id = update.effective_chat.id, text = output, parse_mode = 'HTML')

async def sendProd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    productTitle = scraper.productTitle
    prezzo = scraper.prezzo
    url = scraper.url
    await context.bot.send_message(chat_id=update.effective_chat.id, text = productTitle + "\n\n🇮🇹 " + prezzo + '\n\n' + url)
    
async def discordInviteCommand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    output = "🇮🇹 Entra a far parte della nostra community! \n🇬🇧 Join in the our <b>community!</b> \n\n(https://discord.gg/kTg5fhVERQv)"
    await context.bot.send_message(chat_id = update.effective_chat.id, text = output, parse_mode = 'HTML')
    
async def randomSong(update : Update, context : ContextTypes.DEFAULT_TYPE):
    output = "🎶 Scopri una canzone random! \n🇬🇧 Find a random song! \n(https://www.youtube.com/watch?v=dQw4w9WgXcQ)"
    await context.bot.send_message(chat_id = update.effective_chat.id, text = output)
    
async def help(update : Update, context : ContextTypes.DEFAULT_TYPE):
    output = 'Comandi:\n' + '\t/start - Inizia a usare il bot\n' + '\t/help - Visualizza questo messaggio\n' + '\t/discord - Entra nel server discord \n' + '\t/song - Scopri una canzone random\n'
    output = output + '\t/url {url prodotto amazon} - Salva prodotto da tracciare\n' + '\t/uri {link prodotto amazon} - Invia prezzo attuale del prodotto\n'
    output = output + '\t/prodotti - Visualizza tutti i prodotti tracciati\n\n'
    output = output + '🔗 <b>Link Affiliati:</b>\n' + '\t/convertlink {link} - Converti link Amazon in affiliato\n' + '\t/stats - Visualizza le tue statistiche\n' + '\t/stop - Disattiva reminder giornalieri\n\n'

    if config.AI_ENABLED:
        output = output + '🤖 <b>AI Assistant:</b>\n' + '\t/aihelp - Come usare l\'assistente AI\n' + '\tInvia una richiesta prodotto per consigli intelligenti!'

    await context.bot.send_message(chat_id = update.effective_chat.id, text = output, parse_mode='HTML')

async def sendProduct(update: Update, context: ContextTypes.DEFAULT_TYPE):
    userinput = update.message.text
    productTitle = scraper.findProdTitle(mf.modLink(userinput))
    prezzo = scraper.findPrice(mf.modLink(userinput))
    await context.bot.send_message(chat_id=update.effective_chat.id, text = productTitle + "\n\n" + '🇮🇹' + prezzo + '\n' + mf.modLink(userinput))

async def takeLink(update: Update, context: ContextTypes.DEFAULT_TYPE):
    output = mf.duplicateProd(mf.modLink(update.message.text))
    await context.bot.send_message(chat_id=update.effective_chat.id, text = output)

async def products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    prod = mf.leggiFileCSV()
    
    keyboard = [
        [
            InlineKeyboardButton(text = 'Seleziona un prodotto ', callback_data = 'Nessun prodotto selezioanto!'),
        ],
    ]
    
    for key, value in prod.items():
        link = mf.trovaLink(value)
        productTitle = scraper.findProdTitle(link)
        keyboard = keyboard + [[InlineKeyboardButton(text = productTitle, url = link)],]
        
    markup = InlineKeyboardMarkup(keyboard)
    
    output = 'Qui trovi tutti i prodotti che stai tracciando!\n'
    
    output = output + 'Clicca sui bottoni per essere reindirizzato alla pagina di Amazon'
    
    await context.bot.send_message(chat_id = update.effective_chat.id, text = output, reply_markup = markup)
    
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    #await query.answer()

    if query.data == 'Nessun prodotto selezioanto!':
        await context.bot.answer_callback_query(callback_query_id=query.id, text="Nessun prodotto selezionato", show_alert=True)


async def unified_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler unificato per messaggi non-comando

    Priorità:
    1. Se contiene link Amazon → conversione affiliati
    2. Altrimenti, se AI abilitata → richiesta AI per consigli prodotti
    3. Altrimenti → ignora
    """
    text = update.message.text

    # 1. Controlla se contiene link Amazon
    if amazon_affiliate.is_amazon_link(text):
        await amazon_affiliate.handle_message_with_amazon_link(update, context)
        return

    # 2. Se AI abilitata, gestisci come richiesta AI
    if config.AI_ENABLED:
        await ai_assistant.handle_ai_request(update, context)
        return

    # 3. Altrimenti ignora (comportamento originale)
    # Nessuna risposta per messaggi generici senza AI
    
if __name__ == '__main__':
    application = ApplicationBuilder().token(token).build()

    # === Handler Comandi Esistenti ===
    keyHandlerCommand = CommandHandler("prodotti", products)
    application.add_handler(keyHandlerCommand)

    application.add_handler(CallbackQueryHandler(button))

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    devCommandHandler = CommandHandler('dev', dev)
    application.add_handler(devCommandHandler)

    helpHandler = CommandHandler('help', help)
    application.add_handler(helpHandler)

    prodHandlerCommand = CommandHandler('sendProduct', sendProd)
    application.add_handler(prodHandlerCommand)

    discordHandlerCommand = CommandHandler('discord', discordInviteCommand)
    application.add_handler(discordHandlerCommand)

    songHandlerCommand = CommandHandler('song', randomSong)
    application.add_handler(songHandlerCommand)

    urlSavedCommand = CommandHandler('url', takeLink)
    application.add_handler(urlSavedCommand)

    trackItemCommand = CommandHandler('uri', sendProduct)
    application.add_handler(trackItemCommand)

    # === Handler Link Affiliati (NUOVI) ===
    # Comando conversione manuale
    convertlink_handler = CommandHandler('convertlink', amazon_affiliate.convert_link_command)
    application.add_handler(convertlink_handler)

    # Comando statistiche
    stats_handler = CommandHandler('stats', amazon_affiliate.stats_command)
    application.add_handler(stats_handler)

    # Comando stop reminder
    stop_handler = CommandHandler('stop', user_manager.stop_reminders)
    application.add_handler(stop_handler)

    # === Handler AI Assistant (NUOVI) ===
    if config.AI_ENABLED:
        # Comando aihelp
        aihelp_handler = CommandHandler('aihelp', ai_assistant.ai_help_command)
        application.add_handler(aihelp_handler)
        logging.info("🤖 AI Assistant abilitata")

    # === Handler Price Tracking (NUOVI - Supabase) ===
    if config.SUPABASE_ENABLED:
        # Comando tracking prodotti
        track_handler = CommandHandler('track', price_tracker.track_product_command)
        application.add_handler(track_handler)

        untrack_handler = CommandHandler('untrack', price_tracker.untrack_product_command)
        application.add_handler(untrack_handler)

        myproducts_handler = CommandHandler('myproducts', price_tracker.my_products_command)
        application.add_handler(myproducts_handler)

        setalert_handler = CommandHandler('setalert', price_tracker.set_alert_command)
        application.add_handler(setalert_handler)

        history_handler = CommandHandler('history', price_tracker.price_history_command)
        application.add_handler(history_handler)

        logging.info("📊 Price Tracking abilitato")

    # === Handler Messaggi Unificato ===
    # Gestisce sia link Amazon che richieste AI
    # IMPORTANTE: deve essere aggiunto PER ULTIMO per non interferire con altri handler
    message_handler = MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        unified_message_handler
    )
    application.add_handler(message_handler)

    # === Setup Reminder Giornalieri ===
    scheduler.setup_daily_reminders(application)

    # === Health Checks ===
    if config.AI_ENABLED:
        logging.info("🔍 Verifico connessione Ollama...")
        # Health check sincrono all'avvio
        ollama_available = ollama_client.test_ollama_sync()
        if ollama_available:
            logging.info(f"✅ Ollama disponibile - Modello: {config.OLLAMA_MODEL}")
        else:
            logging.warning(f"⚠️ Ollama NON disponibile su {config.OLLAMA_API_URL}")
            logging.warning("   AI Assistant non funzionerà. Vedi docs/SETUP_AI.md per installazione")

    if config.SUPABASE_ENABLED:
        from utils import supabase_manager
        logging.info("🔍 Verifico connessione Supabase...")
        supabase_ok = supabase_manager.check_supabase_health()
        if supabase_ok:
            logging.info("✅ Supabase disponibile - Price Tracking attivo")
        else:
            logging.warning("⚠️ Supabase NON disponibile")
            logging.warning("   Price Tracking non funzionerà. Vedi docs/SETUP_SUPABASE.md per configurazione")

    logging.info("🚀 Bot avviato con successo! Reminder configurati per le 11:00 e 16:00")

    application.run_polling()
    application.idle() 
