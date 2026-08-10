"""Script management API endpoints."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.dependencies import (
    get_current_user,
    get_script_service,
)
from app.models.user import User
from app.services.script_service import ScriptService
from app.schemas.script import (
    ScriptCreate,
    ScriptUpdate,
    ScriptResponse,
    ScriptListResponse,
    ScriptGenerateRequest,
)
from app.schemas.common import PaginatedResponse
from app.core.errors import NotFoundError, ValidationError

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[ScriptListResponse])
async def list_scripts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    storyboard_id: Optional[UUID] = None,
    current_user: User = Depends(get_current_user),
    script_service: ScriptService = Depends(get_script_service),
):
    """List scripts."""
    skip = (page - 1) * page_size
    
    scripts, total = await script_service.list_scripts(
        user_id=current_user.id,
        storyboard_id=storyboard_id,
        skip=skip,
        limit=page_size,
    )
    
    return PaginatedResponse(
        items=scripts,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.post("/", response_model=ScriptResponse, status_code=status.HTTP_201_CREATED)
async def create_script(
    request: ScriptCreate,
    current_user: User = Depends(get_current_user),
    script_service: ScriptService = Depends(get_script_service),
):
    """Create a new script."""
    try:
        script = await script_service.create_script(
            storyboard_id=request.storyboard_id,
            user_id=current_user.id,
            name=request.name,
            language=request.language,
        )
        return script
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get("/{script_id}", response_model=ScriptResponse)
async def get_script(
    script_id: UUID,
    current_user: User = Depends(get_current_user),
    script_service: ScriptService = Depends(get_script_service),
):
    """Get script by ID."""
    script = await script_service.get_script(script_id)
    if not script:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Script not found",
        )
    
    # Check access
    storyboard = await script_service.get_storyboard(script.storyboard_id)
    project = await script_service.get_project(storyboard.project_id)
    if project.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    return script


@router.patch("/{script_id}", response_model=ScriptResponse)
async def update_script(
    script_id: UUID,
    request: ScriptUpdate,
    current_user: User = Depends(get_current_user),
    script_service: ScriptService = Depends(get_script_service),
):
    """Update script."""
    script = await script_service.get_script(script_id)
    if not script:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Script not found",
        )
    
    # Check access
    storyboard = await script_service.get_storyboard(script.storyboard_id)
    project = await script_service.get_project(storyboard.project_id)
    if project.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    updated = await script_service.update_script(
        script_id=script_id,
        updates=request.dict(exclude_unset=True),
    )
    return updated


@router.delete("/{script_id}")
async def delete_script(
    script_id: UUID,
    current_user: User = Depends(get_current_user),
    script_service: ScriptService = Depends(get_script_service),
):
    """Delete script."""
    script = await script_service.get_script(script_id)
    if not script:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Script not found",
        )
    
    # Check access
    storyboard = await script_service.get_storyboard(script.storyboard_id)
    project = await script_service.get_project(storyboard.project_id)
    if project.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    await script_service.delete_script(script_id)
    return {"message": "Script deleted successfully"}


@router.post("/{script_id}/generate")
async def generate_script(
    script_id: UUID,
    request: ScriptGenerateRequest,
    current_user: User = Depends(get_current_user),
    script_service: ScriptService = Depends(get_script_service),
):
    """Generate script content."""
    script = await script_service.get_script(script_id)
    if not script:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Script not found",
        )
    
    # Check access
    storyboard = await script_service.get_storyboard(script.storyboard_id)
    project = await script_service.get_project(storyboard.project_id)
    if project.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    job_id = await script_service.generate_script(
        script_id=script_id,
        tone=request.tone,
        length=request.length,
        include_captions=request.include_captions,
    )
    return {
        "message": "Script generation started",
        "job_id": job_id,
        "script_id": script_id,
    }


@router.get("/{script_id}/content")
async def get_script_content(
    script_id: UUID,
    current_user: User = Depends(get_current_user),
    script_service: ScriptService = Depends(get_script_service),
):
    """Get full script content."""
    script = await script_service.get_script(script_id)
    if not script:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Script not found",
        )
    
    content = await script_service.get_script_content(script_id)
    return content


@router.post("/{script_id}/regenerate")
async def regenerate_script(
    script_id: UUID,
    current_user: User = Depends(get_current_user),
    script_service: ScriptService = Depends(get_script_service),
):
    """Regenerate script with new parameters."""
    script = await script_service.get_script(script_id)
    if not script:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Script not found",
        )
    
    job_id = await script_service.regenerate_script(script_id)
    return {
        "message": "Script regeneration started",
        "job_id": job_id,
        "script_id": script_id,
    }


@router.get("/{script_id}/preview")
async def preview_script(
    script_id: UUID,
    current_user: User = Depends(get_current_user),
    script_service: ScriptService = Depends(get_script_service),
):
    """Get script preview."""
    preview = await script_service.get_script_preview(script_id)
    return preview