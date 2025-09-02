from typing import Any, Dict, Callable, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message
from aiogram.fsm.storage.redis import RedisStorage

from src.configuration.config import THROTTLE_FIRST_LIMIT, THROTTLE_SECOND_LIMIT


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, storage: RedisStorage):
        self.storage = storage

    async def __call__(
            self,
            handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any],
    ) -> Any:
        user = f'user:{event.from_user.id}'
        check_user = await self.storage.redis.get(name=user)

        if check_user:
            if int(check_user.decode()) == 1:
                await self.storage.redis.set(name=user, value=0, ex=THROTTLE_SECOND_LIMIT)
                return await event.answer('Too many requests! Try later')
            return

        await self.storage.redis.set(name=user, value=1, ex=THROTTLE_FIRST_LIMIT)
        return await handler(event, data)