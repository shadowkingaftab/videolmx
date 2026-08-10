"""Pipeline definition and execution."""

from typing import Dict, Any, List, Optional, Callable, Awaitable
from dataclasses import dataclass, field
import asyncio

from app.core.event_bus import event_bus


@dataclass
class PipelineStage:
    """A stage in a pipeline."""
    id: str
    name: str
    processor: Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]
    parallel: bool = False
    continue_on_error: bool = False


class Pipeline:
    """Pipeline definition."""
    
    def __init__(
        self,
        id: str,
        name: str,
        description: Optional[str] = None
    ):
        self.id = id
        self.name = name
        self.description = description
        self.stages: List[PipelineStage] = []
        self.pre_processors: List[Callable] = []
        self.post_processors: List[Callable] = []
        self.error_handlers: Dict[Exception, Callable] = {}
    
    def add_stage(self, stage: PipelineStage) -> "Pipeline":
        """Add a stage to the pipeline."""
        self.stages.append(stage)
        return self
    
    def pre_process(self, processor: Callable) -> "Pipeline":
        """Add pre-processor."""
        self.pre_processors.append(processor)
        return self
    
    def post_process(self, processor: Callable) -> "Pipeline":
        """Add post-processor."""
        self.post_processors.append(processor)
        return self
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the pipeline."""
        data = input_data.copy()
        
        # Pre-processing
        for processor in self.pre_processors:
            data = await processor(data)
        
        # Execute stages
        for stage in self.stages:
            try:
                if stage.parallel:
                    # Execute parallel stages
                    tasks = []
                    for sub_stage in stage.processor:
                        tasks.append(sub_stage(data))
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    data[stage.id] = results
                else:
                    # Execute single stage
                    data[stage.id] = await stage.processor(data)
                
                # Publish stage completion event
                await event_bus.publish(
                    "pipeline_stage_completed",
                    {
                        "pipeline_id": self.id,
                        "stage_id": stage.id,
                        "data": data[stage.id],
                    }
                )
                
            except Exception as e:
                # Handle error
                if stage.continue_on_error:
                    data[f"{stage.id}_error"] = str(e)
                    continue
                
                handler = self.error_handlers.get(type(e))
                if handler:
                    data[stage.id] = await handler(e, data)
                else:
                    # Publish error event
                    await event_bus.publish(
                        "pipeline_stage_error",
                        {
                            "pipeline_id": self.id,
                            "stage_id": stage.id,
                            "error": str(e),
                        }
                    )
                    raise
        
        # Post-processing
        for processor in self.post_processors:
            data = await processor(data)
        
        # Publish completion event
        await event_bus.publish(
            "pipeline_completed",
            {
                "pipeline_id": self.id,
                "data": data,
            }
        )
        
        return data