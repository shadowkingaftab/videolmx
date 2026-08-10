"""Analysis worker."""

from datetime import datetime

from app.workers.worker_app import celery_app
from app.core.event_bus import event_bus
from app.database.engine import get_db_session
from app.repositories.job_repository import JobRepository
from app.understanding.website_analyzer import WebsiteAnalyzer


@celery_app.task(name="analysis_worker.process_analysis", bind=True)
def process_analysis(self, job_id: str):
    """Process analysis job."""
    try:
        # Update job status
        self.update_state(state="RUNNING", meta={"progress": 0})
        
        # Get analysis job
        async def _run():
            async with get_db_session() as db:
                job_repo = JobRepository(db)
                job = await job_repo.get_analysis_job(job_id)
                if not job:
                    raise ValueError(f"Job not found: {job_id}")
                
                # Execute analysis
                analyzer = WebsiteAnalyzer()
                result = await analyzer.analyze(
                    website_id=job.website_id,
                    depth=job.depth,
                )
                
                # Update job with results
                job.status = "completed"
                job.progress = 100.0
                job.semantic_understanding = result.get("semantic_understanding")
                job.ui_analysis = result.get("ui_analysis")
                job.feature_extraction = result.get("feature_extraction")
                job.navigation_graph = result.get("navigation_graph")
                job.value_proposition = result.get("value_proposition")
                job.confidence_scores = result.get("confidence_scores")
                job.summary = result.get("summary")
                job.completed_at = datetime.utcnow()
                await job_repo.update_analysis_job(job)
                
                # Publish event
                await event_bus.publish(
                    "analysis_completed",
                    {"job_id": job_id, "result": result},
                )
                
                return result
        
        import asyncio
        result = asyncio.run(_run())
        return {"status": "completed", "result": result}
        
    except Exception as e:
        # Handle error
        async def _handle():
            async with get_db_session() as db:
                job_repo = JobRepository(db)
                job = await job_repo.get_analysis_job(job_id)
                job.status = "failed"
                job.error_message = str(e)
                job.failed_at = datetime.utcnow()
                await job_repo.update_analysis_job(job)
            
            await event_bus.publish(
                "analysis_failed",
                {"job_id": job_id, "error": str(e)},
            )
        
        import asyncio
        asyncio.run(_handle())
        raise