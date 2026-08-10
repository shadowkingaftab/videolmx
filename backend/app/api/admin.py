"""Admin API endpoints."""

from typing import Optional
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.dependencies import get_current_admin_user, get_admin_service
from app.models.user import User
from app.services.admin_service import AdminService
from app.schemas.admin import (
    AdminStats,
    AdminUserList,
    AdminUserUpdate,
    AdminSystemSettings,
    AdminLogEntry,
)

router = APIRouter()


@router.get("/stats", response_model=AdminStats)
async def get_admin_stats(
    admin_user: User = Depends(get_current_admin_user),
    admin_service: AdminService = Depends(get_admin_service),
):
    """Get admin dashboard statistics."""
    stats = await admin_service.get_stats()
    return stats


@router.get("/users", response_model=AdminUserList)
async def list_users_admin(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    plan: Optional[str] = None,
    admin_user: User = Depends(get_current_admin_user),
    admin_service: AdminService = Depends(get_admin_service),
):
    """List users (admin only)."""
    skip = (page - 1) * page_size
    users, total = await admin_service.list_users(
        skip=skip,
        limit=page_size,
        search=search,
        is_active=is_active,
        plan=plan,
    )
    
    return {
        "items": users,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size,
    }


@router.patch("/users/{user_id}", response_model=AdminUserUpdate)
async def update_user_admin(
    user_id: UUID,
    request: AdminUserUpdate,
    admin_user: User = Depends(get_current_admin_user),
    admin_service: AdminService = Depends(get_admin_service),
):
    """Update user (admin only)."""
    try:
        updated = await admin_service.update_user(
            user_id=user_id,
            updates=request.dict(exclude_unset=True),
        )
        return updated
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post("/users/{user_id}/activate")
async def activate_user_admin(
    user_id: UUID,
    admin_user: User = Depends(get_current_admin_user),
    admin_service: AdminService = Depends(get_admin_service),
):
    """Activate user (admin only)."""
    await admin_service.activate_user(user_id)
    return {"message": "User activated successfully"}


@router.post("/users/{user_id}/deactivate")
async def deactivate_user_admin(
    user_id: UUID,
    admin_user: User = Depends(get_current_admin_user),
    admin_service: AdminService = Depends(get_admin_service),
):
    """Deactivate user (admin only)."""
    await admin_service.deactivate_user(user_id)
    return {"message": "User deactivated successfully"}


@router.delete("/users/{user_id}")
async def delete_user_admin(
    user_id: UUID,
    admin_user: User = Depends(get_current_admin_user),
    admin_service: AdminService = Depends(get_admin_service),
):
    """Delete user (admin only)."""
    await admin_service.delete_user(user_id)
    return {"message": "User deleted successfully"}


@router.get("/jobs")
async def list_jobs_admin(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    job_type: Optional[str] = None,
    status: Optional[str] = None,
    admin_user: User = Depends(get_current_admin_user),
    admin_service: AdminService = Depends(get_admin_service),
):
    """List all jobs (admin only)."""
    skip = (page - 1) * page_size
    jobs, total = await admin_service.list_jobs(
        skip=skip,
        limit=page_size,
        job_type=job_type,
        status=status,
    )
    
    return {
        "items": jobs,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size,
    }


@router.post("/jobs/{job_id}/cancel")
async def cancel_job_admin(
    job_id: UUID,
    admin_user: User = Depends(get_current_admin_user),
    admin_service: AdminService = Depends(get_admin_service),
):
    """Cancel a job (admin only)."""
    await admin_service.cancel_job(job_id)
    return {"message": "Job cancelled successfully"}


@router.get("/system/settings", response_model=AdminSystemSettings)
async def get_system_settings(
    admin_user: User = Depends(get_current_admin_user),
    admin_service: AdminService = Depends(get_admin_service),
):
    """Get system settings (admin only)."""
    settings = await admin_service.get_system_settings()
    return settings


@router.patch("/system/settings", response_model=AdminSystemSettings)
async def update_system_settings(
    request: AdminSystemSettings,
    admin_user: User = Depends(get_current_admin_user),
    admin_service: AdminService = Depends(get_admin_service),
):
    """Update system settings (admin only)."""
    settings = await admin_service.update_system_settings(
        updates=request.dict(exclude_unset=True),
    )
    return settings


@router.get("/system/logs")
async def get_system_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    level: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    admin_user: User = Depends(get_current_admin_user),
    admin_service: AdminService = Depends(get_admin_service),
):
    """Get system logs (admin only)."""
    skip = (page - 1) * page_size
    logs, total = await admin_service.get_logs(
        skip=skip,
        limit=page_size,
        level=level,
        start_date=start_date,
        end_date=end_date,
    )
    
    return {
        "items": logs,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size,
    }


@router.get("/system/health")
async def get_system_health(
    admin_user: User = Depends(get_current_admin_user),
    admin_service: AdminService = Depends(get_admin_service),
):
    """Get system health status (admin only)."""
    health = await admin_service.get_system_health()
    return health