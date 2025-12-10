from src.handlers.start import router as register_router
from src.handlers.help import router as help_router
from src.handlers.check_commands import check_stock_router, check_crypto_router, check_steam_router
from src.handlers.add_commands import add_stock_router, add_crypto_router, add_steam_router
from src.handlers.remove_commands import remove_stock_router, remove_crypto_router, remove_steam_router
from src.handlers.alert_commands import alerts_router, set_alert_router, delete_alert_router
from src.handlers.portfolio import router as portfolio_router
from src.handlers.history import router as history_router

__all__ = [
    "register_router",
    "help_router",
    "check_stock_router", "check_crypto_router", "check_steam_router",
    "add_stock_router", "add_crypto_router", "add_steam_router",
    "remove_stock_router", "remove_crypto_router", "remove_steam_router",
    "alerts_router", "set_alert_router", "delete_alert_router",
    "portfolio_router",
    "history_router"
]