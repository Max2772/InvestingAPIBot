import re
from decimal import Decimal
import aiohttp
from html import escape
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import select, and_, func
from sqlalchemy.exc import SQLAlchemyError

from src.dao.models import AsyncSessionLocal, User, Alert
from src.bot_init import dp
from src.config import MAXIMUM_ALERTS
from src import (get_logger, get_api_url, fetch_api_data)


logger = get_logger()

@dp.message(Command('set_alert'))
async def set_alert_handler(message: Message, user: User):
    pattern = re.compile(r"^/set_alert\s+(stock|crypto|steam)(\s+\d+)?\s+(.+)\s+(>|>=|<|<=)\s+(\d+(\.\d+)?)$", re.IGNORECASE)
    match = pattern.match(message.text.strip())
    if not match:
        await message.answer("❌ Invalid format. Use /help to see how to write this command.")
        return

    asset_type = match.group(1).lower()
    app_id = int(match.group(2)) if match.group(2) else None
    asset_name = match.group(3).upper() if asset_type == 'stock' else match.group(3)
    direction = match.group(4)
    price = Decimal(str(match.group(5)))

    if price <= 0:
        await message.answer("Target price must be positive!")
        return

    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(
                select(func.count()).where(Alert.user_id == user.telegram_id) # NoQa
            )

            count = result.scalar_one_or_none()
            if count + 1 > MAXIMUM_ALERTS:
                await message.answer(
                    f"You have reached the maximum number of alerts ({MAXIMUM_ALERTS}). Delete some alerts first."
                )
                return

            async with aiohttp.ClientSession() as client:
                url = get_api_url(asset_type, asset_name, app_id)
                data = await fetch_api_data(client, url, message)
                if data is None:
                    return

                name = str(data.get('name', asset_name))

                alert = Alert(
                    user_id=user.telegram_id,
                    asset_type=asset_type,
                    asset_name=name,
                    target_price=price,
                    direction=direction,
                    app_id=app_id,
                )

                result = await session.execute(
                    select(Alert).where(
                        and_(
                            Alert.user_id == alert.user_id,
                            Alert.asset_type == alert.asset_type,
                            Alert.asset_name == alert.asset_name,
                            Alert.app_id == alert.app_id
                        )
                    )
                )
                asset = result.scalars().first()

                if asset:
                    await message.answer(
                        f"Alert for <b>{name}</b> already exists.",
                        parse_mode=ParseMode.HTML
                    )
                    return

                session.add(alert)
                await session.commit()
                await message.answer(
                    f"🔔 Alert created for <b>{name}</b> ({asset_type.capitalize()}) "
                    f"with target {escape(direction)} ${price:.2f}.",
                    parse_mode=ParseMode.HTML
                )
        except SQLAlchemyError as e:
            logger.error(f"Database error while adding alert: {e}")
            await message.answer("Failed to add alert due to database error.")
        except Exception as e:
            logger.error(f"Error adding alert: {e}")
            await message.answer("Failed to add alert due to error.")