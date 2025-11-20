"""
Configurazione centralizzata del bot Amazon Tracker & Affiliate Converter
"""
import os
from datetime import time
import pytz

# Bot Token (da variabile d'ambiente)
BOT_TOKEN = os.getenv('BOT_TOKEN', 'BotToken')

# Amazon Affiliate Configuration
AFFILIATE_TAG = "cringejon-21"

# Timezone per l'Italia
TIMEZONE = pytz.timezone('Europe/Rome')

# Orari reminder giornalieri (ore 11:00 e 16:00 Italia)
REMINDER_TIMES = [
    time(hour=11, minute=0, tzinfo=TIMEZONE),
    time(hour=16, minute=0, tzinfo=TIMEZONE)
]

# Messaggi del bot
MESSAGES = {
    'affiliate_link_response': "🔗 Ecco il tuo link affiliato:\n\n{link}\n\nUsa questo link per supportarmi! 🙏",
    'daily_reminder': "🛒 Buongiorno! Ricorda di usare i link convertiti per i tuoi acquisti Amazon oggi! Inviami qualsiasi link e lo convertirò per te. 😊",
    'convertlink_help': "ℹ️ Utilizzo: /convertlink <link Amazon>\n\nEsempio:\n/convertlink https://www.amazon.it/dp/B08N5WRWNW/",
    'invalid_link': "⚠️ Link Amazon non valido. Assicurati che sia un link amazon.it valido!",
    'no_asin_found': "❌ Non riesco a trovare il codice prodotto (ASIN) in questo link.",
    'stats_message': "📊 <b>Le tue statistiche</b>\n\n🔢 Link convertiti oggi: {today}\n📈 Totale link convertiti: {total}",
    'reminders_stopped': "✋ Reminder disattivati! Non riceverai più notifiche giornaliere.\n\nPer riattivarli usa /start",
    'reminders_reactivated': "✅ Benvenuto! I reminder giornalieri sono attivi.\n\nRiceverai promemoria alle 11:00 e alle 16:00 ogni giorno! 🔔",
    'already_subscribed': "Hello sir, Welcome to the Amazon Tracker Bot.\nPlease write /help to see the commands available.\n\n✅ Reminder già attivi!"
}

# File paths
DATA_DIR = 'data'
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
STATS_FILE = os.path.join(DATA_DIR, 'stats.json')

# Logging
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_LEVEL = 'INFO'
