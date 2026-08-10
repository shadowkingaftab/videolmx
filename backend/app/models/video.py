"""Video model."""

from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4

from sqlalchemy import String, DateTime, ForeignKey, JSON, Float, Integer, Boolean, Index
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.constants import VideoStatus


class Video(Base):
    """Video model."""
    
    __tablename__ = "videos"
    
    id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True, default=uuid4)
    project_id: Mapped[UUID] = mapped_column(PGUUID, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    storyboard_id: Mapped[Optional[UUID]] = mapped_column(PGUUID, ForeignKey("storyboards.id"), nullable=True, index=True)
    script_id: Mapped[Optional[UUID]] = mapped_column(PGUUID, ForeignKey("scripts.id"), nullable=True, index=True)
    narration_id: Mapped[Optional[UUID]] = mapped_column(PGUUID, ForeignKey("narrations.id"), nullable=True, index=True)
    
    status: Mapped[str] = mapped_column(String(50), default=VideoStatus.DRAFT, index=True)
    progress: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Video settings
    resolution: Mapped[str] = mapped_column(String(50), default="1920x1080")
    fps: Mapped[int] = mapped_column(Integer, default=30)
    quality: Mapped[str] = mapped_column(String(50), default="medium")
    
    # Render settings
    include_captions: Mapped[bool] = mapped_column(Boolean, default=True)
    include_background_music: Mapped[bool] = mapped_column(Boolean, default=True)
    background_music_volume: Mapped[float] = mapped_column(Float, default=0.3)
    
    # Output
    duration: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    file_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    storage_key: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Preview
    preview_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Rendering metadata
    render_job_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    render_duration: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    render_started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    render_completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Error
    error_message: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    error_details: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True, default={})
    
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    share_count: Mapped[int] = mapped_column(Integer, default=0)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="videos")
    storyboard: Mapped[Optional["Storyboard"]] = relationship("Storyboard")
    exports: Mapped[List["Export"]] = relationship("Export", back_populates="video", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_videos_project_status", "project_id", "status"),
        Index("idx_videos_created_at", "created_at"),
        Index("idx_videos_updated_at", "updated_at"),
    )
    
    def __repr__(self) -> str:
        return f"<Video {self.name} - {self.status}>"