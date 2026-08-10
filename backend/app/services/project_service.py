"""Project service."""

from typing import Optional, List, Tuple, Dict, Any
from uuid import UUID

from app.models.project import Project
from app.repositories.project_repository import ProjectRepository
from app.repositories.user_repository import UserRepository
from app.core.errors import NotFoundError, AuthorizationError
from app.constants import ProjectStatus


class ProjectService:
    """Project service."""
    
    def __init__(
        self,
        project_repo: ProjectRepository,
        user_repo: UserRepository
    ):
        self.project_repo = project_repo
        self.user_repo = user_repo
    
    async def create_project(
        self,
        user_id: UUID,
        name: str,
        description: Optional[str] = None
    ) -> Project:
        """Create a new project."""
        user = await self.user_repo.get(user_id)
        if not user:
            raise NotFoundError("User not found")
        
        project = Project(
            user_id=user_id,
            name=name,
            description=description,
            status=ProjectStatus.ACTIVE,
        )
        
        return await self.project_repo.create(project)
    
    async def get_project(self, project_id: UUID) -> Optional[Project]:
        """Get project by ID."""
        return await self.project_repo.get(project_id)
    
    async def list_projects(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None
    ) -> Tuple[List[Project], int]:
        """List projects for a user."""
        return await self.project_repo.list_by_user(
            user_id=user_id,
            skip=skip,
            limit=limit,
            status=status
        )
    
    async def update_project(
        self,
        project_id: UUID,
        updates: Dict[str, Any]
    ) -> Project:
        """Update project."""
        project = await self.project_repo.get(project_id)
        if not project:
            raise NotFoundError("Project not found")
        
        for key, value in updates.items():
            if hasattr(project, key):
                setattr(project, key, value)
        
        return await self.project_repo.update(project)
    
    async def delete_project(self, project_id: UUID) -> None:
        """Delete project."""
        project = await self.project_repo.get(project_id)
        if not project:
            raise NotFoundError("Project not found")
        
        # Soft delete
        project.status = ProjectStatus.DELETED
        await self.project_repo.update(project)
    
    async def archive_project(self, project_id: UUID) -> None:
        """Archive project."""
        project = await self.project_repo.get(project_id)
        if not project:
            raise NotFoundError("Project not found")
        
        project.status = ProjectStatus.ARCHIVED
        await self.project_repo.update(project)
    
    async def restore_project(self, project_id: UUID) -> None:
        """Restore archived project."""
        project = await self.project_repo.get(project_id)
        if not project:
            raise NotFoundError("Project not found")
        
        project.status = ProjectStatus.ACTIVE
        await self.project_repo.update(project)
    
    async def get_project_stats(self, project_id: UUID) -> Dict[str, Any]:
        """Get project statistics."""
        # This would aggregate stats from related tables
        return {
            "total_websites": 0,
            "total_videos": 0,
            "total_assets": 0,
            "total_scenes": 0,
        }
    
    async def list_project_websites(
        self,
        project_id: UUID,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[Dict], int]:
        """List websites in a project."""
        # This would be implemented with website repository
        return [], 0
    
    async def list_project_videos(
        self,
        project_id: UUID,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[Dict], int]:
        """List videos in a project."""
        # This would be implemented with video repository
        return [], 0