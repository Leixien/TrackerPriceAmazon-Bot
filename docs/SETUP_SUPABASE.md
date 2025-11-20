# 🗄️ Setup Supabase - Price Tracking Database

Guida completa per configurare Supabase come database per **tracking prezzi prodotti Amazon**.

> **⚠️ NOTA**: Supabase è **opzionale**. Il bot funziona anche senza!
>
> Usa Supabase se vuoi:
> - 📊 Tracciare prezzi prodotti Amazon nel tempo
> - 📉 Storico prezzi con grafici
> - 🔔 Alert automatici quando prezzo scende
> - 💾 Backup automatico cloud
> - 📈 Analytics risparmi

---

## 📋 Cos'è il Price Tracking?

Con Supabase abilitato, il bot può:

1. **Tracciare prodotti**: Aggiungi prodotti da monitorare con `/track <link>`
2. **Storico prezzi**: Vedi come il prezzo è cambiato con `/history <ASIN>`
3. **Alert prezzi**: Ricevi notifica quando prezzo scende con `/setalert <ASIN> <prezzo>`
4. **Notifiche automatiche**: Il bot ti avvisa quando il prezzo cambia

---

## 💰 Piano FREE Supabase

✅ **GRATIS FOREVER** (no carta credito):
- 500MB database storage
- 2GB bandwidth/mese
- 50.000 richieste/mese
- Backup automatici

**Capienza**: ~10.000 prodotti tracciati + 100.000 rilevamenti prezzi ✅

---

## 🚀 Setup (10 minuti)

### 1. Crea Account Supabase

1. Vai su https://supabase.com
2. Click "Start your project"
3. Sign up con GitHub/Google (gratis, no carta)

### 2. Crea Progetto

1. Click "+ New project"
2. Nome: `amazon-price-tracker`
3. Database Password: Genera strong password (salvala!)
4. Region: **Europe (West)** (consigliato per Italia)
5. Click "Create new project"

⏱️ Attendi 1-2 minuti...

### 3. Ottieni Credenziali

Una volta creato:

1. Menu laterale → ⚙️ **Settings** → **API**
2. Copia:
   - **Project URL** (es: `https://abc123.supabase.co`)
   - **anon/public API Key** (la chiave `anon`)

### 4. Crea Tabelle Database

1. Menu laterale → 🔨 **SQL Editor**
2. Click "+ New query"
3. Copia e incolla **TUTTO** questo SQL:

```sql
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
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies
        WHERE tablename = 'tracked_products'
        AND policyname = 'Service role has full access'
    ) THEN
        CREATE POLICY "Service role has full access" ON tracked_products
            FOR ALL USING (true);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_policies
        WHERE tablename = 'price_history'
        AND policyname = 'Service role has full access'
    ) THEN
        CREATE POLICY "Service role has full access" ON price_history
            FOR ALL USING (true);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_policies
        WHERE tablename = 'price_alerts'
        AND policyname = 'Service role has full access'
    ) THEN
        CREATE POLICY "Service role has full access" ON price_alerts
            FOR ALL USING (true);
    END IF;
END $$;

-- Funzione per ottenere alert triggered
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
```

4. Click **RUN** o premi Cmd/Ctrl + Enter
5. Dovresti vedere: `Success. No rows returned`

✅ **Tabelle create!**

### 5. Configura Bot

Sul server del bot, modifica `.env`:

```bash
nano .env
```

Aggiungi:

