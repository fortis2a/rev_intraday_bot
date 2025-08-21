#!/usr/bin/env python3
"""
Emergency Position Closer - Cancel ALL orders first, then close positions
"""

import sys
from pathlib import Path
import alpaca_trade_api as tradeapi
import time

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from config import config

def emergency_close_everything():
    """Cancel ALL orders first, then close ALL positions"""
    print("\n🚨 EMERGENCY CLOSE EVERYTHING 🚨")
    print("="*60)
    
    try:
        # Connect to Alpaca
        api = tradeapi.REST(
            config['ALPACA_API_KEY'],
            config['ALPACA_SECRET_KEY'], 
            config['ALPACA_BASE_URL']
        )
        
        print("🔗 Connected to Alpaca API")
        
        # STEP 1: Cancel ALL orders first
        print("\n🗑️ STEP 1: Cancelling ALL orders...")
        try:
            api.cancel_all_orders()
            print("✅ All orders cancelled successfully")
        except Exception as e:
            print(f"⚠️ Cancel all orders error: {e}")
        
        # Wait a moment for cancellations to process
        time.sleep(2)
        
        # STEP 2: Check remaining orders
        print("\n🔍 Checking remaining orders...")
        orders = api.list_orders(status='all', limit=50)
        pending_orders = [o for o in orders if o.status in ['new', 'partially_filled', 'accepted', 'pending_new']]
        
        if pending_orders:
            print(f"⚠️ {len(pending_orders)} orders still pending:")
            for order in pending_orders:
                print(f"  • {order.symbol}: {order.side} {order.qty} @ {order.type} ({order.status})")
                try:
                    api.cancel_order(order.id)
                    print(f"    ✅ Cancelled order {order.id}")
                except Exception as e:
                    print(f"    ❌ Failed to cancel {order.id}: {e}")
        else:
            print("✅ No pending orders found")
        
        # Wait for cancellations to process
        time.sleep(3)
        
        # STEP 3: Close all positions
        print("\n💼 STEP 3: Closing ALL positions...")
        positions = api.list_positions()
        
        if not positions:
            print("✅ No positions to close")
            return
        
        print(f"📊 Found {len(positions)} positions to close:")
        
        success_count = 0
        failed_symbols = []
        
        for i, pos in enumerate(positions, 1):
            symbol = pos.symbol
            qty = int(pos.qty)
            abs_qty = abs(qty)
            side = "LONG" if qty > 0 else "SHORT"
            pnl = float(pos.unrealized_pl)
            
            print(f"\n[{i}/{len(positions)}] {symbol}: {side} {abs_qty} shares (P&L: ${pnl:.2f})")
            
            try:
                # Use the API's close position method
                api.close_position(symbol)
                print(f"  ✅ Position closed using API close_position()")
                success_count += 1
                
            except Exception as e:
                print(f"  ⚠️ API close failed: {e}")
                
                # Fallback: Manual market order
                try:
                    order_side = 'sell' if qty > 0 else 'buy'
                    print(f"  🔄 Trying manual {order_side} order...")
                    
                    order = api.submit_order(
                        symbol=symbol,
                        qty=abs_qty,
                        side=order_side,
                        type='market',
                        time_in_force='day'
                    )
                    
                    print(f"  ✅ Manual order submitted: {order.id}")
                    success_count += 1
                    
                except Exception as e2:
                    print(f"  ❌ Manual order failed: {e2}")
                    failed_symbols.append(symbol)
            
            time.sleep(1)  # Small delay between orders
        
        # STEP 4: Final verification
        print(f"\n📊 FINAL RESULTS:")
        print(f"✅ Successfully processed: {success_count}/{len(positions)} positions")
        
        if failed_symbols:
            print(f"❌ Failed: {', '.join(failed_symbols)}")
        
        # Check final status
        print(f"\n🔍 Final position check...")
        final_positions = api.list_positions()
        
        if final_positions:
            print(f"⚠️ {len(final_positions)} positions still remain:")
            for pos in final_positions:
                print(f"  • {pos.symbol}: {int(pos.qty)} shares")
        else:
            print("🎉 ALL POSITIONS SUCCESSFULLY CLOSED!")
        
        print("\n🏁 Emergency closure process completed!")
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    emergency_close_everything()
