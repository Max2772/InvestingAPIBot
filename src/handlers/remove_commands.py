import re
from decimal import Decimal
from urllib.parse import unquote
import aiohttp
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import select, and_
from sqlalchemy.exc import SQLAlchemyError

from src.dao.models import AsyncSessionLocal, User, Portfolio
from src.bot_init import dp
from src import (get_api_url, get_logger, fetch_api_data)


logger = get_logger()

@dp.message(Command('remove_stock'))
async def remove_stock_handler(message: Message, user: User):
    pattern = re.compile(r"^/remove_stock\s+(.+)\s+(\d+(\.\d+)?|\d+(\.\d+)?[eE][+-]\d+)$")
    match = pattern.match(message.text.strip())
    if not match:
        await message.answer("Please provide a valid ticker and amount!")
        return

    ticker = match.group(1).upper()
    amount = Decimal(str(match.group(2)))

    if amount <= 0:
        await message.answer('Amount must be positive!')
        return

    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(
                select(Portfolio).where(
                and_(
                    Portfolio.user_id == user.telegram_id,
                    Portfolio.asset_type == 'stock',
                    Portfolio.asset_name == ticker
                    )
                )
            )
            asset = result.scalar_one_or_none()

            if not asset:
                await message.answer(f"Sorry, you don't have {ticker} in your portfolio.")
                return

            if asset.quantity < amount:
                await message.answer(f"Sorry, you don't have {amount} of {ticker} in your portfolio.\nCurrent amount {asset.quantity:.2f}")
                return
            elif asset.quantity == amount:
                await session.delete(asset)
            else:
                asset.quantity -= amount
            await session.commit()

            await message.answer(f"Removed {amount} {ticker} from portfolio")
        except SQLAlchemyError as e:
            logger.error(f"Database error while removing stock {ticker}: {e}")
            await message.answer(f"Failed to remove stock {ticker} due to database error.")
        except Exception as e:
            logger.error(f"Failed to remove stock {ticker}: {e}")
            await message.answer(f"Failed to remove stock {ticker}.")

@dp.message(Command('remove_crypto'))
async def remove_crypto_handler(message: Message, user: User):
    pattern = re.compile(r"^/remove_crypto\s+(.+)\s+(\d+(\.\d+)?|\d+(\.\d+)?[eE][+-]\d+)$")
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

                name = str(data.get('name', coin))

                result = await session.execute(
                    select(Portfolio).where(
                    and_(
                        Portfolio.user_id == user.telegram_id,
                        Portfolio.asset_type == 'crypto',
                        Portfolio.asset_name == name
                        )
                    )
                )
                asset = result.scalar_one_or_none()

                if not asset:
                    await message.answer(f"Sorry, you don't have {coin} in your portfolio.")
                    return

                if asset.quantity < amount:
                    await message.answer(f"Sorry, you don't have {amount} of {coin} in your portfolio.\nCurrent amount {asset.quantity}")
                    return
                elif asset.quantity == amount:
                    await session.delete(asset)
                else:
                    asset.quantity -= amount

                await session.commit()
                await message.answer(f"Removed {amount} {coin} from portfolio")
    except SQLAlchemyError as e:
        logger.error(f"Database error while removing crypto {coin}: {e}")
        await message.answer(f"Failed to remove crypto {coin} due to database error.")
    except Exception as e:
        logger.error(f"Failed to remove crypto {coin}: {e}")
        await message.answer(f"Failed to remove crypto {coin}.")

@dp.message(Command('remove_steam'))
async def remove_steam_handler(message: Message, user: User):
    pattern = re.compile(r"^/remove_steam\s+(\d+)\s+(.+)\s+(\d+)$")
    match = pattern.match(message.text.strip())
    if not match:
        await message.answer("Please provide a valid app_id, market_name and amount!")
        return

    app_id = int(match.group(1))
    market_name = unquote(match.group(2))
    amount = Decimal(str(match.group(3)))

    if amount <= 0:
        await message.answer('Amount must be positive!')
        return

    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(
                select(Portfolio).where(
                    and_
                        (
                        Portfolio.user_id == user.telegram_id,
                        Portfolio.asset_type == 'steam',
                        Portfolio.asset_name == market_name,
                        Portfolio.app_id == app_id
                        )
                )
            )
            asset = result.scalar_one_or_none()

            if not asset:
                await message.answer(f"Sorry, you don't have {market_name} in your portfolio.")
                return

            if asset.quantity < amount:
                await message.answer(f"Sorry, you don't have {amount} of {market_name} in your portfolio.\nCurrent amount {asset.quantity:2f}")
                return
            elif asset.quantity == amount:
                await session.delete(asset)
            else:
                asset.quantity -= amount

            await session.commit()

            await message.answer(f"Removed {amount} {market_name} from portfolio")
        except SQLAlchemyError as e:
            logger.error(f"Database error while removing Steam item {market_name}: {e}")
            await message.answer(f"Failed to remove Steam item {market_name} due to database error.")
        except Exception as e:
            logger.error(f"Failed to remove Steam item {market_name}: {e}")
            await message.answer(f"Failed to remove Steam item {market_name}.")