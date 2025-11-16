"""
Example usage of the Cryptocurrency MCP Server.
"""

import asyncio
from datetime import datetime, timedelta


async def example_basic_usage():
    """Basic usage example."""
    print("=" * 70)
    print("EXAMPLE 1: Basic Cryptocurrency Price Query")
    print("=" * 70)
    
    # In a real MCP client, you would use:
    # result = await session.call_tool(
    #     "get_cryptocurrency_price",
    #     arguments={"symbols": "BTC,ETH,ADA"}
    # )
    
    print("""
    Tool: get_cryptocurrency_price
    Arguments: {"symbols": "BTC,ETH,ADA", "convert": "USD"}
    
    Expected Response:
    ------------------
    Cryptocurrency Prices (USD):
    ==================================================
    
    Bitcoin (BTC)
      Price: USD 50,000.00
      Market Cap: USD 950,000,000,000
      24h Volume: USD 30,000,000,000
      24h Change: +2.50%
      7d Change: +5.00%
      Market Cap Rank: #1
    
    Ethereum (ETH)
      Price: USD 3,000.00
      Market Cap: USD 360,000,000,000
      24h Volume: USD 15,000,000,000
      24h Change: +1.80%
      7d Change: +3.50%
      Market Cap Rank: #2
    """)


async def example_market_overview():
    """Market overview example."""
    print("=" * 70)
    print("EXAMPLE 2: Global Market Metrics")
    print("=" * 70)
    
    print("""
    Tool: get_global_metrics
    Arguments: {"convert": "USD"}
    
    Expected Response:
    ------------------
    Global Cryptocurrency Market Metrics:
    ==================================================
    
    Active Cryptocurrencies: 10,000
    Total Cryptocurrencies: 20,000
    Active Exchanges: 500
    Active Market Pairs: 50,000
    
    Total Market Cap: USD 2,000,000,000,000
    Total 24h Volume: USD 100,000,000,000
    BTC Dominance: 45.00%
    ETH Dominance: 18.50%
    
    DeFi Market Cap: USD 50,000,000,000
    DeFi 24h Volume: USD 5,000,000,000
    Stablecoin Market Cap: USD 150,000,000,000
    Stablecoin 24h Volume: USD 40,000,000,000
    """)


async def example_historical_data():
    """Historical data example."""
    print("=" * 70)
    print("EXAMPLE 3: Historical Price Data")
    print("=" * 70)
    
    print("""
    Tool: get_historical_data
    Arguments: {
        "symbol": "BTC",
        "count": 7,
        "interval": "daily",
        "convert": "USD"
    }
    
    Expected Response:
    ------------------
    Historical Price Data for BTC (USD):
    Interval: daily, Data Points: 7
    ================================================================================
    2024-01-01 00:00  Price: $   48,000.00  Volume: $ 28,000,000,000  Market Cap: $ 912,000,000,000
    2024-01-02 00:00  Price: $   49,500.00  Volume: $ 29,000,000,000  Market Cap: $ 940,500,000,000
    2024-01-03 00:00  Price: $   50,200.00  Volume: $ 30,500,000,000  Market Cap: $ 953,800,000,000
    2024-01-04 00:00  Price: $   49,800.00  Volume: $ 29,800,000,000  Market Cap: $ 946,200,000,000
    2024-01-05 00:00  Price: $   51,000.00  Volume: $ 31,000,000,000  Market Cap: $ 969,000,000,000
    2024-01-06 00:00  Price: $   50,500.00  Volume: $ 30,200,000,000  Market Cap: $ 959,500,000,000
    2024-01-07 00:00  Price: $   50,000.00  Volume: $ 30,000,000,000  Market Cap: $ 950,000,000,000
    """)


async def example_ohlcv_data():
    """OHLCV data example."""
    print("=" * 70)
    print("EXAMPLE 4: OHLCV Trading Data")
    print("=" * 70)
    
    print("""
    Tool: get_ohlcv_data
    Arguments: {
        "symbol": "ETH",
        "time_period": "daily",
        "count": 5,
        "convert": "USD"
    }
    
    Expected Response:
    ------------------
    OHLCV Data for ETH (USD):
    Period: daily, Intervals: 5
    ====================================================================================================
    Date                         Open         High          Low        Close           Volume
    ----------------------------------------------------------------------------------------------------
    2024-01-01 00:00      $  2,900.00  $  3,100.00  $  2,850.00  $  3,000.00  $ 14,500,000,000
    2024-01-02 00:00      $  3,000.00  $  3,150.00  $  2,980.00  $  3,100.00  $ 15,200,000,000
    2024-01-03 00:00      $  3,100.00  $  3,200.00  $  3,050.00  $  3,150.00  $ 15,800,000,000
    2024-01-04 00:00      $  3,150.00  $  3,250.00  $  3,100.00  $  3,180.00  $ 16,100,000,000
    2024-01-05 00:00      $  3,180.00  $  3,300.00  $  3,150.00  $  3,250.00  $ 16,500,000,000
    """)


