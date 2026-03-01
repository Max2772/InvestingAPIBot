from decimal import Decimal

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.logger import logger
from src.regex.add_patterns import add_asset_re
from src.types.response_enums import AssetType
from src.types.system_types import LocalUser
from src.utils.api_utils import get_unique_asset
from src.utils.db_utils import upsert_asset
from src.utils.formatters import get_asset_name
from src.utils.tg_utils import validate_amount_and_price

ADD_ASSET_CMD_ROUTER = Router()


@ADD_ASSET_CMD_ROUTER.message(Command("add"))
async def add_cmd_handler(message: Message, user: LocalUser):
    match = add_asset_re.match(message.text.strip())
    if not match:
        await message.answer("Please provide a valid format, e.g., <code>/add stock AMD 10</code>")
        return

    asset_type: AssetType = AssetType(match.group(1).lower())
    app_id = int(match.group(2)) if match.group(2) else None
    asset_name = get_asset_name(match.group(3), asset_type)

    amount = Decimal(match.group(4))
    parameter_price = Decimal(match.group(5)) if match.group(5) else None

    if not await validate_amount_and_price(message, amount, parameter_price):
        return

    if asset_type == AssetType.STEAM and not match.group(4).isdigit():
        await message.answer("Steam amount must be an integer.")
        return

    if app_id and app_id <= 0:
        await message.answer("App id must be positive!")
        return

    unique_asset_name, latest_price = await get_unique_asset(
        asset_type,
        asset_name,
        app_id
    )

    if unique_asset_name is None or latest_price is None:
        await message.answer(f"Sorry, <b>{asset_name}</b> doesn't exist.")
        return

    price: Decimal = parameter_price or latest_price

    try:
        await upsert_asset(
            user_id=user.telegram_id,
            asset_type=asset_type,
            asset_name=unique_asset_name,
            amount=amount,
            price=price,
            app_id=app_id
        )

        await message.answer(f"Added <b>{amount} {asset_name}</b> at <b>{price}$</b>")
    except Exception as e:
        logger.error(f"Error adding {asset_name}: {e}")
        await message.answer(f"Failed to add {asset_name}")
