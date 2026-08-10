"""Analysis job management API endpoints."""

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
from app.schemas.analysis import (
    AnalysisJobCreate,
    AnalysisJobResponse,
    AnalysisJobListResponse,
    AnalysisJobUpdate,
)
from app.schemas.common import PaginatedResponse
from app.core.errors import NotFoundError

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[AnalysisJobListResponse])
async def list_analysis_jobs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    website_id: Optional[UUID] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service),
):
    """List analysis jobs."""
    skip = (page - 1) * page_size
    
    jobs, total = await job_service.list_analysis_jobs(
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


@router.post("/", response_model=AnalysisJobResponse, status_code=status.HTTP_201_CREATED)
async def create_analysis_job(
    request: AnalysisJobCreate,
    current_user: User = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service),
):
    """Create a new analysis job."""
    try:
        job = await job_service.create_analysis_job(
            website_id=request.website_id,
            user_id=current_user.id,
            analysis_type=request.analysis_type,
            depth=request.depth,
        )
        return job
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get("/{job_id}", response_model=AnalysisJobResponse)
async def get_analysis_job(
    job_id: UUID,
    current_user: User = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service),
):
    """Get analysis job by ID."""
    job = await job_service.get_analysis_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis job not found",
        )
    
    # Check access
    website = await job_service.get_website(job.website_id)
    if website.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    return job


@router.patch("/{job_id}", response_model=AnalysisJobResponse)
async def update_analysis_job(
    job_id: UUID,
    request: AnalysisJobUpdate,
    current_user: User = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service),
):
    """Update analysis job."""
    job = await job_service.get_analysis_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis job not found",
        )
    
    # Check access
    website = await job_service.get_website(job.website_id)
    if website.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    updated = await job_service.update_analysis_job(
        job_id=job_id,
        updates=request.dict(exclude_unset=True),
    )
    return updated


@router.post("/{job_id}/cancel")
async def cancel_analysis_job(
    job_id: UUID,
    current_user: User = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service),
):
    """Cancel an analysis job."""
    job = await job_service.get_analysis_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis job not found",
        )
    
    # Check access
    website = await job_service.get_website(job.website_id)
    if website.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    await job_service.cancel_analysis_job(job_id)
    return {"message": "Analysis job cancelled"}


@router.get("/{job_id}/progress")
async def get_analysis_progress(
    job_id: UUID,
    current_user: User = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service),
):
    """Get analysis job progress."""
    job = await job_service.get_analysis_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis job not found",
        )
    
    progress = await job_service.get_analysis_progress(job_id)
    return progress


@router.get("/{job_id}/results")
async def get_analysis_results(
    job_id: UUID,
    current_user: User = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service),
):
    """Get analysis job results."""
    job = await job_service.get_analysis_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis job not found",
        )
    
    # Check access
    website = await job_service.get_website(job.website_id)
    if website.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    results = await job_service.get_analysis_results(job_id)
    return results


@router.get("/{job_id}/insights")
async def get_analysis_insights(
    job_id: UUID,
    current_user: User = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service),
):
    """Get analysis insights."""
    job = await job_service.get_analysis_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis job not found",
        )
    
    insights = await job_service.get_analysis_insights(job_id)
    return insights