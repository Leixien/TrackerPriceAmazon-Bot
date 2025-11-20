# 🗄️ Setup Supabase Database (Opzionale)

Guida per configurare Supabase come database per storico conversazioni e analytics.

> **⚠️ NOTA**: Supabase è **opzionale**. Il bot funziona perfettamente anche senza!
>
> Usa Supabase se vuoi:
> - Storico conversazioni permanente
> - Analytics avanzate
> - Sync multi-device
> - Backup automatico

---

## 📋 Vantaggi Supabase

✅ **Piano FREE** (senza carta di credito):
- 500MB database storage
- 2GB bandwidth/mese
- 50.000 richieste/mese
- Backup automatici

✅ **Features**:
- PostgreSQL completo
- API REST automatica
- Dashboard web
- Row Level Security

---

## 🚀 Setup (5 minuti)

### 1. Crea Account Supabase

1. Vai su https://supabase.com
2. Click su "Start your project"
3. Sign up con GitHub/Google (gratis, no carta)

### 2. Crea Nuovo Progetto

1. Click "+ New project"
2. Nome progetto: `amazon-bot` (o quello che vuoi)
3. Database Password: Genera una strong password (salvala!)
4. Region: `Europe (West)` (consigliato per Italia)
5. Click "Create new project"

⏱️ Attendi 1-2 minuti per provisioning...

### 3. Ottieni Credenziali

Una volta creato il progetto:

1. Nel menu laterale, vai a ⚙️ **Settings** → **API**
2. Copia:
   - **Project URL** (es: `https://abcdefgh.supabase.co`)
   - **Project API Key** (`anon/public` key)

### 4. Crea Tabelle Database

1. Nel menu laterale, vai a 🔨 **SQL Editor**
2. Click "+ New query"
3. Copia e incolla questo SQL:

```sql
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

-- Enable Row Level Security (RLS)
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE product_cache ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_analytics ENABLE ROW LEVEL SECURITY;

-- Policy per service_role (full access)
CREATE POLICY "Service role has full access" ON conversations
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role has full access" ON product_cache
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role has full access" ON ai_analytics
    FOR ALL USING (auth.role() = 'service_role');
```

4. Click "Run" o premisend Cmd/Ctrl + Enter
5. Dovresti vedere "Success. No rows returned"

### 5. Configura Bot

Modifica `.env` sul server del bot:

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

### Test 1: Invia Messaggio al Bot

Su Telegram:
```
Mi consigli un laptop gaming?
```

### Test 2: Controlla Dashboard Supabase

1. Vai su Supabase Dashboard
2. Menu laterale → 🗂️ **Table Editor**
3. Seleziona tabella `conversations`
4. Dovresti vedere la tua conversazione salvata!

---

## 📊 Interrogare il Database

### Via Dashboard (GUI)

Dashboard → Table Editor → Seleziona tabella

### Via SQL Editor

Esempi query utili:

```sql
-- Conversazioni recenti
SELECT * FROM conversations
ORDER BY created_at DESC
LIMIT 10;

-- Conversazioni per utente
SELECT * FROM conversations
WHERE user_id = 123456789
ORDER BY created_at DESC;

-- Statistiche utenti più attivi
SELECT user_id, COUNT(*) as num_messages
FROM conversations
GROUP BY user_id
ORDER BY num_messages DESC;

-- Analytics tempi risposta
SELECT
    DATE(created_at) as date,
    AVG(response_time_ms) as avg_response_ms,
    COUNT(*) as num_requests
FROM ai_analytics
GROUP BY DATE(created_at)
ORDER BY date DESC;
```

---

## 🔒 Sicurezza

### Row Level Security (RLS)

Le policy create permettono solo al bot (service_role) di accedere ai dati.

### Protezione API Key

⚠️ **MAI condividere** la `SUPABASE_KEY`!

✅ Usa variabili d'ambiente (`.env`)
✅ Aggiungi `.env` al `.gitignore`

### Backup

Supabase fa backup automatici, ma puoi esportare manualmente:

Dashboard → Settings → Database → Download backup

---

## 💰 Limiti Piano Free

| Risorsa | Limite |
|---------|--------|
| Storage | 500MB |
| Bandwidth | 2GB/mese |
| Richieste API | 50.000/mese |
| Righe tabella | Illimitate (nel limite storage) |

