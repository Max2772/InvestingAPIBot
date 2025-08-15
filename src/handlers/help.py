from aiogram.filters import Command
from aiogram.types import Message
from src.common import dp

@dp.message(Command('help'))
async def help_handler(message: Message) -> None:
    help_text = (
        "/start, /register - Register and start tracking\n"
        "/stock <ticker> - Get stock price\n"
        "/crypto <coin> - Get crypto price\n"
        "/steam <app_id> <market_name> - Get Steam item price\n"
        "/add_stock <ticker> <quantity> - Add stock to portfolio\n"
        "/add_crypto <coin> <quantity> - Add crypto to portfolio\n"
        "/add_steam <app_id> <market_name> <quantity> - Add Steam item to portfolio\n"
        "/remove_stock <ticker> <quantity> - Remove stock from portfolio\n"
        "/remove_crypto <coin> <quantity> - Remove crypto from portfolio\n"
        "/remove_steam <app_id> <market_name> <quantity> - Remove Steam item from portfolio\n"
        "/portfolio - View your portfolio\n"
    )
    await message.answer(help_text, parse_mode=None)