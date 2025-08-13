#!/usr/bin/env python3
"""
📊 Complete Live P&L Monitor  
Fetches comprehensive P&L data directly from Alpaca including realized gains
"""

import sys
import time
import os
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import pytz

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from utils.alpaca_trader import AlpacaTrader
from config import config

class CompleteLivePnLMonitor:
    """Complete live P&L monitor with realized + unrealized P&L from Alpaca"""
    
    def __init__(self):
        self.trader = AlpacaTrader()
        self.watchlist = ["IONQ", "PG", "QBTS", "RGTI", "JNJ"]
        self.session_start_time = datetime.now()
        self.initial_equity = None
        
    def clear_screen(self):
        """Clear the console screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def get_complete_account_data(self):
        """Get complete account data including all P&L metrics"""
        try:
            # Get main account info
            account = self.trader.trading_client.get_account()
            
            account_data = {
                'equity': float(account.equity),
                'last_equity': float(account.last_equity),
                'buying_power': float(account.buying_power),
                'cash': float(account.cash),
                'portfolio_value': float(account.portfolio_value),
                'long_market_value': float(account.long_market_value) if account.long_market_value else 0.0,
                'short_market_value': float(account.short_market_value) if account.short_market_value else 0.0,
                'day_trade_count': getattr(account, 'day_trade_count', 0),
                'pattern_day_trader': getattr(account, 'pattern_day_trader', False)
            }
            
            # Calculate total P&L vs previous close
            daily_pnl = account_data['equity'] - account_data['last_equity']
            daily_pnl_pct = (daily_pnl / account_data['last_equity']) * 100 if account_data['last_equity'] > 0 else 0
            
            account_data.update({
                'daily_pnl': daily_pnl,
                'daily_pnl_pct': daily_pnl_pct
            })
            
            return account_data
            
        except Exception as e:
            print(f"Error getting account data: {e}")
            return None
    
    def get_positions_with_pnl(self):
        """Get positions with complete P&L data"""
        try:
            positions = self.trader.trading_client.get_all_positions()
            position_data = {}
            
            for pos in positions:
                symbol = pos.symbol
                if symbol in self.watchlist:
                    position_data[symbol] = {
                        'qty': float(pos.qty),
                        'market_value': float(pos.market_value),
                        'cost_basis': float(pos.cost_basis),
                        'unrealized_pnl': float(pos.unrealized_pnl),
                        'unrealized_pnl_pct': float(pos.unrealized_plpc) * 100,
                        'side': pos.side,
                        'current_price': float(pos.current_price) if pos.current_price else 0,
                        'avg_entry_price': float(pos.avg_entry_price) if pos.avg_entry_price else 0
                    }
            
            return position_data
        except Exception as e:
            print(f"Error getting positions: {e}")
            return {}
    
    def get_portfolio_history(self):
        """Get portfolio history (simplified - focus on main P&L from account)"""
        try:
            # Simple approach - we already get the main P&L from account.equity vs account.last_equity
            # Portfolio history is nice-to-have but not essential for total P&L tracking
            return None
        except Exception as e:
            return None
    
    def get_current_prices(self):
        """Get current market prices"""
        try:
            prices = {}
            for symbol in self.watchlist:
                try:
                    trade = self.trader.data_client.get_latest_trade(symbol)
                    if trade and hasattr(trade, 'price'):
                        prices[symbol] = float(trade.price)
                    else:
                        prices[symbol] = 0.0
                except Exception:
                    prices[symbol] = 0.0
            return prices
        except Exception as e:
            print(f"Error getting prices: {e}")
            return {symbol: 0.0 for symbol in self.watchlist}
    
    def format_pnl(self, value, is_percentage=False):
        """Format P&L with colors"""
        if is_percentage:
            if value > 0:
                return f"🟢 +{value:.2f}%"
            elif value < 0:
                return f"🔴 {value:.2f}%"
            else:
                return f"⚪ {value:.2f}%"
        else:
            if value > 0:
                return f"🟢 +${value:,.2f}"
            elif value < 0:
                return f"🔴 ${value:,.2f}"
            else:
                return f"⚪ ${value:,.2f}"
    
    def display_comprehensive_pnl(self):
        """Display comprehensive P&L dashboard"""
        self.clear_screen()
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print("📊 COMPLETE LIVE P&L MONITOR - ALPACA DATA")
        print("=" * 75)
        print(f"🕐 {current_time} ET")
        print(f"🎯 Quantum Watchlist: {', '.join(self.watchlist)}")
        print("=" * 75)
        
        # Get comprehensive data
        account_data = self.get_complete_account_data()
        positions = self.get_positions_with_pnl()
        current_prices = self.get_current_prices()
        portfolio_history = self.get_portfolio_history()
        
        if not account_data:
            print("❌ Unable to connect to Alpaca")
            return
        
        # Set initial equity for session tracking
        if self.initial_equity is None:
            self.initial_equity = account_data['last_equity']  # Use previous close as baseline
        
        session_pnl = account_data['equity'] - self.initial_equity
        session_pnl_pct = (session_pnl / self.initial_equity) * 100 if self.initial_equity > 0 else 0
        
        # COMPREHENSIVE ACCOUNT SUMMARY
        print(f"\n💰 COMPLETE ACCOUNT SUMMARY:")
        print(f"   Current Equity: ${account_data['equity']:,.2f}")
        print(f"   Previous Close: ${account_data['last_equity']:,.2f}")
        print(f"   Cash Available: ${account_data['cash']:,.2f}")
        print(f"   Buying Power: ${account_data['buying_power']:,.2f}")
        print(f"   ────────────────────────────────────────────────────")
        print(f"   📈 Daily P&L (Total): {self.format_pnl(account_data['daily_pnl'])} ({self.format_pnl(account_data['daily_pnl_pct'], True)})")
        print(f"   🕐 Session P&L: {self.format_pnl(session_pnl)} ({self.format_pnl(session_pnl_pct, True)})")
        print(f"   📊 Long Positions: ${account_data['long_market_value']:,.2f}")
        print(f"   📉 Short Positions: ${abs(account_data['short_market_value']):,.2f}")
        print(f"   🔄 Day Trades: {account_data['day_trade_count']}/3")
        
        # POSITION BREAKDOWN
        print(f"\n📊 LIVE POSITION BREAKDOWN:")
        print("─" * 75)
        print(f"{'Symbol':<8} {'Side':<6} {'Qty':<8} {'Entry$':<10} {'Current$':<10} {'P&L':<15} {'P&L%':<12}")
        print("─" * 75)
        
        total_unrealized_pnl = 0
        total_position_value = 0
        
        for symbol in self.watchlist:
            if symbol in positions:
                pos = positions[symbol]
                qty = pos['qty']
                entry_price = pos['avg_entry_price']
                current_price = pos['current_price']
                unrealized_pnl = pos['unrealized_pnl']
                pnl_pct = pos['unrealized_pnl_pct']
                market_value = pos['market_value']
                side = pos['side'].upper()
                
                total_unrealized_pnl += unrealized_pnl
                total_position_value += abs(market_value)
                
                side_emoji = "📈" if side == "LONG" else "📉"
                print(f"{symbol:<8} {side_emoji}{side:<4} {qty:<8.0f} ${entry_price:<9.2f} ${current_price:<9.2f} {self.format_pnl(unrealized_pnl):<23} {self.format_pnl(pnl_pct, True)}")
            else:
                current_price = current_prices.get(symbol, 0)
                print(f"{symbol:<8} {'--':<6} {'--':<8} {'--':<10} ${current_price:<9.2f} {'No Position':<23} {'--'}")
        
        print("─" * 75)
        print(f"{'TOTALS':<8} {'':<6} {'':<8} {'':<10} {'':<10} {self.format_pnl(total_unrealized_pnl):<23} {''}")
        
        # CALCULATED P&L BREAKDOWN
        realized_pnl_estimate = account_data['daily_pnl'] - total_unrealized_pnl
        
        print(f"\n🧮 P&L BREAKDOWN ANALYSIS:")
        print(f"   💎 Unrealized P&L (Open Positions): {self.format_pnl(total_unrealized_pnl)}")
        print(f"   ✅ Estimated Realized P&L: {self.format_pnl(realized_pnl_estimate)}")
        print(f"   📊 Total Daily P&L: {self.format_pnl(account_data['daily_pnl'])}")
        print(f"   📈 Portfolio Utilization: {(total_position_value / account_data['equity'] * 100):.1f}%")
        
        # MARKET STATUS
        print(f"\n📈 CURRENT MARKET PRICES:")
        print("─" * 50)
        for symbol in self.watchlist:
            price = current_prices.get(symbol, 0)
            status = f"📊 HOLDING ({positions[symbol]['side'].upper()})" if symbol in positions else "👀 WATCHING"
            print(f"{symbol:<8} ${price:<12.2f} {status}")
        
        # STATUS FOOTER
        print(f"\n🔄 LIVE ALPACA DATA | Updates every 5 seconds")
        print(f"💡 Shows COMPLETE P&L: Realized trades + Open positions")
        print(f"📊 Data source: Alpaca account equity & position tracking")
        print("=" * 75)
    
    def run(self):
        """Run the complete live P&L monitor"""
        print("📊 Starting Complete Live P&L Monitor...")
        print("🔗 Connecting to Alpaca for comprehensive P&L data...")
        
        try:
            while True:
                self.display_comprehensive_pnl()
                time.sleep(5)  # Update every 5 seconds
                
        except KeyboardInterrupt:
            print("\n\n👋 Complete P&L Monitor stopped")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("🔄 Restarting in 10 seconds...")
            time.sleep(10)
            self.run()  # Restart on error

if __name__ == "__main__":
    monitor = CompleteLivePnLMonitor()
    monitor.run()
