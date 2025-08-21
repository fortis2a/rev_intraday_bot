#!/usr/bin/env python3
"""
EMERGENCY CLOSE ALL POSITIONS
Quick script to close all positions immediately
"""

import sys
from pathlib import Path
import alpaca_trade_api as tradeapi

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from config import config

def emergency_close_all():
    """Emergency close all positions"""
    print("\n🚨 EMERGENCY POSITION CLOSER 🚨")
    print("="*50)
    
    try:
        # Connect to Alpaca
        api = tradeapi.REST(
            config['ALPACA_API_KEY'],
            config['ALPACA_SECRET_KEY'], 
            config['ALPACA_BASE_URL']
        )
        
        print("🔗 Connected to Alpaca API")
        
        # Get positions
        positions = api.list_positions()
        
        if not positions:
            print("📭 No positions found to close")
            return
        
        print(f"\n📊 Found {len(positions)} positions:")
        total_pnl = 0
        for pos in positions:
            pnl = float(pos.unrealized_pl)
            total_pnl += pnl
            side = "LONG" if int(pos.qty) > 0 else "SHORT"
            print(f"  • {pos.symbol}: {side} {abs(int(pos.qty))} shares (P&L: ${pnl:.2f})")
        
        print(f"💰 Total Unrealized P&L: ${total_pnl:.2f}")
        
        # Safety confirmation
        print(f"\n⚠️  WARNING: This will close ALL {len(positions)} positions!")
        confirm = input("Type 'EMERGENCY CLOSE' to proceed: ").strip()
        
        if confirm != 'EMERGENCY CLOSE':
            print("❌ Operation cancelled - safety check failed")
            return
        
        print("\n🔄 Closing all positions...")
        
        # Close all positions
        try:
            api.close_all_positions()
            print("✅ Emergency close command sent successfully!")
            print("📋 All positions are being closed at market prices")
            
        except Exception as e:
            print(f"❌ API close_all failed: {e}")
            print("🔄 Attempting individual closures...")
            
            # Fallback: close individually
            for pos in positions:
                try:
                    symbol = pos.symbol
                    qty = int(pos.qty)
                    abs_qty = abs(qty)
                    
                    if qty > 0:
                        # Close long with sell
                        order = api.submit_order(
                            symbol=symbol,
                            qty=abs_qty,
                            side='sell',
                            type='market',
                            time_in_force='day'
                        )
                    else:
                        # Close short with buy
                        order = api.submit_order(
                            symbol=symbol,
                            qty=abs_qty,
                            side='buy',
                            type='market',
                            time_in_force='day'
                        )
                    
                    print(f"✅ {symbol} closed (Order: {order.id})")
                    
                except Exception as e:
                    print(f"❌ Failed to close {pos.symbol}: {e}")
        
        print("\n🏁 Emergency closure process completed!")
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")

if __name__ == "__main__":
    emergency_close_all()
