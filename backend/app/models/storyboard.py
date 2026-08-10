"""Storyboard and Scene models."""

from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4

from sqlalchemy import String, DateTime, ForeignKey, Integer, JSON, Text, Index, Float
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Storyboard(Base):
    """Storyboard model."""
    
    __tablename__ = "storyboards"
    
    id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True, default=uuid4)
    project_id: Mapped[UUID] = mapped_column(PGUUID, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    template: Mapped[str] = mapped_column(String(50), default="default")
    style: Mapped[str] = mapped_column(String(50), default="professional")
    
    total_scenes: Mapped[int] = mapped_column(Integer, default=0)
    estimated_duration: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    settings: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True, default={})
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True, default={})
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="storyboards")
    scenes: Mapped[List["Scene"]] = relationship("Scene", back_populates="storyboard", cascade="all, delete-orphan", order_by="Scene.order")
    scripts: Mapped[List["Script"]] = relationship("Script", back_populates="storyboard", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_storyboards_project_created", "project_id", "created_at"),
    )
    
    def __repr__(self) -> str:
        return f"<Storyboard {self.name} - {self.total_scenes} scenes>"


class Scene(Base):
    """Scene model."""
    
    __tablename__ = "scenes"
    
    id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True, default=uuid4)
    storyboard_id: Mapped[UUID] = mapped_column(PGUUID, ForeignKey("storyboards.id", ondelete="CASCADE"), nullable=False, index=True)
    
    order: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Scene type: intro, feature, testimonial, pricing, conclusion, etc.
    scene_type: Mapped[str] = mapped_column(String(50), nullable=False, default="feature")
    
    # Duration in seconds
    duration: Mapped[float] = mapped_column(Float, nullable=False, default=5.0)
    
    # Visual elements
    screenshot_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    video_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    background_color: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Animation settings
    camera_movement: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    zoom_effect: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    highlight_areas: Mapped[Optional[List[dict]]] = mapped_column(JSONB, nullable=True)
    overlays: Mapped[Optional[List[dict]]] = mapped_column(JSONB, nullable=True)
    
    # Narration
    narration_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    voice_settings: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Transition
    transition_type: Mapped[str] = mapped_column(String(50), default="fade")
    transition_duration: Mapped[float] = mapped_column(Float, default=0.5)
    
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True, default={})
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    storyboard: Mapped["Storyboard"] = relationship("Storyboard", back_populates="scenes")
    
    __table_args__ = (
        Index("idx_scenes_storyboard_order", "storyboard_id", "order"),
    )
    
    def __repr__(self) -> str:
        return f"<Scene {self.order}: {self.title}>"