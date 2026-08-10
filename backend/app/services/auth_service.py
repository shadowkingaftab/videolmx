"""Authentication service."""

from datetime import datetime, timedelta
from uuid import UUID
from typing import Dict, Any, Optional

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.security import password_hasher, jwt_manager
from app.core.errors import AuthenticationError, ValidationError
from app.core.cache import get_cache


class AuthService:
    """Authentication service."""
    
    def __init__(self, user_repository: UserRepository):
        self.user_repo = user_repository
    
    async def authenticate(self, email: str, password: str) -> User:
        """Authenticate user with email and password."""
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise AuthenticationError("Invalid credentials")
        
        if not password_hasher.verify_password(password, user.password_hash):
            raise AuthenticationError("Invalid credentials")
        
        if not user.is_active:
            raise AuthenticationError("Account is deactivated")
        
        # Update last login
        user.last_login_at = datetime.utcnow()
        await self.user_repo.update(user)
        
        return user
    
    async def register(self, email: str, password: str, full_name: str) -> User:
        """Register a new user."""
        # Check if user exists
        existing = await self.user_repo.get_by_email(email)
        if existing:
            raise ValidationError("Email already registered")
        
        # Validate password
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters")
        
        # Create user
        user = User(
            email=email,
            password_hash=password_hasher.hash_password(password),
            full_name=full_name,
            is_active=True,
            is_verified=False,
        )
        
        user = await self.user_repo.create(user)
        return user
    
    async def create_tokens(self, user: User) -> Dict[str, str]:
        """Create access and refresh tokens."""
        access_token = jwt_manager.create_access_token(
            user_id=user.id,
            extra_data={"email": user.email}
        )
        refresh_token = jwt_manager.create_refresh_token(user.id)
        
        # Store refresh token in cache
        cache = await get_cache()
        await cache.setex(
            f"refresh_token:{user.id}",
            timedelta(days=7),
            refresh_token
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
    
    async def refresh_tokens(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token using refresh token."""
        try:
            payload = jwt_manager.decode_token(refresh_token)
            if payload.get("type") != "refresh":
                raise AuthenticationError("Invalid refresh token")
            
            user_id = UUID(payload["sub"])
            
            # Verify refresh token in cache
            cache = await get_cache()
            stored = await cache.get(f"refresh_token:{user_id}")
            if not stored or stored != refresh_token:
                raise AuthenticationError("Invalid refresh token")
            
            # Get user
            user = await self.user_repo.get(user_id)
            if not user:
                raise AuthenticationError("User not found")
            
            # Create new tokens
            tokens = await self.create_tokens(user)
            tokens["user_id"] = str(user.id)
            return tokens
            
        except Exception as e:
            raise AuthenticationError(str(e))
    
    async def get_user_from_token(self, token: str) -> Optional[User]:
        """Get user from access token."""
        try:
            payload = jwt_manager.decode_token(token)
            if payload.get("type") != "access":
                return None
            
            user_id = UUID(payload["sub"])
            user = await self.user_repo.get(user_id)
            
            if user and user.is_active:
                return user
            return None
            
        except Exception:
            return None
    
    async def logout(self, user_id: UUID) -> None:
        """Logout user by invalidating refresh token."""
        cache = await get_cache()
        await cache.delete(f"refresh_token:{user_id}")
    
    async def change_password(
        self,
        user_id: UUID,
        current_password: str,
        new_password: str
    ) -> None:
        """Change user password."""
        user = await self.user_repo.get(user_id)
        if not user:
            raise AuthenticationError("User not found")
        
        if not password_hasher.verify_password(current_password, user.password_hash):
            raise AuthenticationError("Invalid current password")
        
        if len(new_password) < 8:
            raise ValidationError("Password must be at least 8 characters")
        
        user.password_hash = password_hasher.hash_password(new_password)
        await self.user_repo.update(user)
    
    async def request_password_reset(self, email: str) -> None:
        """Request password reset."""
        # This would send an email with reset link
        pass
    
    async def reset_password(self, token: str, new_password: str) -> None:
        """Reset password with token."""
        # This would validate token and reset password
        pass