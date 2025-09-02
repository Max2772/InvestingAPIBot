from html import escape

from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.exc import SQLAlchemyError

from src.dao.models import AsyncSessionLocal, User
from src.configuration.bot_init import dp
from src.utils import get_logger


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
                asset = (
                    f"{alert.asset_name}"
                    if not alert.app_id else
                    f"{alert.asset_name}, app_id={alert.app_id}"
                )

                alert_text += (
                    f"<b>#{alert.id}</b>: {asset}, target {escape(alert.direction)} <b>${alert.target_price:.2f}</b>\n"
                )

            await message.answer(alert_text, parse_mode=ParseMode.HTML)

        except SQLAlchemyError as e:
            logger.error(f"Database error while listing alerts: {e}")
            await message.answer(f"Failed to list alerts due to database error.")
        except Exception as e:
            logger.error(f"Failed to list alerts: {e}")
            await message.answer(f"Failed to list alerts due to error.")

