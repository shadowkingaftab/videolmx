"""Rate limiting implementation."""

import time
from typing import Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

from app.core.cache import get_cache
from app.config import settings
from app.core.errors import RateLimitError


@dataclass
class RateLimitInfo:
    """Rate limit information."""
    limit: int
    remaining: int
    reset: int
    retry_after: Optional[int] = None


class RateLimiter:
    """Rate limiter using token bucket algorithm."""
    
    def __init__(
        self,
        key_prefix: str = "rate_limit",
        requests_per_minute: int = 60,
        burst: int = 120,
    ):
        self.key_prefix = key_prefix
        self.requests_per_minute = requests_per_minute
        self.burst = burst
        self.cache = None
    
    async def _get_cache(self):
        """Get cache client."""
        if self.cache is None:
            self.cache = await get_cache()
        return self.cache
    
    async def check_rate_limit(
        self,
        key: str,
        limit: Optional[int] = None,
        window_seconds: int = 60,
    ) -> RateLimitInfo:
        """Check if request is within rate limit."""
        cache_key = f"{self.key_prefix}:{key}"
        cache = await self._get_cache()
        
        # Get current count
        current = await cache.get(cache_key)
        if current is None:
            # First request, set count to 1 with TTL
            await cache.setex(cache_key, window_seconds, 1)
            remaining = (limit or self.requests_per_minute) - 1
            return RateLimitInfo(
                limit=limit or self.requests_per_minute,
                remaining=remaining,
                reset=int(time.time()) + window_seconds,
            )
        
        # Increment count
        count = await cache.incr(cache_key)
        limit_value = limit or self.requests_per_minute
        
        if count > limit_value:
            # Rate limit exceeded
            ttl = await cache.ttl(cache_key)
            return RateLimitInfo(
                limit=limit_value,
                remaining=0,
                reset=int(time.time()) + ttl,
                retry_after=ttl,
            )
        
        return RateLimitInfo(
            limit=limit_value,
            remaining=limit_value - count,
            reset=int(time.time()) + await cache.ttl(cache_key),
        )
    
    async def check_limit(
        self,
        key: str,
        limit: int,
        window_seconds: int,
    ) -> Tuple[bool, RateLimitInfo]:
        """Check if request is allowed."""
        info = await self.check_rate_limit(key, limit, window_seconds)
        if info.remaining < 0:
            raise RateLimitError(
                f"Rate limit exceeded. Retry after {info.retry_after} seconds",
                retry_after=info.retry_after or 60,
            )
        return True, info


class UserRateLimiter(RateLimiter):
    """User-specific rate limiter."""
    
    async def check_user_limit(
        self,
        user_id: str,
        limit: Optional[int] = None,
    ) -> RateLimitInfo:
        """Check rate limit for a specific user."""
        return await self.check_rate_limit(
            f"user:{user_id}",
            limit or settings.RATE_LIMIT_REQUESTS_PER_MINUTE,
        )


class IPRateLimiter(RateLimiter):
    """IP-based rate limiter."""
    
    async def check_ip_limit(
        self,
        ip: str,
        limit: Optional[int] = None,
    ) -> RateLimitInfo:
        """Check rate limit for a specific IP."""
        return await self.check_rate_limit(
            f"ip:{ip}",
            limit or settings.RATE_LIMIT_REQUESTS_PER_MINUTE * 2,
        )


class EndpointRateLimiter(RateLimiter):
    """Endpoint-specific rate limiter."""
    
    async def check_endpoint_limit(
        self,
        endpoint: str,
        method: str,
        limit: Optional[int] = None,
    ) -> RateLimitInfo:
        """Check rate limit for a specific endpoint."""
        return await self.check_rate_limit(
            f"endpoint:{method}:{endpoint}",
            limit or settings.RATE_LIMIT_REQUESTS_PER_MINUTE,
        )


class SlidingWindowRateLimiter:
    """Sliding window rate limiter using Redis sorted sets."""
    
    def __init__(self, key_prefix: str = "sliding_rate_limit"):
        self.key_prefix = key_prefix
        self.cache = None
    
    async def _get_cache(self):
        """Get cache client."""
        if self.cache is None:
            self.cache = await get_cache()
        return self.cache
    
    async def check_rate_limit(
        self,
        key: str,
        limit: int,
        window_seconds: int,
    ) -> Tuple[bool, RateLimitInfo]:
        """Check rate limit using sliding window."""
        cache = await self._get_cache()
        cache_key = f"{self.key_prefix}:{key}"
        
        # Get current timestamp
        now = time.time()
        window_start = now - window_seconds
        
        # Remove old entries
        await cache.zremrangebyscore(cache_key, 0, window_start)
        
        # Count requests in window
        count = await cache.zcard(cache_key)
        
        if count >= limit:
            # Get oldest entry for retry_after
            oldest = await cache.zrange(cache_key, 0, 0, withscores=True)
            if oldest:
                retry_after = int(oldest[0][1] + window_seconds - now)
            else:
                retry_after = window_seconds
            
            return False, RateLimitInfo(
                limit=limit,
                remaining=0,
                reset=int(now) + retry_after,
                retry_after=retry_after,
            )
        
        # Add current request
        member = f"{now}:{id(self)}"
        await cache.zadd(cache_key, {member: now})
        await cache.expire(cache_key, window_seconds)
        
        remaining = limit - count - 1
        
        return True, RateLimitInfo(
            limit=limit,
            remaining=remaining,
            reset=int(now) + window_seconds,
        )


# Global instances
rate_limiter = RateLimiter()
user_rate_limiter = UserRateLimiter()
ip_rate_limiter = IPRateLimiter()
endpoint_rate_limiter = EndpointRateLimiter()
sliding_rate_limiter = SlidingWindowRateLimiter()