"""Billing and subscription API endpoints."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.dependencies import get_current_user, get_billing_service
from app.models.user import User
from app.services.billing_service import BillingService
from app.schemas.billing import (
    PlanResponse,
    PlanListResponse,
    SubscriptionCreate,
    SubscriptionUpdate,
    SubscriptionResponse,
    InvoiceResponse,
    InvoiceListResponse,
    PaymentMethodResponse,
    PaymentMethodCreate,
)

router = APIRouter()


@router.get("/plans", response_model=PlanListResponse)
async def list_plans(
    current_user: User = Depends(get_current_user),
    billing_service: BillingService = Depends(get_billing_service),
):
    """List available subscription plans."""
    plans = await billing_service.list_plans()
    return {"plans": plans}


@router.get("/plans/{plan_id}", response_model=PlanResponse)
async def get_plan(
    plan_id: str,
    current_user: User = Depends(get_current_user),
    billing_service: BillingService = Depends(get_billing_service),
):
    """Get plan details."""
    plan = await billing_service.get_plan(plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found",
        )
    return plan


@router.get("/subscription", response_model=SubscriptionResponse)
async def get_subscription(
    current_user: User = Depends(get_current_user),
    billing_service: BillingService = Depends(get_billing_service),
):
    """Get current user's subscription."""
    subscription = await billing_service.get_subscription(current_user.id)
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription",
        )
    return subscription


@router.post("/subscription", response_model=SubscriptionResponse)
async def create_subscription(
    request: SubscriptionCreate,
    current_user: User = Depends(get_current_user),
    billing_service: BillingService = Depends(get_billing_service),
):
    """Create a new subscription."""
    try:
        subscription = await billing_service.create_subscription(
            user_id=current_user.id,
            plan_id=request.plan_id,
            payment_method_id=request.payment_method_id,
        )
        return subscription
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.patch("/subscription", response_model=SubscriptionResponse)
async def update_subscription(
    request: SubscriptionUpdate,
    current_user: User = Depends(get_current_user),
    billing_service: BillingService = Depends(get_billing_service),
):
    """Update subscription."""
    try:
        subscription = await billing_service.update_subscription(
            user_id=current_user.id,
            plan_id=request.plan_id,
            payment_method_id=request.payment_method_id,
        )
        return subscription
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/subscription/cancel")
async def cancel_subscription(
    current_user: User = Depends(get_current_user),
    billing_service: BillingService = Depends(get_billing_service),
):
    """Cancel subscription."""
    try:
        result = await billing_service.cancel_subscription(current_user.id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/invoices", response_model=InvoiceListResponse)
async def list_invoices(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    billing_service: BillingService = Depends(get_billing_service),
):
    """List user's invoices."""
    skip = (page - 1) * page_size
    invoices, total = await billing_service.list_invoices(
        user_id=current_user.id,
        skip=skip,
        limit=page_size,
    )
    
    return {
        "items": invoices,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size,
    }


@router.get("/invoices/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: str,
    current_user: User = Depends(get_current_user),
    billing_service: BillingService = Depends(get_billing_service),
):
    """Get invoice details."""
    invoice = await billing_service.get_invoice(invoice_id)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found",
        )
    return invoice


@router.get("/payment-methods", response_model=PaymentMethodResponse)
async def list_payment_methods(
    current_user: User = Depends(get_current_user),
    billing_service: BillingService = Depends(get_billing_service),
):
    """List user's payment methods."""
    methods = await billing_service.list_payment_methods(current_user.id)
    return {"payment_methods": methods}


@router.post("/payment-methods", response_model=PaymentMethodResponse)
async def create_payment_method(
    request: PaymentMethodCreate,
    current_user: User = Depends(get_current_user),
    billing_service: BillingService = Depends(get_billing_service),
):
    """Add a new payment method."""
    try:
        method = await billing_service.create_payment_method(
            user_id=current_user.id,
            payment_method_id=request.payment_method_id,
            set_default=request.set_default,
        )
        return method
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/payment-methods/{payment_method_id}")
async def delete_payment_method(
    payment_method_id: str,
    current_user: User = Depends(get_current_user),
    billing_service: BillingService = Depends(get_billing_service),
):
    """Delete a payment method."""
    try:
        result = await billing_service.delete_payment_method(
            user_id=current_user.id,
            payment_method_id=payment_method_id,
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post("/payment-methods/{payment_method_id}/default")
async def set_default_payment_method(
    payment_method_id: str,
    current_user: User = Depends(get_current_user),
    billing_service: BillingService = Depends(get_billing_service),
):
    """Set default payment method."""
    try:
        result = await billing_service.set_default_payment_method(
            user_id=current_user.id,
            payment_method_id=payment_method_id,
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get("/usage")
async def get_usage(
    current_user: User = Depends(get_current_user),
    billing_service: BillingService = Depends(get_billing_service),
):
    """Get usage statistics."""
    usage = await billing_service.get_usage(current_user.id)
    return usage