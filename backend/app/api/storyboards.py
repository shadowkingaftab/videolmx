"""Storyboard management API endpoints."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.dependencies import (
    get_current_user,
    get_storyboard_service,
    get_current_project,
)
from app.models.user import User
from app.models.project import Project
from app.services.storyboard_service import StoryboardService
from app.schemas.storyboard import (
    StoryboardCreate,
    StoryboardUpdate,
    StoryboardResponse,
    StoryboardListResponse,
    SceneCreate,
    SceneUpdate,
    SceneResponse,
)
from app.schemas.common import PaginatedResponse
from app.core.errors import NotFoundError, ValidationError

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[StoryboardListResponse])
async def list_storyboards(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    project_id: Optional[UUID] = None,
    current_user: User = Depends(get_current_user),
    storyboard_service: StoryboardService = Depends(get_storyboard_service),
):
    """List storyboards."""
    skip = (page - 1) * page_size
    
    storyboards, total = await storyboard_service.list_storyboards(
        user_id=current_user.id,
        project_id=project_id,
        skip=skip,
        limit=page_size,
    )
    
    return PaginatedResponse(
        items=storyboards,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.post("/", response_model=StoryboardResponse, status_code=status.HTTP_201_CREATED)
async def create_storyboard(
    request: StoryboardCreate,
    current_user: User = Depends(get_current_user),
    storyboard_service: StoryboardService = Depends(get_storyboard_service),
):
    """Create a new storyboard."""
    try:
        storyboard = await storyboard_service.create_storyboard(
            project_id=request.project_id,
            user_id=current_user.id,
            name=request.name,
            description=request.description,
            template=request.template,
        )
        return storyboard
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get("/{storyboard_id}", response_model=StoryboardResponse)
async def get_storyboard(
    storyboard_id: UUID,
    current_user: User = Depends(get_current_user),
    storyboard_service: StoryboardService = Depends(get_storyboard_service),
):
    """Get storyboard by ID."""
    storyboard = await storyboard_service.get_storyboard(storyboard_id)
    if not storyboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Storyboard not found",
        )
    
    # Check access
    project = await storyboard_service.get_project(storyboard.project_id)
    if project.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    return storyboard


@router.patch("/{storyboard_id}", response_model=StoryboardResponse)
async def update_storyboard(
    storyboard_id: UUID,
    request: StoryboardUpdate,
    current_user: User = Depends(get_current_user),
    storyboard_service: StoryboardService = Depends(get_storyboard_service),
):
    """Update storyboard."""
    storyboard = await storyboard_service.get_storyboard(storyboard_id)
    if not storyboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Storyboard not found",
        )
    
    # Check access
    project = await storyboard_service.get_project(storyboard.project_id)
    if project.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    updated = await storyboard_service.update_storyboard(
        storyboard_id=storyboard_id,
        updates=request.dict(exclude_unset=True),
    )
    return updated


@router.delete("/{storyboard_id}")
async def delete_storyboard(
    storyboard_id: UUID,
    current_user: User = Depends(get_current_user),
    storyboard_service: StoryboardService = Depends(get_storyboard_service),
):
    """Delete storyboard."""
    storyboard = await storyboard_service.get_storyboard(storyboard_id)
    if not storyboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Storyboard not found",
        )
    
    # Check access
    project = await storyboard_service.get_project(storyboard.project_id)
    if project.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    await storyboard_service.delete_storyboard(storyboard_id)
    return {"message": "Storyboard deleted successfully"}


@router.post("/{storyboard_id}/generate")
async def generate_storyboard(
    storyboard_id: UUID,
    current_user: User = Depends(get_current_user),
    storyboard_service: StoryboardService = Depends(get_storyboard_service),
):
    """Generate storyboard from website analysis."""
    storyboard = await storyboard_service.get_storyboard(storyboard_id)
    if not storyboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Storyboard not found",
        )
    
    # Check access
    project = await storyboard_service.get_project(storyboard.project_id)
    if project.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    job_id = await storyboard_service.generate_storyboard(storyboard_id)
    return {
        "message": "Storyboard generation started",
        "job_id": job_id,
        "storyboard_id": storyboard_id,
    }


@router.get("/{storyboard_id}/scenes")
async def list_scenes(
    storyboard_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    storyboard_service: StoryboardService = Depends(get_storyboard_service),
):
    """List scenes in a storyboard."""
    storyboard = await storyboard_service.get_storyboard(storyboard_id)
    if not storyboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Storyboard not found",
        )
    
    skip = (page - 1) * page_size
    scenes, total = await storyboard_service.list_scenes(
        storyboard_id=storyboard_id,
        skip=skip,
        limit=page_size,
    )
    
    return {
        "items": scenes,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size,
    }


@router.post("/{storyboard_id}/scenes", response_model=SceneResponse)
async def create_scene(
    storyboard_id: UUID,
    request: SceneCreate,
    current_user: User = Depends(get_current_user),
    storyboard_service: StoryboardService = Depends(get_storyboard_service),
):
    """Create a new scene in a storyboard."""
    storyboard = await storyboard_service.get_storyboard(storyboard_id)
    if not storyboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Storyboard not found",
        )
    
    # Check access
    project = await storyboard_service.get_project(storyboard.project_id)
    if project.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    scene = await storyboard_service.create_scene(
        storyboard_id=storyboard_id,
        **request.dict(),
    )
    return scene


@router.patch("/{storyboard_id}/scenes/{scene_id}", response_model=SceneResponse)
async def update_scene(
    storyboard_id: UUID,
    scene_id: UUID,
    request: SceneUpdate,
    current_user: User = Depends(get_current_user),
    storyboard_service: StoryboardService = Depends(get_storyboard_service),
):
    """Update a scene."""
    scene = await storyboard_service.get_scene(scene_id)
    if not scene:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scene not found",
        )
    
    # Check access
    storyboard = await storyboard_service.get_storyboard(storyboard_id)
    project = await storyboard_service.get_project(storyboard.project_id)
    if project.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    updated = await storyboard_service.update_scene(
        scene_id=scene_id,
        updates=request.dict(exclude_unset=True),
    )
    return updated


@router.delete("/{storyboard_id}/scenes/{scene_id}")
async def delete_scene(
    storyboard_id: UUID,
    scene_id: UUID,
    current_user: User = Depends(get_current_user),
    storyboard_service: StoryboardService = Depends(get_storyboard_service),
):
    """Delete a scene."""
    scene = await storyboard_service.get_scene(scene_id)
    if not scene:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scene not found",
        )
    
    # Check access
    storyboard = await storyboard_service.get_storyboard(storyboard_id)
    project = await storyboard_service.get_project(storyboard.project_id)
    if project.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    await storyboard_service.delete_scene(scene_id)
    return {"message": "Scene deleted successfully"}


@router.post("/{storyboard_id}/scenes/reorder")
async def reorder_scenes(
    storyboard_id: UUID,
    scene_order: list[UUID],
    current_user: User = Depends(get_current_user),
    storyboard_service: StoryboardService = Depends(get_storyboard_service),
):
    """Reorder scenes in a storyboard."""
    storyboard = await storyboard_service.get_storyboard(storyboard_id)
    if not storyboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Storyboard not found",
        )
    
    # Check access
    project = await storyboard_service.get_project(storyboard.project_id)
    if project.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    await storyboard_service.reorder_scenes(storyboard_id, scene_order)
    return {"message": "Scenes reordered successfully"}