async def example_search():
    """Search example."""
    print("=" * 70)
    print("EXAMPLE 5: Cryptocurrency Search")
    print("=" * 70)
    
    print("""
    Tool: search_cryptocurrencies
    Arguments: {"query": "bit", "limit": 5}
    
    Expected Response:
    ------------------
    Search Results for 'bit':
    Found 5 results
    ============================================================
    
    1. Bitcoin (BTC)
       ID: 1
       Rank: #1
       Status: Active
       Slug: bitcoin
    
    2. Bitcoin Cash (BCH)
       ID: 1831
       Rank: #20
       Status: Active
       Slug: bitcoin-cash
    
    3. Bitcoin SV (BSV)
       ID: 3602
       Rank: #45
       Status: Active
       Slug: bitcoin-sv
    """)


async def example_top_cryptocurrencies():
    """Top cryptocurrencies example."""
    print("=" * 70)
    print("EXAMPLE 6: Top Cryptocurrencies by Market Cap")
    print("=" * 70)
    
    print("""
    Tool: get_top_cryptocurrencies
    Arguments: {"limit": 10, "convert": "USD"}
    
    Expected Response:
    ------------------
    Top 10 Cryptocurrencies by Market Cap (USD):
    ================================================================================
      1. Bitcoin            (BTC   ) $   50,000.00  Cap: $  950.00B  24h:  +2.50%
      2. Ethereum           (ETH   ) $    3,000.00  Cap: $  360.00B  24h:  +1.80%
      3. Tether             (USDT  ) $        1.00  Cap: $   95.00B  24h:  +0.01%
      4. BNB                (BNB   ) $      400.00  Cap: $   62.00B  24h:  +0.75%
      5. Solana             (SOL   ) $      120.00  Cap: $   50.00B  24h:  +3.20%
      6. XRP                (XRP   ) $        0.60  Cap: $   32.00B  24h:  +1.50%
      7. USD Coin           (USDC  ) $        1.00  Cap: $   28.00B  24h:  +0.00%
      8. Cardano            (ADA   ) $        0.50  Cap: $   18.00B  24h:  +2.10%
      9. Dogecoin           (DOGE  ) $        0.08  Cap: $   11.00B  24h:  +4.50%
     10. TRON               (TRX   ) $        0.10  Cap: $    9.00B  24h:  +1.20%
    """)


async def example_market_statistics():
    """Market statistics example."""
    print("=" * 70)
    print("EXAMPLE 7: Comprehensive Market Statistics")
    print("=" * 70)
    
    print("""
    Tool: get_market_statistics
    Arguments: {"convert": "USD"}
    
    Expected Response:
    ------------------
    Cryptocurrency Market Statistics:
    ======================================================================
    
    📊 MARKET OVERVIEW
    Total Market Cap: USD 2,000,000,000,000
    24h Trading Volume: USD 100,000,000,000
    Volume/Market Cap Ratio: 5.00%
    Active Cryptocurrencies: 10,000
    Active Markets: 50,000
    Active Exchanges: 500
    
    📈 DOMINANCE
    Bitcoin (BTC): 45.00%
    Ethereum (ETH): 18.50%
    Altcoins: 36.50%
    
    💎 DeFi METRICS
    DeFi Market Cap: USD 50,000,000,000
    DeFi Dominance: 2.50%
    DeFi 24h Volume: USD 5,000,000,000
    
    💵 STABLECOIN METRICS
    Stablecoin Market Cap: USD 150,000,000,000
    Stablecoin Dominance: 7.50%
    Stablecoin 24h Volume: USD 40,000,000,000
    
    🏆 TOP 10 BY MARKET CAP
     1. BTC    $   50,000.00  📈  +2.50%  Cap: $950.00B
     2. ETH    $    3,000.00  📈  +1.80%  Cap: $360.00B
     3. USDT   $        1.00  📈  +0.01%  Cap: $ 95.00B
     4. BNB    $      400.00  📈  +0.75%  Cap: $ 62.00B
     5. SOL    $      120.00  📈  +3.20%  Cap: $ 50.00B
     6. XRP    $        0.60  📈  +1.50%  Cap: $ 32.00B
     7. USDC   $        1.00  📈  +0.00%  Cap: $ 28.00B
     8. ADA    $        0.50  📈  +2.10%  Cap: $ 18.00B
     9. DOGE   $        0.08  📈  +4.50%  Cap: $ 11.00B
    10. TRX    $        0.10  📈  +1.20%  Cap: $  9.00B
    
    ⏰ Last Updated: 2024-01-07 12:00:00 UTC
    """)


async def main():
    """Run all examples."""
    print("\n")
    print("*" * 70)
    print("*" + " " * 68 + "*")
    print("*" + "  CRYPTOCURRENCY MARKET DATA MCP SERVER - USAGE EXAMPLES  ".center(68) + "*")
    print("*" + " " * 68 + "*")
    print("*" * 70)
    print("\n")
    
    await example_basic_usage()
    await asyncio.sleep(1)
    
    await example_market_overview()
    await asyncio.sleep(1)
    
    await example_historical_data()
    await asyncio.sleep(1)
    
    await example_ohlcv_data()
    await asyncio.sleep(1)
    
    await example_search()
    await asyncio.sleep(1)
    
    await example_top_cryptocurrencies()
    await asyncio.sleep(1)
    
    await example_market_statistics()
    
    print("\n")
    print("=" * 70)
    print("For more information, see README.md")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
