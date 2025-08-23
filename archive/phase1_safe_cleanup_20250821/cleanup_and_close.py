#!/usr/bin/env python3
"""
Check and Cancel Orders, then Force Close
"""

import sys
from pathlib import Path

import alpaca_trade_api as tradeapi

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from config import config


def check_and_cancel_orders():
    """Check for open orders and cancel them"""
    try:
        api = tradeapi.REST(
            config['ALPACA_API_KEY'],
            config['ALPACA_SECRET_KEY'], 
            config['ALPACA_BASE_URL']
        )
        
        print("🔍 Checking for open orders...")
        
        # Get all open orders
        orders = api.list_orders(status='open')
        
        if not orders:
            print("📭 No open orders found")
            return True
        
        print(f"📋 Found {len(orders)} open orders:")
        for order in orders:
            print(f"  • {order.symbol}: {order.side.upper()} {order.qty} @ {order.order_type} (ID: {order.id})")
        
        # Cancel all orders
        print(f"\n🚫 Cancelling all {len(orders)} open orders...")
        
        for order in orders:
            try:
                api.cancel_order(order.id)
                print(f"  ✅ Cancelled {order.symbol} order {order.id}")
            except Exception as e:
                print(f"  ❌ Failed to cancel {order.symbol}: {e}")
        
        print("✅ Order cancellation completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error checking orders: {e}")
        return False

def force_close_with_gtc():
    """Try closing with Good Till Cancelled orders"""
    try:
        api = tradeapi.REST(
            config['ALPACA_API_KEY'],
            config['ALPACA_SECRET_KEY'], 
            config['ALPACA_BASE_URL']
        )
        
        positions = api.list_positions()
        
        if not positions:
            print("📭 No positions to close")
            return
        
        print(f"\n🎯 Attempting to close {len(positions)} positions with GTC orders...")
        
        for pos in positions:
            symbol = pos.symbol
            qty = int(pos.qty)
            abs_qty = abs(qty)
            
            try:
                if qty > 0:
                    # Close long with sell
                    order = api.submit_order(
                        symbol=symbol,
                        qty=abs_qty,
                        side='sell',
                        type='market',
                        time_in_force='gtc'  # Good Till Cancelled
                    )
                else:
                    # Close short with buy
                    order = api.submit_order(
                        symbol=symbol,
                        qty=abs_qty,
                        side='buy',
                        type='market',
                        time_in_force='gtc'
                    )
                
                print(f"✅ {symbol}: Order {order.id} submitted")
                
            except Exception as e:
                print(f"❌ {symbol}: {e}")
        
    except Exception as e:
        print(f"❌ Error in GTC close: {e}")

def main():
    print("🛠️  ORDER CLEANUP AND FORCE CLOSE")
    print("="*50)
    
    # Step 1: Cancel all open orders
    if check_and_cancel_orders():
        print("\n" + "="*50)
        
        # Step 2: Try force close again
        force_close_with_gtc()

if __name__ == "__main__":
    main()
