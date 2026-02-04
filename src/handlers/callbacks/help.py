import asyncio

from aiogram import Router
from aiogram.types import CallbackQuery

from src.types.dto.help_cb import HelpCb
from src.utils.handler_utils.help_utils import get_help_text
from src.utils.tg_utils import cq_answer, edit_content

HELP_CB_ROUTER = Router()

@HELP_CB_ROUTER.callback_query(HelpCb.filter())
async def help_cb_handler(cq: CallbackQuery):
    help_text = get_help_text()
    await asyncio.gather(
        cq_answer(cq),
        edit_content(
            cq.message,
            help_text
        )
    )