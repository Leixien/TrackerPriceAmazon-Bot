"""
Manager per Supabase Database
Gestisce:
- Storico conversazioni AI
- Cache ricerche prodotti
- Analytics avanzate
"""
import logging
from datetime import datetime
import config

logger = logging.getLogger(__name__)

# Import condizionale - Supabase è opzionale
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    logger.warning("Supabase non installato - funzionalità DB disabilitate")


def get_supabase_client():
    """
    Ottieni client Supabase (lazy initialization)

    Returns:
        Client: Supabase client o None se non configurato
    """
    if not SUPABASE_AVAILABLE:
        return None

    if not config.SUPABASE_URL or not config.SUPABASE_KEY:
        logger.warning("Supabase non configurato (URL/KEY mancanti)")
        return None

    try:
        client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
        return client
    except Exception as e:
        logger.error(f"Errore connessione Supabase: {e}")
        return None


def save_conversation(user_id, message, role="user"):
    """
    Salva conversazione nel database Supabase

    Args:
        user_id (int): ID utente Telegram
        message (str): Testo messaggio
        role (str): "user" o "assistant"

    Returns:
        bool: True se salvato, False altrimenti
    """
    if not SUPABASE_AVAILABLE:
        return False

    client = get_supabase_client()
    if not client:
        return False

    try:
        data = {
            "user_id": user_id,
            "message": message,
            "role": role,
            "created_at": datetime.utcnow().isoformat()
        }

        response = client.table('conversations').insert(data).execute()

        logger.info(f"Conversazione salvata su Supabase: user {user_id}, role {role}")
        return True

    except Exception as e:
        logger.error(f"Errore salvataggio conversazione Supabase: {e}")
        return False


def get_user_conversation_history(user_id, limit=10):
    """
    Recupera storico conversazioni utente

    Args:
        user_id (int): ID utente Telegram
        limit (int): Numero massimo messaggi

    Returns:
        list: Lista conversazioni o []
    """
    if not SUPABASE_AVAILABLE:
        return []

    client = get_supabase_client()
    if not client:
        return []

    try:
        response = client.table('conversations') \
            .select('*') \
            .eq('user_id', user_id) \
            .order('created_at', desc=True) \
            .limit(limit) \
            .execute()

        conversations = response.data
        logger.info(f"Recuperate {len(conversations)} conversazioni per user {user_id}")
        return conversations

    except Exception as e:
        logger.error(f"Errore recupero conversazioni Supabase: {e}")
        return []


def save_product_cache(query, products):
    """
    Salva cache ricerca prodotti per ottimizzare performance

    Args:
        query (str): Query di ricerca
        products (list): Lista prodotti trovati

    Returns:
        bool: True se salvato, False altrimenti
    """
    if not SUPABASE_AVAILABLE:
        return False

    client = get_supabase_client()
    if not client:
        return False

    try:
        data = {
            "query": query.lower(),
            "products": products,
            "created_at": datetime.utcnow().isoformat()
        }

        response = client.table('product_cache').insert(data).execute()

        logger.info(f"Cache prodotti salvata: {query}")
        return True

    except Exception as e:
        logger.error(f"Errore salvataggio cache prodotti: {e}")
        return False


def get_product_cache(query, max_age_hours=24):
    """
    Recupera cache prodotti se recente

    Args:
        query (str): Query di ricerca
        max_age_hours (int): Età massima cache in ore

    Returns:
        list: Prodotti cached o None
    """
    if not SUPABASE_AVAILABLE:
        return None

    client = get_supabase_client()
    if not client:
        return None

    try:
        from datetime import timedelta

        cutoff_time = (datetime.utcnow() - timedelta(hours=max_age_hours)).isoformat()

        response = client.table('product_cache') \
            .select('products') \
            .eq('query', query.lower()) \
            .gte('created_at', cutoff_time) \
            .order('created_at', desc=True) \
            .limit(1) \
            .execute()

        if response.data:
            products = response.data[0]['products']
            logger.info(f"Cache prodotti trovata per: {query}")
            return products
        else:
            logger.info(f"Nessuna cache prodotti per: {query}")
            return None

    except Exception as e:
        logger.error(f"Errore recupero cache prodotti: {e}")
        return None


def log_ai_request(user_id, query, response_time_ms):
    """
    Log analytics richiesta AI

    Args:
        user_id (int): ID utente
        query (str): Query utente
        response_time_ms (int): Tempo risposta in millisecondi

    Returns:
        bool: True se salvato, False altrimenti
    """
    if not SUPABASE_AVAILABLE:
        return False

    client = get_supabase_client()
    if not client:
        return False

    try:
        data = {
            "user_id": user_id,
            "query": query,
            "response_time_ms": response_time_ms,
            "created_at": datetime.utcnow().isoformat()
        }

        response = client.table('ai_analytics').insert(data).execute()

        logger.debug(f"Analytics AI salvate: user {user_id}, {response_time_ms}ms")
        return True

    except Exception as e:
        logger.error(f"Errore salvataggio analytics AI: {e}")
        return False


def check_supabase_health():
    """
    Verifica connessione Supabase

    Returns:
        bool: True se connesso, False altrimenti
    """
    if not SUPABASE_AVAILABLE:
        return False

    client = get_supabase_client()
    if not client:
        return False

    try:
        # Test query
        response = client.table('conversations').select('id').limit(1).execute()
        logger.info("Supabase health check: OK")
        return True

    except Exception as e:
        logger.error(f"Supabase health check failed: {e}")
        return False


# SQL per creare tabelle Supabase (esegui manualmente nel dashboard)
SUPABASE_SCHEMA = """
-- Tabella conversazioni
CREATE TABLE conversations (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    message TEXT NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_created_at ON conversations(created_at DESC);

-- Tabella cache prodotti
CREATE TABLE product_cache (
    id BIGSERIAL PRIMARY KEY,
    query TEXT NOT NULL,
    products JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_product_cache_query ON product_cache(query);
CREATE INDEX idx_product_cache_created_at ON product_cache(created_at DESC);

-- Tabella analytics AI
CREATE TABLE ai_analytics (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    query TEXT NOT NULL,
    response_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_ai_analytics_user_id ON ai_analytics(user_id);
CREATE INDEX idx_ai_analytics_created_at ON ai_analytics(created_at DESC);

-- Enable Row Level Security (RLS) per sicurezza
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE product_cache ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_analytics ENABLE ROW LEVEL SECURITY;

-- Policy per service_role (full access)
CREATE POLICY "Service role has full access" ON conversations
    FOR ALL USING (true);

CREATE POLICY "Service role has full access" ON product_cache
    FOR ALL USING (true);

CREATE POLICY "Service role has full access" ON ai_analytics
    FOR ALL USING (true);
"""

if __name__ == "__main__":
    print("Supabase Schema SQL:")
    print(SUPABASE_SCHEMA)
    print("\n⚠️ Copia questo SQL nel Supabase SQL Editor per creare le tabelle")
