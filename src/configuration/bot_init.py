from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from src.handlers import *
from src.middlewares import ThrottlingMiddleware, UserMiddleware
from src.configuration.config import TOKEN, REDIS_URL, ADMIN_ID
from src.utils import get_logger
from src.configuration.check_redis import check_redis


logger = get_logger()

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
storage = RedisStorage.from_url(REDIS_URL)
dp = Dispatcher(storage=storage)
dp.message.middleware.register(ThrottlingMiddleware(storage=storage))
dp.message.middleware.register(UserMiddleware())

dp.include_router(register_router)
dp.include_router(help_router)

dp.include_router(check_stock_router)
dp.include_router(check_crypto_router)
dp.include_router(check_steam_router)

dp.include_router(add_stock_router)
dp.include_router(add_crypto_router)
dp.include_router(add_steam_router)

dp.include_router(remove_stock_router)
dp.include_router(remove_crypto_router)
dp.include_router(remove_steam_router)

dp.include_router(alerts_router)
dp.include_router(set_alert_router)
dp.include_router(delete_alert_router)

dp.include_router(portfolio_router)
dp.include_router(history_router)


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
    else:
        await bot.send_message(ADMIN_ID, "✅ Redis available, bot started successfully.")
        logger.info("Redis available, bot started successfully")
