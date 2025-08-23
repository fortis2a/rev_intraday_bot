#!/usr/bin/env python3
"""
Debug why SOFI/NIO are not generating signals now when they did before
"""
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd

from config import config
from core.data_manager import DataManager
from stock_specific_config import should_execute_trade
from strategies.mean_reversion import MeanReversionStrategy


def debug_signal_generation():
    """Debug specific symbols that should be generating signals"""
    print("="*60)
    print("DEBUG: Why are SOFI/NIO not generating signals?")
    print("="*60)
    
    data_manager = DataManager()
    
    # Test the exact symbols that were working before
    test_symbols = ["SOFI", "NIO"]
    
    for symbol in test_symbols:
        print(f"\n🔍 DEBUGGING {symbol}")
        print("-" * 40)
        
        try:
            # Get the same data as main.py
            df = data_manager.get_bars(symbol, config['TIMEFRAME'])
            print(f"Data bars: {len(df)}")
            
            if df.empty or len(df) < 26:
                print(f"❌ Insufficient data")
                continue
                
            # Calculate indicators
            df = data_manager.calculate_indicators(df)
            
            # Check recent price data
            recent = df.tail(3)
            print(f"Recent prices:")
            for i, row in recent.iterrows():
                print(f"  {i}: ${row['close']:.2f}")
            
            # Check Bollinger Bands specifically
            latest = df.iloc[-1]
            print(f"\nBollinger Band Analysis:")
            print(f"  Close: ${latest['close']:.2f}")
            print(f"  BB Upper: ${latest['bb_upper']:.2f}")
            print(f"  BB Lower: ${latest['bb_lower']:.2f}")
            print(f"  BB Middle: ${latest['bb_middle']:.2f}")
            
            # Calculate position relative to bands
            bb_position = (latest['close'] - latest['bb_lower']) / (latest['bb_upper'] - latest['bb_lower'])
            print(f"  Position in bands: {bb_position:.1%} (0%=lower, 100%=upper)")
            
            # Check if this should trigger mean reversion
            print(f"\nMean Reversion Conditions:")
            if latest['close'] > latest['bb_upper']:
                print(f"  ✅ Price above upper band - SELL condition")
            elif latest['close'] < latest['bb_lower']:
                print(f"  ✅ Price below lower band - BUY condition")
            else:
                print(f"  ⚪ Price within bands - No signal")
            
            # Test mean reversion strategy directly
            print(f"\nStrategy Test:")
            mean_rev = MeanReversionStrategy(symbol)
            signal = mean_rev.generate_signal(symbol, df)
            print(f"  Mean reversion signal: {signal}")
            
            # Test confidence
            print(f"\nConfidence Test:")
            trade_decision = should_execute_trade(symbol)
            print(f"  Confidence decision: {trade_decision}")
            
        except Exception as e:
            print(f"❌ Error debugging {symbol}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    debug_signal_generation()
