"""Billing service."""

from typing import Optional, List, Tuple, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta

from app.models.billing import Subscription, Invoice, PaymentMethod
from app.repositories.user_repository import UserRepository
from app.core.errors import NotFoundError, ValidationError


class BillingService:
    """Billing service."""
    
    def __init__(
        self,
        user_repo: UserRepository
    ):
        self.user_repo = user_repo
    
    async def list_plans(self) -> List[Dict[str, Any]]:
        """List available plans."""
        return [
            {
                "id": "free",
                "name": "Free",
                "price": 0,
                "currency": "usd",
                "features": {
                    "videos_per_month": 1,
                    "max_duration_minutes": 1,
                    "storage_gb": 0.1,
                    "ai_avatar": False,
                    "multi_language": False,
                    "batch_generation": False,
                    "api_access": False,
                    "white_label": False,
                }
            },
            {
                "id": "pro",
                "name": "Pro",
                "price": 49,
                "currency": "usd",
                "features": {
                    "videos_per_month": 10,
                    "max_duration_minutes": 5,
                    "storage_gb": 5,
                    "ai_avatar": True,
                    "multi_language": True,
                    "batch_generation": False,
                    "api_access": False,
                    "white_label": False,
                }
            },
            {
                "id": "business",
                "name": "Business",
                "price": 199,
                "currency": "usd",
                "features": {
                    "videos_per_month": 50,
                    "max_duration_minutes": 10,
                    "storage_gb": 50,
                    "ai_avatar": True,
                    "multi_language": True,
                    "batch_generation": True,
                    "api_access": True,
                    "white_label": False,
                }
            },
            {
                "id": "enterprise",
                "name": "Enterprise",
                "price": 499,
                "currency": "usd",
                "features": {
                    "videos_per_month": -1,
                    "max_duration_minutes": 30,
                    "storage_gb": 500,
                    "ai_avatar": True,
                    "multi_language": True,
                    "batch_generation": True,
                    "api_access": True,
                    "white_label": True,
                }
            },
        ]
    
    async def get_plan(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """Get plan by ID."""
        plans = await self.list_plans()
        for plan in plans:
            if plan["id"] == plan_id:
                return plan
        return None
    
    async def get_subscription(self, user_id: UUID) -> Optional[Dict[str, Any]]:
        """Get user's subscription."""
        # This would fetch from Stripe
        return {
            "id": "sub_123",
            "user_id": str(user_id),
            "plan_id": "pro",
            "status": "active",
            "current_period_start": datetime.utcnow().isoformat(),
            "current_period_end": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        }
    
    async def create_subscription(
        self,
        user_id: UUID,
        plan_id: str,
        payment_method_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new subscription."""
        plan = await self.get_plan(plan_id)
        if not plan:
            raise ValidationError("Invalid plan")
        
        # This would create in Stripe
        return {
            "id": "sub_123",
            "user_id": str(user_id),
            "plan_id": plan_id,
            "status": "active",
            "current_period_start": datetime.utcnow().isoformat(),
            "current_period_end": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        }
    
    async def update_subscription(
        self,
        user_id: UUID,
        plan_id: Optional[str] = None,
        payment_method_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update subscription."""
        if plan_id:
            plan = await self.get_plan(plan_id)
            if not plan:
                raise ValidationError("Invalid plan")
        
        # This would update in Stripe
        return {
            "id": "sub_123",
            "user_id": str(user_id),
            "plan_id": plan_id or "pro",
            "status": "active",
        }
    
    async def cancel_subscription(self, user_id: UUID) -> Dict[str, Any]:
        """Cancel subscription."""
        # This would cancel in Stripe
        return {
            "message": "Subscription cancelled",
            "effective_date": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        }
    
    async def list_invoices(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[Dict[str, Any]], int]:
        """List user's invoices."""
        # This would fetch from Stripe
        return [], 0
    
    async def get_invoice(self, invoice_id: str) -> Optional[Dict[str, Any]]:
        """Get invoice details."""
        # This would fetch from Stripe
        return {
            "id": invoice_id,
            "amount": 49,
            "currency": "usd",
            "status": "paid",
            "invoice_date": datetime.utcnow().isoformat(),
            "pdf_url": "https://example.com/invoice.pdf",
        }
    
    async def list_payment_methods(self, user_id: UUID) -> List[Dict[str, Any]]:
        """List user's payment methods."""
        return [
            {
                "id": "pm_123",
                "type": "card",
                "last4": "4242",
                "brand": "visa",
                "exp_month": 12,
                "exp_year": 2025,
                "is_default": True,
            }
        ]
    
    async def create_payment_method(
        self,
        user_id: UUID,
        payment_method_id: str,
        set_default: bool = False
    ) -> Dict[str, Any]:
        """Add a new payment method."""
        return {
            "id": payment_method_id,
            "user_id": str(user_id),
            "type": "card",
            "is_default": set_default,
        }
    
    async def delete_payment_method(
        self,
        user_id: UUID,
        payment_method_id: str
    ) -> Dict[str, Any]:
        """Delete a payment method."""
        return {"message": "Payment method deleted"}
    
    async def set_default_payment_method(
        self,
        user_id: UUID,
        payment_method_id: str
    ) -> Dict[str, Any]:
        """Set default payment method."""
        return {"message": "Default payment method updated"}
    
    async def get_usage(self, user_id: UUID) -> Dict[str, Any]:
        """Get usage statistics."""
        return {
            "videos_generated": 5,
            "videos_limit": 10,
            "storage_used_gb": 0.5,
            "storage_limit_gb": 5,
            "minutes_used": 12,
            "minutes_limit": 50,
        }