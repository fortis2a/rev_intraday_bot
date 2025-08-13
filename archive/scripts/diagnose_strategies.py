#!/usr/bin/env python3
"""
Strategy Error Diagnosis - Find out why strategies are failing
"""

import sys
from pathlib import Path
from datetime import datetime
import traceback

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from config import config
from core.data_manager import DataManager
from stock_watchlist import ACTIVE_WATCHLIST
from strategies.momentum_scalp import MomentumScalpStrategy
from strategies.mean_reversion import MeanReversionStrategy
from strategies.vwap_bounce import VWAPBounceStrategy

def diagnose_strategy_errors():
    print("🔍 STRATEGY ERROR DIAGNOSIS")
    print("=" * 60)
    
    dm = DataManager()
    
    # Initialize strategies
    strategies = [
        ("Momentum Scalping", MomentumScalpStrategy()),
        ("Mean Reversion", MeanReversionStrategy()),
        ("VWAP Bounce", VWAPBounceStrategy())
    ]
    
    # Test with a tradeable symbol
    test_symbol = "PG"  # Known to be tradeable from dashboard
    
    print(f"🧪 Testing strategies with {test_symbol}...")
    print("-" * 60)
    
    try:
        # Get current market data
        current_data = dm.get_current_market_data(test_symbol, force_fresh=True)
        print(f"✅ Current data for {test_symbol}: ${current_data['price']:.2f}")
        
        # Get historical data
        print(f"📊 Fetching historical data for {test_symbol}...")
        historical_data = dm.get_historical_data(test_symbol, config.TIMEFRAME, 100)
        
        if historical_data is not None:
            print(f"✅ Historical data: {len(historical_data)} bars")
            print(f"   Columns: {list(historical_data.columns)}")
            print(f"   Latest close: ${historical_data.iloc[-1]['close']:.2f}")
            print(f"   Data index type: {type(historical_data.index)}")
        else:
            print("❌ No historical data available")
            return
        
        print("\n🎯 Testing each strategy:")
        print("-" * 60)
        
        for strategy_name, strategy in strategies:
            print(f"\n🔧 Testing {strategy_name}...")
            
            try:
                # Test the strategy
                signals = strategy.generate_signals(test_symbol, historical_data)
                
                if signals and len(signals) > 0:
                    latest_signal = signals[-1]
                    action = latest_signal.signal_type
                    confidence = latest_signal.confidence
                    
                    if action in ['BUY', 'SELL']:
                        print(f"   ✅ Signal: {action} (confidence: {confidence:.1f})")
                        print(f"   📝 Strategy: {latest_signal.strategy}")
                        print(f"   💰 Entry: ${latest_signal.entry_price:.2f}")
                        print(f"   🛑 Stop: ${latest_signal.stop_loss:.2f}")
                        print(f"   🎯 Target: ${latest_signal.profit_target:.2f}")
                    else:
                        print(f"   ⚪ No actionable signal (type: {action})")
                else:
                    print(f"   ⚪ No signals generated")
                    
            except Exception as e:
                print(f"   ❌ ERROR: {str(e)}")
                print(f"   📋 Full traceback:")
                traceback.print_exc()
                print("-" * 40)
    
    except Exception as e:
        print(f"❌ FATAL ERROR: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    diagnose_strategy_errors()
