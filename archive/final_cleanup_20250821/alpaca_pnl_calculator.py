#!/usr/bin/env python3
"""
Alpaca P&L Calculator
Demonstrates how to pull actual trading activities from Alpaca and calculate P&L

This script shows multiple methods:
1. Get filled orders from today and calculate realized P&L
2. Get account activities (trades, dividends, etc.)
3. Get portfolio history for daily P&L tracking
4. Get current positions for unrealized P&L
5. Calculate comprehensive daily P&L summary
"""

import os
import sys
from datetime import datetime, timedelta
from decimal import Decimal

import pandas as pd

# Add the parent directory to sys.path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.data_manager import DataManager
from utils.logger import setup_logger


class AlpacaPnLCalculator:
    """Calculate P&L using actual Alpaca trading activities"""

    def __init__(self):
        self.logger = setup_logger("AlpacaPnLCalculator")
        self.data_manager = DataManager()
        self.api = self.data_manager.api

    def get_todays_filled_orders(self):
        """Get all filled orders from today"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            orders = self.api.list_orders(
                status="filled",
                limit=200,  # Increase limit for active trading days
                after=today,
            )

            self.logger.info(f"Found {len(orders)} filled orders today")
            return orders

        except Exception as e:
            self.logger.error(f"Error getting today's orders: {e}")
            return []

    def get_account_activities(self, activity_type=None):
        """
        Get account activities (trades, dividends, etc.)

        Activity types:
        - 'FILL' - Trade fills
        - 'DIV' - Dividends
        - 'TRANS' - Transfers
        - 'MISC' - Miscellaneous
        """
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            activities = self.api.list_account_activities(
                activity_type=activity_type, date=today
            )

            self.logger.info(
                f"Found {len(activities)} activities today (type: {activity_type or 'ALL'})"
            )
            return activities

        except Exception as e:
            self.logger.error(f"Error getting account activities: {e}")
            return []

    def get_portfolio_history(self, period="1D", timeframe="1Min"):
        """Get portfolio history for P&L tracking"""
        try:
            portfolio_history = self.api.get_portfolio_history(
                period=period, timeframe=timeframe
            )

            return portfolio_history

        except Exception as e:
            self.logger.error(f"Error getting portfolio history: {e}")
            return None

    def calculate_realized_pnl_from_orders(self, orders):
        """Calculate realized P&L from filled orders"""
        try:
            symbol_trades = {}
            realized_pnl = 0.0

            for order in orders:
                symbol = order.symbol
                side = order.side
                qty = float(order.filled_qty or order.qty)
                price = float(order.filled_avg_price or 0)

                if symbol not in symbol_trades:
                    symbol_trades[symbol] = {"buys": [], "sells": []}

                trade_data = {
                    "qty": qty,
                    "price": price,
                    "time": order.filled_at or order.created_at,
                    "order_id": order.id,
                }

                if side == "buy":
                    symbol_trades[symbol]["buys"].append(trade_data)
                else:  # sell
                    symbol_trades[symbol]["sells"].append(trade_data)

            # Calculate P&L for each symbol using FIFO
            pnl_details = {}

            for symbol, trades in symbol_trades.items():
                symbol_pnl = 0.0
                buys = sorted(trades["buys"], key=lambda x: x["time"])
                sells = sorted(trades["sells"], key=lambda x: x["time"])

                # Simple FIFO matching
                buy_queue = buys.copy()

                for sell in sells:
                    sell_qty_remaining = sell["qty"]
                    sell_price = sell["price"]

                    while sell_qty_remaining > 0 and buy_queue:
                        buy = buy_queue[0]
                        buy_qty_available = buy["qty"]
                        buy_price = buy["price"]

                        # Match quantities
                        matched_qty = min(sell_qty_remaining, buy_qty_available)

                        # Calculate P&L for this match
                        trade_pnl = matched_qty * (sell_price - buy_price)
                        symbol_pnl += trade_pnl

                        # Update quantities
                        sell_qty_remaining -= matched_qty
                        buy["qty"] -= matched_qty

                        if buy["qty"] <= 0:
                            buy_queue.pop(0)

                pnl_details[symbol] = symbol_pnl
                realized_pnl += symbol_pnl

            return realized_pnl, pnl_details

        except Exception as e:
            self.logger.error(f"Error calculating realized P&L: {e}")
            return 0.0, {}

    def calculate_realized_pnl_from_activities(self):
        """Calculate realized P&L from account activities (more reliable)"""
        try:
            fill_activities = self.get_account_activities("FILL")

            if not fill_activities:
                return 0.0, {}

            symbol_pnl = {}
            total_realized = 0.0

            for activity in fill_activities:
                if hasattr(activity, "symbol") and hasattr(activity, "net_amount"):
                    symbol = activity.symbol
                    net_amount = float(activity.net_amount)

                    if symbol not in symbol_pnl:
                        symbol_pnl[symbol] = 0.0

                    # Net amount is negative for buys, positive for sells
                    # The P&L is embedded in the net amount calculation
                    if activity.side == "sell":
                        # For sells, we want to track the profit/loss
                        symbol_pnl[symbol] += net_amount
                        total_realized += net_amount

            return total_realized, symbol_pnl

        except Exception as e:
            self.logger.error(f"Error calculating P&L from activities: {e}")
            return 0.0, {}

    def get_unrealized_pnl(self):
        """Get current unrealized P&L from positions"""
        try:
            positions = self.data_manager.get_positions()
            total_unrealized = 0.0
            position_details = {}

            for pos in positions:
                symbol = pos["symbol"]
                unrealized_pl = pos["unrealized_pl"]

                position_details[symbol] = {
                    "qty": pos["qty"],
                    "avg_entry_price": pos["avg_entry_price"],
                    "market_value": pos["market_value"],
                    "unrealized_pl": unrealized_pl,
                }

                total_unrealized += unrealized_pl

            return total_unrealized, position_details

        except Exception as e:
            self.logger.error(f"Error getting unrealized P&L: {e}")
            return 0.0, {}

    def get_alpaca_daily_pnl(self):
        """Get Alpaca's official daily P&L calculation"""
        try:
            account = self.api.get_account()
            current_equity = float(account.equity)
            last_equity = float(account.last_equity)

            daily_pnl = current_equity - last_equity
            daily_return_pct = (daily_pnl / last_equity * 100) if last_equity > 0 else 0

            return {
                "daily_pnl": daily_pnl,
                "current_equity": current_equity,
                "last_equity": last_equity,
                "daily_return_pct": daily_return_pct,
            }

        except Exception as e:
            self.logger.error(f"Error getting Alpaca daily P&L: {e}")
            return None

    def generate_comprehensive_pnl_report(self):
        """Generate a comprehensive P&L report using all available data"""
        print("=" * 80)
        print("🔍 COMPREHENSIVE P&L ANALYSIS FROM ALPACA DATA")
        print("=" * 80)
        print()

        # Method 1: Alpaca's Official Daily P&L
        print("📊 1. ALPACA'S OFFICIAL DAILY P&L")
        print("-" * 50)
        alpaca_pnl = self.get_alpaca_daily_pnl()
        if alpaca_pnl:
            print(f"Previous Day Close:    ${alpaca_pnl['last_equity']:,.2f}")
            print(f"Current Equity:        ${alpaca_pnl['current_equity']:,.2f}")
            print(f"Daily P&L:             ${alpaca_pnl['daily_pnl']:+,.2f}")
            print(f"Daily Return:          {alpaca_pnl['daily_return_pct']:+.3f}%")
        else:
            print("❌ Unable to retrieve official P&L data")
        print()

        # Method 2: Calculate from Today's Orders
        print("📈 2. REALIZED P&L FROM TODAY'S ORDERS")
        print("-" * 50)
        orders = self.get_todays_filled_orders()
        if orders:
            realized_pnl, order_pnl_details = self.calculate_realized_pnl_from_orders(
                orders
            )
            print(f"Total Orders Today:    {len(orders)}")
            print(f"Realized P&L:          ${realized_pnl:+,.2f}")

            if order_pnl_details:
                print("\nPer-Symbol Breakdown:")
                for symbol, pnl in order_pnl_details.items():
                    print(f"  {symbol:>6}: ${pnl:+8.2f}")
        else:
            print("❌ No filled orders found for today")
        print()

        # Method 3: Calculate from Account Activities
        print("💰 3. REALIZED P&L FROM ACCOUNT ACTIVITIES")
        print("-" * 50)
        activity_realized, activity_details = (
            self.calculate_realized_pnl_from_activities()
        )
        print(f"Realized P&L:          ${activity_realized:+,.2f}")

        if activity_details:
            print("\nPer-Symbol Activity:")
            for symbol, pnl in activity_details.items():
                print(f"  {symbol:>6}: ${pnl:+8.2f}")
        print()

        # Method 4: Current Unrealized P&L
        print("📊 4. CURRENT UNREALIZED P&L")
        print("-" * 50)
        unrealized_pnl, position_details = self.get_unrealized_pnl()
        print(f"Total Unrealized P&L:  ${unrealized_pnl:+,.2f}")

        if position_details:
            print("\nCurrent Positions:")
            for symbol, pos in position_details.items():
                qty = pos["qty"]
                entry = pos["avg_entry_price"]
                unrealized = pos["unrealized_pl"]
                market_value = pos["market_value"]
                side = "LONG" if qty > 0 else "SHORT"

                print(
                    f"  {symbol:>6}: {side} {abs(qty):>3.0f} @ ${entry:>7.2f} | "
                    f"Value: ${market_value:>9.2f} | P&L: ${unrealized:+8.2f}"
                )
        else:
            print("No open positions")
        print()

        # Method 5: Portfolio History Analysis
        print("📈 5. PORTFOLIO HISTORY ANALYSIS")
        print("-" * 50)
        try:
            portfolio_history = self.get_portfolio_history()
            if (
                portfolio_history
                and hasattr(portfolio_history, "equity")
                and portfolio_history.equity
            ):
                equity_data = portfolio_history.equity
                timestamp_data = portfolio_history.timestamp

                if len(equity_data) > 1:
                    start_equity = equity_data[0]
                    end_equity = equity_data[-1]
                    intraday_pnl = end_equity - start_equity

                    print(f"Start of Day Equity:   ${start_equity:,.2f}")
                    print(f"Current Equity:        ${end_equity:,.2f}")
                    print(f"Intraday P&L:          ${intraday_pnl:+,.2f}")

                    # Calculate high/low
                    max_equity = max(equity_data)
                    min_equity = min(equity_data)
                    print(f"Daily High:            ${max_equity:,.2f}")
                    print(f"Daily Low:             ${min_equity:,.2f}")
                    print(f"Drawdown from High:    ${end_equity - max_equity:+,.2f}")
                else:
                    print("Insufficient portfolio history data")
            else:
                print("❌ Unable to retrieve portfolio history")
        except Exception as e:
            print(f"❌ Portfolio history error: {e}")
        print()

        # Summary
        print("📋 6. SUMMARY & VALIDATION")
        print("-" * 50)
        if alpaca_pnl:
            official_pnl = alpaca_pnl["daily_pnl"]
            calculated_total = unrealized_pnl + activity_realized

            print(f"Alpaca Official P&L:   ${official_pnl:+,.2f}")
            print(f"Calculated Total:      ${calculated_total:+,.2f}")
            print(f"  ├─ Realized:         ${activity_realized:+,.2f}")
            print(f"  └─ Unrealized:       ${unrealized_pnl:+,.2f}")

            difference = abs(official_pnl - calculated_total)
            if difference < 0.01:
                print(f"✅ Calculations match! (diff: ${difference:.2f})")
            else:
                print(f"⚠️  Difference: ${difference:.2f} (may be timing/rounding)")

        print("=" * 80)


def main():
    """Main function to run the P&L calculator"""
    try:
        calculator = AlpacaPnLCalculator()
        calculator.generate_comprehensive_pnl_report()

    except Exception as e:
        print(f"❌ Error running P&L calculator: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
