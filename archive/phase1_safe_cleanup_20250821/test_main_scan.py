#!/usr/bin/env python3
"""
Test signal scanning exactly like main.py does it
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import IntradayEngine
from config import config

def test_main_scan():
    """Test the exact scan_for_signals method from main.py"""
    
    print("Testing main.py scan_for_signals method...")
    print("-" * 50)
    
    # Initialize the bot
    bot = IntradayEngine()
    
    # Call the exact same scan method
    signals = bot.scan_for_signals()
    
    print(f"Found {len(signals)} signals:")
    
    for i, signal in enumerate(signals):
        print(f"  {i+1}. {signal['symbol']} {signal['action']} - {signal['reason']}")
        print(f"     Confidence: {signal['confidence']:.2f}")
        if 'price' in signal:
            print(f"     Price: ${signal['price']:.2f}")
        else:
            print(f"     No price in signal")
    
    if not signals:
        print("  No signals found - investigating why...")
        
        # Debug each symbol manually
        print("\nDebugging each symbol in watchlist:")
        for symbol in config['INTRADAY_WATCHLIST'][:5]:  # Check first 5
            print(f"\n--- Debugging {symbol} ---")
            
            try:
                # Get data like main.py does
                df = bot.data_manager.get_bars(symbol, config['TIMEFRAME'])
                if df.empty or len(df) < 26:
                    print(f"  ❌ Insufficient data: {len(df) if not df.empty else 0} bars")
                    continue
                
                print(f"  ✅ Data: {len(df)} bars")
                
                # Calculate indicators
                df = bot.data_manager.calculate_indicators(df)
                print(f"  ✅ Indicators calculated")
                
                # Check price limits
                current_price = df.iloc[-1]['close']
                print(f"  📊 Price: ${current_price:.2f} (limits: ${config['MIN_PRICE']}-${config['MAX_PRICE']})")
                
                if current_price < config['MIN_PRICE'] or current_price > config['MAX_PRICE']:
                    print(f"  ❌ Price outside limits")
                    continue
                
                # Test each strategy
                for strategy_name, strategy_class in bot.strategy_classes.items():
                    print(f"  Testing {strategy_name} strategy...")
                    try:
                        strategy = strategy_class(symbol)
                        signal = strategy.generate_signal(symbol, df)
                        if signal:
                            print(f"    🚀 {strategy_name.upper()} SIGNAL: {signal['action']} - {signal['reason']}")
                        else:
                            print(f"    ⭕ No {strategy_name} signal")
                    except Exception as e:
                        print(f"    ❌ {strategy_name} error: {e}")
                        
            except Exception as e:
                print(f"  ❌ Error with {symbol}: {e}")

if __name__ == "__main__":
    test_main_scan()
