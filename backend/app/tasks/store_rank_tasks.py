"""门店月度排名与分红任务 - 每月1日凌晨1:00"""
import asyncio
from app.tasks.celery_app import celery_app
from app.agents.all_agents import TeamAgent


def run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(name="app.tasks.store_rank_tasks.monthly_store_dividend")
def monthly_store_dividend():
    """每月1日执行门店月度排名与阶梯分红"""
    from app.database import async_session_factory
    from datetime import datetime, timedelta
    async def _run():
        async with async_session_factory() as db:
            # 统计上月业绩
            last_month = (datetime.now().replace(day=1) - timedelta(days=1)).strftime("%Y-%m")
            agent = TeamAgent()
            result = await agent.run({"db": db, "year_month": last_month})
            await db.commit()
            return result
    return run_async(_run())
