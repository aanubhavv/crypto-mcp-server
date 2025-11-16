"""
Unit tests for utility functions (errors, cache, validators).
"""

import pytest
import time
import asyncio
from datetime import datetime

from src.utils.errors import (
    APIError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    handle_api_error
)
from src.utils.cache import CryptoCache, RateLimiter, cached
from src.utils.validators import (
    validate_symbol,
    validate_symbols,
    validate_limit,
    validate_date,
    sanitize_parameters
)


class TestErrors:
    """Test error handling utilities."""
    
    def test_authentication_error(self):
        """Test authentication error."""
        error = AuthenticationError("Invalid API key")
        assert str(error) == "Invalid API key"
        assert isinstance(error, APIError)
    
    def test_rate_limit_error(self):
        """Test rate limit error."""
        error = RateLimitError("Rate limit exceeded", retry_after=60)
        assert error.retry_after == 60
        assert isinstance(error, APIError)
    
    def test_validation_error(self):
        """Test validation error."""
        error = ValidationError("Invalid data", errors=["Field required"])
        assert len(error.errors) == 1
        assert error.errors[0] == "Field required"
    
    def test_handle_api_error_401(self):
        """Test handling 401 error."""
        with pytest.raises(AuthenticationError):
            handle_api_error(401, {"status": {"error_message": "Invalid key"}})
    
    def test_handle_api_error_429(self):
        """Test handling 429 error."""
        with pytest.raises(RateLimitError):
            handle_api_error(429, {"status": {"error_message": "Rate limit"}})
    
    def test_handle_api_error_500(self):
        """Test handling 500 error."""
        with pytest.raises(APIError):
            handle_api_error(500, {"status": {"error_message": "Server error"}})


class TestCache:
    """Test caching functionality."""
    
    def test_cache_initialization(self):
        """Test cache initialization."""
        cache = CryptoCache(ttl_seconds=60, max_size=100)
        assert cache.ttl_seconds == 60
        assert cache.max_size == 100
    
    def test_cache_set_get(self):
        """Test basic cache operations."""
        cache = CryptoCache(ttl_seconds=60, max_size=100)
        
        cache.set("key1", "value1")
        value = cache.get("key1")
        
        assert value == "value1"
        assert cache._stats["sets"] == 1
        assert cache._stats["hits"] == 1
    
    def test_cache_miss(self):
        """Test cache miss."""
        cache = CryptoCache(ttl_seconds=60, max_size=100)
        
        value = cache.get("nonexistent")
        
        assert value is None
        assert cache._stats["misses"] == 1
    
    def test_cache_ttl_expiration(self):
        """Test TTL expiration."""
        cache = CryptoCache(ttl_seconds=1, max_size=100)
        
        cache.set("key1", "value1")
        time.sleep(1.1)
        value = cache.get("key1")
        
        assert value is None
    
    def test_cache_clear(self):
        """Test cache clearing."""
        cache = CryptoCache(ttl_seconds=60, max_size=100)
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.clear()
        
        assert cache.get("key1") is None
        assert cache.get("key2") is None
    
    def test_cache_stats(self):
        """Test cache statistics."""
        cache = CryptoCache(ttl_seconds=60, max_size=100)
        
        cache.set("key1", "value1")
        cache.get("key1")
        cache.get("key2")
        
        stats = cache.get_stats()
        
        assert stats["sets"] == 1
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["total_requests"] == 2
        assert stats["hit_rate"] == 50.0
    
    def test_cache_invalidate_pattern(self):
        """Test pattern-based invalidation."""
        cache = CryptoCache(ttl_seconds=60, max_size=100)
        
        cache.set("price:BTC", "50000")
        cache.set("price:ETH", "3000")
        cache.set("info:BTC", "Bitcoin")
        
        invalidated = cache.invalidate_pattern("price:")
        
        assert invalidated == 2
        assert cache.get("price:BTC") is None
        assert cache.get("info:BTC") == "Bitcoin"
    
    def test_generate_key(self):
        """Test cache key generation."""
        cache = CryptoCache()
        
        key1 = cache._generate_key("test", symbol="BTC", convert="USD")
        key2 = cache._generate_key("test", convert="USD", symbol="BTC")
        
        # Keys should be same regardless of parameter order
        assert key1 == key2
    
    @pytest.mark.asyncio
    async def test_cached_decorator_async(self):
        """Test async cached decorator."""
        cache = CryptoCache(ttl_seconds=60, max_size=100)
        call_count = 0
        
        @cached(cache, "test_func")
        async def expensive_function(x: int) -> int:
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.01)
            return x * 2
        
        result1 = await expensive_function(5)
        result2 = await expensive_function(5)
        result3 = await expensive_function(10)
        
        assert result1 == 10
        assert result2 == 10
        assert result3 == 20
        assert call_count == 2  # Should only call twice (once for 5, once for 10)


