"""Workflow definition and execution."""

from typing import Dict, Any, List, Optional, Callable, Awaitable
from dataclasses import dataclass, field
import asyncio

from app.core.event_bus import event_bus


@dataclass
class WorkflowContext:
    """Workflow execution context."""
    data: Dict[str, Any] = field(default_factory=dict)
    variables: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from data."""
        return self.data.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set value in data."""
        self.data[key] = value
    
    def get_var(self, key: str, default: Any = None) -> Any:
        """Get variable."""
        return self.variables.get(key, default)
    
    def set_var(self, key: str, value: Any) -> None:
        """Set variable."""
        self.variables[key] = value


@dataclass
class WorkflowStep:
    """A step in a workflow."""
    id: str
    name: str
    action: Callable[[WorkflowContext], Awaitable[Any]]
    retry_count: int = 0
    retry_delay: int = 1
    timeout: Optional[int] = None


class Workflow:
    """Workflow definition."""
    
    def __init__(
        self,
        id: str,
        name: str,
        description: Optional[str] = None
    ):
        self.id = id
        self.name = name
        self.description = description
        self.steps: List[WorkflowStep] = []
        self.error_handlers: Dict[Exception, Callable] = {}
        self.on_complete: Optional[Callable] = None
        self.on_error: Optional[Callable] = None
    
    def add_step(
        self,
        step: WorkflowStep
    ) -> "Workflow":
        """Add a step to the workflow."""
        self.steps.append(step)
        return self
    
    def on_step_error(
        self,
        exception_type: type,
        handler: Callable
    ) -> "Workflow":
        """Register error handler for a step."""
        self.error_handlers[exception_type] = handler
        return self
    
    def on_complete(self, handler: Callable) -> "Workflow":
        """Register completion handler."""
        self.on_complete = handler
        return self
    
    def on_error(self, handler: Callable) -> "Workflow":
        """Register error handler."""
        self.on_error = handler
        return self
    
    async def execute(self, context: WorkflowContext) -> Dict[str, Any]:
        """Execute the workflow."""
        results = {}
        
        for step in self.steps:
            try:
                # Execute step with retry logic
                for attempt in range(step.retry_count + 1):
                    try:
                        if step.timeout:
                            result = await asyncio.wait_for(
                                step.action(context),
                                timeout=step.timeout
                            )
                        else:
                            result = await step.action(context)
                        
                        results[step.id] = result
                        break
                    except Exception as e:
                        if attempt == step.retry_count:
                            raise
                        await asyncio.sleep(step.retry_delay * (attempt + 1))
                
                # Publish step completion event
                await event_bus.publish(
                    "workflow_step_completed",
                    {
                        "workflow_id": self.id,
                        "step_id": step.id,
                        "result": results.get(step.id),
                    }
                )
                
            except Exception as e:
                # Handle error
                handler = self.error_handlers.get(type(e))
                if handler:
                    error_result = await handler(e, context)
                    results[step.id] = error_result
                else:
                    # Publish error event
                    await event_bus.publish(
                        "workflow_step_error",
                        {
                            "workflow_id": self.id,
                            "step_id": step.id,
                            "error": str(e),
                        }
                    )
                    
                    if self.on_error:
                        await self.on_error(e, context)
                    
                    raise
        
        # Complete workflow
        if self.on_complete:
            await self.on_complete(context)
        
        # Publish completion event
        await event_bus.publish(
            "workflow_completed",
            {
                "workflow_id": self.id,
                "results": results,
            }
        )
        
        return results