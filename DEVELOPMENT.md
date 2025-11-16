# Cryptocurrency Market Data MCP Server - Development Guide

## Setup

### 1. Create Virtual Environment

```bash
python -m venv venv
```

### 2. Activate Virtual Environment

Windows:
```cmd
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
copy .env.example .env
```

Edit `.env` and add your CoinMarketCap API key:
```
COINMARKETCAP_API_KEY=your_actual_api_key_here
```

## Running the Server

### Development Mode

```bash
python -m src.server
```

### With Debugging

Set `DEBUG=True` in `.env` and run:
```bash
python -m src.server
```

## Testing

### Run All Tests

```bash
pytest
```

### Run with Coverage

```bash
pytest --cov=src --cov-report=html
```

### Run Specific Test File

```bash
pytest tests/test_api_client.py -v
```

### Run Specific Test

```bash
pytest tests/test_api_client.py::TestCoinMarketCapClient::test_client_initialization -v
```

## Code Quality

### Format Code

```bash
black src/ tests/
```

### Check Code Style

```bash
flake8 src/ tests/
```

### Type Checking

```bash
mypy src/
```

## Project Structure

```
project/
├── src/                    # Source code
│   ├── api/               # API client and models
│   │   ├── client.py      # CoinMarketCap API client
│   │   └── models.py      # Data models
│   ├── tools/             # MCP tools
│   │   ├── realtime.py    # Real-time data tools
│   │   ├── historical.py  # Historical data tools
│   │   └── analytics.py   # Analytics tools
│   ├── utils/             # Utilities
│   │   ├── cache.py       # Caching
│   │   ├── errors.py      # Error handling
│   │   └── validators.py  # Data validation
│   ├── config.py          # Configuration
│   └── server.py          # Main server
├── tests/                 # Test suite
│   ├── test_api_client.py
│   ├── test_tools.py
│   ├── test_utils.py
│   └── test_server.py
├── examples/              # Usage examples
├── requirements.txt       # Dependencies
├── .env.example          # Environment template
└── README.md             # Documentation
```

## API Tools

### Real-time Data Tools
1. `get_cryptocurrency_price` - Get current prices
2. `get_cryptocurrency_info` - Get detailed info
3. `get_top_cryptocurrencies` - Get top by market cap
4. `get_global_metrics` - Get global market data

### Historical Data Tools
1. `get_historical_data` - Get historical prices
2. `get_ohlcv_data` - Get OHLCV trading data

### Analytics Tools
1. `search_cryptocurrencies` - Search cryptocurrencies
2. `get_market_statistics` - Get market analytics

## Common Issues

### API Key Issues
- Make sure your API key is valid
- Check that `.env` file exists and has the correct format
- Verify the API key has sufficient credits

### Rate Limiting
- Free tier: 10,000 credits/month (~333/day)
- Adjust `RATE_LIMIT_REQUESTS` and `RATE_LIMIT_PERIOD` in `.env`
- Server automatically handles rate limiting

### Cache Issues
- Clear cache: delete cache files or restart server
- Adjust `CACHE_TTL_SECONDS` for different caching behavior

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run test suite
6. Submit pull request

## Support

For issues and questions:
- Check the documentation
- Review test examples
- Check API documentation: https://coinmarketcap.com/api/documentation/v1/
