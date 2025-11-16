"""
Data validation utilities for cryptocurrency data.
"""

import re
from typing import List, Optional, Union, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator, field_validator
from enum import Enum


class SortOrder(str, Enum):
    """Sort order enum."""
    ASC = "asc"
    DESC = "desc"


class TimeInterval(str, Enum):
    """Time interval enum for historical data."""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class ConvertCurrency(str, Enum):
    """Supported conversion currencies."""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"
    CNY = "CNY"
    BTC = "BTC"
    ETH = "ETH"


def validate_symbol(symbol: str) -> str:
    """
    Validate cryptocurrency symbol.
    
    Args:
        symbol: Cryptocurrency symbol
        
    Returns:
        Validated symbol
        
    Raises:
        ValueError: If symbol is invalid
    """
    if not symbol:
        raise ValueError("Symbol cannot be empty")
    
    # Remove whitespace and convert to uppercase
    symbol = symbol.strip().upper()
    
    # Check format (letters, numbers, hyphens allowed)
    if not re.match(r'^[A-Z0-9-]+$', symbol):
        raise ValueError(f"Invalid symbol format: {symbol}")
    
    if len(symbol) > 10:
        raise ValueError(f"Symbol too long: {symbol}")
    
    return symbol


def validate_symbols(symbols: Union[str, List[str]]) -> List[str]:
    """
    Validate multiple cryptocurrency symbols.
    
    Args:
        symbols: Single symbol or list of symbols
        
    Returns:
        List of validated symbols
    """
    if isinstance(symbols, str):
        symbols = [s.strip() for s in symbols.split(",")]
    
    return [validate_symbol(s) for s in symbols]


def validate_limit(limit: int, min_val: int = 1, max_val: int = 5000) -> int:
    """
    Validate limit parameter.
    
    Args:
        limit: Limit value
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        
    Returns:
        Validated limit
        
    Raises:
        ValueError: If limit is out of range
    """
    if not min_val <= limit <= max_val:
        raise ValueError(f"Limit must be between {min_val} and {max_val}")
    return limit


def validate_date(date_str: str) -> datetime:
    """
    Validate and parse date string.
    
    Args:
        date_str: Date string in ISO format
        
    Returns:
        Parsed datetime object
        
    Raises:
        ValueError: If date format is invalid
    """
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except ValueError as e:
        raise ValueError(f"Invalid date format: {date_str}. Use ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)")


class CryptocurrencyPriceRequest(BaseModel):
    """Request model for cryptocurrency price."""
    symbols: Union[str, List[str]] = Field(..., description="Cryptocurrency symbols")
    convert: str = Field(default="USD", description="Conversion currency")
    
    @field_validator('symbols')
    @classmethod
    def validate_symbols_field(cls, v):
        return validate_symbols(v)
    
    @field_validator('convert')
    @classmethod
    def validate_convert_field(cls, v):
        return v.upper()


class CryptocurrencyListRequest(BaseModel):
    """Request model for listing cryptocurrencies."""
    limit: int = Field(default=100, ge=1, le=5000, description="Number of results")
    start: int = Field(default=1, ge=1, description="Starting position")
    convert: str = Field(default="USD", description="Conversion currency")
    sort: str = Field(default="market_cap", description="Sort field")
    sort_dir: Optional[SortOrder] = Field(default=SortOrder.DESC, description="Sort direction")


class HistoricalDataRequest(BaseModel):
    """Request model for historical data."""
    symbol: str = Field(..., description="Cryptocurrency symbol")
    time_start: Optional[str] = Field(None, description="Start time (ISO format)")
    time_end: Optional[str] = Field(None, description="End time (ISO format)")
    count: int = Field(default=10, ge=1, le=10000, description="Number of data points")
    interval: Optional[TimeInterval] = Field(None, description="Time interval")
    convert: str = Field(default="USD", description="Conversion currency")
    
    @field_validator('symbol')
    @classmethod
    def validate_symbol_field(cls, v):
        return validate_symbol(v)
    
    @field_validator('time_start', 'time_end')
    @classmethod
    def validate_time_fields(cls, v):
        if v:
            validate_date(v)
        return v


class OHLCVRequest(BaseModel):
    """Request model for OHLCV data."""
    symbol: str = Field(..., description="Cryptocurrency symbol")
    time_period: str = Field(default="daily", description="Time period")
    time_start: Optional[str] = Field(None, description="Start time (ISO format)")
    time_end: Optional[str] = Field(None, description="End time (ISO format)")
    count: int = Field(default=10, ge=1, le=10000, description="Number of intervals")
    convert: str = Field(default="USD", description="Conversion currency")


class SearchRequest(BaseModel):
    """Request model for cryptocurrency search."""
    query: str = Field(..., min_length=1, description="Search query")
    limit: int = Field(default=10, ge=1, le=100, description="Number of results")


def validate_request_data(model_class: type[BaseModel], data: dict) -> BaseModel:
    """
    Validate request data using Pydantic model.
    
    Args:
        model_class: Pydantic model class
        data: Request data
        
    Returns:
        Validated model instance
        
    Raises:
        ValidationError: If validation fails
    """
    from src.utils.errors import ValidationError
    
    try:
        return model_class(**data)
    except Exception as e:
        raise ValidationError(str(e), errors=[str(e)])


def sanitize_parameters(params: dict) -> dict:
    """
    Sanitize request parameters by removing None values.
    
    Args:
        params: Parameters dictionary
        
    Returns:
        Sanitized parameters
    """
    return {k: v for k, v in params.items() if v is not None}
