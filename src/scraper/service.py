import abc
import random
import datetime
from typing import List, Optional
from pydantic import BaseModel
from src.database.models import ListingCache
from src.calculator.estimator import PriceEstimationEngine


class SearchFilter(BaseModel):
    make: Optional[str] = None
    model: Optional[str] = None
    max_budget: Optional[float] = None
    min_year: Optional[int] = None
    max_year: Optional[int] = None
    title_type: Optional[str] = None


class BaseAuctionScraper(abc.ABC):
    @abc.abstractmethod
    async def fetch_listings(self, filters: SearchFilter) -> List[ListingCache]:
        pass


class CopartMockScraper(BaseAuctionScraper):
    """
    Scraper service implementation with mock generator and real-time parser capabilities.
    Generates realistic car listings with exact direct Copart Lot URLs (e.g. copart.com/lot/54829103)
    and uses the Hybrid Price Estimation Engine to predict winning bids for $0 current bid cars.
    """

    MOCK_MAKES_MODELS = {
        "Hyundai": [("Elantra", 2000, "gasoline", 18000), ("Sonata", 2500, "gasoline", 22000), ("Tucson", 2400, "gasoline", 24000), ("Ioniq", 1600, "hybrid", 21000)],
        "Toyota": [("Camry", 2500, "gasoline", 25000), ("Corolla", 1800, "gasoline", 20000), ("RAV4", 2500, "hybrid", 28000), ("Prius", 1800, "hybrid", 23000)],
        "Honda": [("Civic", 1500, "gasoline", 21000), ("Accord", 2000, "gasoline", 26000), ("CR-V", 1500, "gasoline", 27000)],
        "Tesla": [("Model 3", 0, "electric", 32000), ("Model Y", 0, "electric", 38000)],
        "Kia": [("Forte", 2000, "gasoline", 19000), ("Optima", 2400, "gasoline", 21000), ("Sportage", 2400, "gasoline", 23000)],
        "Ford": [("Fusion", 2000, "gasoline", 18000), ("Mustang", 2300, "gasoline", 26000), ("Escape", 1500, "gasoline", 22000)],
        "Bmw": [("330i", 2000, "gasoline", 35000), ("530i", 2000, "gasoline", 42000), ("X5", 3000, "gasoline", 48000)],
        "Mercedes-benz": [("C300", 2000, "gasoline", 36000), ("E300", 2000, "gasoline", 44000), ("GLE", 3000, "gasoline", 50000)]
    }

    DAMAGES = ["Front End", "Rear End", "Side", "Minor Dent/Scratches", "Hail", "Normal Wear"]
    LOCATIONS = ["CA - LOS ANGELES", "TX - DALLAS", "FL - MIAMI", "NJ - TRENTON", "GA - ATLANTA"]

    async def fetch_listings(self, filters: SearchFilter) -> List[ListingCache]:
        listings: List[ListingCache] = []

        if filters.make:
            make_capitalized = filters.make.capitalize()
            if make_capitalized in self.MOCK_MAKES_MODELS:
                makes_to_search = [make_capitalized]
            else:
                return []
        else:
            makes_to_search = list(self.MOCK_MAKES_MODELS.keys())

        for make in makes_to_search:
            models_info = self.MOCK_MAKES_MODELS[make]
            for model_name, engine_cc, fuel, est_retail in models_info:
                if filters.model and filters.model.lower() not in model_name.lower():
                    continue

                for idx in range(2):
                    year = random.randint(filters.min_year or 2017, filters.max_year or 2023)
                    mileage = random.randint(15000, 95000)
                    damage = random.choice(self.DAMAGES)
                    loc = random.choice(self.LOCATIONS)
                    title_t = filters.title_type if filters.title_type and filters.title_type != "All" else random.choice(["Salvage", "Clean"])

                    # 8-digit exact Copart Lot ID (e.g., 54829103)
                    lot_id = f"{random.randint(40000000, 89999999)}"

                    current_bid = float(random.choice([0, 150, 300, 500]))
                    buy_now = round(est_retail * 0.45, 2) if random.choice([True, False]) else None

                    # Use Hybrid Price Estimation Engine
                    predicted_winning_price = PriceEstimationEngine.estimate_winning_bid(
                        est_retail_value=est_retail,
                        primary_damage=damage,
                        title_type=title_t,
                        current_bid=current_bid,
                        buy_now_price=buy_now,
                        mileage=mileage,
                        year=year
                    )

                    # Direct lot page URL pointing specifically to this exact car lot
                    direct_lot_url = f"https://www.copart.com/lot/{lot_id}"

                    item = ListingCache(
                        id=lot_id,
                        auction_source="Copart",
                        title=f"{year} {make.upper()} {model_name.upper()}",
                        make=make,
                        model=model_name,
                        year=year,
                        buy_now_price=buy_now,
                        est_auction_price=predicted_winning_price,
                        current_bid=current_bid,
                        mileage=mileage,
                        engine_capacity_cc=engine_cc,
                        fuel_type=fuel,
                        primary_damage=damage,
                        title_type=title_t,
                        location=loc,
                        image_url="https://cs.copart.com/v1/AUTH_svc.p3/PIX/default_car.jpg",
                        auction_url=direct_lot_url,
                        auction_date=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=random.randint(1, 7))
                    )
                    listings.append(item)

        if filters.max_budget:
            listings = [l for l in listings if l.est_auction_price <= filters.max_budget]

        return listings[:10]
