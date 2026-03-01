from decimal import Decimal

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.logger import logger
from src.regex.remove_patterns import remove_asset_re
from src.types.response_enums import RemoveAssetResult, AssetType
from src.types.system_types import LocalUser
from src.utils.api_utils import get_unique_asset_name
from src.utils.db_utils import remove_asset
from src.utils.formatters import get_asset_name

REMOVE_ASSET_CMD_ROUTER = Router()

@REMOVE_ASSET_CMD_ROUTER.message(Command("remove"))
async def remove_cmd_handler(message: Message, user: LocalUser):
    match = remove_asset_re.match(message.text.strip())
    if not match:
        await message.answer("Please provide a valid asset and amount, e.g. <code>/remove stock AMD 10</code>")
        return

    asset_type: AssetType = AssetType(match.group(1).lower())
    app_id = int(match.group(2)) if match.group(2) else None
    asset_name = get_asset_name(match.group(3), asset_type)
    amount = Decimal(match.group(4)) if match.group(4) is not None else None

    if amount and amount <= 0:
        await message.answer("Amount must be positive!")
        return

    if app_id and app_id <= 0:
        await message.answer("App Id must be positive!")
        return

    unique_asset_name: str = await get_unique_asset_name(
        asset_type,
        asset_name,
        app_id
    )

    if unique_asset_name is None:
        await message.answer(f"Sorry, <b>{asset_name}</b> doesn't exist.")
        return


    try:
        result: RemoveAssetResult = await remove_asset(
            user.telegram_id,
            asset_type,
            unique_asset_name,
            amount,
            app_id
        )

        if result == RemoveAssetResult.ASSET_NOT_FOUND:
            await message.answer(f"Sorry, you don't have <b>{asset_name}</b> in your portfolio.")
            return
        elif result == RemoveAssetResult.NOT_ENOUGH:
            await message.answer(
                f"Sorry, you don't have <b>{amount} {asset_name}</b> in your portfolio."
            )
            return
        else:
            amount_text = f" {amount}" if amount else ""
            await message.answer(f"Removed<b>{amount_text} {unique_asset_name}</b> from portfolio.")

    except Exception as e:
        logger.error(f"Failed to remove {asset_name}: {e}")
        await message.answer(f"Failed to remove {asset_name}.")
