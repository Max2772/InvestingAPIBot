import re
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from src.common import dp
from src.dao.models import AsyncSessionLocal, User, Portfolio
from src.utils import get_logger

logger = get_logger()

@dp.message(Command('remove_stock'))
async def remove_stock_handler(message: Message) -> None:
    pattern = re.compile(r"^/remove_stock\s+(.+)\s+(\d+\.?\d*)$")
    match = pattern.match(message.text.strip())
    if not match:
        await message.answer("Please provide a valid ticker and amount!")
        return

    ticker = match.group(1).upper()
    amount = float(match.group(2))

    async with AsyncSessionLocal() as session:
        try:
            user = await session.get(User, message.from_user.id)
            if not user:
                await message.answer(f"Sorry, to use this command, you need to first register(/register).")
                return

            result = await session.execute(select(Portfolio).where(
                    Portfolio.user_id == user.telegram_id, # NoQa
                    Portfolio.asset_type == 'stock', # NoQa
                    Portfolio.asset_name == ticker # NoQa
                    )
            )
            asset = result.scalars().first()


            asset = asset.scalar_one_or_none()
            if not asset:
                await message.answer(f"No {ticker} found in your portfolio.")
                return

            if amount < asset.quantity:
                asset.quantity -= amount
            else:
                await session.delete(asset)

            await session.commit()
            await message.answer(f"Removed {amount} {ticker} from portfolio")
        except SQLAlchemyError as e:
            logger.error(f"Database error while removing stock {ticker}: {e}")
            await message.answer(f"Failed to remove stock {ticker} due to database error.")
        except Exception as e:
            logger.error(f"Failed to remove stock {ticker}: {e}")
            await message.answer(f"Failed to remove stock {ticker}.")