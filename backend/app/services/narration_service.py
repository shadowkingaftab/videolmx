"""Narration service."""

from typing import Optional, List, Tuple, Dict, Any
from uuid import UUID

from app.models.narration import Narration
from app.repositories.narration_repository import NarrationRepository
from app.repositories.script_repository import ScriptRepository
from app.repositories.storyboard_repository import StoryboardRepository
from app.repositories.project_repository import ProjectRepository
from app.core.errors import NotFoundError
from app.core.task_queue import get_queue


class NarrationService:
    """Narration service."""
    
    def __init__(
        self,
        narration_repo: NarrationRepository,
        script_repo: ScriptRepository,
        storyboard_repo: StoryboardRepository,
        project_repo: ProjectRepository
    ):
        self.narration_repo = narration_repo
        self.script_repo = script_repo
        self.storyboard_repo = storyboard_repo
        self.project_repo = project_repo
    
    async def create_narration(
        self,
        script_id: UUID,
        user_id: UUID,
        name: str,
        voice_id: str = "default",
        language: str = "en"
    ) -> Narration:
        """Create a new narration."""
        script = await self.script_repo.get(script_id)
        if not script:
            raise NotFoundError("Script not found")
        
        narration = Narration(
            script_id=script_id,
            name=name,
            voice_id=voice_id,
            language=language,
        )
        
        return await self.narration_repo.create(narration)
    
    async def get_narration(self, narration_id: UUID) -> Optional[Narration]:
        """Get narration by ID."""
        return await self.narration_repo.get(narration_id)
    
    async def list_narrations(
        self,
        user_id: UUID,
        script_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[Narration], int]:
        """List narrations."""
        return await self.narration_repo.list_by_user(
            user_id=user_id,
            script_id=script_id,
            skip=skip,
            limit=limit
        )
    
    async def update_narration(
        self,
        narration_id: UUID,
        updates: Dict[str, Any]
    ) -> Narration:
        """Update narration."""
        narration = await self.narration_repo.get(narration_id)
        if not narration:
            raise NotFoundError("Narration not found")
        
        for key, value in updates.items():
            if hasattr(narration, key):
                setattr(narration, key, value)
        
        return await self.narration_repo.update(narration)
    
    async def delete_narration(self, narration_id: UUID) -> None:
        """Delete narration."""
        narration = await self.narration_repo.get(narration_id)
        if not narration:
            raise NotFoundError("Narration not found")
        
        await self.narration_repo.delete(narration)
    
    async def generate_narration(
        self,
        narration_id: UUID,
        voice_id: Optional[str] = None,
        speed: float = 1.0,
        pitch: float = 1.0,
        emotion: str = "neutral"
    ) -> UUID:
        """Generate narration audio."""
        narration = await self.narration_repo.get(narration_id)
        if not narration:
            raise NotFoundError("Narration not found")
        
        # Queue generation job
        queue = await get_queue()
        await queue.enqueue(
            'narration_worker.generate_narration',
            args=[str(narration_id), voice_id, speed, pitch, emotion],
            queue='voice',
        )
        
        return narration_id
    
    async def get_audio_url(self, narration_id: UUID) -> Optional[str]:
        """Get narration audio URL."""
        narration = await self.narration_repo.get(narration_id)
        if not narration:
            raise NotFoundError("Narration not found")
        
        return narration.audio_url
    
    async def preview_voice(
        self,
        voice_id: str,
        text: str,
        speed: float = 1.0,
        pitch: float = 1.0
    ) -> Dict[str, Any]:
        """Preview a voice with sample text."""
        # This would call the TTS service
        return {
            "voice_id": voice_id,
            "preview_url": "https://example.com/preview.mp3",
            "duration": 2.5,
        }
    
    async def list_voices(self) -> List[Dict[str, Any]]:
        """List available voices."""
        return [
            {
                "id": "voice_1",
                "name": "Professional Male",
                "gender": "male",
                "language": "en",
                "accent": "american",
            },
            {
                "id": "voice_2",
                "name": "Professional Female",
                "gender": "female",
                "language": "en",
                "accent": "american",
            },
        ]
    
    async def get_voice(self, voice_id: str) -> Optional[Dict[str, Any]]:
        """Get voice details."""
        voices = await self.list_voices()
        for voice in voices:
            if voice["id"] == voice_id:
                return voice
        return None
    
    async def get_script(self, script_id: UUID) -> Optional[Script]:
        """Get script by ID."""
        return await self.script_repo.get(script_id)
    
    async def get_storyboard(self, storyboard_id: UUID) -> Optional[Storyboard]:
        """Get storyboard by ID."""
        return await self.storyboard_repo.get(storyboard_id)
    
    async def get_project(self, project_id: UUID) -> Optional[Project]:
        """Get project by ID."""
        return await self.project_repo.get(project_id)