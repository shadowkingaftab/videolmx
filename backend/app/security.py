"""Security utilities."""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from uuid import UUID

import bcrypt
import jwt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from app.config import settings
from app.core.errors import AuthenticationError


class PasswordHasher:
    """Password hashing utility."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt."""
        salt = bcrypt.gensalt(rounds=settings.BCRYPT_ROUNDS)
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify a password against its hash."""
        try:
            return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
        except ValueError:
            return False


class JWTManager:
    """JWT token management."""
    
    @staticmethod
    def create_access_token(
        user_id: UUID,
        expires_delta: Optional[timedelta] = None,
        extra_data: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Create an access token."""
        if expires_delta is None:
            expires_delta = timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
        
        payload = {
            "sub": str(user_id),
            "exp": datetime.utcnow() + expires_delta,
            "iat": datetime.utcnow(),
            "type": "access",
        }
        
        if extra_data:
            payload.update(extra_data)
        
        return jwt.encode(
            payload,
            settings.SECRET_KEY.get_secret_value(),
            algorithm=settings.JWT_ALGORITHM,
        )
    
    @staticmethod
    def create_refresh_token(user_id: UUID) -> str:
        """Create a refresh token."""
        expires_delta = timedelta(days=settings.JWT_REFRESH_EXPIRE_DAYS)
        payload = {
            "sub": str(user_id),
            "exp": datetime.utcnow() + expires_delta,
            "iat": datetime.utcnow(),
            "type": "refresh",
        }
        return jwt.encode(
            payload,
            settings.SECRET_KEY.get_secret_value(),
            algorithm=settings.JWT_ALGORITHM,
        )
    
    @staticmethod
    def decode_token(token: str) -> Dict[str, Any]:
        """Decode and validate a token."""
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY.get_secret_value(),
                algorithms=[settings.JWT_ALGORITHM],
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise AuthenticationError(f"Invalid token: {str(e)}")
    
    @staticmethod
    def get_user_id_from_token(token: str) -> UUID:
        """Extract user ID from token."""
        payload = JWTManager.decode_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationError("Invalid token: missing user ID")
        return UUID(user_id)


class EncryptionManager:
    """Encryption utilities for sensitive data."""
    
    def __init__(self):
        """Initialize encryption manager."""
        # Generate key from secret
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"website2video_salt",
            iterations=100000,
        )
        key = kdf.derive(settings.SECRET_KEY.get_secret_value().encode())
        self.cipher = Fernet(base64.urlsafe_b64encode(key))
    
    def encrypt(self, data: str) -> str:
        """Encrypt data."""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted: str) -> str:
        """Decrypt data."""
        return self.cipher.decrypt(encrypted.encode()).decode()
    
    def encrypt_dict(self, data: Dict[str, Any]) -> str:
        """Encrypt a dictionary."""
        import json
        return self.encrypt(json.dumps(data))
    
    def decrypt_dict(self, encrypted: str) -> Dict[str, Any]:
        """Decrypt a dictionary."""
        import json
        return json.loads(self.decrypt(encrypted))


class APIKeyManager:
    """API key management."""
    
    @staticmethod
    def generate_api_key() -> Tuple[str, str]:
        """Generate a new API key pair."""
        prefix = "wk2v"
        key = secrets.token_urlsafe(32)
        secret = secrets.token_urlsafe(32)
        return f"{prefix}_{key}", secret
    
    @staticmethod
    def hash_api_key(api_key: str) -> str:
        """Hash an API key for storage."""
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    @staticmethod
    def verify_api_key(api_key: str, hashed: str) -> bool:
        """Verify an API key against its hash."""
        return hashlib.sha256(api_key.encode()).hexdigest() == hashed


class CSRFProtection:
    """CSRF protection utilities."""
    
    @staticmethod
    def generate_csrf_token() -> str:
        """Generate a CSRF token."""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def verify_csrf_token(token: str, stored: str) -> bool:
        """Verify a CSRF token."""
        return secrets.compare_digest(token, stored)


# Singleton instances
password_hasher = PasswordHasher()
jwt_manager = JWTManager()
encryption_manager = EncryptionManager()
api_key_manager = APIKeyManager()
csrf_protection = CSRFProtection()