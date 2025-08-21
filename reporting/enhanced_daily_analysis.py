#!/usr/bin/env python3
"""
Enhanced Daily Analysis - Includes Cross-Day Trades
Captures all P&L realized today, including positions opened yesterday but closed today
"""

import sys
import os
from datetime import datetime, date, timedelta
import pandas as pd
import numpy as np
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

import alpaca_trade_api as tradeapi
from config import config
from utils.logger import setup_logger

class EnhancedDailyAnalysis:
    """Enhanced daily analysis including cross-day trades"""
    
    def __init__(self):
        self.logger = setup_logger('enhanced_daily_analysis')
        self.today = date.today()
        self.yesterday = self.today - timedelta(days=1)
        
        # Connect to Alpaca
        self.api = tradeapi.REST(
            config['ALPACA_API_KEY'],
            config['ALPACA_SECRET_KEY'], 
            config['ALPACA_BASE_URL']
        )
        
        print(f"📊 ENHANCED DAILY ANALYSIS - {self.today.strftime('%B %d, %Y')}")
        print("🔄 Including cross-day trades (opened yesterday, closed today)")
        print("="*75)
    
    def get_extended_orders(self):
        """Get orders from yesterday and today to capture cross-day trades"""
        try:
            # Get orders from yesterday and today
            yesterday_start = datetime.combine(self.yesterday, datetime.min.time())
            formatted_date = yesterday_start.strftime('%Y-%m-%dT%H:%M:%SZ')
            
            orders = self.api.list_orders(
                status='all',
                after=formatted_date
            )
            
            # Filter for filled orders only
            filled_orders = [o for o in orders if o.status == 'filled']
            
            # Separate today's orders vs yesterday's orders
            today_orders = []
            yesterday_orders = []
            
            for order in filled_orders:
                if order.filled_at:
                    order_date = order.filled_at.date()
                    if order_date == self.today:
                        today_orders.append(order)
                    elif order_date == self.yesterday:
                        yesterday_orders.append(order)
            
            print(f"📋 Found {len(today_orders)} orders filled today")
            print(f"📋 Found {len(yesterday_orders)} orders filled yesterday")
            
            return today_orders, yesterday_orders
            
        except Exception as e:
            print(f"❌ Error getting orders: {e}")
            return [], []
    
    def match_cross_day_trades(self, today_orders, yesterday_orders):
        """Match buy/sell orders across days to find cross-day trades"""
        cross_day_trades = []
        today_only_trades = []
        
        # Group orders by symbol
        yesterday_by_symbol = {}
        today_by_symbol = {}
        
        for order in yesterday_orders:
            symbol = order.symbol
            if symbol not in yesterday_by_symbol:
                yesterday_by_symbol[symbol] = []
            yesterday_by_symbol[symbol].append(order)
        
        for order in today_orders:
            symbol = order.symbol
            if symbol not in today_by_symbol:
                today_by_symbol[symbol] = []
            today_by_symbol[symbol].append(order)
        
        # Find cross-day trades for each symbol
        all_symbols = set(list(yesterday_by_symbol.keys()) + list(today_by_symbol.keys()))
        
        for symbol in all_symbols:
            yesterday_symbol_orders = yesterday_by_symbol.get(symbol, [])
            today_symbol_orders = today_by_symbol.get(symbol, [])
            
            # Look for cross-day patterns (buy yesterday, sell today or vice versa)
            for yesterday_order in yesterday_symbol_orders:
                for today_order in today_symbol_orders:
                    # Check if they form a complete trade (opposite sides)
                    if yesterday_order.side != today_order.side:
                        cross_day_trades.append({
                            'symbol': symbol,
                            'open_order': yesterday_order,
                            'close_order': today_order,
                            'open_date': yesterday_order.filled_at.date(),
                            'close_date': today_order.filled_at.date()
                        })
                        break  # Match found, move to next yesterday order
            
            # Add today-only trades for this symbol
            if symbol in today_by_symbol:
                # Group today's orders by buy/sell
                today_buys = [o for o in today_symbol_orders if o.side == 'buy']
                today_sells = [o for o in today_symbol_orders if o.side == 'sell']
                
                # Match buys and sells from today
                min_pairs = min(len(today_buys), len(today_sells))
                for i in range(min_pairs):
                    today_only_trades.append({
                        'symbol': symbol,
                        'buy_order': today_buys[i],
                        'sell_order': today_sells[i],
                        'same_day': True
                    })
        
        return cross_day_trades, today_only_trades
    
    def analyze_cross_day_performance(self, cross_day_trades, today_only_trades):
        """Analyze performance including cross-day trades"""
        print(f"\n🔄 CROSS-DAY TRADE ANALYSIS:")
        print("="*60)
        
        if cross_day_trades:
            print(f"📅 Cross-Day Trades (opened yesterday, closed today): {len(cross_day_trades)}")
            print(f"{'Symbol':<8} {'Open':<12} {'Close':<12} {'P&L $':<12} {'P&L %':<10}")
            print("-"*60)
            
            total_cross_day_pnl = 0
            
            for trade in cross_day_trades:
                symbol = trade['symbol']
                open_order = trade['open_order']
                close_order = trade['close_order']
                
                open_price = float(open_order.filled_avg_price)
                close_price = float(close_order.filled_avg_price)
                qty = min(float(open_order.filled_qty), float(close_order.filled_qty))
                
                # Calculate P&L based on trade direction
                if open_order.side == 'buy':  # Long position
                    pnl = (close_price - open_price) * qty
                else:  # Short position
                    pnl = (open_price - close_price) * qty
                
                pnl_pct = (pnl / (open_price * qty)) * 100 if open_price > 0 else 0
                total_cross_day_pnl += pnl
                
                status = "🟢" if pnl >= 0 else "🔴"
                print(f"{status} {symbol:<7} ${open_price:<11.2f} ${close_price:<11.2f} ${pnl:<11.2f} {pnl_pct:+.1f}%")
            
            print("-"*60)
            print(f"💰 Cross-Day P&L: ${total_cross_day_pnl:.2f}")
        else:
            print("📭 No cross-day trades found")
            total_cross_day_pnl = 0
        
        # Analyze today-only trades
        print(f"\n📅 TODAY-ONLY TRADES:")
        print("="*45)
        
        if today_only_trades:
            print(f"🎯 Same-Day Trades: {len(today_only_trades)}")
            print(f"{'Symbol':<8} {'Buy':<12} {'Sell':<12} {'P&L $':<12} {'P&L %':<10}")
            print("-"*60)
            
            total_same_day_pnl = 0
            
            for trade in today_only_trades:
                symbol = trade['symbol']
                buy_order = trade['buy_order']
                sell_order = trade['sell_order']
                
                buy_price = float(buy_order.filled_avg_price)
                sell_price = float(sell_order.filled_avg_price)
                qty = min(float(buy_order.filled_qty), float(sell_order.filled_qty))
                
                pnl = (sell_price - buy_price) * qty
                pnl_pct = (pnl / (buy_price * qty)) * 100 if buy_price > 0 else 0
                total_same_day_pnl += pnl
                
                status = "🟢" if pnl >= 0 else "🔴"
                print(f"{status} {symbol:<7} ${buy_price:<11.2f} ${sell_price:<11.2f} ${pnl:<11.2f} {pnl_pct:+.1f}%")
            
            print("-"*60)
            print(f"💰 Same-Day P&L: ${total_same_day_pnl:.2f}")
        else:
            print("📭 No same-day complete trades found")
            total_same_day_pnl = 0
        
        return total_cross_day_pnl + total_same_day_pnl
    
    def get_account_info(self):
        """Get current account information"""
        try:
            account = self.api.get_account()
            
            print(f"\n💰 ACCOUNT SUMMARY:")
            print(f"  💵 Total Equity: ${float(account.equity):,.2f}")
            print(f"  💸 Buying Power: ${float(account.buying_power):,.2f}")
            print(f"  📊 Portfolio Value: ${float(account.portfolio_value):,.2f}")
            
            return account
            
        except Exception as e:
            print(f"❌ Error getting account info: {e}")
            return None
    
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
                
                total_unrealized_pnl = 0
                
                for pos in positions:
                    side = "LONG" if float(pos.qty) > 0 else "SHORT"
                    qty = abs(float(pos.qty))
                    value = float(pos.market_value)
                    pnl = float(pos.unrealized_pl)
                    
                    total_unrealized_pnl += pnl
                    
                    status = "🟢" if pnl >= 0 else "🔴"
                    print(f"{status} {pos.symbol:<7} {side:<6} {qty:<8.0f} ${abs(value):<11.2f} ${pnl:+.2f}")
                
                print("-"*50)
                print(f"💰 Total Unrealized P&L: ${total_unrealized_pnl:+.2f}")
            else:
                print(f"\n✅ ALL POSITIONS CLOSED")
                print("🏁 Clean slate for tomorrow!")
        
        except Exception as e:
            print(f"❌ Error checking positions: {e}")
    
    def generate_enhanced_summary(self):
        """Generate complete enhanced daily summary"""
        print(f"\n🎯 ENHANCED DAILY SUMMARY - {self.today.strftime('%A, %B %d, %Y')}")
        print("="*75)
        
        # Get account info
        account = self.get_account_info()
        
        # Get extended orders (yesterday + today)
        today_orders, yesterday_orders = self.get_extended_orders()
        
        # Match cross-day trades
        cross_day_trades, today_only_trades = self.match_cross_day_trades(today_orders, yesterday_orders)
        
        # Analyze performance including cross-day trades
        total_realized_pnl = self.analyze_cross_day_performance(cross_day_trades, today_only_trades)
        
        # Get portfolio performance
        portfolio_pnl = self.get_portfolio_performance()
        
        # Check open positions
        self.check_current_positions()
        
        # Final enhanced summary
        print(f"\n🏆 ENHANCED FINAL SUMMARY:")
        print("="*40)
        print(f"🔄 Cross-Day Trades: {len(cross_day_trades)}")
        print(f"📅 Same-Day Trades: {len(today_only_trades)}")
        if total_realized_pnl != 0:
            print(f"💹 Total Realized P&L: ${total_realized_pnl:+.2f}")
        if portfolio_pnl != 0:
            print(f"📊 Portfolio P&L: ${portfolio_pnl:+.2f}")
        
        print(f"📅 Analysis Date: {self.today}")
        print(f"⏰ Generated: {datetime.now().strftime('%H:%M:%S')}")
        print("\n🎉 Enhanced Analysis Complete!")

def main():
    """Main function to run enhanced daily analysis"""
    try:
        analyzer = EnhancedDailyAnalysis()
        analyzer.generate_enhanced_summary()
        
    except KeyboardInterrupt:
        print("\n\n👋 Analysis interrupted by user")
    except Exception as e:
        print(f"❌ Error in enhanced analysis: {e}")

if __name__ == "__main__":
    main()
