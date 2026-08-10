"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.config import settings
from app.lifecycle import lifespan
from app.logging import setup_logging
from app.observability import setup_observability
from app.router import api_router
from app.exception_handlers import register_exception_handlers
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.audit import AuditMiddleware
from app.middleware.compression import CompressionMiddleware
from app.middleware.timeout import TimeoutMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.middleware.cors import cors_options

# Setup logging
setup_logging()

# Setup observability
setup_observability()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan handler."""
    # Startup
    await lifespan.startup(app)
    yield
    # Shutdown
    await lifespan.shutdown(app)


# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    docs_url=settings.DOCS_URL,
    redoc_url=settings.REDOC_URL,
    openapi_url=settings.OPENAPI_URL,
    lifespan=lifespan,
    debug=settings.DEBUG,
)

# Register exception handlers
register_exception_handlers(app)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Processing-Time"],
)

app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(AuditMiddleware)
app.add_middleware(CompressionMiddleware)
app.add_middleware(TimeoutMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

# Include routers
app.include_router(api_router, prefix=settings.API_V1_STR)

# Health check endpoints
@app.get("/health")
async def health_check():
    """Basic health check."""
    return {"status": "healthy", "version": settings.VERSION}

@app.get("/health/ready")
async def readiness_check():
    """Readiness check."""
    return {"status": "ready"}

@app.get("/health/live")
async def liveness_check():
    """Liveness check."""
    return {"status": "alive"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )