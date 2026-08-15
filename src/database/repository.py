from typing import List, Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import User, SavedSearch, ListingCache, SystemConfig


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create(self, user_id: int, username: Optional[str] = None, full_name: Optional[str] = None) -> User:
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            user = User(id=user_id, username=username, full_name=full_name)
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
        return user

    async def update_language(self, user_id: int, lang_code: str):
        stmt = update(User).where(User.id == user_id).values(language_code=lang_code)
        await self.session.execute(stmt)
        await self.session.commit()

    async def set_broker_status(self, user_id: int, is_broker: bool):
        stmt = update(User).where(User.id == user_id).values(is_broker=is_broker)
        await self.session.execute(stmt)
        await self.session.commit()


class SavedSearchRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_search(
        self,
        user_id: int,
        make: Optional[str] = None,
        model: Optional[str] = None,
        max_budget: Optional[float] = None,
        min_year: Optional[int] = None,
        max_year: Optional[int] = None,
        title_type: Optional[str] = None,
    ) -> SavedSearch:
        saved_search = SavedSearch(
            user_id=user_id,
            make=make,
            model=model,
            max_budget=max_budget,
            min_year=min_year,
            max_year=max_year,
            title_type=title_type,
        )
        self.session.add(saved_search)
        await self.session.commit()
        await self.session.refresh(saved_search)
        return saved_search

    async def get_user_searches(self, user_id: int) -> List[SavedSearch]:
        stmt = select(SavedSearch).where(SavedSearch.user_id == user_id, SavedSearch.is_active == True)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_all_active_searches(self) -> List[SavedSearch]:
        stmt = select(SavedSearch).where(SavedSearch.is_active == True)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def delete_search(self, search_id: int, user_id: int):
        stmt = update(SavedSearch).where(SavedSearch.id == search_id, SavedSearch.user_id == user_id).values(is_active=False)
        await self.session.execute(stmt)
        await self.session.commit()


class ListingRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_listings(self, listings: List[ListingCache]):
        for item in listings:
            await self.session.merge(item)
        await self.session.commit()

    async def search_listings(
        self,
        make: Optional[str] = None,
        model: Optional[str] = None,
        max_budget: Optional[float] = None,
        min_year: Optional[int] = None,
        max_year: Optional[int] = None,
        title_type: Optional[str] = None,
        limit: int = 10,
    ) -> List[ListingCache]:
        query = select(ListingCache)
        if make:
            query = query.where(ListingCache.make.ilike(f"%{make}%"))
        if model:
            query = query.where(ListingCache.model.ilike(f"%{model}%"))
        if min_year:
            query = query.where(ListingCache.year >= min_year)
        if max_year:
            query = query.where(ListingCache.year <= max_year)
        if title_type and title_type != "All":
            query = query.where(ListingCache.title_type.ilike(title_type))
        if max_budget:
            query = query.where(ListingCache.est_auction_price <= max_budget)

        query = query.order_by(ListingCache.created_at.desc()).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())


class SystemConfigRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_value(self, key: str, default: str) -> str:
        stmt = select(SystemConfig).where(SystemConfig.key == key)
        result = await self.session.execute(stmt)
        row = result.scalar_one_or_none()
        return row.value if row else default

    async def set_value(self, key: str, value: str):
        config = SystemConfig(key=key, value=value)
        await self.session.merge(config)
        await self.session.commit()
