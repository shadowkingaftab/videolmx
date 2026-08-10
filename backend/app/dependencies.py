"""FastAPI dependency injection."""

from typing import Optional, AsyncGenerator, Dict, Any
from uuid import UUID

from fastapi import Depends, Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db_session
from app.core.cache import get_cache
from app.core.task_queue import get_queue
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.services.project_service import ProjectService
from app.services.website_service import WebsiteService
from app.services.job_service import JobService
from app.services.storyboard_service import StoryboardService
from app.services.script_service import ScriptService
from app.services.video_service import VideoService
from app.repositories.user_repository import UserRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.website_repository import WebsiteRepository
from app.repositories.job_repository import JobRepository
from app.repositories.storyboard_repository import StoryboardRepository
from app.repositories.script_repository import ScriptRepository
from app.repositories.asset_repository import AssetRepository
from app.repositories.video_repository import VideoRepository
from app.models.user import User
from app.core.errors import AuthenticationError, AuthorizationError

security = HTTPBearer()


# Database dependencies
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    async for session in get_db_session():
        yield session


# Repository dependencies
async def get_user_repository(
    db: AsyncSession = Depends(get_db)
) -> UserRepository:
    """Get user repository."""
    return UserRepository(db)


async def get_project_repository(
    db: AsyncSession = Depends(get_db)
) -> ProjectRepository:
    """Get project repository."""
    return ProjectRepository(db)


async def get_website_repository(
    db: AsyncSession = Depends(get_db)
) -> WebsiteRepository:
    """Get website repository."""
    return WebsiteRepository(db)


async def get_job_repository(
    db: AsyncSession = Depends(get_db)
) -> JobRepository:
    """Get job repository."""
    return JobRepository(db)


async def get_storyboard_repository(
    db: AsyncSession = Depends(get_db)
) -> StoryboardRepository:
    """Get storyboard repository."""
    return StoryboardRepository(db)


async def get_script_repository(
    db: AsyncSession = Depends(get_db)
) -> ScriptRepository:
    """Get script repository."""
    return ScriptRepository(db)


async def get_asset_repository(
    db: AsyncSession = Depends(get_db)
) -> AssetRepository:
    """Get asset repository."""
    return AssetRepository(db)


async def get_video_repository(
    db: AsyncSession = Depends(get_db)
) -> VideoRepository:
    """Get video repository."""
    return VideoRepository(db)


# Service dependencies
async def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repository),
) -> AuthService:
    """Get authentication service."""
    return AuthService(user_repo)


async def get_user_service(
    user_repo: UserRepository = Depends(get_user_repository),
) -> UserService:
    """Get user service."""
    return UserService(user_repo)


async def get_project_service(
    project_repo: ProjectRepository = Depends(get_project_repository),
    user_repo: UserRepository = Depends(get_user_repository),
) -> ProjectService:
    """Get project service."""
    return ProjectService(project_repo, user_repo)


async def get_website_service(
    website_repo: WebsiteRepository = Depends(get_website_repository),
    project_repo: ProjectRepository = Depends(get_project_repository),
) -> WebsiteService:
    """Get website service."""
    return WebsiteService(website_repo, project_repo)


async def get_job_service(
    job_repo: JobRepository = Depends(get_job_repository),
    website_repo: WebsiteRepository = Depends(get_website_repository),
) -> JobService:
    """Get job service."""
    return JobService(job_repo, website_repo)


async def get_storyboard_service(
    storyboard_repo: StoryboardRepository = Depends(get_storyboard_repository),
    project_repo: ProjectRepository = Depends(get_project_repository),
) -> StoryboardService:
    """Get storyboard service."""
    return StoryboardService(storyboard_repo, project_repo)


async def get_script_service(
    script_repo: ScriptRepository = Depends(get_script_repository),
    storyboard_repo: StoryboardRepository = Depends(get_storyboard_repository),
) -> ScriptService:
    """Get script service."""
    return ScriptService(script_repo, storyboard_repo)


async def get_video_service(
    video_repo: VideoRepository = Depends(get_video_repository),
    project_repo: ProjectRepository = Depends(get_project_repository),
) -> VideoService:
    """Get video service."""
    return VideoService(video_repo, project_repo)


# Authentication dependencies
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    """Get current authenticated user."""
    token = credentials.credentials
    user = await auth_service.get_user_from_token(token)
    if not user:
        raise AuthenticationError("Invalid authentication credentials")
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise AuthenticationError("Inactive user")
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Get current admin user."""
    if not current_user.is_admin:
        raise AuthorizationError("Admin privileges required")
    return current_user


# Cache dependencies
async def get_cache_client():
    """Get cache client."""
    return await get_cache()


# Queue dependencies
async def get_queue_client():
    """Get queue client."""
    return await get_queue()


# Utility dependencies
async def get_current_project(
    project_id: UUID,
    project_service: ProjectService = Depends(get_project_service),
    current_user: User = Depends(get_current_active_user),
):
    """Get project with ownership validation."""
    project = await project_service.get_project(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check if user has access
    if project.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return project


async def get_current_website(
    website_id: UUID,
    website_service: WebsiteService = Depends(get_website_service),
    current_user: User = Depends(get_current_active_user),
):
    """Get website with ownership validation."""
    website = await website_service.get_website(website_id)
    if not website:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Website not found"
        )
    
    # Check if user has access through project
    project = await website_service.get_project(website.project_id)
    if project.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return website


# Request context
async def get_request_context(request: Request) -> Dict[str, Any]:
    """Get request context for logging and tracing."""
    return {
        "request_id": request.state.request_id,
        "client_ip": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
        "path": request.url.path,
        "method": request.method,
    }