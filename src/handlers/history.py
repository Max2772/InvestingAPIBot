import re
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.exc import SQLAlchemyError

from src.bot_init import dp
from src import (get_logger)
from src.dao.models import User


logger = get_logger()

HISTORY_SETTINGS = ['all', 'stocks', 'crypto', 'steam']

mode_titles = {
    'all': 'Your Portfolio History',
    'stock': 'Your Portfolio History (Stocks)',
    'crypto': 'Your Portfolio History (Crypto)',
    'steam': 'Your Portfolio History (Steam)',
}

@dp.message(Command('history'))
async def history_handler(message: Message, user: User) -> None:
    pattern = re.compile(r"^/history\s+(all|stocks|crypto|steam)$")
    match = pattern.match(message.text.strip())
    if not match:
        await message.answer("Please provide a parameter, e.g., /history all")
        return

    mode = match.group(1) if match and match.group(1) in HISTORY_SETTINGS else 'all'
    if mode == 'stocks':
        mode = 'stock'

    if not user.portfolios:
        await message.answer(f"Sorry, there is no history for this account.")
        return

    stock_text = "<b>🗠  Stocks</b>\n"
    crypto_text = "<b>₿  Crypto</b>\n"
    steam_text = "<b>🎮  Steam Items</b>\n"

    try:
        history_text = "<b>📜 Portfolio History</b>\n\n"
        for portfolio in user.portfolios:
            if portfolio.asset_type == mode or mode == 'all':
                asset_text = (f"Added {portfolio.quantity if portfolio.asset_type == 'crypto' else portfolio.quantity:.2f} {portfolio.asset_name}"
                              f" at {portfolio.purchase_date.strftime('%y-%m-%d %H:%M:%S')}\n")

                if portfolio.asset_type == 'stock':
                    stock_text += asset_text
                elif portfolio.asset_type == 'crypto':
                    crypto_text += asset_text
                elif portfolio.asset_type == 'steam':
                    steam_text += asset_text

        if mode == 'stock':
            history_text += stock_text + '\n'
        elif mode == 'crypto':
            history_text += crypto_text + '\n'
        elif mode == 'steam':
            history_text += steam_text + '\n'
        else:
            history_text += stock_text + '\n' + crypto_text + '\n' + steam_text + '\n'

        await message.answer(history_text)

    except SQLAlchemyError as e:
        logger.error(f"Database error while retrieving history: {e}")
        await message.answer(f"Failed to retrieve history due to database error.")
    except Exception as e:
        logger.error(f"Failed to retrieve history: {e}")
        await message.answer(f"Failed to retrieve history.")