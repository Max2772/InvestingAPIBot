import os
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

def get_now() -> datetime:
    return datetime.utcnow()

LOG_LEVEL: str = (os.getenv("LOG_LEVEL") or "INFO").upper()

BOT_TOKEN: str = os.getenv("BOT_TOKEN")
API_BASE_URL: str = os.getenv("API_BASE_URL") or "http://127.0.0.1:8000"

DATABASE_URL: str = os.getenv("DATABASE_URL") or "sqlite:///InvestingAPIBot.db"
ASYNC_DATABASE_URL: str = os.getenv("ASYNC_DATABASE_URL") or "sqlite+aiosqlite:///InvestingAPIBot.db"

MAXIMUM_ALERTS: int = int(os.getenv("MAXIMUM_ALERTS") or 10)
ALERT_INTERVAL_SECONDS: int = int(os.getenv("ALERT_INTERVAL_SECONDS") or 300)