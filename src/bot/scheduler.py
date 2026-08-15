import logging
from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.database.session import AsyncSessionLocal
from src.database.repository import SavedSearchRepository, UserRepository, SystemConfigRepository
from src.scraper.service import CopartMockScraper, SearchFilter
from src.calculator.customs import CustomsCalculator
from src.bot.lexicon import get_text
from src.config import settings

logger = logging.getLogger(__name__)


async def check_alerts_and_notify(bot: Bot):
    logger.info("Running background alert monitoring job...")
    async with AsyncSessionLocal() as session:
        search_repo = SavedSearchRepository(session)
        user_repo = UserRepository(session)
        cfg_repo = SystemConfigRepository(session)

        active_searches = await search_repo.get_all_active_searches()
        if not active_searches:
            logger.info("No active search alerts found.")
            return

        logistics_val = float(await cfg_repo.get_value("DEFAULT_LOGISTICS_BASE_USD", str(settings.DEFAULT_LOGISTICS_BASE_USD)))
        broker_val = float(await cfg_repo.get_value("DEFAULT_BROKER_FEE_USD", str(settings.DEFAULT_BROKER_FEE_USD)))

        scraper = CopartMockScraper()

        for search in active_searches:
            filters = SearchFilter(
                make=search.make,
                model=search.model,
                max_budget=search.max_budget,
                min_year=search.min_year,
                title_type=search.title_type
            )
            listings = await scraper.fetch_listings(filters)
            if not listings:
                continue

            user = await user_repo.get_or_create(search.user_id)
            lang = user.language_code

            # Take top result to notify user
            car = listings[0]
            cost = CustomsCalculator.calculate_full_cost(
                auction_price=car.est_auction_price,
                year=car.year,
                engine_cc=car.engine_capacity_cc,
                fuel_type=car.fuel_type,
                base_logistics_usd=logistics_val,
                broker_fee_usd=broker_val
            )

            card_msg = f"🔔 **NEW MATCHING CAR FOUND!**\n\n" + get_text(
                lang,
                "car_card",
                title=car.title,
                id=car.id,
                auction_source=car.auction_source,
                year=car.year,
                mileage=car.mileage or "N/A",
                fuel_type=car.fuel_type,
                engine_cc=car.engine_capacity_cc,
                primary_damage=car.primary_damage or "N/A",
                title_type=car.title_type,
                location=car.location or "USA",
                auction_price=cost.auction_price,
                auction_fee=cost.auction_fee,
                total_logistics=cost.total_logistics,
                customs_clearance_total=cost.customs_clearance_total,
                broker_fee=cost.broker_fee,
                total_cost=cost.total_cost,
                auction_url=car.auction_url
            )

            try:
                await bot.send_message(search.user_id, card_msg, parse_mode="Markdown", disable_web_page_preview=True)
                logger.info(f"Notification sent to user {search.user_id} for car {car.id}")
            except Exception as e:
                logger.error(f"Failed to send alert notification to user {search.user_id}: {e}")


def setup_scheduler(bot: Bot) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        check_alerts_and_notify,
        "interval",
        minutes=15,
        args=[bot],
        id="check_auction_alerts"
    )
    return scheduler
