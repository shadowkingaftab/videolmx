"""Event bus for pub/sub messaging."""

from typing import Dict, Any, List, Callable, Awaitable, Optional
import asyncio
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime

from app.logging import logger


@dataclass
class Event:
    """Event data structure."""
    type: str
    data: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    source: Optional[str] = None
    correlation_id: Optional[str] = None


class EventBus:
    """Event bus for pub/sub messaging."""
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[Event], Awaitable[None]]]] = defaultdict(list)
        self._event_history: List[Event] = []
        self._max_history: int = 1000
        self._lock = asyncio.Lock()
    
    def subscribe(
        self,
        event_type: str,
        callback: Callable[[Event], Awaitable[None]]
    ) -> None:
        """Subscribe to an event type."""
        self._subscribers[event_type].append(callback)
        logger.debug(f"Subscribed to event: {event_type}")
    
    def unsubscribe(
        self,
        event_type: str,
        callback: Callable[[Event], Awaitable[None]]
    ) -> None:
        """Unsubscribe from an event type."""
        if event_type in self._subscribers:
            self._subscribers[event_type] = [
                cb for cb in self._subscribers[event_type]
                if cb != callback
            ]
            logger.debug(f"Unsubscribed from event: {event_type}")
    
    async def publish(
        self,
        event_type: str,
        data: Dict[str, Any],
        source: Optional[str] = None,
        correlation_id: Optional[str] = None
    ) -> None:
        """Publish an event."""
        event = Event(
            type=event_type,
            data=data,
            source=source,
            correlation_id=correlation_id,
        )
        
        # Store in history
        async with self._lock:
            self._event_history.append(event)
            if len(self._event_history) > self._max_history:
                self._event_history = self._event_history[-self._max_history:]
        
        # Notify subscribers
        if event_type in self._subscribers:
            tasks = []
            for callback in self._subscribers[event_type]:
                tasks.append(callback(event))
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
        
        # Also notify wildcard subscribers
        if "*" in self._subscribers:
            tasks = []
            for callback in self._subscribers["*"]:
                tasks.append(callback(event))
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
    
    async def publish_sync(
        self,
        event_type: str,
        data: Dict[str, Any],
        source: Optional[str] = None,
        correlation_id: Optional[str] = None
    ) -> List[Any]:
        """Publish an event and wait for results."""
        event = Event(
            type=event_type,
            data=data,
            source=source,
            correlation_id=correlation_id,
        )
        
        results = []
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                try:
                    result = await callback(event)
                    results.append(result)
                except Exception as e:
                    logger.error(f"Error in event subscriber: {e}")
        
        return results
    
    def get_history(
        self,
        event_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Event]:
        """Get event history."""
        if event_type:
            events = [e for e in self._event_history if e.type == event_type]
        else:
            events = self._event_history
        
        return events[-limit:]
    
    def clear_history(self) -> None:
        """Clear event history."""
        self._event_history = []
    
    async def on(self, event_type: str) -> Callable:
        """Decorator to subscribe to an event."""
        def decorator(callback: Callable) -> Callable:
            self.subscribe(event_type, callback)
            return callback
        return decorator


# Global event bus
event_bus = EventBus()