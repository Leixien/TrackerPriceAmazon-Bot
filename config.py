"""
Configurazione centralizzata del bot Amazon Tracker & Affiliate Converter
"""
import os
from datetime import time
from pathlib import Path
import pytz
from dotenv import load_dotenv

# Carica variabili da .env (percorso relativo alla cartella del progetto)
ENV_PATH = Path(__file__).parent / '.env'
load_dotenv(ENV_PATH)

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

# ========================================
# AI CONFIGURATION (Ollama)
# ========================================

# URL Ollama API (localhost se su stesso Raspberry, altrimenti IP Raspberry)
OLLAMA_API_URL = os.getenv('OLLAMA_API_URL', 'http://localhost:11434/api/generate')

# Modello da usare (consigliati per Raspberry Pi 4/5):
# - "mistral:7b" - Veloce, buona qualità (4GB RAM)
# - "llama3.2:3b" - Più veloce, meno RAM (2GB)
# - "llama3.2:1b" - Ultra-leggero per Raspberry Pi 3/Zero (1GB)
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'mistral:7b')

# Abilita/disabilita AI (utile per testing senza AI)
AI_ENABLED = os.getenv('AI_ENABLED', 'true').lower() == 'true'

# ========================================
# SUPABASE CONFIGURATION (Opzionale)
# ========================================

# Supabase Project URL e API Key (da dashboard Supabase)
SUPABASE_URL = os.getenv('SUPABASE_URL', '')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', '')

# Abilita/disabilita Supabase
SUPABASE_ENABLED = bool(SUPABASE_URL and SUPABASE_KEY)

# ========================================
# MESSAGGI DEL BOT
# ========================================

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
    'already_subscribed': "Hello sir, Welcome to the Amazon Tracker Bot.\nPlease write /help to see the commands available.\n\n✅ Reminder già attivi!",

    # Nuovi messaggi AI
    'ai_not_product_request': "🤖 Ciao! Sono un assistente specializzato in <b>consigli prodotti Amazon</b>.\n\n"
                              "❓ <b>Come posso aiutarti:</b>\n"
                              "• Consigli su prodotti specifici\n"
                              "• Confronti tra prodotti\n"
                              "• Suggerimenti basati sul budget\n\n"
                              "💡 <b>Esempi:</b>\n"
                              "\"Mi consigli un laptop per gaming sotto 1000€?\"\n"
                              "\"Quale è il miglior smartphone con fotocamera?\"\n\n"
                              "Usa /aihelp per maggiori info! 🚀",

    'ai_error': "⚠️ Ops! Si è verificato un errore con l'assistente AI.\n\n"
                "Riprova tra poco o usa i comandi manuali:\n"
                "/convertlink - Converti link Amazon\n"
                "/help - Vedi tutti i comandi"
}

# File paths
DATA_DIR = 'data'
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
STATS_FILE = os.path.join(DATA_DIR, 'stats.json')

# Logging
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_LEVEL = 'INFO'
