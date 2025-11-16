# Cryptocurrency Market Data MCP Server

A robust Python-based Model Context Protocol (MCP) server for retrieving real-time and historical cryptocurrency market data from CoinMarketCap API.

## Features

### Core MCP Features
- **Real-time Data Fetching**: Get current prices, market caps, and trading volumes
- **Historical Queries**: Access historical price data and OHLCV information
- **Market Analytics**: Retrieve top cryptocurrencies, trending coins, and market statistics
- **Global Market Metrics**: Get overall cryptocurrency market data

### Advanced Features
- **Intelligent Caching**: TTL-based caching to minimize API calls
- **Rate Limiting**: Built-in rate limiting to respect API quotas
- **Error Handling**: Comprehensive error handling and retry mechanisms
- **Data Validation**: Pydantic models for data validation
- **Async Support**: Fully asynchronous implementation for high performance

## Installation

1. Clone the repository:
```bash
cd d:\Programming\Python\internshala\project
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
copy .env.example .env
# Edit .env and add your CoinMarketCap API key
```

## Configuration

Get your free API key from [CoinMarketCap](https://coinmarketcap.com/api/) and add it to your `.env` file:

```
COINMARKETCAP_API_KEY=your_actual_api_key_here
```

## Usage

### Starting the Server

```bash
python -m src.server
```

### Available Tools

1. **get_cryptocurrency_price**: Get real-time price for specific cryptocurrencies
2. **get_cryptocurrency_info**: Get detailed information about cryptocurrencies
3. **get_top_cryptocurrencies**: List top cryptocurrencies by market cap
4. **get_historical_data**: Retrieve historical price data
5. **get_ohlcv_data**: Get OHLCV (Open, High, Low, Close, Volume) data
6. **get_global_metrics**: Get global cryptocurrency market metrics
7. **search_cryptocurrencies**: Search for cryptocurrencies by name or symbol

### Example Usage with MCP Client

```python
# Example client code
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "src.server"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Get Bitcoin price
            result = await session.call_tool(
                "get_cryptocurrency_price",
                arguments={"symbols": "BTC"}
            )
            print(result)
```

## Project Structure

```
project/
├── src/
│   ├── __init__.py
│   ├── server.py           # Main MCP server
│   ├── api/
│   │   ├── __init__.py
│   │   ├── client.py       # CoinMarketCap API client
│   │   └── models.py       # Data models
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── realtime.py     # Real-time data tools
│   │   ├── historical.py   # Historical data tools
│   │   └── analytics.py    # Analytics tools
│   └── utils/
│       ├── __init__.py
│       ├── cache.py        # Caching utilities
│       ├── errors.py       # Error handling
│       └── validators.py   # Data validators
├── tests/
│   ├── __init__.py
│   ├── test_server.py
│   ├── test_api_client.py
│   ├── test_tools.py
│   └── test_utils.py
├── requirements.txt
├── .env.example
└── README.md
```

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_api_client.py -v
```

## API Rate Limits

The free CoinMarketCap API tier includes:
- 10,000 credits per month
- ~333 credits per day
- Rate limiting is handled automatically by the server

## Error Handling

The server includes comprehensive error handling for:
- API authentication errors
- Rate limit exceeded
- Network timeouts
- Invalid parameters
- Data validation errors

## Development

### Running Tests
```bash
pytest -v
```

### Code Formatting
```bash
black src/ tests/
```

### Type Checking
```bash
mypy src/
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
