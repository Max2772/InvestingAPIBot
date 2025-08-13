from decimal import Decimal
import httpx
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.exc import SQLAlchemyError
from src.common import dp
from src.dao.models import AsyncSessionLocal, User
from src.utils import get_logger
from src.common import API_BASE_URL

logger = get_logger()

@dp.message(Command('portfolio'))
async def portfolio_handler(message: Message) -> None:
    async with (AsyncSessionLocal() as session):
        try:
            user = await session.get(User, message.from_user.id)
            if not user:
                await message.answer(f"Sorry, to use this command, you need to first register(/register).")
                return

            if not user.portfolios:
                await message.answer("Your portfolio is empty. Add assets with /add_stock, /add_crypto, or /add_steam.")
                return

            portfolio_text = "<b>📊 Your Portfolio</b>\n\n"
            total_old_value = Decimal(0)
            total_current_value = Decimal(0)

            total_stock_invested = Decimal(0)
            total_stock_profit = Decimal(0)
            total_crypto_invested = Decimal(0)
            total_crypto_profit = Decimal(0)
            total_steam_invested = Decimal(0)
            total_steam_profit = Decimal(0)

            stock_text = "<b>🗠  Stocks</b>\n"
            crypto_text = "<b>₿  Crypto</b>\n"
            steam_text = "<b>🎮  Steam Items</b>\n"

            sort_order = {"stock": 1, "crypto": 2, "steam": 3}
            portfolios_sorted = sorted(user.portfolios, key=lambda p: sort_order.get(p.asset_type, 99))

            async with httpx.AsyncClient() as client:
                for portfolio in portfolios_sorted:
                    buy_price = portfolio.buy_price
                    asset_type = portfolio.asset_type
                    asset_name = portfolio.asset_name
                    app_id = portfolio.app_id

                    url = f"{API_BASE_URL}/{asset_type}/{asset_name}" if app_id is None else f"{API_BASE_URL}/{asset_type}/{app_id}/{asset_name}"
                    response = await client.get(url)
                    response.raise_for_status()
                    data = response.json()
                    current_price = Decimal(str(data.get('price', 0)))
                    total_old_value += buy_price * portfolio.quantity
                    total_current_value += current_price * portfolio.quantity
                    growth = ((current_price - buy_price ) / buy_price) * 100

                    emoji = "📈" if growth > 0 else "📉" if growth < 0 else ''
                    growth_sign = '+' if growth > 0 else ''
                    asset_text = f"<b>{asset_name}</b>: {portfolio.quantity:.2f} at avg. price ${buy_price}, now ${current_price}, value ${buy_price * portfolio.quantity:.2f} ({growth_sign}{growth:.2f}% {emoji})\n"

                    if asset_type == 'stock':
                        stock_text += asset_text
                    elif asset_type == 'crypto':
                        crypto_text += asset_text
                    else:
                        steam_text += asset_text

            portfolio_text += stock_text + '\n' + crypto_text + '\n' + steam_text + '\n'

            total_percent_change = ((total_current_value - total_old_value) / total_old_value) * 100
            portfolio_text += (f"<b>💰 Total portfolio value: ${total_current_value:.2f}</b>\n"
                               f"<b>📊 Total portfolio growth: {total_percent_change:+.2f}% {'📈' if total_percent_change > 0 else '📉'}</b>")

            await message.answer(portfolio_text, parse_mode=ParseMode.HTML)

        except SQLAlchemyError as e:
            logger.error(f"Database error while checking portfolio: {e}")
            await message.answer(f"Failed to check portfolio due to database error.")
        except Exception as e:
            logger.error(f"Failed to check portfolio: {e}")
            await message.answer(f"Failed to check portfolio due to error.")
