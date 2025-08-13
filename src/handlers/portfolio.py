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

            async with httpx.AsyncClient() as client:
                for portfolio in user.portfolios:
                    buy_price = portfolio.buy_price
                    asset_type = portfolio.asset_type
                    asset_name = portfolio.asset_name
                    response = await client.get(f"{API_BASE_URL}/{asset_type}/{asset_name}")
                    response.raise_for_status()
                    data = response.json()
                    current_price = Decimal(str(data.get('price', 0)))
                    total_old_value += buy_price * portfolio.quantity
                    total_current_value += current_price * portfolio.quantity
                    growth = ((current_price - buy_price ) / buy_price) * 100

                    emoji = "📈" if growth and growth > 0 else "📉"
                    asset_text = (f"<b> {emoji} {asset_type}:{asset_name}</b>\n"
                                  f"Buy: {portfolio.quantity:.2f} at avg ${buy_price} on {portfolio.purchase_date.strftime('%Y-%m-%d')}\n"
                                  f"Current: ${current_price}, growth: {growth:.2f}%\n\n")
                    portfolio_text += asset_text

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
