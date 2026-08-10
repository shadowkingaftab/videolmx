"""Project management API endpoints."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.dependencies import (
    get_current_user,
    get_project_service,
    get_current_project,
)
from app.models.user import User
from app.models.project import Project
from app.services.project_service import ProjectService
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListResponse,
)
from app.schemas.common import PaginatedResponse
from app.core.errors import NotFoundError

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[ProjectListResponse])
async def list_projects(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service),
):
    """List all projects for the current user."""
    skip = (page - 1) * page_size
    
    projects, total = await project_service.list_projects(
        user_id=current_user.id,
        skip=skip,
        limit=page_size,
        status=status,
    )
    
    return PaginatedResponse(
        items=projects,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    request: ProjectCreate,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service),
):
    """Create a new project."""
    project = await project_service.create_project(
        user_id=current_user.id,
        name=request.name,
        description=request.description,
    )
    return project


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project: Project = Depends(get_current_project),
):
    """Get project by ID."""
    return project


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    request: ProjectUpdate,
    project: Project = Depends(get_current_project),
    project_service: ProjectService = Depends(get_project_service),
):
    """Update project."""
    updated = await project_service.update_project(
        project_id=project.id,
        updates=request.dict(exclude_unset=True),
    )
    return updated


@router.delete("/{project_id}")
async def delete_project(
    project: Project = Depends(get_current_project),
    project_service: ProjectService = Depends(get_project_service),
):
    """Delete project."""
    await project_service.delete_project(project.id)
    return {"message": "Project deleted successfully"}


@router.post("/{project_id}/archive")
async def archive_project(
    project: Project = Depends(get_current_project),
    project_service: ProjectService = Depends(get_project_service),
):
    """Archive project."""
    await project_service.archive_project(project.id)
    return {"message": "Project archived successfully"}


@router.post("/{project_id}/restore")
async def restore_project(
    project: Project = Depends(get_current_project),
    project_service: ProjectService = Depends(get_project_service),
):
    """Restore archived project."""
    await project_service.restore_project(project.id)
    return {"message": "Project restored successfully"}


@router.get("/{project_id}/stats")
async def get_project_stats(
    project: Project = Depends(get_current_project),
    project_service: ProjectService = Depends(get_project_service),
):
    """Get project statistics."""
    stats = await project_service.get_project_stats(project.id)
    return stats


@router.get("/{project_id}/websites")
async def list_project_websites(
    project: Project = Depends(get_current_project),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    project_service: ProjectService = Depends(get_project_service),
):
    """List websites in a project."""
    skip = (page - 1) * page_size
    websites, total = await project_service.list_project_websites(
        project_id=project.id,
        skip=skip,
        limit=page_size,
    )
    
    return {
        "items": websites,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size,
    }


@router.get("/{project_id}/videos")
async def list_project_videos(
    project: Project = Depends(get_current_project),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    project_service: ProjectService = Depends(get_project_service),
):
    """List videos in a project."""
    skip = (page - 1) * page_size
    videos, total = await project_service.list_project_videos(
        project_id=project.id,
        skip=skip,
        limit=page_size,
    )
    
    return {
        "items": videos,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size,
    }