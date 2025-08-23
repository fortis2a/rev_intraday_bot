#!/usr/bin/env python3
"""
Today's Trading Performance Analysis - Quick Daily Summary
Generates a comprehensive end-of-day analysis for today's trading session
"""

import os
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

import alpaca_trade_api as tradeapi

from config import config
from utils.logger import setup_logger


class TodayAnalysis:
    """Generate today's trading performance analysis"""
    
    def __init__(self):
        self.logger = setup_logger('today_analysis')
        self.today = date.today()
        
        # Connect to Alpaca
        self.api = tradeapi.REST(
            config['ALPACA_API_KEY'],
            config['ALPACA_SECRET_KEY'], 
            config['ALPACA_BASE_URL']
        )
        
        print(f"📊 DAILY TRADING ANALYSIS - {self.today.strftime('%B %d, %Y')}")
        print("="*70)
    
    def get_today_orders(self):
        """Get all orders from today"""
        try:
            # Get orders from today with proper ISO format
            today_start = datetime.combine(self.today, datetime.min.time())
            formatted_date = today_start.strftime('%Y-%m-%dT%H:%M:%SZ')
            
            orders = self.api.list_orders(
                status='all',
                after=formatted_date
            )
            
            # Filter for filled orders only
            filled_orders = [o for o in orders if o.status == 'filled']
            
            print(f"📋 Found {len(filled_orders)} filled orders today")
            return filled_orders
            
        except Exception as e:
            print(f"❌ Error getting orders: {e}")
            return []
    
    def get_account_info(self):
        """Get current account information"""
        try:
            account = self.api.get_account()
            
            print(f"\n💰 ACCOUNT SUMMARY:")
            print(f"  💵 Total Equity: ${float(account.equity):,.2f}")
            print(f"  💸 Buying Power: ${float(account.buying_power):,.2f}")
            print(f"  💴 Day Trade Buying Power: ${float(account.daytrading_buying_power):,.2f}")
            print(f"  📊 Portfolio Value: ${float(account.portfolio_value):,.2f}")
            
            return account
            
        except Exception as e:
            print(f"❌ Error getting account info: {e}")
            return None
    
    def analyze_trades(self, orders):
        """Analyze today's trading performance"""
        if not orders:
            print("📭 No trades executed today")
            return
        
        print(f"\n🔍 TRADE ANALYSIS:")
        print("="*50)
        
        # Group orders by symbol
        trades_by_symbol = {}
        total_pnl = 0
        buy_orders = []
        sell_orders = []
        
        for order in orders:
            symbol = order.symbol
            side = order.side
            qty = float(order.filled_qty)
            price = float(order.filled_avg_price)
            value = qty * price
            
            if symbol not in trades_by_symbol:
                trades_by_symbol[symbol] = {'buys': [], 'sells': []}
            
            order_data = {
                'qty': qty,
                'price': price,
                'value': value,
                'time': order.filled_at,
                'id': order.id
            }
            
            if side == 'buy':
                trades_by_symbol[symbol]['buys'].append(order_data)
                buy_orders.append(order_data)
            else:
                trades_by_symbol[symbol]['sells'].append(order_data)
                sell_orders.append(order_data)
        
        # Calculate P&L for each symbol
        print(f"📈 SYMBOL PERFORMANCE:")
        print(f"{'Symbol':<8} {'Trades':<8} {'P&L $':<12} {'P&L %':<10} {'Volume $':<12}")
        print("-"*55)
        
        for symbol, trades in trades_by_symbol.items():
            buys = trades['buys']
            sells = trades['sells']
            
            total_bought = sum(t['qty'] for t in buys)
            total_sold = sum(t['qty'] for t in sells)
            
            buy_value = sum(t['value'] for t in buys)
            sell_value = sum(t['value'] for t in sells)
            
            # Calculate average prices
            avg_buy = buy_value / total_bought if total_bought > 0 else 0
            avg_sell = sell_value / total_sold if total_sold > 0 else 0
            
            # Calculate P&L
            if total_bought > 0 and total_sold > 0:
                closed_qty = min(total_bought, total_sold)
                pnl = (avg_sell - avg_buy) * closed_qty
                pnl_pct = (pnl / (avg_buy * closed_qty)) * 100 if avg_buy > 0 else 0
                total_pnl += pnl
                
                status = "🟢" if pnl >= 0 else "🔴"
                total_volume = buy_value + sell_value
                
                print(f"{status} {symbol:<7} {len(buys)+len(sells):<8} ${pnl:<11.2f} {pnl_pct:+.1f}%     ${total_volume:,.0f}")
        
        print("-"*55)
        print(f"💰 TOTAL P&L: ${total_pnl:.2f}")
        
        # Trading statistics
        print(f"\n📊 TRADING STATISTICS:")
        print(f"  🎯 Total Orders: {len(orders)}")
        print(f"  📥 Buy Orders: {len(buy_orders)}")
        print(f"  📤 Sell Orders: {len(sell_orders)}")
        print(f"  💵 Total Buy Volume: ${sum(o['value'] for o in buy_orders):,.2f}")
        print(f"  💸 Total Sell Volume: ${sum(o['value'] for o in sell_orders):,.2f}")
        
        # Time analysis
        if orders:
            first_trade = min(orders, key=lambda x: x.filled_at)
            last_trade = max(orders, key=lambda x: x.filled_at)
            
            print(f"\n⏰ TIME ANALYSIS:")
            print(f"  🌅 First Trade: {first_trade.filled_at.strftime('%H:%M:%S')} ({first_trade.symbol})")
            print(f"  🌆 Last Trade: {last_trade.filled_at.strftime('%H:%M:%S')} ({last_trade.symbol})")
        
        return total_pnl
    
    def get_portfolio_performance(self):
        """Get portfolio performance for today"""
        try:
            # Get portfolio history for today
            portfolio_history = self.api.get_portfolio_history(
                period='1D',
                timeframe='1Min'
            )
            
            if portfolio_history and hasattr(portfolio_history, 'equity'):
                equity_values = portfolio_history.equity
                
                if len(equity_values) > 1:
                    start_value = equity_values[0]
                    end_value = equity_values[-1]
                    day_pnl = end_value - start_value
                    day_pnl_pct = (day_pnl / start_value) * 100 if start_value > 0 else 0
                    
                    print(f"\n📈 PORTFOLIO PERFORMANCE:")
                    print(f"  🌅 Start of Day: ${start_value:,.2f}")
                    print(f"  🌆 End of Day: ${end_value:,.2f}")
                    print(f"  📊 Daily P&L: ${day_pnl:+.2f} ({day_pnl_pct:+.2f}%)")
                    
                    # Find peak and trough
                    max_value = max(equity_values)
                    min_value = min(equity_values)
                    
                    print(f"  📈 Peak Value: ${max_value:,.2f}")
                    print(f"  📉 Lowest Value: ${min_value:,.2f}")
                    print(f"  📏 Daily Range: ${max_value - min_value:,.2f}")
                    
                    return day_pnl
        
        except Exception as e:
            print(f"❌ Error getting portfolio performance: {e}")
        
        return 0
    
    def check_current_positions(self):
        """Check if any positions are still open"""
        try:
            positions = self.api.list_positions()
            
            if positions:
                print(f"\n⚠️  OPEN POSITIONS ({len(positions)}):")
                print(f"{'Symbol':<8} {'Side':<6} {'Qty':<8} {'Value':<12} {'P&L':<12}")
                print("-"*50)
                
                total_position_value = 0
                total_unrealized_pnl = 0
                
                for pos in positions:
                    side = "LONG" if float(pos.qty) > 0 else "SHORT"
                    qty = abs(float(pos.qty))
                    value = float(pos.market_value)
                    pnl = float(pos.unrealized_pl)
                    
                    total_position_value += abs(value)
                    total_unrealized_pnl += pnl
                    
                    status = "🟢" if pnl >= 0 else "🔴"
                    print(f"{status} {pos.symbol:<7} {side:<6} {qty:<8.0f} ${abs(value):<11.2f} ${pnl:+.2f}")
                
                print("-"*50)
                print(f"💼 Total Position Value: ${total_position_value:,.2f}")
                print(f"💰 Total Unrealized P&L: ${total_unrealized_pnl:+.2f}")
            else:
                print(f"\n✅ ALL POSITIONS CLOSED")
                print("🏁 Clean slate for tomorrow!")
        
        except Exception as e:
            print(f"❌ Error checking positions: {e}")
    
    def generate_summary(self):
        """Generate complete daily summary"""
        print(f"\n🎯 DAILY SUMMARY - {self.today.strftime('%A, %B %d, %Y')}")
        print("="*70)
        
        # Get account info
        account = self.get_account_info()
        
        # Get and analyze trades
        orders = self.get_today_orders()
        trade_pnl = self.analyze_trades(orders)
        
        # Get portfolio performance
        portfolio_pnl = self.get_portfolio_performance()
        
        # Check open positions
        self.check_current_positions()
        
        # Final summary
        print(f"\n🏆 FINAL SUMMARY:")
        print("="*30)
        if trade_pnl and trade_pnl != 0:
            print(f"💹 Trading P&L: ${trade_pnl:+.2f}")
        if portfolio_pnl and portfolio_pnl != 0:
            print(f"📊 Portfolio P&L: ${portfolio_pnl:+.2f}")
        
        print(f"📅 Analysis Date: {self.today}")
        print(f"⏰ Generated: {datetime.now().strftime('%H:%M:%S')}")
        print("\n🎉 Analysis Complete!")

def main():
    """Main function to run today's analysis"""
    try:
        analyzer = TodayAnalysis()
        analyzer.generate_summary()
        
    except KeyboardInterrupt:
        print("\n\n👋 Analysis interrupted by user")
    except Exception as e:
        print(f"❌ Error in analysis: {e}")

if __name__ == "__main__":
    main()
