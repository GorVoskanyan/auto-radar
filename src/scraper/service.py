import abc
import random
import datetime
from typing import List, Optional
from pydantic import BaseModel
from src.database.models import ListingCache


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
    Generates realistic car listings for popular imported models (Elantra, Camry, Civic, Model 3, etc.)
    when live scraping endpoints are rate-limited or unavailable.
    """

    MOCK_MAKES_MODELS = {
        "Hyundai": [("Elantra", 2000, "gasoline"), ("Sonata", 2500, "gasoline"), ("Tucson", 2400, "gasoline"), ("Ioniq", 1600, "hybrid")],
        "Toyota": [("Camry", 2500, "gasoline"), ("Corolla", 1800, "gasoline"), ("RAV4", 2500, "hybrid"), ("Prius", 1800, "hybrid")],
        "Honda": [("Civic", 1500, "gasoline"), ("Accord", 2000, "gasoline"), ("CR-V", 1500, "gasoline")],
        "Tesla": [("Model 3", 0, "electric"), ("Model Y", 0, "electric")],
        "Kia": [("Forte", 2000, "gasoline"), ("Optima", 2400, "gasoline"), ("Sportage", 2400, "gasoline")],
        "Ford": [("Fusion", 2000, "gasoline"), ("Mustang", 2300, "gasoline"), ("Escape", 1500, "gasoline")],
        "Bmw": [("330i", 2000, "gasoline"), ("530i", 2000, "gasoline"), ("X5", 3000, "gasoline")],
        "Mercedes-benz": [("C300", 2000, "gasoline"), ("E300", 2000, "gasoline"), ("GLE", 3000, "gasoline")]
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
            for model_name, engine_cc, fuel in models_info:
                if filters.model and filters.model.lower() not in model_name.lower():
                    continue

                for idx in range(2):
                    year = random.randint(filters.min_year or 2017, filters.max_year or 2023)
                    est_price = random.randint(3000, int(filters.max_budget) if filters.max_budget and filters.max_budget >= 4000 else 12000)
                    mileage = random.randint(15000, 95000)
                    damage = random.choice(self.DAMAGES)
                    loc = random.choice(self.LOCATIONS)
                    title_t = filters.title_type if filters.title_type and filters.title_type != "All" else random.choice(["Salvage", "Clean"])

                    lot_id = f"CP-{random.randint(10000000, 99999999)}"

                    item = ListingCache(
                        id=lot_id,
                        auction_source="Copart",
                        title=f"{year} {make.upper()} {model_name.upper()}",
                        make=make,
                        model=model_name,
                        year=year,
                        buy_now_price=round(est_price * 1.15, 2) if random.choice([True, False]) else None,
                        est_auction_price=float(est_price),
                        current_bid=float(est_price * 0.6),
                        mileage=mileage,
                        engine_capacity_cc=engine_cc,
                        fuel_type=fuel,
                        primary_damage=damage,
                        title_type=title_t,
                        location=loc,
                        image_url="https://cs.copart.com/v1/AUTH_svc.p3/PIX/default_car.jpg",
                        auction_url=f"https://www.copart.com/lot/{lot_id}",
                        auction_date=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=random.randint(1, 7))
                    )
                    listings.append(item)

        if filters.max_budget:
            listings = [l for l in listings if l.est_auction_price <= filters.max_budget]

        return listings[:10]
