"""User settings API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_current_user
from app.models.user import User
from app.services.user_service import UserService
from app.schemas.settings import (
    UserSettings,
    UserSettingsUpdate,
    NotificationSettings,
    NotificationSettingsUpdate,
)

router = APIRouter()


@router.get("/profile", response_model=UserSettings)
async def get_user_settings(
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(UserService),
):
    """Get user settings."""
    settings = await user_service.get_settings(current_user.id)
    return settings


@router.patch("/profile", response_model=UserSettings)
async def update_user_settings(
    request: UserSettingsUpdate,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(UserService),
):
    """Update user settings."""
    settings = await user_service.update_settings(
        user_id=current_user.id,
        updates=request.dict(exclude_unset=True),
    )
    return settings


@router.get("/notifications", response_model=NotificationSettings)
async def get_notification_settings(
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(UserService),
):
    """Get notification settings."""
    settings = await user_service.get_notification_settings(current_user.id)
    return settings


@router.patch("/notifications", response_model=NotificationSettings)
async def update_notification_settings(
    request: NotificationSettingsUpdate,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(UserService),
):
    """Update notification settings."""
    settings = await user_service.update_notification_settings(
        user_id=current_user.id,
        updates=request.dict(exclude_unset=True),
    )
    return settings


@router.get("/api-keys")
async def list_api_keys(
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(UserService),
):
    """List user's API keys."""
    keys = await user_service.list_api_keys(current_user.id)
    return {"api_keys": keys}


@router.post("/api-keys")
async def create_api_key(
    name: str,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(UserService),
):
    """Create a new API key."""
    key, secret = await user_service.create_api_key(
        user_id=current_user.id,
        name=name,
    )
    return {
        "id": key.id,
        "name": key.name,
        "key": key.key,
        "secret": secret,
        "created_at": key.created_at,
    }


@router.delete("/api-keys/{key_id}")
async def delete_api_key(
    key_id: str,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(UserService),
):
    """Delete an API key."""
    await user_service.delete_api_key(
        user_id=current_user.id,
        key_id=key_id,
    )
    return {"message": "API key deleted successfully"}