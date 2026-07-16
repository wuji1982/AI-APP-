"""
Celery 应用配置与定时任务调度
"""
from celery import Celery
from celery.schedules import crontab

from app.config import settings

celery_app = Celery(
    "aixingmu",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
)

# 定时任务调度
celery_app.conf.beat_schedule = {
    # 每日9:50创建当日拼团场次
    "create-daily-sessions": {
        "task": "app.tasks.group_buy_tasks.create_daily_sessions",
        "schedule": crontab(hour=9, minute=50),
    },
    # 每小时检查并结算已满场次 (10:00-22:00)
    "check-and-settle-sessions": {
        "task": "app.tasks.group_buy_tasks.check_and_settle_sessions",
        "schedule": crontab(minute=5),  # 每小时第5分钟执行
    },
    # 每日23:00检查过期场次
    "check-expired-sessions": {
        "task": "app.tasks.group_buy_tasks.check_expired_sessions",
        "schedule": crontab(hour=23, minute=0),
    },
    # 每周一凌晨2:00执行贡献值分红
    "weekly-dividend": {
        "task": "app.tasks.dividend_tasks.weekly_dividend",
        "schedule": crontab(hour=2, minute=0, day_of_week=1),
    },
    # 每日凌晨3:00执行贡献值递减兑换核算
    "daily-contribution-check": {
        "task": "app.tasks.contribution_tasks.daily_contribution_check",
        "schedule": crontab(hour=3, minute=0),
    },
    # 每月1日凌晨1:00执行门店月度排名与分红
    "monthly-store-dividend": {
        "task": "app.tasks.store_rank_tasks.monthly_store_dividend",
        "schedule": crontab(hour=1, minute=0, day_of_month=1),
    },
}
