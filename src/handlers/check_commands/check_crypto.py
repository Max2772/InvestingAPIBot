import re

import aiohttp
from aiogram import Router, html
from aiogram.filters import Command
from aiogram.types import Message

from src.utils import get_logger, get_api_url, fetch_api_data

logger = get_logger()

router = Router()

@router.message(Command('check_crypto'))
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
