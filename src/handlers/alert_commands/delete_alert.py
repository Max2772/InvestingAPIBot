import re
from aiogram import html
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import select, and_
from sqlalchemy.exc import SQLAlchemyError
from src.common import dp
from src.dao.models import AsyncSessionLocal, User, Alert
from src import (get_logger)

logger = get_logger()


@dp.message(Command('delete_alert'))
async def delete_alert_handler(message: Message) -> None:
    pattern = re.compile(r"^/delete_alert\s+(\d+)$", re.IGNORECASE)
    match = pattern.match(message.text.strip())
    if not match:
        await message.answer("Please provide a valid alert id!")
        return

    alert_id = int(match.group(1))

    async with AsyncSessionLocal() as session:
        user = await session.get(User, message.from_user.id)
        if not user:
            await message.answer(f"Sorry, to use this command, you need to first register(/register).")
            return

        try:
            result = await session.execute(
                select(Alert).where(
                    and_(
                        Alert.user_id == user.telegram_id,
                        Alert.id == alert_id
                    )
                )
            )

            alert = result.scalars().first()

            if not alert:
                await message.answer(f"Alert with id {alert_id} does not exist.")
                return

            await session.delete(alert)
            await session.commit()
            await message.answer(f"Deleted alert for {alert.asset_name} with id {alert.id}")

        except SQLAlchemyError as e:
            logger.error(f"Database error while deleting alert with id {alert_id}: {e}")
            await message.answer(f"Failed to delete alert with id {alert_id} due to database error.")
        except Exception as e:
            logger.error(f"Failed to delete alert with id {alert_id}: {e}")
            await message.answer(f"Failed to delete alert with id {alert_id}.")