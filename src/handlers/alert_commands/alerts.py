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
async def alerts_handler(message: Message, user: User):
    async with AsyncSessionLocal() as session:
        try:
            if not user.alerts:
                await message.answer("You have no active alerts.")
                return

            alert_text = "<b>📢 Your Alerts</b>\n\n"
            for alert in user.alerts:
                asset = f"{alert.asset_name}" if not alert.app_id else f"{alert.asset_name}, app_id: {alert.app_id}"

                alert_text += (
                    f"#{alert.id}: {asset}, target {alert.direction} ${alert.target_price:.2f} "
                )

            await message.answer(alert_text, parse_mode=ParseMode.HTML)

        except SQLAlchemyError as e:
            logger.error(f"Database error while listing alerts: {e}")
            await message.answer(f"Failed to list alerts due to database error.")
        except Exception as e:
            logger.error(f"Failed to list alerts: {e}")
            await message.answer(f"Failed to list alerts due to error.")

