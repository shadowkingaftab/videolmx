"""Asset management API endpoints."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File

from app.dependencies import (
    get_current_user,
    get_asset_service,
)
from app.models.user import User
from app.services.asset_service import AssetService
from app.schemas.asset import (
    AssetResponse,
    AssetListResponse,
    AssetUploadRequest,
    AssetUpdate,
)
from app.schemas.common import PaginatedResponse
from app.core.errors import NotFoundError, ValidationError

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[AssetListResponse])
async def list_assets(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    project_id: Optional[UUID] = None,
    asset_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    asset_service: AssetService = Depends(get_asset_service),
):
    """List assets."""
    skip = (page - 1) * page_size
    
    assets, total = await asset_service.list_assets(
        user_id=current_user.id,
        project_id=project_id,
        asset_type=asset_type,
        skip=skip,
        limit=page_size,
    )
    
    return PaginatedResponse(
        items=assets,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.post("/upload", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
async def upload_asset(
    project_id: UUID = Query(...),
    file: UploadFile = File(...),
    asset_type: str = Query(...),
    name: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    asset_service: AssetService = Depends(get_asset_service),
):
    """Upload a new asset."""
    try:
        asset = await asset_service.upload_asset(
            project_id=project_id,
            user_id=current_user.id,
            file=file,
            asset_type=asset_type,
            name=name,
        )
        return asset
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset(
    asset_id: UUID,
    current_user: User = Depends(get_current_user),
    asset_service: AssetService = Depends(get_asset_service),
):
    """Get asset by ID."""
    asset = await asset_service.get_asset(asset_id)
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found",
        )
    
    # Check access
    project = await asset_service.get_project(asset.project_id)
    if project.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    return asset


@router.patch("/{asset_id}", response_model=AssetResponse)
async def update_asset(
    asset_id: UUID,
    request: AssetUpdate,
    current_user: User = Depends(get_current_user),
    asset_service: AssetService = Depends(get_asset_service),
):
    """Update asset metadata."""
    asset = await asset_service.get_asset(asset_id)
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found",
        )
    
    # Check access
    project = await asset_service.get_project(asset.project_id)
    if project.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    updated = await asset_service.update_asset(
        asset_id=asset_id,
        updates=request.dict(exclude_unset=True),
    )
    return updated


@router.delete("/{asset_id}")
async def delete_asset(
    asset_id: UUID,
    current_user: User = Depends(get_current_user),
    asset_service: AssetService = Depends(get_asset_service),
):
    """Delete asset."""
    asset = await asset_service.get_asset(asset_id)
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found",
        )
    
    # Check access
    project = await asset_service.get_project(asset.project_id)
    if project.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    await asset_service.delete_asset(asset_id)
    return {"message": "Asset deleted successfully"}


@router.get("/{asset_id}/download")
async def download_asset(
    asset_id: UUID,
    current_user: User = Depends(get_current_user),
    asset_service: AssetService = Depends(get_asset_service),
):
    """Get asset download URL."""
    asset = await asset_service.get_asset(asset_id)
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found",
        )
    
    # Check access
    project = await asset_service.get_project(asset.project_id)
    if project.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    url = await asset_service.get_download_url(asset_id)
    return {"download_url": url}


@router.get("/{asset_id}/preview")
async def preview_asset(
    asset_id: UUID,
    current_user: User = Depends(get_current_user),
    asset_service: AssetService = Depends(get_asset_service),
):
    """Get asset preview URL."""
    asset = await asset_service.get_asset(asset_id)
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found",
        )
    
    # Check access
    project = await asset_service.get_project(asset.project_id)
    if project.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    url = await asset_service.get_preview_url(asset_id)
    return {"preview_url": url}


@router.post("/{asset_id}/process")
async def process_asset(
    asset_id: UUID,
    current_user: User = Depends(get_current_user),
    asset_service: AssetService = Depends(get_asset_service),
):
    """Process asset (generate thumbnails, optimize, etc.)."""
    asset = await asset_service.get_asset(asset_id)
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found",
        )
    
    # Check access
    project = await asset_service.get_project(asset.project_id)
    if project.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    job_id = await asset_service.process_asset(asset_id)
    return {
        "message": "Asset processing started",
        "job_id": job_id,
        "asset_id": asset_id,
    }


@router.get("/search")
async def search_assets(
    query: str = Query(...),
    project_id: Optional[UUID] = None,
    asset_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    asset_service: AssetService = Depends(get_asset_service),
):
    """Search assets."""
    results = await asset_service.search_assets(
        user_id=current_user.id,
        query=query,
        project_id=project_id,
        asset_type=asset_type,
    )
    return {"results": results}