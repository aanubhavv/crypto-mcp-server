"""
Unit tests for API client.
"""

import pytest
import httpx
import respx
from datetime import datetime

from src.api.client import CoinMarketCapClient
from src.api.models import Cryptocurrency, GlobalMetrics
from src.utils.errors import (
    AuthenticationError,
    RateLimitError,
    APIConnectionError,
    APITimeoutError
)


@pytest.fixture
def api_key():
    """Fixture for API key."""
    return "test_api_key_12345"


@pytest.fixture
def api_client(api_key):
    """Fixture for API client."""
    return CoinMarketCapClient(
        api_key=api_key,
        base_url="https://pro-api.coinmarketcap.com/v1",
        timeout=10,
        rate_limit_requests=100,
        rate_limit_period=60
    )


@pytest.fixture
def mock_crypto_response():
    """Fixture for mock cryptocurrency response."""
    return {
        "status": {
            "timestamp": "2024-01-01T00:00:00.000Z",
            "error_code": 0,
            "error_message": None,
            "elapsed": 10,
            "credit_count": 1
        },
        "data": {
            "BTC": {
                "id": 1,
                "name": "Bitcoin",
                "symbol": "BTC",
                "slug": "bitcoin",
                "cmc_rank": 1,
                "num_market_pairs": 10000,
                "circulating_supply": 19000000,
                "total_supply": 21000000,
                "max_supply": 21000000,
                "last_updated": "2024-01-01T00:00:00.000Z",
                "date_added": "2013-04-28T00:00:00.000Z",
                "tags": ["mineable", "pow"],
                "platform": None,
                "quote": {
                    "USD": {
                        "price": 50000.0,
                        "volume_24h": 30000000000.0,
                        "percent_change_1h": 0.5,
                        "percent_change_24h": 2.5,
                        "percent_change_7d": 5.0,
                        "market_cap": 950000000000.0,
                        "last_updated": "2024-01-01T00:00:00.000Z"
                    }
                }
            }
        }
    }


@pytest.fixture
def mock_global_metrics_response():
    """Fixture for mock global metrics response."""
    return {
        "status": {
            "timestamp": "2024-01-01T00:00:00.000Z",
            "error_code": 0,
            "error_message": None,
            "elapsed": 10,
            "credit_count": 1
        },
        "data": {
            "active_cryptocurrencies": 10000,
            "total_cryptocurrencies": 20000,
            "active_market_pairs": 50000,
            "active_exchanges": 500,
            "total_exchanges": 1000,
            "eth_dominance": 18.5,
            "btc_dominance": 45.0,
            "quote": {
                "USD": {
                    "total_market_cap": 2000000000000.0,
                    "total_volume_24h": 100000000000.0
                }
            },
            "last_updated": "2024-01-01T00:00:00.000Z"
        }
    }