```env
# Supabase Configuration
SUPABASE_URL=https://tuoprogetto.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Sostituisci con i tuoi valori copiati al punto 3.

### 6. Installa Libreria Python

```bash
pip install supabase
```

O aggiungi a `requirements.txt`:
```
supabase>=2.0.0
```

### 7. Restart Bot

```bash
python main.py
```

Nell'output dovresti vedere:
```
Supabase health check: OK
```

---

## ✅ Verifica Funzionamento

### Test 1: Traccia Prodotto

Su Telegram:
```
/track https://www.amazon.it/dp/B08N5WRWNW/
```

Risposta attesa:
```
✅ Prodotto aggiunto al tracking!
📦 Nome prodotto...
💰 Prezzo attuale: 99.99€
```

### Test 2: Controlla Dashboard Supabase

1. Dashboard Supabase → 🗂️ **Table Editor**
2. Seleziona tabella `tracked_products`
3. Dovresti vedere il prodotto appena aggiunto!

### Test 3: Vedi Prodotti Tracciati

```
/myproducts
```

---

## 🔔 Setup Cron Job (Controllo Prezzi Automatico)

Per controllare i prezzi periodicamente e inviare notifiche, configura un cron job:

### Opzione 1: Cron (Semplice)

```bash
# Apri crontab
crontab -e

# Aggiungi (controlla ogni 6 ore)
0 */6 * * * cd /path/to/TrackerPriceAmazon-Bot && python scripts/check_prices.py >> logs/price_check.log 2>&1

# Salva e chiudi
```

### Opzione 2: Systemd Timer (Avanzato)

Crea `/etc/systemd/system/amazon-price-check.service`:

```ini
[Unit]
Description=Amazon Price Checker
After=network.target

[Service]
Type=oneshot
User=tuoutente
WorkingDirectory=/path/to/TrackerPriceAmazon-Bot
ExecStart=/usr/bin/python3 scripts/check_prices.py
StandardOutput=append:/var/log/price-check.log
StandardError=append:/var/log/price-check.log
```

Crea `/etc/systemd/system/amazon-price-check.timer`:

```ini
[Unit]
Description=Amazon Price Check Timer
Requires=amazon-price-check.service

[Timer]
OnCalendar=*-*-* 00/6:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

Attiva:
```bash
sudo systemctl daemon-reload
sudo systemctl enable amazon-price-check.timer
sudo systemctl start amazon-price-check.timer

# Verifica
sudo systemctl status amazon-price-check.timer
```

### Test Manuale

```bash
cd /path/to/TrackerPriceAmazon-Bot
python scripts/check_prices.py
```

---

## 📱 Comandi Bot Disponibili

Con Supabase configurato:

| Comando | Descrizione | Esempio |
|---------|-------------|---------|
| `/track <link>` | Aggiungi prodotto al tracking | `/track https://amazon.it/dp/...` |
| `/untrack <ASIN>` | Rimuovi prodotto | `/untrack B08N5WRWNW` |
| `/myproducts` | Lista prodotti tracciati | `/myproducts` |
| `/setalert <ASIN> <prezzo>` | Imposta alert prezzo | `/setalert B08N5WRWNW 50` |
| `/history <ASIN>` | Storico prezzi (30 giorni) | `/history B08N5WRWNW` |

---

## 📊 Query Analytics Utili

### Prodotti tracciati per utente

```sql
SELECT user_id, COUNT(*) as num_products
FROM tracked_products
GROUP BY user_id
ORDER BY num_products DESC;
```

### Prodotti con maggior sconto

```sql
SELECT
    product_name,
    asin,
    initial_price,
    last_price,
    (initial_price - last_price) as discount,
    ROUND(((initial_price - last_price) / initial_price * 100), 2) as discount_pct
FROM tracked_products
WHERE initial_price > last_price
ORDER BY discount DESC
LIMIT 10;
```

### Storico prezzi prodotto

```sql
SELECT
    TO_CHAR(timestamp, 'YYYY-MM-DD HH24:MI') as datetime,
    price
FROM price_history
WHERE asin = 'B08N5WRWNW'
ORDER BY timestamp DESC
LIMIT 50;
```

### Alert attivi

```sql
SELECT
    pa.user_id,
    tp.product_name,
    pa.target_price,
    tp.last_price,
    (tp.last_price - pa.target_price) as diff
FROM price_alerts pa
JOIN tracked_products tp ON pa.user_id = tp.user_id AND pa.asin = tp.asin
WHERE pa.is_active = TRUE
ORDER BY diff ASC;
```

---

## 🔧 Troubleshooting

