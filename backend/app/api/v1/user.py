"""用户API"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.main import UserInfo, WalletInfo, UserSearchResult
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


def _mask_phone(phone: str) -> str:
    """手机号脱敏: 138****8000"""
    if len(phone) >= 7:
        return phone[:3] + "****" + phone[-4:]
    return phone


@router.get("/search", response_model=List[UserSearchResult])
async def search_users(
    keyword: str = Query(..., min_length=2, description="手机号或昵称关键字"),
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """按手机号或昵称搜索用户（不返回敏感信息）"""
    query = select(User).where(
        or_(
            User.phone.like(f"%{keyword}%"),
            User.nickname.like(f"%{keyword}%"),
        )
    ).where(User.id != current_user_id).limit(20)

    result = await db.execute(query)
    users = result.scalars().all()

    return [
        UserSearchResult(
            id=u.id,
            nickname=u.nickname,
            phone_masked=_mask_phone(u.phone),
            avatar_url=u.avatar_url,
        )
        for u in users
    ]
