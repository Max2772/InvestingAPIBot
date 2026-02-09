import os
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from sqlalchemy import String, Boolean, DateTime, create_engine, BigInteger, Integer, ForeignKey, \
    Numeric, Enum
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, Mapped, mapped_column

from src.env import DATABASE_URL, ASYNC_DATABASE_URL, get_now
from src.logger import logger
from src.types.response_enums import AssetType, HistoryOperation

Base = declarative_base()


class DbUser(Base):
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str | None] = mapped_column(String(50), nullable=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    registered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: get_now())

    portfolios = relationship(
        "Portfolio",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    history = relationship(
        "History",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    alerts = relationship(
        "Alert",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    def __repr__(self):
        return f"<User(id={self.telegram_id}, username='{self.username}')>"


class Portfolio(Base):
    __tablename__ = "portfolios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id"), nullable=False)
    asset_type: Mapped[AssetType] = mapped_column(
        Enum(AssetType, name="asset_type_enum"),
        nullable=False
    )
    asset_name: Mapped[str] = mapped_column(String, nullable=False)
    app_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    quantity: Mapped[Decimal] = mapped_column(Numeric(precision=38, scale=18))
    buy_price: Mapped[Decimal] = mapped_column(Numeric(precision=38, scale=2))

    user = relationship(
        DbUser,
        back_populates="portfolios",
        lazy="selectin"
    )

    history = relationship(
        "History",
        back_populates="portfolio",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    def __repr__(self):
        return f"<Portfolio(id={self.id}, user_id={self.user_id}, name='{self.asset_name}')>"


class History(Base):
    __tablename__ = "histories"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id"), nullable=False)
    portfolio_id: Mapped[int] = mapped_column(Integer, ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=False)
    operation: Mapped[HistoryOperation] = mapped_column(
        Enum(HistoryOperation, name="history_operation_enum"),
        nullable=False
    )
    asset_type: Mapped[AssetType] = mapped_column(
        Enum(AssetType, name="asset_type_enum"),
        nullable=False
    )
    asset_name: Mapped[str] = mapped_column(String, nullable=False)
    app_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    quantity: Mapped[Decimal] = mapped_column(Numeric(precision=38, scale=18))
    buy_price: Mapped[Decimal] = mapped_column(Numeric(precision=38, scale=2))
    purchase_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: get_now())

    user = relationship(
        DbUser,
        back_populates="history",
        lazy="selectin"
    )

    portfolio = relationship(
        Portfolio,
        back_populates="history",
        lazy="selectin"
    )


    def __repr__(self):
        return f"<History(id={self.id}, user_id={self.user_id}, name='{self.asset_name}')>"


class Alert(Base):
    __tablename__ = "alerts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id"), nullable=False)
    asset_type: Mapped[AssetType] = mapped_column(
        Enum(AssetType, name="asset_type_enum"),
        nullable=False
    )
    asset_name: Mapped[str] = mapped_column(String, nullable=False)
    app_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    target_price: Mapped[Decimal] = mapped_column(Numeric(precision=38, scale=18))
    direction: Mapped[str] = mapped_column(String, nullable=False, default='>')
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    registered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: get_now())

    user = relationship(
        DbUser,
        back_populates="alerts",
        lazy="selectin"
    )

    def __repr__(self):
        return f"<Alert(id={self.id}, user_id={self.user_id}, name='{self.asset_name}', alert_price={self.target_price})>"


engine = create_engine(
    DATABASE_URL
)

async_engine = create_async_engine(
    ASYNC_DATABASE_URL
)

AsyncSessionLocal = sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)

DB_PATH = Path(__file__).resolve().parent.parent.parent / "InvestingAPIBot.db"


if not os.path.exists(DB_PATH):
    logger.info(f"Creating InvestingAPIBot database...")
    Base.metadata.create_all(engine)