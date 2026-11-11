# Asynchronous Ozon Marketplace Scraper & Telegram Bot

A high-performance, asynchronous web scraper and price monitoring system for **Ozon.ru** built with Python. This project demonstrates a decoupled Producer-Consumer architecture using Redis queues, asynchronous SQLite storage, Playwright browser automation, and a Telegram bot interface.

---

## Key Features

* **Decoupled Producer-Consumer Architecture**: Separates task dispatching (Telegram Bot), browser scraping (`main.py`), and database persistence (`consumer.py`) via asynchronous **Redis** queues.
* **Advanced Anti-Bot Bypass**: Utilizes `Playwright` with disabled automation flags (`AutomationControlled`), custom user-agent/viewport fingerprints, optional proxy support, and randomized human-like delays (`_human_delay`).
* **100% Asynchronous Engine**: Built on `asyncio`, `playwright.async_api`, `redis.asyncio`, `aiosqlite`, and `aiogram 3` for non-blocking concurrent execution.
* **Persistent SQLite Storage**: Automatically initializes and updates product records (title, sanitized price, unique URL, and timestamps) with fast lowest-price search queries.
* **Telegram Bot Control**: Allows users to submit search queries directly from Telegram and retrieve sorted product listings via `/find`.
* **Process Orchestration**: Includes `start_pars.py` to launch and gracefully manage background worker processes with a single command.

---

## Tech Stack & Tools

* **Core**: Python 3.12+
* **Automation & Scraping**: Playwright (Chromium Async API)
* **Message Broker & Queues**: Redis (`redis.asyncio`)
* **Database**: SQLite (`aiosqlite`)
* **Telegram Interface**: Aiogram 3 (`aiohttp` proxy support)
* **Configuration & Logging**: `python-dotenv`, standard Python `logging`

---

## Project Architecture

The repository follows a modular Producer-Consumer layout, isolating browser automation, queue management, database persistence, and user interaction:

```text
OzonParseRuslBot/
├── .env                    # Environment variables (Tokens, Redis, Proxy)
├── .gitignore              # Git ignore rules (venv, database.db, cache)
├── requirements.txt        # Project dependencies
├── README.md               # Project documentation
├── start_pars.py           # Process orchestrator for background workers
├── tg_bot.py               # Telegram bot interface (Aiogram 3)
└── src/
    ├── __init__.py
    ├── config.py           # Configuration loader and constants
    ├── browser_manager.py  # Playwright browser & context lifecycle manager
    ├── network_utils.py    # Safe navigation with retries and random delays
    ├── parser.py           # Ozon DOM scraping and card extraction logic
    ├── queue_manager.py    # Async Redis FIFO queues (tasks & products)
    ├── database.py         # Async SQLite schema and CRUD operations
    ├── consumer.py         # Background worker saving queued items to SQLite
    └── main.py             # Scraper worker listening to search tasks
```

---

## Getting Started

### 1. Prerequisites
* **Python 3.12+**
* **Redis Server** running locally (default `localhost:6379`) or remotely.

### 2. Installation
Clone the repository, create a virtual environment, and install dependencies:

```bash
git clone <your-repository-url>
cd OzonParseRuslBot
python -m venv venv

# Windows:
.\venv\Scripts\Activate.ps1
# Linux / macOS:
source venv/bin/activate

pip install -r requirements.txt
playwright install chromium
```

### 3. Configuration
Create a `.env` file in the project root and configure your environment variables:

```env
REDIS_HOST=localhost
REDIS_PORT=6379
BOT_TOKEN=your_telegram_bot_token
PROXY_SERVER=http://user:pass@host:port
```

### 4. Running the Project
* **Start the scraper worker and database consumer together:**
  ```bash
  python start_pars.py
  ```
* **Start the Telegram bot interface (in a separate terminal):**
  ```bash
  python tg_bot.py
  ```

---

## Telegram Bot Commands

* `/start` — Display welcome message and usage instructions.
* `<any product name>` — Dispatch a new scraping task to the Redis queue (e.g., `ноутбук`).
* `/find <product name>` — Retrieve up to 10 stored products from SQLite sorted by lowest price.

---

## Disclaimer
