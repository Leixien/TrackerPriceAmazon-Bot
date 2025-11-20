"""
Scheduler per reminder giornalieri agli utenti
"""
import logging
from telegram.ext import ContextTypes
from telegram.error import Forbidden, BadRequest
import config
from utils import user_manager

logger = logging.getLogger(__name__)


async def send_daily_reminder(context: ContextTypes.DEFAULT_TYPE):
    """
    Invia reminder giornaliero a tutti gli utenti iscritti

    Viene eseguito automaticamente agli orari configurati (11:00 e 16:00)
    """
    users = user_manager.get_all_users()
    message = config.MESSAGES['daily_reminder']

    sent_count = 0
    failed_count = 0
    blocked_count = 0

    logger.info(f"Inizio invio reminder giornaliero a {len(users)} utenti")

    for user_id in users:
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=message
            )
            sent_count += 1
            logger.debug(f"Reminder inviato a user {user_id}")

        except Forbidden:
            # Utente ha bloccato il bot
            logger.warning(f"Utente {user_id} ha bloccato il bot, rimozione dai reminder")
            user_manager.remove_user(user_id)
            blocked_count += 1

        except BadRequest as e:
            logger.error(f"BadRequest per user {user_id}: {e}")
            failed_count += 1

        except Exception as e:
            logger.error(f"Errore invio reminder a user {user_id}: {e}")
            failed_count += 1

    logger.info(
        f"Reminder completato: {sent_count} inviati, "
        f"{blocked_count} bloccati, {failed_count} falliti"
    )


def setup_daily_reminders(application):
    """
    Configura i job per i reminder giornalieri

    Args:
        application: Telegram Application instance
    """
    job_queue = application.job_queue

    # Aggiungi un job per ogni orario configurato
    for reminder_time in config.REMINDER_TIMES:
        job_queue.run_daily(
            send_daily_reminder,
            time=reminder_time,
            name=f"daily_reminder_{reminder_time.hour}:{reminder_time.minute}"
        )
        logger.info(f"Reminder giornaliero configurato per le {reminder_time.hour}:{reminder_time.minute:02d}")
