from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from src.middlewares import (ThrottlingMiddleware, UserMiddleware)
from src.config import TOKEN, REDIS_URL

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
storage = RedisStorage.from_url(REDIS_URL)
dp = Dispatcher(storage=storage)
dp.message.middleware.register(ThrottlingMiddleware(storage=storage))
dp.message.middleware.register(UserMiddleware())