from decimal import Decimal
from typing import Optional

from sqlalchemy import select, and_, func

from src.dao.models import AsyncSessionLocal, Portfolio, Alert, DbUser, History
from src.env import MAXIMUM_ALERTS
from src.logger import logger
from src.types.response_enums import AssetType, AlertAddResult, RemoveAssetResult, HistoryOperation
from src.utils.api_utils import get_api_response


async def upsert_asset(
        user_id: int,
        asset_type: AssetType,
        asset_name: str,
        amount: Decimal,
        price: Decimal,
        app_id: Optional[int] = None
):
    async with AsyncSessionLocal() as session:
        try:
            conditions = [
                Portfolio.user_id == user_id,
                Portfolio.asset_type == asset_type,
                Portfolio.asset_name == asset_name,
            ]

            if app_id is not None:
                conditions.append(Portfolio.app_id == app_id)

            result = await session.execute(
                select(Portfolio).where(and_(*conditions))
            )
            asset = result.scalars().first()

            if asset:
                asset.buy_price = (asset.quantity * asset.buy_price + amount * price) / (asset.quantity + amount)
                asset.quantity += amount
            else:
                asset = Portfolio(
                        user_id=user_id,
                        asset_type=asset_type,
                        asset_name=asset_name,
                        quantity=amount,
                        buy_price=price,
                        app_id=app_id
                    )
                session.add(asset)

            await session.flush()

            history = History(
                user_id=user_id,
                portfolio_id=asset.id,
                operation=HistoryOperation.ADD,
                asset_type=asset_type,
                asset_name=asset_name,
                app_id=app_id,
                quantity=amount,
                buy_price=price
            )

            session.add(history)
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def remove_asset(
        user_id: int,
        asset_type: AssetType,
        asset_name: str,
        amount: Optional[Decimal],
        app_id: Optional[int] = None
) -> RemoveAssetResult:
    async with AsyncSessionLocal() as session:
        conditions = [
            Portfolio.user_id == user_id,
            Portfolio.asset_type == asset_type,
            Portfolio.asset_name == asset_name,
        ]

        if app_id is not None:
            conditions.append(Portfolio.app_id == app_id)

        result = await session.execute(
            select(Portfolio).where(
            and_(
                *conditions
                )
            )
        )

        asset: Portfolio = result.scalar_one_or_none()
        if not asset:
            return RemoveAssetResult.ASSET_NOT_FOUND

        if amount and asset.quantity < amount:
            return RemoveAssetResult.NOT_ENOUGH
        if amount is None or asset.quantity == amount:
            await session.delete(asset)
        else:
            asset.quantity -= amount

        history = History(
            user_id=user_id,
            portfolio_id=asset.id,
            operation=HistoryOperation.REMOVE,
            asset_type=asset_type,
            asset_name=asset_name,
            app_id=app_id,
            quantity=amount if amount else asset.quantity,
            buy_price=asset.buy_price
        )

        session.add(history)
        await session.commit()
        return RemoveAssetResult.SUCCESS


async def delete_alert(
        user_id: int,
        alert_id: int
) -> bool:
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(
                select(Alert).where(
                    and_(
                        Alert.user_id == user_id,
                        Alert.id == alert_id
                    )
                )
            )
            alert = result.scalars().first()

            if not alert:
                return False

            await session.delete(alert)
            await session.commit()

            return True
        except Exception:
            await session.rollback()
            raise

async def add_alert(
        user_id: int,
        asset_type: AssetType,
        asset_name: str,
        price: Decimal,
        direction: str,
        app_id: Optional[int] = None
) -> AlertAddResult:
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(
                select(func.count()).where(
                    and_(
                        Alert.user_id == user_id,
                        Alert.active
                        )
                )
            )

            count = result.scalar_one_or_none() or 0
            if count >= MAXIMUM_ALERTS:
                return AlertAddResult.LIMIT_REACHED

            data = await get_api_response(asset_type, asset_name, app_id)
            if data is None:
                return AlertAddResult.ASSET_NOT_FOUND

            session.add(
                Alert(
                    user_id=user_id,
                    asset_type=asset_type,
                    asset_name=asset_name,
                    target_price=price,
                    direction=direction,
                    app_id=app_id,
                )
            )
            await session.commit()
            return AlertAddResult.SUCCESS
        except Exception:
            await session.rollback()
            raise

async def upsert_user(
        user_id: int,
        username: str,
        first_name: str,
        last_name: str
) -> bool:
    async with AsyncSessionLocal() as session:
        try:
            user = await session.get(DbUser, user_id)
            if not user:
                session.add(
                    DbUser(
                        telegram_id=user_id,
                        username=username,
                        first_name=first_name,
                        last_name=last_name
                    )
                )
                await session.commit()
                return False
            return True
        except Exception:
            await session.rollback()
            raise

async def get_user(user_id: int) -> Optional[DbUser]:
    async with AsyncSessionLocal() as session:
        try:
            user = await session.get(DbUser, user_id)
            return user if user else None
        except Exception:
            logger.warning(f"Failed to get user {user_id}")
            raise

async def no_active_alerts(user: DbUser) -> bool:
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(select(func.count()).where(
                and_(
                    Alert.user_id == user.telegram_id,
                    Alert.active
                )
            ))
            count = result.scalar_one()
            return count == 0

        except Exception:
            logger.warning(f"Failed to check active alerts {user.telegram_id}")
            raise