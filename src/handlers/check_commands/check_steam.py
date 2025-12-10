import re
from urllib.parse import unquote

import aiohttp
from aiogram import Router, html
from aiogram.filters import Command
from aiogram.types import Message

from src.utils import get_logger, get_api_url, fetch_api_data

logger = get_logger()

router = Router()

@router.message(Command('check_steam'))
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