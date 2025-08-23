#!/usr/bin/env python3
"""
Check order status and force close positions regardless of market hours
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderStatus
from alpaca.trading.requests import MarketOrderRequest, OrderSide, TimeInForce

from config import ALPACA_API_KEY, ALPACA_SECRET_KEY


def check_and_force_close():
    """Check recent orders and force close positions"""
    print("\n🔍 CHECK ORDER STATUS & FORCE CLOSE 🔍")
    print("="*50)
    
    try:
        client = TradingClient(ALPACA_API_KEY, ALPACA_SECRET_KEY, paper=True)
        
        # Check recent orders
        print("📋 Checking recent orders...")
        orders = client.get_orders()
        
        recent_orders = orders[:5] if orders else []
        print(f"Found {len(recent_orders)} recent orders:")
        
        for order in recent_orders:
            print(f"  • {order.symbol}: {order.side.name} {order.qty} - Status: {order.status.name}")
        
        # Check market status
        print(f"\n📈 Checking market status...")
        clock = client.get_clock()
        print(f"Market is {'OPEN' if clock.is_open else 'CLOSED'}")
        print(f"Next open: {clock.next_open}")
        print(f"Next close: {clock.next_close}")
        
        # Get positions
        print(f"\n📊 Current positions...")
        positions = client.get_all_positions()
        
        if not positions:
            print("✅ No positions found - all closed!")
            return
        
        print(f"⚠️ {len(positions)} positions still open:")
        for pos in positions:
            print(f"  • {pos.symbol}: {pos.side.name} {pos.qty} shares")
        
        # If market is closed, we might need to wait or use different strategy
        if not clock.is_open:
            print(f"\n⏰ Market is closed. Market orders may not execute immediately.")
            print(f"Options:")
            print(f"  1. Wait for market to open")
            print(f"  2. Use extended hours trading (if available)")
            print(f"  3. Positions will auto-close with market orders when market opens")
        
        # Try one more close attempt
        print(f"\n🔄 Attempting to close all positions again...")
        
        for pos in positions:
            symbol = pos.symbol
            qty = abs(int(float(pos.qty)))
            side = pos.side.name
            
            try:
                # Use liquidate position API if available
                response = client.close_position(symbol)
                print(f"✅ {symbol}: Liquidation initiated")
                
            except Exception as e:
                print(f"⚠️ {symbol}: Liquidation API failed - {e}")
                
                # Fallback to market order
                try:
                    order_side = OrderSide.SELL if side == 'LONG' else OrderSide.BUY
                    
                    market_order_data = MarketOrderRequest(
                        symbol=symbol,
                        qty=qty,
                        side=order_side,
                        time_in_force=TimeInForce.DAY
                    )
                    
                    order = client.submit_order(order_data=market_order_data)
                    print(f"✅ {symbol}: Market order submitted - {order.id}")
                    
                except Exception as e2:
                    print(f"❌ {symbol}: Market order failed - {e2}")
        
        print(f"\n🏁 Close attempt completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_and_force_close()
