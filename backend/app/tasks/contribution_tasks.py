"""贡献值每日递减核算任务 - 每日凌晨3:00"""
import asyncio
from app.tasks.celery_app import celery_app
from app.services.contribution_service import ContributionService


def run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(name="app.tasks.contribution_tasks.daily_contribution_check")
def daily_contribution_check():
    """每日贡献值递减核算(数据累计, 周一统一结算)"""
    from app.database import async_session_factory
    async def _run():
        async with async_session_factory() as db:
            # 每日核算, 但消费券仅周一发放
            from datetime import datetime
            if datetime.utcnow().weekday() == 0:  # 周一
                result = await ContributionService.weekly_settle(db)
                await db.commit()
                return result
            return {"message": "非周一, 仅累计数据"}
    return run_async(_run())
