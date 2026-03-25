from celery import Celery
from celery.schedules import crontab
from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "reddit_marketing",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "app.tasks.analysis_tasks",
        "app.tasks.report_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,  # 10 min max per task
    worker_max_tasks_per_child=50,  # Restart worker after 50 tasks (prevent memory leaks)
)

# Scheduled tasks
celery_app.conf.beat_schedule = {
    # Daily incremental crawl for all active monitors
    "daily-crawl": {
        "task": "app.tasks.analysis_tasks.daily_incremental_crawl",
        "schedule": crontab(hour=6, minute=0),  # 6 AM UTC daily
    },
    # Weekly full refresh
    "weekly-refresh": {
        "task": "app.tasks.analysis_tasks.weekly_full_refresh",
        "schedule": crontab(hour=3, minute=0, day_of_week=1),  # Monday 3 AM UTC
    },
    # Monthly quota reset
    "monthly-quota-reset": {
        "task": "app.tasks.analysis_tasks.reset_monthly_quotas",
        "schedule": crontab(hour=0, minute=0, day_of_month=1),  # 1st of month
    },
}
