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
    registered_at = Column(DateTime(timezone=True), default=lambda: datetime.now(tz=UTC))

    portfolios = relationship("Portfolio", back_populates="user", lazy="selectin")
    alerts = relationship("Alert", back_populates="user", lazy="selectin")

    def __repr__(self):
        return f"<User(id={self.telegram_id}, username='{self.username}')>"

class Portfolio(Base):
    __tablename__ = 'investingapibot_portfolios'
    id = Column(Integer, unique=True, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('investingapibot_users.telegram_id'), nullable=False)
    asset_type = Column(String, nullable=False)
    asset_name = Column(String, nullable=False)
    quantity = Column(Numeric(precision=38, scale=18))
    buy_price = Column(Numeric(precision=38, scale=2))
    purchase_date = Column(DateTime(timezone=True), default=lambda: datetime.now(tz=UTC))
    app_id = Column(Integer, nullable=True)

    user = relationship("User", back_populates="portfolios", lazy="selectin")

    def __repr__(self):
        return f"<Portfolio(id={self.id}, user_id={self.user_id}, name='{self.asset_name}')>"

class Alert(Base):
    __tablename__ = 'investingapibot_alerts'
    id = Column(Integer, unique=True, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('investingapibot_users.telegram_id'), nullable=False)
    asset_type = Column(String, nullable=False)
    asset_name = Column(String, nullable=False)
    target_price = Column(Numeric(precision=38, scale=18))
    direction = Column(String, nullable=False, default='>')
    registered_at = Column(DateTime(timezone=True), default=lambda: datetime.now(tz=UTC))
    app_id = Column(Integer, nullable=True)
    user = relationship("User", back_populates="alerts", lazy="selectin")

    def __repr__(self):
        return f"<Alert(id={self.id}, user_id={self.user_id}, name='{self.asset_name}', alert_price={self.alert_price})>"


engine = create_engine(
    os.getenv("INVESTINGAPIBOT_DATABASE_URL", "sqlite:///InvestingAPIBot.db"),
    echo=True
)

async_engine = create_async_engine(
    os.getenv("INVESTINGAPIBOT_DATABASE_URL", "sqlite+aiosqlite:///InvestingAPIBot.db"),
    echo=True
)

AsyncSessionLocal = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False) # NoQa