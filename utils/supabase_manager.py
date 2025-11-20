"""
Manager per Supabase Database - Price Tracking
Gestisce:
- Prodotti tracciati dagli utenti
- Storico prezzi prodotti
- Alert prezzi personalizzati
- Notifiche price drop
"""
import logging
from datetime import datetime, timedelta
import config

logger = logging.getLogger(__name__)

# Import condizionale - Supabase è opzionale
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    logger.warning("Supabase non installato - funzionalità price tracking disabilitate")


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


# ========================================
# TRACKED PRODUCTS
# ========================================

def add_tracked_product(user_id, asin, product_name, current_price, url):
    """
    Aggiungi prodotto da tracciare per un utente

    Args:
        user_id (int): ID utente Telegram
        asin (str): ASIN prodotto Amazon
        product_name (str): Nome prodotto
        current_price (float): Prezzo attuale in euro
        url (str): URL prodotto Amazon

    Returns:
        bool: True se aggiunto, False altrimenti
    """
    if not SUPABASE_AVAILABLE:
        return False

    client = get_supabase_client()
    if not client:
        return False

    try:
        # Controlla se esiste già
        existing = client.table('tracked_products') \
            .select('*') \
            .eq('user_id', user_id) \
            .eq('asin', asin) \
            .execute()

        if existing.data:
            # Aggiorna prodotto esistente
            data = {
                'product_name': product_name,
                'last_price': current_price,
                'last_checked': datetime.utcnow().isoformat(),
                'url': url
            }

            client.table('tracked_products') \
                .update(data) \
                .eq('user_id', user_id) \
                .eq('asin', asin) \
                .execute()

            logger.info(f"Prodotto {asin} aggiornato per user {user_id}")
        else:
            # Inserisci nuovo prodotto
            data = {
                'user_id': user_id,
                'asin': asin,
                'product_name': product_name,
                'url': url,
                'initial_price': current_price,
                'last_price': current_price,
                'tracked_since': datetime.utcnow().isoformat(),
                'last_checked': datetime.utcnow().isoformat()
            }

            client.table('tracked_products').insert(data).execute()

            logger.info(f"Prodotto {asin} aggiunto per user {user_id}")

        # Aggiungi entry nello storico prezzi
        add_price_history(asin, current_price, product_name)

        return True

    except Exception as e:
        logger.error(f"Errore aggiunta prodotto tracciato: {e}")
        return False


def remove_tracked_product(user_id, asin):
    """
    Rimuovi prodotto dal tracking

    Args:
        user_id (int): ID utente Telegram
        asin (str): ASIN prodotto

    Returns:
        bool: True se rimosso, False altrimenti
    """
    if not SUPABASE_AVAILABLE:
        return False

    client = get_supabase_client()
    if not client:
        return False

    try:
        # Rimuovi anche gli alert associati
        client.table('price_alerts') \
            .delete() \
            .eq('user_id', user_id) \
            .eq('asin', asin) \
            .execute()

        # Rimuovi prodotto
        client.table('tracked_products') \
            .delete() \
            .eq('user_id', user_id) \
            .eq('asin', asin) \
            .execute()

        logger.info(f"Prodotto {asin} rimosso per user {user_id}")
        return True

    except Exception as e:
        logger.error(f"Errore rimozione prodotto: {e}")
        return False


def get_user_tracked_products(user_id):
    """
    Ottieni lista prodotti tracciati da un utente

    Args:
        user_id (int): ID utente Telegram

    Returns:
        list: Lista dict prodotti o []
    """
    if not SUPABASE_AVAILABLE:
        return []

    client = get_supabase_client()
    if not client:
        return []

    try:
        response = client.table('tracked_products') \
            .select('*') \
            .eq('user_id', user_id) \
            .order('tracked_since', desc=True) \
            .execute()

        products = response.data or []
        logger.info(f"Recuperati {len(products)} prodotti per user {user_id}")
        return products

    except Exception as e:
        logger.error(f"Errore recupero prodotti tracciati: {e}")
        return []


def get_all_tracked_products():
    """
    Ottieni TUTTI i prodotti tracciati (per price checker)

    Returns:
        list: Lista dict prodotti o []
    """
    if not SUPABASE_AVAILABLE:
        return []

    client = get_supabase_client()
    if not client:
        return []

    try:
        response = client.table('tracked_products') \
            .select('*') \
            .execute()

        products = response.data or []
        logger.info(f"Recuperati {len(products)} prodotti totali da trackare")
        return products

    except Exception as e:
        logger.error(f"Errore recupero tutti i prodotti: {e}")
        return []


# ========================================
# PRICE HISTORY
# ========================================

def add_price_history(asin, price, product_name=None):
    """
    Aggiungi entry nello storico prezzi

    Args:
        asin (str): ASIN prodotto
        price (float): Prezzo in euro
        product_name (str): Nome prodotto (opzionale)

    Returns:
        bool: True se aggiunto, False altrimenti
    """
    if not SUPABASE_AVAILABLE:
        return False

    client = get_supabase_client()
    if not client:
        return False

    try:
        data = {
            'asin': asin,
            'price': price,
            'currency': 'EUR',
            'product_name': product_name,
            'timestamp': datetime.utcnow().isoformat()
        }

        client.table('price_history').insert(data).execute()

        logger.debug(f"Prezzo {price}€ aggiunto per ASIN {asin}")
        return True

    except Exception as e:
        logger.error(f"Errore salvataggio storico prezzo: {e}")
        return False


