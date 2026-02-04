from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from src.bot_init.middlewares.UserRegMiddleware import UserRegMiddleware
from src.env import BOT_TOKEN
from src.handlers import HANDLERS_ROUTER

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

dp.update.middleware(UserRegMiddleware())

dp.include_router(HANDLERS_ROUTER)