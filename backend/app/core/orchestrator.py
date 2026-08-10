"""Workflow orchestrator."""

from typing import Dict, Any, Optional, Callable
import asyncio
from datetime import datetime

from app.core.workflow import Workflow, WorkflowContext
from app.core.pipeline import Pipeline
from app.core.state_machine import StateMachine
from app.core.event_bus import event_bus
from app.core.task_queue import get_queue
from app.core.cache import get_cache
from app.logging import logger


class Orchestrator:
    """Orchestrates workflows and pipelines."""
    
    def __init__(self):
        self._workflows: Dict[str, Workflow] = {}
        self._pipelines: Dict[str, Pipeline] = {}
        self._state_machines: Dict[str, StateMachine] = {}
        self._running_jobs: Dict[str, Dict[str, Any]] = {}
    
    def register_workflow(self, workflow: Workflow) -> None:
        """Register a workflow."""
        self._workflows[workflow.id] = workflow
        logger.info(f"Registered workflow: {workflow.id}")
    
    def register_pipeline(self, pipeline: Pipeline) -> None:
        """Register a pipeline."""
        self._pipelines[pipeline.id] = pipeline
        logger.info(f"Registered pipeline: {pipeline.id}")
    
    async def execute_workflow(
        self,
        workflow_id: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a workflow."""
        workflow = self._workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow not found: {workflow_id}")
        
        workflow_context = WorkflowContext(context)
        result = await workflow.execute(workflow_context)
        
        # Publish event
        await event_bus.publish(
            "workflow_completed",
            {
                "workflow_id": workflow_id,
                "result": result,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )
        
        return result
    
    async def execute_pipeline(
        self,
        pipeline_id: str,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a pipeline."""
        pipeline = self._pipelines.get(pipeline_id)
        if not pipeline:
            raise ValueError(f"Pipeline not found: {pipeline_id}")
        
        result = await pipeline.execute(input_data)
        
        # Publish event
        await event_bus.publish(
            "pipeline_completed",
            {
                "pipeline_id": pipeline_id,
                "result": result,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )
        
        return result
    
    async def start_job(
        self,
        job_type: str,
        job_data: Dict[str, Any]
    ) -> str:
        """Start a new job."""
        job_id = f"{job_type}_{datetime.utcnow().timestamp()}"
        
        self._running_jobs[job_id] = {
            "type": job_type,
            "data": job_data,
            "status": "running",
            "started_at": datetime.utcnow().isoformat(),
        }
        
        # Queue the job
        queue = await get_queue()
        await queue.enqueue(
            f"{job_type}_worker.process",
            args=[job_id, job_data],
            queue=job_type,
        )
        
        return job_id
    
    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job status."""
        cache = await get_cache()
        status = await cache.get(f"job_status:{job_id}")
        if status:
            return status
        return self._running_jobs.get(job_id)
    
    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a job."""
        if job_id in self._running_jobs:
            self._running_jobs[job_id]["status"] = "cancelled"
            await self._running_jobs[job_id].get("cancel_callback", lambda: None)()
            return True
        return False


# Global orchestrator
orchestrator = Orchestrator()