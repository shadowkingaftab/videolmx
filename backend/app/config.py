"""Application configuration management."""

from typing import List, Optional, Dict, Any
from functools import lru_cache

from pydantic import Field, PostgresDsn, RedisDsn, SecretStr, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Project
    PROJECT_NAME: str = "Website2Video AI"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Transform any website into a professional AI-generated explainer video"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # API
    API_V1_STR: str = "/api/v1"
    DOCS_URL: str = "/docs"
    REDOC_URL: str = "/redoc"
    OPENAPI_URL: str = "/openapi.json"
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Security
    SECRET_KEY: SecretStr = Field(..., min_length=32)
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_EXPIRE_DAYS: int = 7
    BCRYPT_ROUNDS: int = 12
    SESSION_TIMEOUT_MINUTES: int = 60
    
    # Database
    DATABASE_URL: PostgresDsn = Field(
        "postgresql+asyncpg://user:pass@localhost:5432/website2video"
    )
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 40
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_ECHO: bool = False
    
    @validator("DATABASE_URL", pre=True)
    def validate_database_url(cls, v: str) -> str:
        """Ensure asyncpg driver is used."""
        if "postgresql" in v and "asyncpg" not in v:
            return v.replace("postgresql://", "postgresql+asyncpg://")
        return v
    
    # Redis
    REDIS_URL: RedisDsn = Field("redis://localhost:6379/0")
    REDIS_BROKER_URL: RedisDsn = Field("redis://localhost:6379/1")
    REDIS_BACKEND_URL: RedisDsn = Field("redis://localhost:6379/2")
    REDIS_CACHE_URL: RedisDsn = Field("redis://localhost:6379/3")
    REDIS_MAX_CONNECTIONS: int = 10
    REDIS_CACHE_TTL_SECONDS: int = 3600
    
    # MinIO / Object Storage
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_SECURE: bool = False
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: SecretStr = Field("minioadmin123")
    MINIO_BUCKET_ASSETS: str = "assets"
    MINIO_BUCKET_VIDEOS: str = "videos"
    MINIO_BUCKET_UPLOADS: str = "uploads"
    MINIO_BUCKET_EXPORTS: str = "exports"
    MINIO_BUCKET_CACHE: str = "cache"
    
    # AI Services
    OPENAI_API_KEY: Optional[SecretStr] = None
    OPENAI_ORG_ID: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-ada-002"
    OPENAI_MAX_TOKENS: int = 4000
    OPENAI_TEMPERATURE: float = 0.7
    
    ANTHROPIC_API_KEY: Optional[SecretStr] = None
    ANTHROPIC_MODEL: str = "claude-3-opus-20240229"
    
    GOOGLE_API_KEY: Optional[SecretStr] = None
    GOOGLE_MODEL: str = "gemini-pro"
    
    # Voice Generation
    ELEVENLABS_API_KEY: Optional[SecretStr] = None
    ELEVENLABS_DEFAULT_VOICE: str = "21m00Tcm4TlvDq8ikWAM"
    ELEVENLABS_MODEL: str = "eleven_monolingual_v1"
    
    # Rendering
    RENDER_VIDEO_RESOLUTION: str = "1920x1080"
    RENDER_VIDEO_FPS: int = 30
    RENDER_VIDEO_CRF: int = 23
    RENDER_VIDEO_PRESET: str = "medium"
    RENDER_MAX_WORKERS: int = 4
    RENDER_TEMP_DIR: str = "/tmp/rendering"
    RENDER_TIMEOUT_SECONDS: int = 3600
    
    # Playwright
    PLAYWRIGHT_HEADLESS: bool = True
    PLAYWRIGHT_TIMEOUT_MS: int = 30000
    PLAYWRIGHT_VIEWPORT_WIDTH: int = 1920
    PLAYWRIGHT_VIEWPORT_HEIGHT: int = 1080
    PLAYWRIGHT_USER_AGENT: str = "Mozilla/5.0 (compatible; Website2Video/1.0)"
    PLAYWRIGHT_MAX_PAGES: int = 100
    PLAYWRIGHT_NAVIGATION_TIMEOUT: int = 60000
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    CELERY_TASK_ALWAYS_EAGER: bool = False
    CELERY_TASK_ACKS_LATE: bool = True
    CELERY_TASK_REJECT_ON_WORKER_LOST: bool = True
    CELERY_TASK_TRACK_STARTED: bool = True
    CELERY_TASK_TIME_LIMIT: int = 3600
    CELERY_TASK_SOFT_TIME_LIMIT: int = 3300
    CELERY_WORKER_CONCURRENCY: int = 4
    CELERY_WORKER_PREFETCH_MULTIPLIER: int = 1
    CELERY_WORKER_MAX_TASKS_PER_CHILD: int = 100
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    LOG_FILE_PATH: str = "/var/log/website2video/app.log"
    LOG_MAX_BYTES: int = 10485760  # 10MB
    LOG_BACKUP_COUNT: int = 5
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    PROMETHEUS_ENABLED: bool = True
    PROMETHEUS_PORT: int = 9090
    METRICS_ENABLED: bool = True
    
    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[SecretStr] = None
    SMTP_FROM_EMAIL: str = "noreply@website2video.com"
    SMTP_USE_TLS: bool = True
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 120
    RATE_LIMIT_STORAGE_URL: str = "redis://localhost:6379/4"
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # File upload
    MAX_UPLOAD_SIZE_MB: int = 100
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", "image/webp", "image/svg+xml"]
    ALLOWED_VIDEO_TYPES: List[str] = ["video/mp4", "video/webm", "video/quicktime"]
    
    # Crawling
    CRAWL_MAX_DEPTH: int = 3
    CRAWL_MAX_PAGES: int = 50
    CRAWL_REQUEST_TIMEOUT: int = 30
    CRAWL_RETRY_ATTEMPTS: int = 3
    CRAWL_DELAY_BETWEEN_REQUESTS: float = 0.5
    CRAWL_RESPECT_ROBOTS: bool = True
    CRAWL_USER_AGENT: str = "Website2Video-Crawler/1.0"
    
    # Feature flags
    ENABLE_AI_AVATAR: bool = False
    ENABLE_MULTI_LANGUAGE: bool = True
    ENABLE_INTERACTIVE_EDITOR: bool = True
    ENABLE_BATCH_GENERATION: bool = False
    ENABLE_API_ACCESS: bool = False
    ENABLE_WHITE_LABEL: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()