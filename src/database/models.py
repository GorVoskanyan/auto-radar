import datetime
from sqlalchemy import BigInteger, Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True)  # Telegram user ID
    username = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    language_code = Column(String, default="hy")  # hy or en
    is_broker = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    saved_searches = relationship("SavedSearch", back_populates="user", cascade="all, delete-orphan")


class SavedSearch(Base):
    __tablename__ = "saved_searches"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    make = Column(String, nullable=True)
    model = Column(String, nullable=True)
    max_budget = Column(Float, nullable=True)
    min_year = Column(Integer, nullable=True)
    max_year = Column(Integer, nullable=True)
    title_type = Column(String, nullable=True)  # Clean, Salvage, All
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="saved_searches")


class ListingCache(Base):
    __tablename__ = "listing_cache"

    id = Column(String, primary_key=True)  # Auction Lot ID
    auction_source = Column(String, default="Copart")  # Copart, IAAI, etc.
    title = Column(String, nullable=False)
    make = Column(String, nullable=False)
    model = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    buy_now_price = Column(Float, nullable=True)
    est_auction_price = Column(Float, nullable=False)
    current_bid = Column(Float, nullable=True)
    mileage = Column(Integer, nullable=True)
    engine_capacity_cc = Column(Integer, default=2000)
    fuel_type = Column(String, default="gasoline")  # gasoline, hybrid, electric
    primary_damage = Column(String, nullable=True)
    title_type = Column(String, default="Salvage")
    location = Column(String, nullable=True)
    image_url = Column(Text, nullable=True)
    auction_url = Column(Text, nullable=True)
    auction_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class SystemConfig(Base):
    __tablename__ = "system_config"

    key = Column(String, primary_key=True)
    value = Column(String, nullable=False)
