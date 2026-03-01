from decimal import Decimal
from typing import Optional, Union, Tuple

from aiohttp import ClientSession

from src.env import API_BASE_URL
from src.logger import logger
from src.types.api_models import StockResponse, CryptoResponse, SteamResponse
from src.types.response_enums import AssetType


def get_api_url(
        asset_type: AssetType,
        asset_name: str,
        app_id: Optional[int] = None
) -> str:
    return (
        f"{API_BASE_URL}/{asset_type.value}/{app_id}/{asset_name}"
        if app_id
        else f"{API_BASE_URL}/{asset_type.value}/{asset_name}"
    )


async def get_api_response(
        asset_type: AssetType,
        asset_name: str,
        app_id: Optional[int] = None
) -> Union[StockResponse, CryptoResponse, SteamResponse, None]:
    try:
        url = get_api_url(asset_type, asset_name, app_id)
        async with ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 404:
                    logger.warning("Asset not found.")
                    return None
                response.raise_for_status()
                return await response.json()
    except Exception as e:
        logger.error(f"Error fetching data: {str(e)}")
        return None


async def get_latest_price(
        asset_type: AssetType,
        asset_name: str,
        app_id: Optional[int] = None
) -> Union[Decimal, None]:
    data = await get_api_response(asset_type, asset_name, app_id)
    if data is None:
        return None
    return Decimal(str(data.get("price", 0.0)))


async def get_unique_asset(
        asset_type: AssetType,
        asset_name: str,
        app_id: Optional[int] = None
) -> Optional[Tuple[str, Decimal]]:
    data = await get_api_response(asset_type, asset_name, app_id)
    if data is None:
        return None
    return data.get("name"), Decimal(str(data.get("price", 0.0)))


async def get_unique_asset_name(
        asset_type: AssetType,
        asset_name: str,
        app_id: Optional[int] = None
) -> Optional[str]:
    data = await get_api_response(asset_type, asset_name, app_id)
    if data is None or data.get("name") is None:
        return None
    return data["name"]