#!/usr/bin/env python3
"""
After-Hours Position Management Analysis
=======================================

This script analyzes what happens to open positions after the 3:30 PM trading cutoff.
"""

import sys
sys.path.append('.')

from core.data_manager import DataManager
from core.intraday_engine import IntradayEngine
from datetime import datetime
import config

def analyze_after_hours_behavior():
    print("🕕 AFTER-HOURS POSITION MANAGEMENT ANALYSIS")
    print("=" * 60)
    
    # 1. Check current market status
    print("\n1. MARKET STATUS:")
    now = datetime.now().time()
    market_close = config.MARKET_CLOSE
    is_closed = now > market_close
    
    print(f"   🕐 Current time: {now}")
    print(f"   🏁 Bot trading cutoff: {market_close} (3:30 PM)")
    print(f"   🔴 Market closed: {is_closed}")
    print(f"   📈 Actual market close: 4:00 PM (continues for 30 min after bot stops)")
    
    # 2. Check current positions
    print("\n2. CURRENT OPEN POSITIONS:")
    dm = DataManager()
    positions = dm.get_positions()
    
    if positions:
        print(f"   📊 Total positions: {len(positions)}")
        total_unrealized = 0
        for pos in positions:
            symbol = pos.get('symbol', 'Unknown')
            qty = float(pos.get('qty', 0))
            side = pos.get('side', 'Unknown')
            unrealized_pl = float(pos.get('unrealized_pl', 0))
            market_value = float(pos.get('market_value', 0))
            current_price = float(pos.get('current_price', 0))
            
            total_unrealized += unrealized_pl
            
            print(f"   📍 {symbol}:")
            print(f"      • Quantity: {qty} shares")
            print(f"      • Side: {side.upper()}")
            print(f"      • Current Price: ${current_price:.2f}")
            print(f"      • Market Value: ${market_value:.2f}")
            print(f"      • Unrealized P&L: ${unrealized_pl:+.2f}")
            
        print(f"   💰 Total Unrealized P&L: ${total_unrealized:+.2f}")
    else:
        print("   📊 No open positions")
    
    # 3. Analyze bot behavior
    print("\n3. BOT BEHAVIOR ANALYSIS:")
    
    # Check if bot automatically closes positions
    try:
        engine = IntradayEngine()
        
        # Check stop method behavior
        import inspect
        stop_source = inspect.getsource(engine.stop)
        auto_closes = "close_position" in stop_source and "for symbol in" in stop_source
        
        print(f"   🛑 Bot stop method auto-closes positions: {auto_closes}")
        
        if auto_closes:
            print("   ✅ When bot stops, ALL positions are automatically closed")
            print("   ✅ This prevents overnight exposure")
            print("   ✅ Ensures all P&L is realized before EOD")
        else:
            print("   ⚠️  Bot may leave positions open overnight")
            
    except Exception as e:
        print(f"   ❌ Error analyzing bot behavior: {e}")
    
    # 4. Check what happens during market close
    print("\n4. MARKET CLOSE PROCESS:")
    print("   🕕 3:30 PM: Bot stops taking new trades")
    print("   🔄 3:30-4:00 PM: Market continues trading (30 min)")
    print("   🏁 4:00 PM: Market officially closes")
    print("   📊 Current status: Market closed, but positions may remain")
    
    # 5. Position management options
    print("\n5. POSITION MANAGEMENT OPTIONS:")
    print("   🔧 Manual closure available via: python close_trade.py")
    print("   🔧 Interactive mode: python close_trade.py --interactive")
    print("   🔧 Close all: python close_trade.py --close-all")
    print("   🔧 Close specific: python close_trade.py --symbol SOFI")
    
    # 6. Recommendations
    print("\n6. RECOMMENDATIONS:")
    if positions:
        print("   ⚠️  OPEN POSITIONS DETECTED AFTER 3:30 PM")
        print("   💡 Consider closing manually to avoid overnight exposure")
        print("   💡 Use: python close_trade.py --close-all")
        print("   💡 Or let positions run overnight for potential gaps")
    else:
        print("   ✅ No open positions - good risk management")
    
    print("\n" + "=" * 60)
    print("🎯 SUMMARY:")
    print("   The bot stops trading at 3:30 PM but may leave positions open.")
    print("   These positions will continue to fluctuate until manually closed")
    print("   or until the next trading day. Use manual tools to close if desired.")

if __name__ == "__main__":
    analyze_after_hours_behavior()
