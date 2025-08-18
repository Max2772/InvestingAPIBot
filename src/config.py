import os
from dotenv import load_dotenv


load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_BASE_URL = "http://127.0.0.1:8000"
REDIS_URL = "redis://localhost:6379"
THROTTLE_FIRST_LIMIT = 100
THROTTLE_SECOND_LIMIT = 100
MAXIMUM_ALERTS = 10
ALERT_INTERVAL_SECONDS = 10
