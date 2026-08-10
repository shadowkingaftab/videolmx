"""Video service."""

from typing import Optional, List, Tuple, Dict, Any
from uuid import UUID

from app.models.video import Video
from app.repositories.video_repository import VideoRepository
from app.repositories.project_repository import ProjectRepository
from app.core.errors import NotFoundError
from app.core.task_queue import get_queue
from app.constants import VideoStatus


class VideoService:
    """Video service."""
    
    def __init__(
        self,
        video_repo: VideoRepository,
        project_repo: ProjectRepository
    ):
        self.video_repo = video_repo
        self.project_repo = project_repo
    
    async def create_video(
        self,
        project_id: UUID,
        user_id: UUID,
        name: str,
        description: Optional[str] = None,
        storyboard_id: Optional[UUID] = None,
        script_id: Optional[UUID] = None,
        narration_id: Optional[UUID] = None
    ) -> Video:
        """Create a new video."""
        project = await self.project_repo.get(project_id)
        if not project:
            raise NotFoundError("Project not found")
        
        video = Video(
            project_id=project_id,
            name=name,
            description=description,
            storyboard_id=storyboard_id,
            script_id=script_id,
            narration_id=narration_id,
            status=VideoStatus.DRAFT,
        )
        
        return await self.video_repo.create(video)
    
    async def get_video(self, video_id: UUID) -> Optional[Video]:
        """Get video by ID."""
        return await self.video_repo.get(video_id)
    
    async def list_videos(
        self,
        user_id: UUID,
        project_id: Optional[UUID] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[Video], int]:
        """List videos."""
        return await self.video_repo.list_by_user(
            user_id=user_id,
            project_id=project_id,
            status=status,
            skip=skip,
            limit=limit
        )
    
    async def update_video(
        self,
        video_id: UUID,
        updates: Dict[str, Any]
    ) -> Video:
        """Update video metadata."""
        video = await self.video_repo.get(video_id)
        if not video:
            raise NotFoundError("Video not found")
        
        for key, value in updates.items():
            if hasattr(video, key):
                setattr(video, key, value)
        
        return await self.video_repo.update(video)
    
    async def delete_video(self, video_id: UUID) -> None:
        """Delete video."""
        video = await self.video_repo.get(video_id)
        if not video:
            raise NotFoundError("Video not found")
        
        await self.video_repo.delete(video)
    
    async def render_video(
        self,
        video_id: UUID,
        resolution: str = "1920x1080",
        fps: int = 30,
        quality: str = "medium",
        include_captions: bool = True,
        include_background_music: bool = True
    ) -> UUID:
        """Render video."""
        video = await self.video_repo.get(video_id)
        if not video:
            raise NotFoundError("Video not found")
        
        # Update video status
        video.status = VideoStatus.RENDERING
        await self.video_repo.update(video)
        
        # Queue rendering job
        queue = await get_queue()
        await queue.enqueue(
            'render_worker.render_video',
            args=[str(video_id), resolution, fps, quality, include_captions, include_background_music],
            queue='render',
        )
        
        return video_id
    
    async def get_video_status(self, video_id: UUID) -> Dict[str, Any]:
        """Get video rendering status."""
        video = await self.video_repo.get(video_id)
        if not video:
            raise NotFoundError("Video not found")
        
        return {
            "status": video.status,
            "progress": video.progress,
            "duration": video.duration,
            "render_started_at": video.render_started_at,
            "render_completed_at": video.render_completed_at,
        }
    
    async def get_download_url(self, video_id: UUID) -> Optional[str]:
        """Get video download URL."""
        video = await self.video_repo.get(video_id)
        if not video:
            raise NotFoundError("Video not found")
        
        return video.file_url
    
    async def get_stream_url(self, video_id: UUID) -> Optional[str]:
        """Get video stream URL."""
        video = await self.video_repo.get(video_id)
        if not video:
            raise NotFoundError("Video not found")
        
        return video.preview_url
    
    async def export_video(
        self,
        video_id: UUID,
        format: str = "mp4",
        quality: str = "medium",
        include_watermark: bool = True
    ) -> UUID:
        """Export video to different format."""
        video = await self.video_repo.get(video_id)
        if not video:
            raise NotFoundError("Video not found")
        
        # Queue export job
        queue = await get_queue()
        await queue.enqueue(
            'export_worker.export_video',
            args=[str(video_id), format, quality, include_watermark],
            queue='export',
        )
        
        return video_id
    
    async def list_exports(self, video_id: UUID) -> List[Dict[str, Any]]:
        """List video exports."""
        # This would be implemented with export repository
        return []
    
    async def get_project(self, project_id: UUID) -> Optional[Project]:
        """Get project by ID."""
        return await self.project_repo.get(project_id)