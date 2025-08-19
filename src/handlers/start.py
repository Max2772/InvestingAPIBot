from aiogram.filters import Command
from aiogram.types import Message
from aiogram import html

from src.dao.models import AsyncSessionLocal, User
from src.bot_init import dp


@dp.message(Command('start', 'register'))
async def register_handler(message: Message):
    async with AsyncSessionLocal() as session:
        user = await session.get(User, message.from_user.id)
        if not user:
            user = User(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name
            )

            session.add(user)
            await session.commit()
            await message.answer(f"Welcome, you are registered, {html.bold(message.from_user.full_name)}!")
        else:
            await message.answer(f"Hello again, {html.bold(user.first_name)}!")
