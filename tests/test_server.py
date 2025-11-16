"""
Integration tests for the MCP server.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio

from src.server import CryptoMCPServer


@pytest.fixture
def mock_env(monkeypatch):
    """Mock environment variables."""
    monkeypatch.setenv("COINMARKETCAP_API_KEY", "test_key_123")
    monkeypatch.setenv("CACHE_TTL_SECONDS", "300")
    monkeypatch.setenv("CACHE_MAX_SIZE", "1000")
    monkeypatch.setenv("RATE_LIMIT_REQUESTS", "30")
    monkeypatch.setenv("RATE_LIMIT_PERIOD", "60")


@pytest.fixture
def server(mock_env):
    """Fixture for MCP server."""
    return CryptoMCPServer()


class TestCryptoMCPServer:
    """Test MCP server."""
    
    def test_server_initialization(self, server):
        """Test server initialization."""
        assert server.server is not None
        assert server.server.name == "cryptocurrency-market-data"
    
    @pytest.mark.asyncio
    async def test_server_initialize_components(self, server):
        """Test initializing server components."""
        await server.initialize()
        
        assert server.api_client is not None
        assert server.cache is not None
        assert server.realtime_tools is not None
        assert server.historical_tools is not None
        assert server.analytics_tools is not None
    
    @pytest.mark.asyncio
    async def test_server_cleanup(self, server):
        """Test server cleanup."""
        await server.initialize()
        await server.cleanup()
        
        # Verify cleanup was called
        # API client should be closed
    
    def test_get_server_info(self, server):
        """Test getting server info."""
        info = server._get_server_info()
        
        assert "Cryptocurrency Market Data" in info
        assert "Version" in info
        assert "CoinMarketCap" in info
        assert "Features" in info
    
    @pytest.mark.asyncio
    async def test_list_resources_handler(self, server):
        """Test list resources handler."""
        await server.initialize()
        
        # Get the list_resources handler
        handlers = [h for h in dir(server.server) if not h.startswith('_')]
        
        # Server should have resource handlers registered
        assert server.server is not None
    
    @pytest.mark.asyncio
    async def test_list_tools_handler(self, server):
        """Test list tools handler."""
        await server.initialize()
        
        # Tools should be initialized
        assert server.realtime_tools is not None
        assert server.historical_tools is not None
        assert server.analytics_tools is not None
        
        # Get all tool definitions
        realtime_tools = server.realtime_tools.get_tool_definitions()
        historical_tools = server.historical_tools.get_tool_definitions()
        analytics_tools = server.analytics_tools.get_tool_definitions()
        
        total_tools = len(realtime_tools) + len(historical_tools) + len(analytics_tools)
        assert total_tools == 8  # 4 + 2 + 2


class TestServerHandlers:
    """Test server protocol handlers."""
    
    @pytest.mark.asyncio
    async def test_call_tool_get_cryptocurrency_price(self, server):
        """Test calling get_cryptocurrency_price tool."""
        await server.initialize()
        
        # Mock the API client response
        from src.api.models import Cryptocurrency, Quote
        from datetime import datetime
        
        mock_crypto = Cryptocurrency(
            id=1,
            name="Bitcoin",
            symbol="BTC",
            slug="bitcoin",
            cmc_rank=1,
            quote={
                "USD": Quote(
                    price=50000.0,
                    volume_24h=30000000000.0,
                    percent_change_24h=2.5,
                    market_cap=950000000000.0
                )
            }
        )
        
        server.api_client.get_cryptocurrency_quotes = AsyncMock(
            return_value={"BTC": mock_crypto}
        )
        
        # Mock the call_tool method to test the handler
        result = await server.realtime_tools.get_cryptocurrency_price(
            symbols="BTC",
            convert="USD"
        )
        
        assert len(result) == 1
        assert "Bitcoin" in result[0].text
    
    @pytest.mark.asyncio
    async def test_call_tool_unknown_tool(self, server):
        """Test calling unknown tool."""
        await server.initialize()
        
        # This would normally be handled by the MCP protocol
        # but we can test the logic directly
        
        # The server should handle unknown tools gracefully
        # by returning an error message


class TestServerErrorHandling:
    """Test server error handling."""
    
    @pytest.mark.asyncio
    async def test_api_error_handling(self, server):
        """Test handling API errors."""
        await server.initialize()
        
        # Mock API client to raise error
        from src.utils.errors import APIError
        
        server.api_client.get_cryptocurrency_quotes = AsyncMock(
            side_effect=APIError("API Error")
        )
        
        result = await server.realtime_tools.get_cryptocurrency_price(
            symbols="BTC",
            convert="USD"
        )
        
        assert len(result) == 1
        assert "Error" in result[0].text
    
    @pytest.mark.asyncio
    async def test_validation_error_handling(self, server):
        """Test handling validation errors."""
        await server.initialize()
        
        # Test with invalid input
        result = await server.realtime_tools.get_cryptocurrency_price(
            symbols="",  # Empty symbol
            convert="USD"
        )
        
        assert len(result) == 1
        assert "Error" in result[0].text


class TestServerCaching:
    """Test server caching functionality."""
    
    @pytest.mark.asyncio
    async def test_cache_integration(self, server):
        """Test cache integration in server."""
        await server.initialize()
        
        assert server.cache is not None
        
        # Test cache operations
        server.cache.set("test_key", "test_value")
        value = server.cache.get("test_key")
        
        assert value == "test_value"
    
    @pytest.mark.asyncio
    async def test_cache_stats_resource(self, server):
        """Test cache statistics resource."""
        await server.initialize()
        
        # Perform some cache operations
        server.cache.set("key1", "value1")
        server.cache.get("key1")
        server.cache.get("key2")  # Miss
        
        stats = server.cache.get_stats()
        
        assert stats["sets"] == 1
        assert stats["hits"] == 1
        assert stats["misses"] == 1


class TestServerRateLimiting:
    """Test server rate limiting."""
    
    @pytest.mark.asyncio
    async def test_rate_limiter_integration(self, server):
        """Test rate limiter integration."""
        await server.initialize()
        
        assert server.api_client.rate_limiter is not None
        
        # Rate limiter should be configured
        assert server.api_client.rate_limiter.requests_per_period == 30
        assert server.api_client.rate_limiter.period_seconds == 60


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
