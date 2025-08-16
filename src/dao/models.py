import os
from datetime import datetime, UTC
from sqlalchemy import Column, String, Boolean, DateTime, create_engine, BigInteger, Integer, ForeignKey, Float, Numeric
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'investingapibot_users'

    telegram_id = Column(BigInteger, unique=True, primary_key=True)
    username = Column(String(50), nullable=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=True)
    phone = Column(String(20), nullable=True)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    registered_at = Column(DateTime(timezone=True), default=datetime.now(tz=UTC))

    portfolios = relationship("Portfolio", back_populates="user", lazy="selectin")

    def __repr__(self):
        return f"<User(id={self.telegram_id}, username='{self.username}')>"

class Portfolio(Base):
    __tablename__ = 'investingapibot_portfolios'
    id = Column(Integer, unique=True, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('investingapibot_users.telegram_id'), nullable=False)
    asset_type = Column(String)
    asset_name = Column(String)
    quantity = Column(Numeric(precision=38, scale=18))
    buy_price = Column(Numeric(precision=38, scale=2))
    purchase_date = Column(DateTime(timezone=True), default=datetime.now(tz=UTC))
    app_id = Column(Integer, nullable=True)

    user = relationship("User", back_populates="portfolios", lazy="selectin")

    def __repr__(self):
        return f"<Portfolio(id={self.id}, user_id={self.user_id}, name='{self.asset_name}')>"


DATABASE_URL = os.getenv(
    "INVESTINGAPIBOT_ASYNC_DATABASE_URL",
    "sqlite+aiosqlite:///InvestingAPIBot.db"
)

async_engine = create_async_engine(
    DATABASE_URL,
    echo=True
)
AsyncSessionLocal = sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False) # NoQa