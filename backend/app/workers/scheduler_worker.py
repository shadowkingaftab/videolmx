"""Scheduler worker for periodic tasks."""

from datetime import datetime, timedelta

from app.workers.worker_app import celery_app
from app.database.engine import get_db_session
from app.repositories.job_repository import JobRepository
from app.repositories.export_repository import ExportRepository
from app.constants import JobStatus, ExportStatus


@celery_app.task(name="app.workers.scheduler_worker.cleanup_expired")
def cleanup_expired():
    """Clean up expired records."""
    async def _run():
        async with get_db_session() as db:
            # Clean up old exports
            export_repo = ExportRepository(db)
            cutoff = datetime.utcnow() - timedelta(days=7)
            await export_repo.delete_older_than(cutoff)
            
            # Clean up old jobs
            job_repo = JobRepository(db)
            cutoff = datetime.utcnow() - timedelta(days=30)
            await job_repo.delete_completed_older_than(cutoff)
    
    import asyncio
    asyncio.run(_run())
    return {"message": "Cleanup completed"}


@celery_app.task(name="app.workers.scheduler_worker.update_video_status")
def update_video_status():
    """Update video status for long-running renders."""
    # This would check render status from external services
    return {"message": "Video status updated"}


@celery_app.task(name="app.workers.scheduler_worker.check_failed_jobs")
def check_failed_jobs():
    """Check and retry failed jobs."""
    async def _run():
        async with get_db_session() as db:
            job_repo = JobRepository(db)
            failed_jobs = await job_repo.get_failed_jobs(limit=10)
            
            for job in failed_jobs:
                # Retry logic here
                job.status = JobStatus.RETRYING
                await job_repo.update_crawl_job(job)
    
    import asyncio
    asyncio.run(_run())
    return {"message": "Failed jobs checked"}