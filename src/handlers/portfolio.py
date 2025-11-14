import re
from decimal import Decimal

import aiohttp
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError

from src.dao.models import AsyncSessionLocal, User, Portfolio
from src.configuration.bot_init import dp
from src.utils import get_api_url, get_logger, profit_emoji, profit_sign, fetch_api_data


logger = get_logger()

PORTFOLIO_SETTINGS = ['all', 'stocks', 'crypto', 'steam']

MODE_TITLES = {
    'all': 'Your Portfolio',
    'stock': 'Your Portfolio (Stocks)',
    'crypto': 'Your Portfolio (Crypto)',
    'steam': 'Your Portfolio (Steam)',
}

@dp.message(Command('portfolio'))
async def portfolio_handler(message: Message, user: User):
    pattern = re.compile(r"^/portfolio\s+(all|stocks|crypto|steam)$")
    match = re.match(pattern, message.text.strip())
    if not match:
        await message.answer("Please provide a parameter, e.g., /portfolio all")
        return

    mode = match.group(1) if match and match.group(1) in PORTFOLIO_SETTINGS else 'all'
    if mode == 'stocks':
        mode = 'stock'

    async with AsyncSessionLocal() as session:
        try:
            if not user.portfolios:
                await message.answer("Your portfolio is empty. Add assets with /add_stock, /add_crypto, or /add_steam.")
                return

            portfolio_text = f"<b>📊 {MODE_TITLES[mode]}</b>\n\n"
            stock_text = "<b>🏛️  Stocks</b>\n"
            crypto_text = "<b>₿  Crypto</b>\n"
            steam_text = "<b>🎮  Steam Items</b>\n"

            total_old_value = Decimal('0')
            total_current_value = Decimal('0')

            result = await session.execute(
                select(func.count()).where(Portfolio.user_id == user.telegram_id) # NoQa
            )
            total_steps = result.scalar() or 0
            step = 1
            loading_message = await message.answer('Loading 0%')

            async with aiohttp.ClientSession() as client:
                for portfolio in user.portfolios:
                    if portfolio.asset_type == mode or mode == 'all':
                        buy_price = Decimal(str(portfolio.buy_price))
                        quantity = Decimal(str(portfolio.quantity))
                        asset_type = portfolio.asset_type
                        asset_name = portfolio.asset_name
                        app_id = portfolio.app_id

                        try:
                            url = get_api_url(asset_type, asset_name, app_id)
                            data = await fetch_api_data(client, url, message)
                            if data is None:
                                continue

                            current_price = Decimal(str(data.get('price', 0.0)))
                            if current_price == 0:
                                logger.warning(f"No valid price for {asset_type}:{asset_name}")
                                continue
                        except Exception as e:
                            logger.error(f"Error fetching price for {asset_type}:{asset_name}: {e}")
                            await message.answer(f"Failed to fetch price for {asset_name}.")
                            continue

                        total_old_value += buy_price * quantity
                        total_current_value += current_price * quantity
                        growth = ((current_price - buy_price) / buy_price) * 100 if buy_price != 0 else Decimal('0')

                        asset_quantity = portfolio.quantity.quantize(Decimal('0.01')) if portfolio.asset_type != "crypto" else portfolio.quantity.normalize()
                        asset_text = (f"<b>{asset_name}</b>: {asset_quantity} at avg. price ${buy_price:.2f},"
                                      f" now ${current_price:.2f}, value ${buy_price * portfolio.quantity:.2f}"
                                      f" ({profit_sign(growth)}{growth:.2f}%{profit_emoji(growth)})\n")

                        if asset_type == 'stock':
                            stock_text += asset_text
                        elif asset_type == 'crypto':
                            crypto_text += asset_text
                        elif asset_type == 'steam':
                            steam_text += asset_text

                    percent = int(step / total_steps * 100)
                    bar = '█' * (percent // 10) + '░' * (10 - percent // 10)
                    await loading_message.edit_text(f"Loading {percent}%\n[{bar}]")
                    step += 1
            await loading_message.delete()

            if mode == 'stock':
                portfolio_text += stock_text + '\n'
            elif mode == 'crypto':
                portfolio_text += crypto_text + '\n'
            elif mode == 'steam':
                portfolio_text += steam_text + '\n'
            else:
                portfolio_text += stock_text + '\n' + crypto_text + '\n' + steam_text + '\n'

            total_percent_change = ((total_current_value - total_old_value) / total_old_value) * 100 if total_old_value != 0 else Decimal('0')
            portfolio_text += ("◇───────────────────────────────────────────◇\n\n"
                               f"<b>💰 Total value: ${total_current_value:.2f}</b>\n"
                               f"<b>📊 Total growth: {total_percent_change:+.2f}%{profit_emoji(total_percent_change)}</b>")
            await message.answer(portfolio_text, parse_mode=ParseMode.HTML)

        except SQLAlchemyError as e:
            logger.error(f"Database error while checking portfolio: {e}")
            await message.answer(f"Failed to check portfolio due to database error.")
        except Exception as e:
            logger.error(f"Failed to check portfolio: {e}")
            await message.answer(f"Failed to check portfolio due to error.")
