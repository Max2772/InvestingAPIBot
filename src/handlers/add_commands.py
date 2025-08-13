import re
import httpx
from decimal import Decimal
from aiogram import html
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import select, and_

from src.common import dp, API_BASE_URL
from src.dao.models import AsyncSessionLocal, User, Portfolio
from src.utils import (get_logger)

logger = get_logger()

@dp.message(Command('add_stock'))
async def add_stock_handler(message: Message) -> None:
    pattern = re.compile(r"^/add_stock\s+(.+)\s+(\d+(\.\d+)?|\d+(\.\d+)?[eE][+-]\d+)$")
    match = pattern.match(message.text.strip())
    if not match:
        await message.answer("Please provide a valid ticker and amount!")
        return

    ticker = match.group(1).upper()
    amount = Decimal(str(match.group(2)))

    if amount == 0:
        await message.answer("Amount cannot be zero!")
        return

    async with AsyncSessionLocal() as session:
        user = await session.get(User, message.from_user.id)
        if not user:
            await message.answer(f"Sorry, to use this command, you need to first register(/register).")
            return
        async with httpx.AsyncClient() as client:
            try:
                url = f"{API_BASE_URL}/stock/{ticker}"
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
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
                    asset.buy_price = (asset.quantity * asset.buy_price + amount * price) / 2
                    asset.quantity += amount
                else:
                    session.add(portfolio)

                await session.commit()
                await message.answer(f"Added {amount} {ticker} at {html.bold(price)}$")
            except (httpx.HTTPError, KeyError, ValueError) as e:
                logger.error(f"Error adding stock {ticker}: {e}")
                await message.answer(f"Failed to add stock {ticker}")

@dp.message(Command('add_crypto'))
async def add_crypto_handler(message: Message) -> None:
    pattern = re.compile(r"^/add_stock\s+(.+)\s+(\d+(\.\d+)?|\d+(\.\d+)?[eE][+-]\d+)$")
    match = pattern.match(message.text.strip())
    if not match:
        await message.answer("Please provide a valid coin and amount!")
        return

    coin = match.group(1).upper()
    amount = Decimal(str(match.group(2)))

    if amount == 0:
        await message.answer("Amount cannot be zero!")
        return

    async with AsyncSessionLocal() as session:
        user = await session.get(User, message.from_user.id)
        if not user:
            await message.answer(f"Sorry, to use this command, you need to first register(/register).")
            return
        async with httpx.AsyncClient() as client:
            try:
                url = f"{API_BASE_URL}/crypto/{coin}"
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                price = Decimal(str(data.get('price', 0.0)))

                portfolio = Portfolio(
                    user_id=user.telegram_id,
                    asset_type='crypto',
                    asset_name=coin,
                    quantity=amount,
                    buy_price=price
                )

                result = await session.execute(
                    select(Portfolio).where(
                        and_(
                            Portfolio.user_id == user.telegram_id,
                            Portfolio.asset_type == 'crypto',
                            Portfolio.asset_name == coin
                        )
                    )
                )

                asset = result.scalars().first()

                if asset:
                    asset.buy_price = (asset.quantity * asset.buy_price + amount * price) / 2
                    asset.quantity += amount
                else:
                    session.add(portfolio)

                await session.commit()
                await message.answer(f"Added {amount} {coin} at {html.bold(price)}$")
            except (httpx.HTTPError, KeyError, ValueError) as e:
                logger.error(f"Error adding crypto {coin}: {e}")
                await message.answer(f"Failed to add crypto {coin}")

@dp.message(Command('add_steam'))
async def add_steam_handler(message: Message) -> None:
    pattern = re.compile(r"^/add_steam\s+(\d+)\s+(.+)\s+(\d+)$")
    match = pattern.match(message.text.strip())
    if not match:
        await message.answer("Please provide a valid app_id, market name and amount!")
        return

    app_id = match.group(1)
    market_name = match.group(2)
    amount = Decimal(str(match.group(3)))

    if amount == 0:
        await message.answer("Amount cannot be zero!")
        return

    async with AsyncSessionLocal() as session:
        user = await session.get(User, message.from_user.id)
        if not user:
            await message.answer(f"Sorry, to use this command, you need to first register(/register).")
            return
        async with httpx.AsyncClient() as client:
            try:
                url = f"{API_BASE_URL}/steam/{app_id}/{market_name}"
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
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
                    asset.buy_price = (asset.quantity * asset.buy_price + amount * price) / 2
                    asset.quantity += amount
                else:
                    session.add(portfolio)

                await session.commit()

                await message.answer(f"Added {amount} {market_name} at {html.bold(price)}$")
            except (httpx.HTTPError, KeyError, ValueError) as e:
                logger.error(f"Error adding Steam item {market_name}, app_id {app_id}: {e}")
                await message.answer(f"Failed to add Steam item {market_name}, app_id {app_id}")