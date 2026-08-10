"""Script generation worker."""

from datetime import datetime

from app.workers.worker_app import celery_app
from app.core.event_bus import event_bus
from app.database.engine import get_db_session
from app.repositories.script_repository import ScriptRepository
from app.repositories.storyboard_repository import StoryboardRepository
from app.script_generation.script_generator import ScriptGenerator


@celery_app.task(name="script_worker.generate_script", bind=True)
def generate_script(self, script_id: str, tone: str = "professional", length: str = "medium", include_captions: bool = True):
    """Generate script content."""
    try:
        self.update_state(state="RUNNING", meta={"progress": 0})
        
        async def _run():
            async with get_db_session() as db:
                script_repo = ScriptRepository(db)
                storyboard_repo = StoryboardRepository(db)
                
                script = await script_repo.get(script_id)
                if not script:
                    raise ValueError(f"Script not found: {script_id}")
                
                # Get storyboard
                storyboard = await storyboard_repo.get(script.storyboard_id)
                
                # Generate script
                generator = ScriptGenerator()
                result = await generator.generate(
                    storyboard=storyboard,
                    tone=tone,
                    length=length,
                    include_captions=include_captions,
                )
                
                # Update script
                script.content = result.get("content")
                script.scenes = result.get("scenes")
                script.narration = result.get("narration")
                script.captions = result.get("captions")
                script.is_generated = True
                script.quality_score = result.get("quality_score")
                script.readability_score = result.get("readability_score")
                await script_repo.update(script)
                
                # Publish event
                await event_bus.publish(
                    "script_generated",
                    {"script_id": script_id, "result": result},
                )
                
                return result
        
        import asyncio
        result = asyncio.run(_run())
        return {"status": "completed", "result": result}
        
    except Exception as e:
        async def _handle():
            async with get_db_session() as db:
                script_repo = ScriptRepository(db)
                script = await script_repo.get(script_id)
                if script:
                    script.is_generated = False
                    await script_repo.update(script)
            
            await event_bus.publish(
                "script_generation_failed",
                {"script_id": script_id, "error": str(e)},
            )
        
        import asyncio
        asyncio.run(_handle())
        raise


@celery_app.task(name="script_worker.generate_storyboard", bind=True)
def generate_storyboard(self, storyboard_id: str):
    """Generate storyboard from website analysis."""
    try:
        self.update_state(state="RUNNING", meta={"progress": 0})
        
        async def _run():
            async with get_db_session() as db:
                storyboard_repo = StoryboardRepository(db)
                storyboard = await storyboard_repo.get(storyboard_id)
                if not storyboard:
                    raise ValueError(f"Storyboard not found: {storyboard_id}")
                
                # Get project and website
                project = await storyboard_repo.get_project(storyboard.project_id)
                website = await storyboard_repo.get_website(project.websites[0].id if project.websites else None)
                
                # Generate storyboard
                generator = ScriptGenerator()
                result = await generator.generate_storyboard(
                    website=website,
                    template=storyboard.template,
                )
                
                # Create scenes
                for scene_data in result.get("scenes", []):
                    scene = Scene(
                        storyboard_id=storyboard_id,
                        order=scene_data.get("order"),
                        title=scene_data.get("title"),
                        description=scene_data.get("description"),
                        scene_type=scene_data.get("type"),
                        duration=scene_data.get("duration", 5.0),
                        narration_text=scene_data.get("narration"),
                    )
                    await storyboard_repo.create_scene(scene)
                
                storyboard.total_scenes = len(result.get("scenes", []))
                storyboard.estimated_duration = result.get("estimated_duration")
                await storyboard_repo.update(storyboard)
                
                return result
        
        import asyncio
        result = asyncio.run(_run())
        return {"status": "completed", "result": result}
        
    except Exception as e:
        raise