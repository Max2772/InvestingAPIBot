import re
import httpx
from aiogram import html
from aiogram.filters import Command
from aiogram.types import Message
from src.common import dp, API_BASE_URL
from src.dao.models import AsyncSessionLocal, User

@dp.message(Command('stock'))
async def command_stock_handler(message: Message) -> None:
    arg = message.text.split()[1:]
    if not arg:
        await message.answer("Please provide a stock ticker, e.g., /stock AMD")
        return

    ticker = arg[0].upper()

    async with AsyncSessionLocal() as session:
        user = await session.get(User, message.from_user.id)
        if not user:
            await message.answer(f"Sorry, to use this command, you need to first register(/register).")
        else:
            async with httpx.AsyncClient() as client:
                try:
                    url = f"{API_BASE_URL}/stocks/{ticker}"
                    response = await client.get(url)
                    response.raise_for_status()
                    data = response.json()
                    await message.answer(f"Stock ticker {ticker}: {html.bold(data.get('price', 'X'))}$")
                except (httpx.HTTPError, KeyError, ValueError) as e:
                    await message.answer(f"Failed to fetch stock {ticker}")

@dp.message(Command('crypto'))
async def command_crypto_handler(message: Message) -> None:
    arg = message.text.split()[1:]
    if not arg:
        await message.answer("Please provide the crypto's fullname or abbreviation, e.g., /crypto Bitcoin, /crypto BTC")
        return

    coin = arg[0].upper()

    async with AsyncSessionLocal() as session:
        user = await session.get(User, message.from_user.id)
        if not user:
            await message.answer(f"Sorry, to use this command, you need to first register(/register).")
        else:
            async with httpx.AsyncClient() as client:
                try:
                    url = f"{API_BASE_URL}/crypto/{coin}"
                    response = await client.get(url)
                    response.raise_for_status()
                    data = response.json()
                    await message.answer(f"Coin {coin}: {html.bold(data.get('price', 'X'))}$")
                except (httpx.HTTPError, KeyError, ValueError) as e:

                    await message.answer(f"Failed to fetch crypto {coin}")

@dp.message(Command('steam'))
async def command_steam_handler(message: Message) -> None:
    pattern = re.compile(r"^/steam\s+(\d+)\s+(.+)$")
    match = pattern.match(message.text.strip())
    if not match:
        await message.answer("Please provide a valid app_id and steam market name!")
        return

    app_id = match.group(1)
    market_name = match.group(2)

    async with AsyncSessionLocal() as session:
        user = await session.get(User, message.from_user.id)
        if not user:
            await message.answer(f"Sorry, to use this command, you need to first register(/register).")
        else:
            async with httpx.AsyncClient() as client:
                try:
                    url = f"{API_BASE_URL}/steam/{app_id}/{market_name}"
                    response = await client.get(url)
                    response.raise_for_status()
                    data = response.json()
                    price = data.get('price', 0.0)
                    await message.answer(f"Steam game: {app_id}, Steam item {market_name}: {html.bold(price)}$")
                except (httpx.HTTPError, KeyError, ValueError) as e:
                    await message.answer(f"Failed to fetch steam item {market_name} from {app_id}")

