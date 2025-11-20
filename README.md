# TrackerPriceAmazon-Bot
A simple Amazon price tracking bot written in Python by <a href = 'https://github.com/Leixien'>Leixien</a>

# Description of the Code

<b><i>Brief description of the code</i><b></br>

This Telegram Bot checks the price of a given Amazon Product.
  - You can save the product and check the price when you want with a single tap.
  - You can check the prices of different amazon store states by sending the link of the product itself
  - **NEW!** 🔗 Automatic Amazon affiliate link conversion
  - **NEW!** 📊 Track your conversion statistics
  - **NEW!** 🔔 Daily reminders at 11:00 and 16:00 (Italy time)
  - **NEW!** 🤖 AI-powered product advisor (Ollama local AI)
  - **NEW!** 🗄️ Optional Supabase database for analytics
  - Join my <a href = 'https://discord.gg/kTg5fhVERQv' >discord</a> :)
  - Find a new song (try it <3 )
                             
The modules I used are:

  - <a href = 'https://www.crummy.com/software/BeautifulSoup/bs4/doc/' >BeautifulSoup (BS4)</a> - to scrap Amazon website
  - <a href = 'https://python-telegram-bot.org/'>Telegram API</a> - for Bot API

# Bot Code
I created 3 files to make the code <a href = 'https://www.martinfowler.com/bliki/CodeAsDocumentation.html#:~:text=I%20think%20part,began%20to%20program.'>clear</a> and <a href = 'https://www.martinfowler.com/bliki/CodeAsDocumentation.html#:~:text=I%20think%20part,began%20to%20program.'>readable</a>!

In the files You will find:
  - <a href = 'https://github.com/Leixien/TrackerPriceAmazon-Bot/blob/main/main.py'> main.py</a> - Main code whit Telegram API
  - <a href = 'https://github.com/Leixien/TrackerPriceAmazon-Bot/blob/main/myFunctions.py'>myFunctions.py</a> - Functions implements for manipulate the data and 
  - <a href = 'https://github.com/Leixien/TrackerPriceAmazon-Bot/blob/main/scraper.py'>scraper.py</a> - Scraper Amazon site with BeautifulSoup

# 🔗 Affiliate Link Conversion Features

## Automatic Conversion
Simply send any Amazon.it link to the bot and it will automatically reply with the affiliate version!

**Supported formats:**
- `https://www.amazon.it/dp/B08N5WRWNW/`
- `https://www.amazon.it/product-name/dp/B08N5WRWNW/`
- `https://amazon.it/gp/product/B08N5WRWNW`
- `https://amzn.eu/d/XXXXX` (short links)

## Commands

### `/convertlink <url>`
Manually convert an Amazon link to affiliate link.

**Example:**
```
/convertlink https://www.amazon.it/dp/B08N5WRWNW/
```

### `/stats`
View your conversion statistics (today and total).

### `/stop`
Disable daily reminders.

### `/start`
Re-enable daily reminders.

## Daily Reminders
The bot sends automatic reminders at **11:00** and **16:00** (Italy time) to all subscribed users!

# 🤖 AI Product Advisor

## Features
The bot includes an **intelligent AI assistant** powered by Ollama (local AI on Raspberry Pi):

- 💡 **Smart product recommendations** based on your requests
- 🔍 **Product comparisons** (e.g., "iPhone 15 vs Samsung S24")
- 💰 **Budget-based suggestions** (e.g., "laptop gaming under 1000€")
- 🎯 **Personalized advice** tailored to your needs
- 🔒 **100% FREE** - runs locally on Raspberry Pi, no API costs!

## How it Works

Simply ask the bot for product advice in natural language:

**Examples:**
```
"Mi consigli un laptop per gaming sotto 1000€?"
"Quale è il miglior smartphone con fotocamera?"
"Confronta iPhone 15 vs Samsung S24"
"Ho bisogno di cuffie wireless per correre"
"Cerco una friggitrice ad aria buona"
```

The bot will:
1. 🧠 Analyze your request with AI
2. 💡 Generate personalized recommendations
3. 🔗 Provide affiliate Amazon links automatically

### `/aihelp`
Show detailed AI assistant help and examples.

## Setup AI (Raspberry Pi)

The AI runs locally on Raspberry Pi using **Ollama** (free, open-source).

### Quick Start

```bash
# On Raspberry Pi
chmod +x scripts/setup_raspberry_ollama.sh
./scripts/setup_raspberry_ollama.sh
```

The script will:
- ✅ Install Ollama
- ✅ Download AI model (Mistral 7B / LLaMA 3.2)
- ✅ Configure the service
- ✅ Test the installation

**Full guide:** See [docs/SETUP_AI.md](docs/SETUP_AI.md)

### Requirements

- Raspberry Pi 4/5 with 4GB RAM (for Mistral 7B)
- Raspberry Pi 4 with 2GB RAM (for LLaMA 3.2 3B)
- Raspberry Pi 3 with 2GB RAM (for LLaMA 3.2 1B)
- Raspberry Pi OS (64-bit)

### AI Disabled by Default?

No problem! The bot works perfectly even without AI. Simply set in `.env`:

```env
AI_ENABLED=false
```

## Installation & Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure environment
Create a `.env` file from the template:
```bash
cp .env.example .env
```

Edit `.env` and add your bot token:
```
BOT_TOKEN=your_telegram_bot_token_here
```

### 3. Configure affiliate tag
Edit `config.py` and set your Amazon affiliate tag:
```python
AFFILIATE_TAG = "your-tag-21"
```

### 4. Run the bot
```bash
python main.py
```

## Project Structure
```
TrackerPriceAmazon-Bot/
├── main.py                      # Main bot with command handlers
├── scraper.py                   # Amazon scraper for prices
├── myFunctions.py               # Utility functions
├── config.py                    # Configuration (affiliate tag, timezones, AI, etc.)
│
├── handlers/
│   ├── amazon_affiliate.py      # Affiliate link conversion logic
│   └── ai_assistant.py          # AI product advisor (NEW)
│
├── utils/
│   ├── user_manager.py          # User tracking for reminders
│   ├── scheduler.py             # Daily reminder scheduler
│   ├── ollama_client.py         # Ollama AI client (NEW)
│   └── supabase_manager.py      # Supabase database (NEW, optional)
│
├── data/
│   ├── users.json               # User database for broadcast
│   └── stats.json               # Conversion statistics
│
├── docs/
│   ├── SETUP_AI.md              # AI setup guide (NEW)
│   └── SETUP_SUPABASE.md        # Supabase setup guide (NEW)
│
└── scripts/
    └── setup_raspberry_ollama.sh  # Ollama auto-install script (NEW)
```

# Next Upgrade
I will try to add some new features every month to make this bot useful
Some features I will improve in the next month:
  - ✅ ~~Schedulable Messages for price alert~~ (DONE - Daily reminders implemented!)
  - ✅ ~~AI-powered product recommendations~~ (DONE - Ollama AI integrated!)
  - Amazon Product API integration for real product search
  - A graphic with the price of the product
  - Inline mode for SuperGroups
  - Price drop notifications
  - Multi-language support (EN/IT/ES)
