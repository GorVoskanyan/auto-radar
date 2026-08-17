import pytest
from src.calculator.estimator import PriceEstimationEngine
from src.scraper.service import CopartMockScraper, SearchFilter


def test_hybrid_price_estimator():
    # Test estimation for front end salvage car
    est_bid = PriceEstimationEngine.estimate_winning_bid(
        est_retail_value=20000.0,
        primary_damage="Front End",
        title_type="Salvage",
        current_bid=0.0
    )
    assert est_bid > 500.0
    assert est_bid < 20000.0

    # Test estimation with Buy It Now
    est_bid_buy_now = PriceEstimationEngine.estimate_winning_bid(
        est_retail_value=20000.0,
        primary_damage="Front End",
        title_type="Salvage",
        current_bid=0.0,
        buy_now_price=8000.0
    )
    assert est_bid_buy_now > 0.0


@pytest.mark.asyncio
async def test_direct_lot_url_generation():
    scraper = CopartMockScraper()
    results = await scraper.fetch_listings(SearchFilter(make="Toyota", model="Camry"))
    assert len(results) > 0
    for car in results:
        assert "copart.com/lot/" in car.auction_url
