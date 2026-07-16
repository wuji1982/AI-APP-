"""用户API"""
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.main import UserInfo, WalletInfo
from app.utils.auth import get_current_user_id

router = APIRouter()


@router.get("/me", response_model=UserInfo)
async def get_current_user(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one()
    return user


@router.get("/wallet", response_model=WalletInfo)
async def get_wallet(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one()
    return WalletInfo(
        balance=user.balance,
        contribution_value=user.contribution_value,
        points=user.points,
        coupon_balance=user.coupon_balance,
    )
