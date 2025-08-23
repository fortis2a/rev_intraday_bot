#!/usr/bin/env python3
"""
Live P&L External Monitor
Real-time P&L monitoring in external window with enhanced display
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from core.data_manager import DataManager
from utils.logger import setup_logger


class LivePnLMonitor:
    """External P&L monitoring with real-time updates"""

    def __init__(self):
        self.logger = setup_logger("live_pnl_external")
        self.data_manager = DataManager()
        self.last_update = None
        self.running = True
        self.start_of_day_equity = None

        # Import watchlist from config
        from config import config

        self.watchlist = config["INTRADAY_WATCHLIST"]

        # Display settings
        self.update_interval = 5  # seconds
        self.show_positions = True
        self.show_account_details = True
        self.show_daily_pnl = True
        self.show_percentage_returns = True
        self.show_watchlist_overview = True  # New feature

        print("=" * 80)
        print("             LIVE P&L MONITOR - SYNCED WITH ALPACA")
        print("=" * 80)
        print(f"Update Interval: {self.update_interval} seconds")
        print(f"Watchlist: {', '.join(self.watchlist)}")
        print(
            f"Features: All Watchlist Stocks | Individual P&L | Summary P&L | Alpaca-Synced"
        )
        print(f"Press Ctrl+C to stop monitoring")
        print("=" * 80)

        # Initialize with Alpaca's daily tracking
        self.initialize_alpaca_daily_tracking()

    def clear_screen(self):
        """Clear the console screen"""
        os.system("cls" if os.name == "nt" else "clear")

    def initialize_alpaca_daily_tracking(self):
        """Initialize daily P&L tracking using Alpaca's official data"""
        try:
            account_info = self.data_manager.get_account_info()
            if account_info:
                # Use Alpaca's last_equity as the start of day value
                # This syncs with what Alpaca considers the previous day's close
                account = self.data_manager.api.get_account()
                self.start_of_day_equity = float(account.last_equity)
                current_equity = account_info["equity"]

                self.logger.info(
                    f"📊 Alpaca last equity (start of day): ${self.start_of_day_equity:,.2f}"
                )
                self.logger.info(f"📊 Current equity: ${current_equity:,.2f}")

                # Also get portfolio history to double-check
                try:
                    portfolio_history = self.data_manager.api.get_portfolio_history(
                        period="1D", timeframe="1Min"
                    )
                    if (
                        hasattr(portfolio_history, "equity")
                        and portfolio_history.equity
                    ):
                        historical_start = portfolio_history.equity[0]
                        self.logger.info(
                            f"📊 Portfolio history start: ${historical_start:,.2f}"
                        )

                        # Use portfolio history if available and different from last_equity
                        if abs(historical_start - self.start_of_day_equity) > 0.01:
                            self.start_of_day_equity = historical_start
                            self.logger.info(
                                f"📊 Using portfolio history start of day: ${self.start_of_day_equity:,.2f}"
                            )
                except Exception as portfolio_error:
                    self.logger.warning(
                        f"Portfolio history not available: {portfolio_error}"
                    )

            else:
                self.start_of_day_equity = 100000  # Default fallback
                self.logger.warning(
                    "Account info unavailable, using fallback start of day equity"
                )

        except Exception as e:
            self.logger.error(f"Failed to initialize Alpaca daily tracking: {e}")
            self.start_of_day_equity = 100000

    def get_alpaca_daily_pnl(self):
        """Get daily P&L using Alpaca's official calculation"""
        try:
            account = self.data_manager.api.get_account()
            current_equity = float(account.equity)
            last_equity = float(account.last_equity)

            # Alpaca's official daily P&L
            alpaca_daily_pnl = current_equity - last_equity

            return {
                "daily_pnl": alpaca_daily_pnl,
                "current_equity": current_equity,
                "last_equity": last_equity,
                "daily_return_pct": (
                    (alpaca_daily_pnl / last_equity * 100) if last_equity > 0 else 0
                ),
            }
        except Exception as e:
            self.logger.error(f"Error getting Alpaca daily P&L: {e}")
            return {
                "daily_pnl": 0.0,
                "current_equity": 0.0,
                "last_equity": 0.0,
                "daily_return_pct": 0.0,
            }

    def get_todays_orders(self):
        """Get today's completed orders for realized P&L"""
        try:
            from datetime import datetime

            orders = self.data_manager.api.list_orders(
                status="filled", limit=100, after=datetime.now().strftime("%Y-%m-%d")
            )
            return orders
        except Exception as e:
            self.logger.error(f"Error getting today's orders: {e}")
            return []

    def calculate_realized_pnl(self, orders):
        """Calculate realized P&L from today's orders (simplified)"""
        # Note: This is a simplified calculation
        # Real implementation would need to track cost basis properly
        try:
            realized_pnl = 0.0
            symbol_positions = {}

            for order in orders:
                if hasattr(order, "filled_avg_price") and order.filled_avg_price:
                    symbol = order.symbol
                    side = order.side
                    qty = float(order.filled_qty or 0)
                    price = float(order.filled_avg_price or 0)

                    if symbol not in symbol_positions:
                        symbol_positions[symbol] = {"buys": [], "sells": []}

                    if side == "buy":
                        symbol_positions[symbol]["buys"].append(
                            {"qty": qty, "price": price}
                        )
                    else:
                        symbol_positions[symbol]["sells"].append(
                            {"qty": qty, "price": price}
                        )

            # Calculate P&L for each symbol (simplified FIFO)
            for symbol, positions in symbol_positions.items():
                for sell in positions["sells"]:
                    if positions["buys"]:
                        buy = positions["buys"][0]  # FIFO
                        matched_qty = min(sell["qty"], buy["qty"])
                        pnl = matched_qty * (sell["price"] - buy["price"])
                        realized_pnl += pnl

                        # Update quantities
                        buy["qty"] -= matched_qty
                        sell["qty"] -= matched_qty

                        if buy["qty"] <= 0:
                            positions["buys"].pop(0)

            return realized_pnl
        except Exception as e:
            self.logger.error(f"Error calculating realized P&L: {e}")
            return 0.0

    def format_currency(self, amount):
        """Format currency with proper sign and color indicators"""
        if amount > 0:
            return f"+${amount:,.2f}"
        elif amount < 0:
            return f"-${abs(amount):,.2f}"
        else:
            return f"${amount:,.2f}"

    def display_header(self):
        """Display monitoring header"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n🔴 LIVE P&L MONITOR - {now}")
        print("=" * 80)

    def display_account_summary(self, account_info):
        """Display account summary information"""
        if not account_info:
            print("❌ Account information unavailable")
            return

        print("💰 ACCOUNT SUMMARY")
        print("-" * 40)
        print(f"Total Equity:        ${account_info['equity']:,.2f}")
        print(f"Buying Power:        ${account_info['buying_power']:,.2f}")
        print(f"Cash Available:      ${account_info['cash']:,.2f}")
        print(f"Portfolio Value:     ${account_info['portfolio_value']:,.2f}")

        if "day_trading_buying_power" in account_info:
            print(
                f"Day Trading Power:   ${account_info['day_trading_buying_power']:,.2f}"
            )

    def display_positions(self, positions):
        """Display current positions with enhanced details"""
        if not positions:
            print("\n📊 POSITIONS: No open positions")
            return

        print(f"\n📊 POSITIONS ({len(positions)} open)")
        print("-" * 95)
        print(
            f"{'Symbol':<8} {'Qty':<8} {'Side':<6} {'Entry $':<10} {'Current $':<10} {'P&L $':<12} {'P&L %':<8} {'Mkt Val $':<12}"
        )
        print("-" * 95)

        total_unrealized = 0
        total_market_value = 0

        for pos in positions:
            symbol = pos["symbol"]
            qty = int(pos["qty"])
            side = pos["side"]
            avg_price = pos["avg_entry_price"]
            market_value = pos["market_value"]
            unrealized_pl = pos["unrealized_pl"]
            total_unrealized += unrealized_pl
            total_market_value += market_value

            # Calculate current price and percentage return
            current_price = market_value / abs(qty) if qty != 0 else avg_price
            pnl_pct = (
                (unrealized_pl / (abs(qty) * avg_price)) * 100
                if qty != 0 and avg_price != 0
                else 0
            )

            pnl_str = self.format_currency(unrealized_pl)
            pnl_pct_str = f"{pnl_pct:+.2f}%"

            print(
                f"{symbol:<8} {qty:<8} {side:<6} ${avg_price:<9.2f} ${current_price:<9.2f} "
                f"{pnl_str:<12} {pnl_pct_str:<8} ${market_value:<11.2f}"
            )

        print("-" * 95)
        print(
            f"{'TOTALS:':<50} {self.format_currency(total_unrealized):<12} {'':>8} ${total_market_value:<11.2f}"
        )

        return total_unrealized, total_market_value

    def display_watchlist_overview(self, positions):
        """Display complete watchlist with positions and current prices"""
        print(f"\n📊 WATCHLIST OVERVIEW ({len(self.watchlist)} stocks)")
        print("-" * 105)
        print(
            f"{'Symbol':<8} {'Status':<12} {'Qty':<8} {'Entry $':<10} {'Current $':<10} {'P&L $':<12} {'P&L %':<8} {'Mkt Val $':<12}"
        )
        print("-" * 105)

        # Create position lookup for quick access
        position_lookup = {pos["symbol"]: pos for pos in positions}

        total_unrealized = 0
        total_market_value = 0

        for symbol in self.watchlist:
            try:
                # Get current price for the symbol
                current_price = self.data_manager.get_current_price(symbol)

                if symbol in position_lookup:
                    # Stock has an open position
                    pos = position_lookup[symbol]
                    qty = int(pos["qty"])
                    side = pos["side"]
                    avg_price = pos["avg_entry_price"]
                    market_value = pos["market_value"]
                    unrealized_pl = pos["unrealized_pl"]

                    total_unrealized += unrealized_pl
                    total_market_value += market_value

                    pnl_pct = (
                        (unrealized_pl / (abs(qty) * avg_price)) * 100
                        if qty != 0 and avg_price != 0
                        else 0
                    )
                    pnl_str = self.format_currency(unrealized_pl)
                    pnl_pct_str = f"{pnl_pct:+.2f}%"
                    status = f"LONG {qty}" if side == "long" else f"SHORT {qty}"

                    print(
                        f"{symbol:<8} {status:<12} {qty:<8} ${avg_price:<9.2f} ${current_price:<9.2f} "
                        f"{pnl_str:<12} {pnl_pct_str:<8} ${market_value:<11.2f}"
                    )
                else:
                    # Stock is on watchlist but no position
                    if current_price:
                        print(
                            f"{symbol:<8} {'NO POSITION':<12} {'-':<8} {'-':<10} ${current_price:<9.2f} "
                            f"{'$0.00':<12} {'+0.00%':<8} {'$0.00':<12}"
                        )
                    else:
                        print(
                            f"{symbol:<8} {'PRICE ERROR':<12} {'-':<8} {'-':<10} {'-':<10} "
                            f"{'$0.00':<12} {'+0.00%':<8} {'$0.00':<12}"
                        )

            except Exception as e:
                self.logger.error(f"Error getting data for {symbol}: {e}")
                print(
                    f"{symbol:<8} {'ERROR':<12} {'-':<8} {'-':<10} {'-':<10} "
                    f"{'$0.00':<12} {'+0.00%':<8} {'$0.00':<12}"
                )

        print("-" * 105)
        print(
            f"{'POSITION TOTALS:':<60} {self.format_currency(total_unrealized):<12} {'':>8} ${total_market_value:<11.2f}"
        )

        return total_unrealized, total_market_value

    def display_daily_pnl_summary(self, account_info, total_unrealized):
        """Display comprehensive daily P&L summary using Alpaca's official data"""
        if not account_info:
            return

        # Get Alpaca's official daily P&L calculation
        alpaca_pnl_data = self.get_alpaca_daily_pnl()

        current_equity = alpaca_pnl_data["current_equity"]
        last_equity = alpaca_pnl_data["last_equity"]
        alpaca_daily_pnl = alpaca_pnl_data["daily_pnl"]
        daily_return_pct = alpaca_pnl_data["daily_return_pct"]

        # Get today's orders for additional context
        todays_orders = self.get_todays_orders()
        completed_trades = len([o for o in todays_orders if hasattr(o, "side")])

        print(f"\n💰 DAILY P&L SUMMARY (ALPACA-SYNCED)")
        print("-" * 70)
        print(f"Previous Day Close:      ${last_equity:,.2f}")
        print(f"Current Equity:          ${current_equity:,.2f}")
        print(f"Alpaca Daily P&L:        {self.format_currency(alpaca_daily_pnl)}")
        print(f"  └─ Unrealized P&L:     {self.format_currency(total_unrealized)}")

        # Calculate implied realized P&L
        implied_realized = alpaca_daily_pnl - total_unrealized
        print(f"  └─ Implied Realized:   {self.format_currency(implied_realized)}")

        print(f"Daily Return:            {daily_return_pct:+.3f}%")
        print(f"Trades Completed Today:  {completed_trades}")

        print("-" * 70)

    def display_watchlist_summary(self):
        """Display quick watchlist performance summary"""
        try:
            print(f"\n📈 WATCHLIST PERFORMANCE")
            print("-" * 50)

            current_prices = {}
            for symbol in self.watchlist:
                try:
                    price = self.data_manager.get_current_price(symbol)
                    current_prices[symbol] = price
                except:
                    current_prices[symbol] = None

            # Quick price display
            price_line = ""
            for symbol in self.watchlist:
                price = current_prices[symbol]
                if price:
                    price_line += f"{symbol}: ${price:.2f}  "
                else:
                    price_line += f"{symbol}: N/A  "

            print(f"Current Prices: {price_line}")

            # Count positions
            positions = self.get_current_positions()
            positions_count = len(
                [
                    s
                    for s in self.watchlist
                    if any(pos["symbol"] == s for pos in positions)
                ]
            )
            print(
                f"Active Positions: {positions_count}/{len(self.watchlist)} watchlist stocks"
            )

        except Exception as e:
            print(f"Watchlist summary error: {e}")

    def get_current_positions(self):
        """Get current positions for summary calculations"""
        try:
            return self.data_manager.get_positions()
        except:
            return []

    def display_market_status(self):
        """Display market status"""
        try:
            market_status = self.data_manager.get_market_status()
            if market_status:
                status = "🟢 OPEN" if market_status["is_open"] else "🔴 CLOSED"
                print(f"\n🏛️ MARKET STATUS: {status}")
            else:
                print(f"\n🏛️ MARKET STATUS: ❓ UNKNOWN")
        except Exception as e:
            print(f"\n🏛️ MARKET STATUS: ❌ ERROR - {e}")

    def display_fees_disclaimer(self):
        """Display disclaimer about fees and slippage"""
        print(f"\n⚠️  NOTES:")
        print(f"• Daily P&L synced with Alpaca's official calculation")
        print(f"• P&L shown is before fees/commissions")
        print(f"• Paper trading account - no actual fees")
        print(f"• Live trading would include $0.005/share commission")
        print(f"• Matches what you see in Alpaca dashboard")
        """Display market status"""
        try:
            market_status = self.data_manager.get_market_status()
            if market_status:
                status = "🟢 OPEN" if market_status["is_open"] else "🔴 CLOSED"
                print(f"\n🏛️ MARKET STATUS: {status}")
            else:
                print(f"\n🏛️ MARKET STATUS: ❓ UNKNOWN")
        except Exception as e:
            print(f"\n🏛️ MARKET STATUS: ❌ ERROR - {e}")

    def run_monitor(self):
        """Main monitoring loop"""
        self.logger.info("🚀 Live P&L External Monitor started")

        while self.running:
            try:
                # Clear screen for fresh display
                self.clear_screen()

                # Display header
                self.display_header()

                # Get account information
                account_info = self.data_manager.get_account_info()

                # Get current positions
                positions = self.data_manager.get_positions()

                # Display account summary
                if self.show_account_details:
                    self.display_account_summary(account_info)

                # Display market status
                self.display_market_status()

                # Display watchlist overview (shows all 5 stocks)
                total_unrealized = 0
                if self.show_watchlist_overview:
                    watchlist_result = self.display_watchlist_overview(positions)
                    if watchlist_result:
                        total_unrealized, total_market_value = watchlist_result
                    else:
                        total_unrealized = 0

                # Also display detailed positions if there are any
                if positions and self.show_positions:
                    print(f"\n📋 DETAILED POSITIONS")
                    self.display_positions(positions)

                # Display comprehensive daily P&L summary
                if self.show_daily_pnl:
                    self.display_daily_pnl_summary(account_info, total_unrealized)

                # Display watchlist performance summary
                self.display_watchlist_summary()

                # Display fees disclaimer
                self.display_fees_disclaimer()

                # Show update info
                self.last_update = datetime.now()
                print(f"\n⏰ Last Updated: {self.last_update.strftime('%H:%M:%S')}")
                print(f"🔄 Next Update: {self.update_interval}s | Press Ctrl+C to stop")

                # Log summary with Alpaca-synced data
                total_unrealized = (
                    sum(p["unrealized_pl"] for p in positions) if positions else 0
                )
                alpaca_pnl_data = self.get_alpaca_daily_pnl()

                self.logger.info(
                    f"💰 Equity: ${alpaca_pnl_data['current_equity']:,.2f} | "
                    f"Alpaca Daily P&L: {self.format_currency(alpaca_pnl_data['daily_pnl'])} | "
                    f"Unrealized: {self.format_currency(total_unrealized)} | "
                    f"Positions: {len(positions) if positions else 0}"
                )

                # Wait for next update
                time.sleep(self.update_interval)

            except KeyboardInterrupt:
                print(f"\n\n🛑 Stopping Live P&L Monitor...")
                self.running = False
                break

            except Exception as e:
                print(f"\n❌ ERROR: {e}")
                self.logger.error(f"Monitor error: {e}")
                print(f"Retrying in {self.update_interval} seconds...")
                time.sleep(self.update_interval)

        self.logger.info("🛑 Live P&L External Monitor stopped")
        print("Monitor stopped. Press any key to close window.")


def main():
    """Run the live P&L monitor"""
    try:
        monitor = LivePnLMonitor()
        monitor.run_monitor()
    except Exception as e:
        print(f"❌ Failed to start Live P&L Monitor: {e}")
        input("Press Enter to close...")


if __name__ == "__main__":
    main()
