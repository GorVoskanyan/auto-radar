import pytest
from src.calculator.estimator import PriceEstimationEngine
from src.scraper.service import CopartMockScraper, SearchFilter
from src.bot.lexicon import get_text


def test_historical_sales_data_estimator():
    # Test Tesla Model 3 estimation with historical market average
    hist_avg = PriceEstimationEngine.get_historical_market_avg("Tesla", "Model 3")
    assert hist_avg == 9500.0

    predicted_bid = PriceEstimationEngine.estimate_winning_bid(
        est_retail_value=32000.0,
        make="Tesla",
        model="Model 3",
        primary_damage="Front End",
        title_type="Salvage"
    )
    assert predicted_bid > 5000.0


@pytest.mark.asyncio
async def test_direct_lot_urls_and_budget_filtering():
    scraper = CopartMockScraper()
    # Filter with budget below Tesla Model 3 market price ($3,000)
    results_low = await scraper.fetch_listings(SearchFilter(make="Tesla", model="Model 3", max_budget=3000.0))
    assert len(results_low) == 0

    # Filter with budget above market price ($15,000)
    results_high = await scraper.fetch_listings(SearchFilter(make="Tesla", model="Model 3", max_budget=15000.0))
    assert len(results_high) > 0
    for car in results_high:
        assert "copart.com/lot/" in car.auction_url
        assert car.est_auction_price <= 15000.0


def test_budget_recommendation_lexicon():
    text_hy = get_text('hy', 'budget_too_low_warning', make='Tesla', model='Model 3', user_budget=5000, min_auction_price=8200, min_yerevan_price=13500)
    assert "$5000" in text_hy
    assert "Tesla Model 3" in text_hy
    assert "$8200" in text_hy