**Quante conversazioni?**
- Conversazione media: ~500 bytes
- 500MB = ~1.000.000 conversazioni ✅

Difficile raggiungere i limiti per uso normale!

---

## 🔧 Troubleshooting

### Problema: "Supabase non configurato"

**Causa**: SUPABASE_URL o SUPABASE_KEY vuoti

**Soluzione**: Verifica `.env`:
```bash
cat .env | grep SUPABASE
```

### Problema: "Errore connessione Supabase"

**Causa**: Credenziali errate o progetto pausato

**Soluzione**:
1. Verifica credenziali nel dashboard Supabase
2. Verifica progetto attivo (Settings → General)

### Problema: "Row Level Security policy violation"

**Causa**: Policy RLS non configurata

**Soluzione**: Ri-esegui SQL per creare policy (punto 4 setup)

### Problema: "Table does not exist"

**Causa**: Tabelle non create

**Soluzione**: Esegui SQL schema (punto 4 setup)

---

## 🗑️ Pulizia Vecchi Dati

Per evitare di riempire il database:

```sql
-- Elimina conversazioni più vecchie di 90 giorni
DELETE FROM conversations
WHERE created_at < NOW() - INTERVAL '90 days';

-- Elimina cache prodotti più vecchia di 30 giorni
DELETE FROM product_cache
WHERE created_at < NOW() - INTERVAL '30 days';
```

Puoi automatizzare con Supabase Edge Functions o cron job.

---

## 📈 Query Analytics Utili

### Conversazioni per giorno

```sql
SELECT
    DATE(created_at) as date,
    COUNT(*) as num_conversations
FROM conversations
WHERE role = 'user'
GROUP BY DATE(created_at)
ORDER BY date DESC;
```

### Utenti attivi per mese

```sql
SELECT
    DATE_TRUNC('month', created_at) as month,
    COUNT(DISTINCT user_id) as active_users
FROM conversations
GROUP BY DATE_TRUNC('month', created_at)
ORDER BY month DESC;
```

### Query prodotti più cercati (via AI)

```sql
SELECT
    query,
    COUNT(*) as num_searches
FROM ai_analytics
GROUP BY query
ORDER BY num_searches DESC
LIMIT 10;
```

---

## 🚀 Features Avanzate (Opzionali)

### 1. Realtime Updates

Ricevi notifiche quando nuove conversazioni vengono salvate:

```python
# TODO: Implementare con supabase.channel().on()
```

### 2. API REST

Accedi ai dati via HTTP:

```bash
curl https://tuoprogetto.supabase.co/rest/v1/conversations \
  -H "apikey: TUA_API_KEY" \
  -H "Authorization: Bearer TUA_API_KEY"
```

### 3. Dashboard Personalizzata

Crea dashboard con Grafana/Metabase connesso a Supabase PostgreSQL.

---

## ❓ FAQ

**Q: Devo pagare qualcosa?**
A: No! Piano free permanente, no carta di credito.

**Q: Cosa succede se supero i limiti?**
A: Supabase pausa temporaneamente le richieste. Puoi:
- Upgrade a piano Pro ($25/mese)
- Pulire vecchi dati
- Aspettare nuovo mese (reset limiti)

**Q: I dati sono sicuri?**
A: Sì. Supabase usa crittografia, backup, e compliance GDPR.

**Q: Posso migrare da Supabase a altro DB?**
A: Sì! Esporta PostgreSQL dump e importa altrove.

**Q: Funziona senza Supabase?**
A: Sì! Supabase è opzionale. Il bot usa JSON locale come fallback.

---

## 📚 Risorse

- [Supabase Documentation](https://supabase.com/docs)
- [PostgreSQL Tutorial](https://www.postgresqltutorial.com/)
- [Supabase Python Client](https://supabase.com/docs/reference/python/introduction)

---

## ✅ Checklist Setup

- [ ] Account Supabase creato
- [ ] Progetto creato (Europe West)
- [ ] Credenziali copiate (URL + API Key)
- [ ] Tabelle create (SQL eseguito)
- [ ] Policy RLS configurate
- [ ] `.env` aggiornato
- [ ] `pip install supabase` eseguito
- [ ] Bot riavviato
- [ ] Test conversazione salvata OK

🎉 **Setup Supabase completato!** Ora hai storico conversazioni persistente!
