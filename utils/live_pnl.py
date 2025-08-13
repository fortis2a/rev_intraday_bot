#!/usr/bin/env python3
"""
📱 Live PnL Display - Real-time P&L monitoring during trading hours
Shows current session performance with auto-refresh
"""

import os
import time
import threading
from datetime import datetime
from typing import Dict
import json

from utils.pnl_tracker import get_pnl_tracker
from utils.logger import setup_scalping_loggers
from config import config

class LivePnLDisplay:
    """Real-time P&L display for terminal/console"""
    
    def __init__(self):
        """Initialize live display"""
        self.loggers = setup_scalping_loggers()
        self.logger = self.loggers['live_pnl']
        self.pnl_tracker = get_pnl_tracker()
        
        self.is_running = False
        self.display_thread = None
        self.refresh_interval = 5  # seconds
        
        self.logger.info("📱 Live PnL Display initialized")
    
    def start_display(self):
        """Start the live P&L display"""
        if self.is_running:
            self.logger.warning("⚠️ Display already running")
            return
        
        self.is_running = True
        self.display_thread = threading.Thread(target=self._display_loop, daemon=True)
        self.display_thread.start()
        
        self.logger.info("📱 Live P&L display started")
    
    def stop_display(self):
        """Stop the live P&L display"""
        self.is_running = False
        if self.display_thread:
            self.display_thread.join(timeout=2)
        
        self.logger.info("📱 Live P&L display stopped")
    
    def _display_loop(self):
        """Main display loop"""
        try:
            while self.is_running:
                self._update_display()
                time.sleep(self.refresh_interval)
                
        except Exception as e:
            self.logger.error(f"❌ Display loop error: {e}")
    
    def _update_display(self):
        """Update the P&L display"""
        try:
            # Clear screen (works on Windows and Unix)
            os.system('cls' if os.name == 'nt' else 'clear')
            
            # Get current session data
            session_summary = self.pnl_tracker.get_current_session_pnl()
            
            if not session_summary:
                print("📊 No session data available")
                return
            
            # Display header
            print("=" * 80)
            print("📊 SCALPING BOT - LIVE P&L MONITOR")
            print("=" * 80)
            print(f"🕐 Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"📅 Session: {session_summary['session_date']}")
            print(f"⏱️ Duration: {session_summary['session_duration']}")
            print("=" * 80)
            
            # Main metrics
            total_pnl = session_summary['total_pnl']
            pnl_color = "🟢" if total_pnl >= 0 else "🔴"
            pnl_percentage = ((session_summary['current_balance'] - session_summary['start_balance']) / session_summary['start_balance'] * 100) if session_summary['start_balance'] > 0 else 0
            
            print(f"{pnl_color} TOTAL P&L: ${total_pnl:+.2f} ({pnl_percentage:+.2f}%)")
            print(f"💰 Portfolio Value: ${session_summary['current_balance']:,.2f}")
            print(f"📈 Starting Balance: ${session_summary['start_balance']:,.2f}")
            print()
            
            # Trading metrics
            print("📊 TRADING METRICS:")
            print(f"   🎯 Total Trades: {session_summary['total_trades']}")
            print(f"   ✅ Winning Trades: {session_summary['winning_trades']}")
            print(f"   ❌ Losing Trades: {session_summary['losing_trades']}")
            print(f"   📊 Win Rate: {session_summary['win_rate']:.1f}%")
            print(f"   📈 Average Trade: ${session_summary['avg_trade']:+.2f}")
            print(f"   🏆 Best Trade: ${session_summary['best_trade']:+.2f}")
            print(f"   📉 Worst Trade: ${session_summary['worst_trade']:+.2f}")
            print()
            
            # Risk metrics
            print("⚠️ RISK METRICS:")
            print(f"   📉 Max Drawdown: ${session_summary['max_drawdown']:.2f}")
            print(f"   💎 Max Profit: ${session_summary['max_profit']:.2f}")
            print(f"   🔒 Open Positions: {session_summary['open_positions']}")
            
            # Daily loss limit check
            daily_loss_limit = session_summary['start_balance'] * (config.MAX_DAILY_LOSS_PCT / 100)
            current_loss = max(0, session_summary['start_balance'] - session_summary['current_balance'])
            loss_percentage = (current_loss / daily_loss_limit * 100) if daily_loss_limit > 0 else 0
            
            if loss_percentage > 80:
                print(f"   🚨 DAILY LOSS WARNING: {loss_percentage:.1f}% of limit used!")
            elif loss_percentage > 50:
                print(f"   ⚠️ Daily Loss: {loss_percentage:.1f}% of limit used")
            else:
                print(f"   ✅ Daily Loss: {loss_percentage:.1f}% of limit used")
            
            print()
            
            # Recent trades (last 5)
            recent_trades = self._get_recent_trades()
            if recent_trades:
                print("📋 RECENT TRADES:")
                print("   Time     | Symbol | Side | P&L      | Strategy")
                print("   " + "-" * 50)
                for trade in recent_trades[-5:]:  # Last 5 trades
                    trade_time = datetime.fromisoformat(trade['exit_time']).strftime('%H:%M:%S') if trade.get('exit_time') else 'OPEN'
                    pnl_str = f"${trade['pnl']:+6.2f}" if trade.get('pnl') is not None else "  OPEN "
                    pnl_indicator = "🟢" if trade.get('pnl', 0) >= 0 else "🔴"
                    
                    print(f"   {trade_time} | {trade['symbol']:6} | {trade['side']:4} | {pnl_indicator} {pnl_str} | {trade['strategy'][:10]}")
            else:
                print("📋 No completed trades yet")
            
            print()
            print("=" * 80)
            print("📱 Press Ctrl+C to stop monitoring")
            print("🔄 Auto-refresh every 5 seconds")
            print("=" * 80)
            
        except Exception as e:
            self.logger.error(f"❌ Display update error: {e}")
            print(f"❌ Display error: {e}")
    
    def _get_recent_trades(self) -> list:
        """Get recent completed trades"""
        try:
            # Get completed trades from current session
            return self.pnl_tracker.session_trades
            
        except Exception as e:
            self.logger.error(f"❌ Recent trades error: {e}")
            return []
    
    def show_snapshot(self):
        """Show a single snapshot without continuous monitoring"""
        try:
            self._update_display()
            
        except Exception as e:
            self.logger.error(f"❌ Snapshot error: {e}")
            print(f"❌ Error showing P&L snapshot: {e}")

def show_live_pnl():
    """Standalone function to show live P&L"""
    display = LivePnLDisplay()
    
    try:
        print("📱 Starting live P&L monitor...")
        display.start_display()
        
        # Keep main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n👋 Stopping live P&L monitor...")
        display.stop_display()
    except Exception as e:
        print(f"❌ Live P&L error: {e}")
        display.stop_display()

def show_pnl_snapshot():
    """Show a single P&L snapshot"""
    display = LivePnLDisplay()
    display.show_snapshot()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--snapshot':
        show_pnl_snapshot()
    else:
        show_live_pnl()
