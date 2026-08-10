"""Global exception handlers for FastAPI."""

import logging
from typing import Dict, Any
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError

from app.core.errors import (
    AppError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ValidationError as AppValidationError,
    ConflictError,
    RateLimitError,
    ExternalServiceError,
)
from app.constants import ErrorCode
from app.logging import logger

# Module logger
log = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers."""
    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        """Handle HTTP exceptions."""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": ErrorCode.NOT_FOUND if exc.status_code == 404 else "HTTP_ERROR",
                    "message": exc.detail,
                    "status_code": exc.status_code,
                }
            },
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        """Handle request validation errors."""
        errors = []
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error["loc"])
            errors.append({
                "field": field,
                "message": error["msg"],
                "type": error["type"],
            })
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "code": ErrorCode.INVALID_INPUT,
                    "message": "Validation error",
                    "details": errors,
                }
            },
        )
    
    @app.exception_handler(AuthenticationError)
    async def auth_exception_handler(request: Request, exc: AuthenticationError) -> JSONResponse:
        """Handle authentication errors."""
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "error": {
                    "code": ErrorCode.INVALID_CREDENTIALS,
                    "message": str(exc),
                }
            },
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    @app.exception_handler(AuthorizationError)
    async def authz_exception_handler(request: Request, exc: AuthorizationError) -> JSONResponse:
        """Handle authorization errors."""
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "error": {
                    "code": ErrorCode.INSUFFICIENT_PERMISSIONS,
                    "message": str(exc),
                }
            },
        )
    
    @app.exception_handler(NotFoundError)
    async def not_found_exception_handler(request: Request, exc: NotFoundError) -> JSONResponse:
        """Handle not found errors."""
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error": {
                    "code": ErrorCode.NOT_FOUND,
                    "message": str(exc),
                }
            },
        )
    
    @app.exception_handler(AppValidationError)
    async def app_validation_exception_handler(request: Request, exc: AppValidationError) -> JSONResponse:
        """Handle application validation errors."""
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": {
                    "code": ErrorCode.INVALID_INPUT,
                    "message": str(exc),
                    "details": exc.details if hasattr(exc, "details") else None,
                }
            },
        )
    
    @app.exception_handler(ConflictError)
    async def conflict_exception_handler(request: Request, exc: ConflictError) -> JSONResponse:
        """Handle conflict errors."""
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "error": {
                    "code": ErrorCode.CONFLICT,
                    "message": str(exc),
                }
            },
        )
    
    @app.exception_handler(RateLimitError)
    async def rate_limit_exception_handler(request: Request, exc: RateLimitError) -> JSONResponse:
        """Handle rate limit errors."""
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": {
                    "code": ErrorCode.RATE_LIMIT_EXCEEDED,
                    "message": str(exc),
                }
            },
            headers={
                "Retry-After": str(exc.retry_after) if hasattr(exc, "retry_after") else "60",
            },
        )
    
    @app.exception_handler(ExternalServiceError)
    async def external_service_exception_handler(request: Request, exc: ExternalServiceError) -> JSONResponse:
        """Handle external service errors."""
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "error": {
                    "code": ErrorCode.AI_SERVICE_ERROR,
                    "message": str(exc),
                    "service": exc.service if hasattr(exc, "service") else "unknown",
                }
            },
        )
    
    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
        """Handle database errors."""
        log.error(f"Database error: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "DB_ERROR",
                    "message": "Database error occurred",
                }
            },
        )
    
    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Handle unhandled exceptions."""
        log.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred",
                }
            },
        )