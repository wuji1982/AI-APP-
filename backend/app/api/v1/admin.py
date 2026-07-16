"""管理后台API"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.group_buy_service import GroupBuyService
from app.services.contribution_service import ContributionService
from app.services.dividend_service import DividendService
from app.services.settlement_service import SettlementService
from app.services.points_service import PointsService
from app.services.risk_service import RiskService
from app.utils.auth import get_current_user_id

router = APIRouter()


@router.post("/group-buy/create-sessions")
async def create_daily_sessions(
    date: str = None,
    db: AsyncSession = Depends(get_db),
):
    """手动创建每日拼团场次"""
    if date:
        dt = datetime.strptime(date, "%Y-%m-%d")
    else:
        dt = datetime.utcnow()
    sessions = await GroupBuyService.create_daily_sessions(db, dt)
    return {"created": len(sessions), "date": dt.strftime("%Y-%m-%d")}


@router.post("/group-buy/settle/{session_id}")
async def settle_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
):
    """手动结算拼团场次"""
    try:
        result = await GroupBuyService.settle_session(db, session_id)
        return {"code": 0, "message": "结算成功", "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/dividend/weekly")
async def trigger_weekly_dividend(db: AsyncSession = Depends(get_db)):
    """手动触发每周分红"""
    result = await DividendService.weekly_dividend(db)
    return {"code": 0, "message": "分红完成", "data": result}


@router.post("/contribution/weekly-settle")
async def trigger_weekly_contribution_settle(db: AsyncSession = Depends(get_db)):
    """手动触发每周贡献值递减兑换"""
    result = await ContributionService.weekly_settle(db)
    return {"code": 0, "message": "结算完成", "data": result}


@router.post("/store/monthly-dividend")
async def trigger_store_monthly_dividend(
    year_month: str = None,
    db: AsyncSession = Depends(get_db),
):
    """手动触发门店月度阶梯分红"""
    if not year_month:
        year_month = datetime.now().strftime("%Y-%m")
    result = await SettlementService.settle_store_monthly_dividend(db, year_month)
    return {"code": 0, "message": "分红完成", "data": result}


@router.get("/risk/logs")
async def get_risk_logs(
    page: int = 1,
    size: int = 20,
    db: AsyncSession = Depends(get_db),
):
    """获取风控日志"""
    result = await RiskService.get_risk_logs(db, page=page, size=size)
    return result


@router.get("/points/pool")
async def get_points_pool(db: AsyncSession = Depends(get_db)):
    """获取积分池状态"""
    return await PointsService.get_pool_status(db)
