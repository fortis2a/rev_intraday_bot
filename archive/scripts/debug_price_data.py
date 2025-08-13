#!/usr/bin/env python3
"""
Debug Price Data Source - Find out where the incorrect price/spread is coming from
"""

import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from config import config
from core.data_manager import DataManager

def debug_price_data():
    print("🔍 DEBUGGING PRICE DATA SOURCE")
    print("=" * 60)
    
    dm = DataManager()
    
    # Test PG specifically since that's showing the false data
    symbol = "PG"
    
    print(f"🧪 Investigating {symbol} price data...")
    print("-" * 60)
    
    try:
        # Get current market data and examine the raw response
        print("📊 Calling get_current_market_data...")
        data = dm.get_current_market_data(symbol, force_fresh=True)
        
        if data:
            print(f"✅ Data received for {symbol}:")
            print(f"   💰 Price: ${data['price']:.2f}")
            print(f"   📈 Bid: ${data.get('bid', 'N/A')}")
            print(f"   📉 Ask: ${data.get('ask', 'N/A')}")
            print(f"   📊 Spread: {data['spread_pct']:.3f}%")
            print(f"   📦 Volume: {data.get('volume', 'N/A'):,}")
            print(f"   🕐 Timestamp: {data.get('timestamp', 'N/A')}")
            
            # Check if this is coming from cache or live data
            print(f"\n🔍 Data source analysis:")
            if hasattr(dm, 'alpaca_trader') and dm.alpaca_trader:
                print("   📡 Using Alpaca API connection")
                
                # Try to get raw Alpaca data directly
                try:
                    from alpaca.data.requests import StockLatestQuoteRequest
                    from alpaca.data.historical import StockHistoricalDataClient
                    
                    # Get raw quote data
                    quote_request = StockLatestQuoteRequest(symbol_or_symbols=symbol)
                    quotes = dm.alpaca_trader.data_client.get_stock_latest_quote(quote_request)
                    
                    if symbol in quotes:
                        raw_quote = quotes[symbol]
                        print(f"   🎯 RAW Alpaca Quote:")
                        print(f"      Bid: ${raw_quote.bid_price:.2f} (size: {raw_quote.bid_size})")
                        print(f"      Ask: ${raw_quote.ask_price:.2f} (size: {raw_quote.ask_size})")
                        print(f"      Timestamp: {raw_quote.timestamp}")
                        
                        # Calculate spread manually
                        if raw_quote.bid_price > 0 and raw_quote.ask_price > 0:
                            mid_price = (raw_quote.bid_price + raw_quote.ask_price) / 2
                            spread_pct = ((raw_quote.ask_price - raw_quote.bid_price) / mid_price) * 100
                            print(f"      Mid Price: ${mid_price:.2f}")
                            print(f"      Calculated Spread: {spread_pct:.3f}%")
                        else:
                            print(f"      ❌ Invalid bid/ask prices!")
                
                except Exception as e:
                    print(f"   ❌ Error getting raw Alpaca data: {e}")
            else:
                print("   ❌ No Alpaca connection found")
                
        else:
            print(f"❌ No data returned for {symbol}")
            
        # Check what the current real market price should be
        print(f"\n🌐 For comparison, check current market price manually:")
        print(f"   Go to: https://finance.yahoo.com/quote/{symbol}")
        print(f"   Or: https://www.google.com/finance/quote/{symbol}:NYSE")
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_price_data()
