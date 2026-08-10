"""Narration generation worker."""

from datetime import datetime

from app.workers.worker_app import celery_app
from app.core.event_bus import event_bus
from app.database.engine import get_db_session
from app.repositories.narration_repository import NarrationRepository
from app.repositories.script_repository import ScriptRepository
from app.voice.tts import TTSEngine


@celery_app.task(name="narration_worker.generate_narration", bind=True)
def generate_narration(self, narration_id: str, voice_id: str = None, speed: float = 1.0, pitch: float = 1.0, emotion: str = "neutral"):
    """Generate narration audio."""
    try:
        self.update_state(state="RUNNING", meta={"progress": 0})
        
        async def _run():
            async with get_db_session() as db:
                narration_repo = NarrationRepository(db)
                script_repo = ScriptRepository(db)
                
                narration = await narration_repo.get(narration_id)
                if not narration:
                    raise ValueError(f"Narration not found: {narration_id}")
                
                # Get script content
                script = await script_repo.get(narration.script_id)
                if not script or not script.narration:
                    raise ValueError("Script or narration content not found")
                
                # Generate audio
                tts = TTSEngine()
                result = await tts.generate(
                    text=script.narration.get("text", ""),
                    voice_id=voice_id or narration.voice_id,
                    speed=speed,
                    pitch=pitch,
                    emotion=emotion,
                )
                
                # Update narration
                narration.audio_url = result.get("audio_url")
                narration.audio_storage_key = result.get("storage_key")
                narration.audio_duration = result.get("duration")
                narration.audio_size = result.get("size")
                narration.alignment_data = result.get("alignment")
                narration.is_generated = True
                await narration_repo.update(narration)
                
                # Publish event
                await event_bus.publish(
                    "narration_generated",
                    {"narration_id": narration_id, "result": result},
                )
                
                return result
        
        import asyncio
        result = asyncio.run(_run())
        return {"status": "completed", "result": result}
        
    except Exception as e:
        async def _handle():
            async with get_db_session() as db:
                narration_repo = NarrationRepository(db)
                narration = await narration_repo.get(narration_id)
                if narration:
                    narration.is_generated = False
                    await narration_repo.update(narration)
            
            await event_bus.publish(
                "narration_generation_failed",
                {"narration_id": narration_id, "error": str(e)},
            )
        
        import asyncio
        asyncio.run(_handle())
        raise