"""Crawl job model."""

from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4

from sqlalchemy import String, DateTime, ForeignKey, Integer, JSON, Float, Boolean, Index
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.constants import JobStatus


class CrawlJob(Base):
    """Crawl job model."""
    
    __tablename__ = "crawl_jobs"
    
    id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True, default=uuid4)
    website_id: Mapped[UUID] = mapped_column(PGUUID, ForeignKey("websites.id", ondelete="CASCADE"), nullable=False, index=True)
    
    status: Mapped[str] = mapped_column(String(50), default=JobStatus.PENDING, index=True)
    progress: Mapped[float] = mapped_column(Float, default=0.0)
    
    max_pages: Mapped[int] = mapped_column(Integer, default=50)
    max_depth: Mapped[int] = mapped_column(Integer, default=3)
    include_assets: Mapped[bool] = mapped_column(Boolean, default=True)
    respect_robots: Mapped[bool] = mapped_column(Boolean, default=True)
    
    pages_crawled: Mapped[int] = mapped_column(Integer, default=0)
    total_pages: Mapped[int] = mapped_column(Integer, default=0)
    assets_collected: Mapped[int] = mapped_column(Integer, default=0)
    
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    failed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    error_message: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    error_details: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    results: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True, default={})
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    website: Mapped["Website"] = relationship("Website", back_populates="crawl_jobs")
    pages: Mapped[List["CrawledPage"]] = relationship("CrawledPage", back_populates="crawl_job", cascade="all, delete-orphan")
    assets: Mapped[List["CrawledAsset"]] = relationship("CrawledAsset", back_populates="crawl_job", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_crawl_jobs_website_status", "website_id", "status"),
        Index("idx_crawl_jobs_created_at", "created_at"),
    )
    
    def __repr__(self) -> str:
        return f"<CrawlJob {self.id} - {self.status}>"


class CrawledPage(Base):
    """Crawled page model."""
    
    __tablename__ = "crawled_pages"
    
    id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True, default=uuid4)
    crawl_job_id: Mapped[UUID] = mapped_column(PGUUID, ForeignKey("crawl_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    
    url: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    content_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    
    depth: Mapped[int] = mapped_column(Integer, default=0)
    status_code: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    html: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    text_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    links: Mapped[Optional[List[str]]] = mapped_column(JSONB, nullable=True)
    assets: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    screenshot_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    screenshot_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationships
    crawl_job: Mapped["CrawlJob"] = relationship("CrawlJob", back_populates="pages")
    
    __table_args__ = (
        Index("idx_crawled_pages_job_url", "crawl_job_id", "url"),
        Index("idx_crawled_pages_hash", "content_hash"),
    )


class CrawledAsset(Base):
    """Crawled asset model."""
    
    __tablename__ = "crawled_assets"
    
    id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True, default=uuid4)
    crawl_job_id: Mapped[UUID] = mapped_column(PGUUID, ForeignKey("crawl_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    content_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    storage_key: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    width: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    height: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationships
    crawl_job: Mapped["CrawlJob"] = relationship("CrawlJob", back_populates="assets")
    
    __table_args__ = (
        Index("idx_crawled_assets_job_type", "crawl_job_id", "type"),
    )