#!/usr/bin/env python3
"""
Investigate why signals aren't triggering trades
"""

import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from config import config
from core.data_manager import DataManager
from stock_watchlist import ACTIVE_WATCHLIST
from strategies.momentum_scalp import MomentumScalpStrategy
from strategies.mean_reversion import MeanReversionStrategy
from strategies.vwap_bounce import VWAPBounceStrategy

def investigate_signals():
    print("🔍 INVESTIGATING SIGNAL PROCESSING GAP")
    print("=" * 60)
    
    dm = DataManager()
    
    # Initialize strategies
    momentum_strategy = MomentumScalpStrategy()
    mean_reversion_strategy = MeanReversionStrategy()
    vwap_strategy = VWAPBounceStrategy()
    
    strategies = [
        ("Momentum", momentum_strategy),
        ("Mean Rev", mean_reversion_strategy),
        ("VWAP", vwap_strategy)
    ]
    
    print("📊 Testing signal generation for each stock...")
    print("-" * 60)
    
    all_signals = []
    
    for symbol in ACTIVE_WATCHLIST:
        print(f"\n🧪 Testing {symbol}:")
        
        try:
            # Get current market data
            current_data = dm.get_current_market_data(symbol, force_fresh=True)
            if not current_data:
                print(f"   ❌ No current data available")
                continue
                
            price = current_data['price']
            spread = current_data['spread_pct']
            
            print(f"   💰 Price: ${price:.2f} | Spread: {spread:.3f}%")
            
            # Check if tradeable
            if spread > config.MAX_SPREAD_PCT:
                print(f"   ❌ Not tradeable - spread too wide")
                continue
            
            # Get historical data
            historical_data = dm.get_historical_data(symbol, config.TIMEFRAME, 100)
            if historical_data is None or len(historical_data) < 20:
                print(f"   ❌ Insufficient historical data")
                continue
                
            print(f"   ✅ Historical data: {len(historical_data)} bars")
            
            # Test each strategy
            symbol_signals = []
            for strategy_name, strategy in strategies:
                try:
                    signals = strategy.generate_signals(symbol, historical_data)
                    
                    if signals and len(signals) > 0:
                        for signal in signals:
                            if signal.signal_type in ['BUY', 'SELL']:
                                symbol_signals.append({
                                    'symbol': symbol,
                                    'strategy': strategy_name,
                                    'signal': signal,
                                    'price': price,
                                    'spread': spread
                                })
                                print(f"   🎯 {strategy_name}: {signal.signal_type} signal (confidence: {signal.confidence:.1f})")
                                print(f"      Entry: ${signal.entry_price:.2f} | Stop: ${signal.stop_loss:.2f} | Target: ${signal.profit_target:.2f}")
                    else:
                        print(f"   ⚪ {strategy_name}: No signals")
                        
                except Exception as e:
                    print(f"   ❌ {strategy_name}: Error - {str(e)[:50]}...")
            
            all_signals.extend(symbol_signals)
            
        except Exception as e:
            print(f"   ❌ Error processing {symbol}: {str(e)[:50]}...")
    
    print(f"\n" + "=" * 60)
    print(f"📊 SIGNAL SUMMARY:")
    print(f"   🎯 Total signals detected: {len(all_signals)}")
    
    if all_signals:
        print(f"\n🚨 ACTIVE TRADING SIGNALS:")
        for i, sig in enumerate(all_signals, 1):
            signal = sig['signal']
            print(f"   {i}. {sig['symbol']} - {sig['strategy']} - {signal.signal_type}")
            print(f"      Entry: ${signal.entry_price:.2f} | Confidence: {signal.confidence:.1f}")
    
    print(f"\n🔍 POSSIBLE REASONS FOR NO TRADES:")
    print(f"   1. Signal confidence too low (need > minimum threshold)")
    print(f"   2. Risk management blocking trades")
    print(f"   3. Position limits reached")
    print(f"   4. Order execution system not processing signals")
    print(f"   5. Market timing filters (signal delay, etc.)")

if __name__ == "__main__":
    investigate_signals()
