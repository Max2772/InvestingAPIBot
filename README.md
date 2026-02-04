<img src="assets/icon.png" alt="SkinsRadar Logo" width="150"/>

# @InvestingAPIBot 🤖

[![Python Version](https://img.shields.io/badge/python-3.11--3.13-blue)](https://www.python.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Telegram](https://img.shields.io/badge/telegram-@InvestingAPIBot-blue)](https://t.me/InvestingAPIBot)
[![Docker](https://img.shields.io/badge/docker-supported-blue)](https://www.docker.com)


[@InvestingAPIBot](https://t.me/InvestingAPIBot) is a Telegram bot built with `aiogram` that allows you to manage and track your investment portfolio 📊 in real-time. It integrates with [InvestAPI](https://github.com/Max2772/InvestAPI) to fetch prices for stocks, ETFs, cryptocurrencies, and Steam items. The bot consolidates data from multiple asset types into one convenient interface, eliminating the need to check prices across multiple apps or websites.

**Key Features:**
- 📈 Track stocks, crypto, and Steam items in a single portfolio.
- 🔔 Set price alerts (up to 10 per user).
- 📜 View full purchase/removal history.
- 💻 Reliable cached prices from InvestAPI.
- 🚀 Docker-based production setup with PostgreSQL.

The bot is live and public: [@InvestingAPIBot](https://t.me/InvestingAPIBot).  
Development uses SQLite; production uses PostgreSQL (via Docker).


## Installation 🛠️

### Requirements
- Python 3.11 (recommended)
- Running [InvestAPI](https://github.com/Max2772/InvestAPI) (default: `http://127.0.0.1:8000`)
- Docker + docker-compose (for production PostgreSQL)
- Telegram Bot Token from [@BotFather](https://t.me/BotFather)


### Local Development
1. Clone the repository:
   ```bash
   git clone https://github.com/Max2772/InvestingAPIBot.git
   cd InvestingAPIBot
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements/dev/requirements.txt
   ```

3. Create `.env` in the project root:
   ```env
   LOG_LEVEL=INFO
   BOT_TOKEN=your_telegram_bot_token
   API_BASE_URL=http://127.0.0.1:8000
   DATABASE_URL=sqlite:///InvestingAPIBot.db
   ASYNC_DATABASE_URL=sqlite+aiosqlite:///InvestingAPIBot.db
   MAXIMUM_ALERTS=10
   ALERT_INTERVAL_SECONDS=300
   ```

4. Run the bot:
   ```bash
   python main.py
   ```

### Production (Docker)
1. Make sure InvestAPI is running and accessible via `API_BASE_URL`.

2. Create `.env` in the project root (update `DATABASE_URL` for PostgreSQL):
   ```env
   LOG_LEVEL=INFO
   BOT_TOKEN=your_telegram_bot_token
   API_BASE_URL=http://127.0.0.1:8000
   DATABASE_URL=postgresql://postgres:your_password@database:5432/investingapibot
   ASYNC_DATABASE_URL=postgresql+asyncpg://postgres:your_password@database:5432/investingapibot
   MAXIMUM_ALERTS=10
   ALERT_INTERVAL_SECONDS=300
   ```

   **Note:** `database` is the compose service name. Set a secure password in `.env`.

3. Start the stack:
   ```bash
   docker compose up --build -d
   ```

   The bot will be available in Telegram.

### Dockerfile (production)
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements/prod/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

CMD ["python", "main.py"]
```

### docker-compose.yaml (production)
```yaml
services:
  api:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    container_name: investingapibot
    env_file:
      - ../.env
    depends_on:
      - database
    restart: unless-stopped

  database:
    image: postgres:17-alpine
    container_name: investingapibot_database
    volumes:
      - investingapibot_db_data:/var/lib/postgresql/data
    env_file:
      - ../.env
    ports:
      - "127.0.0.1:5432:5432"

volumes:
  investingapibot_db_data:
```

## Usage 📝

Interact with the bot directly in Telegram at [@InvestingAPIBot](https://t.me/InvestingAPIBot).  

Start with `/start` to open the main menu (with quick portfolio overview via buttons) or `/help` to see the full list of commands.

All commands now use a unified format with `asset_type` (`stock`, `crypto`, or `steam`). For Steam items, include `app_id` (e.g., `730` for CS2).

### Key Commands

- **/check** `<asset_type>` [`<app_id>`] `<asset_name>`  
  Get the current price of any asset.  
  Examples:  
  ```
  /check stock AMD
  /check crypto BTC
  /check steam 730 Glove Case
  ```
  Sample responses:  
  ```
  Stock AMD: $202.05
  ```
  ```
  Crypto BTC: $73359.0
  ```
  ```
  Steam Glove Case: $20.85
  ```

- **/add** `<asset_type>` [`<app_id>`] `<asset_name>` `<quantity>` [-p `<price>`]  
  Add an asset to your portfolio. Use optional `-p <price>` to set your custom purchase price (otherwise uses current market price).  
  Examples:  
  ```
  /add stock AMD 2 -p 170.50
  /add crypto SOLANA 15
  /add steam 730 Glove Case 10 -p 2.15
  /add crypto BTC 0.05 -p 76969.69
  /add steam 730 Operation Bravo Case 10
  ```
  Sample responses:  
  ```
  Added 2 AMD at 170.50$
  ```
  ```
  Added 15 SOLANA at 92.35$
  ```
  ```
  Added 10 Glove Case at 2.15$
  ```

- **/remove** `<asset_type>` [`<app_id>`] `<asset_name>` [`<quantity>`]  
  Remove an asset (or a specific quantity) from your portfolio. If no quantity is given, removes all.  
  Examples:  
  ```
  /remove stock AMD 2
  /remove crypto BTC
  /remove steam 730 Glove Case 10
  ```
  Sample responses:  
  ```
  Removed 2 AMD from portfolio.
  ```
  ```
  Removed BTC from portfolio.
  ```
  ```
  Removed 10 Glove Case from portfolio.
  ```

- **/portfolio** [`all|stock|crypto|steam`]  
  View your portfolio (filtered by type or all). Shows quantity, average buy price, current price, value, and profit/loss % per asset, plus total value and overall growth.  
  Example:  
  ```
  /portfolio all
  ```
  Sample response:
  ```
  📊 Your Portfolio
  💹 Stocks
  TSLA: 1.00 at avg. price $350.25, now $405.99, value $405.99 (+15.91% 📈)
  NVDA: 3.00 at avg. price $142.10, now $174.00, value $522.00 (+22.45% 📈)
  ⚡ Crypto
  ETH: 0.7000000 at avg. price $3200.00, now $2112.49, value $1478.74 (-33.98% 📉)
  SOLANA: 15.0000000 at avg. price $92.35, now $91.81, value $1377.15 (-0.58% 📉)
  🕹️ Steam Items
  Danger Zone Case: 7.00 at avg. price $2.00, now $2.00, value $14.00 (0.00%)
  Operation Bravo Case: 10.00 at avg. price $65.82, now $65.82, value $658.20 (0.00%)
  ◇───────────────────────────────────────────◇
  💰 Total value: $4456.08
  📊 Total growth: -12.18% 📉
  ```

- **/set_alert** `<asset_type>` [`<app_id>`] `<asset_name>` `<condition>` `<price>`  
  Set a price alert (conditions: `>`, `>=`, `<`, `<=`). Alerts trigger notifications when met.  
  Example:  
  ```
  /set_alert stock AMD > 200
  ```
  Sample response:  
  ```
  🔔 Alert created for AMD (stock) with target > $200.00.
  ```

- **/alerts**  
  List all your active alerts with IDs.  
  Sample response:  
  ```
  📢 Your Alerts
  #3: BTC, target >= $100000.00
  #4: ETH, target <= $2000.00
  #6: AMD, target > $200.00
  ```

- **/delete_alert** `<id>`  
  Delete an alert by its ID (from `/alerts`).  
  Example: `/delete_alert 6`


When an alert triggers, you'll get a notification like:
```
🔔 Alert Triggered!
Asset: AMD
Current price: $202.05
Target: > $200.00
```

- **/history** [`all|stock|crypto|steam`]  
  View the full log of additions and removals.  
  Example:  
  ```
  /history all
  ```
  Sample response:
  ```
  📜 Portfolio History
  Added 2.00 TSLA at 26-02-04 15:35:52
  Added 3.00 NVDA at 26-02-04 15:35:59
  Added 1.20 ETH at 26-02-04 15:36:05
  Added 2.00 AK-47 | Redline at 26-02-04 15:36:08
  Added 10.00 Danger Zone Case at 26-02-04 15:36:17
  Removed 5.00 AAPL at 26-02-04 15:50:37
  Removed 1.00 TSLA at 26-02-04 15:50:40
  Removed 0.50 ETH at 26-02-04 15:50:44
  Removed 3.00 Danger Zone Case at 26-02-04 15:50:47
  Removed 5.00 Glove Case at 26-02-04 15:50:49
  Added 15.00 SOLANA at 26-02-04 16:13:43
  Added 10.00 Operation Bravo Case at 26-02-04 16:41:44
  Removed 2.00 AMD at 26-02-04 16:42:03
  Removed 0.10 BTC at 26-02-04 16:42:14
  Removed 10.00 Glove Case at 26-02-04 16:42:29
  ```

This unified command system makes the bot simpler and more flexible—everything works the same way across stocks, crypto, and Steam items! 🚀

### Example Portfolio (/portfolio all)
<img src="assets/bot_example.png" alt="Portfolio Command Example" width="600"/>

Shows quantity, average buy price, current price, value, profit/loss %, total portfolio value and growth.

## Limitations
- Maximum 10 alerts per user (`MAXIMUM_ALERTS`).
- Alerts checked every 300 seconds (`ALERT_INTERVAL_SECONDS`).
- No hard limit on portfolio size (high-precision `Numeric` type in DB).

## Dependencies & Architecture 🏗️

### Production Dependencies
- `python-dotenv`
- `aiogram`
- `sqlalchemy`
- `psycopg2-binary`
- `asyncpg`

(Development adds `aiosqlite` instead of psycopg2/asyncpg.)

### Architecture
The bot uses `aiogram` for async Telegram handling. It fetches prices from InvestAPI and stores user data in the database:
- `users` — registered users
- `portfolios` — assets, quantities, buy prices
- `alerts` — price alerts
- `history` — all additions/removals

## License 📜 

This project is licensed under the MIT License. See the [License](LICENSE) file for details.

## Contact 📫

- GitHub: [@Max2772](https://github.com/Max2772)
- Email: [bib.maxim@gmail.com](mailto:bib.maxim@gmail.com)