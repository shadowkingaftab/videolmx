"""Script model."""

from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4

from sqlalchemy import String, DateTime, ForeignKey, JSON, Text, Boolean, Index
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Script(Base):
    """Script model."""
    
    __tablename__ = "scripts"
    
    id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True, default=uuid4)
    storyboard_id: Mapped[UUID] = mapped_column(PGUUID, ForeignKey("storyboards.id", ondelete="CASCADE"), nullable=False, index=True)
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    language: Mapped[str] = mapped_column(String(10), default="en")
    
    tone: Mapped[str] = mapped_column(String(50), default="professional")
    length: Mapped[str] = mapped_column(String(50), default="medium")
    
    # Full script content
    content: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    scenes: Mapped[Optional[List[dict]]] = mapped_column(JSONB, nullable=True)
    
    # Narration script with timing
    narration: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Captions
    captions: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Quality metrics
    quality_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    readability_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    is_generated: Mapped[bool] = mapped_column(Boolean, default=False)
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False)
    
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True, default={})
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    storyboard: Mapped["Storyboard"] = relationship("Storyboard", back_populates="scripts")
    narrations: Mapped[List["Narration"]] = relationship("Narration", back_populates="script", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_scripts_storyboard", "storyboard_id"),
    )
    
    def __repr__(self) -> str:
        return f"<Script {self.name} - {self.language}>"