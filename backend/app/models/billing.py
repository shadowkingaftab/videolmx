"""Billing models."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import String, DateTime, ForeignKey, JSON, Float, Boolean, Integer, Enum, Index
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.constants import PlanType


class Subscription(Base):
    """Subscription model."""
    
    __tablename__ = "subscriptions"
    
    id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(PGUUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    stripe_subscription_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, unique=True, index=True)
    stripe_customer_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    
    plan: Mapped[PlanType] = mapped_column(Enum(PlanType), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    current_period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    current_period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    cancel_at_period_end: Mapped[bool] = mapped_column(Boolean, default=False)
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    price: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="usd")
    
    features: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True, default={})
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User")
    
    __table_args__ = (
        Index("idx_subscriptions_user", "user_id"),
        Index("idx_subscriptions_status", "status"),
    )


class Invoice(Base):
    """Invoice model."""
    
    __tablename__ = "invoices"
    
    id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(PGUUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    stripe_invoice_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    stripe_payment_intent_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    invoice_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    
    status: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="usd")
    
    invoice_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    pdf_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    line_items: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True, default={})
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User")
    
    __table_args__ = (
        Index("idx_invoices_user_status", "user_id", "status"),
        Index("idx_invoices_date", "invoice_date"),
    )


class PaymentMethod(Base):
    """Payment method model."""
    
    __tablename__ = "payment_methods"
    
    id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(PGUUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    stripe_payment_method_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    last4: Mapped[Optional[str]] = mapped_column(String(4), nullable=True)
    exp_month: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    exp_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    brand: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    billing_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    billing_address: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True, default={})
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User")
    
    __table_args__ = (
        Index("idx_payment_methods_user_default", "user_id", "is_default"),
    )