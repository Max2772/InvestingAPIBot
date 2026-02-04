from aiogram import Router

from src.handlers.commands.add import ADD_ASSET_CMD_ROUTER
from src.handlers.commands.alerts import ALERTS_CMD_ROUTER
from src.handlers.commands.check import CHECK_ASSET_CMD_ROUTER
from src.handlers.commands.help import HELP_CMD_CMD_ROUTER
from src.handlers.commands.history import HISTORY_CMD_ROUTER
from src.handlers.commands.portfolio import PORTFOLIO_CMD_ROUTER
from src.handlers.commands.remove import REMOVE_ASSET_CMD_ROUTER
from src.handlers.commands.start import START_CMD_ROUTER

CMD_ROUTER = Router()
CMD_ROUTER.include_routers(
    ADD_ASSET_CMD_ROUTER,
    ALERTS_CMD_ROUTER,
    CHECK_ASSET_CMD_ROUTER,
    HELP_CMD_CMD_ROUTER,
    HISTORY_CMD_ROUTER,
    PORTFOLIO_CMD_ROUTER,
    REMOVE_ASSET_CMD_ROUTER,
    START_CMD_ROUTER
)