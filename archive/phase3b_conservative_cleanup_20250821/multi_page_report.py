#!/usr/bin/env python3
"""
Multi-Page Trading Report Generator
Creates separate pages for overall summary and individual trading days
"""

import sys
import os
from datetime import datetime, timedelta, date
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages

# Add the parent directory to sys.path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.data_manager import DataManager
from utils.logger import setup_logger


class MultiPageTradingReport:
    """Create multi-page trading report with daily breakdowns"""

    def __init__(self):
        self.logger = setup_logger("MultiPageTradingReport")
        self.data_manager = DataManager()
        self.api = self.data_manager.api

        # Set up style for maximum readability
        plt.style.use("seaborn-v0_8-whitegrid")
        plt.rcParams.update(
            {
                "figure.facecolor": "white",
                "axes.facecolor": "white",
                "axes.edgecolor": "black",
                "axes.linewidth": 2,
                "grid.alpha": 0.3,
                "font.size": 16,
                "axes.titlesize": 20,
                "axes.labelsize": 18,
                "xtick.labelsize": 16,
                "ytick.labelsize": 16,
                "legend.fontsize": 16,
                "figure.titlesize": 24,
            }
        )

    def get_trading_data_by_day(self, days_back=7):
        """Get trading data organized by day"""
        try:
            start_date = (datetime.now() - timedelta(days=days_back)).strftime(
                "%Y-%m-%d"
            )

            # Get all orders
            orders = self.api.list_orders(status="filled", limit=500, after=start_date)

            if not orders:
                return None

            # Organize orders by date
            orders_by_date = {}
            for order in orders:
                if hasattr(order, "filled_at") and order.filled_at:
                    order_date = order.filled_at.date()
                    date_str = order_date.strftime("%Y-%m-%d")

                    if date_str not in orders_by_date:
                        orders_by_date[date_str] = []

                    orders_by_date[date_str].append(
                        {
                            "symbol": order.symbol,
                            "side": order.side,
                            "qty": float(order.filled_qty or order.qty),
                            "price": float(order.filled_avg_price or 0),
                            "filled_at": order.filled_at,
                            "order_id": order.id,
                        }
                    )

            return orders_by_date

        except Exception as e:
            self.logger.error(f"Error getting trading data: {e}")
            return None

    def calculate_daily_pnl(self, orders):
        """Calculate P&L for a day's orders using FIFO"""
        symbol_groups = {}

        # Group by symbol
        for order in orders:
            symbol = order["symbol"]
            if symbol not in symbol_groups:
                symbol_groups[symbol] = {"buys": [], "sells": []}

            if order["side"] == "buy":
                symbol_groups[symbol]["buys"].append(order)
            else:
                symbol_groups[symbol]["sells"].append(order)

        # Calculate P&L using FIFO
        stock_pnl = {}
        total_pnl = 0

        for symbol, data in symbol_groups.items():
            buys = data["buys"].copy()
            sells = data["sells"].copy()
            pnl = 0

            for sell in sells:
                remaining_qty = sell["qty"]
                while remaining_qty > 0 and buys:
                    buy = buys[0]
                    if buy["qty"] <= remaining_qty:
                        pnl += buy["qty"] * (sell["price"] - buy["price"])
                        remaining_qty -= buy["qty"]
                        buys.pop(0)
                    else:
                        pnl += remaining_qty * (sell["price"] - buy["price"])
                        buy["qty"] -= remaining_qty
                        remaining_qty = 0

            stock_pnl[symbol] = pnl
            total_pnl += pnl

        return stock_pnl, total_pnl

    def create_overview_page(self, pdf, all_data):
        """Create overview page with all days combined"""
        fig = plt.figure(figsize=(16, 20))
        fig.suptitle(
            "TRADING PERFORMANCE OVERVIEW - ALL DAYS",
            fontsize=28,
            fontweight="bold",
            y=0.95,
        )

        # Combine all data
        all_stock_pnl = {}
        daily_totals = {}

        for date_str, orders in all_data.items():
            stock_pnl, total_pnl = self.calculate_daily_pnl(orders)
            daily_totals[date_str] = total_pnl

            for symbol, pnl in stock_pnl.items():
                if symbol not in all_stock_pnl:
                    all_stock_pnl[symbol] = 0
                all_stock_pnl[symbol] += pnl

        # 1. Overall Stock Performance (Top)
        plt.subplot(3, 2, 1)
        if all_stock_pnl:
            symbols = list(all_stock_pnl.keys())
            pnls = list(all_stock_pnl.values())
            colors = ["green" if p > 0 else "red" for p in pnls]

            bars = plt.bar(symbols, pnls, color=colors, edgecolor="black", linewidth=2)
            plt.title(
                "OVERALL STOCK PERFORMANCE", fontsize=20, fontweight="bold", pad=20
            )
            plt.ylabel("Total P&L ($)", fontsize=18, fontweight="bold")
            plt.xticks(rotation=45, fontsize=16)
            plt.grid(True, alpha=0.3, axis="y")
            plt.axhline(y=0, color="black", linestyle="-", linewidth=2)

            # Add value labels
            for bar, pnl in zip(bars, pnls):
                height = bar.get_height()
                plt.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    height + (10 if height > 0 else -30),
                    f"${pnl:.0f}",
                    ha="center",
                    va="bottom" if height > 0 else "top",
                    fontsize=14,
                    fontweight="bold",
                )

        # 2. Daily P&L Trend (Top Right)
        plt.subplot(3, 2, 2)
        if daily_totals:
            dates = list(daily_totals.keys())
            totals = list(daily_totals.values())
            colors = ["green" if t > 0 else "red" for t in totals]

            bars = plt.bar(
                range(len(dates)), totals, color=colors, edgecolor="black", linewidth=2
            )
            plt.title("DAILY P&L TREND", fontsize=20, fontweight="bold", pad=20)
            plt.ylabel("Daily P&L ($)", fontsize=18, fontweight="bold")
            plt.xticks(range(len(dates)), [d.split("-")[2] for d in dates], fontsize=16)
            plt.xlabel("Day of Month", fontsize=18, fontweight="bold")
            plt.grid(True, alpha=0.3, axis="y")
            plt.axhline(y=0, color="black", linestyle="-", linewidth=2)

            # Add value labels
            for bar, total in zip(bars, totals):
                height = bar.get_height()
                plt.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    height + (10 if height > 0 else -30),
                    f"${total:.0f}",
                    ha="center",
                    va="bottom" if height > 0 else "top",
                    fontsize=14,
                    fontweight="bold",
                )

        # 3. Summary Statistics (Middle)
        plt.subplot(3, 1, 2)
        plt.axis("off")

        total_pnl = sum(all_stock_pnl.values()) if all_stock_pnl else 0
        winners = (
            len([p for p in all_stock_pnl.values() if p > 0]) if all_stock_pnl else 0
        )
        total_stocks = len(all_stock_pnl) if all_stock_pnl else 0
        win_rate = (winners / total_stocks * 100) if total_stocks > 0 else 0

        best_stock = (
            max(all_stock_pnl.items(), key=lambda x: x[1])
            if all_stock_pnl
            else ("N/A", 0)
        )
        worst_stock = (
            min(all_stock_pnl.items(), key=lambda x: x[1])
            if all_stock_pnl
            else ("N/A", 0)
        )

        best_day = (
            max(daily_totals.items(), key=lambda x: x[1])
            if daily_totals
            else ("N/A", 0)
        )
        worst_day = (
            min(daily_totals.items(), key=lambda x: x[1])
            if daily_totals
            else ("N/A", 0)
        )

        summary_text = f"""
OVERALL SUMMARY

TOTAL P&L: ${total_pnl:+,.2f}
TRADING DAYS: {len(daily_totals)}
STOCKS TRADED: {total_stocks}
WIN RATE: {win_rate:.0f}%

BEST STOCK: {best_stock[0]} (${best_stock[1]:+.2f})
WORST STOCK: {worst_stock[0]} (${worst_stock[1]:+.2f})

BEST DAY: {best_day[0]} (${best_day[1]:+.2f})
WORST DAY: {worst_day[0]} (${worst_day[1]:+.2f})
        """

        plt.text(
            0.5,
            0.5,
            summary_text,
            transform=plt.gca().transAxes,
            fontsize=20,
            ha="center",
            va="center",
            fontweight="bold",
            bbox=dict(boxstyle="round,pad=1", facecolor="lightblue", alpha=0.8),
        )

        # 4. Trading Days Overview Table (Bottom)
        plt.subplot(3, 1, 3)
        plt.axis("off")

        if daily_totals:
            table_data = []
            for date_str, total in sorted(daily_totals.items()):
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                day_name = date_obj.strftime("%A")
                stocks_traded = len(
                    [s for s, p in all_stock_pnl.items() if date_str in str(all_data)]
                )
                status = (
                    "PROFIT" if total > 0 else "LOSS" if total < 0 else "BREAK-EVEN"
                )
                table_data.append([date_str, day_name, f"${total:+.2f}", status])

            table = plt.table(
                cellText=table_data,
                colLabels=["Date", "Day", "P&L", "Status"],
                cellLoc="center",
                loc="center",
                bbox=[0, 0, 1, 1],
            )

            table.auto_set_font_size(False)
            table.set_fontsize(16)
            table.scale(1, 2)

            # Color code the table
            for i in range(1, len(table_data) + 1):
                total = list(daily_totals.values())[i - 1]
                color = (
                    "lightgreen"
                    if total > 0
                    else "lightcoral" if total < 0 else "lightyellow"
                )
                table[(i, 2)].set_facecolor(color)  # P&L column
                table[(i, 3)].set_facecolor(color)  # Status column

        plt.tight_layout(rect=[0, 0.03, 1, 0.92])
        pdf.savefig(fig, bbox_inches="tight")
        plt.close()

    def create_daily_page(self, pdf, date_str, orders):
        """Create a page for a specific day's trading"""
        stock_pnl, total_pnl = self.calculate_daily_pnl(orders)

        fig = plt.figure(figsize=(16, 20))
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        day_name = date_obj.strftime("%A, %B %d, %Y")

        # Special note for August 12th
        if date_str == "2025-08-12":
            fig.suptitle(
                f"TRADING ANALYSIS - {day_name}\\nWARNING: NO PROPER RISK MANAGEMENT",
                fontsize=24,
                fontweight="bold",
                y=0.95,
                color="red",
            )
        else:
            fig.suptitle(
                f"TRADING ANALYSIS - {day_name}", fontsize=24, fontweight="bold", y=0.95
            )

        # 1. Stock Performance for the Day (Top Left)
        plt.subplot(3, 2, 1)
        if stock_pnl:
            symbols = list(stock_pnl.keys())
            pnls = list(stock_pnl.values())
            colors = ["green" if p > 0 else "red" for p in pnls]

            bars = plt.bar(symbols, pnls, color=colors, edgecolor="black", linewidth=2)
            plt.title("STOCK PERFORMANCE", fontsize=18, fontweight="bold", pad=15)
            plt.ylabel("P&L ($)", fontsize=16, fontweight="bold")
            plt.xticks(rotation=45, fontsize=14)
            plt.grid(True, alpha=0.3, axis="y")
            plt.axhline(y=0, color="black", linestyle="-", linewidth=2)

            # Add value labels
            for bar, pnl in zip(bars, pnls):
                height = bar.get_height()
                plt.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    height + (5 if height > 0 else -15),
                    f"${pnl:.1f}",
                    ha="center",
                    va="bottom" if height > 0 else "top",
                    fontsize=12,
                    fontweight="bold",
                )

        # 2. Trade Timeline (Top Right)
        plt.subplot(3, 2, 2)
        if orders:
            # Sort orders by time
            sorted_orders = sorted(orders, key=lambda x: x["filled_at"])
            times = [
                order["filled_at"].strftime("%H:%M") for order in sorted_orders[:10]
            ]  # First 10
            symbols = [order["symbol"] for order in sorted_orders[:10]]

            plt.plot(
                range(len(times)), range(len(times)), "o-", linewidth=3, markersize=8
            )
            plt.title("TRADE TIMELINE", fontsize=18, fontweight="bold", pad=15)
            plt.ylabel("Trade Number", fontsize=16, fontweight="bold")
            plt.xlabel("Time", fontsize=16, fontweight="bold")

            # Add symbol labels
            for i, (time, symbol) in enumerate(zip(times, symbols)):
                plt.text(
                    i,
                    i,
                    f"{symbol}\\n{time}",
                    ha="center",
                    va="bottom",
                    fontsize=10,
                    fontweight="bold",
                )

            plt.xticks(range(len(times)), times, rotation=45, fontsize=12)
            plt.grid(True, alpha=0.3)

        # 3. Daily Metrics (Middle)
        plt.subplot(3, 1, 2)
        plt.axis("off")

        winners = len([p for p in stock_pnl.values() if p > 0]) if stock_pnl else 0
        total_stocks = len(stock_pnl) if stock_pnl else 0
        win_rate = (winners / total_stocks * 100) if total_stocks > 0 else 0

        best_stock = (
            max(stock_pnl.items(), key=lambda x: x[1]) if stock_pnl else ("N/A", 0)
        )
        worst_stock = (
            min(stock_pnl.items(), key=lambda x: x[1]) if stock_pnl else ("N/A", 0)
        )

        total_trades = len(orders) if orders else 0
        avg_pnl = total_pnl / total_stocks if total_stocks > 0 else 0

        metrics_text = f"""
DAILY METRICS - {date_str}

TOTAL P&L: ${total_pnl:+,.2f}
TOTAL TRADES: {total_trades}
STOCKS TRADED: {total_stocks}
WIN RATE: {win_rate:.0f}%
AVG P&L PER STOCK: ${avg_pnl:+.2f}

BEST PERFORMER: {best_stock[0]} (${best_stock[1]:+.2f})
WORST PERFORMER: {worst_stock[0]} (${worst_stock[1]:+.2f})
        """

        color = (
            "lightgreen"
            if total_pnl > 0
            else "lightcoral" if total_pnl < 0 else "lightyellow"
        )
        plt.text(
            0.5,
            0.5,
            metrics_text,
            transform=plt.gca().transAxes,
            fontsize=18,
            ha="center",
            va="center",
            fontweight="bold",
            bbox=dict(boxstyle="round,pad=1", facecolor=color, alpha=0.8),
        )

        # 4. Trade Details Table (Bottom)
        plt.subplot(3, 1, 3)
        plt.axis("off")

        if stock_pnl:
            table_data = []
            for symbol, pnl in sorted(
                stock_pnl.items(), key=lambda x: x[1], reverse=True
            ):
                symbol_orders = [o for o in orders if o["symbol"] == symbol]
                trade_count = len(symbol_orders)
                avg_pnl = pnl / trade_count if trade_count > 0 else 0
                status = "PROFIT" if pnl > 0 else "LOSS" if pnl < 0 else "BREAK-EVEN"
                table_data.append(
                    [symbol, f"${pnl:+.2f}", trade_count, f"${avg_pnl:+.2f}", status]
                )

            table = plt.table(
                cellText=table_data,
                colLabels=["Stock", "Total P&L", "Trades", "Avg P&L", "Status"],
                cellLoc="center",
                loc="center",
                bbox=[0, 0, 1, 1],
            )

            table.auto_set_font_size(False)
            table.set_fontsize(14)
            table.scale(1, 2)

            # Color code the table
            for i in range(1, len(table_data) + 1):
                pnl = list(stock_pnl.values())[i - 1]
                color = (
                    "lightgreen"
                    if pnl > 0
                    else "lightcoral" if pnl < 0 else "lightyellow"
                )
                table[(i, 1)].set_facecolor(color)  # P&L column
                table[(i, 4)].set_facecolor(color)  # Status column

        plt.tight_layout(rect=[0, 0.03, 1, 0.92])
        pdf.savefig(fig, bbox_inches="tight")
        plt.close()

    def create_multi_page_report(self, output_dir="reports/daily"):
        """Create multi-page PDF report"""
        try:
            os.makedirs(output_dir, exist_ok=True)

            # Get data by day
            all_data = self.get_trading_data_by_day(days_back=10)
            if not all_data:
                print("No trading data found")
                return None

            # Create PDF
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pdf_path = os.path.join(
                output_dir, f"multi_page_trading_report_{timestamp}.pdf"
            )

            with PdfPages(pdf_path) as pdf:
                print(
                    f"Creating multi-page report with {len(all_data)} trading days..."
                )

                # Page 1: Overview
                print("Creating overview page...")
                self.create_overview_page(pdf, all_data)

                # Individual day pages
                for date_str in sorted(all_data.keys()):
                    print(f"Creating page for {date_str}...")
                    self.create_daily_page(pdf, date_str, all_data[date_str])

                # Add metadata
                d = pdf.infodict()
                d["Title"] = "Multi-Page Trading Report"
                d["Author"] = "Scalping Bot System"
                d["Subject"] = "Daily Trading Analysis"
                d["Keywords"] = "Trading, P&L, Analysis"
                d["Creator"] = "Python Matplotlib"

            return pdf_path

        except Exception as e:
            self.logger.error(f"Error creating multi-page report: {e}")
            return None


def main():
    """Main function"""
    try:
        report = MultiPageTradingReport()

        print("Creating Multi-Page Trading Report...")
        pdf_path = report.create_multi_page_report()

        if pdf_path:
            print(f"\\nMulti-Page Trading Report created: {pdf_path}")
            print("\\nReport includes:")
            print("- Page 1: Overall summary across all days")
            print("- Separate pages for each trading day")
            print("- August 12th page marked with risk management warning")
            print("- August 14th and other days shown separately")
        else:
            print("Failed to create report")

    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
