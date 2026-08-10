"""Asset model."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import String, DateTime, ForeignKey, Integer, JSON, Text, Boolean, Index
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.constants import AssetType


class Asset(Base):
    """Asset model."""
    
    __tablename__ = "assets"
    
    id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True, default=uuid4)
    project_id: Mapped[UUID] = mapped_column(PGUUID, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    storage_key: Mapped[str] = mapped_column(String(500), nullable=False)
    url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    content_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    width: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    height: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    duration: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    thumbnail_key: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True, default={})
    tags: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True, default=[])
    
    is_processed: Mapped[bool] = mapped_column(Boolean, default=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    
    source_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    source_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="assets")
    
    __table_args__ = (
        Index("idx_assets_project_type", "project_id", "type"),
        Index("idx_assets_created_at", "created_at"),
        Index("idx_assets_tags", "tags", postgresql_using="gin"),
    )
    
    def __repr__(self) -> str:
        return f"<Asset {self.name} - {self.type}>"