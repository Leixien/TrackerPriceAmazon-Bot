# 🤖 Setup AI Assistant (Ollama)

Guida completa per configurare l'assistente AI locale sul Raspberry Pi.

## 📋 Prerequisiti

### Hardware
- **Raspberry Pi 4/5** (consigliato)
  - 4GB RAM → Mistral 7B
  - 2GB RAM → LLaMA 3.2 3B
- **Raspberry Pi 3/Zero** (limitato)
  - 2GB RAM → LLaMA 3.2 1B

### Software
- Raspberry Pi OS (64-bit) o Ubuntu Server 64-bit
- Python 3.9+
- Accesso root (sudo)

---

## 🚀 Installazione Automatica (Consigliata)

### 1. Scarica e esegui lo script

Sul Raspberry Pi, esegui:

```bash
cd /path/to/TrackerPriceAmazon-Bot
chmod +x scripts/setup_raspberry_ollama.sh
./scripts/setup_raspberry_ollama.sh
```

Lo script:
- ✅ Verifica architettura e RAM
- ✅ Installa Ollama
- ✅ Avvia il servizio
- ✅ Scarica il modello AI
- ✅ Testa l'installazione

### 2. Copia la configurazione

Alla fine dello script, copia le variabili nel file `.env` del bot:

```bash
OLLAMA_API_URL=http://localhost:11434/api/generate
OLLAMA_MODEL=mistral:7b
AI_ENABLED=true
```

---

## 🛠️ Installazione Manuale

### 1. Installa Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### 2. Avvia il servizio

```bash
sudo systemctl enable ollama
sudo systemctl start ollama
```

### 3. Verifica che sia attivo

```bash
sudo systemctl status ollama
```

Dovresti vedere: `Active: active (running)`

### 4. Scarica un modello

Scegli in base alla RAM disponibile:

```bash
# Raspberry Pi 4/5 con 4GB+ RAM
ollama pull mistral:7b

# Raspberry Pi 4 con 2-4GB RAM
ollama pull llama3.2:3b

# Raspberry Pi 3/Zero con 2GB RAM
ollama pull llama3.2:1b
```

### 5. Testa il modello

```bash
ollama run mistral:7b "Ciao, funzioni?"
```

---

## ⚙️ Configurazione Bot

### 1. Modifica `.env`

```bash
cd /path/to/TrackerPriceAmazon-Bot
cp .env.example .env
nano .env
```

Aggiungi/modifica:

```env
# AI Configuration
OLLAMA_API_URL=http://localhost:11434/api/generate
OLLAMA_MODEL=mistral:7b  # o llama3.2:3b o llama3.2:1b
AI_ENABLED=true
```

### 2. Installa dipendenze Python

```bash
pip install -r requirements.txt
```

### 3. Avvia il bot

```bash
python main.py
```

Nell'output dovresti vedere:

```
✅ Ollama disponibile - Modello: mistral:7b
🤖 AI Assistant abilitata
🚀 Bot avviato con successo!
```

---

## 🧪 Test AI

### Test 1: Health Check

```bash
python -c "from utils import ollama_client; ollama_client.test_ollama_sync()"
```

Output atteso: `✅ Ollama test OK`

### Test 2: Telegram

Invia al bot su Telegram:

```
Mi consigli un laptop per gaming sotto 1000€?
```

Il bot dovrebbe rispondere con consigli intelligenti!

---

## 🔧 Troubleshooting

### Problema: "Ollama NON disponibile"

**Causa**: Servizio Ollama non attivo

**Soluzione**:
```bash
sudo systemctl start ollama
sudo systemctl status ollama
```

### Problema: "Connection refused"

**Causa**: Porta 11434 bloccata/firewall

**Soluzione**:
```bash
# Verifica porta aperta
sudo netstat -tlnp | grep 11434

# Se usa firewall
sudo ufw allow 11434
```

### Problema: "Model not found"

**Causa**: Modello non scaricato

**Soluzione**:
```bash
ollama list  # Vedi modelli disponibili
ollama pull mistral:7b  # Scarica modello mancante
```

### Problema: Bot lento a rispondere

