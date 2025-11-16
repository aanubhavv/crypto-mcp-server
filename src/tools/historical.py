"""
Historical cryptocurrency data tools for MCP server.
"""

import logging
from typing import List
from mcp.types import Tool, TextContent

from src.api.client import CoinMarketCapClient
from src.utils.cache import CryptoCache
from src.utils.validators import validate_symbol, validate_limit

logger = logging.getLogger(__name__)


class HistoricalTools:
    """Historical cryptocurrency data tools."""
    
    def __init__(self, api_client: CoinMarketCapClient, cache: CryptoCache):
        """
        Initialize historical tools.
        
        Args:
            api_client: CoinMarketCap API client
            cache: Cache instance
        """
        self.api_client = api_client
        self.cache = cache
        logger.info("Initialized historical tools")
    
    def get_tool_definitions(self) -> List[Tool]:
        """Get tool definitions for MCP."""
        return [
            Tool(
                name="get_historical_data",
                description="Get historical price data for a cryptocurrency",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "Cryptocurrency symbol (e.g., 'BTC')"
                        },
                        "time_start": {
                            "type": "string",
                            "description": "Start time in ISO format (e.g., '2024-01-01')"
                        },
                        "time_end": {
                            "type": "string",
                            "description": "End time in ISO format (e.g., '2024-01-31')"
                        },
                        "count": {
                            "type": "number",
                            "description": "Number of data points (default: 10, max: 10000)",
                            "default": 10
                        },
                        "interval": {
                            "type": "string",
                            "description": "Time interval: hourly, daily, weekly, monthly (default: daily)",
                            "enum": ["hourly", "daily", "weekly", "monthly"],
                            "default": "daily"
                        },
                        "convert": {
                            "type": "string",
                            "description": "Currency to convert to (default: USD)",
                            "default": "USD"
                        }
                    },
                    "required": ["symbol"]
                }
            ),
            Tool(
                name="get_ohlcv_data",
                description="Get OHLCV (Open, High, Low, Close, Volume) historical data for a cryptocurrency",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "Cryptocurrency symbol (e.g., 'BTC')"
                        },
                        "time_period": {
                            "type": "string",
                            "description": "Time period: hourly, daily, weekly, monthly (default: daily)",
                            "default": "daily"
                        },
                        "time_start": {
                            "type": "string",
                            "description": "Start time in ISO format"
                        },
                        "time_end": {
                            "type": "string",
                            "description": "End time in ISO format"
                        },
                        "count": {
                            "type": "number",
                            "description": "Number of intervals (default: 10, max: 10000)",
                            "default": 10
                        },
                        "convert": {
                            "type": "string",
                            "description": "Currency to convert to (default: USD)",
                            "default": "USD"
                        }
                    },
                    "required": ["symbol"]
                }
            )
        ]
    
    async def get_historical_data(
        self,
        symbol: str,
        time_start: str = None,
        time_end: str = None,
        count: int = 10,
        interval: str = "daily",
        convert: str = "USD"
    ) -> List[TextContent]:
        """
        Get historical price data.
        
        Args:
            symbol: Cryptocurrency symbol
            time_start: Start time
            time_end: End time
            count: Number of data points
            interval: Time interval
            convert: Conversion currency
            
        Returns:
            List of TextContent with historical data
        """
        try:
            symbol = validate_symbol(symbol)
            count = validate_limit(count, min_val=1, max_val=10000)
            logger.info(f"Getting historical data for {symbol}")
            
            # Check cache
            cache_key = self.cache._generate_key(
                "historical",
                symbol=symbol,
                time_start=time_start,
                time_end=time_end,
                count=count,
                interval=interval,
                convert=convert
            )
            cached_data = self.cache.get(cache_key)
            
            if cached_data:
                return [TextContent(type="text", text=cached_data)]
            
            # Fetch from API
            quotes = await self.api_client.get_historical_quotes(
                symbol=symbol,
                time_start=time_start,
                time_end=time_end,
                count=count,
                interval=interval,
                convert=convert
            )
            
            # Format response
            result_lines = [
                f"Historical Price Data for {symbol} ({convert}):",
                f"Interval: {interval}, Data Points: {len(quotes)}",
                "=" * 80
            ]
            
            for quote_data in quotes:
                timestamp = quote_data.timestamp
                quote = quote_data.quote.get(convert)
                
                if quote:
                    result_lines.append(
                        f"{timestamp.strftime('%Y-%m-%d %H:%M')}  "
                        f"Price: ${quote.price:12,.2f}  "
                        f"Volume: ${quote.volume_24h:15,.0f}  "
                        f"Market Cap: ${quote.market_cap:15,.0f}"
                    )
            
            if not quotes:
                result_lines.append("\nNo historical data available for the specified period.")
            
            response_text = "\n".join(result_lines)
            self.cache.set(cache_key, response_text)
            
            return [TextContent(type="text", text=response_text)]
        
        except Exception as e:
            logger.error(f"Error getting historical data: {e}")
            return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    async def get_ohlcv_data(
        self,
        symbol: str,
        time_period: str = "daily",
        time_start: str = None,
        time_end: str = None,
        count: int = 10,
        convert: str = "USD"
    ) -> List[TextContent]:
        """
        Get OHLCV data.
        
        Args:
            symbol: Cryptocurrency symbol
            time_period: Time period
            time_start: Start time
            time_end: End time
            count: Number of intervals
            convert: Conversion currency
            
        Returns:
            List of TextContent with OHLCV data
        """
        try:
            symbol = validate_symbol(symbol)
            count = validate_limit(count, min_val=1, max_val=10000)
            logger.info(f"Getting OHLCV data for {symbol}")
            
            # Check cache
            cache_key = self.cache._generate_key(
                "ohlcv",
                symbol=symbol,
                time_period=time_period,
                time_start=time_start,
                time_end=time_end,
                count=count,
                convert=convert
            )
            cached_data = self.cache.get(cache_key)
            
            if cached_data:
                return [TextContent(type="text", text=cached_data)]
            
            # Fetch from API
            ohlcv_data = await self.api_client.get_ohlcv_historical(
                symbol=symbol,
                time_period=time_period,
                time_start=time_start,
                time_end=time_end,
                count=count,
                convert=convert
            )
            
            # Format response
            result_lines = [
                f"OHLCV Data for {symbol} ({convert}):",
                f"Period: {time_period}, Intervals: {len(ohlcv_data)}",
                "=" * 100,
                f"{'Date':<20} {'Open':>12} {'High':>12} {'Low':>12} {'Close':>12} {'Volume':>15}",
                "-" * 100
            ]
            
            for data_point in ohlcv_data:
                time_open = data_point.time_open
                quote_data = data_point.quote.get(convert, {})
                
                result_lines.append(
                    f"{time_open.strftime('%Y-%m-%d %H:%M'):<20} "
                    f"${quote_data.get('open', 0):11,.2f} "
                    f"${quote_data.get('high', 0):11,.2f} "
                    f"${quote_data.get('low', 0):11,.2f} "
                    f"${quote_data.get('close', 0):11,.2f} "
                    f"${quote_data.get('volume', 0):14,.0f}"
                )
            
            if not ohlcv_data:
                result_lines.append("\nNo OHLCV data available for the specified period.")
            
            response_text = "\n".join(result_lines)
            self.cache.set(cache_key, response_text)
            
            return [TextContent(type="text", text=response_text)]
        
        except Exception as e:
            logger.error(f"Error getting OHLCV data: {e}")
            return [TextContent(type="text", text=f"Error: {str(e)}")]
