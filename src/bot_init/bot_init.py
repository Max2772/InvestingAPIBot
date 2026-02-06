from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from src.bot_init.middlewares.UserRegMiddleware import UserRegMiddleware
from src.env import BOT_TOKEN
from src.handlers import HANDLERS_ROUTER

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

dp.update.middleware(UserRegMiddleware())

dp.include_router(HANDLERS_ROUTER)


async def set_bot_commands():
    commands = [
        BotCommand(command="start", description="Open main menu with portfolio overview"),
        BotCommand(command="help", description="Show help message with all commands"),
        BotCommand(command="check", description="Get current price of an asset"),
        BotCommand(command="add", description="Add an asset to your portfolio"),
        BotCommand(command="remove", description="Remove an asset from your portfolio"),
        BotCommand(command="portfolio", description="View your portfolio"),
        BotCommand(command="set_alert", description="Set a price alert"),
        BotCommand(command="alerts", description="Show all active alerts"),
        BotCommand(command="delete_alert", description="Delete a price alert by ID"),
        BotCommand(command="history", description="View the full log of additions/removals"),
    ]
    await bot.set_my_commands(commands)