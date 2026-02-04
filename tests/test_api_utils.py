from decimal import Decimal
from unittest.mock import AsyncMock, patch

import pytest
from aiohttp import ClientSession, ClientResponseError

from src.types.response_enums import AssetType
from src.utils.api_utils import get_api_url, get_api_response, get_latest_price
from src.env import API_BASE_URL

ASSET_NAME = "AMD"
APP_ID = 730
FAKE_PRICE = 150.25

@pytest.fixture
def mock_response():
    response = AsyncMock()
    response.status = 200
    response.json = AsyncMock(return_value={"price": FAKE_PRICE})
    return response


@pytest.fixture
def mock_session(mock_response):
    session = AsyncMock(spec=ClientSession)
    session.get = AsyncMock()
    session.get.return_value.__aenter__.return_value = mock_response
    session.get.return_value.__aexit__ = AsyncMock()
    return session


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "asset_type, app_id, expected_url",
    [
        (AssetType.STOCK, None, f"{API_BASE_URL}/stock/AMD"),
        (AssetType.CRYPTO, None, f"{API_BASE_URL}/crypto/ETH"),
        (AssetType.STEAM, 730, f"{API_BASE_URL}/steam/730/Danger Zone Case"),
    ],
)
def test_get_api_url(asset_type, app_id, expected_url):
    asset_name = "Danger Zone Case" if app_id else "AMD" if asset_type == AssetType.STOCK else "ETH"
    url = get_api_url(asset_type, asset_name, app_id)
    assert url == expected_url


@pytest.mark.asyncio
async def test_get_api_response_success(mock_session, mock_response):
    with patch("src.utils.api_utils.ClientSession", return_value=mock_session):
        data = await get_api_response(AssetType.STOCK, "AMD")

    assert data == {"price": FAKE_PRICE}
    mock_session.get.assert_called_once_with(f"{API_BASE_URL}/stock/AMD")


@pytest.mark.asyncio
async def test_get_api_response_404():
    mock_resp = AsyncMock()
    mock_resp.status = 404
    mock_resp.raise_for_status = AsyncMock(side_effect=ClientResponseError(
        request_info=AsyncMock(), history=(), status=404, message="Not Found"
    ))

    mock_sess = AsyncMock()
    mock_sess.get.return_value.__aenter__.return_value = mock_resp

    with patch("src.utils.api_utils.ClientSession", return_value=mock_sess):
        data = await get_api_response(AssetType.CRYPTO, "UNKNOWN_COIN")

    assert data is None


@pytest.mark.asyncio
async def test_get_api_response_exception():
    mock_sess = AsyncMock()
    mock_sess.get.side_effect = Exception("Connection timeout")

    with patch("src.utils.api_utils.ClientSession", return_value=mock_sess):
        data = await get_api_response(AssetType.STEAM, "Item", 730)

    assert data is None


@pytest.mark.asyncio
async def test_get_latest_price_success(mock_session, mock_response):
    with patch("src.utils.api_utils.ClientSession", return_value=mock_session):
        price = await get_latest_price(AssetType.STOCK, "AMD")

    assert isinstance(price, Decimal)
    assert price == Decimal("150.25")


@pytest.mark.asyncio
async def test_get_latest_price_no_data():
    mock_resp = AsyncMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value={})  # нет "price"

    mock_sess = AsyncMock()
    mock_sess.get.return_value.__aenter__.return_value = mock_resp

    with patch("src.utils.api_utils.ClientSession", return_value=mock_sess):
        price = await get_latest_price(AssetType.CRYPTO, "BTC")

    assert price == Decimal("0.0")


@pytest.mark.asyncio
async def test_get_latest_price_asset_not_found():
    mock_resp = AsyncMock()
    mock_resp.status = 404
    mock_resp.raise_for_status = AsyncMock(side_effect=ClientResponseError(
        request_info=AsyncMock(), history=(), status=404
    ))

    mock_sess = AsyncMock()
    mock_sess.get.return_value.__aenter__.return_value = mock_resp

    with patch("src.utils.api_utils.ClientSession", return_value=mock_sess):
        price = await get_latest_price(AssetType.STEAM, "Unknown Item", 730)

    assert price is None