# API Documentation

## CoinMarketCap MCP Server API Reference

### Overview

The Cryptocurrency Market Data MCP Server provides 8 tools for accessing real-time and historical cryptocurrency market data through the Model Context Protocol.

---

## Real-time Data Tools

### 1. get_cryptocurrency_price

Get real-time price and market data for specific cryptocurrencies.

**Input Schema:**
```json
{
  "symbols": "string (required)",
  "convert": "string (optional, default: USD)"
}
```

**Parameters:**
- `symbols`: Comma-separated cryptocurrency symbols (e.g., "BTC,ETH,ADA")
- `convert`: Currency to convert to (USD, EUR, GBP, etc.)

**Example:**
```json
{
  "symbols": "BTC,ETH",
  "convert": "USD"
}
```

**Response Fields:**
- Cryptocurrency name and symbol
- Current price
- Market capitalization
- 24h trading volume
- Price changes (1h, 24h, 7d)
- Market cap rank

---

### 2. get_cryptocurrency_info

Get detailed information about cryptocurrencies including description, website, and social links.

**Input Schema:**
```json
{
  "symbols": "string (required)"
}
```

**Parameters:**
- `symbols`: Comma-separated cryptocurrency symbols

**Example:**
```json
{
  "symbols": "BTC,ETH"
}
```

**Response Fields:**
- Name and symbol
- Category
- Description
- Website URL
- Twitter handle
- Tags
- Date added

---

### 3. get_top_cryptocurrencies

Get top cryptocurrencies ranked by market capitalization.

**Input Schema:**
```json
{
  "limit": "number (optional, default: 100)",
  "convert": "string (optional, default: USD)"
}
```

**Parameters:**
- `limit`: Number of cryptocurrencies to return (1-5000)
- `convert`: Currency to convert to

**Example:**
```json
{
  "limit": 50,
  "convert": "USD"
}
```

**Response Fields:**
- Rank, name, symbol
- Current price
- Market cap
- 24h price change

---

### 4. get_global_metrics

Get global cryptocurrency market metrics.

**Input Schema:**
```json
{
  "convert": "string (optional, default: USD)"
}
```

**Parameters:**
- `convert`: Currency to convert to

**Example:**
```json
{
  "convert": "USD"
}
```

**Response Fields:**
- Total market cap
- Total 24h volume
- BTC/ETH dominance
- Active cryptocurrencies
- Active exchanges
- DeFi metrics
- Stablecoin metrics

---

## Historical Data Tools

### 5. get_historical_data

Get historical price data for a cryptocurrency.

**Input Schema:**
```json
{
  "symbol": "string (required)",
  "time_start": "string (optional)",
  "time_end": "string (optional)",
  "count": "number (optional, default: 10)",
  "interval": "string (optional, default: daily)",
  "convert": "string (optional, default: USD)"
}
```

**Parameters:**
- `symbol`: Cryptocurrency symbol
- `time_start`: Start time in ISO format (e.g., "2024-01-01")
- `time_end`: End time in ISO format
- `count`: Number of data points (1-10000)
- `interval`: Time interval (hourly, daily, weekly, monthly)
- `convert`: Currency to convert to

**Example:**
```json
{
  "symbol": "BTC",
  "time_start": "2024-01-01",
  "time_end": "2024-01-31",
  "interval": "daily",
  "convert": "USD"
}
```

**Response Fields:**
- Timestamp
- Price
- Volume
- Market cap

---

### 6. get_ohlcv_data

Get OHLCV (Open, High, Low, Close, Volume) historical data.

**Input Schema:**
```json
{
  "symbol": "string (required)",
  "time_period": "string (optional, default: daily)",
  "time_start": "string (optional)",
  "time_end": "string (optional)",
  "count": "number (optional, default: 10)",
  "convert": "string (optional, default: USD)"
}
```

**Parameters:**
- `symbol`: Cryptocurrency symbol
- `time_period`: Time period (hourly, daily, weekly, monthly)
- `time_start`: Start time in ISO format
- `time_end`: End time in ISO format
- `count`: Number of intervals (1-10000)
- `convert`: Currency to convert to

**Example:**
```json
{
  "symbol": "ETH",
  "time_period": "daily",
  "count": 30,
  "convert": "USD"
}
```

**Response Fields:**
- Open time/close time
- Open, High, Low, Close prices
- Trading volume

---

## Analytics Tools

### 7. search_cryptocurrencies

Search for cryptocurrencies by name or symbol.

**Input Schema:**
```json
{
  "query": "string (required)",
  "limit": "number (optional, default: 10)"
}
```

**Parameters:**
- `query`: Search query (name or symbol)
- `limit`: Maximum number of results (1-100)

**Example:**
```json
{
  "query": "bitcoin",
  "limit": 5
}
```

**Response Fields:**
- ID, name, symbol
- Rank
- Status (active/inactive)
- Slug

---

### 8. get_market_statistics

Get comprehensive market statistics and analytics.

**Input Schema:**
```json
{
  "convert": "string (optional, default: USD)"
}
```

**Parameters:**
- `convert`: Currency to convert to

**Example:**
```json
{
  "convert": "USD"
}
```

**Response Fields:**
- Market overview (total cap, volume, ratios)
- Dominance statistics
- DeFi metrics
- Stablecoin metrics
- Top performers

---

## Error Handling

All tools return errors in a consistent format:

```
Error: <error_message>
```

### Common Errors

1. **Authentication Error**: Invalid or missing API key
2. **Rate Limit Error**: Too many requests
3. **Validation Error**: Invalid parameters
4. **Not Found Error**: Cryptocurrency not found
5. **Connection Error**: Network/API issues

---

## Rate Limits

- Free tier: 10,000 credits/month (~333 per day)
- Server automatically manages rate limiting
- Exponential backoff on errors
- Configurable via environment variables

---

## Caching

- TTL-based caching (default: 5 minutes)
- Reduces API calls
- Improves performance
- Configurable cache size and TTL

---

## Resources

The server exposes two resources:

1. `crypto://info` - Server information
2. `crypto://cache/stats` - Cache statistics

---

## Support

For more information:
- CoinMarketCap API Docs: https://coinmarketcap.com/api/documentation/v1/
- GitHub: [Your repository URL]
- Issues: [Your issues URL]
