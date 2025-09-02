from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from src.middlewares import (ThrottlingMiddleware, UserMiddleware)
from src.configuration.config import TOKEN, REDIS_URL, ADMIN_ID
from src.utils import get_logger
from src.configuration import check_redis


logger = get_logger()

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
storage = RedisStorage.from_url(REDIS_URL)
dp = Dispatcher(storage=storage)
dp.message.middleware.register(ThrottlingMiddleware(storage=storage))
dp.message.middleware.register(UserMiddleware())


@dp.startup()
async def on_startup():
    if not await check_redis(storage):
        try:
            await bot.send_message(ADMIN_ID, "❌ Redis unavailable, bot stopped.")
            logger.error("Redis unavailable, bot stopped.")
        except Exception as e:
            logger.error(f"Bot stopped: {e}")

        await bot.session.close()
        quit()
