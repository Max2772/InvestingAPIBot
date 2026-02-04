from typing import List

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.dao.models import History, DbUser
from src.logger import logger
from src.regex.history_patterns import history_re
from src.types.response_enums import AssetType, HistoryOperation
from src.types.system_types import LocalUser
from src.utils.db_utils import get_user

HISTORY_CMD_ROUTER = Router()


@HISTORY_CMD_ROUTER.message(Command("history"))
async def history_cmd_handler(message: Message, user: LocalUser):
    match = history_re.match(message.text.strip())
    if not match:
        await message.answer("Please provide a valid format, e.g., <code>/history all</code>")
        return

    mode = AssetType(match.group(1))

    user: DbUser = await get_user(user.telegram_id)

    histories: List[History] = [
        h for h in user.history
        if mode == AssetType.ALL or h.asset_type == mode
    ]

    if not histories:
        history_name = mode
        await message.answer(f"No history found for {history_name.value}!")
        return

    history_text = "<b>📜 Portfolio History</b>\n\n"

    try:
        for history in user.history:
            if history.asset_type == mode or mode == AssetType.ALL:
                if history.operation == HistoryOperation.ADD:
                    history_text += (
                        f"Added <code>{history.quantity if history.asset_type == AssetType.CRYPTO else history.quantity:.2f} {history.asset_name}</code>"
                        f" at <b>{history.purchase_date.strftime('%y-%m-%d %H:%M:%S')}</b>\n"
                    )
                else:
                    history_text += (
                        f"Removed <code>{history.quantity if history.asset_type == AssetType.CRYPTO else history.quantity:.2f} {history.asset_name}</code>"
                        f" at <b>{history.purchase_date.strftime('%y-%m-%d %H:%M:%S')}</b>\n"
                    )


        await message.answer(history_text)

    except Exception as e:
        logger.error(f"Failed to retrieve history: {e}")
        await message.answer(f"Failed to retrieve history.")