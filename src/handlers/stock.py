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


