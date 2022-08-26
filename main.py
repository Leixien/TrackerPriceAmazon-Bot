import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, Updater, InlineQueryHandler, CallbackContext
import myFunctions as mf
import scraper

logging.basicConfig(
    
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

token = 'BotToken'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hello sir, Welcome to the Amazon Tracker Bot.\nPlease write /help to see the commands available.")
    
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
    output = output + '\t/prodotti - Visualizza tutti i prodotti tracciati'
    await context.bot.send_message(chat_id = update.effective_chat.id, text = output)

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
    
if __name__ == '__main__':
    application = ApplicationBuilder().token(token).build()
    
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
    
    application.run_polling()
    application.idle() 
