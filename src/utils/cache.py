"""
Caching utilities for the cryptocurrency MCP server.
"""

import time
import hashlib
import json
from typing import Any, Optional, Dict, Callable
from functools import wraps
from datetime import datetime, timedelta
from cachetools import TTLCache, LRUCache
import logging

logger = logging.getLogger(__name__)


class CryptoCache:
    """
    Advanced caching system with TTL and LRU eviction.
    """
    
    def __init__(self, ttl_seconds: int = 300, max_size: int = 1000):
        """
        Initialize cache.
        
        Args:
            ttl_seconds: Time-to-live for cache entries in seconds
            max_size: Maximum number of entries in cache
        """
        self.ttl_seconds = ttl_seconds
        self.max_size = max_size
        self._cache: TTLCache = TTLCache(maxsize=max_size, ttl=ttl_seconds)
        self._stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "evictions": 0
        }
        logger.info(f"Initialized cache with TTL={ttl_seconds}s, max_size={max_size}")
    
    def _generate_key(self, prefix: str, **kwargs) -> str:
        """
        Generate cache key from prefix and arguments.
        
        Args:
            prefix: Key prefix
            **kwargs: Key components
            
        Returns:
            Cache key string
        """
        # Sort kwargs for consistent key generation
        sorted_items = sorted(kwargs.items())
        key_data = json.dumps(sorted_items, sort_keys=True)
        key_hash = hashlib.md5(key_data.encode()).hexdigest()
        return f"{prefix}:{key_hash}"
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        try:
            value = self._cache.get(key)
            if value is not None:
                self._stats["hits"] += 1
                logger.debug(f"Cache hit: {key}")
                return value
            else:
                self._stats["misses"] += 1
                logger.debug(f"Cache miss: {key}")
                return None
        except KeyError:
            self._stats["misses"] += 1
            return None
    
    def set(self, key: str, value: Any) -> None:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        try:
            self._cache[key] = value
            self._stats["sets"] += 1
            logger.debug(f"Cache set: {key}")
        except Exception as e:
            logger.error(f"Failed to set cache key {key}: {e}")
    
    def delete(self, key: str) -> None:
        """
        Delete value from cache.
        
        Args:
            key: Cache key
        """
        try:
            del self._cache[key]
            logger.debug(f"Cache delete: {key}")
        except KeyError:
            pass
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
        logger.info("Cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        total_requests = self._stats["hits"] + self._stats["misses"]
        hit_rate = (self._stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            **self._stats,
            "size": len(self._cache),
            "max_size": self.max_size,
            "hit_rate": round(hit_rate, 2),
            "total_requests": total_requests
        }
    
    def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate all cache keys matching pattern.
        
        Args:
            pattern: Pattern to match (simple prefix match)
            
        Returns:
            Number of keys invalidated
        """
        keys_to_delete = [key for key in self._cache.keys() if key.startswith(pattern)]
        for key in keys_to_delete:
            del self._cache[key]
        logger.info(f"Invalidated {len(keys_to_delete)} keys matching pattern: {pattern}")
        return len(keys_to_delete)


def cached(cache: CryptoCache, key_prefix: str, ttl: Optional[int] = None):
    """
    Decorator for caching function results.
    
    Args:
        cache: Cache instance
        key_prefix: Prefix for cache keys
        ttl: Optional TTL override for this function
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Generate cache key from function arguments
            cache_key = cache._generate_key(
                key_prefix,
                args=args,
                kwargs=kwargs
            )
            
            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Call function and cache result
            result = await func(*args, **kwargs)
            cache.set(cache_key, result)
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Generate cache key from function arguments
            cache_key = cache._generate_key(
                key_prefix,
                args=args,
                kwargs=kwargs
            )
            
            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Call function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result)
            return result
        
        # Return appropriate wrapper based on function type
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


class RateLimiter:
    """
    Token bucket rate limiter for API requests.
    """
    
    def __init__(self, requests_per_period: int = 30, period_seconds: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_period: Number of requests allowed per period
            period_seconds: Period duration in seconds
        """
        self.requests_per_period = requests_per_period
        self.period_seconds = period_seconds
        self.tokens = requests_per_period
        self.last_update = time.time()
        logger.info(f"Initialized rate limiter: {requests_per_period} requests per {period_seconds}s")
    
    def _refill_tokens(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_update
        
        # Calculate tokens to add
        tokens_to_add = (elapsed / self.period_seconds) * self.requests_per_period
        self.tokens = min(self.requests_per_period, self.tokens + tokens_to_add)
        self.last_update = now
    
    def acquire(self, tokens: int = 1) -> bool:
        """
        Try to acquire tokens.
        
        Args:
            tokens: Number of tokens to acquire
            
        Returns:
            True if tokens acquired, False otherwise
        """
        self._refill_tokens()
        
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False
    
    async def wait_for_token(self, tokens: int = 1) -> None:
        """
        Wait until tokens are available.
        
        Args:
            tokens: Number of tokens needed
        """
        import asyncio
        
        while not self.acquire(tokens):
            # Wait a bit before retrying
            wait_time = (tokens - self.tokens) / self.requests_per_period * self.period_seconds
            await asyncio.sleep(max(0.1, wait_time))
    
    def get_wait_time(self) -> float:
        """
        Get estimated wait time for next token.
        
        Returns:
            Wait time in seconds
        """
        if self.tokens >= 1:
            return 0.0
        
        tokens_needed = 1 - self.tokens
        return (tokens_needed / self.requests_per_period) * self.period_seconds
