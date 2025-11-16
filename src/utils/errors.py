"""
Custom exceptions for the cryptocurrency MCP server.
"""


class CryptoMCPError(Exception):
    """Base exception for all crypto MCP errors."""
    pass


class APIError(CryptoMCPError):
    """Base exception for API-related errors."""
    pass


class AuthenticationError(APIError):
    """Raised when API authentication fails."""
    def __init__(self, message="Invalid API key or authentication failed"):
        self.message = message
        super().__init__(self.message)


class RateLimitError(APIError):
    """Raised when API rate limit is exceeded."""
    def __init__(self, message="API rate limit exceeded", retry_after=None):
        self.message = message
        self.retry_after = retry_after
        super().__init__(self.message)


class APIConnectionError(APIError):
    """Raised when connection to API fails."""
    def __init__(self, message="Failed to connect to API"):
        self.message = message
        super().__init__(self.message)


class APITimeoutError(APIError):
    """Raised when API request times out."""
    def __init__(self, message="API request timed out"):
        self.message = message
        super().__init__(self.message)


class InvalidResponseError(APIError):
    """Raised when API returns invalid response."""
    def __init__(self, message="Invalid response from API"):
        self.message = message
        super().__init__(self.message)


class ValidationError(CryptoMCPError):
    """Raised when data validation fails."""
    def __init__(self, message="Data validation failed", errors=None):
        self.message = message
        self.errors = errors or []
        super().__init__(self.message)


class CacheError(CryptoMCPError):
    """Raised when cache operations fail."""
    pass


class ConfigurationError(CryptoMCPError):
    """Raised when configuration is invalid or missing."""
    def __init__(self, message="Invalid or missing configuration"):
        self.message = message
        super().__init__(self.message)


class CryptocurrencyNotFoundError(CryptoMCPError):
    """Raised when requested cryptocurrency is not found."""
    def __init__(self, symbol=None, message=None):
        if message is None:
            message = f"Cryptocurrency not found: {symbol}" if symbol else "Cryptocurrency not found"
        self.symbol = symbol
        self.message = message
        super().__init__(self.message)


class InvalidParameterError(CryptoMCPError):
    """Raised when invalid parameters are provided."""
    def __init__(self, parameter, message=None):
        if message is None:
            message = f"Invalid parameter: {parameter}"
        self.parameter = parameter
        self.message = message
        super().__init__(self.message)


def handle_api_error(status_code: int, response_data: dict) -> None:
    """
    Handle API errors based on status code and response data.
    
    Args:
        status_code: HTTP status code
        response_data: Response data from API
        
    Raises:
        Appropriate exception based on error type
    """
    error_message = response_data.get("status", {}).get("error_message", "Unknown error")
    
    if status_code == 401:
        raise AuthenticationError(error_message)
    elif status_code == 429:
        raise RateLimitError(error_message)
    elif status_code == 400:
        raise InvalidParameterError("request", error_message)
    elif status_code == 404:
        raise CryptocurrencyNotFoundError(message=error_message)
    elif status_code >= 500:
        raise APIConnectionError(f"Server error: {error_message}")
    else:
        raise APIError(f"API error (status {status_code}): {error_message}")
