"""
Real-time cryptocurrency data tools for MCP server.
"""

import logging
from typing import Dict, List, Any
from mcp.types import Tool, TextContent

from src.api.client import CoinMarketCapClient
from src.utils.cache import CryptoCache
from src.utils.validators import validate_symbols, validate_limit

logger = logging.getLogger(__name__)


class RealtimeTools:
    """Real-time cryptocurrency data tools."""
    
    def __init__(self, api_client: CoinMarketCapClient, cache: CryptoCache):
        """
        Initialize realtime tools.
        
        Args:
            api_client: CoinMarketCap API client
            cache: Cache instance
        """
        self.api_client = api_client
        self.cache = cache
        logger.info("Initialized realtime tools")
    
    def get_tool_definitions(self) -> List[Tool]:
        """Get tool definitions for MCP."""
        return [
            Tool(
                name="get_cryptocurrency_price",
                description="Get real-time price and market data for specific cryptocurrencies",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "symbols": {
                            "type": "string",
                            "description": "Comma-separated cryptocurrency symbols (e.g., 'BTC,ETH,ADA')"
                        },
                        "convert": {
                            "type": "string",
                            "description": "Currency to convert to (default: USD)",
                            "default": "USD"
                        }
                    },
                    "required": ["symbols"]
                }
            ),
            Tool(
                name="get_cryptocurrency_info",
                description="Get detailed information about cryptocurrencies including description, website, and social links",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "symbols": {
                            "type": "string",
                            "description": "Comma-separated cryptocurrency symbols"
                        }
                    },
                    "required": ["symbols"]
                }
            ),
            Tool(
                name="get_top_cryptocurrencies",
                description="Get top cryptocurrencies by market cap ranking",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "number",
                            "description": "Number of cryptocurrencies to return (1-5000, default: 100)",
                            "default": 100
                        },
                        "convert": {
                            "type": "string",
                            "description": "Currency to convert to (default: USD)",
                            "default": "USD"
                        }
                    }
                }
            ),
            Tool(
                name="get_global_metrics",
                description="Get global cryptocurrency market metrics including total market cap, volume, and dominance",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "convert": {
                            "type": "string",
                            "description": "Currency to convert to (default: USD)",
                            "default": "USD"
                        }
                    }
                }
            )
        ]
    
    async def get_cryptocurrency_price(self, symbols: str, convert: str = "USD") -> List[TextContent]:
        """
        Get real-time cryptocurrency prices.
        
        Args:
            symbols: Comma-separated symbols
            convert: Conversion currency
            
        Returns:
            List of TextContent with price data
        """
        try:
            symbol_list = validate_symbols(symbols)
            logger.info(f"Getting prices for: {symbol_list}")
            
            # Check cache first
            cache_key = self.cache._generate_key("price", symbols=symbols, convert=convert)
            cached_data = self.cache.get(cache_key)
            
            if cached_data:
                logger.debug("Returning cached price data")
                return [TextContent(type="text", text=cached_data)]
            
            # Fetch from API
            quotes = await self.api_client.get_cryptocurrency_quotes(
                symbols=symbol_list,
                convert=convert
            )
            
            # Format response
            result_lines = [f"Cryptocurrency Prices ({convert}):", "=" * 50]
            
            for symbol, crypto in quotes.items():
                quote = crypto.quote.get(convert)
                if quote:
                    result_lines.extend([
                        f"\n{crypto.name} ({crypto.symbol})",
                        f"  Price: {convert} {quote.price:,.2f}",
                        f"  Market Cap: {convert} {quote.market_cap:,.0f}" if quote.market_cap else "",
                        f"  24h Volume: {convert} {quote.volume_24h:,.0f}" if quote.volume_24h else "",
                        f"  24h Change: {quote.percent_change_24h:+.2f}%" if quote.percent_change_24h else "",
                        f"  7d Change: {quote.percent_change_7d:+.2f}%" if quote.percent_change_7d else "",
                        f"  Market Cap Rank: #{crypto.cmc_rank}" if crypto.cmc_rank else ""
                    ])
            
            response_text = "\n".join(line for line in result_lines if line)
            
            # Cache result
            self.cache.set(cache_key, response_text)
            
            return [TextContent(type="text", text=response_text)]
        
        except Exception as e:
            logger.error(f"Error getting cryptocurrency price: {e}")
            return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    async def get_cryptocurrency_info(self, symbols: str) -> List[TextContent]:
        """
        Get detailed cryptocurrency information.
        
        Args:
            symbols: Comma-separated symbols
            
        Returns:
            List of TextContent with info data
        """
        try:
            symbol_list = validate_symbols(symbols)
            logger.info(f"Getting info for: {symbol_list}")
            
            # Check cache
            cache_key = self.cache._generate_key("info", symbols=symbols)
            cached_data = self.cache.get(cache_key)
            
            if cached_data:
                return [TextContent(type="text", text=cached_data)]
            
            # Fetch from API
            info_dict = await self.api_client.get_cryptocurrency_info(symbols=symbol_list)
            
            # Format response
            result_lines = ["Cryptocurrency Information:", "=" * 50]
            
            for symbol, info in info_dict.items():
                result_lines.extend([
                    f"\n{info.name} ({info.symbol})",
                    f"  Category: {info.category or 'N/A'}",
                    f"  Description: {(info.description[:200] + '...') if info.description else 'N/A'}",
                    f"  Website: {info.urls.get('website', ['N/A'])[0] if info.urls else 'N/A'}",
                    f"  Twitter: @{info.twitter_username or 'N/A'}",
                    f"  Tags: {', '.join(info.tags[:5]) if info.tags else 'N/A'}",
                    f"  Date Added: {info.date_added.strftime('%Y-%m-%d') if info.date_added else 'N/A'}"
                ])
            
            response_text = "\n".join(result_lines)
            self.cache.set(cache_key, response_text)
            
            return [TextContent(type="text", text=response_text)]
        
        except Exception as e:
            logger.error(f"Error getting cryptocurrency info: {e}")
            return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    async def get_top_cryptocurrencies(self, limit: int = 100, convert: str = "USD") -> List[TextContent]:
        """
        Get top cryptocurrencies by market cap.
        
        Args:
            limit: Number of results
            convert: Conversion currency
            
        Returns:
            List of TextContent with top cryptos
        """
        try:
            limit = validate_limit(limit, min_val=1, max_val=5000)
            logger.info(f"Getting top {limit} cryptocurrencies")
            
            # Check cache
            cache_key = self.cache._generate_key("top", limit=limit, convert=convert)
            cached_data = self.cache.get(cache_key)
            
            if cached_data:
                return [TextContent(type="text", text=cached_data)]
            
            # Fetch from API
            cryptos = await self.api_client.get_cryptocurrency_listings(
                limit=limit,
                convert=convert
            )
            
            # Format response
            result_lines = [
                f"Top {limit} Cryptocurrencies by Market Cap ({convert}):",
                "=" * 80
            ]
            
            for crypto in cryptos:
                quote = crypto.quote.get(convert)
                if quote:
                    result_lines.append(
                        f"{crypto.cmc_rank:3d}. {crypto.name:20s} ({crypto.symbol:6s}) "
                        f"${quote.price:12,.2f}  "
                        f"Cap: ${quote.market_cap/1e9:8,.2f}B  "
                        f"24h: {quote.percent_change_24h:+6.2f}%"
                    )
            
            response_text = "\n".join(result_lines)
            self.cache.set(cache_key, response_text)
            
            return [TextContent(type="text", text=response_text)]
        
        except Exception as e:
            logger.error(f"Error getting top cryptocurrencies: {e}")
            return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    async def get_global_metrics(self, convert: str = "USD") -> List[TextContent]:
        """
        Get global cryptocurrency market metrics.
        
        Args:
            convert: Conversion currency
            
        Returns:
            List of TextContent with global metrics
        """
        try:
            logger.info("Getting global market metrics")
            
            # Check cache
            cache_key = self.cache._generate_key("global", convert=convert)
            cached_data = self.cache.get(cache_key)
            
            if cached_data:
                return [TextContent(type="text", text=cached_data)]
            
            # Fetch from API
            metrics = await self.api_client.get_global_metrics(convert=convert)
            quote = metrics.quote.get(convert, {})
            
            # Format response
            result_lines = [
                "Global Cryptocurrency Market Metrics:",
                "=" * 50,
                f"\nActive Cryptocurrencies: {metrics.active_cryptocurrencies:,}",
                f"Total Cryptocurrencies: {metrics.total_cryptocurrencies:,}",
                f"Active Exchanges: {metrics.active_exchanges:,}",
                f"Active Market Pairs: {metrics.active_market_pairs:,}",
                f"\nTotal Market Cap: {convert} {quote.get('total_market_cap', 0):,.0f}",
                f"Total 24h Volume: {convert} {quote.get('total_volume_24h', 0):,.0f}",
                f"BTC Dominance: {metrics.btc_dominance:.2f}%",
                f"ETH Dominance: {metrics.eth_dominance:.2f}%",
                f"\nDeFi Market Cap: {convert} {metrics.defi_market_cap or 0:,.0f}",
                f"DeFi 24h Volume: {convert} {metrics.defi_volume_24h or 0:,.0f}",
                f"Stablecoin Market Cap: {convert} {metrics.stablecoin_market_cap or 0:,.0f}",
                f"Stablecoin 24h Volume: {convert} {metrics.stablecoin_volume_24h or 0:,.0f}",
                f"\nLast Updated: {metrics.last_updated.strftime('%Y-%m-%d %H:%M:%S UTC')}"
            ]
            
            response_text = "\n".join(result_lines)
            self.cache.set(cache_key, response_text)
            
            return [TextContent(type="text", text=response_text)]
        
        except Exception as e:
            logger.error(f"Error getting global metrics: {e}")
            return [TextContent(type="text", text=f"Error: {str(e)}")]
