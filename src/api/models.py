"""
Data models for cryptocurrency API responses.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class Quote(BaseModel):
    """Quote model for cryptocurrency price data."""
    price: float = Field(..., description="Current price")
    volume_24h: Optional[float] = Field(None, description="24h trading volume")
    volume_change_24h: Optional[float] = Field(None, description="24h volume change percentage")
    percent_change_1h: Optional[float] = Field(None, description="1h price change percentage")
    percent_change_24h: Optional[float] = Field(None, description="24h price change percentage")
    percent_change_7d: Optional[float] = Field(None, description="7d price change percentage")
    percent_change_30d: Optional[float] = Field(None, description="30d price change percentage")
    market_cap: Optional[float] = Field(None, description="Market capitalization")
    market_cap_dominance: Optional[float] = Field(None, description="Market cap dominance")
    fully_diluted_market_cap: Optional[float] = Field(None, description="Fully diluted market cap")
    last_updated: Optional[datetime] = Field(None, description="Last update time")


class Platform(BaseModel):
    """Platform model for token information."""
    id: int
    name: str
    symbol: str
    slug: str
    token_address: str


class Cryptocurrency(BaseModel):
    """Cryptocurrency model."""
    id: int = Field(..., description="CoinMarketCap ID")
    name: str = Field(..., description="Cryptocurrency name")
    symbol: str = Field(..., description="Cryptocurrency symbol")
    slug: str = Field(..., description="URL slug")
    cmc_rank: Optional[int] = Field(None, description="CoinMarketCap rank")
    num_market_pairs: Optional[int] = Field(None, description="Number of market pairs")
    circulating_supply: Optional[float] = Field(None, description="Circulating supply")
    total_supply: Optional[float] = Field(None, description="Total supply")
    max_supply: Optional[float] = Field(None, description="Maximum supply")
    last_updated: Optional[datetime] = Field(None, description="Last update time")
    date_added: Optional[datetime] = Field(None, description="Date added to CMC")
    tags: Optional[List[str]] = Field(default_factory=list, description="Tags")
    platform: Optional[Platform] = Field(None, description="Platform info for tokens")
    quote: Optional[Dict[str, Quote]] = Field(default_factory=dict, description="Price quotes")


class CryptocurrencyInfo(BaseModel):
    """Detailed cryptocurrency information."""
    id: int
    name: str
    symbol: str
    category: Optional[str] = None
    description: Optional[str] = None
    slug: str
    logo: Optional[str] = None
    subreddit: Optional[str] = None
    notice: Optional[str] = None
    tags: Optional[List[str]] = Field(default_factory=list)
    tag_names: Optional[List[str]] = Field(default_factory=list)
    tag_groups: Optional[List[str]] = Field(default_factory=list)
    urls: Optional[Dict[str, List[str]]] = Field(default_factory=dict)
    platform: Optional[Platform] = None
    date_added: Optional[datetime] = None
    twitter_username: Optional[str] = None
    is_hidden: Optional[int] = 0


class GlobalMetrics(BaseModel):
    """Global cryptocurrency market metrics."""
    active_cryptocurrencies: int
    total_cryptocurrencies: int
    active_market_pairs: int
    active_exchanges: int
    total_exchanges: int
    eth_dominance: float
    btc_dominance: float
    defi_volume_24h: Optional[float] = None
    defi_market_cap: Optional[float] = None
    stablecoin_volume_24h: Optional[float] = None
    stablecoin_market_cap: Optional[float] = None
    derivatives_volume_24h: Optional[float] = None
    quote: Dict[str, Any]
    last_updated: datetime


class HistoricalQuote(BaseModel):
    """Historical quote data point."""
    timestamp: datetime = Field(..., description="Data point timestamp")
    quote: Dict[str, Quote] = Field(..., description="Price quotes")


class OHLCVData(BaseModel):
    """OHLCV (Open, High, Low, Close, Volume) data point."""
    time_open: datetime = Field(..., description="Opening time")
    time_close: datetime = Field(..., description="Closing time")
    time_high: Optional[datetime] = Field(None, description="High time")
    time_low: Optional[datetime] = Field(None, description="Low time")
    quote: Dict[str, Dict[str, float]] = Field(..., description="OHLCV quote data")


class APIStatus(BaseModel):
    """API status information."""
    timestamp: datetime
    error_code: int
    error_message: Optional[str] = None
    elapsed: int
    credit_count: int
    notice: Optional[str] = None


class APIResponse(BaseModel):
    """Generic API response wrapper."""
    status: APIStatus
    data: Any


class SearchResult(BaseModel):
    """Search result model."""
    id: int
    name: str
    symbol: str
    slug: str
    rank: Optional[int] = None
    is_active: int = 1


def parse_cryptocurrency_data(data: Dict[str, Any]) -> Cryptocurrency:
    """
    Parse cryptocurrency data from API response.
    
    Args:
        data: Raw API data
        
    Returns:
        Cryptocurrency model instance
    """
    return Cryptocurrency(**data)


def parse_cryptocurrency_list(data: List[Dict[str, Any]]) -> List[Cryptocurrency]:
    """
    Parse list of cryptocurrencies from API response.
    
    Args:
        data: Raw API data list
        
    Returns:
        List of Cryptocurrency model instances
    """
    return [Cryptocurrency(**item) for item in data]


def parse_global_metrics(data: Dict[str, Any]) -> GlobalMetrics:
    """
    Parse global metrics from API response.
    
    Args:
        data: Raw API data
        
    Returns:
        GlobalMetrics model instance
    """
    return GlobalMetrics(**data)
