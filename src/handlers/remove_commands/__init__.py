from src.handlers.remove_commands.remove_stock import router as remove_stock_router
from src.handlers.remove_commands.remove_crypto import router as remove_crypto_router
from src.handlers.remove_commands.remove_steam import router as remove_steam_router

__all__ = ["remove_stock_router", "remove_crypto_router", "remove_steam_router"]