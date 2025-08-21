#!/usr/bin/env python3
"""
Close Trade Script - Main Interface
Quick and easy way to close individual stocks or all positions
"""

import sys
import os
import argparse
from pathlib import Path
import alpaca_trade_api as tradeapi

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Import configuration
from config import config
from utils.logger import setup_logger

class QuickTradeCloser:
    """Quick utility to close trades via Alpaca API"""
    
    def __init__(self):
        self.logger = setup_logger('quick_closer')
        
        # Initialize Alpaca API
        self.api = tradeapi.REST(
            config['ALPACA_API_KEY'],
            config['ALPACA_SECRET_KEY'], 
            config['ALPACA_BASE_URL']
        )
        
        print("🔗 Connected to Alpaca API")
        print(f"🏦 Environment: {config['ALPACA_BASE_URL']}")
    
    def list_positions(self):
        """List all current positions"""
        try:
            positions = self.api.list_positions()
            
            if not positions:
                print("📭 No open positions found")
                return []
            
            print("\n" + "="*70)
            print("                    CURRENT POSITIONS")
            print("="*70)
            print(f"{'#':<3} {'Symbol':<8} {'Side':<6} {'Qty':<6} {'Entry':<10} {'Current':<10} {'P&L $':<12} {'P&L %':<8}")
            print("-"*70)
            
            for i, pos in enumerate(positions, 1):
                symbol = pos.symbol
                qty = int(pos.qty)
                side = "LONG" if qty > 0 else "SHORT"
                entry_price = float(pos.avg_entry_price)
                current_price = float(pos.current_price) if hasattr(pos, 'current_price') else 0
                unrealized_pnl = float(pos.unrealized_pl)
                
                # Calculate percentage
                if entry_price > 0:
                    pnl_pct = (unrealized_pnl / (entry_price * abs(qty))) * 100
                else:
                    pnl_pct = 0
                
                status = "🟢" if unrealized_pnl >= 0 else "🔴"
                
                print(f"{status} {i:<2} {symbol:<8} {side:<6} {abs(qty):<6} ${entry_price:<9.2f} ${current_price:<9.2f} ${unrealized_pnl:<11.2f} {pnl_pct:+.1f}%")
            
            print("="*70)
            print(f"Total Positions: {len(positions)}")
            
            return positions
            
        except Exception as e:
            print(f"❌ Error getting positions: {e}")
            return []
    
    def close_position(self, symbol):
        """Close a specific position"""
        try:
            print(f"\n🎯 Closing position: {symbol.upper()}")
            
            # Get position
            try:
                position = self.api.get_position(symbol.upper())
            except:
                print(f"❌ No position found for {symbol.upper()}")
                return False
            
            qty = int(position.qty)
            side = "LONG" if qty > 0 else "SHORT"
            abs_qty = abs(qty)
            
            print(f"📊 Position: {side} {abs_qty} shares @ ${float(position.avg_entry_price):.2f}")
            print(f"💰 Current P&L: ${float(position.unrealized_pl):.2f}")
            
            # Close the position
            if qty > 0:
                # Close long position with sell order
                order = self.api.submit_order(
                    symbol=symbol.upper(),
                    qty=abs_qty,
                    side='sell',
                    type='market',
                    time_in_force='day'
                )
            else:
                # Close short position with buy order
                order = self.api.submit_order(
                    symbol=symbol.upper(),
                    qty=abs_qty,
                    side='buy',
                    type='market',
                    time_in_force='day'
                )
            
            print(f"✅ {symbol.upper()} position closed successfully!")
            print(f"📋 Order ID: {order.id}")
            print(f"🔄 Order Status: {order.status}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error closing {symbol}: {e}")
            return False
    
    def close_all_positions(self):
        """Close all positions"""
        try:
            positions = self.api.list_positions()
            
            if not positions:
                print("📭 No positions to close")
                return
            
            print(f"\n⚠️  CLOSING ALL {len(positions)} POSITIONS:")
            for pos in positions:
                side = "LONG" if int(pos.qty) > 0 else "SHORT"
                print(f"    • {pos.symbol}: {side} {abs(int(pos.qty))} shares (P&L: ${float(pos.unrealized_pl):.2f})")
            
            confirm = input(f"\n⚠️  Type 'CLOSE ALL' to confirm: ").strip()
            
            if confirm != 'CLOSE ALL':
                print("❌ Cancelled - Safety check failed")
                return
            
            print("\n🔄 Closing all positions...")
            
            # Close all positions
            try:
                result = self.api.close_all_positions()
                print("✅ Close all positions command sent successfully!")
                
                # Show individual results if available
                if hasattr(result, '__iter__'):
                    for order in result:
                        if hasattr(order, 'symbol'):
                            print(f"  • {order.symbol}: Order {order.id} ({order.status})")
                
                return True
                
            except Exception as e:
                print(f"❌ Error with close_all_positions(): {e}")
                print("🔄 Falling back to individual closures...")
                
                # Fallback: close each position individually
                closed_count = 0
                for pos in positions:
                    if self.close_position_silent(pos.symbol):
                        closed_count += 1
                
                print(f"\n📊 Closed {closed_count}/{len(positions)} positions")
                return closed_count == len(positions)
                
        except Exception as e:
            print(f"❌ Error in close_all: {e}")
            return False
    
    def close_position_silent(self, symbol):
        """Close position without prompts (for batch operations)"""
        try:
            position = self.api.get_position(symbol.upper())
            qty = int(position.qty)
            abs_qty = abs(qty)
            
            if qty > 0:
                order = self.api.submit_order(
                    symbol=symbol.upper(),
                    qty=abs_qty,
                    side='sell',
                    type='market',
                    time_in_force='day'
                )
            else:
                order = self.api.submit_order(
                    symbol=symbol.upper(),
                    qty=abs_qty,
                    side='buy',
                    type='market',
                    time_in_force='day'
                )
            
            print(f"✅ {symbol.upper()} closed (Order: {order.id})")
            return True
            
        except Exception as e:
            print(f"❌ Failed to close {symbol}: {e}")
            return False

