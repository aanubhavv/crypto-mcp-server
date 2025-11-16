"""
Configuration management for the MCP server.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class ServerConfig(BaseSettings):
    """Server configuration."""
    
    # API Configuration
    coinmarketcap_api_key: str = Field(
        ...,
        description="CoinMarketCap API key"
    )
    coinmarketcap_base_url: str = Field(
        default="https://pro-api.coinmarketcap.com/v1",
        description="CoinMarketCap API base URL"
    )
    
    # Cache Configuration
    cache_ttl_seconds: int = Field(
        default=300,
        description="Cache TTL in seconds"
    )
    cache_max_size: int = Field(
        default=1000,
        description="Maximum cache size"
    )
    
    # Rate Limiting
    rate_limit_requests: int = Field(
        default=30,
        description="Number of requests per period"
    )
    rate_limit_period: int = Field(
        default=60,
        description="Rate limit period in seconds"
    )
    
    # Server Configuration
    log_level: str = Field(
        default="INFO",
        description="Logging level"
    )
    debug: bool = Field(
        default=False,
        description="Debug mode"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


def load_config() -> ServerConfig:
    """
    Load configuration from environment.
    
    Returns:
        ServerConfig instance
    """
    return ServerConfig()
