import re
from decimal import Decimal
from urllib.parse import unquote

import aiohttp
from aiogram import Router, html
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import select, and_

from src.dao.models import AsyncSessionLocal, User, Portfolio
from src.utils import get_logger, get_api_url, fetch_api_data, float_price_pattern


logger = get_logger()

router = Router()


@router.message(Command('add_steam'))
async def add_steam_handler(message: Message, user: User) -> None:
    pattern = re.compile(rf"^/add_steam\s+(\d+)\s+(.+)\s+(\d+)\s*(?:-p\s+({float_price_pattern}))?$")
    match = pattern.match(message.text.strip())
    if not match:
        await message.answer("Please provide a valid app_id, market name and amount!")
        return

    app_id = int(match.group(1))
    market_name = unquote(match.group(2))
    amount = Decimal(str(match.group(3)))
    parameter_price = Decimal(str(match.group(4))) if match.group(4) else None

    if amount <= 0 or app_id <= 0:
        await message.answer('Amount and app id must be positive!')
        return

    if parameter_price is not None and parameter_price <= 0:
        await message.answer('Price must be positive!')
        return


    try:
        async with AsyncSessionLocal() as session:
            if parameter_price is not None:
                price = parameter_price
            else:
                async with aiohttp.ClientSession() as client:
                    url = get_api_url('steam', market_name, app_id)
                    data = await fetch_api_data(client, url, message)
                    if data is None:
                        return

                    price = Decimal(str(data.get('price', 0.0)))

            portfolio = Portfolio(
                user_id=user.telegram_id,
                asset_type='steam',
                asset_name=market_name,
                quantity=amount,
                buy_price=price,
                app_id=app_id
            )

            result = await session.execute(
                select(Portfolio).where(
                    and_(
                        Portfolio.user_id == user.telegram_id,
                        Portfolio.asset_type == 'steam',
                        Portfolio.asset_name == market_name,
                        Portfolio.app_id == app_id
                    )
                )
            )

            asset = result.scalars().first()

            if asset:
                asset.buy_price = (asset.quantity * asset.buy_price + amount * price) / (asset.quantity + amount)
                asset.quantity += amount
            else:
                session.add(portfolio)

            await session.commit()
            await message.answer(f"Added {amount} {market_name} at {html.bold(price)}$")
    except Exception as e:
        logger.error(f"Error adding Steam item {market_name}, app_id={app_id}: {e}")
        await message.answer(f"Failed to add Steam item {market_name}, app_id={app_id}")