import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.database.models import Base
from src.database.repository import UserRepository, SavedSearchRepository, SystemConfigRepository


@pytest_asyncio.fixture
async def async_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with session_factory() as session:
        yield session


@pytest.mark.asyncio
async def test_user_repository(async_session):
    repo = UserRepository(async_session)
    user = await repo.get_or_create(12345, "testuser", "Test User")
    assert user.id == 12345
    assert user.language_code == "hy"

    await repo.update_language(12345, "en")
    updated_user = await repo.get_or_create(12345)
    assert updated_user.language_code == "en"


@pytest.mark.asyncio
async def test_saved_search_repository(async_session):
    repo = SavedSearchRepository(async_session)
    search = await repo.create_search(user_id=12345, make="Hyundai", model="Elantra", max_budget=8000.0)
    assert search.id is not None
    assert search.make == "Hyundai"

    user_searches = await repo.get_user_searches(12345)
    assert len(user_searches) == 1

    await repo.delete_search(search.id, 12345)
    active_searches = await repo.get_user_searches(12345)
    assert len(active_searches) == 0


@pytest.mark.asyncio
async def test_system_config_repository(async_session):
    repo = SystemConfigRepository(async_session)
    val = await repo.get_value("TEST_KEY", "default_val")
    assert val == "default_val"

    await repo.set_value("TEST_KEY", "new_val")
    val_updated = await repo.get_value("TEST_KEY", "default_val")
    assert val_updated == "new_val"
