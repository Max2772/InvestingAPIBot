import asyncio

from sqlalchemy import select

from src.bot_init.bot_init import bot
from src.dao.models import AsyncSessionLocal, Alert
from src.env import ALERT_INTERVAL_SECONDS
from src.logger import logger
from src.types.operators import operators
from src.utils.api_utils import get_latest_price
from src.utils.formatters import format_alert_triggered


async def check_alerts():
    while True:
        try:
            logger.info("Checking alerts...")
            async with AsyncSessionLocal() as session:
                result = await session.execute(select(Alert).where(Alert.active))
                alerts = result.scalars().all()

                if not alerts:
                    logger.info("No active alerts found.")
                    await asyncio.sleep(ALERT_INTERVAL_SECONDS)
                    continue

                for alert in alerts:
                    try:
                        asset_type = alert.asset_type
                        asset_name = alert.asset_name
                        app_id = alert.app_id

                        price = await get_latest_price(asset_type, asset_name, app_id)
                        if price is None:
                            continue

                        if operators[alert.direction](price, alert.target_price):
                            message = format_alert_triggered(
                                asset_name,
                                app_id,
                                price,
                                alert.direction,
                                alert.target_price,
                            )

                            await bot.send_message(alert.user_id, message)

                            alert.active = False
                            logger.info(f"Alert {alert.id} triggered for {asset_type}:{asset_name}, user_id: {alert.user_id}")
                    except Exception as e:
                        await session.rollback()
                        logger.error(f"Error fetching price for alert {alert.id} ({asset_type}:{asset_name}, user_id: {alert.user_id}): {e}")
                        continue

                await session.commit()
        except Exception as e:
            logger.error(f"Failed to gather alert: {e}")
        finally:
            await asyncio.sleep(ALERT_INTERVAL_SECONDS)