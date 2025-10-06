<img src="assets/icon.png" alt="SkinsRadar Logo" width="150"/>

# @InvestingAPIBot 🤖

Telegram bot for tracking your investments in stocks, crypto, and Steam items using InvestAPI.


[![Python Version](https://img.shields.io/badge/python-3.11--3.13-blue)](https://www.python.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Telegram](https://img.shields.io/badge/telegram-@InvestingAPIBot-blue)](https://t.me/InvestingAPIBot)

## Description

[@InvestingAPIBot](https://t.me/InvestingAPIBot) is a Telegram bot built with `aiogram` that allows you to manage and track your investment portfolio 📊 in real-time. It integrates with [InvestAPI](https://github.com/Max2772/InvestAPI) to fetch prices for stocks, ETFs, cryptocurrencies, and Steam items. The bot consolidates data from multiple asset types into one convenient interface, eliminating the need to check prices across multiple apps or websites.

**Key Features:**
- 📈 Track stocks, cryptocurrencies, and Steam items in a single portfolio.
- 🔔 Set price alerts for assets (up to 10 per user).
- 📜 View purchase history and portfolio performance.
- 💻 Powered by InvestAPI for reliable, cached price data.
- 🚀 Throttling to prevent spam and ensure smooth operation.

The bot is live and publicly available at [@InvestingAPIBot](https://t.me/InvestingAPIBot). It uses SQLite for local development and PostgreSQL (via Docker) for production to store portfolio and alert data.

## Installation 🛠️

### Requirements
- Python 3.11–3.13 (3.11 recommended for optimal dependency compatibility).
- [InvestAPI](https://github.com/Max2772/InvestAPI) running locally or on a server (default: `http://127.0.0.1:8000`).
- Docker (for production PostgreSQL database and optional Redis).
- Redis (for throttling middleware; can reuse InvestAPI’s Redis container).
- Telegram Bot Token (obtained via [@BotFather](https://t.me/BotFather)).

### Installation Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/Max2772/InvestingAPIBot.git
   cd InvestingAPIBot
   ```
2. Install dependencies (choose `dev` or `prod`):
   ```bash
   pip install -r requirements/dev/requirements.txt  # For local development
   # or
   pip install -r requirements/prod/requirements.txt  # For production
   ```
3. Set up environment variables (see [Configuration](#configuration)).


4. For production, deploy the PostgreSQL database (and optional Redis):
   ```bash
   cd docker
   docker compose up --build -d
   ```
5. Run the bot:
   ```bash
   python main.py
   ```

### Running as a Systemd Service (Production)
To run the bot as a service on a Linux server (e.g., Ubuntu):
1. Create `/etc/systemd/system/investingapibot.service` with the following content:

   ```ini
   [Unit]
   Description=Telegram Bot for InvestAPI
   After=network.target

   [Service]
   User=investingapibot
   WorkingDirectory=/home/investingapibot/projects/InvestingAPIBot
   ExecStart=/home/investingapibot/.pyenv/versions/InvestingAPIBot-3.11/bin/python /home/investingapibot/projects/InvestingAPIBot/main.py
   Restart=always
   RestartSec=10
   EnvironmentFile=/etc/investingapibot.conf

   [Install]
   WantedBy=multi-user.target
   ```
   **Note**: Adjust `User`, `WorkingDirectory`, and `ExecStart` paths to match your server setup. The `.service` file is not included in the repository, so copy it from this README.

2. Create `/etc/investingapibot.conf` (see [Configuration](#configuration)).

3. Enable and start the service:
   ```bash
   sudo systemctl enable investingapibot
   sudo systemctl start investingapibot
   ```

<h2 id="configuration">Configuration ⚙️</h2>

Create environment files in the project root for local development (`.env` and `.env.dev`) or `/etc/investingapibot.conf` for production. The bot can reuse the Redis container from InvestAPI (on `redis://127.0.0.1:6379`), but for standalone deployment, consider adding a Redis service to `docker-compose.yaml`.

### Local Development
- **`.env`**:
  ```env
  TELEGRAM_BOT_TOKEN=your_telegram_bot_token
  ADMIN_ID=your_telegram_user_id
  REDIS_URL=redis://127.0.0.1:6379
  API_BASE_URL=http://127.0.0.1:8000
  ```
- **`.env.dev`**:
  ```env
  INVESTINGAPIBOT_DATABASE_URL=sqlite:///InvestingAPIBot.db
  INVESTINGAPIBOT_ASYNC_DATABASE_URL=sqlite+aiosqlite:///InvestingAPIBot.db
  ```

### Production (`/etc/investingapibot.conf`)
```env
PYTHONUNBUFFERED=1
INVESTINGAPIBOT_DATABASE_URL=postgresql://USER:PASSWORD@127.0.0.1:5432/investingapibot
INVESTINGAPIBOT_ASYNC_DATABASE_URL=postgresql+asyncpg://USER:PASSWORD@127.0.0.1:5432/investingapibot
```

- **`.env`**:
  ```env
  TELEGRAM_BOT_TOKEN=your_telegram_bot_token
  ADMIN_ID=your_telegram_user_id
  REDIS_URL=redis://127.0.0.1:6379
  API_BASE_URL=http://127.0.0.1:8000
  ```

**Note**: Replace `USER` and `PASSWORD` with your PostgreSQL credentials. File `.conf` is not included in the repository, so copy it from this README.

Additional settings can be adjusted in `config.py`:
```python
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_BASE_URL = os.getenv("API_BASE_URL","http://127.0.0.1:8000")
REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379")
ADMIN_ID = os.getenv("ADMIN_ID")
THROTTLE_FIRST_LIMIT = 2  # Warning after 2 seconds of rapid messages
THROTTLE_SECOND_LIMIT = 5  # Ignore after 5 seconds of rapid messages
MAXIMUM_ALERTS = 10  # Max alerts per user
ALERT_INTERVAL_SECONDS = 300  # Check alerts every 5 minutes
```

### Docker Configuration
For production, use the following `docker-compose.yaml` to set up PostgreSQL and an optional Redis container:
```yaml
services:
  database:
    image: postgres:17
    container_name: investingapibot_database
    volumes:
      - /var/lib/postgresql/data:/var/lib/postgresql/data
    env_file:
      - database.env
    ports:
      - "127.0.0.1:5432:5432"
  redis:
    image: redis
    container_name: investingapibot_redis
    ports:
      - "127.0.0.1:6379:6379"
```
**Note**: If running InvestAPI on the same machine, you can reuse its Redis container (`redis://127.0.0.1:6379`) instead of adding a separate one.

## Usage 📝

<!-- Add screenshot here: <img src="assets/screenshot-portfolio.png" alt="Portfolio Command Example" width="400"/> -->

Interact with the bot via Telegram at [@InvestingAPIBot](https://t.me/InvestingAPIBot). Start with `/start` or `/register` to set up your portfolio.

### Key Commands
- `/check_stock <ticker>`: Get current stock price.
  - Example: `/check_stock AMD`
  - Response: `Stock ticker AMD: $206.58`
- `/check_crypto <coin>`: Get current cryptocurrency price.
  - Example: `/check_crypto BTC`
  - Response: `Coin BTC: $125953.0`
- `/check_steam <app_id> <market_name>`: Get Steam item price.
  - Example: `/check_steam 730 Glove Case`
  - Response:
    ```
    Steam item: Glove Case
    app_id: 730
    Price: $15.1
    ```
- `/add_stock <ticker> <quantity> [-p <price>]`: Add stock to portfolio.
  - Example: `/add_stock AMD 2 -p 170.50`
  - Response: `Added 2 AMD at 170.50$`
- `/add_crypto <coin> <quantity> [-p <price>]`: Add cryptocurrency to portfolio.
  - Example: `/add_crypto BTC 0.05 -p 106969.69`
  - Response: `Added 0.05 BTC at 106969.69$`
- `/add_steam <app_id> <market_name> <quantity> [-p <price>]`: Add Steam item to portfolio.
  - Example: `/add_steam 730 Operation Bravo Case 10`
  - Response: `Added 10 Operation Bravo Case at 54.05$`
- `/remove_stock <ticker> <quantity>`: Remove stock from portfolio.
  - Example: `/remove_stock AMD 2`
  - Response: `Removed 2 AMD from portfolio`
- `/remove_crypto <coin> <quantity>`: Remove cryptocurrency from portfolio.
  - Example: `/remove_crypto BTC 0.05`
  - Response: `Removed 0.05 BTC from portfolio`
- `/remove_steam <app_id> <market_name> <quantity>`: Remove Steam item from portfolio.
-   - Example: `/remove_steam 730 Glove Case 10`
    - Response: `Removed 10 Glove Case from portfolio`
- `/portfolio <all|stocks|crypto|steam|total>`: View your portfolio.
  - Example: `/portfolio all`
  - Response:
    ```
    📊 Your Portfolio

    🏛️ Stocks
    MSFT: 69.69 at avg. price $508.14, now $528.52, value $35412.28 (+4.01% 📈)
    NVDA: 90.00 at avg. price $178.07, now $185.96, value $16026.30 (+4.43% 📈)

    ₿ Crypto
    solana: 69.00 at avg. price $196.77, now $236.66, value $13577.13 (+20.27% 📈)

    🎮 Steam Items
    Recoil Case: 1050.00 at avg. price $0.44, now $0.43, value $462.00 (-2.27% 📉)
    Snakebite Case: 1703.00 at avg. price $0.33, now $0.82, value $561.99 (+148.48% 📈)
    Clutch Case: 1.00 at avg. price $100.00, now $1.11, value $100.00 (-98.89% 📉)

    ◇───────────────────────────────────────────◇

    💰 Total value: $71747.57
    📊 Total growth: +8.48% 📈
    ```
- `/set_alert <asset_type> [app_id] <asset_name> <condition> <price>`: Set a price alert.
  - Example: `/set_alert stock AMD > 200`
  - Response: `🔔 Alert created for AMD (Stock) with target > $200.00`
  - <!-- Add alert screenshot here: <img src="assets/alert-example.png" alt="Price Alert Example" width="400"/> -->
- `/alerts`: Show all active alerts.
  - Example: `/alerts`
  - Response:
    ```
    #11: NVDA, target > $200.00
    #12: AMZN, target > $250.00
    #13: Fever Case, app_id=730, target > $2.00
    #14: Fracture Case, app_id=730, target > $1.00
    ```
- `/delete_alert <id>`: Remove an alert by ID.
  - Example: `/delete_alert 1`
  - Response: `🔔 Alert #1 for AMD deleted successfully`
- `/history <all|stocks|crypto|steam>`: View purchase history.
  - Example: `/history stocks`
  - Response:
    ```
    📜 Portfolio History

    🗠 Stocks
    Added 69.69 MSFT at 25-08-22 18:42:55
    Added 90.00 NVDA at 25-08-22 18:42:11
    ```

### Example Portfolio

Below is a live example of `/portfolio all` showing Stocks, Crypto, and Steam Items:

<img src="assets/bot_example.png" alt="Portfolio Command Example" width="600"/>

This shows:
- Each asset with quantity, average price, current price, and value.
- Profit/loss in %.
- Total portfolio value and growth.


### Limitations
- **Throttling**: To prevent spam, `ThrottlingMiddleware` (Redis-based) warns users after sending messages within 2 seconds (`THROTTLE_FIRST_LIMIT`) with "Too many requests! Try later" and ignores requests after 5 seconds (`THROTTLE_SECOND_LIMIT`). Adjust in `config.py`.
- **Alerts**: Maximum 10 alerts per user (`MAXIMUM_ALERTS`). Alerts are checked every 300 seconds (`ALERT_INTERVAL_SECONDS`). Configurable in `config.py`.
- **Portfolio**: No size limits, using `Numeric` type in SQLAlchemy with 38-digit precision for small/large values (e.g., cryptocurrencies).

## Dependencies and Architecture 🏗️

### Dependencies
- `aiogram`: For Telegram bot development.
- `aiohttp`: For asynchronous requests to InvestAPI.
- `redis`: For throttling middleware.
- `sqlalchemy` and `alembic`: For database management.
- `aiosqlite` (dev) or `psycopg2-binary`/`asyncpg` (prod): For SQLite/PostgreSQL databases.
- `python-dotenv`: For environment variables.
- `pytest` and `pytest-asyncio`: For future testing.

### Architecture
The bot uses `aiogram` for asynchronous Telegram command handling. It communicates with [InvestAPI](https://github.com/Max2772/InvestAPI) for price data and stores user data in a database (SQLite for dev, PostgreSQL for prod). The database includes:
- `investingapibot_users`: Tracks registered users.
- `investingapibot_portfolios`: Stores portfolio data (assets, quantities, purchase prices).
- `investingapibot_alerts`: Manages price alerts.
- `alembic_version`: For database migrations.

**Workflow Example (/portfolio)**:
1. `UserMiddleware` identifies the user via Telegram ID.
2. `ThrottlingMiddleware` (Redis-based) prevents spam, warning after rapid messages within 2 seconds and ignoring after 5 seconds.
3. The bot queries the `investingapibot_portfolios` table via SQLAlchemy, retrieves user assets, fetches current prices from InvestAPI, calculates profit/loss, and formats the response.

<!-- Add architecture diagram here: <img src="assets/architecture-diagram.png" alt="Bot Architecture" width="600"/> -->

## Contributing 🤝

Contributions are welcome! Fork the repository and submit a Pull Request. The bot is publicly available at [@InvestingAPIBot](https://t.me/InvestingAPIBot) and actively maintained. Roadmap:
- Add inline keyboards for faster command interaction.
- Implement tests with `pytest`.
- Support additional asset types.

## License 📜

This project is licensed under the MIT License. See the [License](LICENSE) file for details.

## Contact 📫

- GitHub: [@Max2772](https://github.com/Max2772)
- Email: [bib.maxim@gmail.com](mailto:bib.maxim@gmail.com)
- Telegram: [@max_bibikov](https://t.me/max_bibikov)