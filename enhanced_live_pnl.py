#!/usr/bin/env python3
"""
📊 Enhanced Live P&L Monitor
Real-time P&L tracking with per-stock breakdown and summary
"""

import sys
import time
import os
from datetime import datetime
from pathlib import Path
import subprocess

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from utils.alpaca_trader import AlpacaTrader
from config import config

class EnhancedLivePnLMonitor:
    """Enhanced live P&L monitor with per-stock breakdown"""
    
    def __init__(self):
        self.trader = AlpacaTrader()
        self.watchlist = ["IONQ", "PG", "QBTS", "RGTI", "JNJ"]
        self.previous_equity = None
        self.session_start_equity = None
        self.position_history = {}
        self.daily_realized_pnl = 0.0
        self.daily_unrealized_pnl = 0.0
        self.stock_realized_pnl = {symbol: 0.0 for symbol in self.watchlist}
        self.stock_unrealized_pnl = {symbol: 0.0 for symbol in self.watchlist}
        
    def clear_screen(self):
        """Clear the console screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def get_portfolio_history(self):
        """Get portfolio history to calculate realized P&L"""
        try:
            from datetime import datetime, timedelta
            import pytz
            
            # Get today's date in ET timezone
            et_tz = pytz.timezone('America/New_York')
            today = datetime.now(et_tz).date()
            
            # Get portfolio history for today
            portfolio_history = self.trader.trading_client.get_portfolio_history(
                period="1D",
                timeframe="1Min"
            )
            
            if portfolio_history and hasattr(portfolio_history, 'equity'):
                equity_values = portfolio_history.equity
                if equity_values and len(equity_values) > 0:
                    start_equity = equity_values[0]
                    current_equity = equity_values[-1]
                    total_pnl = current_equity - start_equity
                    return {
                        'start_equity': start_equity,
                        'current_equity': current_equity,
                        'total_pnl': total_pnl,
                        'equity_history': equity_values
                    }
            
            return None
        except Exception as e:
            print(f"Error getting portfolio history: {e}")
            return None
    
    def get_orders_today(self):
        """Get today's orders to calculate realized P&L per stock"""
        try:
            from datetime import datetime, timedelta
            import pytz
            from alpaca.trading.enums import OrderStatus
            
            # Get today's date in ET timezone
            et_tz = pytz.timezone('America/New_York')
            today = datetime.now(et_tz).date()
            
            # Get orders from today
            orders = self.trader.trading_client.get_orders(
                status=OrderStatus.FILLED,
                limit=100,
                nested=True
            )
            
            # Calculate realized P&L per stock from filled orders
            stock_pnl = {symbol: 0.0 for symbol in self.watchlist}
            
            for order in orders:
                if order.symbol in self.watchlist and order.filled_at:
                    # Check if order was filled today
                    filled_date = order.filled_at.date()
                    if filled_date == today:
                        # This is a simplified calculation - you'd need to track buy/sell pairs
                        # For now, we'll rely on portfolio history for total P&L
                        pass
            
            return stock_pnl
        except Exception as e:
            print(f"Error getting orders: {e}")
            return {symbol: 0.0 for symbol in self.watchlist}
    
    def get_account_info(self):
        """Get current account information with P&L details"""
        try:
            account = self.trader.trading_client.get_account()
            
            # Get additional P&L information
            portfolio_history = self.get_portfolio_history()
            
            account_info = {
                'equity': float(account.equity),
                'buying_power': float(account.buying_power),
                'day_trade_count': getattr(account, 'day_trade_count', 0),
                'pattern_day_trader': getattr(account, 'pattern_day_trader', False),
                'portfolio_value': float(account.portfolio_value) if hasattr(account, 'portfolio_value') else float(account.equity)
            }
            
            # Add portfolio history data if available
            if portfolio_history:
                account_info.update({
                    'start_equity': portfolio_history['start_equity'],
                    'total_session_pnl': portfolio_history['total_pnl'],
                    'equity_history': portfolio_history['equity_history']
                })
            
            return account_info
        except Exception as e:
            print(f"Error getting account info: {e}")
            return None
    
    def get_positions(self):
        """Get current positions with P&L"""
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
                        'current_price': float(pos.current_price) if pos.current_price else 0
                    }
            
            return position_data
        except Exception as e:
            print(f"Error getting positions: {e}")
            return {}
    
    def get_stock_prices(self):
        """Get current stock prices for watchlist"""
        try:
            prices = {}
            for symbol in self.watchlist:
                try:
                    # Try to get latest trade first
                    trade = self.trader.data_client.get_latest_trade(symbol)
                    if trade and hasattr(trade, 'price'):
                        prices[symbol] = float(trade.price)
                    else:
                        # Fallback to quote
                        quote = self.trader.data_client.get_latest_quote(symbol)
                        if quote and hasattr(quote, 'bid_price') and quote.bid_price:
                            prices[symbol] = float(quote.bid_price)
                        else:
                            prices[symbol] = 0.0
                except Exception as e:
                    print(f"Error getting price for {symbol}: {e}")
                    prices[symbol] = 0.0
            return prices
        except Exception as e:
            print(f"Error getting stock prices: {e}")
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
    
    def display_dashboard(self):
        """Display the live P&L dashboard with comprehensive P&L tracking"""
        self.clear_screen()
        
        # Header
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print("📊 ENHANCED LIVE P&L MONITOR")
        print("=" * 70)
        print(f"🕐 {current_time} ET")
        print(f"🎯 Quantum Watchlist: {', '.join(self.watchlist)}")
        print("=" * 70)
        
        # Get data
        account_info = self.get_account_info()
        positions = self.get_positions()
        stock_prices = self.get_stock_prices()
        
        if not account_info:
            print("❌ Unable to connect to Alpaca")
            return
        
        current_equity = account_info['equity']
        
        # Calculate P&L from multiple sources
        total_unrealized_pnl = sum(pos.get('unrealized_pnl', 0) for pos in positions.values())
        
        # Use portfolio history if available, otherwise fallback to session calculation
        if 'total_session_pnl' in account_info:
            total_session_pnl = account_info['total_session_pnl']
            start_equity = account_info['start_equity']
        else:
            # Initialize session start equity
            if self.session_start_equity is None:
                self.session_start_equity = current_equity - total_unrealized_pnl  # Adjust for current unrealized
            start_equity = self.session_start_equity
            total_session_pnl = current_equity - start_equity
        
        # Calculate realized P&L (total session - unrealized)
        realized_pnl = total_session_pnl - total_unrealized_pnl
        session_pnl_pct = (total_session_pnl / start_equity) * 100 if start_equity > 0 else 0
        
        # Account Summary with comprehensive P&L
        print(f"\n💰 COMPREHENSIVE P&L SUMMARY:")
        print(f"   Total Equity: ${current_equity:,.2f}")
        print(f"   Starting Equity: ${start_equity:,.2f}")
        print(f"   Buying Power: ${account_info['buying_power']:,.2f}")
        print(f"   ─────────────────────────────────────")
        print(f"   📈 Total Session P&L: {self.format_pnl(total_session_pnl)} ({self.format_pnl(session_pnl_pct, True)})")
        print(f"   💎 Unrealized P&L: {self.format_pnl(total_unrealized_pnl)}")
        print(f"   ✅ Realized P&L: {self.format_pnl(realized_pnl)}")
        print(f"   📊 Day Trades Used: {account_info['day_trade_count']}/3")
        
        # Position Details with enhanced P&L breakdown
        print(f"\n📊 POSITION DETAILS:")
        print("─" * 70)
        print(f"{'Symbol':<8} {'Qty':<10} {'Price':<10} {'Unrealized':<15} {'P&L%':<10} {'Value':<12}")
        print("─" * 70)
        
        total_position_value = 0
        
        for symbol in self.watchlist:
            if symbol in positions:
                pos = positions[symbol]
                qty = pos['qty']
                price = pos['current_price']
                unrealized_pnl = pos['unrealized_pnl']
                pnl_pct = pos['unrealized_pnl_pct']
                value = pos['market_value']
                side = pos['side']
                
                total_position_value += abs(value)
                
                side_symbol = "📈" if side == "long" else "📉"
                print(f"{symbol:<8} {side_symbol}{qty:<8.0f} ${price:<9.2f} {self.format_pnl(unrealized_pnl):<23} {self.format_pnl(pnl_pct, True):<18} ${value:,.0f}")
            else:
                # Show current price even if no position
                current_price = stock_prices.get(symbol, 0)
                print(f"{symbol:<8} {'--':<10} ${current_price:<9.2f} {'No Position':<23} {'--':<18} {'--'}")
        
        print("─" * 70)
        print(f"{'TOTAL':<8} {'':<10} {'':<10} {self.format_pnl(total_unrealized_pnl):<23} {'':<18} ${total_position_value:,.0f}")
        
        # Market Status
        print(f"\n📈 MARKET PRICES:")
        print("─" * 40)
        for symbol in self.watchlist:
            price = stock_prices.get(symbol, 0)
            if symbol in positions:
                status = f"📊 HOLDING ({positions[symbol]['side'].upper()})"
            else:
                status = "👀 WATCHING"
            print(f"{symbol:<8} ${price:<10.2f} {status}")
        
        # Enhanced Performance Metrics
        print(f"\n📊 COMPREHENSIVE PERFORMANCE:")
        print(f"   Active Positions: {len(positions)}")
        print(f"   Total Position Value: ${total_position_value:,.2f}")
        print(f"   Portfolio Utilization: {(total_position_value / current_equity * 100):.1f}%")
        
        if len(positions) > 0:
            avg_unrealized_pnl_pct = sum(pos['unrealized_pnl_pct'] for pos in positions.values()) / len(positions)
            print(f"   Average Unrealized P&L%: {self.format_pnl(avg_unrealized_pnl_pct, True)}")
        
        # Show equity trend if available
        if 'equity_history' in account_info and len(account_info['equity_history']) > 1:
            equity_history = account_info['equity_history']
            recent_change = equity_history[-1] - equity_history[-2] if len(equity_history) > 1 else 0
            trend_indicator = "📈" if recent_change > 0 else "📉" if recent_change < 0 else "➡️"
            print(f"   Recent Trend: {trend_indicator} {self.format_pnl(recent_change)} (last minute)")
        
        # Status Footer
        print(f"\n🔄 Live data from Alpaca | Updates every 5 seconds | Press Ctrl+C to exit")
        print(f"💡 Showing TOTAL P&L (realized + unrealized) and position breakdown")
        print("=" * 70)
    
    def run(self):
        """Run the live P&L monitor"""
        print("📊 Starting Enhanced Live P&L Monitor...")
        print("🔗 Connecting to Alpaca...")
        
        try:
            while True:
                self.display_dashboard()
                time.sleep(5)  # Update every 5 seconds
                
        except KeyboardInterrupt:
            print("\n\n👋 Live P&L Monitor stopped")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("🔄 Restarting in 10 seconds...")
            time.sleep(10)
            self.run()  # Restart on error

if __name__ == "__main__":
    monitor = EnhancedLivePnLMonitor()
    monitor.run()
