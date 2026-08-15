import asyncio
import logging
from src.logging_config import setup_logging
from src.database.session import init_db
from src.bot.main import setup_bot_and_dispatcher
from src.bot.scheduler import setup_scheduler


async def main():
    setup_logging()
    logging.info("Initializing database...")
    await init_db()

    logging.info("Setting up Telegram bot and handlers...")
    bot, dp = setup_bot_and_dispatcher()

    # Drop any pending updates and delete active webhook to prevent TelegramConflictError
    await bot.delete_webhook(drop_pending_updates=True)

    logging.info("Starting background alert scheduler...")
    scheduler = setup_scheduler(bot)
    scheduler.start()

    try:
        logging.info("Starting Telegram bot polling...")
        await dp.start_polling(bot)
    finally:
        scheduler.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
