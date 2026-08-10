"""Application lifecycle management."""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator, Optional

from fastapi import FastAPI

from app.config import settings
from app.database.engine import init_db, close_db
from app.storage.object_store import init_storage, close_storage
from app.core.cache import init_cache, close_cache
from app.core.task_queue import init_queue, close_queue
from app.integrations.openai_client import init_openai, close_openai
from app.workers.worker_app import init_worker, close_worker

logger = logging.getLogger(__name__)


class LifespanManager:
    """Manages application lifecycle."""
    
    def __init__(self):
        self._startup_tasks: list = []
        self._shutdown_tasks: list = []
        self._initialized: bool = False
    
    async def startup(self, app: FastAPI) -> None:
        """Run startup tasks."""
        if self._initialized:
            return
        
        logger.info("Starting application lifecycle...")
        
        # Initialize components in order
        await self._init_database()
        await self._init_storage()
        await self._init_cache()
        await self._init_queue()
        await self._init_ai_services()
        await self._init_workers()
        
        self._initialized = True
        logger.info("Application startup complete")
    
    async def shutdown(self, app: FastAPI) -> None:
        """Run shutdown tasks."""
        if not self._initialized:
            return
        
        logger.info("Shutting down application...")
        
        # Close components in reverse order
        await self._close_workers()
        await self._close_ai_services()
        await self._close_queue()
        await self._close_cache()
        await self._close_storage()
        await self._close_database()
        
        self._initialized = False
        logger.info("Application shutdown complete")
    
    async def _init_database(self) -> None:
        """Initialize database connection pool."""
        try:
            await init_db()
            logger.info("Database initialized")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    async def _close_database(self) -> None:
        """Close database connection pool."""
        try:
            await close_db()
            logger.info("Database closed")
        except Exception as e:
            logger.error(f"Error closing database: {e}")
    
    async def _init_storage(self) -> None:
        """Initialize object storage."""
        try:
            await init_storage()
            logger.info("Storage initialized")
        except Exception as e:
            logger.error(f"Failed to initialize storage: {e}")
            raise
    
    async def _close_storage(self) -> None:
        """Close object storage."""
        try:
            await close_storage()
            logger.info("Storage closed")
        except Exception as e:
            logger.error(f"Error closing storage: {e}")
    
    async def _init_cache(self) -> None:
        """Initialize cache."""
        try:
            await init_cache()
            logger.info("Cache initialized")
        except Exception as e:
            logger.error(f"Failed to initialize cache: {e}")
            raise
    
    async def _close_cache(self) -> None:
        """Close cache connection."""
        try:
            await close_cache()
            logger.info("Cache closed")
        except Exception as e:
            logger.error(f"Error closing cache: {e}")
    
    async def _init_queue(self) -> None:
        """Initialize task queue."""
        try:
            await init_queue()
            logger.info("Task queue initialized")
        except Exception as e:
            logger.error(f"Failed to initialize task queue: {e}")
            raise
    
    async def _close_queue(self) -> None:
        """Close task queue."""
        try:
            await close_queue()
            logger.info("Task queue closed")
        except Exception as e:
            logger.error(f"Error closing task queue: {e}")
    
    async def _init_ai_services(self) -> None:
        """Initialize AI services."""
        try:
            await init_openai()
            logger.info("AI services initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize AI services: {e}")
    
    async def _close_ai_services(self) -> None:
        """Close AI services."""
        try:
            await close_openai()
            logger.info("AI services closed")
        except Exception as e:
            logger.error(f"Error closing AI services: {e}")
    
    async def _init_workers(self) -> None:
        """Initialize worker processes."""
        try:
            await init_worker()
            logger.info("Workers initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize workers: {e}")
    
    async def _close_workers(self) -> None:
        """Close worker processes."""
        try:
            await close_worker()
            logger.info("Workers closed")
        except Exception as e:
            logger.error(f"Error closing workers: {e}")


# Singleton instance
lifespan = LifespanManager()


@asynccontextmanager
async def lifespan_context(app: FastAPI) -> AsyncIterator[None]:
    """Context manager for application lifespan."""
    await lifespan.startup(app)
    yield
    await lifespan.shutdown(app)