**Causa**: Modello troppo pesante per RAM disponibile

**Soluzione**: Usa modello più leggero

```bash
ollama rm mistral:7b  # Rimuovi modello pesante
ollama pull llama3.2:3b  # Scarica modello leggero
```

Poi modifica `.env`:
```env
OLLAMA_MODEL=llama3.2:3b
```

### Problema: Out of Memory (OOM)

**Causa**: RAM insufficiente

**Soluzioni**:
1. Chiudi applicazioni non necessarie
2. Aumenta swap:
   ```bash
   sudo dphys-swapfile swapoff
   sudo nano /etc/dphys-swapfile
   # Imposta: CONF_SWAPSIZE=2048
   sudo dphys-swapfile setup
   sudo dphys-swapfile swapon
   ```
3. Usa modello più leggero (llama3.2:1b)

---

## 📊 Modelli Consigliati

| Modello | RAM Richiesta | Qualità | Velocità | Raspberry Pi |
|---------|---------------|---------|----------|--------------|
| **mistral:7b** | 4GB+ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Pi 4/5 (4GB+) |
| **llama3.2:3b** | 2GB+ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Pi 4 (2-4GB) |
| **llama3.2:1b** | 1GB+ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Pi 3/Zero |

### Come scegliere?

```bash
# Controlla RAM disponibile
free -h

# Controlla dimensione modello
ollama list
```

**Regola generale**:
- Modello 7B → minimo 4GB RAM
- Modello 3B → minimo 2GB RAM
- Modello 1B → minimo 1GB RAM

---

## 🎯 Comandi Utili

```bash
# Lista modelli scaricati
ollama list

# Scarica nuovo modello
ollama pull <modello>

# Rimuovi modello
ollama rm <modello>

# Test interattivo modello
ollama run mistral:7b

# Restart servizio
sudo systemctl restart ollama

# Log servizio
sudo journalctl -u ollama -f

# Disabilita AI temporaneamente (senza disinstallare)
# In .env:
AI_ENABLED=false
```

---

## 🌐 Setup Remoto (Raspberry Pi separato)

Se vuoi Ollama su un Raspberry Pi separato dal bot:

### 1. Sul Raspberry Pi (Server Ollama)

Configura Ollama per accettare connessioni remote:

```bash
sudo nano /etc/systemd/system/ollama.service
```

Aggiungi sotto `[Service]`:
```ini
Environment="OLLAMA_HOST=0.0.0.0:11434"
```

Restart:
```bash
sudo systemctl daemon-reload
sudo systemctl restart ollama
```

### 2. Sul Server Bot

Modifica `.env`:
```env
OLLAMA_API_URL=http://IP_RASPBERRY:11434/api/generate
```

Sostituisci `IP_RASPBERRY` con l'IP del Raspberry Pi (es: `192.168.1.100`).

---

## 💡 Ottimizzazioni Prestazioni

### 1. Overclock Raspberry Pi 4/5

```bash
sudo nano /boot/config.txt
```

Aggiungi:
```ini
# Overclock (a tuo rischio!)
over_voltage=6
arm_freq=2000
```

### 2. Usa SSD invece di microSD

Ollama legge/scrive molto → SSD USB 3.0 molto più veloce!

### 3. Raffredamento

Modelli 7B generano calore → dissipatore + ventola consigliati

---

## 📚 Risorse

- [Ollama Documentation](https://github.com/ollama/ollama)
- [Lista completa modelli](https://ollama.com/library)
- [Raspberry Pi Overclocking Guide](https://www.raspberrypi.com/documentation/computers/config_txt.html#overclocking)

---

## ✅ Checklist Setup

- [ ] Raspberry Pi con OS 64-bit
- [ ] Almeno 2GB RAM disponibile
- [ ] Ollama installato
- [ ] Servizio Ollama attivo
- [ ] Modello scaricato
- [ ] `.env` configurato
- [ ] Dipendenze Python installate
- [ ] Test health check OK
- [ ] Bot avviato con AI abilitata

🎉 **Setup completato!** Il bot ora risponde con AI a richieste prodotti!
