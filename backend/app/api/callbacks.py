"""Webhook callbacks API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status, Request

from app.dependencies import get_current_user
from app.models.user import User
from app.services.webhook_client import WebhookClient
from app.schemas.callbacks import (
    WebhookRegistration,
    WebhookResponse,
    WebhookEvent,
    WebhookDelivery,
)
from app.core.errors import ValidationError

router = APIRouter()


@router.post("/webhooks/register", response_model=WebhookResponse)
async def register_webhook(
    request: WebhookRegistration,
    current_user: User = Depends(get_current_user),
    webhook_client: WebhookClient = Depends(WebhookClient),
):
    """Register a webhook endpoint."""
    try:
        webhook = await webhook_client.register_webhook(
            user_id=current_user.id,
            url=request.url,
            events=request.events,
            secret=request.secret,
        )
        return webhook
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/webhooks", response_model=list[WebhookResponse])
async def list_webhooks(
    current_user: User = Depends(get_current_user),
    webhook_client: WebhookClient = Depends(WebhookClient),
):
    """List user's webhooks."""
    webhooks = await webhook_client.list_webhooks(current_user.id)
    return webhooks


@router.delete("/webhooks/{webhook_id}")
async def delete_webhook(
    webhook_id: str,
    current_user: User = Depends(get_current_user),
    webhook_client: WebhookClient = Depends(WebhookClient),
):
    """Delete a webhook."""
    await webhook_client.delete_webhook(
        user_id=current_user.id,
        webhook_id=webhook_id,
    )
    return {"message": "Webhook deleted successfully"}


@router.post("/webhooks/{webhook_id}/test")
async def test_webhook(
    webhook_id: str,
    current_user: User = Depends(get_current_user),
    webhook_client: WebhookClient = Depends(WebhookClient),
):
    """Test a webhook."""
    result = await webhook_client.test_webhook(
        user_id=current_user.id,
        webhook_id=webhook_id,
    )
    return result


@router.get("/webhooks/{webhook_id}/deliveries")
async def list_webhook_deliveries(
    webhook_id: str,
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    webhook_client: WebhookClient = Depends(WebhookClient),
):
    """List webhook deliveries."""
    deliveries = await webhook_client.list_deliveries(
        user_id=current_user.id,
        webhook_id=webhook_id,
        page=page,
        page_size=page_size,
    )
    return deliveries


@router.post("/stripe/webhook")
async def stripe_webhook(
    request: Request,
    stripe_client = Depends(StripeClient),
):
    """Handle Stripe webhook events."""
    payload = await request.body()
    signature = request.headers.get("stripe-signature")
    
    try:
        event = await stripe_client.handle_webhook(
            payload=payload,
            signature=signature,
        )
        return {"status": "received"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )