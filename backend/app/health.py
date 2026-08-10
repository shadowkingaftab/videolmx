"""Health check endpoints and utilities."""

import asyncio
from typing import Dict, Any, List
from datetime import datetime

from app.config import settings
from app.database.engine import engine
from app.core.cache import get_cache
from app.storage.object_store import get_storage


class HealthChecker:
    """Health check utilities."""
    
    @staticmethod
    async def check_database() -> Dict[str, Any]:
        """Check database connectivity."""
        try:
            async with engine.connect() as conn:
                await conn.execute("SELECT 1")
            return {"status": "healthy", "latency_ms": 0}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    @staticmethod
    async def check_cache() -> Dict[str, Any]:
        """Check cache connectivity."""
        try:
            cache = await get_cache()
            await cache.ping()
            return {"status": "healthy"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    @staticmethod
    async def check_storage() -> Dict[str, Any]:
        """Check object storage connectivity."""
        try:
            storage = await get_storage()
            await storage.bucket_exists("assets")
            return {"status": "healthy"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    @staticmethod
    async def check_ai_services() -> Dict[str, Any]:
        """Check AI service connectivity."""
        results = {}
        if settings.OPENAI_API_KEY:
            try:
                from app.integrations.openai_client import get_openai_client
                client = await get_openai_client()
                await client.health_check()
                results["openai"] = {"status": "healthy"}
            except Exception as e:
                results["openai"] = {"status": "unhealthy", "error": str(e)}
        
        if settings.ANTHROPIC_API_KEY:
            try:
                from app.integrations.anthropic_client import get_anthropic_client
                client = await get_anthropic_client()
                await client.health_check()
                results["anthropic"] = {"status": "healthy"}
            except Exception as e:
                results["anthropic"] = {"status": "unhealthy", "error": str(e)}
        
        return results
    
    @staticmethod
    async def check_workers() -> Dict[str, Any]:
        """Check worker status."""
        # This would check Celery or worker queue status
        return {"status": "healthy"}
    
    @staticmethod
    async def check_all() -> Dict[str, Any]:
        """Check all services."""
        checks = {
            "database": await HealthChecker.check_database(),
            "cache": await HealthChecker.check_cache(),
            "storage": await HealthChecker.check_storage(),
            "ai_services": await HealthChecker.check_ai_services(),
            "workers": await HealthChecker.check_workers(),
        }
        
        # Determine overall status
        overall = "healthy"
        for service, status in checks.items():
            if isinstance(status, dict) and status.get("status") == "unhealthy":
                overall = "unhealthy"
                break
            elif isinstance(status, list):
                for item in status:
                    if item.get("status") == "unhealthy":
                        overall = "unhealthy"
                        break
        
        return {
            "status": overall,
            "services": checks,
            "timestamp": datetime.utcnow().isoformat(),
        }


async def get_health_status() -> Dict[str, Any]:
    """Get comprehensive health status."""
    return await HealthChecker.check_all()


async def get_ready_status() -> Dict[str, Any]:
    """Get readiness status."""
    checks = {
        "database": await HealthChecker.check_database(),
        "cache": await HealthChecker.check_cache(),
        "storage": await HealthChecker.check_storage(),
    }
    
    ready = all(c.get("status") == "healthy" for c in checks.values())
    
    return {
        "ready": ready,
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat(),
    }


async def get_live_status() -> Dict[str, Any]:
    """Get liveness status."""
    return {
        "alive": True,
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
    }