import pytest
from src.scraper.service import CopartMockScraper, SearchFilter


@pytest.mark.asyncio
async def test_scraper_search_filter():
    scraper = CopartMockScraper()
    filters = SearchFilter(make="Hyundai", model="Elantra", max_budget=15000.0)
    results = await scraper.fetch_listings(filters)

    assert len(results) > 0
    for car in results:
        assert car.make == "Hyundai"
        assert "ELANTRA" in car.model.upper()
