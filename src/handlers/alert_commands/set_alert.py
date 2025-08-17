import re
from decimal import Decimal
import httpx
from aiogram import html
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import select, and_
from src.common import dp
from src.dao.models import AsyncSessionLocal, User, Alert
from src import (get_logger)
from src.common import API_BASE_URL

logger = get_logger()

@dp.message(Command('set_alert'))
async def set_alert_handler(message: Message) -> None:
    pattern = re.compile(r"^/set_alert\s+(stock|crypto|steam)(\s+\d+)?\s+(.+)\s+(\d+(\.\d+)?)$", re.IGNORECASE)
    match = pattern.match(message.text.strip())
    if not match:
        await message.answer("Please provide a valid asset type, name and amount!")
        return

    asset_type = match.group(1).lower()
    app_id = int(match.group(2)) if match.group(2) else None
    asset_name = match.group(3)
    price = Decimal(str(match.group(4)))


    if price == 0:
        await message.answer("Target price cannot be zero!")
        return

    async with AsyncSessionLocal() as session:
        user = await session.get(User, message.from_user.id)
        if not user:
            await message.answer(f"Sorry, to use this command, you need to first register(/register).")
            return

        try:
            async with httpx.AsyncClient() as client:
                url = f"{API_BASE_URL}/{asset_type}/{asset_name}" if app_id is None else f"{API_BASE_URL}/{asset_type}/{app_id}/{asset_name}"
                response = await client.get(url)
                response.raise_for_status()
                if response.status_code == 404:
                    await message.answer("Sorry, this asset doesn't exist.")
                    return

                data = response.json()
                name = str(data.get('name', asset_name))

                alert = Alert(
                    user_id=user.telegram_id,
                    asset_type=asset_type,
                    asset_name=name,
                    target_price=price
                )

                result = await session.execute(
                    select(Alert).where(
                        and_(
                            Alert.user_id == alert.user_id,
                            Alert.asset_type == alert.asset_type,
                            Alert.asset_name == alert.asset_name
                        )
                    )
                )
                asset = result.scalars().first()

                if asset:
                    await message.answer(f"Alert {alert.asset_name} is already registered.")
                    return

                session.add(alert)
                await session.commit()
                await message.answer(f"Added alert for {alert.asset_name} with target price ${html.bold(price)}")

        except (httpx.HTTPError, KeyError, ValueError) as e:
          logger.error(f"Error adding alert for {alert.asset_name}: {e}")
          await message.answer(f"Failed to add alert for {alert.asset_name}")