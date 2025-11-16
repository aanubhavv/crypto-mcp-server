"""
Main MCP server for cryptocurrency market data.
"""

import os
import logging
import asyncio
from typing import Any
from dotenv import load_dotenv

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent

from src.api.client import CoinMarketCapClient
from src.utils.cache import CryptoCache
from src.utils.errors import CryptoMCPError
from src.tools.realtime import RealtimeTools
from src.tools.historical import HistoricalTools
from src.tools.analytics import AnalyticsTools

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CryptoMCPServer:
    """
    Main MCP server for cryptocurrency market data.
    """
    
    def __init__(self):
        """Initialize the MCP server."""
        self.server = Server("cryptocurrency-market-data")
        self.api_client: CoinMarketCapClient = None
        self.cache: CryptoCache = None
        self.realtime_tools: RealtimeTools = None
        self.historical_tools: HistoricalTools = None
        self.analytics_tools: AnalyticsTools = None
        
        logger.info("Initialized CryptoMCPServer")
        
        # Register handlers
        self._register_handlers()
    
    def _register_handlers(self):
        """Register MCP protocol handlers."""
        
        @self.server.list_resources()
        async def list_resources() -> list[Resource]:
            """List available resources."""
            return [
                Resource(
                    uri="crypto://info",
                    name="Cryptocurrency Market Data Server",
                    description="Real-time and historical cryptocurrency market data from CoinMarketCap",
                    mimeType="text/plain"
                ),
                Resource(
                    uri="crypto://cache/stats",
                    name="Cache Statistics",
                    description="View cache performance statistics",
                    mimeType="application/json"
                )
            ]
        
        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            """Read resource content."""
            if uri == "crypto://info":
                return self._get_server_info()
            elif uri == "crypto://cache/stats":
                import json
                return json.dumps(self.cache.get_stats(), indent=2)
            else:
                raise ValueError(f"Unknown resource: {uri}")
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available tools."""
            tools = []
            
            if self.realtime_tools:
                tools.extend(self.realtime_tools.get_tool_definitions())
            if self.historical_tools:
                tools.extend(self.historical_tools.get_tool_definitions())
            if self.analytics_tools:
                tools.extend(self.analytics_tools.get_tool_definitions())
            
            logger.info(f"Listed {len(tools)} tools")
            return tools
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> list[TextContent]:
            """Call a tool with given arguments."""
            logger.info(f"Calling tool: {name} with arguments: {arguments}")
            
            try:
                # Realtime tools
                if name == "get_cryptocurrency_price":
                    return await self.realtime_tools.get_cryptocurrency_price(**arguments)
                elif name == "get_cryptocurrency_info":
                    return await self.realtime_tools.get_cryptocurrency_info(**arguments)
                elif name == "get_top_cryptocurrencies":
                    return await self.realtime_tools.get_top_cryptocurrencies(**arguments)
                elif name == "get_global_metrics":
                    return await self.realtime_tools.get_global_metrics(**arguments)
                
                # Historical tools
                elif name == "get_historical_data":
                    return await self.historical_tools.get_historical_data(**arguments)
                elif name == "get_ohlcv_data":
                    return await self.historical_tools.get_ohlcv_data(**arguments)
                
                # Analytics tools
                elif name == "search_cryptocurrencies":
                    return await self.analytics_tools.search_cryptocurrencies(**arguments)
                elif name == "get_market_statistics":
                    return await self.analytics_tools.get_market_statistics(**arguments)
                
                else:
                    raise ValueError(f"Unknown tool: {name}")
            
            except CryptoMCPError as e:
                logger.error(f"Tool error: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
            except Exception as e:
                logger.error(f"Unexpected error in tool {name}: {e}", exc_info=True)
                return [TextContent(type="text", text=f"Unexpected error: {str(e)}")]
    
    def _get_server_info(self) -> str:
        """Get server information."""
        return """
Cryptocurrency Market Data MCP Server
=====================================

Version: 1.0.0
Provider: CoinMarketCap API

Available Features:
- Real-time cryptocurrency prices and market data
- Top cryptocurrencies by market cap
- Global market metrics and statistics
- Historical price data
- OHLCV (Open, High, Low, Close, Volume) data
- Cryptocurrency search and information
- Market analytics and trends

Data includes:
- Price in multiple currencies
- Market capitalization
- Trading volume (24h)
- Price changes (1h, 24h, 7d, 30d)
- Supply information
- Market dominance
- DeFi and stablecoin metrics

Cache Status:
- Enabled with TTL-based caching
- Reduces API calls and improves performance
- Use crypto://cache/stats to view statistics

Rate Limiting:
- Automatically managed to respect API quotas
- Exponential backoff on errors
- Retry mechanism for transient failures
"""
    
    async def initialize(self):
        """Initialize server components."""
        logger.info("Initializing server components...")
        
        # Initialize cache
        cache_ttl = int(os.getenv("CACHE_TTL_SECONDS", "300"))
        cache_size = int(os.getenv("CACHE_MAX_SIZE", "1000"))
        self.cache = CryptoCache(ttl_seconds=cache_ttl, max_size=cache_size)
        
        # Initialize API client
        rate_limit_requests = int(os.getenv("RATE_LIMIT_REQUESTS", "30"))
        rate_limit_period = int(os.getenv("RATE_LIMIT_PERIOD", "60"))
        
        self.api_client = CoinMarketCapClient(
            rate_limit_requests=rate_limit_requests,
            rate_limit_period=rate_limit_period
        )
        
        # Initialize tools
        self.realtime_tools = RealtimeTools(self.api_client, self.cache)
        self.historical_tools = HistoricalTools(self.api_client, self.cache)
        self.analytics_tools = AnalyticsTools(self.api_client, self.cache)
        
        logger.info("Server components initialized successfully")
    
    async def cleanup(self):
        """Cleanup server resources."""
        logger.info("Cleaning up server resources...")
        
        if self.api_client:
            await self.api_client.close()
        
        if self.cache:
            stats = self.cache.get_stats()
            logger.info(f"Final cache stats: {stats}")
        
        logger.info("Cleanup complete")
    
    async def run(self):
        """Run the MCP server."""
        try:
            await self.initialize()
            
            async with stdio_server() as (read_stream, write_stream):
                logger.info("MCP server running on stdio")
                await self.server.run(
                    read_stream,
                    write_stream,
                    self.server.create_initialization_options()
                )
        
        except KeyboardInterrupt:
            logger.info("Server interrupted by user")
        except Exception as e:
            logger.error(f"Server error: {e}", exc_info=True)
            raise
        finally:
            await self.cleanup()


async def main():
    """Main entry point."""
    server = CryptoMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
