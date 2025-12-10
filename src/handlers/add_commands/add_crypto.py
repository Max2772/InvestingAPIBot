import re
from decimal import Decimal

import aiohttp
from aiogram import Router, html
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import select, and_

from src.dao.models import AsyncSessionLocal, User, Portfolio
from src.utils import get_logger, get_api_url, fetch_api_data, science_price_pattern

logger = get_logger()

router = Router()


@router.message(Command('add_crypto'))
async def add_crypto_handler(message: Message, user: User):
    pattern = re.compile(rf"^/add_crypto\s+([-A-Za-z0-9. ]+)\s+({science_price_pattern})\s*(?:-p\s+({science_price_pattern}))?$")
    match = pattern.match(message.text.strip())
    if not match:
        await message.answer("Please provide a valid coin and amount!")
        return

    coin = match.group(1).upper()
    amount = Decimal(str(match.group(2)))
    parameter_price = Decimal(str(match.group(3))) if match.group(3) else None

    if amount <= 0:
        await message.answer('Amount must be positive!')
        return

    if parameter_price is not None and parameter_price <= 0:
        await message.answer('Price must be positive!')
        return

    try:
        async with AsyncSessionLocal() as session:
            async with aiohttp.ClientSession() as client:
                url = get_api_url('crypto', coin)
                data = await fetch_api_data(client, url, message)
                if data is None:
                    return

                price = Decimal(str(data.get('price', 0.0))) if parameter_price is None else parameter_price

            name = str(data.get('name', coin))

            portfolio = Portfolio(
                user_id=user.telegram_id,
                asset_type='crypto',
                asset_name=name,
                quantity=amount,
                buy_price=price
            )

            result = await session.execute(
                select(Portfolio).where(
                    and_(
                        Portfolio.user_id == user.telegram_id,
                        Portfolio.asset_type == 'crypto',
                        Portfolio.asset_name == name
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
            await message.answer(f"Added {amount} {coin} at {html.bold(price)}$")
    except Exception as e:
        logger.error(f"Error adding crypto {coin}: {e}")
        await message.answer(f"Failed to add crypto {coin}")