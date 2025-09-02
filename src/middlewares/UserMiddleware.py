from typing import Any, Dict, Callable, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message

from src.dao.models import AsyncSessionLocal, User


class UserMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any],
    ) -> Any:
        if event.text.strip().lower() in ('/start', '/register'):
            return await handler(event, data)

        async with AsyncSessionLocal() as session:
            user = await session.get(User, event.from_user.id)
            if not user:
                await event.answer('Please register first (/register).')
                return

            data['user'] = user
            return await handler(event, data)
