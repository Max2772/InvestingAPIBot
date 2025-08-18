import os
from typing import Any, Awaitable, Callable, Dict
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, BaseMiddleware
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.types import TelegramObject, Message
from aiogram.enums import ParseMode

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_BASE_URL = "http://127.0.0.1:8000"

class ThrotllingMiddleware(BaseMiddleware):
    def __init__(self, storage: RedisStorage):
        self.storage = storage

    async def __call__(self,
                       handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: Message,
                       data: Dict[str, Any]
                       ) -> Any:
        user = f'user:{event.from_user.id}'

        check_user = await self.storage.redis.get(name=user)

        if check_user:
            if int(check_user.decode()) == 1:
                await self.storage.redis.set(name=user, value=0, ex=1)
                return await event.answer("Too many requests! Try Later")

            return

        await self.storage.redis.set(name=user, value=1, ex=1)
        return await handler(event, data)

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
storage = RedisStorage.from_url("redis://localhost:6379")
dp = Dispatcher(storage=storage)
dp.message.middleware.register(ThrotllingMiddleware(storage=storage))