class TestCoinMarketCapClient:
    """Test CoinMarketCap API client."""
    
    def test_client_initialization(self, api_key):
        """Test client initialization."""
        client = CoinMarketCapClient(api_key=api_key)
        
        assert client.api_key == api_key
        assert client.headers["X-CMC_PRO_API_KEY"] == api_key
        assert "Accept" in client.headers
    
    def test_client_initialization_no_api_key(self, monkeypatch):
        """Test client initialization without API key."""
        from src.utils.errors import ConfigurationError
        
        # Ensure environment variable is not set
        monkeypatch.delenv("COINMARKETCAP_API_KEY", raising=False)
        
        with pytest.raises(ConfigurationError):
            CoinMarketCapClient(api_key=None)
    
    @pytest.mark.asyncio
    @respx.mock
    async def test_get_cryptocurrency_quotes_success(
        self, api_client, mock_crypto_response
    ):
        """Test successful cryptocurrency quotes request."""
        route = respx.get(
            "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
        ).mock(return_value=httpx.Response(200, json=mock_crypto_response))
        
        result = await api_client.get_cryptocurrency_quotes(
            symbols=["BTC"],
            convert="USD"
        )
        
        assert "BTC" in result
        assert result["BTC"].name == "Bitcoin"
        assert result["BTC"].symbol == "BTC"
        assert result["BTC"].quote["USD"].price == 50000.0
    
    @pytest.mark.asyncio
    @respx.mock
    async def test_get_cryptocurrency_quotes_auth_error(self, api_client):
        """Test authentication error handling."""
        error_response = {
            "status": {
                "error_code": 401,
                "error_message": "Invalid API key"
            }
        }
        
        route = respx.get(
            "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
        ).mock(return_value=httpx.Response(401, json=error_response))
        
        with pytest.raises(AuthenticationError):
            await api_client.get_cryptocurrency_quotes(symbols=["BTC"])
    
    @pytest.mark.asyncio
    @respx.mock
    async def test_get_cryptocurrency_quotes_rate_limit(self, api_client):
        """Test rate limit error handling."""
        error_response = {
            "status": {
                "error_code": 429,
                "error_message": "Rate limit exceeded"
            }
        }
        
        route = respx.get(
            "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
        ).mock(return_value=httpx.Response(429, json=error_response))
        
        with pytest.raises(RateLimitError):
            await api_client.get_cryptocurrency_quotes(symbols=["BTC"])
    
    @pytest.mark.asyncio
    @respx.mock
    async def test_get_cryptocurrency_listings_success(
        self, api_client, mock_crypto_response
    ):
        """Test successful listings request."""
        listings_response = {
            "status": mock_crypto_response["status"],
            "data": [mock_crypto_response["data"]["BTC"]]
        }
        
        route = respx.get(
            "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
        ).mock(return_value=httpx.Response(200, json=listings_response))
        
        result = await api_client.get_cryptocurrency_listings(
            limit=10,
            convert="USD"
        )
        
        assert len(result) == 1
        assert result[0].symbol == "BTC"
        assert result[0].cmc_rank == 1
    
    @pytest.mark.asyncio
    @respx.mock
    async def test_get_global_metrics_success(
        self, api_client, mock_global_metrics_response
    ):
        """Test successful global metrics request."""
        route = respx.get(
            "https://pro-api.coinmarketcap.com/v1/global-metrics/quotes/latest"
        ).mock(return_value=httpx.Response(200, json=mock_global_metrics_response))
        
        result = await api_client.get_global_metrics(convert="USD")
        
        assert result.active_cryptocurrencies == 10000
        assert result.btc_dominance == 45.0
        assert result.eth_dominance == 18.5
    
    @pytest.mark.asyncio
    @respx.mock
    async def test_request_retry_on_timeout(self, api_client):
        """Test retry mechanism on timeout."""
        # First call times out, second succeeds
        route = respx.get(
            "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
        ).mock(side_effect=[
            httpx.TimeoutException("Timeout"),
            httpx.Response(200, json={
                "status": {"error_code": 0},
                "data": {}
            })
        ])
        
        # Should succeed after retry
        result = await api_client.get_cryptocurrency_quotes(symbols=["BTC"])
        assert result is not None
    
    @pytest.mark.asyncio
    @respx.mock
    async def test_request_max_retries_exceeded(self, api_client):
        """Test max retries exceeded."""
        # All calls timeout
        route = respx.get(
            "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
        ).mock(side_effect=httpx.TimeoutException("Timeout"))
        
        with pytest.raises(APITimeoutError):
            await api_client.get_cryptocurrency_quotes(symbols=["BTC"])
    
    @pytest.mark.asyncio
    @respx.mock
    async def test_search_cryptocurrencies(self, api_client):
        """Test cryptocurrency search."""
        search_response = {
            "status": {"error_code": 0},
            "data": [
                {
                    "id": 1,
                    "name": "Bitcoin",
                    "symbol": "BTC",
                    "slug": "bitcoin",
                    "rank": 1,
                    "is_active": 1
                },
                {
                    "id": 1027,
                    "name": "Ethereum",
                    "symbol": "ETH",
                    "slug": "ethereum",
                    "rank": 2,
                    "is_active": 1
                }
            ]
        }
        
        route = respx.get(
            "https://pro-api.coinmarketcap.com/v1/cryptocurrency/map"
        ).mock(return_value=httpx.Response(200, json=search_response))
        
        result = await api_client.search_cryptocurrencies(query="bit", limit=5)
        
        assert len(result) > 0
        assert any(r.symbol == "BTC" for r in result)
    
    @pytest.mark.asyncio
    async def test_client_context_manager(self, api_key):
        """Test client as context manager."""
        async with CoinMarketCapClient(api_key=api_key) as client:
            assert client.api_key == api_key
        
        # Client should be closed after context
    
    @pytest.mark.asyncio
    @respx.mock
    async def test_get_ohlcv_historical(self, api_client):
        """Test OHLCV historical data."""
        ohlcv_response = {
            "status": {"error_code": 0},
            "data": {
                "quotes": [
                    {
                        "time_open": "2024-01-01T00:00:00.000Z",
                        "time_close": "2024-01-02T00:00:00.000Z",
                        "quote": {
                            "USD": {
                                "open": 49000.0,
                                "high": 51000.0,
                                "low": 48000.0,
                                "close": 50000.0,
                                "volume": 30000000000.0
                            }
                        }
                    }
                ]
            }
        }
        
        route = respx.get(
            "https://pro-api.coinmarketcap.com/v1/cryptocurrency/ohlcv/historical"
        ).mock(return_value=httpx.Response(200, json=ohlcv_response))
        
        result = await api_client.get_ohlcv_historical(
            symbol="BTC",
            count=1,
            convert="USD"
        )
        
        assert len(result) == 1
        assert result[0].quote["USD"]["close"] == 50000.0


class TestRateLimiting:
    """Test rate limiting in API client."""
    
    @pytest.mark.asyncio
    async def test_rate_limiter_respects_limits(self, api_key):
        """Test that rate limiter respects limits."""
        client = CoinMarketCapClient(
            api_key=api_key,
            rate_limit_requests=2,
            rate_limit_period=1
        )
        
        # Should be able to make 2 requests quickly
        assert client.rate_limiter.acquire() is True
        assert client.rate_limiter.acquire() is True
        
        # Third should fail without waiting
        assert client.rate_limiter.acquire() is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
