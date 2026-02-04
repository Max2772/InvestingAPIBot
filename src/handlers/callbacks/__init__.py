import asyncio

from aiogram import Router
from aiogram.types import CallbackQuery

from src.handlers.callbacks.help import HELP_CB_ROUTER
from src.handlers.callbacks.portfolio import PORTFOLIO_CB_ROUTER
from src.utils.menu_utils import open_main_menu
from src.utils.tg_utils import cq_answer


CB_ROUTER = Router()
CB_ROUTER.include_routers(
    HELP_CB_ROUTER,
    PORTFOLIO_CB_ROUTER
)

FALLBACK_CB_ROUTER = Router()

BUTTON_NOT_FOUND: str = (
    "🤷‍♂️ Button outdated.\n"
    "Menu restarted.\n"
)

@FALLBACK_CB_ROUTER.callback_query()
async def unknown_callback_handler(cq: CallbackQuery):
    await asyncio.gather(
        open_main_menu(cq.message),
        cq_answer(cq, BUTTON_NOT_FOUND, show_alert=True)
    )

CB_ROUTER.include_router(FALLBACK_CB_ROUTER)
