"""Video management API endpoints."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import FileResponse

from app.dependencies import (
    get_current_user,
    get_video_service,
)
from app.models.user import User
from app.services.video_service import VideoService
from app.schemas.video import (
    VideoCreate,
    VideoUpdate,
    VideoResponse,
    VideoListResponse,
    VideoRenderRequest,
    VideoExportRequest,
)
from app.schemas.common import PaginatedResponse
from app.core.errors import NotFoundError, ValidationError

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[VideoListResponse])
async def list_videos(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    project_id: Optional[UUID] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    video_service: VideoService = Depends(get_video_service),
):
    """List videos."""
    skip = (page - 1) * page_size
    
    videos, total = await video_service.list_videos(
        user_id=current_user.id,
        project_id=project_id,
        status=status,
        skip=skip,
        limit=page_size,
    )
    
    return PaginatedResponse(
        items=videos,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.post("/", response_model=VideoResponse, status_code=status.HTTP_201_CREATED)
async def create_video(
    request: VideoCreate,
    current_user: User = Depends(get_current_user),
    video_service: VideoService = Depends(get_video_service),
):
    """Create a new video."""
    try:
        video = await video_service.create_video(
            project_id=request.project_id,
            user_id=current_user.id,
            name=request.name,
            description=request.description,
            storyboard_id=request.storyboard_id,
            script_id=request.script_id,
            narration_id=request.narration_id,
        )
        return video
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get("/{video_id}", response_model=VideoResponse)
async def get_video(
    video_id: UUID,
    current_user: User = Depends(get_current_user),
    video_service: VideoService = Depends(get_video_service),
):
    """Get video by ID."""
    video = await video_service.get_video(video_id)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found",
        )
    
    # Check access
    project = await video_service.get_project(video.project_id)
    if project.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    return video


@router.patch("/{video_id}", response_model=VideoResponse)
async def update_video(
    video_id: UUID,
    request: VideoUpdate,
    current_user: User = Depends(get_current_user),
    video_service: VideoService = Depends(get_video_service),
):
    """Update video metadata."""
    video = await video_service.get_video(video_id)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found",
        )
    
    # Check access
    project = await video_service.get_project(video.project_id)
    if project.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    updated = await video_service.update_video(
        video_id=video_id,
        updates=request.dict(exclude_unset=True),
    )
    return updated


@router.delete("/{video_id}")
async def delete_video(
    video_id: UUID,
    current_user: User = Depends(get_current_user),
    video_service: VideoService = Depends(get_video_service),
):
    """Delete video."""
    video = await video_service.get_video(video_id)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found",
        )
    
    # Check access
    project = await video_service.get_project(video.project_id)
    if project.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    await video_service.delete_video(video_id)
    return {"message": "Video deleted successfully"}


@router.post("/{video_id}/render")
async def render_video(
    video_id: UUID,
    request: VideoRenderRequest,
    current_user: User = Depends(get_current_user),
    video_service: VideoService = Depends(get_video_service),
):
    """Render video."""
    video = await video_service.get_video(video_id)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found",
        )
    
    # Check access
    project = await video_service.get_project(video.project_id)
    if project.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    job_id = await video_service.render_video(
        video_id=video_id,
        resolution=request.resolution,
        fps=request.fps,
        quality=request.quality,
        include_captions=request.include_captions,
        include_background_music=request.include_background_music,
    )
    return {
        "message": "Video rendering started",
        "job_id": job_id,
        "video_id": video_id,
    }


@router.get("/{video_id}/status")
async def get_video_status(
    video_id: UUID,
    current_user: User = Depends(get_current_user),
    video_service: VideoService = Depends(get_video_service),
):
    """Get video rendering status."""
    video = await video_service.get_video(video_id)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found",
        )
    
    status = await video_service.get_video_status(video_id)
    return status


@router.get("/{video_id}/download")
async def download_video(
    video_id: UUID,
    current_user: User = Depends(get_current_user),
    video_service: VideoService = Depends(get_video_service),
):
    """Download video."""
    video = await video_service.get_video(video_id)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found",
        )
    
    # Check access
    project = await video_service.get_project(video.project_id)
    if project.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    url = await video_service.get_download_url(video_id)
    return {"download_url": url}


@router.get("/{video_id}/stream")
async def stream_video(
    video_id: UUID,
    current_user: User = Depends(get_current_user),
    video_service: VideoService = Depends(get_video_service),
):
    """Stream video for preview."""
    video = await video_service.get_video(video_id)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found",
        )
    
    # Check access
    project = await video_service.get_project(video.project_id)
    if project.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    url = await video_service.get_stream_url(video_id)
    return {"stream_url": url}


@router.post("/{video_id}/export")
async def export_video(
    video_id: UUID,
    request: VideoExportRequest,
    current_user: User = Depends(get_current_user),
    video_service: VideoService = Depends(get_video_service),
):
    """Export video to different format."""
    video = await video_service.get_video(video_id)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found",
        )
    
    # Check access
    project = await video_service.get_project(video.project_id)
    if project.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    job_id = await video_service.export_video(
        video_id=video_id,
        format=request.format,
        quality=request.quality,
        include_watermark=request.include_watermark,
    )
    return {
        "message": "Video export started",
        "job_id": job_id,
        "video_id": video_id,
    }


@router.get("/{video_id}/exports")
async def list_exports(
    video_id: UUID,
    current_user: User = Depends(get_current_user),
    video_service: VideoService = Depends(get_video_service),
):
    """List video exports."""
    exports = await video_service.list_exports(video_id)
    return {"exports": exports}