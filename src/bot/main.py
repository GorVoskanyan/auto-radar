from aiogram import Bot, Dispatcher
from src.config import settings
from src.bot.handlers import router


def setup_bot_and_dispatcher() -> tuple[Bot, Dispatcher]:
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    return bot, dp
