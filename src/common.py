import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from src.middlewares import (ThrottlingMiddleware, UserMiddleware)

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_BASE_URL = "http://127.0.0.1:8000"

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
storage = RedisStorage.from_url("redis://localhost:6379")
dp = Dispatcher(storage=storage)
dp.message.middleware.register(ThrottlingMiddleware(storage=storage))
dp.message.middleware.register(UserMiddleware())