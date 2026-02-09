import asyncio
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

from src.dao.models import Portfolio
from src.logger import logger
from src.types.labels import PORTFOLIO_MODE_TITLES, PORTFOLIO_SECTION_TITLES
from src.types.response_enums import AssetType
from src.types.system_types import LocalUser
from src.utils.api_utils import get_latest_price
from src.utils.db_utils import get_user
from src.utils.formatters import portfolio_asset_format, loading_bar_text, total_portfolio_stats


async def build_portfolio_text(
    local_user: LocalUser,
    mode: AssetType,
) -> Optional[str]:

    user = await get_user(local_user.telegram_id)

    portfolios: List[Portfolio] = [
        p for p in user.portfolios
        if mode == AssetType.ALL or p.asset_type == mode
    ]

    if not portfolios:
        return None

    text = f"<b>📊 {PORTFOLIO_MODE_TITLES[mode]}</b>\n\n"

    sections: Dict[AssetType, str] = {
        asset_type: f"<b>{title}</b>\n"
        for asset_type, title in PORTFOLIO_SECTION_TITLES.items()
    }

    total_old_value = total_new_value = Decimal("0")

    async def fetch_price(portfolio: Portfolio) -> Tuple[Portfolio, Optional[Decimal]]:
        try:
            price = await get_latest_price(
                portfolio.asset_type,
                portfolio.asset_name,
                portfolio.app_id
            )
            return portfolio, price
        except Exception as e:
            logger.error(f"Error fetching price for {portfolio.asset_name}: {e}")
            return portfolio, None

    portfolio_tasks = [fetch_price(p) for p in portfolios]
    results = await asyncio.gather(*portfolio_tasks)

    for portfolio, current_price in results:
        if current_price is None:
            continue

        asset_text, old_value, new_value = portfolio_asset_format(
            portfolio,
            current_price
        )
        sections[portfolio.asset_type] += asset_text
        total_old_value += old_value
        total_new_value += new_value

    if mode != AssetType.ALL:
        text += sections[mode] + "\n"
    else:
        text += "\n".join(sections.values())

    text += total_portfolio_stats(total_old_value, total_new_value)
    return text