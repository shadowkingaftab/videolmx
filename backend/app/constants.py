"""Application constants."""

from enum import Enum
from typing import Dict, Any

# ==========================================
# Status Constants
# ==========================================

class JobStatus(str, Enum):
    """Job status enumeration."""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"
    RETRYING = "retrying"


class CrawlStatus(str, Enum):
    """Crawl status enumeration."""
    INITIALIZING = "initializing"
    CRAWLING = "crawling"
    PARSING = "parsing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AnalysisStatus(str, Enum):
    """Analysis status enumeration."""
    PENDING = "pending"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"


class RenderingStatus(str, Enum):
    """Rendering status enumeration."""
    PENDING = "pending"
    RENDERING = "rendering"
    COMPLETED = "completed"
    FAILED = "failed"


class ExportStatus(str, Enum):
    """Export status enumeration."""
    PENDING = "pending"
    EXPORTING = "exporting"
    COMPLETED = "completed"
    FAILED = "failed"


class VideoStatus(str, Enum):
    """Video status enumeration."""
    DRAFT = "draft"
    GENERATING = "generating"
    RENDERING = "rendering"
    READY = "ready"
    FAILED = "failed"
    EXPIRED = "expired"


class ProjectStatus(str, Enum):
    """Project status enumeration."""
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


# ==========================================
# Plan Types
# ==========================================

class PlanType(str, Enum):
    """Subscription plan types."""
    FREE = "free"
    PRO = "pro"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"


class FeatureFlag(str, Enum):
    """Feature flags."""
    AI_AVATAR = "ai_avatar"
    MULTI_LANGUAGE = "multi_language"
    INTERACTIVE_EDITOR = "interactive_editor"
    BATCH_GENERATION = "batch_generation"
    API_ACCESS = "api_access"
    WHITE_LABEL = "white_label"
    PRIORITY_QUEUE = "priority_queue"
    CUSTOM_BRANDING = "custom_branding"
    ADVANCED_ANALYTICS = "advanced_analytics"
    TEAM_COLLABORATION = "team_collaboration"


# ==========================================
# File Types
# ==========================================

class AssetType(str, Enum):
    """Asset type enumeration."""
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    FONT = "font"
    DOCUMENT = "document"
    OTHER = "other"


class ExportFormat(str, Enum):
    """Export format enumeration."""
    MP4 = "mp4"
    WEBM = "webm"
    GIF = "gif"
    AVI = "avi"
    MOV = "mov"


class VoiceGender(str, Enum):
    """Voice gender enumeration."""
    MALE = "male"
    FEMALE = "female"
    NEUTRAL = "neutral"


class VoiceAccent(str, Enum):
    """Voice accent enumeration."""
    AMERICAN = "american"
    BRITISH = "british"
    AUSTRALIAN = "australian"
    INDIAN = "indian"


# ==========================================
# Error Codes
# ==========================================

class ErrorCode(str, Enum):
    """Error codes for API responses."""
    # Authentication errors (1000-1099)
    INVALID_CREDENTIALS = "AUTH_1001"
    TOKEN_EXPIRED = "AUTH_1002"
    INSUFFICIENT_PERMISSIONS = "AUTH_1003"
    USER_NOT_FOUND = "AUTH_1004"
    EMAIL_ALREADY_EXISTS = "AUTH_1005"
    
    # Validation errors (1100-1199)
    INVALID_INPUT = "VALID_1101"
    REQUIRED_FIELD = "VALID_1102"
    INVALID_FORMAT = "VALID_1103"
    INVALID_URL = "VALID_1104"
    
    # Resource errors (1200-1299)
    NOT_FOUND = "RES_1201"
    ALREADY_EXISTS = "RES_1202"
    CONFLICT = "RES_1203"
    
    # Processing errors (1300-1399)
    CRAWL_FAILED = "PROC_1301"
    ANALYSIS_FAILED = "PROC_1302"
    GENERATION_FAILED = "PROC_1303"
    RENDER_FAILED = "PROC_1304"
    EXPORT_FAILED = "PROC_1305"
    
    # Storage errors (1400-1499)
    UPLOAD_FAILED = "STOR_1401"
    DOWNLOAD_FAILED = "STOR_1402"
    STORAGE_FULL = "STOR_1403"
    
    # Rate limit errors (1500-1599)
    RATE_LIMIT_EXCEEDED = "RATE_1501"
    QUOTA_EXCEEDED = "RATE_1502"
    
    # External service errors (1600-1699)
    AI_SERVICE_ERROR = "EXT_1601"
    TTS_SERVICE_ERROR = "EXT_1602"
    PAYMENT_ERROR = "EXT_1603"


# ==========================================
# Limits
# ==========================================

class Limits:
    """Application limits."""
    MAX_VIDEO_DURATION_SECONDS = 600  # 10 minutes
    MAX_VIDEO_SIZE_MB = 500
    MAX_WEBSITE_PAGES = 100
    MAX_PROJECTS_PER_USER = 50
    MAX_VIDEOS_PER_PROJECT = 100
    MAX_STORYBOARD_SCENES = 50
    MAX_ASSETS_PER_PROJECT = 1000
    MAX_UPLOAD_SIZE_MB = 100
    MAX_CONCURRENT_JOBS = 10


# ==========================================
# Default Values
# ==========================================

DEFAULT_VIDEO_SETTINGS = {
    "resolution": "1920x1080",
    "fps": 30,
    "crf": 23,
    "preset": "medium",
    "audio_codec": "aac",
    "video_codec": "h264",
    "bitrate": "5M",
}

DEFAULT_NARRATION_SETTINGS = {
    "voice": "21m00Tcm4TlvDq8ikWAM",
    "speed": 1.0,
    "pitch": 1.0,
    "language": "en",
    "emotion": "neutral",
}

DEFAULT_ANIMATION_SETTINGS = {
    "transition": "fade",
    "transition_duration": 0.5,
    "camera_pan": True,
    "zoom_effect": True,
    "highlight_effect": True,
    "cursor_effect": True,
}


# ==========================================
# Headers
# ==========================================

class Headers:
    """HTTP headers."""
    REQUEST_ID = "X-Request-ID"
    PROCESSING_TIME = "X-Processing-Time"
    RATE_LIMIT_LIMIT = "X-RateLimit-Limit"
    RATE_LIMIT_REMAINING = "X-RateLimit-Remaining"
    RATE_LIMIT_RESET = "X-RateLimit-Reset"
    CORRELATION_ID = "X-Correlation-ID"


# ==========================================
# Environment
# ==========================================

class Environment(str, Enum):
    """Environment enumeration."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"