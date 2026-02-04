import asyncio

from src.bot_init.bot_init import bot, dp
from src.logger import logger
from src.tasks import check_alerts


async def main():
    alert_task = asyncio.create_task(check_alerts())
    bot_task = asyncio.create_task(dp.start_polling(bot))

    await asyncio.gather(
        alert_task,
        bot_task
    )

if __name__ == '__main__':
    logger.info("Staring InvestingAPI Bot...")
    asyncio.run(main())