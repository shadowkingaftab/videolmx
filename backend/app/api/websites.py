"""Website management API endpoints."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.dependencies import (
    get_current_user,
    get_website_service,
    get_current_website,
)
from app.models.user import User
from app.models.website import Website
from app.services.website_service import WebsiteService
from app.schemas.website import (
    WebsiteCreate,
    WebsiteUpdate,
    WebsiteResponse,
    WebsiteListResponse,
    WebsiteAnalyzeRequest,
)
from app.schemas.common import PaginatedResponse
from app.core.errors import NotFoundError, ValidationError

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[WebsiteListResponse])
async def list_websites(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    project_id: Optional[UUID] = None,
    current_user: User = Depends(get_current_user),
    website_service: WebsiteService = Depends(get_website_service),
):
    """List websites for the current user."""
    skip = (page - 1) * page_size
    
    websites, total = await website_service.list_websites(
        user_id=current_user.id,
        project_id=project_id,
        skip=skip,
        limit=page_size,
    )
    
    return PaginatedResponse(
        items=websites,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.post("/", response_model=WebsiteResponse, status_code=status.HTTP_201_CREATED)
async def create_website(
    request: WebsiteCreate,
    current_user: User = Depends(get_current_user),
    website_service: WebsiteService = Depends(get_website_service),
):
    """Add a website to a project."""
    try:
        website = await website_service.create_website(
            project_id=request.project_id,
            url=request.url,
            user_id=current_user.id,
        )
        return website
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/{website_id}", response_model=WebsiteResponse)
async def get_website(
    website: Website = Depends(get_current_website),
):
    """Get website by ID."""
    return website


@router.patch("/{website_id}", response_model=WebsiteResponse)
async def update_website(
    request: WebsiteUpdate,
    website: Website = Depends(get_current_website),
    website_service: WebsiteService = Depends(get_website_service),
):
    """Update website."""
    updated = await website_service.update_website(
        website_id=website.id,
        updates=request.dict(exclude_unset=True),
    )
    return updated


@router.delete("/{website_id}")
async def delete_website(
    website: Website = Depends(get_current_website),
    website_service: WebsiteService = Depends(get_website_service),
):
    """Delete website."""
    await website_service.delete_website(website.id)
    return {"message": "Website deleted successfully"}


@router.post("/{website_id}/analyze")
async def analyze_website(
    request: WebsiteAnalyzeRequest,
    website: Website = Depends(get_current_website),
    website_service: WebsiteService = Depends(get_website_service),
):
    """Analyze website content."""
    job_id = await website_service.analyze_website(
        website_id=website.id,
        max_pages=request.max_pages,
        depth=request.depth,
        include_assets=request.include_assets,
    )
    return {
        "message": "Analysis started",
        "job_id": job_id,
        "website_id": website.id,
    }


@router.get("/{website_id}/analyze/status")
async def get_analysis_status(
    website: Website = Depends(get_current_website),
    website_service: WebsiteService = Depends(get_website_service),
):
    """Get website analysis status."""
    status = await website_service.get_analysis_status(website.id)
    return status


@router.get("/{website_id}/pages")
async def list_website_pages(
    website: Website = Depends(get_current_website),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    website_service: WebsiteService = Depends(get_website_service),
):
    """List pages crawled from a website."""
    skip = (page - 1) * page_size
    pages, total = await website_service.list_pages(
        website_id=website.id,
        skip=skip,
        limit=page_size,
    )
    
    return {
        "items": pages,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size,
    }


@router.get("/{website_id}/assets")
async def list_website_assets(
    website: Website = Depends(get_current_website),
    asset_type: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    website_service: WebsiteService = Depends(get_website_service),
):
    """List assets extracted from a website."""
    skip = (page - 1) * page_size
    assets, total = await website_service.list_assets(
        website_id=website.id,
        asset_type=asset_type,
        skip=skip,
        limit=page_size,
    )
    
    return {
        "items": assets,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size,
    }


@router.get("/{website_id}/digital-twin")
async def get_digital_twin(
    website: Website = Depends(get_current_website),
    website_service: WebsiteService = Depends(get_website_service),
):
    """Get website digital twin."""
    twin = await website_service.get_digital_twin(website.id)
    if not twin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Digital twin not found. Please analyze the website first.",
        )
    return twin