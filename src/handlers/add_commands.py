import re
import aiohttp
from decimal import Decimal
from urllib.parse import unquote
from aiogram import html
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import select, and_

from src.dao.models import AsyncSessionLocal, User, Portfolio
from src.bot_init import dp
from src import (get_logger, get_api_url, fetch_api_data, science_price_pattern, simple_price_pattern)

logger = get_logger()

@dp.message(Command('add_stock'))
async def add_stock_handler(message: Message, user: User):
    pattern = re.compile(rf"^/add_stock\s+(.+)\s+{science_price_pattern}(\s+-p\s+{science_price_pattern})?$")
    match = pattern.match(message.text.strip())
    if not match:
        await message.answer("Please provide a valid ticker and amount!")
        return

    ticker = match.group(1).upper()
    amount = Decimal(str(match.group(2)))
    parameter_price = Decimal(str(match.group(4))) if match.group(3) else None

    if amount <= 0:
        await message.answer('Amount must be positive!')
        return

    if  parameter_price is not None and parameter_price <= 0:
        await message.answer('Price must be positive!')
        return

    try:
        async with AsyncSessionLocal() as session:
            if parameter_price is not None:
                price = parameter_price
            else:
                async with aiohttp.ClientSession() as client:
                    url = get_api_url('stock', ticker)
                    data = await fetch_api_data(client, url, message)
                    if data is None:
                        return

                    price = Decimal(str(data.get('price', 0.0)))

            portfolio = Portfolio(
                user_id=user.telegram_id,
                asset_type='stock',
                asset_name=ticker,
                quantity=amount,
                buy_price=price
            )

            result = await session.execute(
                select(Portfolio).where(
                    and_(
                        Portfolio.user_id == user.telegram_id,
                        Portfolio.asset_type == 'stock',
                        Portfolio.asset_name == ticker
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
            await message.answer(f"Added {amount} {ticker} at {html.bold(price)}$")
    except Exception as e:
        logger.error(f"Error adding stock {ticker}: {e}")
        await message.answer(f"Failed to add stock {ticker}")

@dp.message(Command('add_crypto'))
async def add_crypto_handler(message: Message, user: User):
    pattern = re.compile(r"^/add_crypto\s+(.+)\s+(\d+(\.\d+)?|\d+(\.\d+)?[eE][+-]\d+)$")
    match = pattern.match(message.text.strip())
    if not match:
        await message.answer("Please provide a valid coin and amount!")
        return

    coin = match.group(1).upper()
    amount = Decimal(str(match.group(2)))

    if amount <= 0:
        await message.answer('Amount must be positive!')
        return

    try:
        async with AsyncSessionLocal() as session:
            async with aiohttp.ClientSession() as client:
                url = get_api_url('crypto', coin)
                data = await fetch_api_data(client, url, message)
                if data is None:
                    return

                price = Decimal(str(data.get('price', 0.0)))
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

@dp.message(Command('add_steam'))
async def add_steam_handler(message: Message, user: User) -> None:
    pattern = re.compile(r"^/add_steam\s+(\d+)\s+(.+)\s+(\d+)$")
    match = pattern.match(message.text.strip())
    if not match:
        await message.answer("Please provide a valid app_id, market name and amount!")
        return

    app_id = int(match.group(1))
    market_name = unquote(match.group(2))
    amount = Decimal(str(match.group(3)))

    if amount <= 0:
        await message.answer('Amount must be positive!')
        return

    try:
        async with AsyncSessionLocal() as session:
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