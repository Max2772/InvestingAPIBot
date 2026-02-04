from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.utils.handler_utils.help_utils import get_help_text

HELP_CMD_CMD_ROUTER = Router()

@HELP_CMD_CMD_ROUTER.message(Command("help"))
async def help_cmd_handler(message: Message):
    await message.answer(get_help_text())