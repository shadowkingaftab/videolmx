"""Video rendering worker."""

from datetime import datetime

from app.workers.worker_app import celery_app
from app.core.event_bus import event_bus
from app.database.engine import get_db_session
from app.repositories.video_repository import VideoRepository
from app.rendering.renderer import Renderer
from app.constants import VideoStatus


@celery_app.task(name="render_worker.render_video", bind=True)
def render_video(self, video_id: str, resolution: str = "1920x1080", fps: int = 30, quality: str = "medium", include_captions: bool = True, include_background_music: bool = True):
    """Render video."""
    try:
        self.update_state(state="RUNNING", meta={"progress": 0})
        
        async def _run():
            async with get_db_session() as db:
                video_repo = VideoRepository(db)
                
                video = await video_repo.get(video_id)
                if not video:
                    raise ValueError(f"Video not found: {video_id}")
                
                # Update status
                video.status = VideoStatus.RENDERING
                video.render_started_at = datetime.utcnow()
                await video_repo.update(video)
                
                # Get components
                storyboard = await video_repo.get_storyboard(video.storyboard_id)
                script = await video_repo.get_script(video.script_id)
                narration = await video_repo.get_narration(video.narration_id)
                
                # Render video
                renderer = Renderer()
                result = await renderer.render(
                    storyboard=storyboard,
                    script=script,
                    narration=narration,
                    resolution=resolution,
                    fps=fps,
                    quality=quality,
                    include_captions=include_captions,
                    include_background_music=include_background_music,
                )
                
                # Update video
                video.status = VideoStatus.READY
                video.progress = 100.0
                video.duration = result.get("duration")
                video.file_size = result.get("size")
                video.file_url = result.get("url")
                video.storage_key = result.get("storage_key")
                video.preview_url = result.get("preview_url")
                video.thumbnail_url = result.get("thumbnail_url")
                video.render_completed_at = datetime.utcnow()
                await video_repo.update(video)
                
                # Publish event
                await event_bus.publish(
                    "video_rendered",
                    {
                        "video_id": video_id,
                        "url": result.get("url"),
                        "user_id": str(video.project.user_id),
                    },
                )
                
                return result
        
        import asyncio
        result = asyncio.run(_run())
        return {"status": "completed", "result": result}
        
    except Exception as e:
        async def _handle():
            async with get_db_session() as db:
                video_repo = VideoRepository(db)
                video = await video_repo.get(video_id)
                if video:
                    video.status = VideoStatus.FAILED
                    video.error_message = str(e)
                    await video_repo.update(video)
            
            await event_bus.publish(
                "video_render_failed",
                {"video_id": video_id, "error": str(e)},
            )
        
        import asyncio
        asyncio.run(_handle())
        raise