"""Project model."""

from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4

from sqlalchemy import String, DateTime, Enum, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.constants import ProjectStatus


class Project(Base):
    """Project model."""
    
    __tablename__ = "projects"
    
    id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(PGUUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    status: Mapped[ProjectStatus] = mapped_column(Enum(ProjectStatus), default=ProjectStatus.ACTIVE, index=True)
    
    settings: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True, default={})
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="projects")
    websites: Mapped[List["Website"]] = relationship("Website", back_populates="project", cascade="all, delete-orphan")
    storyboards: Mapped[List["Storyboard"]] = relationship("Storyboard", back_populates="project", cascade="all, delete-orphan")
    videos: Mapped[List["Video"]] = relationship("Video", back_populates="project", cascade="all, delete-orphan")
    assets: Mapped[List["Asset"]] = relationship("Asset", back_populates="project", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_projects_user_status", "user_id", "status"),
        Index("idx_projects_created_at", "created_at"),
    )
    
    def __repr__(self) -> str:
        return f"<Project {self.name}>"