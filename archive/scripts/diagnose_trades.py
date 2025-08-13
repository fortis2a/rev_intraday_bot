#!/usr/bin/env python3
"""
Trade Execution Diagnostic - Find out why signals aren't triggering trades
"""

import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from config import config
from core.data_manager import DataManager
from core.risk_manager import RiskManager
from core.order_manager import OrderManager
from stock_watchlist import ACTIVE_WATCHLIST
from strategies.momentum_scalp import MomentumScalpStrategy

def diagnose_trade_execution():
    print("🔍 TRADE EXECUTION DIAGNOSTIC")
    print("=" * 60)
    
    # Initialize components
    dm = DataManager()
    risk_mgr = RiskManager()
    order_mgr = OrderManager()
    momentum_strategy = MomentumScalpStrategy()
    
    print("✅ Components initialized")
    print(f"📊 Max open positions: {config.MAX_OPEN_POSITIONS}")
    print(f"💰 Max position value: ${config.MAX_POSITION_VALUE}")
    print(f"📈 Max position size: {config.MAX_POSITION_SIZE} shares")
    print(f"📋 Account risk: {config.ACCOUNT_RISK_PCT}%")
    print(f"🛑 Stop loss: {config.STOP_LOSS_PCT}%")
    print(f"🎯 Profit target: {config.PROFIT_TARGET_PCT}%")
    
    # Check account status
    try:
        account_info = order_mgr.get_account_info()
        if account_info:
            equity = float(account_info.get('equity', 0))
            buying_power = float(account_info.get('buying_power', 0))
            print(f"\n💰 Account Status:")
            print(f"   Equity: ${equity:,.2f}")
            print(f"   Buying Power: ${buying_power:,.2f}")
        else:
            print(f"\n❌ Could not get account info")
    except Exception as e:
        print(f"\n❌ Account info error: {e}")
    
    # Check existing positions
    try:
        positions = order_mgr.get_all_positions()
        print(f"\n📊 Current Positions: {len(positions) if positions else 0}")
        if positions:
            for pos in positions:
                print(f"   {pos.get('symbol', 'Unknown')}: {pos.get('qty', 0)} shares")
    except Exception as e:
        print(f"\n❌ Position check error: {e}")
    
    print(f"\n🧪 Testing trade execution for each stock...")
    print("-" * 60)
    
    for symbol in ACTIVE_WATCHLIST:
        print(f"\n📊 {symbol}:")
        
        try:
            # 1. Check market data
            current_data = dm.get_current_market_data(symbol, force_fresh=True)
            if not current_data:
                print(f"   ❌ No market data")
                continue
                
            price = current_data['price']
            spread = current_data['spread_pct']
            print(f"   💰 Price: ${price:.2f} | Spread: {spread:.3f}%")
            
            # 2. Check spread filter
            if spread > config.MAX_SPREAD_PCT:
                print(f"   ❌ BLOCKED: Spread too wide ({spread:.3f}% > {config.MAX_SPREAD_PCT}%)")
                continue
                
            # 3. Check historical data
            historical_data = dm.get_historical_data(symbol, config.TIMEFRAME, 100)
            if historical_data is None or len(historical_data) < 20:
                print(f"   ❌ BLOCKED: Insufficient historical data")
                continue
                
            # 4. Generate signal
            signals = momentum_strategy.generate_signals(symbol, historical_data)
            if not signals or len(signals) == 0:
                print(f"   ⚪ No signals from momentum strategy")
                continue
                
            signal = signals[0]  # Get first signal
            if signal.signal_type not in ['BUY', 'SELL']:
                print(f"   ⚪ Signal type not actionable: {signal.signal_type}")
                continue
                
            print(f"   🎯 Signal: {signal.signal_type} (confidence: {signal.confidence:.1f})")
            print(f"   💰 Entry: ${signal.entry_price:.2f}")
            
            # 5. Check risk management
            try:
                can_open = risk_mgr.can_open_position(signal.symbol, signal.entry_price, signal.signal_type)
                if not can_open:
                    print(f"   ❌ BLOCKED: Risk management denied position")
                    continue
                print(f"   ✅ Risk check: Passed")
            except Exception as e:
                print(f"   ❌ BLOCKED: Risk check error - {e}")
                continue
                
            # 6. Check position size calculation
            try:
                position_size = risk_mgr.calculate_position_size(
                    entry_price=signal.entry_price,
                    stop_loss=signal.stop_loss,
                    symbol=signal.symbol,
                    side=signal.signal_type.lower()
                )
                if position_size <= 0:
                    print(f"   ❌ BLOCKED: Invalid position size ({position_size})")
                    continue
                print(f"   ✅ Position size: {position_size} shares")
            except Exception as e:
                print(f"   ❌ BLOCKED: Position size error - {e}")
                continue
                
            # 7. Check existing positions
            try:
                existing_pos = order_mgr.get_position_info(signal.symbol)
                if existing_pos and abs(float(existing_pos.get('qty', 0))) > 0:
                    print(f"   ❌ BLOCKED: Already have position ({existing_pos.get('qty')} shares)")
                    continue
                print(f"   ✅ No existing position")
            except Exception as e:
                print(f"   ⚠️ Position check warning: {e}")
                
            # 8. All checks passed - this signal SHOULD execute
            print(f"   🟢 ALL CHECKS PASSED - Signal should execute!")
            print(f"      Action: {signal.signal_type} {position_size} shares @ ${signal.entry_price:.2f}")
            print(f"      Stop Loss: ${signal.stop_loss:.2f}")
            print(f"      Profit Target: ${signal.profit_target:.2f}")
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:60]}...")
    
    print(f"\n" + "=" * 60)
    print(f"🔍 If signals show 'ALL CHECKS PASSED' but no trades occurred,")
    print(f"   the issue may be in the main bot's signal processing timing")
    print(f"   or order execution system.")

if __name__ == "__main__":
    diagnose_trade_execution()
