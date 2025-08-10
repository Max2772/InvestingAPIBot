import asyncio
import logging
import argparse
from src import handlers # NoQa
from src.utils import (setup_logger)
from src.common import bot, dp

async def main() -> None:
    await dp.start_polling(bot)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--log-level", type=str, default=None,
                        help="Logging Level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")

    args = parser.parse_args()

    if args.log_level:
        log_level = args.log_level.upper()
        _logger = setup_logger(log_level)
    else:
        _logger = setup_logger()

    asyncio.run(main())