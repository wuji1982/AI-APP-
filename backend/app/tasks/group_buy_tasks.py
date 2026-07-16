"""拼团定时任务"""
import asyncio
from datetime import datetime
from app.tasks.celery_app import celery_app
from app.agents.group_buy_agent import GroupBuyAgent


def run_async(coro):
    """在同步Celery任务中运行异步代码"""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(name="app.tasks.group_buy_tasks.create_daily_sessions")
def create_daily_sessions():
    """每日9:50创建当日拼团场次"""
    from app.database import async_session_factory
    async def _run():
        async with async_session_factory() as db:
            agent = GroupBuyAgent()
            result = await agent.run({"db": db, "action": "create_sessions", "date": datetime.utcnow()})
            await db.commit()
            return result
    return run_async(_run())


@celery_app.task(name="app.tasks.group_buy_tasks.check_and_settle_sessions")
def check_and_settle_sessions():
    """每小时检查并结算已满场次"""
    from app.database import async_session_factory
    async def _run():
        async with async_session_factory() as db:
            agent = GroupBuyAgent()
            result = await agent.run({"db": db, "action": "check_and_settle"})
            await db.commit()
            return result
    return run_async(_run())


@celery_app.task(name="app.tasks.group_buy_tasks.check_expired_sessions")
def check_expired_sessions():
    """每日23:00检查过期场次"""
    from app.database import async_session_factory
    async def _run():
        async with async_session_factory() as db:
            agent = GroupBuyAgent()
            result = await agent.run({"db": db, "action": "check_expired"})
            await db.commit()
            return result
    return run_async(_run())
