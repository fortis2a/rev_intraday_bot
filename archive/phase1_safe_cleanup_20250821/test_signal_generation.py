#!/usr/bin/env python3
"""
Test signal generation for debugging
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.data_manager import DataManager
from strategies import MomentumStrategy, MeanReversionStrategy
from config import config
import pandas as pd

def test_signal_generation():
    """Test signal generation for symbols without positions"""
    
    # Initialize data manager
    data_manager = DataManager()
    
    # Test symbols that don't have positions (avoid SOXL and INTC)
    test_symbols = ['SOFI', 'TQQQ', 'NIO', 'SPXU', 'TNA']
    
    print("Testing signal generation...")
    print(f"Testing symbols: {test_symbols}")
    print("-" * 50)
    
    for symbol in test_symbols:
        print(f"\nTesting {symbol}:")
        
        try:
            # Get market data
            df = data_manager.get_bars(symbol, config['TIMEFRAME'])
            if df.empty or len(df) < 26:
                print(f"  ❌ Insufficient data: {len(df) if not df.empty else 0} bars")
                continue
            
            print(f"  ✅ Got {len(df)} bars of data")
            
            # Calculate indicators
            df = data_manager.calculate_indicators(df)
            print(f"  ✅ Calculated indicators")
            
            # Check current price
            current_price = df.iloc[-1]['close']
            print(f"  📊 Current price: ${current_price:.2f}")
            
            if current_price < config['MIN_PRICE'] or current_price > config['MAX_PRICE']:
                print(f"  ❌ Price outside limits (${config['MIN_PRICE']}-${config['MAX_PRICE']})")
                continue
            
            # Initialize strategies for this symbol
            momentum_strategy = MomentumStrategy(symbol)
            mean_reversion_strategy = MeanReversionStrategy(symbol)
            
            # Test momentum strategy
            try:
                momentum_signal = momentum_strategy.generate_signal(symbol, df)
                if momentum_signal:
                    print(f"  🚀 MOMENTUM SIGNAL: {momentum_signal['action']} - {momentum_signal['reason']}")
                else:
                    print(f"  ⭕ No momentum signal")
            except Exception as e:
                print(f"  ❌ Momentum strategy error: {e}")
            
            # Test mean reversion strategy
            try:
                mean_rev_signal = mean_reversion_strategy.generate_signal(symbol, df)
                if mean_rev_signal:
                    print(f"  📈 MEAN REVERSION SIGNAL: {mean_rev_signal['action']} - {mean_rev_signal['reason']}")
                else:
                    print(f"  ⭕ No mean reversion signal")
            except Exception as e:
                print(f"  ❌ Mean reversion strategy error: {e}")
                
        except Exception as e:
            print(f"  ❌ Error testing {symbol}: {e}")
    
    print("\nTest completed!")

if __name__ == "__main__":
    test_signal_generation()
