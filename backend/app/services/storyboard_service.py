"""Storyboard service."""

from typing import Optional, List, Tuple, Dict, Any
from uuid import UUID

from app.models.storyboard import Storyboard, Scene
from app.repositories.storyboard_repository import StoryboardRepository
from app.repositories.project_repository import ProjectRepository
from app.core.errors import NotFoundError
from app.core.task_queue import get_queue


class StoryboardService:
    """Storyboard service."""
    
    def __init__(
        self,
        storyboard_repo: StoryboardRepository,
        project_repo: ProjectRepository
    ):
        self.storyboard_repo = storyboard_repo
        self.project_repo = project_repo
    
    async def create_storyboard(
        self,
        project_id: UUID,
        user_id: UUID,
        name: str,
        description: Optional[str] = None,
        template: str = "default"
    ) -> Storyboard:
        """Create a new storyboard."""
        project = await self.project_repo.get(project_id)
        if not project:
            raise NotFoundError("Project not found")
        
        storyboard = Storyboard(
            project_id=project_id,
            name=name,
            description=description,
            template=template,
        )
        
        return await self.storyboard_repo.create(storyboard)
    
    async def get_storyboard(self, storyboard_id: UUID) -> Optional[Storyboard]:
        """Get storyboard by ID."""
        return await self.storyboard_repo.get(storyboard_id)
    
    async def list_storyboards(
        self,
        user_id: UUID,
        project_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[Storyboard], int]:
        """List storyboards."""
        return await self.storyboard_repo.list_by_user(
            user_id=user_id,
            project_id=project_id,
            skip=skip,
            limit=limit
        )
    
    async def update_storyboard(
        self,
        storyboard_id: UUID,
        updates: Dict[str, Any]
    ) -> Storyboard:
        """Update storyboard."""
        storyboard = await self.storyboard_repo.get(storyboard_id)
        if not storyboard:
            raise NotFoundError("Storyboard not found")
        
        for key, value in updates.items():
            if hasattr(storyboard, key):
                setattr(storyboard, key, value)
        
        return await self.storyboard_repo.update(storyboard)
    
    async def delete_storyboard(self, storyboard_id: UUID) -> None:
        """Delete storyboard."""
        storyboard = await self.storyboard_repo.get(storyboard_id)
        if not storyboard:
            raise NotFoundError("Storyboard not found")
        
        await self.storyboard_repo.delete(storyboard)
    
    async def generate_storyboard(self, storyboard_id: UUID) -> UUID:
        """Generate storyboard from website analysis."""
        storyboard = await self.storyboard_repo.get(storyboard_id)
        if not storyboard:
            raise NotFoundError("Storyboard not found")
        
        # Queue generation job
        queue = await get_queue()
        await queue.enqueue(
            'script_worker.generate_storyboard',
            args=[str(storyboard_id)],
            queue='script',
        )
        
        return storyboard_id
    
    async def create_scene(
        self,
        storyboard_id: UUID,
        order: int,
        title: str,
        description: Optional[str] = None,
        scene_type: str = "feature",
        duration: float = 5.0,
        **kwargs
    ) -> Scene:
        """Create a new scene."""
        storyboard = await self.storyboard_repo.get(storyboard_id)
        if not storyboard:
            raise NotFoundError("Storyboard not found")
        
        scene = Scene(
            storyboard_id=storyboard_id,
            order=order,
            title=title,
            description=description,
            scene_type=scene_type,
            duration=duration,
            **kwargs
        )
        
        scene = await self.storyboard_repo.create_scene(scene)
        
        # Update storyboard scene count
        storyboard.total_scenes += 1
        await self.storyboard_repo.update(storyboard)
        
        return scene
    
    async def get_scene(self, scene_id: UUID) -> Optional[Scene]:
        """Get scene by ID."""
        return await self.storyboard_repo.get_scene(scene_id)
    
    async def list_scenes(
        self,
        storyboard_id: UUID,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[Scene], int]:
        """List scenes in a storyboard."""
        return await self.storyboard_repo.list_scenes(
            storyboard_id=storyboard_id,
            skip=skip,
            limit=limit
        )
    
    async def update_scene(
        self,
        scene_id: UUID,
        updates: Dict[str, Any]
    ) -> Scene:
        """Update scene."""
        scene = await self.storyboard_repo.get_scene(scene_id)
        if not scene:
            raise NotFoundError("Scene not found")
        
        for key, value in updates.items():
            if hasattr(scene, key):
                setattr(scene, key, value)
        
        return await self.storyboard_repo.update_scene(scene)
    
    async def delete_scene(self, scene_id: UUID) -> None:
        """Delete scene."""
        scene = await self.storyboard_repo.get_scene(scene_id)
        if not scene:
            raise NotFoundError("Scene not found")
        
        storyboard = await self.storyboard_repo.get(scene.storyboard_id)
        if storyboard:
            storyboard.total_scenes -= 1
            await self.storyboard_repo.update(storyboard)
        
        await self.storyboard_repo.delete_scene(scene)
    
    async def reorder_scenes(
        self,
        storyboard_id: UUID,
        scene_order: List[UUID]
    ) -> None:
        """Reorder scenes in a storyboard."""
        for order, scene_id in enumerate(scene_order):
            scene = await self.storyboard_repo.get_scene(scene_id)
            if scene and scene.storyboard_id == storyboard_id:
                scene.order = order
                await self.storyboard_repo.update_scene(scene)
    
    async def get_project(self, project_id: UUID) -> Optional[Project]:
        """Get project by ID."""
        return await self.project_repo.get(project_id)