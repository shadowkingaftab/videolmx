"""Main API router aggregation."""

from fastapi import APIRouter

from app.api.router import api_router

# Main router
router = APIRouter()

# Include all API routes
router.include_router(api_router)

# Export router
__all__ = ["router"]