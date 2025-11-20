"""
Gestione utenti per tracking e broadcast reminder
"""
import json
import logging
import os
from telegram import Update
from telegram.ext import ContextTypes
import config

logger = logging.getLogger(__name__)


def _load_users():
    """Carica il file users.json"""
    try:
        if os.path.exists(config.USERS_FILE):
            with open(config.USERS_FILE, 'r') as f:
                return json.load(f)
        else:
            return {"users": [], "unsubscribed": []}
    except Exception as e:
        logger.error(f"Errore caricamento users.json: {e}")
        return {"users": [], "unsubscribed": []}


def _save_users(data):
    """Salva il file users.json"""
    try:
        os.makedirs(config.DATA_DIR, exist_ok=True)
        with open(config.USERS_FILE, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logger.error(f"Errore salvataggio users.json: {e}")


def save_user(user_id):
    """
    Salva un utente per i reminder giornalieri

    Args:
        user_id (int): ID Telegram dell'utente
    """
    data = _load_users()

    # Converti a int per consistenza
    user_id = int(user_id)

    # Se era in unsubscribed, rimuovilo da lì
    if user_id in data.get('unsubscribed', []):
        data['unsubscribed'].remove(user_id)
        logger.info(f"Utente {user_id} ri-iscritto ai reminder")

    # Aggiungi a users se non già presente
    if user_id not in data.get('users', []):
        data['users'].append(user_id)
        _save_users(data)
        logger.info(f"Nuovo utente salvato: {user_id}")
        return True

    return False


def remove_user(user_id):
    """
    Rimuove un utente dai reminder (lo aggiunge a unsubscribed)

    Args:
        user_id (int): ID Telegram dell'utente
    """
    data = _load_users()
    user_id = int(user_id)

    # Rimuovi da users
    if user_id in data.get('users', []):
        data['users'].remove(user_id)

    # Aggiungi a unsubscribed se non già presente
    if user_id not in data.get('unsubscribed', []):
        data['unsubscribed'].append(user_id)

    _save_users(data)
    logger.info(f"Utente {user_id} disiscritto dai reminder")


def get_all_users():
    """
    Ottieni lista di tutti gli utenti iscritti ai reminder

    Returns:
        list: Lista di user_id
    """
    data = _load_users()
    return data.get('users', [])


def is_user_subscribed(user_id):
    """
    Verifica se un utente è iscritto ai reminder

    Args:
        user_id (int): ID Telegram dell'utente

    Returns:
        bool: True se iscritto, False altrimenti
    """
    data = _load_users()
    return int(user_id) in data.get('users', [])


async def stop_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler per comando /stop - disattiva i reminder giornalieri
    """
    user_id = update.effective_user.id
    remove_user(user_id)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=config.MESSAGES['reminders_stopped']
    )
    logger.info(f"Utente {user_id} ha disattivato i reminder con /stop")


async def start_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler per comando /start - attiva i reminder giornalieri
    (Questa funzione verrà chiamata dal main.py modificando il comando start esistente)
    """
    user_id = update.effective_user.id
    was_new = save_user(user_id)

    if was_new:
        message = config.MESSAGES['reminders_reactivated']
    else:
        message = config.MESSAGES['already_subscribed']

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message
    )
    logger.info(f"Utente {user_id} attivato con /start")
