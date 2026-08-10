"""User management API endpoints."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_current_user, get_current_admin_user, get_user_service
from app.models.user import User
from app.services.user_service import UserService
from app.schemas.user import UserResponse, UserUpdateRequest, UserListResponse
from app.schemas.common import PaginatedResponse
from app.core.errors import NotFoundError

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[UserListResponse])
async def list_users(
    page: int = 1,
    page_size: int = 20,
    admin_user: User = Depends(get_current_admin_user),
    user_service: UserService = Depends(get_user_service),
):
    """List all users (admin only)."""
    skip = (page - 1) * page_size
    users, total = await user_service.list_users(
        skip=skip,
        limit=page_size,
    )
    
    return PaginatedResponse(
        items=users,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    """Get user by ID."""
    # Users can only view their own profile unless admin
    if user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    user = await user_service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return user


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    request: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    """Update user."""
    # Users can only update their own profile unless admin
    if user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    try:
        user = await user_service.update_user(user_id, request.dict(exclude_unset=True))
        return user
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )


@router.delete("/{user_id}")
async def delete_user(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    """Delete user."""
    # Users can only delete their own account unless admin
    if user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    try:
        await user_service.delete_user(user_id)
        return {"message": "User deleted successfully"}
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )


@router.post("/{user_id}/activate")
async def activate_user(
    user_id: UUID,
    admin_user: User = Depends(get_current_admin_user),
    user_service: UserService = Depends(get_user_service),
):
    """Activate user (admin only)."""
    try:
        await user_service.activate_user(user_id)
        return {"message": "User activated successfully"}
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )


@router.post("/{user_id}/deactivate")
async def deactivate_user(
    user_id: UUID,
    admin_user: User = Depends(get_current_admin_user),
    user_service: UserService = Depends(get_user_service),
):
    """Deactivate user (admin only)."""
    try:
        await user_service.deactivate_user(user_id)
        return {"message": "User deactivated successfully"}
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )


@router.get("/{user_id}/stats")
async def get_user_stats(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    """Get user statistics."""
    if user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    stats = await user_service.get_user_stats(user_id)
    return stats