def get_price_history(asin, days=30):
    """
    Ottieni storico prezzi per un prodotto

    Args:
        asin (str): ASIN prodotto
        days (int): Giorni di storico (default 30)

    Returns:
        list: Lista dict {timestamp, price} o []
    """
    if not SUPABASE_AVAILABLE:
        return []

    client = get_supabase_client()
    if not client:
        return []

    try:
        cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()

        response = client.table('price_history') \
            .select('timestamp, price') \
            .eq('asin', asin) \
            .gte('timestamp', cutoff_date) \
            .order('timestamp', desc=False) \
            .execute()

        history = response.data or []
        logger.info(f"Recuperato storico {len(history)} prezzi per ASIN {asin}")
        return history

    except Exception as e:
        logger.error(f"Errore recupero storico prezzi: {e}")
        return []


def update_product_price(asin, new_price):
    """
    Aggiorna prezzo prodotto e aggiunge a storico

    Args:
        asin (str): ASIN prodotto
        new_price (float): Nuovo prezzo

    Returns:
        dict: Info prodotti aggiornati o None
    """
    if not SUPABASE_AVAILABLE:
        return None

    client = get_supabase_client()
    if not client:
        return None

    try:
        # Aggiorna last_price in tracked_products
        data = {
            'last_price': new_price,
            'last_checked': datetime.utcnow().isoformat()
        }

        response = client.table('tracked_products') \
            .update(data) \
            .eq('asin', asin) \
            .execute()

        # Aggiungi a storico
        add_price_history(asin, new_price)

        logger.info(f"Prezzo aggiornato a {new_price}€ per ASIN {asin}")
        return response.data

    except Exception as e:
        logger.error(f"Errore aggiornamento prezzo: {e}")
        return None


# ========================================
# PRICE ALERTS
# ========================================

def set_price_alert(user_id, asin, target_price):
    """
    Imposta alert prezzo per un prodotto

    Args:
        user_id (int): ID utente Telegram
        asin (str): ASIN prodotto
        target_price (float): Prezzo target in euro

    Returns:
        bool: True se impostato, False altrimenti
    """
    if not SUPABASE_AVAILABLE:
        return False

    client = get_supabase_client()
    if not client:
        return False

    try:
        # Controlla se alert esiste già
        existing = client.table('price_alerts') \
            .select('*') \
            .eq('user_id', user_id) \
            .eq('asin', asin) \
            .execute()

        if existing.data:
            # Aggiorna alert esistente
            data = {
                'target_price': target_price,
                'is_active': True
            }

            client.table('price_alerts') \
                .update(data) \
                .eq('user_id', user_id) \
                .eq('asin', asin) \
                .execute()

            logger.info(f"Alert aggiornato a {target_price}€ per user {user_id} ASIN {asin}")
        else:
            # Crea nuovo alert
            data = {
                'user_id': user_id,
                'asin': asin,
                'target_price': target_price,
                'is_active': True,
                'created_at': datetime.utcnow().isoformat()
            }

            client.table('price_alerts').insert(data).execute()

            logger.info(f"Alert creato a {target_price}€ per user {user_id} ASIN {asin}")

        return True

    except Exception as e:
        logger.error(f"Errore impostazione alert: {e}")
        return False


def get_triggered_alerts():
    """
    Ottieni alert che sono stati triggered (prezzo raggiunto)

    Returns:
        list: Lista dict {user_id, asin, target_price, current_price, product_name} o []
    """
    if not SUPABASE_AVAILABLE:
        return []

    client = get_supabase_client()
    if not client:
        return []

    try:
        # Query che fa join tra price_alerts e tracked_products
        # per trovare prodotti con prezzo <= target_price
        response = client.rpc('get_triggered_alerts').execute()

        alerts = response.data or []
        logger.info(f"Trovati {len(alerts)} alert triggered")
        return alerts

    except Exception as e:
        # Se RPC non esiste, fallback a query manuale
        logger.warning(f"RPC get_triggered_alerts non disponibile: {e}")

        try:
            # Fallback: query manuale
            alerts_data = client.table('price_alerts') \
                .select('*, tracked_products(*)') \
                .eq('is_active', True) \
                .execute()

            triggered = []
            for alert in alerts_data.data or []:
                product = alert.get('tracked_products', [{}])[0] if alert.get('tracked_products') else {}
                current_price = product.get('last_price', float('inf'))
                target_price = alert.get('target_price', 0)

                if current_price <= target_price:
                    triggered.append({
                        'user_id': alert['user_id'],
                        'asin': alert['asin'],
                        'target_price': target_price,
                        'current_price': current_price,
                        'product_name': product.get('product_name', 'Prodotto'),
                        'url': product.get('url', '')
                    })

            logger.info(f"Trovati {len(triggered)} alert triggered (fallback)")
            return triggered

        except Exception as e2:
            logger.error(f"Errore fallback get_triggered_alerts: {e2}")
            return []


