#!/usr/bin/env python3
"""
Test active monitoring and signal generation
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from config import config
from core.data_manager import DataManager
from stock_watchlist import ACTIVE_WATCHLIST

def test_active_monitoring():
    print("🔍 TESTING ACTIVE MONITORING CAPABILITIES")
    print("=" * 60)
    
    dm = DataManager()
    
    # Test strategy signal generation
    print(f"🎯 Testing Strategy Signal Generation:")
    try:
        from strategies.momentum_scalp import MomentumScalpStrategy
        from strategies.mean_reversion import MeanReversionStrategy
        from strategies.vwap_bounce import VWAPBounceStrategy
        
        strategies = {
            'Momentum': MomentumScalpStrategy(),
            'Mean Reversion': MeanReversionStrategy(),
            'VWAP Bounce': VWAPBounceStrategy()
        }
        
        total_signals = 0
        
        for symbol in ACTIVE_WATCHLIST:
            print(f"\n📊 Testing {symbol}:")
            
            try:
                # Get historical data for analysis
                data = dm.get_market_data(symbol, config.TIMEFRAME, 50, force_fresh=True)
                if data is not None and len(data) > 0:
                    print(f"   ✅ Retrieved {len(data)} bars of {config.TIMEFRAME} data")
                    
                    # Test each strategy
                    symbol_signals = 0
                    for name, strategy in strategies.items():
                        try:
                            signals = strategy.generate_signals(symbol, data)
                            if signals:
                                symbol_signals += len(signals)
                                print(f"   🎯 {name}: {len(signals)} signals")
                                
                                # Show signal details
                                for i, signal in enumerate(signals[-2:]):  # Show last 2 signals
                                    print(f"      Signal {i+1}: {signal.signal_type} @ ${signal.entry_price:.2f} (confidence: {signal.confidence:.2f})")
                            else:
                                print(f"   📊 {name}: No signals")
                        except Exception as e:
                            print(f"   ❌ {name}: Error - {str(e)[:50]}...")
                    
                    total_signals += symbol_signals
                    if symbol_signals == 0:
                        print(f"   📈 {symbol}: Market conditions may not favor current strategies")
                else:
                    print(f"   ❌ {symbol}: No historical data available")
                    
            except Exception as e:
                print(f"   ❌ {symbol}: Error - {str(e)[:50]}...")
        
        print(f"\n📊 MONITORING SUMMARY:")
        print(f"   • Total signals detected: {total_signals}")
        print(f"   • Stocks monitored: {len(ACTIVE_WATCHLIST)}")
        print(f"   • Strategies tested: {len(strategies)}")
        
        if total_signals > 0:
            print(f"   🟢 Bot CAN generate trading signals!")
        else:
            print(f"   🟡 No signals in current market conditions")
            
    except Exception as e:
        print(f"   ❌ Strategy testing failed: {e}")
    
    # Test real-time data feed
    print(f"\n📡 Real-time Data Feed Test:")
    for symbol in ACTIVE_WATCHLIST:
        try:
            data = dm.get_current_market_data(symbol, force_fresh=True)
            if data:
                price = data['price']
                spread = data['spread_pct']
                timestamp = data.get('timestamp', 'Unknown')
                print(f"   ✅ {symbol}: ${price:.2f} (spread: {spread:.3f}%) - Real-time feed active")
            else:
                print(f"   ❌ {symbol}: No real-time data")
        except Exception as e:
            print(f"   ❌ {symbol}: Real-time data error - {e}")

if __name__ == "__main__":
    test_active_monitoring()
