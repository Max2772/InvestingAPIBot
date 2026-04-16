from decimal import Decimal
from html import escape
from urllib.parse import unquote

from src.dao.models import Portfolio
from src.types.response_enums import AssetType


def get_asset_name(
        raw_name: str,
        asset_type: AssetType
) -> str:
    return (
        unquote(raw_name)
        if asset_type == AssetType.STEAM
        else raw_name.upper()
    )


def format_growth(value: Decimal) -> str:
    sign = "+" if value > 0 else ""
    emoji = " 📈" if value > 0 else " 📉" if value < 0 else ""
    return f"{sign}{value:.2f}%{emoji}"


def loading_bar_text(
        step: int,
        total_steps: int
) -> str:
    percent = int(step / total_steps * 100)
    bar = "█" * (percent // 10) + "░" * (10 - percent // 10)
    return f"Loading {percent}%\n[{bar}]"


def total_portfolio_stats(
        total_old_value: Decimal,
        total_new_value: Decimal
) -> str:
    total_growth_change = (
        ((total_new_value - total_old_value) / total_old_value) * 100
        if total_old_value != 0
        else Decimal("0")
    )

    separator = "◇───────────────────────────────────────────◇\n\n"
    stats = (
        f"<b>💰 Total value: ${total_new_value:.2f}</b>\n"
        f"<b>📊 Total growth: {format_growth(total_growth_change)}</b>"
    )

    return separator + stats


def portfolio_asset_format(
        portfolio: Portfolio,
        current_price: Decimal
) -> tuple[str, Decimal, Decimal]:
    buy_price = portfolio.buy_price
    quantity = portfolio.quantity

    old_value = buy_price * quantity
    new_value = current_price * quantity

    growth = ((current_price - buy_price) / buy_price) * 100 if buy_price else Decimal("0")
    quantity_formatted = format_quantity(quantity, portfolio.asset_type)

    text = (
        f"<b>{portfolio.asset_name}</b>: {quantity_formatted} "
        f"at avg. price ${buy_price:.2f}, now ${current_price:.2f}, "
        f"value ${new_value:.2f} ({format_growth(growth)})\n"
    )

    return text, old_value, new_value


def format_quantity(quantity: Decimal, asset_type: AssetType) -> str:
    if asset_type == AssetType.CRYPTO:
        s = str(quantity.quantize(Decimal("0.00000001"))).rstrip('0').rstrip('.')
        if '.' not in s:
            s += '.0'
        return s

    else:
        return str(quantity.quantize(Decimal("0.01")))


def format_alert_triggered(
        asset_name: str,
        app_id: int,
        price: Decimal,
        direction: str,
        target_price: Decimal
) -> str:
    asset = f"{asset_name}, app_id = {app_id}" if app_id else asset_name
    message = (
        f"<b>🔔 Alert Triggered!</b>\n"
        f"Asset: <b>{asset}</b>\n"
        f"Current price: <b>${price:.2f}</b>\n"
        f"Target: {escape(direction)} <b>${target_price:.2f}</b>"
    )

    return message


def get_plain_name(user) -> str:
    if user.username:
        return f"@{user.username}"
    else:
        full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
        return full_name if full_name else user.id
