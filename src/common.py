import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_BASE_URL = "http://127.0.0.1:8000"

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()