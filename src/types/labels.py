from typing import Dict

from src.types.response_enums import AssetType

PORTFOLIO_MODE_TITLES: Dict[AssetType, str] = {
    AssetType.ALL: "Your Portfolio",
    AssetType.STOCK: "Your Portfolio (Stocks)",
    AssetType.CRYPTO: "Your Portfolio (Crypto)",
    AssetType.STEAM: "Your Portfolio (Steam)"
}

PORTFOLIO_SECTION_TITLES: Dict[AssetType, str] = {
    AssetType.STOCK: "💹 Stocks",
    AssetType.CRYPTO: "⚡ Crypto",
    AssetType.STEAM: "🕹️ Steam Items",
}

HISTORY_MODE_TITLES: Dict[AssetType, str] = {
    AssetType.ALL: "📜 Portfolio History",
    AssetType.STOCK: "📜 Portfolio History (Stocks)",
    AssetType.CRYPTO: "📜 Portfolio History (Crypto)",
    AssetType.STEAM: "📜 Portfolio History (Steam)",
}
