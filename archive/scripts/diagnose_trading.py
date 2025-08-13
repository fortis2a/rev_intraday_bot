#!/usr/bin/env python3
"""
Trading Diagnostic Tool
Checks why trades aren't executing despite active signals
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from core.data_manager import DataManager
from core.order_manager import OrderManager
from core.scalping_engine import ScalpingEngine
from core.risk_manager import RiskManager
from strategies.momentum_scalp import MomentumScalpStrategy
from strategies.mean_reversion import MeanReversionStrategy
from strategies.vwap_bounce import VWAPBounceStrategy
import config
from datetime import datetime
import pytz

def main():
    print("🔍 TRADING DIAGNOSTIC - Why No Trades?")
    print("=" * 60)
    
    # Initialize components
    try:
        data_manager = DataManager()
        order_manager = OrderManager()
        risk_manager = RiskManager()
        
        # Test strategies
        strategies = [
            MomentumScalpStrategy(),
            MeanReversionStrategy(), 
            VWAPBounceStrategy()
        ]
        
        print(f"✅ Components initialized successfully")
        
        # Check market hours
        est = pytz.timezone('US/Eastern')
        current_time = datetime.now(est)
        market_open = current_time.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = current_time.replace(hour=16, minute=0, second=0, microsecond=0)
        
        print(f"🕐 Current time: {current_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"📈 Market open: {market_open.strftime('%H:%M:%S')}")
        print(f"📉 Market close: {market_close.strftime('%H:%M:%S')}")
        
        is_market_open = market_open <= current_time <= market_close
        print(f"📊 Market is {'OPEN' if is_market_open else 'CLOSED'}")
        
        if not is_market_open:
            print("⚠️  REASON: Market is currently closed - no trading allowed")
            return
            
        # Check account status
        account = order_manager.api.get_account()
        print(f"💰 Account equity: ${float(account.equity):,.2f}")
        print(f"💵 Buying power: ${float(account.buying_power):,.2f}")
        print(f"📊 Account status: {account.status}")
        
        if account.status != 'ACTIVE':
            print(f"⚠️  REASON: Account status is {account.status}, not ACTIVE")
            return
            
        # Check positions and orders
        positions = order_manager.api.get_all_positions()
        orders = order_manager.api.get_orders()
        
        print(f"📈 Current positions: {len(positions)}")
        print(f"📋 Open orders: {len(orders)}")
        
        # Check signals for each symbol
        print("\n🎯 SIGNAL ANALYSIS:")
        print("-" * 40)
        
        active_signals = 0
        tradeable_symbols = 0
        
        for symbol in config.MY_CUSTOM_STOCKS:
            try:
                # Get current data
                bars = data_manager.get_bars(symbol, config.TIMEFRAME, limit=100)
                if not bars or len(bars) < 20:
                    print(f"❌ {symbol}: Insufficient data ({len(bars) if bars else 0} bars)")
                    continue
                    
                tradeable_symbols += 1
                current_price = float(bars[-1].close)
                
                print(f"\n📊 {symbol} - Price: ${current_price:.2f}")
                
                # Check each strategy
                symbol_signals = 0
                for strategy in strategies:
                    try:
                        signal = strategy.generate_signal(bars)
                        if signal and signal['action'] != 'HOLD':
                            symbol_signals += 1
                            active_signals += 1
                            print(f"   🎯 {strategy.__class__.__name__}: {signal['action']} (confidence: {signal['confidence']:.2f})")
                            
                            # Check why this signal isn't resulting in a trade
                            print(f"      Checking trade barriers...")
                            
                            # Risk checks
                            position_size = risk_manager.calculate_position_size(
                                current_price, config.MAX_POSITION_VALUE
                            )
                            print(f"      📊 Position size: {position_size} shares")
                            
                            if position_size <= 0:
                                print(f"      ❌ BARRIER: Position size too small")
                                continue
                                
                            # Check if we already have a position
                            try:
                                existing_position = order_manager.api.get_open_position(symbol)
                                if existing_position:
                                    print(f"      ❌ BARRIER: Already have position in {symbol}")
                                    continue
                            except:
                                pass  # No position exists
                                
                            # Check daily trade limits
                            if len(positions) >= config.MAX_POSITIONS:
                                print(f"      ❌ BARRIER: Max positions reached ({config.MAX_POSITIONS})")
                                continue
                                
                            print(f"      ✅ Signal should result in trade!")
                            
                        else:
                            print(f"   ⚪ {strategy.__class__.__name__}: HOLD")
                    except Exception as e:
                        print(f"   ❌ {strategy.__class__.__name__}: Error - {str(e)}")
                        
                if symbol_signals == 0:
                    print(f"   ⚪ No active signals")
                    
            except Exception as e:
                print(f"❌ {symbol}: Error getting data - {str(e)}")
                
        print(f"\n📋 SUMMARY:")
        print(f"   🎯 Tradeable symbols: {tradeable_symbols}")
        print(f"   🚨 Active signals: {active_signals}")
        
        if active_signals > 0 and is_market_open:
            print(f"\n⚠️  ISSUE: {active_signals} signals detected but no trades executing!")
            print(f"💡 Possible causes:")
            print(f"   - Bot process not running the trading loop")
            print(f"   - Signal confidence below threshold")
            print(f"   - Risk management blocking trades")
            print(f"   - Order execution errors")
            
        elif active_signals == 0:
            print(f"\n✅ No active signals - no trades expected")
            
    except Exception as e:
        print(f"❌ Diagnostic failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
