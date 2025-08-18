import asyncio
from decimal import Decimal
import operator
import httpx
from aiogram import html
from aiogram.enums import ParseMode
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from src.common import bot
from src.dao.models import AsyncSessionLocal, Alert
from src.common import API_BASE_URL
from src import (get_logger)

logger = get_logger()

ops = {
    '>': operator.gt,
    ">=": operator.ge,
    '<': operator.lt,
    "<=": operator.le
}

async def check_alerts():
    while True:
        try:
            logger.info("Checking alerts...")
            async with AsyncSessionLocal() as session:
                result = await session.execute(select(Alert))
                alerts = result.scalars().all()

                if not alerts:
                    await asyncio.sleep(10)
                    continue

                async with httpx.AsyncClient() as client:
                    for alert in alerts:
                        try:
                            asset_type = alert.asset_type
                            asset_name = alert.asset_name
                            app_id = alert.app_id
                            url = f"{API_BASE_URL}/{asset_type}/{asset_name}" if app_id is None else f"{API_BASE_URL}/{asset_type}/{app_id}/{asset_name}"

                            response = await client.get(url)
                            response.raise_for_status()
                            data = response.json()
                            price = Decimal(str(data.get('price', 0.0)))

                            if ops[alert.direction](price, alert.target_price):
                                await bot.send_message(alert.user_id, f"🔔 Alert triggered! {alert.asset_name} "
                                f"reached ${price:.2f} (target: ${alert.target_price:.2f}).")
                                await session.delete(alert)
                                await session.commit()
                        except Exception as e:
                            logger.error(f"Error fetching price for {asset_type}:{asset_name}: {e}")
                            continue
        except SQLAlchemyError as e:
            logger.error(f"Database error while gathering alert with id {alert.id}: {e}")
        except Exception as e:
            logger.error(f"Failed to gather alert with id {alert.id}: {e}")
        finally:
            await asyncio.sleep(10)