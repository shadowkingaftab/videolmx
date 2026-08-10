"""Narration model."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import String, DateTime, ForeignKey, JSON, Float, Boolean, Index
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Narration(Base):
    """Narration model."""
    
    __tablename__ = "narrations"
    
    id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True, default=uuid4)
    script_id: Mapped[UUID] = mapped_column(PGUUID, ForeignKey("scripts.id", ondelete="CASCADE"), nullable=False, index=True)
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Voice settings
    voice_id: Mapped[str] = mapped_column(String(100), nullable=False)
    voice_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    language: Mapped[str] = mapped_column(String(10), default="en")
    
    speed: Mapped[float] = mapped_column(Float, default=1.0)
    pitch: Mapped[float] = mapped_column(Float, default=1.0)
    emotion: Mapped[str] = mapped_column(String(50), default="neutral")
    
    # Audio details
    audio_duration: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    audio_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    audio_storage_key: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Audio file size in bytes
    audio_size: Mapped[Optional[int]] = mapped_column(Float, nullable=True)
    
    # Alignment data (word-level timing)
    alignment_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Status
    is_generated: Mapped[bool] = mapped_column(Boolean, default=False)
    is_final: Mapped[bool] = mapped_column(Boolean, default=False)
    
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True, default={})
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    script: Mapped["Script"] = relationship("Script", back_populates="narrations")
    
    __table_args__ = (
        Index("idx_narrations_script", "script_id"),
        Index("idx_narrations_voice", "voice_id"),
    )
    
    def __repr__(self) -> str:
        return f"<Narration {self.name} - {self.voice_id}>"