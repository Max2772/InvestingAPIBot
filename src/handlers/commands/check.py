from decimal import Decimal
from urllib.parse import unquote

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.logger import logger
from src.regex.check_patterns import check_asset_re
from src.types.response_enums import AssetType
from src.utils.api_utils import get_latest_price

CHECK_ASSET_CMD_ROUTER = Router()

@CHECK_ASSET_CMD_ROUTER.message(Command("check"))
async def check_cmd_handler(message: Message):
    match = check_asset_re.match(message.text.strip())
    if not match:
        await message.answer("Please provide a valid format, e.g., <code>/stock AMD</code>")
        return

    asset_type: AssetType = AssetType(match.group(1).lower())
    app_id = int(match.group(2)) if match.group(2) else None
    asset_name = (
        unquote(match.group(3))
        if asset_type == AssetType.STEAM
        else match.group(3).upper()
    )

    try:
        price: Decimal = await get_latest_price(
            asset_type,
            asset_name,
            app_id
        )

        if price is None:
            await message.answer(f"Sorry, asset <b>{asset_name}</b> doesn't exist.")
            return

        await message.answer(f"{asset_type.value.capitalize()} {asset_name}: <b>${price}</b>")
    except Exception as e:
        logger.error(f"Failed to check {asset_name}: {e}")
        await message.answer(f"Failed to check {asset_name}")
