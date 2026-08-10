"""Observability setup - metrics, tracing, monitoring."""

import time
import functools
from typing import Dict, Any, Optional, Callable
from contextlib import contextmanager
from datetime import datetime

from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    Summary,
    generate_latest,
    CONTENT_TYPE_LATEST,
)

from app.config import settings
from app.logging import logger

# Metrics
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10]
)

ACTIVE_REQUESTS = Gauge(
    "http_active_requests",
    "Active HTTP requests",
    ["method"]
)

JOB_COUNT = Counter(
    "jobs_total",
    "Total jobs processed",
    ["type", "status"]
)

JOB_DURATION = Histogram(
    "job_duration_seconds",
    "Job processing duration in seconds",
    ["type"],
    buckets=[1, 5, 10, 30, 60, 120, 300, 600]
)

CRAWL_COUNT = Counter(
    "crawls_total",
    "Total website crawls",
    ["status"]
)

VIDEO_COUNT = Counter(
    "videos_total",
    "Total videos generated",
    ["status"]
)

VOICE_GENERATION_COUNT = Counter(
    "voice_generations_total",
    "Total voice generations",
    ["voice"]
)

RENDER_DURATION = Histogram(
    "render_duration_seconds",
    "Video render duration in seconds",
    ["resolution", "fps"],
    buckets=[10, 30, 60, 120, 300, 600, 1800]
)

CACHE_HITS = Counter(
    "cache_hits_total",
    "Total cache hits",
    ["cache_type"]
)

CACHE_MISSES = Counter(
    "cache_misses_total",
    "Total cache misses",
    ["cache_type"]
)

DATABASE_QUERY_DURATION = Histogram(
    "db_query_duration_seconds",
    "Database query duration in seconds",
    ["operation"],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1]
)

EXTERNAL_API_CALLS = Counter(
    "external_api_calls_total",
    "External API calls",
    ["service", "status"]
)

EXTERNAL_API_DURATION = Histogram(
    "external_api_duration_seconds",
    "External API call duration in seconds",
    ["service"],
    buckets=[0.1, 0.5, 1, 2, 5, 10, 30, 60]
)


def setup_observability():
    """Setup observability."""
    if settings.SENTRY_DSN:
        try:
            import sentry_sdk
            from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
            from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
            
            sentry_sdk.init(
                dsn=settings.SENTRY_DSN,
                environment=settings.ENVIRONMENT,
                release=settings.VERSION,
                integrations=[SqlalchemyIntegration()],
                traces_sample_rate=0.1 if settings.ENVIRONMENT == "production" else 1.0,
            )
            logger.info("Sentry initialized")
        except ImportError:
            logger.warning("Sentry SDK not installed")
    
    if settings.PROMETHEUS_ENABLED:
        try:
            from prometheus_client import start_http_server
            start_http_server(settings.PROMETHEUS_PORT)
            logger.info(f"Prometheus metrics server started on port {settings.PROMETHEUS_PORT}")
        except Exception as e:
            logger.warning(f"Failed to start Prometheus server: {e}")


def track_request(method: str, endpoint: str):
    """Decorator to track HTTP requests."""
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            ACTIVE_REQUESTS.labels(method=method).inc()
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                status = getattr(result, "status_code", 200) if result else 200
                REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=str(status)).inc()
                return result
            except Exception as e:
                REQUEST_COUNT.labels(method=method, endpoint=endpoint, status="500").inc()
                raise
            finally:
                duration = time.time() - start_time
                REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)
                ACTIVE_REQUESTS.labels(method=method).dec()
        
        return wrapper
    return decorator


def track_job(job_type: str):
    """Decorator to track jobs."""
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                JOB_COUNT.labels(type=job_type, status="success").inc()
                return result
            except Exception:
                JOB_COUNT.labels(type=job_type, status="failed").inc()
                raise
            finally:
                duration = time.time() - start_time
                JOB_DURATION.labels(type=job_type).observe(duration)
        
        return wrapper
    return decorator


def track_external_api(service: str):
    """Decorator to track external API calls."""
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                EXTERNAL_API_CALLS.labels(service=service, status="success").inc()
                return result
            except Exception:
                EXTERNAL_API_CALLS.labels(service=service, status="failed").inc()
                raise
            finally:
                duration = time.time() - start_time
                EXTERNAL_API_DURATION.labels(service=service).observe(duration)
        
        return wrapper
    return decorator


@contextmanager
def track_db_query(operation: str):
    """Context manager to track database queries."""
    start_time = time.time()
    try:
        yield
    finally:
        duration = time.time() - start_time
        DATABASE_QUERY_DURATION.labels(operation=operation).observe(duration)


def track_cache_operation(cache_type: str):
    """Decorator to track cache operations."""
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            if result is not None:
                CACHE_HITS.labels(cache_type=cache_type).inc()
            else:
                CACHE_MISSES.labels(cache_type=cache_type).inc()
            return result
        
        return wrapper
    return decorator


async def get_metrics() -> Dict[str, Any]:
    """Get current metrics."""
    return {
        "http_requests_total": REQUEST_COUNT._value.get(),
        "active_requests": ACTIVE_REQUESTS._value.get(),
        "jobs_total": JOB_COUNT._value.get(),
        "cache_hits": CACHE_HITS._value.get(),
        "cache_misses": CACHE_MISSES._value.get(),
    }


async def get_metrics_prometheus() -> bytes:
    """Get Prometheus metrics."""
    return generate_latest()