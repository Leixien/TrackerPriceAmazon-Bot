"""
Client per comunicazione con Ollama (AI locale)
Gestisce richieste al modello LLaMA/Mistral per consigli prodotti
"""
import logging
import asyncio
import aiohttp
import config

logger = logging.getLogger(__name__)


async def generate_product_advice(user_query, user_id=None):
    """
    Genera consigli prodotti usando Ollama

    Args:
        user_query (str): Richiesta dell'utente
        user_id (int): ID utente Telegram (opzionale)

    Returns:
        str: Risposta generata dall'AI o None se errore
    """
    try:
        # Costruisci prompt ottimizzato per consigli prodotti
        system_prompt = """Sei un esperto consulente di prodotti Amazon specializzato nel mercato italiano.

Il tuo compito è:
1. Analizzare la richiesta dell'utente
2. Fornire 2-3 consigli di prodotti specifici disponibili su Amazon.it
3. Spiegare brevemente pro/contro di ogni prodotto
4. Considerare il budget se menzionato
5. Essere conciso e diretto (max 300 parole)

Formato risposta:
🎯 **Ecco i miei consigli:**

**1. [Nome Prodotto]**
- Prezzo orientativo: ~XXX€
- ✅ Pro: [breve]
- ⚠️ Contro: [breve]

**2. [Nome Prodotto]**
[stesso formato]

💡 **Il mio consiglio**: [quale scegliere e perché]

IMPORTANTE:
- NON inventare link Amazon
- Se non conosci prodotti specifici, descrivi caratteristiche da cercare
- Usa il tono friendly ma professionale
- Scrivi in italiano
"""

        user_prompt = f"Richiesta utente: {user_query}"

        # Payload per Ollama API
        payload = {
            "model": config.OLLAMA_MODEL,
            "prompt": f"{system_prompt}\n\n{user_prompt}",
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 500
            }
        }

        # Chiama Ollama API
        async with aiohttp.ClientSession() as session:
            async with session.post(
                config.OLLAMA_API_URL,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    ai_response = result.get('response', '').strip()

                    if ai_response:
                        logger.info(f"Risposta AI generata per user {user_id}: {len(ai_response)} chars")
                        return ai_response
                    else:
                        logger.error("Risposta AI vuota")
                        return None
                else:
                    error_text = await response.text()
                    logger.error(f"Errore Ollama API ({response.status}): {error_text}")
                    return None

    except asyncio.TimeoutError:
        logger.error("Timeout chiamata Ollama API (>30s)")
        return None
    except aiohttp.ClientError as e:
        logger.error(f"Errore connessione Ollama: {e}")
        return None
    except Exception as e:
        logger.error(f"Errore inaspettato Ollama: {e}")
        return None


async def check_ollama_health():
    """
    Verifica che Ollama sia disponibile

    Returns:
        bool: True se Ollama risponde, False altrimenti
    """
    try:
        async with aiohttp.ClientSession() as session:
            # Endpoint health check Ollama
            health_url = config.OLLAMA_API_URL.replace('/api/generate', '/api/tags')
            async with session.get(health_url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status == 200:
                    logger.info("Ollama health check: OK")
                    return True
                else:
                    logger.warning(f"Ollama health check failed: {response.status}")
                    return False
    except Exception as e:
        logger.error(f"Ollama non disponibile: {e}")
        return False


async def list_available_models():
    """
    Lista modelli disponibili su Ollama

    Returns:
        list: Lista nomi modelli o [] se errore
    """
    try:
        async with aiohttp.ClientSession() as session:
            tags_url = config.OLLAMA_API_URL.replace('/api/generate', '/api/tags')
            async with session.get(tags_url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status == 200:
                    result = await response.json()
                    models = [model['name'] for model in result.get('models', [])]
                    logger.info(f"Modelli Ollama disponibili: {models}")
                    return models
                else:
                    logger.error(f"Errore lista modelli Ollama: {response.status}")
                    return []
    except Exception as e:
        logger.error(f"Errore recupero modelli Ollama: {e}")
        return []


def test_ollama_sync():
    """
    Test sincrono per verificare Ollama (per debug)
    """
    import requests

    try:
        response = requests.post(
            config.OLLAMA_API_URL,
            json={
                "model": config.OLLAMA_MODEL,
                "prompt": "Rispondi solo 'OK' se mi ricevi",
                "stream": False
            },
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Ollama test OK: {result.get('response', '')[:50]}")
            return True
        else:
            print(f"❌ Ollama test FAIL: status {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Ollama test ERROR: {e}")
        return False


# Test rapido all'import (opzionale)
if __name__ == "__main__":
    print("Testing Ollama connection...")
    test_ollama_sync()
