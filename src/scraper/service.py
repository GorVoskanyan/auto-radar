import abc
import random
import datetime
import re
from typing import List, Optional
from pydantic import BaseModel
from src.database.models import ListingCache
from src.calculator.estimator import PriceEstimationEngine


def build_copart_canonical_url(lot_id: str, title: str, location: Optional[str] = None) -> str:
    """
    Constructs canonical Copart Lot URL with SEO slug:
    e.g. https://www.copart.com/lot/99445285/2018-toyota-camry-xse-ky-lexington-west
    """
    clean_title = re.sub(r'[^a-zA-Z0-9\s-]', '', title)
    slug_parts = clean_title.split()

    if location:
        clean_loc = re.sub(r'[^a-zA-Z0-9\s-]', '', location)
        slug_parts.extend(clean_loc.split())

    slug = "-".join([p.lower() for p in slug_parts if p.strip()])
    if slug:
        return f"https://www.copart.com/lot/{lot_id}/{slug}"
    return f"https://www.copart.com/lot/{lot_id}"


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
    Generates realistic car listings and formats exact canonical Copart lot links
    with full vehicle title & location slugs (e.g., https://www.copart.com/lot/99445285/2018-toyota-camry-xse-ky-lexington-west).
    """

    MOCK_MAKES_MODELS = {
        "Hyundai": [("Elantra SE", 2000, "gasoline", 18000), ("Sonata SEL", 2500, "gasoline", 22000), ("Tucson Limited", 2400, "gasoline", 24000)],
        "Toyota": [("Camry XSE", 2500, "gasoline", 25000), ("Corolla LE", 1800, "gasoline", 20000), ("RAV4 XLE", 2500, "hybrid", 28000)],
        "Honda": [("Civic EX", 1500, "gasoline", 21000), ("Accord LX", 2000, "gasoline", 26000)],
        "Tesla": [("Model 3 Long Range", 0, "electric", 32000), ("Model Y Performance", 0, "electric", 38000)],
        "Kia": [("Forte GT", 2000, "gasoline", 19000), ("Optima EX", 2400, "gasoline", 21000)],
        "Ford": [("Fusion SE", 2000, "gasoline", 18000), ("Mustang GT", 2300, "gasoline", 26000)],
        "Bmw": [("330i xDrive", 2000, "gasoline", 35000), ("530i M Sport", 2000, "gasoline", 42000)]
    }

    DAMAGES = ["Front End", "Rear End", "Side", "Minor Dent/Scratches", "Hail", "Normal Wear"]
    LOCATIONS = ["KY - LEXINGTON WEST", "CA - LOS ANGELES", "TX - DALLAS", "FL - MIAMI", "NJ - TRENTON"]

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

                    lot_id = f"{random.randint(40000000, 89999999)}"
                    car_title = f"{year} {make.upper()} {model_name.upper()}"

                    current_bid = float(random.choice([0, 150, 300, 500]))
                    buy_now = round(est_retail * 0.45, 2) if random.choice([True, False]) else None

                    predicted_winning_price = PriceEstimationEngine.estimate_winning_bid(
                        est_retail_value=est_retail,
                        make=make,
                        model=model_name,
                        primary_damage=damage,
                        title_type=title_t,
                        current_bid=current_bid,
                        buy_now_price=buy_now,
                        mileage=mileage,
                        year=year
                    )

                    # Build canonical Copart URL with title and location slug
                    direct_lot_url = build_copart_canonical_url(lot_id, car_title, loc)

                    item = ListingCache(
                        id=lot_id,
                        auction_source="Copart",
                        title=car_title,
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
