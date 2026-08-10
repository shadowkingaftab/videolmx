"""Celery worker application."""

from celery import Celery
from celery.schedules import crontab

from app.config import settings

# Create Celery app
celery_app = Celery(
    "website2video",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.workers.crawl_worker",
        "app.workers.analysis_worker",
        "app.workers.script_worker",
        "app.workers.narration_worker",
        "app.workers.render_worker",
        "app.workers.export_worker",
        "app.workers.scheduler_worker",
    ],
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_always_eager=settings.CELERY_TASK_ALWAYS_EAGER,
    task_acks_late=settings.CELERY_TASK_ACKS_LATE,
    task_reject_on_worker_lost=settings.CELERY_TASK_REJECT_ON_WORKER_LOST,
    task_track_started=settings.CELERY_TASK_TRACK_STARTED,
    task_time_limit=settings.CELERY_TASK_TIME_LIMIT,
    task_soft_time_limit=settings.CELERY_TASK_SOFT_TIME_LIMIT,
    worker_concurrency=settings.CELERY_WORKER_CONCURRENCY,
    worker_prefetch_multiplier=settings.CELERY_WORKER_PREFETCH_MULTIPLIER,
    worker_max_tasks_per_child=settings.CELERY_WORKER_MAX_TASKS_PER_CHILD,
    result_expires=3600,
    result_extended=True,
)

# Beat schedule
celery_app.conf.beat_schedule = {
    "cleanup-expired": {
        "task": "app.workers.scheduler_worker.cleanup_expired",
        "schedule": crontab(hour=2, minute=0),
    },
    "update-video-status": {
        "task": "app.workers.scheduler_worker.update_video_status",
        "schedule": crontab(minute="*/5"),
    },
    "check-failed-jobs": {
        "task": "app.workers.scheduler_worker.check_failed_jobs",
        "schedule": crontab(minute="*/10"),
    },
}


async def init_worker() -> None:
    """Initialize worker."""
    # Setup connections and pools
    pass


async def close_worker() -> None:
    """Close worker."""
    # Close connections and pools
    pass