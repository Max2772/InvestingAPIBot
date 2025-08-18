from aiogram import html
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import func, select, and_
from sqlalchemy.exc import SQLAlchemyError
from src.common import dp
from src.dao.models import AsyncSessionLocal, User, Alert
from src import (get_logger)

logger = get_logger()

@dp.message(Command('alerts'))
async def alerts_handler(message: Message) -> None:
    async with (AsyncSessionLocal() as session):
        try:
            user = await session.get(User, message.from_user.id)
            if not user:
                await message.answer(f"Please register first (/register).")
                return

            if not user.alerts:
                await message.answer("You have no active alerts.")
                return

            result = await session.execute(
                select(Alert).where(Alert.user_id == user.telegram_id) # NoQa
            )

            alerts = result.scalars()

            alert_text = "Alerts:\n\n"

            for alert in alerts:
                alert_text += f"{alert.id}) {alert.asset_name}, target price {alert.direction} ${alert.target_price:.2f}\n"

            await message.answer(alert_text, parse_mode=None)

        except SQLAlchemyError as e:
            logger.error(f"Database error while listing alerts: {e}")
            await message.answer(f"Failed to list alerts due to database error.")
        except Exception as e:
            logger.error(f"Failed to list alerts: {e}")
            await message.answer(f"Failed to list alerts due to error.")

