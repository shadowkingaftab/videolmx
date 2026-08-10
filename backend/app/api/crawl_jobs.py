"""Crawl job management API endpoints."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.dependencies import (
    get_current_user,
    get_job_service,
    get_current_website,
)
from app.models.user import User
from app.models.website import Website
from app.services.job_service import JobService
from app.schemas.crawl import (
    CrawlJobCreate,
    CrawlJobResponse,
    CrawlJobListResponse,
    CrawlJobUpdate,
)
from app.schemas.common import PaginatedResponse
from app.core.errors import NotFoundError

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[CrawlJobListResponse])
async def list_crawl_jobs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    website_id: Optional[UUID] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service),
):
    """List crawl jobs."""
    skip = (page - 1) * page_size
    
    jobs, total = await job_service.list_crawl_jobs(
        user_id=current_user.id,
        website_id=website_id,
        status=status,
        skip=skip,
        limit=page_size,
    )
    
    return PaginatedResponse(
        items=jobs,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.post("/", response_model=CrawlJobResponse, status_code=status.HTTP_201_CREATED)
async def create_crawl_job(
    request: CrawlJobCreate,
    current_user: User = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service),
):
    """Create a new crawl job."""
    try:
        job = await job_service.create_crawl_job(
            website_id=request.website_id,
            user_id=current_user.id,
            max_pages=request.max_pages,
            depth=request.depth,
            include_assets=request.include_assets,
            respect_robots=request.respect_robots,
        )
        return job
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get("/{job_id}", response_model=CrawlJobResponse)
async def get_crawl_job(
    job_id: UUID,
    current_user: User = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service),
):
    """Get crawl job by ID."""
    job = await job_service.get_crawl_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crawl job not found",
        )
    
    # Check access
    website = await job_service.get_website(job.website_id)
    if website.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    return job


@router.patch("/{job_id}", response_model=CrawlJobResponse)
async def update_crawl_job(
    job_id: UUID,
    request: CrawlJobUpdate,
    current_user: User = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service),
):
    """Update crawl job."""
    job = await job_service.get_crawl_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crawl job not found",
        )
    
    # Check access
    website = await job_service.get_website(job.website_id)
    if website.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    updated = await job_service.update_crawl_job(
        job_id=job_id,
        updates=request.dict(exclude_unset=True),
    )
    return updated


@router.post("/{job_id}/cancel")
async def cancel_crawl_job(
    job_id: UUID,
    current_user: User = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service),
):
    """Cancel a crawl job."""
    job = await job_service.get_crawl_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crawl job not found",
        )
    
    # Check access
    website = await job_service.get_website(job.website_id)
    if website.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    await job_service.cancel_crawl_job(job_id)
    return {"message": "Crawl job cancelled"}


@router.get("/{job_id}/progress")
async def get_crawl_progress(
    job_id: UUID,
    current_user: User = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service),
):
    """Get crawl job progress."""
    job = await job_service.get_crawl_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crawl job not found",
        )
    
    progress = await job_service.get_crawl_progress(job_id)
    return progress


@router.get("/{job_id}/results")
async def get_crawl_results(
    job_id: UUID,
    current_user: User = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service),
):
    """Get crawl job results."""
    job = await job_service.get_crawl_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crawl job not found",
        )
    
    # Check access
    website = await job_service.get_website(job.website_id)
    if website.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    results = await job_service.get_crawl_results(job_id)
    return results


@router.get("/{job_id}/pages")
async def list_crawl_pages(
    job_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service),
):
    """List pages from a crawl job."""
    job = await job_service.get_crawl_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crawl job not found",
        )
    
    skip = (page - 1) * page_size
    pages, total = await job_service.list_crawl_pages(
        job_id=job_id,
        skip=skip,
        limit=page_size,
    )
    
    return {
        "items": pages,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size,
    }