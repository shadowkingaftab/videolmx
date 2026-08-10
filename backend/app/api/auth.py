"""Authentication API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer

from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RefreshTokenRequest,
    PasswordResetRequest,
    PasswordResetConfirmRequest,
    ChangePasswordRequest,
)
from app.services.auth_service import AuthService
from app.dependencies import get_auth_service, get_current_user
from app.models.user import User
from app.core.errors import AuthenticationError, NotFoundError

router = APIRouter()
security = HTTPBearer()


@router.post("/register", response_model=LoginResponse)
async def register(
    request: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Register a new user."""
    user = await auth_service.register(
        email=request.email,
        password=request.password,
        full_name=request.full_name,
    )
    
    tokens = await auth_service.create_tokens(user)
    return LoginResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type="bearer",
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
    )


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Login with email and password."""
    try:
        user = await auth_service.authenticate(
            email=request.email,
            password=request.password,
        )
        
        tokens = await auth_service.create_tokens(user)
        return LoginResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type="bearer",
            user_id=user.id,
            email=user.email,
            full_name=user.full_name,
        )
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/refresh", response_model=LoginResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Refresh access token."""
    try:
        tokens = await auth_service.refresh_tokens(request.refresh_token)
        return LoginResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type="bearer",
            user_id=tokens["user_id"],
        )
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/logout")
async def logout(
    user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Logout user."""
    await auth_service.logout(user.id)
    return {"message": "Successfully logged out"}


@router.post("/password-reset")
async def request_password_reset(
    request: PasswordResetRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Request password reset email."""
    try:
        await auth_service.request_password_reset(request.email)
        return {"message": "Password reset email sent"}
    except NotFoundError:
        # Don't reveal if user exists
        return {"message": "Password reset email sent"}


@router.post("/password-reset/confirm")
async def confirm_password_reset(
    request: PasswordResetConfirmRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Confirm password reset with token."""
    await auth_service.reset_password(
        token=request.token,
        new_password=request.new_password,
    )
    return {"message": "Password successfully reset"}


@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Change user password."""
    await auth_service.change_password(
        user_id=user.id,
        current_password=request.current_password,
        new_password=request.new_password,
    )
    return {"message": "Password successfully changed"}


@router.get("/me")
async def get_current_user_info(
    user: User = Depends(get_current_user),
):
    """Get current user info."""
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "is_active": user.is_active,
        "is_admin": user.is_admin,
        "created_at": user.created_at,
        "plan": user.plan,
    }