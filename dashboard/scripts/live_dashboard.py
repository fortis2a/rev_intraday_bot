#!/usr/bin/env python3
"""
Live Position Dashboard
Real-time monitoring of all positions and protection orders
"""

import os
import sys
import time
from datetime import datetime
import alpaca_trade_api as tradeapi

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import config

class LiveDashboard:
    def __init__(self):
        self.api = tradeapi.REST(
            config['ALPACA_API_KEY'],
            config['ALPACA_SECRET_KEY'],
            config['ALPACA_BASE_URL'],
            api_version='v2'
        )

    def get_dashboard_data(self):
        """Get all current positions and orders"""
        try:
            positions = self.api.list_positions()
            orders = self.api.list_orders(status='open')
            account = self.api.get_account()
            
            return {
                'positions': positions,
                'orders': orders,
                'account': account,
                'timestamp': datetime.now()
            }
        except Exception as e:
            print(f"Error fetching data: {e}")
            return None

    def display_dashboard(self):
        """Display live dashboard"""
        while True:
            try:
                # Clear screen
                os.system('cls' if os.name == 'nt' else 'clear')
                
                data = self.get_dashboard_data()
                if not data:
                    print("❌ Error fetching data")
                    time.sleep(30)
                    continue
                
                timestamp = data['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
                
                print("🔴 LIVE TRADING DASHBOARD")
                print("=" * 80)
                print(f"⏰ Last Update: {timestamp}")
                print(f"💰 Account Equity: ${float(data['account'].equity):,.2f}")
                print(f"📈 Day P&L: ${float(data['account'].unrealized_pl):+,.2f}")
                print("=" * 80)
                
                # Positions Section
                print("\n📊 CURRENT POSITIONS")
                print("-" * 80)
                
                if not data['positions']:
                    print("   No positions found")
                else:
                    total_unrealized = 0
                    for pos in data['positions']:
                        side = "LONG" if float(pos.qty) > 0 else "SHORT"
                        entry = float(pos.avg_entry_price)
                        current = float(pos.market_value) / float(pos.qty)
                        unrealized = float(pos.unrealized_pl)
                        total_unrealized += unrealized
                        
                        if side == "LONG":
                            profit_pct = (current - entry) / entry * 100
                        else:
                            profit_pct = (entry - current) / entry * 100
                        
                        status = "🟢 PROFIT" if profit_pct > 0 else "🔴 LOSS"
                        
                        print(f"   {pos.symbol:<6} {side:<5} | Entry: ${entry:>7.2f} | "
                              f"Current: ${current:>7.2f} | {profit_pct:>+6.2f}% | "
                              f"${unrealized:>+8.2f} | {status}")
                    
                    print("-" * 80)
                    print(f"   TOTAL UNREALIZED P&L: ${total_unrealized:>+8.2f}")
                
                # Orders Section
                print("\n🛡️  ACTIVE PROTECTION ORDERS")
                print("-" * 80)
                
                if not data['orders']:
                    print("   No active orders")
                else:
                    for order in data['orders']:
                        order_type = order.order_type.upper()
                        side = order.side.upper()
                        symbol = order.symbol
                        qty = order.qty
                        
                        if order.stop_price:
                            price = f"Stop: ${float(order.stop_price):.2f}"
                        elif order.limit_price:
                            price = f"Limit: ${float(order.limit_price):.2f}"
                        else:
                            price = "Market"
                        
                        purpose = "🛑 STOP LOSS" if order_type == "STOP" else "🎯 TAKE PROFIT"
                        
                        print(f"   {symbol:<6} {side:<4} {qty:<3} | {order_type:<12} | "
                              f"{price:<15} | {purpose}")
                
                # Risk Assessment
                print("\n⚠️  RISK ASSESSMENT")
                print("-" * 80)
                
                protected_positions = 0
                unprotected_positions = 0
                
                for pos in data['positions']:
                    symbol_orders = [o for o in data['orders'] if o.symbol == pos.symbol]
                    if symbol_orders:
                        protected_positions += 1
                    else:
                        unprotected_positions += 1
                        side = "LONG" if float(pos.qty) > 0 else "SHORT"
                        print(f"   ⚠️  {pos.symbol} ({side}) - NO PROTECTION ORDERS")
                
                if unprotected_positions == 0:
                    print("   ✅ All positions are protected with stop/profit orders")
                else:
                    print(f"   ⚠️  {unprotected_positions} positions WITHOUT protection")
                
                print("\n" + "=" * 80)
                print("🔄 Auto-refresh in 30 seconds... (Ctrl+C to exit)")
                print("=" * 80)
                
                time.sleep(30)
                
            except KeyboardInterrupt:
                print("\n\n🛑 Dashboard stopped by user")
                break
            except Exception as e:
                print(f"Error in dashboard: {e}")
                time.sleep(30)

if __name__ == "__main__":
    dashboard = LiveDashboard()
    dashboard.display_dashboard()
