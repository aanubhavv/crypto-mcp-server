"""
Unit tests for MCP tools (realtime, historical, analytics).
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.tools.realtime import RealtimeTools
from src.tools.historical import HistoricalTools
from src.tools.analytics import AnalyticsTools
from src.api.client import CoinMarketCapClient
from src.api.models import Cryptocurrency, GlobalMetrics, Quote
from src.utils.cache import CryptoCache


@pytest.fixture
def mock_api_client():
    """Fixture for mock API client."""
    client = AsyncMock(spec=CoinMarketCapClient)
    return client


@pytest.fixture
def cache():
    """Fixture for cache."""
    return CryptoCache(ttl_seconds=60, max_size=100)


@pytest.fixture
def realtime_tools(mock_api_client, cache):
    """Fixture for realtime tools."""
    return RealtimeTools(mock_api_client, cache)


@pytest.fixture
def historical_tools(mock_api_client, cache):
    """Fixture for historical tools."""
    return HistoricalTools(mock_api_client, cache)


@pytest.fixture
def analytics_tools(mock_api_client, cache):
    """Fixture for analytics tools."""
    return AnalyticsTools(mock_api_client, cache)


@pytest.fixture
def mock_cryptocurrency():
    """Fixture for mock cryptocurrency."""
    from datetime import datetime
    
    return Cryptocurrency(
        id=1,
        name="Bitcoin",
        symbol="BTC",
        slug="bitcoin",
        cmc_rank=1,
        circulating_supply=19000000,
        total_supply=21000000,
        max_supply=21000000,
        last_updated=datetime.now(),
        quote={
            "USD": Quote(
                price=50000.0,
                volume_24h=30000000000.0,
                percent_change_24h=2.5,
                percent_change_7d=5.0,
                market_cap=950000000000.0
            )
        }
    )


class TestRealtimeTools:
    """Test realtime tools."""
    
    def test_get_tool_definitions(self, realtime_tools):
        """Test getting tool definitions."""
        tools = realtime_tools.get_tool_definitions()
        
        assert len(tools) == 4
        tool_names = [tool.name for tool in tools]
        assert "get_cryptocurrency_price" in tool_names
        assert "get_cryptocurrency_info" in tool_names
        assert "get_top_cryptocurrencies" in tool_names
        assert "get_global_metrics" in tool_names
    
    @pytest.mark.asyncio
    async def test_get_cryptocurrency_price_success(
        self, realtime_tools, mock_api_client, mock_cryptocurrency
    ):
        """Test getting cryptocurrency price."""
        mock_api_client.get_cryptocurrency_quotes.return_value = {
            "BTC": mock_cryptocurrency
        }
        
        result = await realtime_tools.get_cryptocurrency_price(
            symbols="BTC",
            convert="USD"
        )
        
        assert len(result) == 1
        assert "Bitcoin" in result[0].text
        assert "50,000.00" in result[0].text
        assert "+2.50%" in result[0].text or "2.50%" in result[0].text
        
        # Verify API was called
        mock_api_client.get_cryptocurrency_quotes.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_cryptocurrency_price_cached(
        self, realtime_tools, mock_api_client, mock_cryptocurrency, cache
    ):
        """Test cached cryptocurrency price."""
        mock_api_client.get_cryptocurrency_quotes.return_value = {
            "BTC": mock_cryptocurrency
        }
        
        # First call - should hit API
        result1 = await realtime_tools.get_cryptocurrency_price(
            symbols="BTC",
            convert="USD"
        )
        
        # Second call - should use cache
        result2 = await realtime_tools.get_cryptocurrency_price(
            symbols="BTC",
            convert="USD"
        )
        
        # API should only be called once
        assert mock_api_client.get_cryptocurrency_quotes.call_count == 1
        
        # Results should be identical
        assert result1[0].text == result2[0].text
    
    @pytest.mark.asyncio
    async def test_get_cryptocurrency_price_error(
        self, realtime_tools, mock_api_client
    ):
        """Test error handling in get_cryptocurrency_price."""
        mock_api_client.get_cryptocurrency_quotes.side_effect = Exception("API Error")
        
        result = await realtime_tools.get_cryptocurrency_price(
            symbols="INVALID",
            convert="USD"
        )
        
        assert len(result) == 1
        assert "Error" in result[0].text
    
    @pytest.mark.asyncio
    async def test_get_top_cryptocurrencies(
        self, realtime_tools, mock_api_client, mock_cryptocurrency
    ):
        """Test getting top cryptocurrencies."""
        mock_api_client.get_cryptocurrency_listings.return_value = [
            mock_cryptocurrency
        ]
        
        result = await realtime_tools.get_top_cryptocurrencies(
            limit=10,
            convert="USD"
        )
        
        assert len(result) == 1
        assert "Top 10" in result[0].text or "Top" in result[0].text
        assert "BTC" in result[0].text
        
        # Verify API was called with correct params
        call_args = mock_api_client.get_cryptocurrency_listings.call_args
        assert call_args[1]["limit"] == 10
        assert call_args[1]["convert"] == "USD"
    
    @pytest.mark.asyncio
    async def test_get_global_metrics(
        self, realtime_tools, mock_api_client
    ):
        """Test getting global metrics."""
        from datetime import datetime
        
        mock_metrics = GlobalMetrics(
            active_cryptocurrencies=10000,
            total_cryptocurrencies=20000,
            active_market_pairs=50000,
            active_exchanges=500,
            total_exchanges=1000,
            eth_dominance=18.5,
            btc_dominance=45.0,
            quote={
                "USD": {
                    "total_market_cap": 2000000000000.0,
                    "total_volume_24h": 100000000000.0
                }
            },
            last_updated=datetime.now()
        )
        
        mock_api_client.get_global_metrics.return_value = mock_metrics
        
        result = await realtime_tools.get_global_metrics(convert="USD")
        
        assert len(result) == 1
        assert "10,000" in result[0].text
        assert "45.00%" in result[0].text
        assert "18.50%" in result[0].text


class TestHistoricalTools:
    """Test historical tools."""
    
    def test_get_tool_definitions(self, historical_tools):
        """Test getting tool definitions."""
        tools = historical_tools.get_tool_definitions()
        
        assert len(tools) == 2
        tool_names = [tool.name for tool in tools]
        assert "get_historical_data" in tool_names
        assert "get_ohlcv_data" in tool_names
    
    @pytest.mark.asyncio
    async def test_get_historical_data(
        self, historical_tools, mock_api_client
    ):
        """Test getting historical data."""
        from datetime import datetime
        from src.api.models import HistoricalQuote
        
        mock_quotes = [
            HistoricalQuote(
                timestamp=datetime.now(),
                quote={
                    "USD": Quote(
                        price=50000.0,
                        volume_24h=30000000000.0,
                        market_cap=950000000000.0
                    )
                }
            )
        ]
        
        mock_api_client.get_historical_quotes.return_value = mock_quotes
        
        result = await historical_tools.get_historical_data(
            symbol="BTC",
            count=10,
            convert="USD"
        )
        
        assert len(result) == 1
        assert "Historical" in result[0].text
        assert "BTC" in result[0].text
    
    @pytest.mark.asyncio
    async def test_get_ohlcv_data(
        self, historical_tools, mock_api_client
    ):
        """Test getting OHLCV data."""
        from datetime import datetime
        from src.api.models import OHLCVData
        
        mock_ohlcv = [
            OHLCVData(
                time_open=datetime.now(),
                time_close=datetime.now(),
                quote={
                    "USD": {
                        "open": 49000.0,
                        "high": 51000.0,
                        "low": 48000.0,
                        "close": 50000.0,
                        "volume": 30000000000.0
                    }
                }
            )
        ]
        
        mock_api_client.get_ohlcv_historical.return_value = mock_ohlcv
        
        result = await historical_tools.get_ohlcv_data(
            symbol="BTC",
            count=10,
            convert="USD"
        )
        
        assert len(result) == 1
        assert "OHLCV" in result[0].text
        assert "BTC" in result[0].text


class TestAnalyticsTools:
    """Test analytics tools."""
    
    def test_get_tool_definitions(self, analytics_tools):
        """Test getting tool definitions."""
        tools = analytics_tools.get_tool_definitions()
        
        assert len(tools) == 2
        tool_names = [tool.name for tool in tools]
        assert "search_cryptocurrencies" in tool_names
        assert "get_market_statistics" in tool_names
    
    @pytest.mark.asyncio
    async def test_search_cryptocurrencies(
        self, analytics_tools, mock_api_client
    ):
        """Test searching cryptocurrencies."""
        from src.api.models import SearchResult
        
        mock_results = [
            SearchResult(
                id=1,
                name="Bitcoin",
                symbol="BTC",
                slug="bitcoin",
                rank=1,
                is_active=1
            )
        ]
        
        mock_api_client.search_cryptocurrencies.return_value = mock_results
        
        result = await analytics_tools.search_cryptocurrencies(
            query="bit",
            limit=10
        )
        
        assert len(result) == 1
        assert "Bitcoin" in result[0].text
        assert "BTC" in result[0].text
    
    @pytest.mark.asyncio
    async def test_search_cryptocurrencies_no_results(
        self, analytics_tools, mock_api_client
    ):
        """Test searching with no results."""
        mock_api_client.search_cryptocurrencies.return_value = []
        
        result = await analytics_tools.search_cryptocurrencies(
            query="nonexistent",
            limit=10
        )
        
        assert len(result) == 1
        assert "No cryptocurrencies found" in result[0].text
    
    @pytest.mark.asyncio
    async def test_get_market_statistics(
        self, analytics_tools, mock_api_client, mock_cryptocurrency
    ):
        """Test getting market statistics."""
        from datetime import datetime
        
        mock_metrics = GlobalMetrics(
            active_cryptocurrencies=10000,
            total_cryptocurrencies=20000,
            active_market_pairs=50000,
            active_exchanges=500,
            total_exchanges=1000,
            eth_dominance=18.5,
            btc_dominance=45.0,
            quote={
                "USD": {
                    "total_market_cap": 2000000000000.0,
                    "total_volume_24h": 100000000000.0
                }
            },
            last_updated=datetime.now()
        )
        
        mock_api_client.get_global_metrics.return_value = mock_metrics
        mock_api_client.get_cryptocurrency_listings.return_value = [
            mock_cryptocurrency
        ]
        
        result = await analytics_tools.get_market_statistics(convert="USD")
        
        assert len(result) == 1
        assert "Market Statistics" in result[0].text
        assert "MARKET OVERVIEW" in result[0].text
        assert "DOMINANCE" in result[0].text
        assert "TOP 10" in result[0].text


class TestToolInputValidation:
    """Test tool input validation."""
    
    @pytest.mark.asyncio
    async def test_invalid_symbol_format(
        self, realtime_tools, mock_api_client
    ):
        """Test invalid symbol format."""
        result = await realtime_tools.get_cryptocurrency_price(
            symbols="BTC$INVALID",
            convert="USD"
        )
        
        assert "Error" in result[0].text
    
    @pytest.mark.asyncio
    async def test_invalid_limit(
        self, realtime_tools, mock_api_client, mock_cryptocurrency
    ):
        """Test invalid limit value."""
        result = await realtime_tools.get_top_cryptocurrencies(
            limit=10000,  # Exceeds max
            convert="USD"
        )
        
        assert "Error" in result[0].text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
