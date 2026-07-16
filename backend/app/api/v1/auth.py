"""认证API"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.database import get_db
from app.models.user import User
from app.schemas.main import RegisterRequest, LoginRequest, TokenResponse
from app.utils.auth import hash_password, verify_password, create_access_token
from app.services.user_agent_service import user_agent_service
from app.services.im_service import im_service
from app.services.openim_client import openim_client

logger = logging.getLogger(__name__)

router = APIRouter()


async def _create_user_agent_background(user_id: int, phone: str, nickname: str):
    """后台任务：为新用户创建AI智能体"""
    try:
        from app.database import async_session_factory
        async with async_session_factory() as db:
            await user_agent_service.create_agent_for_user(db, user_id, phone, nickname)
            logger.info(f"用户 {user_id} 智能体创建成功")
    except Exception as e:
        logger.error(f"用户 {user_id} 智能体创建失败: {e}")


async def _sync_user_to_im_background(user_id: int, phone: str, nickname: str, referrer_id: int = None):
    """后台任务：同步用户到IM并自动添加好友"""
    try:
        # 创建IM账号
        await im_service.sync_user_to_im(user_id, nickname, phone=phone)
        # 自动与推荐人成为好友
        if referrer_id:
            await im_service.auto_add_friends(user_id, referrer_id)
        logger.info(f"用户 {user_id} IM同步成功")
    except Exception as e:
        logger.error(f"用户 {user_id} IM同步失败: {e}")


@router.post("/register", response_model=TokenResponse)
async def register(
    req: RegisterRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    # 检查手机号是否已注册
    result = await db.execute(select(User).where(User.phone == req.phone))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="手机号已注册")

    user = User(
        phone=req.phone,
        password_hash=hash_password(req.password),
        nickname=req.nickname or f"用户{req.phone[-4:]}",
        referrer_id=req.referrer_id,
    )
    db.add(user)
    await db.flush()

    # 后台任务：为新用户创建AI智能体
    background_tasks.add_task(
        _create_user_agent_background,
        user.id,
        user.phone,
        user.nickname
    )

    # 后台任务：同步用户到IM
    background_tasks.add_task(
        _sync_user_to_im_background,
        user.id,
        user.phone,
        user.nickname,
        user.referrer_id
    )

    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(access_token=token, user_id=user.id)


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.phone == req.phone))
    user = result.scalar_one_or_none()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="手机号或密码错误")

    token = create_access_token({"sub": str(user.id)})

    # 获取IM Token（OpenIM未部署时忽略失败）
    im_token = None
    try:
        im_token = await openim_client.get_user_token(str(user.id))
    except Exception as e:
        logger.warning(f"获取IM Token失败（OpenIM可能未部署）: {e}")

    return TokenResponse(access_token=token, user_id=user.id, im_token=im_token)
