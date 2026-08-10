"""Export management API endpoints."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.dependencies import (
    get_current_user,
    get_export_service,
)
from app.models.user import User
from app.services.export_service import ExportService
from app.schemas.export import (
    ExportResponse,
    ExportListResponse,
    ExportCreateRequest,
    ExportUpdate,
)
from app.schemas.common import PaginatedResponse
from app.core.errors import NotFoundError

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[ExportListResponse])
async def list_exports(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    video_id: Optional[UUID] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    export_service: ExportService = Depends(get_export_service),
):
    """List exports."""
    skip = (page - 1) * page_size
    
    exports, total = await export_service.list_exports(
        user_id=current_user.id,
        video_id=video_id,
        status=status,
        skip=skip,
        limit=page_size,
    )
    
    return PaginatedResponse(
        items=exports,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.post("/", response_model=ExportResponse, status_code=status.HTTP_201_CREATED)
async def create_export(
    request: ExportCreateRequest,
    current_user: User = Depends(get_current_user),
    export_service: ExportService = Depends(get_export_service),
):
    """Create a new export."""
    try:
        export = await export_service.create_export(
            video_id=request.video_id,
            user_id=current_user.id,
            format=request.format,
            quality=request.quality,
            include_watermark=request.include_watermark,
        )
        return export
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get("/{export_id}", response_model=ExportResponse)
async def get_export(
    export_id: UUID,
    current_user: User = Depends(get_current_user),
    export_service: ExportService = Depends(get_export_service),
):
    """Get export by ID."""
    export = await export_service.get_export(export_id)
    if not export:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Export not found",
        )
    
    # Check access
    video = await export_service.get_video(export.video_id)
    project = await export_service.get_project(video.project_id)
    if project.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    return export


@router.patch("/{export_id}", response_model=ExportResponse)
async def update_export(
    export_id: UUID,
    request: ExportUpdate,
    current_user: User = Depends(get_current_user),
    export_service: ExportService = Depends(get_export_service),
):
    """Update export."""
    export = await export_service.get_export(export_id)
    if not export:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Export not found",
        )
    
    # Check access
    video = await export_service.get_video(export.video_id)
    project = await export_service.get_project(video.project_id)
    if project.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    updated = await export_service.update_export(
        export_id=export_id,
        updates=request.dict(exclude_unset=True),
    )
    return updated


@router.delete("/{export_id}")
async def delete_export(
    export_id: UUID,
    current_user: User = Depends(get_current_user),
    export_service: ExportService = Depends(get_export_service),
):
    """Delete export."""
    export = await export_service.get_export(export_id)
    if not export:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Export not found",
        )
    
    # Check access
    video = await export_service.get_video(export.video_id)
    project = await export_service.get_project(video.project_id)
    if project.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    await export_service.delete_export(export_id)
    return {"message": "Export deleted successfully"}


@router.get("/{export_id}/download")
async def download_export(
    export_id: UUID,
    current_user: User = Depends(get_current_user),
    export_service: ExportService = Depends(get_export_service),
):
    """Download export."""
    export = await export_service.get_export(export_id)
    if not export:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Export not found",
        )
    
    # Check access
    video = await export_service.get_video(export.video_id)
    project = await export_service.get_project(video.project_id)
    if project.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    url = await export_service.get_download_url(export_id)
    return {"download_url": url}


@router.get("/{export_id}/status")
async def get_export_status(
    export_id: UUID,
    current_user: User = Depends(get_current_user),
    export_service: ExportService = Depends(get_export_service),
):
    """Get export status."""
    status = await export_service.get_export_status(export_id)
    return status