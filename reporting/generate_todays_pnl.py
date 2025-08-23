#!/usr/bin/env python3
"""
Generate Today's P&L Report
Simple P&L report using Alpaca API data
"""

import sys
from pathlib import Path
from datetime import datetime, date

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from alpaca.trading.client import TradingClient
from config import ALPACA_API_KEY, ALPACA_SECRET_KEY


def generate_todays_pnl_report():
    """Generate a simple P&L report for today"""
    print("📊 GENERATING TODAY'S P&L REPORT")
    print("=" * 50)

    try:
        client = TradingClient(ALPACA_API_KEY, ALPACA_SECRET_KEY, paper=True)
        today = date.today()

        print(f"📅 Report Date: {today}")
        print()

        # Get account info
        print("💰 ACCOUNT SUMMARY:")
        account = client.get_account()
        print(f"  • Total Equity: ${float(account.equity):,.2f}")
        print(f"  • Buying Power: ${float(account.buying_power):,.2f}")
        print(f"  • Cash: ${float(account.cash):,.2f}")
        print(f"  • Day Trade Count: {account.daytrade_count}")
        # Day P&L will be calculated from positions
        day_pnl = 0  # Will calculate from positions
        print()

        # Get current positions
        print("📊 CURRENT POSITIONS:")
        positions = client.get_all_positions()
        total_unrealized = 0

        if positions:
            for pos in positions:
                symbol = pos.symbol
                qty = int(float(pos.qty))
                side = pos.side.name
                entry_price = float(pos.avg_entry_price)
                current_price = float(pos.current_price)
                market_value = float(pos.market_value)
                unrealized_pnl = float(pos.unrealized_pl)
                unrealized_pct = float(pos.unrealized_plpc) * 100
                total_unrealized += unrealized_pnl

                pnl_sign = "+" if unrealized_pnl >= 0 else ""
                print(f"  • {symbol}: {side} {qty} shares")
                print(f"    Entry: ${entry_price:.2f} | Current: ${current_price:.2f}")
                print(f"    Market Value: ${abs(market_value):,.2f}")
                print(
                    f"    Unrealized P&L: {pnl_sign}${unrealized_pnl:.2f} ({unrealized_pct:+.2f}%)"
                )
                print()

            print(f"📈 TOTAL UNREALIZED P&L: ${total_unrealized:+.2f}")
        else:
            print("  ✅ No open positions")

        print()

        # Get today's orders
        print("📋 TODAY'S ORDERS:")
        orders = client.get_orders()

        today_orders = []
        for order in orders:
            if order.submitted_at and order.submitted_at.date() == today:
                today_orders.append(order)

        if today_orders:
            print(f"  Found {len(today_orders)} orders submitted today:")
            for order in today_orders:
                status_color = (
                    "✅"
                    if order.status.name == "FILLED"
                    else "⏳" if order.status.name == "ACCEPTED" else "❌"
                )
                print(
                    f"  {status_color} {order.symbol}: {order.side.name} {order.qty} @ {order.order_type.name} - {order.status.name}"
                )
        else:
            print("  📭 No orders found for today")

        print()

        # Try to get portfolio history for today
        print("📈 TODAY'S PORTFOLIO PERFORMANCE:")
        try:
            portfolio_history = client.get_portfolio_history(
                period="1D", timeframe="1Min"
            )

            if portfolio_history.equity:
                start_equity = portfolio_history.equity[0]
                end_equity = portfolio_history.equity[-1]
                day_change = end_equity - start_equity
                day_change_pct = (
                    (day_change / start_equity) * 100 if start_equity > 0 else 0
                )

                print(f"  • Starting Equity: ${start_equity:,.2f}")
                print(f"  • Current Equity: ${end_equity:,.2f}")
                print(f"  • Day Change: ${day_change:+.2f} ({day_change_pct:+.2f}%)")
            else:
                print("  📊 No portfolio history data available")

        except Exception as e:
            print(f"  ⚠️ Portfolio history unavailable: {e}")

        print()

        # Save report
        reports_dir = Path("reports")
        reports_dir.mkdir(exist_ok=True)

        report_filename = f"pnl_report_{today.strftime('%Y%m%d')}.txt"
        report_path = reports_dir / report_filename

        # Write report to file
        with open(report_path, "w") as f:
            f.write(f"P&L REPORT - {today}\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Account Equity: ${float(account.equity):,.2f}\n")
            f.write(f"Day P&L (Unrealized): ${total_unrealized:+.2f}\n")
            f.write(f"Open Positions: {len(positions)}\n")
            f.write(f"Orders Today: {len(today_orders)}\n")
            f.write(f"Generated: {datetime.now()}\n")

        print(f"💾 REPORT SAVED:")
        print(f"  📄 File: {report_path}")
        print(f"  🕐 Generated: {datetime.now().strftime('%H:%M:%S')}")

        print()
        print("🎯 SUMMARY:")
        print(f"  • The bot had {len(today_orders)} orders today")
        print(f"  • Currently holding {len(positions)} positions")
        print(f"  • Account unrealized P&L: ${total_unrealized:+.2f}")

        if len(today_orders) == 0:
            print(f"  ⚠️ No trading activity detected for today")
            print(f"  💡 This explains why no automatic P&L report was generated")

        return True

    except Exception as e:
        print(f"❌ Error generating P&L report: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    generate_todays_pnl_report()
