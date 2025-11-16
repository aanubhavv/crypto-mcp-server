"""
CoinMarketCap API client with error handling and rate limiting.
"""

import os
import logging
from typing import Dict, List, Optional, Any
import httpx
from datetime import datetime

from src.api.models import (
    Cryptocurrency,
    CryptocurrencyInfo,
    GlobalMetrics,
    HistoricalQuote,
    OHLCVData,
    SearchResult,
    parse_cryptocurrency_data,
    parse_cryptocurrency_list,
    parse_global_metrics
)
from src.utils.errors import (
    APIError,
    AuthenticationError,
    RateLimitError,
    APIConnectionError,
    APITimeoutError,
    InvalidResponseError,
    handle_api_error,
    ConfigurationError
)
from src.utils.cache import RateLimiter
from src.utils.validators import sanitize_parameters

logger = logging.getLogger(__name__)


class CoinMarketCapClient:
    """
    Robust CoinMarketCap API client with comprehensive error handling.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        rate_limit_requests: int = 30,
        rate_limit_period: int = 60
    ):
        """
        Initialize CoinMarketCap API client.
        
        Args:
            api_key: CoinMarketCap API key
            base_url: API base URL
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            rate_limit_requests: Number of requests per period
            rate_limit_period: Rate limit period in seconds
        """
        self.api_key = api_key or os.getenv("COINMARKETCAP_API_KEY")
        if not self.api_key:
            raise ConfigurationError("CoinMarketCap API key not provided")
        
        self.base_url = base_url or os.getenv(
            "COINMARKETCAP_BASE_URL",
            "https://pro-api.coinmarketcap.com/v1"
        )
        self.timeout = timeout
        self.max_retries = max_retries
        
        self.headers = {
            "X-CMC_PRO_API_KEY": self.api_key,
            "Accept": "application/json"
        }
        
        self.client = httpx.AsyncClient(
            headers=self.headers,
            timeout=timeout,
            follow_redirects=True
        )
        
        self.rate_limiter = RateLimiter(
            requests_per_period=rate_limit_requests,
            period_seconds=rate_limit_period
        )
        
        logger.info("Initialized CoinMarketCap API client")
    
    async def _make_request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        method: str = "GET"
    ) -> Dict[str, Any]:
        """
        Make HTTP request to API with error handling and retries.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            method: HTTP method
            
        Returns:
            Response data
            
        Raises:
            Various API errors based on response
        """
        url = f"{self.base_url}/{endpoint}"
        params = sanitize_parameters(params or {})
        
        # Apply rate limiting
        await self.rate_limiter.wait_for_token()
        
        retries = 0
        last_exception = None
        
        while retries <= self.max_retries:
            try:
                logger.debug(f"Making request to {url} with params: {params}")
                
                if method == "GET":
                    response = await self.client.get(url, params=params)
                else:
                    response = await self.client.post(url, json=params)
                
                # Handle successful response
                if response.status_code == 200:
                    data = response.json()
                    logger.debug(f"Successful response from {endpoint}")
                    return data
                
                # Handle error responses
                try:
                    error_data = response.json()
                except Exception:
                    error_data = {"status": {"error_message": response.text}}
                
                handle_api_error(response.status_code, error_data)
            
            except httpx.TimeoutException as e:
                last_exception = APITimeoutError(f"Request timeout: {str(e)}")
                logger.warning(f"Timeout on attempt {retries + 1}: {e}")
            
            except httpx.ConnectError as e:
                last_exception = APIConnectionError(f"Connection failed: {str(e)}")
                logger.warning(f"Connection error on attempt {retries + 1}: {e}")
            
            except (AuthenticationError, RateLimitError) as e:
                # Don't retry auth or rate limit errors
                logger.error(f"Non-retryable error: {e}")
                raise
            
            except Exception as e:
                last_exception = APIError(f"Unexpected error: {str(e)}")
                logger.error(f"Unexpected error on attempt {retries + 1}: {e}")
            
            retries += 1
            if retries <= self.max_retries:
                import asyncio
                wait_time = 2 ** retries  # Exponential backoff
                logger.info(f"Retrying in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
        
        # Max retries exceeded
        logger.error(f"Max retries exceeded for {endpoint}")
        raise last_exception or APIError("Max retries exceeded")
    
    async def get_cryptocurrency_quotes(
        self,
        symbols: Optional[List[str]] = None,
        ids: Optional[List[int]] = None,
        convert: str = "USD"
    ) -> Dict[str, Cryptocurrency]:
        """
        Get latest cryptocurrency quotes.
        
        Args:
            symbols: List of cryptocurrency symbols
            ids: List of cryptocurrency IDs
            convert: Conversion currency
            
        Returns:
            Dictionary mapping symbols to Cryptocurrency objects
        """
        params = {"convert": convert}
        
        if symbols:
            params["symbol"] = ",".join(symbols)
        elif ids:
            params["id"] = ",".join(map(str, ids))
        else:
            raise ValueError("Either symbols or ids must be provided")
        
        response = await self._make_request("cryptocurrency/quotes/latest", params)
        
        result = {}
        data = response.get("data", {})
        
        for key, value in data.items():
            crypto = parse_cryptocurrency_data(value)
            result[crypto.symbol] = crypto
        
        return result
    
    async def get_cryptocurrency_listings(
        self,
        start: int = 1,
        limit: int = 100,
        convert: str = "USD",
        sort: str = "market_cap",
        sort_dir: str = "desc"
    ) -> List[Cryptocurrency]:
        """
        Get cryptocurrency listings.
        
        Args:
            start: Starting position
            limit: Number of results
            convert: Conversion currency
            sort: Sort field
            sort_dir: Sort direction
            
        Returns:
            List of Cryptocurrency objects
        """
        params = {
            "start": start,
            "limit": limit,
            "convert": convert,
            "sort": sort,
            "sort_dir": sort_dir
        }
        
        response = await self._make_request("cryptocurrency/listings/latest", params)
        data = response.get("data", [])
        
        return parse_cryptocurrency_list(data)
    
    async def get_cryptocurrency_info(
        self,
        symbols: Optional[List[str]] = None,
        ids: Optional[List[int]] = None
    ) -> Dict[str, CryptocurrencyInfo]:
        """
        Get cryptocurrency metadata/info.
        
        Args:
            symbols: List of cryptocurrency symbols
            ids: List of cryptocurrency IDs
            
        Returns:
            Dictionary mapping symbols to CryptocurrencyInfo objects
        """
        params = {}
        
        if symbols:
            params["symbol"] = ",".join(symbols)
        elif ids:
            params["id"] = ",".join(map(str, ids))
        else:
            raise ValueError("Either symbols or ids must be provided")
        
        response = await self._make_request("cryptocurrency/info", params)
        
        result = {}
        data = response.get("data", {})
        
        for key, value in data.items():
            info = CryptocurrencyInfo(**value)
            result[info.symbol] = info
        
        return result
    
    async def get_global_metrics(self, convert: str = "USD") -> GlobalMetrics:
        """
        Get global cryptocurrency market metrics.
        
        Args:
            convert: Conversion currency
            
        Returns:
            GlobalMetrics object
        """
        params = {"convert": convert}
        response = await self._make_request("global-metrics/quotes/latest", params)
        data = response.get("data", {})
        
        return parse_global_metrics(data)
    
    async def get_ohlcv_historical(
        self,
        symbol: str,
        time_period: str = "daily",
        time_start: Optional[str] = None,
        time_end: Optional[str] = None,
        count: int = 10,
        convert: str = "USD"
    ) -> List[OHLCVData]:
        """
        Get historical OHLCV data.
        
        Args:
            symbol: Cryptocurrency symbol
            time_period: Time period (daily, hourly, etc.)
            time_start: Start time
            time_end: End time
            count: Number of data points
            convert: Conversion currency
            
        Returns:
            List of OHLCVData objects
        """
        params = {
            "symbol": symbol,
            "time_period": time_period,
            "count": count,
            "convert": convert
        }
        
        if time_start:
            params["time_start"] = time_start
        if time_end:
            params["time_end"] = time_end
        
        response = await self._make_request("cryptocurrency/ohlcv/historical", params)
        data = response.get("data", {})
        
        quotes = data.get("quotes", [])
        return [OHLCVData(**item) for item in quotes]
    
    async def get_historical_quotes(
        self,
        symbol: str,
        time_start: Optional[str] = None,
        time_end: Optional[str] = None,
        count: int = 10,
        interval: str = "daily",
        convert: str = "USD"
    ) -> List[HistoricalQuote]:
        """
        Get historical price quotes.
        
        Args:
            symbol: Cryptocurrency symbol
            time_start: Start time
            time_end: End time
            count: Number of data points
            interval: Time interval
            convert: Conversion currency
            
        Returns:
            List of HistoricalQuote objects
        """
        params = {
            "symbol": symbol,
            "count": count,
            "interval": interval,
            "convert": convert
        }
        
        if time_start:
            params["time_start"] = time_start
        if time_end:
            params["time_end"] = time_end
        
        response = await self._make_request("cryptocurrency/quotes/historical", params)
        data = response.get("data", {})
        
        quotes = data.get("quotes", [])
        return [HistoricalQuote(**item) for item in quotes]
    
    async def search_cryptocurrencies(
        self,
        query: str,
        limit: int = 10
    ) -> List[SearchResult]:
        """
        Search for cryptocurrencies.
        
        Args:
            query: Search query
            limit: Number of results
            
        Returns:
            List of SearchResult objects
        """
        # Note: CoinMarketCap's free API doesn't have a direct search endpoint
        # We'll use the map endpoint and filter results
        response = await self._make_request("cryptocurrency/map")
        data = response.get("data", [])
        
        # Filter results based on query
        query_lower = query.lower()
        results = []
        
        for item in data:
            if (query_lower in item.get("name", "").lower() or 
                query_lower in item.get("symbol", "").lower()):
                results.append(SearchResult(
                    id=item["id"],
                    name=item["name"],
                    symbol=item["symbol"],
                    slug=item["slug"],
                    rank=item.get("rank"),
                    is_active=item.get("is_active", 1)
                ))
                
                if len(results) >= limit:
                    break
        
        return results
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
        logger.info("Closed CoinMarketCap API client")
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
