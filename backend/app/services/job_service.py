"""Job service."""

from typing import Optional, List, Tuple, Dict, Any
from uuid import UUID

from app.models.crawl_job import CrawlJob
from app.models.analysis_job import AnalysisJob
from app.repositories.job_repository import JobRepository
from app.repositories.website_repository import WebsiteRepository
from app.core.errors import NotFoundError
from app.core.task_queue import get_queue
from app.constants import JobStatus


class JobService:
    """Job service."""
    
    def __init__(
        self,
        job_repo: JobRepository,
        website_repo: WebsiteRepository
    ):
        self.job_repo = job_repo
        self.website_repo = website_repo
    
    # ===== Crawl Jobs =====
    
    async def create_crawl_job(
        self,
        website_id: UUID,
        user_id: UUID,
        max_pages: int = 50,
        depth: int = 3,
        include_assets: bool = True,
        respect_robots: bool = True
    ) -> CrawlJob:
        """Create a new crawl job."""
        website = await self.website_repo.get(website_id)
        if not website:
            raise NotFoundError("Website not found")
        
        job = CrawlJob(
            website_id=website_id,
            status=JobStatus.PENDING,
            max_pages=max_pages,
            max_depth=depth,
            include_assets=include_assets,
            respect_robots=respect_robots,
        )
        
        job = await self.job_repo.create_crawl_job(job)
        
        # Queue the job
        queue = await get_queue()
        await queue.enqueue(
            'crawl_worker.process_crawl',
            args=[str(job.id)],
            queue='crawler',
        )
        
        return job
    
    async def get_crawl_job(self, job_id: UUID) -> Optional[CrawlJob]:
        """Get crawl job by ID."""
        return await self.job_repo.get_crawl_job(job_id)
    
    async def list_crawl_jobs(
        self,
        user_id: UUID,
        website_id: Optional[UUID] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[CrawlJob], int]:
        """List crawl jobs."""
        return await self.job_repo.list_crawl_jobs(
            user_id=user_id,
            website_id=website_id,
            status=status,
            skip=skip,
            limit=limit
        )
    
    async def update_crawl_job(
        self,
        job_id: UUID,
        updates: Dict[str, Any]
    ) -> CrawlJob:
        """Update crawl job."""
        job = await self.job_repo.get_crawl_job(job_id)
        if not job:
            raise NotFoundError("Crawl job not found")
        
        for key, value in updates.items():
            if hasattr(job, key):
                setattr(job, key, value)
        
        return await self.job_repo.update_crawl_job(job)
    
    async def cancel_crawl_job(self, job_id: UUID) -> None:
        """Cancel a crawl job."""
        job = await self.job_repo.get_crawl_job(job_id)
        if not job:
            raise NotFoundError("Crawl job not found")
        
        job.status = JobStatus.CANCELLED
        await self.job_repo.update_crawl_job(job)
    
    async def get_crawl_progress(self, job_id: UUID) -> Dict[str, Any]:
        """Get crawl job progress."""
        job = await self.job_repo.get_crawl_job(job_id)
        if not job:
            raise NotFoundError("Crawl job not found")
        
        return {
            "status": job.status,
            "progress": job.progress,
            "pages_crawled": job.pages_crawled,
            "total_pages": job.total_pages,
            "assets_collected": job.assets_collected,
            "started_at": job.started_at,
            "completed_at": job.completed_at,
        }
    
    async def get_crawl_results(self, job_id: UUID) -> Dict[str, Any]:
        """Get crawl job results."""
        job = await self.job_repo.get_crawl_job(job_id)
        if not job:
            raise NotFoundError("Crawl job not found")
        
        return job.results or {}
    
    async def list_crawl_pages(
        self,
        job_id: UUID,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[Dict], int]:
        """List pages from a crawl job."""
        # This would be implemented with page repository
        return [], 0
    
    # ===== Analysis Jobs =====
    
    async def create_analysis_job(
        self,
        website_id: UUID,
        user_id: UUID,
        analysis_type: str = "full",
        depth: str = "standard"
    ) -> AnalysisJob:
        """Create a new analysis job."""
        website = await self.website_repo.get(website_id)
        if not website:
            raise NotFoundError("Website not found")
        
        job = AnalysisJob(
            website_id=website_id,
            status="pending",
            analysis_type=analysis_type,
            depth=depth,
        )
        
        job = await self.job_repo.create_analysis_job(job)
        
        # Queue the job
        queue = await get_queue()
        await queue.enqueue(
            'analysis_worker.process_analysis',
            args=[str(job.id)],
            queue='analysis',
        )
        
        return job
    
    async def get_analysis_job(self, job_id: UUID) -> Optional[AnalysisJob]:
        """Get analysis job by ID."""
        return await self.job_repo.get_analysis_job(job_id)
    
    async def list_analysis_jobs(
        self,
        user_id: UUID,
        website_id: Optional[UUID] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[AnalysisJob], int]:
        """List analysis jobs."""
        return await self.job_repo.list_analysis_jobs(
            user_id=user_id,
            website_id=website_id,
            status=status,
            skip=skip,
            limit=limit
        )
    
    async def update_analysis_job(
        self,
        job_id: UUID,
        updates: Dict[str, Any]
    ) -> AnalysisJob:
        """Update analysis job."""
        job = await self.job_repo.get_analysis_job(job_id)
        if not job:
            raise NotFoundError("Analysis job not found")
        
        for key, value in updates.items():
            if hasattr(job, key):
                setattr(job, key, value)
        
        return await self.job_repo.update_analysis_job(job)
    
    async def cancel_analysis_job(self, job_id: UUID) -> None:
        """Cancel an analysis job."""
        job = await self.job_repo.get_analysis_job(job_id)
        if not job:
            raise NotFoundError("Analysis job not found")
        
        job.status = JobStatus.CANCELLED
        await self.job_repo.update_analysis_job(job)
    
    async def get_analysis_progress(self, job_id: UUID) -> Dict[str, Any]:
        """Get analysis job progress."""
        job = await self.job_repo.get_analysis_job(job_id)
        if not job:
            raise NotFoundError("Analysis job not found")
        
        return {
            "status": job.status,
            "progress": job.progress,
            "started_at": job.started_at,
            "completed_at": job.completed_at,
        }
    
    async def get_analysis_results(self, job_id: UUID) -> Dict[str, Any]:
        """Get analysis job results."""
        job = await self.job_repo.get_analysis_job(job_id)
        if not job:
            raise NotFoundError("Analysis job not found")
        
        return {
            "semantic_understanding": job.semantic_understanding,
            "ui_analysis": job.ui_analysis,
            "feature_extraction": job.feature_extraction,
            "navigation_graph": job.navigation_graph,
            "value_proposition": job.value_proposition,
        }
    
    async def get_analysis_insights(self, job_id: UUID) -> Dict[str, Any]:
        """Get analysis insights."""
        job = await self.job_repo.get_analysis_job(job_id)
        if not job:
            raise NotFoundError("Analysis job not found")
        
        return {
            "summary": job.summary,
            "confidence_scores": job.confidence_scores,
        }
    
    async def get_website(self, website_id: UUID) -> Optional[Website]:
        """Get website by ID."""
        return await self.website_repo.get(website_id)