def deactivate_alert(user_id, asin):
    """
    Disattiva alert per un prodotto

    Args:
        user_id (int): ID utente
        asin (str): ASIN prodotto

    Returns:
        bool: True se disattivato, False altrimenti
    """
    if not SUPABASE_AVAILABLE:
        return False

    client = get_supabase_client()
    if not client:
        return False

    try:
        data = {'is_active': False}

        client.table('price_alerts') \
            .update(data) \
            .eq('user_id', user_id) \
            .eq('asin', asin) \
            .execute()

        logger.info(f"Alert disattivato per user {user_id} ASIN {asin}")
        return True

    except Exception as e:
        logger.error(f"Errore disattivazione alert: {e}")
        return False


# ========================================
# STATISTICS
# ========================================

def get_user_stats(user_id):
    """
    Ottieni statistiche tracking per utente

    Args:
        user_id (int): ID utente

    Returns:
        dict: Statistiche o {}
    """
    if not SUPABASE_AVAILABLE:
        return {}

    client = get_supabase_client()
    if not client:
        return {}

    try:
        products = get_user_tracked_products(user_id)

        total_products = len(products)
        total_savings = 0

        for product in products:
            initial = product.get('initial_price', 0)
            current = product.get('last_price', 0)
            if initial > current:
                total_savings += (initial - current)

        return {
            'total_products': total_products,
            'total_savings': round(total_savings, 2),
            'active_alerts': len([p for p in products if p.get('has_alert', False)])
        }

    except Exception as e:
        logger.error(f"Errore recupero stats: {e}")
        return {}


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
        response = client.table('tracked_products').select('id').limit(1).execute()
        logger.info("Supabase health check: OK")
        return True

    except Exception as e:
        logger.error(f"Supabase health check failed: {e}")
        return False


# ========================================
# SQL SCHEMA
# ========================================

SUPABASE_SCHEMA = """
-- =========================================
-- SCHEMA PRICE TRACKING
-- =========================================

-- Tabella prodotti tracciati
CREATE TABLE IF NOT EXISTS tracked_products (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    asin VARCHAR(20) NOT NULL,
    product_name TEXT NOT NULL,
    url TEXT NOT NULL,
    initial_price DECIMAL(10, 2) NOT NULL,
    last_price DECIMAL(10, 2) NOT NULL,
    tracked_since TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_checked TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, asin)
);

CREATE INDEX idx_tracked_products_user_id ON tracked_products(user_id);
CREATE INDEX idx_tracked_products_asin ON tracked_products(asin);
CREATE INDEX idx_tracked_products_last_checked ON tracked_products(last_checked);

-- Tabella storico prezzi
CREATE TABLE IF NOT EXISTS price_history (
    id BIGSERIAL PRIMARY KEY,
    asin VARCHAR(20) NOT NULL,
    product_name TEXT,
    price DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'EUR',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_price_history_asin ON price_history(asin);
CREATE INDEX idx_price_history_timestamp ON price_history(timestamp DESC);

-- Tabella alert prezzi
CREATE TABLE IF NOT EXISTS price_alerts (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    asin VARCHAR(20) NOT NULL,
    target_price DECIMAL(10, 2) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    triggered_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(user_id, asin)
);

CREATE INDEX idx_price_alerts_user_id ON price_alerts(user_id);
CREATE INDEX idx_price_alerts_asin ON price_alerts(asin);
CREATE INDEX idx_price_alerts_active ON price_alerts(is_active) WHERE is_active = TRUE;

-- Enable Row Level Security
ALTER TABLE tracked_products ENABLE ROW LEVEL SECURITY;
ALTER TABLE price_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE price_alerts ENABLE ROW LEVEL SECURITY;

-- Policy per service_role (full access)
CREATE POLICY "Service role has full access" ON tracked_products
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role has full access" ON price_history
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role has full access" ON price_alerts
    FOR ALL USING (auth.role() = 'service_role');

-- Funzione per ottenere alert triggered (opzionale ma più efficiente)
CREATE OR REPLACE FUNCTION get_triggered_alerts()
RETURNS TABLE (
    user_id BIGINT,
    asin VARCHAR(20),
    target_price DECIMAL(10, 2),
    current_price DECIMAL(10, 2),
    product_name TEXT,
    url TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        pa.user_id,
        pa.asin,
        pa.target_price,
        tp.last_price AS current_price,
        tp.product_name,
        tp.url
    FROM price_alerts pa
    INNER JOIN tracked_products tp ON pa.asin = tp.asin AND pa.user_id = tp.user_id
    WHERE pa.is_active = TRUE
    AND tp.last_price <= pa.target_price;
END;
$$ LANGUAGE plpgsql;
"""

if __name__ == "__main__":
    print("=== SCHEMA SQL PER SUPABASE PRICE TRACKING ===\n")
    print(SUPABASE_SCHEMA)
    print("\n⚠️ Copia questo SQL nel Supabase SQL Editor per creare le tabelle")
