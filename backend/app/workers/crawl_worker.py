"""Crawl worker."""

from celery import Task

from app.workers.worker_app import celery_app
from app.core.event_bus import event_bus
from app.core.cache import get_cache
from app.database.engine import get_db_session
from app.repositories.job_repository import JobRepository
from app.crawler.crawler import Crawler


class CrawlWorker(Task):
    """Crawl worker task."""
    
    async def run(self, job_id: str, *args, **kwargs):
        """Run crawl job."""
        try:
            # Update job status
            await self._update_job_status(job_id, "running")
            
            # Get crawl job
            async with get_db_session() as db:
                job_repo = JobRepository(db)
                job = await job_repo.get_crawl_job(job_id)
                if not job:
                    raise ValueError(f"Job not found: {job_id}")
            
            # Execute crawl
            crawler = Crawler()
            result = await crawler.crawl(
                url=job.website.url,
                max_pages=job.max_pages,
                max_depth=job.max_depth,
                include_assets=job.include_assets,
            )
            
            # Update job with results
            async with get_db_session() as db:
                job_repo = JobRepository(db)
                job = await job_repo.get_crawl_job(job_id)
                job.status = "completed"
                job.progress = 100.0
                job.pages_crawled = len(result.get("pages", []))
                job.total_pages = result.get("total_pages", 0)
                job.assets_collected = len(result.get("assets", []))
                job.results = result
                job.completed_at = datetime.utcnow()
                await job_repo.update_crawl_job(job)
            
            # Publish event
            await event_bus.publish(
                "crawl_completed",
                {"job_id": job_id, "result": result},
            )
            
            return result
            
        except Exception as e:
            # Handle error
            async with get_db_session() as db:
                job_repo = JobRepository(db)
                job = await job_repo.get_crawl_job(job_id)
                job.status = "failed"
                job.error_message = str(e)
                job.failed_at = datetime.utcnow()
                await job_repo.update_crawl_job(job)
            
            await event_bus.publish(
                "crawl_failed",
                {"job_id": job_id, "error": str(e)},
            )
            
            raise
    
    async def _update_job_status(self, job_id: str, status: str):
        """Update job status."""
        cache = await get_cache()
        await cache.setex(
            f"job_status:{job_id}",
            3600,
            {"status": status},
        )


# Register task
crawl_worker = celery_app.register_task(CrawlWorker())
celery_app.task(crawl_worker, name="crawl_worker.process_crawl")