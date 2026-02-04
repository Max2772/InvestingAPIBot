from typing import Callable, Awaitable, Dict, Any, Set, Optional

from aiogram import BaseMiddleware
from aiogram.types import Update

from src.bot_init.middlewares.global_stats import USERS, db_to_local_user
from src.dao.models import AsyncSessionLocal, DbUser
from src.logger import logger
from src.types.system_types import LocalUser
from src.utils.formatters import get_plain_name
from src.utils.tg_utils import extract_user

ACTIVE_CHATS: Set[int] = set()

class UserRegMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: Dict[str, Any],
    ):
        tg_user = extract_user(event)

        if tg_user is None:
            logger.warning(f"tg_user is None from: {event}; {data}")
            return None

        is_pre_checkout: bool = event.pre_checkout_query is not None
        chat_id: Optional[int] = None

        if not is_pre_checkout:
            chat = data.get("event_chat")
            if chat is None or chat.id is None:
                return None
            chat_id = chat.id
            if chat_id in ACTIVE_CHATS:
                return None

            ACTIVE_CHATS.add(chat_id)
        try:
            local_user: LocalUser = USERS.get(tg_user.id)

            if local_user:
                data["user"] = local_user
                return await handler(event, data)

            async with AsyncSessionLocal() as session:
                user = await session.get(DbUser, tg_user.id)
                if not user:
                    try:
                        user = DbUser(
                            telegram_id=tg_user.id,
                            username=tg_user.username,
                            first_name=tg_user.first_name,
                            last_name=tg_user.last_name
                        )

                        session.add(user)
                        await session.commit()

                        USERS[tg_user.id] = db_to_local_user(user)
                        logger.info(f"Added user ({tg_user.id}) {get_plain_name(user)}")

                    except Exception as e:
                        logger.error(f"While adding user {tg_user.id}: {e}")
                        await event.answer("🔧 Service error, try again later")
                        return None
                else:
                    USERS[tg_user.id] = db_to_local_user(user)

                data["user"] = USERS[tg_user.id]
                return await handler(event, data)
        finally:
            if not is_pre_checkout:
                ACTIVE_CHATS.discard(chat_id)