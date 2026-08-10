"""Export model."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import String, DateTime, ForeignKey, JSON, Float, Integer, Boolean, Index
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.constants import ExportStatus, ExportFormat


class Export(Base):
    """Export model."""
    
    __tablename__ = "exports"
    
    id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True, default=uuid4)
    video_id: Mapped[UUID] = mapped_column(PGUUID, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False, index=True)
    
    format: Mapped[str] = mapped_column(String(50), nullable=False)
    quality: Mapped[str] = mapped_column(String(50), default="medium")
    
    status: Mapped[str] = mapped_column(String(50), default=ExportStatus.PENDING, index=True)
    progress: Mapped[float] = mapped_column(Float, default=0.0)
    
    include_watermark: Mapped[bool] = mapped_column(Boolean, default=True)
    include_metadata: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Output
    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    file_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    storage_key: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    download_count: Mapped[int] = mapped_column(Integer, default=0)
    
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    error_message: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True, default={})
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    video: Mapped["Video"] = relationship("Video", back_populates="exports")
    
    __table_args__ = (
        Index("idx_exports_video_status", "video_id", "status"),
        Index("idx_exports_created_at", "created_at"),
    )
    
    def __repr__(self) -> str:
        return f"<Export {self.id} - {self.format}>"