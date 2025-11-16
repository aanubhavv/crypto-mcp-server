"""
Analytics and search tools for MCP server.
"""

import logging
from typing import List
from mcp.types import Tool, TextContent

from src.api.client import CoinMarketCapClient
from src.utils.cache import CryptoCache
from src.utils.validators import validate_limit

logger = logging.getLogger(__name__)


class AnalyticsTools:
    """Analytics and search tools for cryptocurrency data."""
    
    def __init__(self, api_client: CoinMarketCapClient, cache: CryptoCache):
        """
        Initialize analytics tools.
        
        Args:
            api_client: CoinMarketCap API client
            cache: Cache instance
        """
        self.api_client = api_client
        self.cache = cache
        logger.info("Initialized analytics tools")
    
    def get_tool_definitions(self) -> List[Tool]:
        """Get tool definitions for MCP."""
        return [
            Tool(
                name="search_cryptocurrencies",
                description="Search for cryptocurrencies by name or symbol",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query (name or symbol)"
                        },
                        "limit": {
                            "type": "number",
                            "description": "Maximum number of results (default: 10, max: 100)",
                            "default": 10
                        }
                    },
                    "required": ["query"]
                }
            ),
            Tool(
                name="get_market_statistics",
                description="Get comprehensive market statistics and analytics",
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
    
    async def search_cryptocurrencies(self, query: str, limit: int = 10) -> List[TextContent]:
        """
        Search for cryptocurrencies.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of TextContent with search results
        """
        try:
            limit = validate_limit(limit, min_val=1, max_val=100)
            logger.info(f"Searching cryptocurrencies: {query}")
            
            # Check cache
            cache_key = self.cache._generate_key("search", query=query, limit=limit)
            cached_data = self.cache.get(cache_key)
            
            if cached_data:
                return [TextContent(type="text", text=cached_data)]
            
            # Search using API
            results = await self.api_client.search_cryptocurrencies(query=query, limit=limit)
            
            # Format response
            result_lines = [
                f"Search Results for '{query}':",
                f"Found {len(results)} results",
                "=" * 60
            ]
            
            if results:
                for i, result in enumerate(results, 1):
                    status = "Active" if result.is_active else "Inactive"
                    rank_info = f"Rank: #{result.rank}" if result.rank else "Rank: N/A"
                    
                    result_lines.extend([
                        f"\n{i}. {result.name} ({result.symbol})",
                        f"   ID: {result.id}",
                        f"   {rank_info}",
                        f"   Status: {status}",
                        f"   Slug: {result.slug}"
                    ])
            else:
                result_lines.append("\nNo cryptocurrencies found matching your query.")
            
            response_text = "\n".join(result_lines)
            self.cache.set(cache_key, response_text)
            
            return [TextContent(type="text", text=response_text)]
        
        except Exception as e:
            logger.error(f"Error searching cryptocurrencies: {e}")
            return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    async def get_market_statistics(self, convert: str = "USD") -> List[TextContent]:
        """
        Get comprehensive market statistics.
        
        Args:
            convert: Conversion currency
            
        Returns:
            List of TextContent with market statistics
        """
        try:
            logger.info("Getting market statistics")
            
            # Check cache
            cache_key = self.cache._generate_key("market_stats", convert=convert)
            cached_data = self.cache.get(cache_key)
            
            if cached_data:
                return [TextContent(type="text", text=cached_data)]
            
            # Get global metrics
            metrics = await self.api_client.get_global_metrics(convert=convert)
            quote = metrics.quote.get(convert, {})
            
            # Get top 10 for additional context
            top_cryptos = await self.api_client.get_cryptocurrency_listings(
                limit=10,
                convert=convert
            )
            
            # Calculate statistics
            total_market_cap = quote.get('total_market_cap', 0)
            total_volume = quote.get('total_volume_24h', 0)
            
            # Format response
            result_lines = [
                "Cryptocurrency Market Statistics:",
                "=" * 70,
                "\n📊 MARKET OVERVIEW",
                f"Total Market Cap: {convert} {total_market_cap:,.0f}",
                f"24h Trading Volume: {convert} {total_volume:,.0f}",
                f"Volume/Market Cap Ratio: {(total_volume/total_market_cap*100):.2f}%",
                f"Active Cryptocurrencies: {metrics.active_cryptocurrencies:,}",
                f"Active Markets: {metrics.active_market_pairs:,}",
                f"Active Exchanges: {metrics.active_exchanges:,}",
                "\n📈 DOMINANCE",
                f"Bitcoin (BTC): {metrics.btc_dominance:.2f}%",
                f"Ethereum (ETH): {metrics.eth_dominance:.2f}%",
                f"Altcoins: {100 - metrics.btc_dominance - metrics.eth_dominance:.2f}%"
            ]
            
            # Add DeFi stats if available
            if metrics.defi_market_cap:
                defi_dominance = (metrics.defi_market_cap / total_market_cap * 100)
                result_lines.extend([
                    "\n💎 DeFi METRICS",
                    f"DeFi Market Cap: {convert} {metrics.defi_market_cap:,.0f}",
                    f"DeFi Dominance: {defi_dominance:.2f}%",
                    f"DeFi 24h Volume: {convert} {metrics.defi_volume_24h or 0:,.0f}"
                ])
            
            # Add stablecoin stats if available
            if metrics.stablecoin_market_cap:
                stable_dominance = (metrics.stablecoin_market_cap / total_market_cap * 100)
                result_lines.extend([
                    "\n💵 STABLECOIN METRICS",
                    f"Stablecoin Market Cap: {convert} {metrics.stablecoin_market_cap:,.0f}",
                    f"Stablecoin Dominance: {stable_dominance:.2f}%",
                    f"Stablecoin 24h Volume: {convert} {metrics.stablecoin_volume_24h or 0:,.0f}"
                ])
            
            # Add top performers
            result_lines.extend([
                "\n🏆 TOP 10 BY MARKET CAP"
            ])
            
            for i, crypto in enumerate(top_cryptos[:10], 1):
                quote_data = crypto.quote.get(convert)
                if quote_data:
                    change_indicator = "📈" if quote_data.percent_change_24h > 0 else "📉"
                    result_lines.append(
                        f"{i:2d}. {crypto.symbol:6s} ${quote_data.price:12,.2f}  "
                        f"{change_indicator} {quote_data.percent_change_24h:+6.2f}%  "
                        f"Cap: ${quote_data.market_cap/1e9:6.2f}B"
                    )
            
            result_lines.append(f"\n⏰ Last Updated: {metrics.last_updated.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            
            response_text = "\n".join(result_lines)
            self.cache.set(cache_key, response_text)
            
            return [TextContent(type="text", text=response_text)]
        
        except Exception as e:
            logger.error(f"Error getting market statistics: {e}")
            return [TextContent(type="text", text=f"Error: {str(e)}")]
