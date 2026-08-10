"""Export service."""

from typing import Optional, List, Tuple, Dict, Any
from uuid import UUID

from app.models.export import Export
from app.repositories.export_repository import ExportRepository
from app.repositories.video_repository import VideoRepository
from app.repositories.project_repository import ProjectRepository
from app.core.errors import NotFoundError
from app.core.task_queue import get_queue
from app.constants import ExportStatus


class ExportService:
    """Export service."""
    
    def __init__(
        self,
        export_repo: ExportRepository,
        video_repo: VideoRepository,
        project_repo: ProjectRepository
    ):
        self.export_repo = export_repo
        self.video_repo = video_repo
        self.project_repo = project_repo
    
    async def create_export(
        self,
        video_id: UUID,
        user_id: UUID,
        format: str,
        quality: str = "medium",
        include_watermark: bool = True
    ) -> Export:
        """Create a new export."""
        video = await self.video_repo.get(video_id)
        if not video:
            raise NotFoundError("Video not found")
        
        export = Export(
            video_id=video_id,
            format=format,
            quality=quality,
            include_watermark=include_watermark,
            status=ExportStatus.PENDING,
        )
        
        export = await self.export_repo.create(export)
        
        # Queue export job
        queue = await get_queue()
        await queue.enqueue(
            'export_worker.process_export',
            args=[str(export.id)],
            queue='export',
        )
        
        return export
    
    async def get_export(self, export_id: UUID) -> Optional[Export]:
        """Get export by ID."""
        return await self.export_repo.get(export_id)
    
    async def list_exports(
        self,
        user_id: UUID,
        video_id: Optional[UUID] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[Export], int]:
        """List exports."""
        return await self.export_repo.list_by_user(
            user_id=user_id,
            video_id=video_id,
            status=status,
            skip=skip,
            limit=limit
        )
    
    async def update_export(
        self,
        export_id: UUID,
        updates: Dict[str, Any]
    ) -> Export:
        """Update export."""
        export = await self.export_repo.get(export_id)
        if not export:
            raise NotFoundError("Export not found")
        
        for key, value in updates.items():
            if hasattr(export, key):
                setattr(export, key, value)
        
        return await self.export_repo.update(export)
    
    async def delete_export(self, export_id: UUID) -> None:
        """Delete export."""
        export = await self.export_repo.get(export_id)
        if not export:
            raise NotFoundError("Export not found")
        
        await self.export_repo.delete(export)
    
    async def get_download_url(self, export_id: UUID) -> Optional[str]:
        """Get export download URL."""
        export = await self.export_repo.get(export_id)
        if not export:
            raise NotFoundError("Export not found")
        
        return export.file_url
    
    async def get_export_status(self, export_id: UUID) -> Dict[str, Any]:
        """Get export status."""
        export = await self.export_repo.get(export_id)
        if not export:
            raise NotFoundError("Export not found")
        
        return {
            "status": export.status,
            "progress": export.progress,
            "started_at": export.started_at,
            "completed_at": export.completed_at,
        }
    
    async def retry_export(self, export_id: UUID) -> UUID:
        """Retry a failed export."""
        export = await self.export_repo.get(export_id)
        if not export:
            raise NotFoundError("Export not found")
        
        export.status = ExportStatus.PENDING
        export.progress = 0
        export.error_message = None
        await self.export_repo.update(export)
        
        # Queue retry job
        queue = await get_queue()
        await queue.enqueue(
            'export_worker.process_export',
            args=[str(export_id)],
            queue='export',
        )
        
        return export_id
    
    async def get_export_formats(self) -> List[Dict[str, Any]]:
        """Get available export formats."""
        return [
            {"format": "mp4", "label": "MP4 Video", "quality": ["low", "medium", "high"]},
            {"format": "webm", "label": "WebM Video", "quality": ["low", "medium", "high"]},
            {"format": "gif", "label": "GIF Animation", "quality": ["low", "medium"]},
            {"format": "avi", "label": "AVI Video", "quality": ["medium", "high"]},
            {"format": "mov", "label": "MOV Video", "quality": ["medium", "high"]},
        ]
    
    async def get_video(self, video_id: UUID) -> Optional[Video]:
        """Get video by ID."""
        return await self.video_repo.get(video_id)
    
    async def get_project(self, project_id: UUID) -> Optional[Project]:
        """Get project by ID."""
        return await self.project_repo.get(project_id)