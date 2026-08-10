"""API router aggregation."""

from fastapi import APIRouter

from app.api import (
    auth,
    users,
    projects,
    websites,
    crawl_jobs,
    analysis_jobs,
    storyboards,
    scripts,
    narration,
    assets,
    videos,
    exports,
    billing,
    admin,
    settings as settings_api,
    callbacks,
    websocket,
)

# Create main API router
api_router = APIRouter()

# Include routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
api_router.include_router(websites.router, prefix="/websites", tags=["Websites"])
api_router.include_router(crawl_jobs.router, prefix="/crawl-jobs", tags=["Crawl Jobs"])
api_router.include_router(analysis_jobs.router, prefix="/analysis-jobs", tags=["Analysis Jobs"])
api_router.include_router(storyboards.router, prefix="/storyboards", tags=["Storyboards"])
api_router.include_router(scripts.router, prefix="/scripts", tags=["Scripts"])
api_router.include_router(narration.router, prefix="/narration", tags=["Narration"])
api_router.include_router(assets.router, prefix="/assets", tags=["Assets"])
api_router.include_router(videos.router, prefix="/videos", tags=["Videos"])
api_router.include_router(exports.router, prefix="/exports", tags=["Exports"])
api_router.include_router(billing.router, prefix="/billing", tags=["Billing"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
api_router.include_router(settings_api.router, prefix="/settings", tags=["Settings"])
api_router.include_router(callbacks.router, prefix="/callbacks", tags=["Callbacks"])
api_router.include_router(websocket.router, prefix="/ws", tags=["WebSocket"])