class TestRateLimiter:
    """Test rate limiting functionality."""
    
    def test_rate_limiter_initialization(self):
        """Test rate limiter initialization."""
        limiter = RateLimiter(requests_per_period=10, period_seconds=60)
        assert limiter.requests_per_period == 10
        assert limiter.period_seconds == 60
        assert limiter.tokens == 10
    
    def test_rate_limiter_acquire(self):
        """Test token acquisition."""
        limiter = RateLimiter(requests_per_period=5, period_seconds=60)
        
        # Should successfully acquire 3 tokens
        assert limiter.acquire(3) is True
        assert limiter.tokens == 2
        
        # Should successfully acquire 2 more
        assert limiter.acquire(2) is True
        assert limiter.tokens == 0
        
        # Should fail to acquire more
        assert limiter.acquire(1) is False
    
    def test_rate_limiter_refill(self):
        """Test token refilling."""
        limiter = RateLimiter(requests_per_period=10, period_seconds=1)
        
        # Consume all tokens
        limiter.acquire(10)
        assert limiter.tokens == 0
        
        # Wait for refill
        time.sleep(0.5)
        limiter._refill_tokens()
        
        # Should have some tokens back
        assert limiter.tokens > 0
    
    @pytest.mark.asyncio
    async def test_rate_limiter_wait(self):
        """Test waiting for tokens."""
        limiter = RateLimiter(requests_per_period=5, period_seconds=1)
        
        # Consume all tokens
        limiter.acquire(5)
        
        # Wait should succeed after tokens refill
        start = time.time()
        await limiter.wait_for_token(1)
        elapsed = time.time() - start
        
        # Should have waited at least a small amount
        assert elapsed > 0


class TestValidators:
    """Test validation utilities."""
    
    def test_validate_symbol_valid(self):
        """Test valid symbol validation."""
        assert validate_symbol("BTC") == "BTC"
        assert validate_symbol("eth") == "ETH"
        assert validate_symbol(" ada ") == "ADA"
    
    def test_validate_symbol_invalid(self):
        """Test invalid symbol validation."""
        with pytest.raises(ValueError):
            validate_symbol("")
        
        with pytest.raises(ValueError):
            validate_symbol("BTC$")
        
        with pytest.raises(ValueError):
            validate_symbol("TOOLONGSYMBOL")
    
    def test_validate_symbols_string(self):
        """Test multiple symbols from string."""
        symbols = validate_symbols("BTC,ETH,ADA")
        assert symbols == ["BTC", "ETH", "ADA"]
    
    def test_validate_symbols_list(self):
        """Test multiple symbols from list."""
        symbols = validate_symbols(["btc", "eth", "ada"])
        assert symbols == ["BTC", "ETH", "ADA"]
    
    def test_validate_limit_valid(self):
        """Test valid limit validation."""
        assert validate_limit(100) == 100
        assert validate_limit(1, min_val=1, max_val=1000) == 1
        assert validate_limit(1000, min_val=1, max_val=1000) == 1000
    
    def test_validate_limit_invalid(self):
        """Test invalid limit validation."""
        with pytest.raises(ValueError):
            validate_limit(0, min_val=1, max_val=100)
        
        with pytest.raises(ValueError):
            validate_limit(101, min_val=1, max_val=100)
    
    def test_validate_date_valid(self):
        """Test valid date validation."""
        date1 = validate_date("2024-01-01")
        assert isinstance(date1, datetime)
        
        date2 = validate_date("2024-01-01T12:00:00")
        assert isinstance(date2, datetime)
    
    def test_validate_date_invalid(self):
        """Test invalid date validation."""
        with pytest.raises(ValueError):
            validate_date("invalid-date")
        
        with pytest.raises(ValueError):
            validate_date("2024-13-01")
    
    def test_sanitize_parameters(self):
        """Test parameter sanitization."""
        params = {
            "symbol": "BTC",
            "limit": 100,
            "start": None,
            "convert": "USD",
            "end": None
        }
        
        sanitized = sanitize_parameters(params)
        
        assert "symbol" in sanitized
        assert "limit" in sanitized
        assert "convert" in sanitized
        assert "start" not in sanitized
        assert "end" not in sanitized


class TestCachedDecorator:
    """Test cached decorator functionality."""
    
    def test_cached_decorator_sync(self):
        """Test sync cached decorator."""
        cache = CryptoCache(ttl_seconds=60, max_size=100)
        call_count = 0
        
        @cached(cache, "sync_func")
        def sync_function(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x * 2
        
        result1 = sync_function(5)
        result2 = sync_function(5)
        result3 = sync_function(10)
        
        assert result1 == 10
        assert result2 == 10
        assert result3 == 20
        assert call_count == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
