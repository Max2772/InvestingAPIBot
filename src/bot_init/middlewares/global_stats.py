from typing import Dict

from sqlalchemy import select

from src.dao.models import AsyncSessionLocal, DbUser
from src.types.system_types import LocalUser

USERS: Dict[int, LocalUser] = {}


def get_local_user(user_id: int) -> LocalUser:
    local_user = USERS.get(user_id)
    if local_user is None:
        raise ValueError(f"User id {user_id} not found")
    return local_user

def db_to_local_user(user: DbUser) -> LocalUser:
    return LocalUser(
        telegram_id=user.telegram_id,
        username=user.username,
        first_name= user.first_name,
        last_name = user.last_name
    )

async def load_users() -> None:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(DbUser))
        users = result.scalars().all()

        for user in users:
            USERS[user.telegram_id] = db_to_local_user(user)

