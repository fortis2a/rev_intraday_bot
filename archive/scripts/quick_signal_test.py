#!/usr/bin/env python3
"""
Simple signal test to see what's happening
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from core.data_manager import DataManager
from strategies.momentum_scalp import MomentumScalpStrategy
from strategies.mean_reversion import MeanReversionStrategy
from strategies.vwap_bounce import VWAPBounceStrategy
import config
from stock_watchlist import MY_CUSTOM_STOCKS
from datetime import datetime
import pytz

def main():
    print("🎯 QUICK SIGNAL TEST")
    print("=" * 50)
    
    # Initialize components
    data_manager = DataManager()
    strategies = [
        ("Momentum", MomentumScalpStrategy()),
        ("Mean Reversion", MeanReversionStrategy()),
        ("VWAP Bounce", VWAPBounceStrategy())
    ]
    
    # Check market hours
    est = pytz.timezone('US/Eastern')
    current_time = datetime.now(est)
    market_open = current_time.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close = current_time.replace(hour=16, minute=0, second=0, microsecond=0)
    is_market_open = market_open <= current_time <= market_close
    
    print(f"⏰ Current time: {current_time.strftime('%H:%M:%S')}")
    print(f"📊 Market is {'OPEN' if is_market_open else 'CLOSED'}")
    
    print(f"\n📋 Testing {len(MY_CUSTOM_STOCKS)} symbols:")
    
    total_signals = 0
    
    for symbol in MY_CUSTOM_STOCKS:
        print(f"\n📈 {symbol}:")
        
        try:
            # Get data
            bars = data_manager.get_market_data(symbol, "1Min", limit=100)
            if bars is None or bars.empty or len(bars) < 20:
                print(f"   ❌ Insufficient data: {len(bars) if bars is not None else 0} bars")
                continue
                
            current_price = float(bars[-1].close)
            print(f"   💰 Current price: ${current_price:.2f}")
            print(f"   📊 Data bars: {len(bars)}")
            
            # Test each strategy
            for strategy_name, strategy in strategies:
                try:
                    signal = strategy.generate_signal(bars)
                    if signal and signal.get('action') != 'HOLD':
                        total_signals += 1
                        confidence = signal.get('confidence', 0)
                        print(f"   🎯 {strategy_name}: {signal['action']} (confidence: {confidence:.2f})")
                    else:
                        print(f"   ⚪ {strategy_name}: HOLD")
                except Exception as e:
                    print(f"   ❌ {strategy_name}: Error - {str(e)}")
                    
        except Exception as e:
            print(f"   ❌ Data error: {str(e)}")
            
    print(f"\n📊 SUMMARY:")
    print(f"   🎯 Total active signals: {total_signals}")
    
    if total_signals > 0:
        print(f"   ✅ Signals are being generated!")
        print(f"   💡 Check bot execution logic")
    else:
        print(f"   ⚠️ No signals found - market may be flat")

if __name__ == "__main__":
    main()
