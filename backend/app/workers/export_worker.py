"""Export worker."""

from datetime import datetime

from app.workers.worker_app import celery_app
from app.core.event_bus import event_bus
from app.database.engine import get_db_session
from app.repositories.export_repository import ExportRepository
from app.repositories.video_repository import VideoRepository
from app.rendering.export import Exporter
from app.constants import ExportStatus


@celery_app.task(name="export_worker.process_export", bind=True)
def process_export(self, export_id: str):
    """Process export."""
    try:
        self.update_state(state="RUNNING", meta={"progress": 0})
        
        async def _run():
            async with get_db_session() as db:
                export_repo = ExportRepository(db)
                video_repo = VideoRepository(db)
                
                export = await export_repo.get(export_id)
                if not export:
                    raise ValueError(f"Export not found: {export_id}")
                
                # Update status
                export.status = ExportStatus.EXPORTING
                export.started_at = datetime.utcnow()
                await export_repo.update(export)
                
                # Get video
                video = await video_repo.get(export.video_id)
                
                # Export video
                exporter = Exporter()
                result = await exporter.export(
                    video=video,
                    format=export.format,
                    quality=export.quality,
                    include_watermark=export.include_watermark,
                )
                
                # Update export
                export.status = ExportStatus.COMPLETED
                export.progress = 100.0
                export.file_size = result.get("size")
                export.file_url = result.get("url")
                export.storage_key = result.get("storage_key")
                export.completed_at = datetime.utcnow()
                await export_repo.update(export)
                
                # Publish event
                await event_bus.publish(
                    "export_completed",
                    {"export_id": export_id, "url": result.get("url")},
                )
                
                return result
        
        import asyncio
        result = asyncio.run(_run())
        return {"status": "completed", "result": result}
        
    except Exception as e:
        async def _handle():
            async with get_db_session() as db:
                export_repo = ExportRepository(db)
                export = await export_repo.get(export_id)
                if export:
                    export.status = ExportStatus.FAILED
                    export.error_message = str(e)
                    await export_repo.update(export)
            
            await event_bus.publish(
                "export_failed",
                {"export_id": export_id, "error": str(e)},
            )
        
        import asyncio
        asyncio.run(_handle())
        raise