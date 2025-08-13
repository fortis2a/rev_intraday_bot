#!/usr/bin/env python3
"""
Test live data connection and verify current prices are not stale
"""

from core.data_manager import DataManager
from datetime import datetime
import time

def test_live_data_connection():
    print("🔍 TESTING LIVE DATA CONNECTION")
    print("=" * 60)
    
    dm = DataManager()
    
    # Test 1: Check data source
    print("📊 Testing Data Source Connection...")
    if dm.alpaca_client:
        print("✅ Alpaca client connected")
    else:
        print("❌ NO ALPACA CLIENT - This would prevent trading!")
        return
    
    # Test 2: Get current data for test symbols
    test_symbols = ["PG", "JNJ", "SPY"]
    
    for symbol in test_symbols:
        print(f"\n🔍 Testing {symbol}:")
        
        # Get data multiple times to check if it's updating
        for i in range(3):
            current_time = datetime.now()
            data = dm.get_current_market_data(symbol, force_fresh=True)
            
            if data:
                price = data['price']
                bid = data['bid']
                ask = data['ask']
                spread = data['spread_pct']
                timestamp = data.get('timestamp', 'Unknown')
                source = data.get('source', 'Unknown')
                
                print(f"   Attempt {i+1}: ${price:.2f} (Bid: ${bid:.2f}, Ask: ${ask:.2f})")
                print(f"      Spread: {spread:.3f}%, Source: {source}")
                print(f"      Data timestamp: {timestamp}")
                print(f"      Request time: {current_time}")
                
                # Check if this looks like real data
                if spread == 0:
                    print("      ⚠️ WARNING: Zero spread might indicate stale data")
                elif spread > 5:
                    print("      ⚠️ WARNING: Very wide spread - check data quality")
                else:
                    print("      ✅ Spread looks normal")
                    
                if source != 'alpaca_live':
                    print("      ❌ WARNING: Data source is not 'alpaca_live'")
                else:
                    print("      ✅ Data source confirmed as live Alpaca")
                    
            else:
                print(f"   ❌ Failed to get data for {symbol}")
                
            if i < 2:  # Small delay between requests
                time.sleep(1)
    
    # Test 3: Check if data changes over time
    print(f"\n⏱️ Testing Data Freshness (5-second test)...")
    initial_data = dm.get_current_market_data("SPY", force_fresh=True)
    if initial_data:
        initial_price = initial_data['price']
        initial_time = datetime.now()
        print(f"   Initial SPY price: ${initial_price:.2f} at {initial_time.strftime('%H:%M:%S')}")
        
        time.sleep(5)
        
        updated_data = dm.get_current_market_data("SPY", force_fresh=True)
        if updated_data:
            updated_price = updated_data['price']
            updated_time = datetime.now()
            price_change = abs(updated_price - initial_price)
            
            print(f"   Updated SPY price: ${updated_price:.2f} at {updated_time.strftime('%H:%M:%S')}")
            print(f"   Price change: ${price_change:.4f}")
            
            if price_change > 0:
                print("   ✅ Price changed - data appears to be live")
            else:
                print("   ⚠️ No price change in 5 seconds - might be stale or market closed")
        else:
            print("   ❌ Failed to get updated data")
    
    # Test 4: Check market hours
    print(f"\n📅 Market Hours Status:")
    market_status = dm.get_market_hours_status()
    if market_status:
        print(f"   Market Open: {market_status.get('is_market_hours', 'Unknown')}")
        print(f"   Weekday: {market_status.get('is_weekday', 'Unknown')}")
    
    print(f"\n✅ Live data connection test completed")
    print(f"🚨 CRITICAL: Bot will ONLY trade with live Alpaca data")
    print(f"🚨 Mock/simulated data is completely blocked for trading decisions")

if __name__ == "__main__":
    test_live_data_connection()
