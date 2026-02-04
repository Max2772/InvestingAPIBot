from enum import Enum

class AssetType(Enum):
    ALL = "all"
    STOCK = "stock"
    CRYPTO = "crypto"
    STEAM = "steam"

class HistoryOperation(Enum):
    ADD = "add"
    REMOVE = "remove"

class AlertAddResult(Enum):
    LIMIT_REACHED = -1
    ASSET_NOT_FOUND = 0
    SUCCESS = 1

class RemoveAssetResult(Enum):
    NOT_ENOUGH = -1
    ASSET_NOT_FOUND = 0
    SUCCESS = 1

