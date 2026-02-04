from aiogram.filters.callback_data import CallbackData
from src.types.response_enums import AssetType

class PortfolioCb(CallbackData, prefix="portfolio"):
    asset_type: AssetType