def main():
    """Main function with argument parsing"""
    parser = argparse.ArgumentParser(description='Close stock positions quickly')
    parser.add_argument('--symbol', '-s', type=str, help='Symbol to close (e.g., AAPL)')
    parser.add_argument('--list', '-l', action='store_true', help='List all positions')
    parser.add_argument('--close-all', action='store_true', help='Close ALL positions')
    parser.add_argument('--interactive', '-i', action='store_true', help='Interactive mode')
    
    args = parser.parse_args()
    
    try:
        closer = QuickTradeCloser()
        
        # Command line modes
        if args.list:
            closer.list_positions()
        
        elif args.close_all:
            closer.close_all_positions()
        
        elif args.symbol:
            closer.close_position(args.symbol)
        
        # Interactive mode (default if no args)
        else:
            print("\n🎯 QUICK TRADE CLOSER - Interactive Mode")
            
            while True:
                print("\n" + "="*50)
                print("                   OPTIONS")
                print("="*50)
                print("1. 📊 List all positions")
                print("2. 🎯 Close specific position")
                print("3. ⚠️  Close ALL positions")
                print("4. 🚪 Exit")
                print("="*50)
                
                choice = input("Select option (1-4): ").strip()
                
                if choice == '1':
                    closer.list_positions()
                
                elif choice == '2':
                    positions = closer.list_positions()
                    if positions:
                        symbol = input("\n📈 Enter symbol to close: ").strip()
                        if symbol:
                            closer.close_position(symbol)
                
                elif choice == '3':
                    closer.close_all_positions()
                
                elif choice == '4':
                    print("👋 Goodbye!")
                    break
                
                else:
                    print("❌ Invalid choice. Please select 1-4.")
    
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user. Goodbye!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")

if __name__ == "__main__":
    main()
