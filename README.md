# Asynchronous Ozon Marketplace Scraper

A high-performance, professional-grade asynchronous web scraper for **Ozon.ru** built with Python 3.14. This project demonstrates clean architecture, advanced anti-bot bypass techniques, robust data validation, and modern async programming practices. It is designed to extract comprehensive product data efficiently without triggering automated ban mechanisms.
---

## 🚀 Key Features

* **Advanced Anti-Bot Bypass**: Utilizes `Playwright` with disabled automation flags (`AutomationControlled`) and custom browser context configurations to gracefully mimic real human behavior and bypass strict marketplace anti-scraping security.
* **100% Asynchronous Engine**: Built entirely on top of Python's `asyncio` and аsync Playwright API, enabling concurrent data processing with minimal CPU/RAM utilization.
* **Robust Data Validation**: Integrates `Pydantic v2` schemas to guarantee data integrity. "Dirty" raw string inputs from web pages (e.g., `"74 990 ₽"`) are automatically sanitized, validated, and cast into clean data types (integers, strict strings) before passing further.
* **Human-like Behavior Emulation**: Implements chaotic, randomized delays (`_human_delay`) between navigation actions to minimize the risk of IP bans.
* **Enterprise Logging Layout**: Implements comprehensive production-ready logging tracking every phase of the scraping cycle (DOM discovery, extraction ratios, and graceful session termination).

---

## 🛠️ Tech Stack & Tools

* **Core**: Python 3.14+ (Fully compatible via modern standard ABI)
* **Automation & Engine**: Playwright (Chromium Async API)
* **Data Validation Layer**: Pydantic v2
* **Configuration**: Python-dotenv (Strict `.env` environment encapsulation)
* **Logging & Monitoring**: Standard Python `logging` library
---

## 📁 Project Architecture

The repository adheres to the **Layered Clean Architecture** pattern, strictly separating configuration, automation layers, and validation boundaries:

```text
ozon_parser/
│
├── .env                  # Confidentials & Environment flags (Headless, Proxy)
├── .gitignore            # Deployment and cache exclusions
├── requirements.txt      # Strictly pinned dependencies for Python 3.14
├── README.md             # Project documentation (You are here)
│
└── src/
    ├── config.py         # Configuration Layer (Parses system environment)
    ├── browser.py        # Automation Layer (Manages Playwright lifecycles & fingerprints)
    ├── models.py         # Validation Layer (Pydantic schemas & custom sanitizers)
    ├── parser.py         # Business Logic Layer (DOM orchestration & selector targeting)
    └── main.py           # Application Entry Point & Orchestrator
```
---

## ⚙️ Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com
   cd ozon_parser
   ```

2. **Configure your Virtual Environment**:
   ```bash
   python -m venv venv
   # On Windows (PowerShell):
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   *Note: For Python 3.14 stability, set the PyO3 ABI forward compatibility flag before compiling native dependencies:*
   ```bash
   # Windows (PowerShell):
   $env:PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1
   
   # Run the installation:
   pip install -r requirements.txt
   playwright install chromium
   ```

4. **Setup Environment Variables**:
   Create a `.env` file in the root folder:
   ```text
   HEADLESS=False
   PROXY_SERVER=""
   ```
---

## 💻 Usage

To launch the asynchronous engine and run a search queries pipeline, execute the main package module from the project root:

```bash
python -m src.main
```
### Expected Output Logs Structure:
```text
2026-10-20 18:36:07 [INFO] root: Starting Ozon Scraper Application...
2026-10-20 18:36:07 [INFO] browser: Initializing Playwright browser client...
2026-10-20 18:36:09 [INFO] parser: Navigating to search page for query: 'ноутбук'
2026-10-20 18:36:15 [INFO] parser: DOM processing: Found 24 product containers.
2026-10-20 18:36:15 [INFO] parser: [1/24] Validated: Lenovo V15 Gen 5... | Price: 74990 (int)
2026-10-20 18:36:15 [INFO] parser: [2/24] Validated: Digma Pro Cursus... | Price: 40570 (int)
...
2026-10-20 18:36:16 [INFO] browser: Closing browser sessions...
2026-10-20 18:36:17 [INFO] root: Application finished successfully.
```
---

## 🔒 License & Disclaimer

This project is developed for educational purposes, portfolio demonstration, and architectural evaluation. Please review the target marketplace terms of service before deploying web automation tools at scale.