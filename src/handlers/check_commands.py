import re
from urllib.parse import unquote
import aiohttp
from aiogram import html
from aiogram.filters import Command
from aiogram.types import Message

from src.bot_init import dp
from src import (get_logger, get_api_url, fetch_api_data)


logger = get_logger()

@dp.message(Command('check_stock'))
async def check_stock_handler(message: Message):
    pattern = re.compile(r"^/check_stock\s+(.+)$")
    match = pattern.match(message.text.strip())
    if not match:
        await message.answer("Please provide a stock ticker, e.g., /stock AMD")
        return

    ticker = match.group(1).upper()

    try:
        url = get_api_url('stock', ticker)
        async with aiohttp.ClientSession() as client:
            data = await fetch_api_data(client, url, message)
            if data is None:
                return

            await message.answer(f"Stock ticker {ticker}: ${html.bold(data.get('price', 0.0))}")
    except Exception as e:
                logger.error(f"Failed to check stock {ticker}: {e}")
                await message.answer(f"Failed to check stock {ticker}")

@dp.message(Command('check_crypto'))
async def check_crypto_handler(message: Message):
    pattern = re.compile(r"^/check_crypto\s+(.+)$")
    match = pattern.match(message.text.strip())
    if not match:
        await message.answer("Please provide a coin name, e.g., /crypto BTC, /crypto Solana")
        return

    coin = match.group(1)

    try:
        url = get_api_url('crypto', coin)
        async with aiohttp.ClientSession() as client:
            data = await fetch_api_data(client, url, message)
            if data is None:
                return

            await message.answer(f"Coin {coin}: ${html.bold(data.get('price', 0.0))}")
    except Exception as e:
                logger.error(f"Failed to check crypto {coin}: {e}")
                await message.answer(f"Failed to check crypto {coin}")

@dp.message(Command('check_steam'))
async def check_steam_handler(message: Message):
    pattern = re.compile(r"^/check_steam\s+(\d+)\s+(.+)$")
    match = pattern.match(message.text.strip())
    if not match:
        await message.answer("Please provide a valid app_id and Steam market name!")
        return

    app_id = int(match.group(1))
    market_name = unquote(match.group(2))

    try:
        url = get_api_url('steam', market_name, app_id)
        async with aiohttp.ClientSession() as client:
            data = await fetch_api_data(client, url, message)
            if data is None:
                return

            await message.answer(f"Steam item: {market_name}\napp_id: {app_id}\nPrice: ${html.bold(data.get('price', 0.0))}")
    except Exception as e:
        logger.error(f"Failed to check Steam item {market_name}, app_id {app_id}: {e}")
        await message.answer(f"Failed to check Steam item {market_name} from {app_id}")