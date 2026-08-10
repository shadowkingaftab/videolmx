"""Script service."""

from typing import Optional, List, Tuple, Dict, Any
from uuid import UUID

from app.models.script import Script
from app.repositories.script_repository import ScriptRepository
from app.repositories.storyboard_repository import StoryboardRepository
from app.repositories.project_repository import ProjectRepository
from app.core.errors import NotFoundError
from app.core.task_queue import get_queue


class ScriptService:
    """Script service."""
    
    def __init__(
        self,
        script_repo: ScriptRepository,
        storyboard_repo: StoryboardRepository,
        project_repo: ProjectRepository
    ):
        self.script_repo = script_repo
        self.storyboard_repo = storyboard_repo
        self.project_repo = project_repo
    
    async def create_script(
        self,
        storyboard_id: UUID,
        user_id: UUID,
        name: str,
        language: str = "en"
    ) -> Script:
        """Create a new script."""
        storyboard = await self.storyboard_repo.get(storyboard_id)
        if not storyboard:
            raise NotFoundError("Storyboard not found")
        
        script = Script(
            storyboard_id=storyboard_id,
            name=name,
            language=language,
        )
        
        return await self.script_repo.create(script)
    
    async def get_script(self, script_id: UUID) -> Optional[Script]:
        """Get script by ID."""
        return await self.script_repo.get(script_id)
    
    async def list_scripts(
        self,
        user_id: UUID,
        storyboard_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[Script], int]:
        """List scripts."""
        return await self.script_repo.list_by_user(
            user_id=user_id,
            storyboard_id=storyboard_id,
            skip=skip,
            limit=limit
        )
    
    async def update_script(
        self,
        script_id: UUID,
        updates: Dict[str, Any]
    ) -> Script:
        """Update script."""
        script = await self.script_repo.get(script_id)
        if not script:
            raise NotFoundError("Script not found")
        
        for key, value in updates.items():
            if hasattr(script, key):
                setattr(script, key, value)
        
        return await self.script_repo.update(script)
    
    async def delete_script(self, script_id: UUID) -> None:
        """Delete script."""
        script = await self.script_repo.get(script_id)
        if not script:
            raise NotFoundError("Script not found")
        
        await self.script_repo.delete(script)
    
    async def generate_script(
        self,
        script_id: UUID,
        tone: str = "professional",
        length: str = "medium",
        include_captions: bool = True
    ) -> UUID:
        """Generate script content."""
        script = await self.script_repo.get(script_id)
        if not script:
            raise NotFoundError("Script not found")
        
        # Queue generation job
        queue = await get_queue()
        await queue.enqueue(
            'script_worker.generate_script',
            args=[str(script_id), tone, length, include_captions],
            queue='script',
        )
        
        return script_id
    
    async def get_script_content(self, script_id: UUID) -> Dict[str, Any]:
        """Get full script content."""
        script = await self.script_repo.get(script_id)
        if not script:
            raise NotFoundError("Script not found")
        
        return {
            "content": script.content,
            "scenes": script.scenes,
            "narration": script.narration,
            "captions": script.captions,
        }
    
    async def regenerate_script(self, script_id: UUID) -> UUID:
        """Regenerate script with new parameters."""
        script = await self.script_repo.get(script_id)
        if not script:
            raise NotFoundError("Script not found")
        
        # Queue regeneration job
        queue = await get_queue()
        await queue.enqueue(
            'script_worker.regenerate_script',
            args=[str(script_id)],
            queue='script',
        )
        
        return script_id
    
    async def get_script_preview(self, script_id: UUID) -> Dict[str, Any]:
        """Get script preview."""
        script = await self.script_repo.get(script_id)
        if not script:
            raise NotFoundError("Script not found")
        
        return {
            "id": script.id,
            "name": script.name,
            "preview": script.content.get("preview") if script.content else None,
            "scene_count": len(script.scenes) if script.scenes else 0,
        }
    
    async def get_storyboard(self, storyboard_id: UUID) -> Optional[Storyboard]:
        """Get storyboard by ID."""
        return await self.storyboard_repo.get(storyboard_id)
    
    async def get_project(self, project_id: UUID) -> Optional[Project]:
        """Get project by ID."""
        return await self.project_repo.get(project_id)