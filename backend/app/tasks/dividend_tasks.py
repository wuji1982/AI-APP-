"""分红定时任务 - 每周一凌晨2:00"""
import asyncio
from app.tasks.celery_app import celery_app
from app.agents.all_agents import DividendAgent


def run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(name="app.tasks.dividend_tasks.weekly_dividend")
def weekly_dividend():
    """每周一执行全网贡献值分红"""
    from app.database import async_session_factory
    async def _run():
        async with async_session_factory() as db:
            agent = DividendAgent()
            result = await agent.run({"db": db})
            await db.commit()
            return result
    return run_async(_run())
