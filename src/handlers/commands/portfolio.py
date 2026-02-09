from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.logger import logger
from src.regex.portfolio_patterns import portfolio_re
from src.types.response_enums import AssetType
from src.types.system_types import LocalUser
from src.utils.handler_utils.portfolio_utils import build_portfolio_text

PORTFOLIO_CMD_ROUTER = Router()


@PORTFOLIO_CMD_ROUTER.message(Command("portfolio"))
async def portfolio_cmd_handler(message: Message, user: LocalUser):
    try:
        match = portfolio_re.match(message.text.strip())
        if not match:
            await message.answer("Please provide a valid parameter, e.g., <code>/portfolio all</code>")
            return

        mode = AssetType(match.group(1))

        portfolio_text = await build_portfolio_text(
            user,
            mode
        )

        if not portfolio_text:
            portfolio_name = f" {mode.value}" if mode != AssetType.ALL else ""
            await message.answer(
                f"Your<b>{portfolio_name}</b> portfolio is empty.\n"
                f"Add assets with /add command to add them to your portfolio."
            )
        else:
            await message.answer(portfolio_text)
    except Exception as e:
        logger.error(f"Failed to check portfolio: {e}")
        await message.answer(f"Failed to check portfolio due to error.")
