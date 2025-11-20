"""
AI Assistant per consigli prodotti Amazon intelligenti
Utilizza Ollama (locale) per generare consigli basati su richieste utente
"""
import logging
import re
from telegram import Update
from telegram.ext import ContextTypes
import config
from utils import ollama_client, supabase_manager, user_manager
from handlers import amazon_affiliate

logger = logging.getLogger(__name__)


def is_product_request(message_text):
    """
    Classifica se il messaggio è una richiesta di consigli prodotti

    Args:
        message_text (str): Testo del messaggio utente

    Returns:
        bool: True se è richiesta prodotto, False altrimenti
    """
    # Keywords che indicano richiesta prodotto
    product_keywords = [
        'consiglia', 'consiglio', 'suggerisci', 'suggerimento',
        'cerco', 'sto cercando', 'mi serve', 'ho bisogno',
        'quale', 'qual è', 'migliore', 'meglio',
        'comprare', 'acquistare', 'compare',
        'differenza tra', 'confronta', 'vs',
        'vale la pena', 'conviene',
        'prodotto', 'articolo', 'cosa comprare',
        'budget', 'sotto', 'euro', '€',
        'recensione', 'opinione', 'pareri'
    ]

    # Categorie prodotti comuni
    product_categories = [
        'laptop', 'computer', 'pc', 'tablet', 'smartphone', 'telefono',
        'cuffie', 'auricolari', 'speaker', 'altoparlante',
        'tastiera', 'mouse', 'monitor', 'schermo',
        'tv', 'televisore', 'televisione',
        'fotocamera', 'camera', 'gopro',
        'console', 'playstation', 'xbox', 'nintendo', 'switch',
        'libro', 'libri', 'romanzo',
        'zaino', 'borsa', 'valigia',
        'scarpe', 'scarpa', 'sneakers',
        'orologio', 'smartwatch',
        'aspirapolvere', 'robot', 'roomba',
        'microonde', 'forno', 'friggitrice',
        'caffettiera', 'macchina caffè',
        'drone', 'stampante', 'hard disk', 'ssd',
        'caricabatterie', 'powerbank', 'batteria'
    ]

    message_lower = message_text.lower()

    # Verifica presenza keywords
    for keyword in product_keywords:
        if keyword in message_lower:
            return True

    # Verifica presenza categorie prodotti
    for category in product_categories:
        if category in message_lower:
            return True

    return False


async def handle_ai_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler principale per richieste AI

    Flusso:
    1. Verifica se è richiesta prodotto
    2. Se no → messaggio informativo
    3. Se sì → genera consigli con AI + link affiliati
    """
    user_id = update.effective_user.id
    message_text = update.message.text

    # Registra utente
    user_manager.save_user(user_id)

    # Classifica messaggio
    if not is_product_request(message_text):
        # Non è richiesta prodotto
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=config.MESSAGES['ai_not_product_request']
        )
        logger.info(f"User {user_id} ha inviato messaggio non-prodotto: {message_text[:50]}")
        return

    # È richiesta prodotto - mostra "typing..."
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )

    logger.info(f"Richiesta prodotto AI da user {user_id}: {message_text[:100]}")

    # Salva conversazione in Supabase (opzionale se configurato)
    supabase_manager.save_conversation(user_id, message_text, "user")

    # Genera risposta AI
    try:
        ai_response = await ollama_client.generate_product_advice(message_text, user_id)

        if not ai_response:
            # Errore AI
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=config.MESSAGES['ai_error']
            )
            return

        # Estrai eventuali link Amazon dalla risposta AI e convertili
        amazon_links = extract_amazon_links_from_text(ai_response)

        if amazon_links:
            # Converti link in affiliati
            converted_links = []
            for link in amazon_links:
                asin = amazon_affiliate.extract_asin(link)
                if asin:
                    affiliate_link = amazon_affiliate.create_affiliate_link(asin)
                    ai_response = ai_response.replace(link, affiliate_link)
                    converted_links.append(affiliate_link)
                    amazon_affiliate.increment_stats(user_id)

            logger.info(f"Convertiti {len(converted_links)} link in risposta AI")

        # Invia risposta
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=ai_response,
            parse_mode='Markdown',
            disable_web_page_preview=False
        )

        # Salva risposta in Supabase
        supabase_manager.save_conversation(user_id, ai_response, "assistant")

        logger.info(f"Risposta AI inviata a user {user_id}")

    except Exception as e:
        logger.error(f"Errore generazione risposta AI: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=config.MESSAGES['ai_error']
        )


def extract_amazon_links_from_text(text):
    """
    Estrae link Amazon da un testo

    Args:
        text (str): Testo da analizzare

    Returns:
        list: Lista di URL Amazon trovati
    """
    url_pattern = r'https?://(?:www\.)?amazon\.it[^\s]+'
    return re.findall(url_pattern, text)


async def search_amazon_products(query, max_results=3):
    """
    Cerca prodotti su Amazon.it (placeholder - richiede Amazon API o scraping)

    Args:
        query (str): Query di ricerca
        max_results (int): Numero massimo risultati

    Returns:
        list: Lista di dict con {title, price, asin, url}
    """
    # TODO: Implementare con Amazon Product Advertising API o scraping
    # Per ora ritorna lista vuota
    logger.warning("search_amazon_products non implementato - richiede Amazon API")
    return []


async def ai_help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Comando /aihelp - Spiega come funziona l'AI assistant
    """
    help_message = """🤖 <b>AI Product Advisor</b>

Sono un assistente intelligente specializzato in <b>consigli su prodotti Amazon</b>!

<b>Come funziono:</b>
✅ Chiedimi consigli su prodotti
✅ Confronto tra prodotti
✅ Suggerimenti basati sul budget
✅ Analisi caratteristiche

<b>Esempi di domande:</b>
• "Mi consigli un laptop per gaming sotto 1000€?"
• "Quale è il miglior smartphone fotocamera?"
• "Confronta iPhone 15 vs Samsung S24"
• "Ho bisogno di cuffie wireless per correre"
• "Cerco una friggitrice ad aria buona"

<b>Come rispondo:</b>
🔍 Analizzo la tua richiesta
💡 Genero consigli personalizzati
🔗 Fornisco link affiliati Amazon

⚠️ <b>Nota:</b> Rispondo SOLO a richieste di consigli prodotti!

<i>Powered by Ollama AI (locale) 🚀</i>
"""

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=help_message,
        parse_mode='HTML'
    )

    logger.info(f"AI help richiesto da user {update.effective_user.id}")
