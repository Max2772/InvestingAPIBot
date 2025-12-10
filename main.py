import asyncio
import argparse

from src.handlers import * # NoQa
from src.tasks import check_alerts
from src.logger import setup_logger
from src.configuration.bot_init import bot, dp


async def main():
    asyncio.create_task(check_alerts())
    await dp.start_polling(bot)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--log-level', type=str, default=None,
                        help="Logging Level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")

    args = parser.parse_args()

    if args.log_level:
        log_level = args.log_level.upper()
        logger = setup_logger(log_level)
    else:
        logger = setup_logger()

    asyncio.run(main())