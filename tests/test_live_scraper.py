import pytest
from src.scraper.copart import CopartLiveScraper
from src.scraper.service import SearchFilter


@pytest.mark.asyncio
async def test_copart_live_scraper_fallback_and_urls():
    scraper = CopartLiveScraper()
    results = await scraper.fetch_listings(SearchFilter(make="Hyundai", model="Elantra"))

    assert len(results) > 0
    for car in results:
        assert car.id is not None
        assert "copart.com/lot/" in car.auction_url
        assert car.est_auction_price >= 500.0
