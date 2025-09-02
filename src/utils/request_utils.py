from typing import Dict, Optional, Any

from aiohttp import ClientSession
from aiogram.types import Message

from src.configuration.config import API_BASE_URL
from src.logger import get_logger


logger = get_logger()


def get_api_url(asset_type: str, asset_name: str, app_id: Optional[int] = None) -> str:
    return (
        f"{API_BASE_URL}/{asset_type}/{asset_name}"
        if app_id is None else
        f"{API_BASE_URL}/{asset_type}/{app_id}/{asset_name}"
    )

async def fetch_api_data(client: ClientSession, url: str, message: Message) -> Optional[Dict[str, Any]]:
    try:
        async with client.get(url) as response:
            asset_name = url.split("/")[-1]
            if response.status == 404:
                await message.answer(f"Sorry, asset {asset_name} doesn't exist.")
                logger.warning('Asset not found.')
                return None

            response.raise_for_status()
            return await response.json()
    except Exception as e:
        logger.error(f"Error fetching data: {str(e)}")
        await message.answer('Error fetching data')
        return None