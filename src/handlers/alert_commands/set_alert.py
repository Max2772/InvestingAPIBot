import re
from decimal import Decimal
import httpx
from aiogram import html
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import select, and_, func
from sqlalchemy.exc import SQLAlchemyError

from src.common import dp
from src.dao.models import AsyncSessionLocal, User, Alert
from src import (get_logger)
from src.common import API_BASE_URL

logger = get_logger()

@dp.message(Command('set_alert'))
async def set_alert_handler(message: Message, user: User):
    pattern = re.compile(r"^/set_alert\s+(stock|crypto|steam)(\s+\d+)?\s+(.+)\s+(>|>=|<|<=)\s+(\d+(\.\d+)?)$", re.IGNORECASE)
    match = pattern.match(message.text.strip())
    if not match:
        await message.answer(
            "<b>🔔 Usage:</b> /set_alert <code>stock|crypto|steam [app_id]</code> "
            "<code>asset</code> <code>>|>=|<|<=</code> <code>price</code>\n",
            parse_mode=ParseMode.HTML
        )
        return

    asset_type = match.group(1).lower()
    app_id = int(match.group(2)) if match.group(2) else None
    asset_name = match.group(3).upper() if asset_type == 'stock' else match.group(3)
    direction = match.group(4)
    price = Decimal(str(match.group(5)))

    if price <= 0:
        await message.answer("Target price must be positive!",)
        return

    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(
                select(func.count()).where(Alert.user_id == user.telegram_id) # NoQa
            )
            count = result.scalar_one_or_none()
            if count > 20:
                await message.answer(
                    "You have reached the maximum number of alerts (20). Delete some alerts first.")
                return

            async with httpx.AsyncClient() as client:
                url = f"{API_BASE_URL}/{asset_type}/{asset_name}" if app_id is None else f"{API_BASE_URL}/{asset_type}/{app_id}/{asset_name}"
                response = await client.get(url)
                if response.status_code == 404:
                    await message.answer("Sorry, this asset doesn't exist.")
                    return

                response.raise_for_status()
                data = response.json()
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
                    f"with target {direction} ${price:.2f}.",
                    parse_mode=ParseMode.HTML
                )
        except SQLAlchemyError as e:
            logger.error(f"Database error while adding alert: {e}")
            await message.answer("Failed to add alert due to database error.")
        except Exception as e:
            logger.error(f"Error adding alert: {e}")
            await message.answer("Failed to add alert due to error.")