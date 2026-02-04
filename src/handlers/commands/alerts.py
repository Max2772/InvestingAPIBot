from decimal import Decimal
from html import escape

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.dao.models import DbUser
from src.env import MAXIMUM_ALERTS
from src.logger import logger
from src.regex.alert_patterns import delete_alert_re, set_alert_re
from src.types.response_enums import AssetType, AlertAddResult
from src.types.system_types import LocalUser
from src.utils.db_utils import delete_alert, add_alert, get_user, no_active_alerts
from src.utils.formatters import get_asset_name

ALERTS_CMD_ROUTER = Router()


@ALERTS_CMD_ROUTER.message(Command("alerts"))
async def alerts_cmd_handler(message: Message, user: LocalUser):
    try:
        user: DbUser = await get_user(user.telegram_id)
        if await no_active_alerts(user):
            await message.answer("You have no active alerts.")
            return

        lines = []
        for alert in user.alerts:
            if not alert.active:
                continue
                
            asset = (
                f"{alert.asset_name}, app_id={alert.app_id}"
                if alert.app_id
                else f"{alert.asset_name}"
            )

            lines.append(
                f"<b>#{alert.id}</b>: {asset}, target {escape(alert.direction)} <b>${alert.target_price:.2f}</b>"
            )

        alert_text = "<b>📢 Your Alerts</b>\n\n" + "\n".join(lines)
        await message.answer(alert_text)
    except Exception as e:
        logger.error(f"Failed to list alerts: {e}")
        await message.answer(f"Failed to list alerts due to error.")




@ALERTS_CMD_ROUTER.message(Command("delete_alert"))
async def delete_alert_cmd_handler(message: Message, user: LocalUser):
    match = delete_alert_re.match(message.text.strip())
    if not match:
        await message.answer("Please provide a valid alert id, e.g. <code>/delete_alert 7</code>")
        return

    alert_id = int(match.group(1))
    try:
        successful: bool = await delete_alert(
            user.telegram_id,
            alert_id
        )

        if not successful:
            await message.answer(f"Alert <b>#{alert_id}</b> does not exist.")
            return

        await message.answer(f"🔔 Alert <b>#{alert_id}</b> deleted successfully.")
    except Exception as e:
        logger.error(f"Failed to delete alert #{alert_id}: {e}")
        await message.answer(f"Failed to delete alert #{alert_id}.")



@ALERTS_CMD_ROUTER.message(Command("set_alert"))
async def set_alert_cmd_handler(message: Message, user: LocalUser):
    match = set_alert_re.match(message.text.strip())
    if not match:
        await message.answer("❌ Invalid format. Use /help to see how to write this command.")
        return

    asset_type: AssetType = AssetType(match.group(1).lower())
    app_id = int(match.group(2)) if match.group(2) else None
    asset_name = get_asset_name(match.group(3), asset_type)
    direction = match.group(4)
    price = Decimal(match.group(5))

    if price <= 0:
        await message.answer("Target price must be positive!")
        return

    try:
        alert_result: AlertAddResult = await add_alert(
            user.telegram_id,
            asset_type,
            asset_name,
            price,
            direction,
            app_id
        )
        if alert_result == AlertAddResult.LIMIT_REACHED:
            await message.answer(
                f"You have reached the maximum number of alerts <b>({MAXIMUM_ALERTS})</b>. Delete some alerts first."
            )
            return
        elif alert_result == AlertAddResult.ASSET_NOT_FOUND:
            await message.answer(f"Asset <b>{asset_name}</b> doesn't exists!")
            return
        elif alert_result == AlertAddResult.SUCCESS:
            await message.answer(
                f"🔔 Alert created for <b>{asset_name}</b> ({asset_type.value}) "
                f"with target {escape(direction)} <b>${price:.2f}.</b>")
    except Exception as e:
        logger.error(f"Error adding alert: {e}")
        await message.answer("Failed to add alert due to error.")