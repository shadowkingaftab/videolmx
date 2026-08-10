"""Analysis job model."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import String, DateTime, ForeignKey, JSON, Float, Boolean, Index, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.constants import AnalysisStatus


class AnalysisJob(Base):
    """Analysis job model."""
    
    __tablename__ = "analysis_jobs"
    
    id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True, default=uuid4)
    website_id: Mapped[UUID] = mapped_column(PGUUID, ForeignKey("websites.id", ondelete="CASCADE"), nullable=False, index=True)
    
    status: Mapped[str] = mapped_column(String(50), default=AnalysisStatus.PENDING, index=True)
    progress: Mapped[float] = mapped_column(Float, default=0.0)
    
    analysis_type: Mapped[str] = mapped_column(String(50), nullable=False, default="full")
    depth: Mapped[str] = mapped_column(String(50), default="standard")
    
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    failed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    error_message: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    error_details: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Analysis results
    semantic_understanding: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    ui_analysis: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    feature_extraction: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    navigation_graph: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    value_proposition: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    confidence_scores: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True, default={})
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    website: Mapped["Website"] = relationship("Website", back_populates="analysis_jobs")
    
    __table_args__ = (
        Index("idx_analysis_jobs_website_status", "website_id", "status"),
        Index("idx_analysis_jobs_created_at", "created_at"),
    )
    
    def __repr__(self) -> str:
        return f"<AnalysisJob {self.id} - {self.status}>"