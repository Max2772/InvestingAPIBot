from aiogram.types import Message
from src.common import dp
from src.utils import get_logger

logger = get_logger()

@dp.message()
async def echo_handler(message: Message) -> None:
    try:
        await message.send_copy(chat_id=message.chat.id)
    except TypeError as e:
        logger.error(f"Error echo: {e}")
        await message.answer("Nice try!")
