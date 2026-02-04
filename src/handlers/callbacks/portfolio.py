import asyncio

from aiogram import Router
from aiogram.types import CallbackQuery

from src.logger import logger
from src.types.dto.portfolio_cb import PortfolioCb
from src.types.response_enums import AssetType
from src.types.system_types import LocalUser
from src.utils.handler_utils.portfolio_utils import build_portfolio_text
from src.utils.tg_utils import cq_answer, edit_content

PORTFOLIO_CB_ROUTER = Router()

@PORTFOLIO_CB_ROUTER.callback_query(PortfolioCb.filter())
async def portfolio_cb_handler(cq: CallbackQuery, callback_data: PortfolioCb, user: LocalUser):
    try:
        mode = callback_data.asset_type

        portfolio_text = await build_portfolio_text(
            user,
            mode,
            cq.message
        )

        if not portfolio_text:
            portfolio_name = f" {mode.value}" if mode != AssetType.ALL else ""
            empty_text = (
                f"Your<b>{portfolio_name}</b> portfolio is empty.\n"
                f"Add assets with /add command to add them to your portfolio."
            )
            await asyncio.gather(
                cq_answer(cq),
                edit_content(
                    cq.message,
                    empty_text
                )
            )
        else:
            await asyncio.gather(
                cq_answer(cq),
                edit_content(
                    cq.message,
                    portfolio_text
                )
            )
    except Exception as e:
        logger.error(f"Failed to check portfolio: {e}")
        await cq.answer(f"Failed to check portfolio due to error.")