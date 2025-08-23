#!/usr/bin/env python3
"""
Real-time Trading System Status Monitor
Live terminal display with auto-refresh every 10 seconds
"""

import json
import os
import sqlite3
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict

import psutil

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from alpaca.trading.client import TradingClient

    from config import ALPACA_API_KEY, ALPACA_SECRET_KEY
except ImportError:
    print("⚠️  Warning: Could not import Alpaca or config")


class RealTimeStatusMonitor:
    """Real-time status monitor for trading system"""

    def __init__(self):
        self.db_path = Path("data/trading.db")
        self.logs_path = Path("logs")
        self.reports_path = Path("reports")

        # Initialize Alpaca client
        try:
            self.alpaca_client = TradingClient(
                ALPACA_API_KEY, ALPACA_SECRET_KEY, paper=True
            )
        except:
            self.alpaca_client = None

    def clear_screen(self):
        """Clear terminal screen"""
        os.system("cls" if os.name == "nt" else "clear")

    def get_market_status(self) -> Dict[str, Any]:
        """Get current market status and timing"""
        now = datetime.now()

        # Market hours (9:30 AM to 4:00 PM ET)
        market_open_time = now.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close_time = now.replace(hour=16, minute=0, second=0, microsecond=0)

        if now < market_open_time:
            status = "PRE_MARKET"
            next_event = "Market Open"
            time_to_event = market_open_time - now
        elif now > market_close_time:
            status = "POST_MARKET"
            next_event = "Market Open (Tomorrow)"
            tomorrow_open = market_open_time + timedelta(days=1)
            time_to_event = tomorrow_open - now
        else:
            status = "MARKET_OPEN"
            next_event = "Market Close"
            time_to_event = market_close_time - now

        minutes_to_event = int(time_to_event.total_seconds() / 60)
        hours = minutes_to_event // 60
        mins = minutes_to_event % 60

        return {
            "status": status,
            "next_event": next_event,
            "time_to_event": f"{hours}h {mins}m" if hours > 0 else f"{mins}m",
            "current_time": now.strftime("%H:%M:%S"),
        }

    def get_process_status(self) -> Dict[str, Any]:
        """Get status of trading-related processes"""
        processes = {}

        for proc in psutil.process_iter(
            ["pid", "name", "cmdline", "cpu_percent", "memory_info"]
        ):
            try:
                if proc.info["name"] == "python.exe" or proc.info["name"] == "python":
                    cmdline = (
                        " ".join(proc.info["cmdline"]) if proc.info["cmdline"] else ""
                    )

                    if "main.py" in cmdline:
                        processes["main_bot"] = {
                            "pid": proc.info["pid"],
                            "status": "RUNNING",
                            "cpu": proc.info["cpu_percent"],
                            "memory_mb": proc.info["memory_info"].rss / 1024 / 1024,
                            "type": "Main Trading Bot",
                        }
                    elif "scalping_command_center.py" in cmdline:
                        processes["command_center"] = {
                            "pid": proc.info["pid"],
                            "status": "RUNNING",
                            "cpu": proc.info["cpu_percent"],
                            "memory_mb": proc.info["memory_info"].rss / 1024 / 1024,
                            "type": "Command Center",
                        }
                    elif "monitor_trading_status.py" in cmdline:
                        processes["monitor"] = {
                            "pid": proc.info["pid"],
                            "status": "RUNNING",
                            "cpu": proc.info["cpu_percent"],
                            "memory_mb": proc.info["memory_info"].rss / 1024 / 1024,
                            "type": "Status Monitor",
                        }
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return processes

    def get_alpaca_status(self) -> Dict[str, Any]:
        """Get Alpaca account status"""
        if not self.alpaca_client:
            return {"status": "DISCONNECTED", "error": "Client not initialized"}

        try:
            account = self.alpaca_client.get_account()
            positions = self.alpaca_client.get_all_positions()

            return {
                "status": "CONNECTED",
                "equity": float(account.equity),
                "buying_power": float(account.buying_power),
                "cash": float(account.cash),
                "open_positions": len(positions),
                "account_status": account.status,
            }
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}

    def get_database_status(self) -> Dict[str, Any]:
        """Get database status and latest data"""
        if not self.db_path.exists():
            return {"status": "NOT_FOUND"}

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get latest daily summary
            cursor.execute(
                """
                SELECT trade_date, total_trades, cash_flow_pnl, alpaca_pnl, total_volume
                FROM daily_summaries 
                ORDER BY trade_date DESC 
                LIMIT 1
            """
            )
            latest_day = cursor.fetchone()

            # Get today's trade count from trading_activities
            today_str = datetime.now().strftime("%Y-%m-%d")
            cursor.execute(
                "SELECT COUNT(*) FROM trading_activities WHERE trade_date = ?",
                (today_str,),
            )
            today_trades = cursor.fetchone()[0]

            conn.close()

            if latest_day:
                return {
                    "status": "CONNECTED",
                    "latest_date": latest_day[0],
                    "latest_trades": latest_day[1],
                    "latest_pnl": latest_day[2] or latest_day[3] or 0,
                    "today_trades": today_trades,
                }
            else:
                return {"status": "EMPTY"}

        except Exception as e:
            return {"status": "ERROR", "error": str(e)}

    def get_log_status(self) -> Dict[str, Any]:
        """Get log file status"""
        today_str = datetime.now().strftime("%Y%m%d")

        log_files = {
            "main_log": self.logs_path / f"intraday_intraday_engine_{today_str}.log",
            "trades_log": self.logs_path / f"intraday_order_manager_{today_str}.log",
            "orders_log": self.logs_path / f"intraday_trading_launcher_{today_str}.log",
        }

        status = {}
        for name, path in log_files.items():
            if path.exists():
                stat = path.stat()
                status[name] = {
                    "exists": True,
                    "size_mb": stat.st_size / 1024 / 1024,
                    "modified": datetime.fromtimestamp(stat.st_mtime).strftime(
                        "%H:%M:%S"
                    ),
                }
            else:
                status[name] = {"exists": False}

        return status

    def format_status_display(self, market, processes, alpaca, database, logs) -> str:
        """Format the complete status display"""

        # Header
        display = f"""
🔥 LIVE TRADING SYSTEM STATUS 🔥
{'='*60}
⏰ Current Time: {market['current_time']}
📈 Market Status: {market['status']}
⏳ {market['next_event']}: {market['time_to_event']}
{'='*60}

🚀 TRADING PROCESSES:
"""

        # Process status
        if "main_bot" in processes:
            p = processes["main_bot"]
            display += f"✅ Main Bot (PID {p['pid']}): {p['status']} | CPU: {p['cpu']:.1f}% | RAM: {p['memory_mb']:.0f}MB\n"
        else:
            display += "❌ Main Bot: NOT RUNNING\n"

        if "command_center" in processes:
            p = processes["command_center"]
            display += f"✅ Command Center (PID {p['pid']}): {p['status']} | CPU: {p['cpu']:.1f}% | RAM: {p['memory_mb']:.0f}MB\n"
        else:
            display += "❌ Command Center: NOT RUNNING\n"

        if "monitor" in processes:
            p = processes["monitor"]
            display += f"✅ Monitor (PID {p['pid']}): {p['status']} | CPU: {p['cpu']:.1f}% | RAM: {p['memory_mb']:.0f}MB\n"
        else:
            display += "⚪ Monitor: NOT RUNNING\n"

        display += f"\n💰 ALPACA ACCOUNT:\n"

        # Alpaca status
        if alpaca["status"] == "CONNECTED":
            display += f"✅ Connection: ACTIVE\n"
            display += f"💵 Equity: ${alpaca['equity']:,.2f}\n"
            display += f"💳 Buying Power: ${alpaca['buying_power']:,.2f}\n"
            display += f"🏦 Cash: ${alpaca['cash']:,.2f}\n"
            display += f"📊 Open Positions: {alpaca['open_positions']}\n"
            display += f"🎯 Account Status: {alpaca['account_status']}\n"
        else:
            display += f"❌ Connection: {alpaca['status']}\n"
            if "error" in alpaca:
                display += f"   Error: {alpaca['error']}\n"

        display += f"\n📊 DATABASE:\n"

        # Database status
        if database["status"] == "CONNECTED":
            display += f"✅ Connection: ACTIVE\n"
            display += f"📅 Latest Data: {database['latest_date']}\n"
            display += f"📈 Latest P&L: ${database['latest_pnl']:+.2f}\n"
            display += f"🔢 Latest Trades: {database['latest_trades']}\n"
            display += f"📊 Today's Trades: {database['today_trades']}\n"
        else:
            display += f"❌ Database: {database['status']}\n"

        display += f"\n📝 LOG FILES:\n"

        # Log status
        for name, info in logs.items():
            if info["exists"]:
                # Format file size more appropriately
                size_mb = info["size_mb"]
                if size_mb >= 1:
                    size_str = f"{size_mb:.1f}MB"
                else:
                    size_kb = size_mb * 1024
                    size_str = f"{size_kb:.1f}KB"

                display += f"✅ {name.replace('_', ' ').title()}: {size_str} (Updated: {info['modified']})\n"
            else:
                display += f"❌ {name.replace('_', ' ').title()}: NOT FOUND\n"

        display += f"\n{'='*60}\n"
        display += "🔄 Auto-refreshing every 10 seconds... (Ctrl+C to stop)\n"
        display += f"{'='*60}"

        return display

    def run_monitor(self):
        """Run the real-time monitor"""
        print("🚀 Starting Real-time Trading System Monitor...")
        print("   Press Ctrl+C to stop")
        time.sleep(2)

        try:
            while True:
                self.clear_screen()

                # Gather all status information
                market_status = self.get_market_status()
                process_status = self.get_process_status()
                alpaca_status = self.get_alpaca_status()
                database_status = self.get_database_status()
                log_status = self.get_log_status()

                # Display status
                status_display = self.format_status_display(
                    market_status,
                    process_status,
                    alpaca_status,
                    database_status,
                    log_status,
                )

                print(status_display)

                # Wait 10 seconds before next update
                time.sleep(10)

        except KeyboardInterrupt:
            print("\n\n👋 Real-time monitor stopped.")
            print("Thank you for using the Trading System Monitor!")


if __name__ == "__main__":
    monitor = RealTimeStatusMonitor()
    monitor.run_monitor()
