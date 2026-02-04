from src.handlers.commands import *
from src.handlers.messages import *
from src.handlers.callbacks import *

HANDLERS_ROUTER = Router()
HANDLERS_ROUTER.include_routers(
    CB_ROUTER,
    CMD_ROUTER
)