#!/bin/bash
#
# Script di installazione Ollama su Raspberry Pi
# Per bot Telegram Amazon Affiliate + AI
#
# Requisiti:
# - Raspberry Pi 4/5 con almeno 4GB RAM (per Mistral 7B)
# - Raspberry Pi 3/Zero con almeno 2GB RAM (per LLaMA 3.2 3B)
# - OS: Raspberry Pi OS (64-bit) o Ubuntu
#

set -e

echo "🚀 ====================================="
echo "   INSTALLAZIONE OLLAMA SU RASPBERRY PI"
echo "   ====================================="
echo ""

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Funzione per stampare messaggi
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Controlla architettura
ARCH=$(uname -m)
echo "📊 Architettura rilevata: $ARCH"

if [[ "$ARCH" != "aarch64" && "$ARCH" != "arm64" ]]; then
    print_error "Architettura non supportata: $ARCH"
    print_info "Ollama richiede architettura arm64/aarch64"
    print_info "Assicurati di usare Raspberry Pi OS (64-bit)"
    exit 1
fi

# Controlla RAM disponibile
TOTAL_RAM=$(free -m | awk '/^Mem:/{print $2}')
echo "💾 RAM totale: ${TOTAL_RAM}MB"

if [ $TOTAL_RAM -lt 2048 ]; then
    print_error "RAM insufficiente: ${TOTAL_RAM}MB"
    print_info "Minimo richiesto: 2GB per modelli leggeri"
    exit 1
elif [ $TOTAL_RAM -lt 4096 ]; then
    print_info "RAM: ${TOTAL_RAM}MB - Consigliato modello leggero (llama3.2:3b o 1b)"
    RECOMMENDED_MODEL="llama3.2:3b"
else
    print_success "RAM: ${TOTAL_RAM}MB - OK per Mistral 7B"
    RECOMMENDED_MODEL="mistral:7b"
fi

echo ""

# Aggiorna sistema
print_info "Aggiornamento sistema..."
sudo apt-get update -qq

# Installa dipendenze
print_info "Installazione dipendenze..."
sudo apt-get install -y curl wget

# Scarica e installa Ollama
print_info "Download e installazione Ollama..."
curl -fsSL https://ollama.com/install.sh | sh

# Verifica installazione
if ! command -v ollama &> /dev/null; then
    print_error "Ollama non installato correttamente"
    exit 1
fi

print_success "Ollama installato con successo!"

# Avvia servizio Ollama
print_info "Avvio servizio Ollama..."
sudo systemctl enable ollama
sudo systemctl start ollama

sleep 3

# Verifica servizio
if sudo systemctl is-active --quiet ollama; then
    print_success "Servizio Ollama attivo"
else
    print_error "Servizio Ollama non attivo"
    print_info "Prova manualmente: sudo systemctl start ollama"
    exit 1
fi

echo ""
echo "📥 ====================================="
echo "   DOWNLOAD MODELLO AI"
echo "   ====================================="
echo ""

# Chiedi quale modello scaricare
echo "Scegli modello da scaricare:"
echo "1) mistral:7b (Consigliato per Pi 4/5 con 4GB+) - ~4.1GB"
echo "2) llama3.2:3b (Veloce, per Pi 4 con 2-4GB) - ~2GB"
echo "3) llama3.2:1b (Ultra-leggero, per Pi 3) - ~1.3GB"
echo "4) Salta (scarico manualmente dopo)"
echo ""

read -p "Scelta [1-4] (default: $RECOMMENDED_MODEL): " MODEL_CHOICE

case $MODEL_CHOICE in
    1)
        MODEL="mistral:7b"
        ;;
    2)
        MODEL="llama3.2:3b"
        ;;
    3)
        MODEL="llama3.2:1b"
        ;;
    4)
        print_info "Download modello saltato"
        MODEL=""
        ;;
    *)
        MODEL="$RECOMMENDED_MODEL"
        ;;
esac

if [ -n "$MODEL" ]; then
    print_info "Download modello $MODEL (potrebbe richiedere 5-15 minuti)..."
    print_info "Dimensione modello: "

    case $MODEL in
        "mistral:7b")
            echo "~4.1GB"
            ;;
        "llama3.2:3b")
            echo "~2GB"
            ;;
        "llama3.2:1b")
            echo "~1.3GB"
            ;;
    esac

    ollama pull $MODEL

    if [ $? -eq 0 ]; then
        print_success "Modello $MODEL scaricato con successo!"
    else
        print_error "Errore download modello $MODEL"
        print_info "Riprova manualmente: ollama pull $MODEL"
    fi
fi

echo ""
echo "🧪 ====================================="
echo "   TEST OLLAMA"
echo "   ====================================="
echo ""

# Test Ollama
if [ -n "$MODEL" ]; then
    print_info "Test generazione risposta..."
    TEST_RESPONSE=$(ollama run $MODEL "Rispondi solo OK se mi ricevi" --verbose=false 2>/dev/null | head -n 1)

    if [ $? -eq 0 ]; then
        print_success "Test OK! Risposta: $TEST_RESPONSE"
    else
        print_error "Test fallito"
    fi
fi

echo ""
echo "✅ ====================================="
echo "   INSTALLAZIONE COMPLETATA!"
echo "   ====================================="
echo ""

# Stampa configurazione .env
echo "📝 Configurazione per .env:"
echo ""
echo "OLLAMA_API_URL=http://localhost:11434/api/generate"
echo "OLLAMA_MODEL=$MODEL"
echo "AI_ENABLED=true"
echo ""

print_info "Copia queste variabili nel file .env del bot"
print_info ""
print_success "Ollama è ora attivo e pronto!"
print_info "URL API: http://localhost:11434"
print_info "Modello: $MODEL"
print_info ""
print_info "Comandi utili:"
echo "  - Lista modelli:     ollama list"
echo "  - Scarica modello:   ollama pull <modello>"
echo "  - Rimuovi modello:   ollama rm <modello>"
echo "  - Test manuale:      ollama run $MODEL"
echo "  - Status servizio:   sudo systemctl status ollama"
echo "  - Restart servizio:  sudo systemctl restart ollama"
echo ""

print_success "Setup completato! 🎉"
print_info "Ora avvia il bot con: python main.py"
