import asyncio
import operator
from decimal import Decimal
from html import escape

import aiohttp
from aiogram.enums import ParseMode
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from src.dao.models import AsyncSessionLocal, Alert
from src.configuration.bot_init import bot
from src.configuration.config import ALERT_INTERVAL_SECONDS
from src.utils import get_logger, get_api_url


logger = get_logger()

ops = {
    '>': operator.gt,
    '>=': operator.ge,
    '<': operator.lt,
    '<=': operator.le
}

async def check_alerts():
    while True:
        try:
            logger.info('Checking alerts...')
            async with AsyncSessionLocal() as session:
                result = await session.execute(select(Alert))
                alerts = result.scalars().all()

                if not alerts:
                    logger.info('No active alerts found.')
                    await asyncio.sleep(ALERT_INTERVAL_SECONDS)
                    continue

                async with aiohttp.ClientSession() as client:
                    for alert in alerts:
                        try:
                            asset_type = alert.asset_type
                            asset_name = alert.asset_name
                            app_id = alert.app_id

                            url = get_api_url(asset_type, asset_name, app_id)
                            async with client.get(url) as response:
                                response.raise_for_status()
                                data = await response.json()
                                price = Decimal(str(data.get('price', 0.0)))

                                if ops[alert.direction](price, alert.target_price):
                                    asset = f"{asset_name}, app id = {app_id}" if app_id else f"{asset_name}"
                                    message = (
                                        f"<b>🔔 Alert Triggered!</b>\n"
                                        f"Asset: <b>{asset}</b>\n"
                                        f"Current price: <b>${price:.2f}</b>\n"
                                        f"Target: {escape(alert.direction)} <b>${alert.target_price:.2f}</b>"
                                    )

                                    await bot.send_message(alert.user_id, message, parse_mode=ParseMode.HTML)
                                    await session.delete(alert)
                                    await session.commit()
                                    logger.info(f"Alert {alert.id} triggered for {asset_type}:{asset_name}, user_id: {alert.user_id}")
                        except aiohttp.ClientResponseError as e:
                            logger.error(f"HTTP error for alert {alert.id} ({asset_type}:{asset_name}, user_id: {alert.user_id}): {e}")
                            continue
                        except (aiohttp.ClientError, aiohttp.ContentTypeError, ValueError, KeyError) as e:
                            logger.error(f"Error fetching price for alert {alert.id} ({asset_type}:{asset_name}, user_id: {alert.user_id}): {e}")
                            continue
        except SQLAlchemyError as e:
            logger.error(f"Database error while gathering alert: {e}")
        except Exception as e:
            logger.error(f"Failed to gather alert: {e}")
        finally:
            await asyncio.sleep(ALERT_INTERVAL_SECONDS)