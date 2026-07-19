"""钱包API"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.wallet_service import WalletService
from app.utils.auth import get_current_user_id

router = APIRouter()


class RechargeRequest(BaseModel):
    """充值请求"""
    amount: float = Field(..., gt=0, description="充值金额")
    description: Optional[str] = Field("余额充值", description="充值说明")


class WithdrawRequest(BaseModel):
    """提现请求"""
    amount: float = Field(..., gt=0, description="提现金额")
    description: Optional[str] = Field("余额提现", description="提现说明")


@router.get("/summary")
async def get_wallet_summary(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """获取钱包汇总信息（四大资产 + 今日收支）"""
    try:
        return await WalletService.get_wallet_summary(db, user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/balance-logs")
async def get_balance_logs(
    asset_type: Optional[str] = Query(None, description="资产类型: balance/contribution/points/coupon"),
    change_type: Optional[str] = Query(None, description="变动类型: income/expense/lock/unlock"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """查询余额流水"""
    return await WalletService.get_balance_logs(
        db, user_id, asset_type, change_type, page, size
    )


@router.post("/recharge")
async def recharge(
    req: RechargeRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """余额充值"""
    try:
        return await WalletService.recharge(db, user_id, req.amount, req.description)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/withdraw")
async def withdraw(
    req: WithdrawRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """余额提现"""
    try:
        return await WalletService.withdraw(db, user_id, req.amount, req.description)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
