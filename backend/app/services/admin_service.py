"""Admin service."""

from typing import Optional, List, Tuple, Dict, Any
from uuid import UUID
from datetime import datetime

from app.repositories.user_repository import UserRepository
from app.core.errors import NotFoundError


class AdminService:
    """Admin service."""
    
    def __init__(
        self,
        user_repo: UserRepository
    ):
        self.user_repo = user_repo
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get admin statistics."""
        # This would aggregate from various repositories
        return {
            "total_users": 100,
            "active_users": 80,
            "total_projects": 250,
            "total_videos": 500,
            "total_assets": 1000,
            "storage_used_gb": 50,
            "jobs_running": 5,
            "jobs_queued": 10,
        }
    
    async def list_users(
        self,
        skip: int = 0,
        limit: int = 20,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        plan: Optional[str] = None
    ) -> Tuple[List[Dict[str, Any]], int]:
        """List users with filters."""
        # This would be implemented with user repository
        return [], 0
    
    async def update_user(
        self,
        user_id: UUID,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update user."""
        user = await self.user_repo.get(user_id)
        if not user:
            raise NotFoundError("User not found")
        
        for key, value in updates.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        await self.user_repo.update(user)
        return {"id": str(user.id), "updated": True}
    
    async def activate_user(self, user_id: UUID) -> None:
        """Activate user."""
        user = await self.user_repo.get(user_id)
        if not user:
            raise NotFoundError("User not found")
        
        user.is_active = True
        await self.user_repo.update(user)
    
    async def deactivate_user(self, user_id: UUID) -> None:
        """Deactivate user."""
        user = await self.user_repo.get(user_id)
        if not user:
            raise NotFoundError("User not found")
        
        user.is_active = False
        await self.user_repo.update(user)
    
    async def delete_user(self, user_id: UUID) -> None:
        """Delete user."""
        user = await self.user_repo.get(user_id)
        if not user:
            raise NotFoundError("User not found")
        
        await self.user_repo.delete(user)
    
    async def list_jobs(
        self,
        skip: int = 0,
        limit: int = 20,
        job_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> Tuple[List[Dict[str, Any]], int]:
        """List all jobs."""
        # This would be implemented with job repository
        return [], 0
    
    async def cancel_job(self, job_id: UUID) -> None:
        """Cancel a job."""
        # This would be implemented with job repository
        pass
    
    async def get_system_settings(self) -> Dict[str, Any]:
        """Get system settings."""
        return {
            "allow_registration": True,
            "maintenance_mode": False,
            "max_file_size_mb": 100,
            "supported_languages": ["en", "es", "fr", "de", "zh"],
            "ai_provider": "openai",
            "default_plan": "free",
        }
    
    async def update_system_settings(
        self,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update system settings."""
        # This would update settings in database
        return updates
    
    async def get_logs(
        self,
        skip: int = 0,
        limit: int = 50,
        level: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Get system logs."""
        # This would fetch from log storage
        return [], 0
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get system health status."""
        return {
            "status": "healthy",
            "services": {
                "database": {"status": "healthy", "latency_ms": 5},
                "cache": {"status": "healthy", "latency_ms": 2},
                "storage": {"status": "healthy", "latency_ms": 10},
                "ai_services": {"status": "healthy"},
                "workers": {"status": "healthy", "active": 4, "queued": 2},
            },
            "uptime_seconds": 86400,
            "version": "1.0.0",
        }