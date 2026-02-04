from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.utils.menu_utils import open_main_menu

START_CMD_ROUTER = Router()

@START_CMD_ROUTER.message(Command("start"))
async def start_cmd_handler(message: Message):
    await open_main_menu(message)