### Problema: "Supabase non configurato"

**Causa**: `SUPABASE_URL` o `SUPABASE_KEY` vuoti in `.env`

**Soluzione**:
```bash
cat .env | grep SUPABASE
# Verifica che siano impostati
```

### Problema: "Table does not exist"

**Causa**: Tabelle non create

**Soluzione**: Ri-esegui SQL schema (punto 4 setup)

### Problema: "Policy violation"

**Causa**: RLS policy non configurata

**Soluzione**: Verifica di aver eseguito **tutto** lo SQL, incluse le policy

### Problema: Cron job non funziona

**Causa**: Path errato o permessi

**Soluzione**:
```bash
# Test manuale
cd /path/to/bot
python scripts/check_prices.py

# Verifica cron log
grep CRON /var/log/syslog
```

### Problema: Bot lento dopo tracking molti prodotti

**Causa**: Rate limiting Amazon

**Soluzione**: Aumenta delay in `scripts/check_prices.py` (riga con `asyncio.sleep`)

---

## 🗑️ Pulizia Dati Vecchi

Per evitare di riempire il database (piano free 500MB):

```sql
-- Elimina storico prezzi più vecchio di 90 giorni
DELETE FROM price_history
WHERE timestamp < NOW() - INTERVAL '90 days';

-- Elimina prodotti non controllati da 30+ giorni
DELETE FROM tracked_products
WHERE last_checked < NOW() - INTERVAL '30 days';
```

Automatizza con Supabase Edge Function o cron job.

---

## 💡 Tips & Best Practices

### 1. Frequenza Check Prezzi

- **Ogni 6 ore**: Consigliato (4 check/giorno)
- **Ogni 12 ore**: OK per pochi prodotti
- **Ogni 1 ora**: ⚠️ Rischio ban Amazon

### 2. Limita Prodotti per Utente

Per evitare abusi, limita numero prodotti:

```python
# In price_tracker.py, funzione track_product_command
products = supabase_manager.get_user_tracked_products(user_id)
if len(products) >= 10:
    await context.bot.send_message(...)
    return
```

### 3. Monitora Usage Supabase

Dashboard → Settings → Usage

Controlla:
- Storage used
- Bandwidth
- API requests

### 4. Backup Periodico

```bash
# Export database
pg_dump "postgresql://..." > backup.sql
```

---

## ❓ FAQ

**Q: Devo pagare qualcosa?**
A: No! Piano free permanente, no carta credito.

**Q: Quanti prodotti posso tracciare?**
A: Limite storage 500MB = ~10.000 prodotti + 100.000 rilevamenti.

**Q: Funziona senza Supabase?**
A: Sì! Supabase è opzionale. Senza Supabase il bot funziona normalmente ma senza price tracking.

**Q: I dati sono sicuri?**
A: Sì. Supabase usa crittografia + backup + GDPR compliance.

**Q: Posso vedere grafici prezzi?**
A: Sì! Dashboard Supabase → Table Editor → price_history → Chart view.

**Q: Amazon può bannarmi?**
A: Improbabile se segui rate limiting (2s tra richieste). Non fare scraping aggressivo.

---

## 📚 Risorse

- [Supabase Documentation](https://supabase.com/docs)
- [PostgreSQL Tutorial](https://www.postgresqltutorial.com/)
- [Amazon scraping best practices](https://scrapeops.io/web-scraping-playbook/amazon-scraper/)

---

## ✅ Checklist Setup

- [ ] Account Supabase creato
- [ ] Progetto creato (Europe West)
- [ ] Credenziali copiate (URL + API Key)
- [ ] Tabelle create (SQL eseguito)
- [ ] `.env` aggiornato
- [ ] `pip install supabase` eseguito
- [ ] Bot riavviato
- [ ] Test `/track` funzionante
- [ ] Cron job configurato
- [ ] Primo alert testato

🎉 **Setup Supabase Price Tracking completato!**

Ora il bot traccia prezzi e invia notifiche automatiche! 📉🔔
