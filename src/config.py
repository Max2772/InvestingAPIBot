import os
from dotenv import load_dotenv


load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_BASE_URL = "http://127.0.0.1:8000"
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
THROTTLE_FIRST_LIMIT = 2
THROTTLE_SECOND_LIMIT = 5
MAXIMUM_ALERTS = 10
ALERT_INTERVAL_SECONDS = 10
