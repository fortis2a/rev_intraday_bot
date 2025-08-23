#!/usr/bin/env python3
"""
Simple Readable Dashboard Generator
Creates a clean, easy-to-read dashboard with large text and clear charts
"""

import os
import sys
from datetime import date, datetime, timedelta

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# Add the parent directory to sys.path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.data_manager import DataManager
from utils.logger import setup_logger


class SimpleReadableDashboard:
    """Create simple, readable dashboard with large text"""

    def __init__(self):
        self.logger = setup_logger("SimpleReadableDashboard")
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
                "font.size": 20,  # Very large base font
                "axes.titlesize": 24,  # Large titles
                "axes.labelsize": 22,  # Large axis labels
                "xtick.labelsize": 18,  # Large tick labels
                "ytick.labelsize": 18,
                "legend.fontsize": 18,
                "figure.titlesize": 30,  # Very large figure title
            }
        )

    def get_simple_data(self):
        """Get simple trading data excluding August 12th"""
        try:
            # Define the date to exclude
            exclude_date = date(2025, 8, 12)
            start_date = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")

            # Get orders
            orders = self.api.list_orders(status="filled", limit=500, after=start_date)

            # Filter out August 12th
            filtered_orders = []
            for order in orders:
                if hasattr(order, "filled_at") and order.filled_at:
                    order_date = order.filled_at.date()
                    if order_date != exclude_date:
                        filtered_orders.append(order)

            # Process into simple format
            trades = []
            symbol_groups = {}

            for order in filtered_orders:
                symbol = order.symbol
                if symbol not in symbol_groups:
                    symbol_groups[symbol] = {"buys": [], "sells": []}

                qty = float(order.filled_qty or order.qty)
                price = float(order.filled_avg_price or 0)

                if order.side == "buy":
                    symbol_groups[symbol]["buys"].append({"qty": qty, "price": price})
                else:
                    symbol_groups[symbol]["sells"].append({"qty": qty, "price": price})

            # Calculate P&L using FIFO
            stock_pnl = {}
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

            return stock_pnl

        except Exception as e:
            self.logger.error(f"Error getting simple data: {e}")
            return None

    def create_simple_dashboard(self, output_dir="reports/daily"):
        """Create simple, readable dashboard"""
        try:
            os.makedirs(output_dir, exist_ok=True)

            # Get data
            stock_pnl = self.get_simple_data()
            if not stock_pnl:
                print("Unable to retrieve data")
                return None

            # Create figure with 4 simple panels
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(24, 18))
            fig.suptitle(
                "SIMPLE TRADING DASHBOARD - EASY TO READ",
                fontsize=36,
                fontweight="bold",
                y=0.95,
            )

            # Add summary info
            total_pnl = sum(stock_pnl.values())
            winners = len([p for p in stock_pnl.values() if p > 0])
            total_stocks = len(stock_pnl)

            summary_text = f"Total P&L: ${total_pnl:+,.2f} | Winners: {winners}/{total_stocks} | Date: {datetime.now().strftime('%B %d, %Y')}"
            fig.text(
                0.5, 0.91, summary_text, ha="center", fontsize=24, fontweight="bold"
            )

            # 1. Stock Performance Bar Chart (Top Left)
            symbols = list(stock_pnl.keys())
            pnls = list(stock_pnl.values())
            colors = ["green" if p > 0 else "red" for p in pnls]

            bars = ax1.bar(symbols, pnls, color=colors, edgecolor="black", linewidth=2)
            ax1.set_title("STOCK PERFORMANCE", fontsize=28, fontweight="bold", pad=30)
            ax1.set_ylabel("Profit/Loss ($)", fontsize=24, fontweight="bold")
            ax1.tick_params(axis="x", rotation=45, labelsize=20)
            ax1.grid(True, alpha=0.3, axis="y")
            ax1.axhline(y=0, color="black", linestyle="-", linewidth=2)

            # Add value labels on bars
            for bar, pnl in zip(bars, pnls):
                height = bar.get_height()
                ax1.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    height + (10 if height > 0 else -20),
                    f"${pnl:.0f}",
                    ha="center",
                    va="bottom" if height > 0 else "top",
                    fontsize=18,
                    fontweight="bold",
                )

            # 2. Winners vs Losers Pie Chart (Top Right)
            losers = total_stocks - winners
            pie_data = [winners, losers]
            pie_labels = [f"Winners\\n{winners} stocks", f"Losers\\n{losers} stocks"]
            pie_colors = ["green", "red"]

            wedges, texts, autotexts = ax2.pie(
                pie_data,
                labels=pie_labels,
                colors=pie_colors,
                autopct="%1.0f%%",
                startangle=90,
                textprops={"fontsize": 20, "fontweight": "bold"},
            )
            ax2.set_title("WIN/LOSS BREAKDOWN", fontsize=28, fontweight="bold", pad=30)

            # 3. Top Performers Table (Bottom Left)
            ax3.axis("off")

            # Sort stocks by performance
            sorted_stocks = sorted(stock_pnl.items(), key=lambda x: x[1], reverse=True)

            # Create table data
            table_data = []
            for i, (symbol, pnl) in enumerate(sorted_stocks[:6], 1):  # Top 6
                status = "PROFIT" if pnl > 0 else "LOSS"
                table_data.append([f"{i}", symbol, f"${pnl:+.2f}", status])

            table = ax3.table(
                cellText=table_data,
                colLabels=["Rank", "Stock", "P&L", "Status"],
                cellLoc="center",
                loc="center",
                bbox=[0, 0, 1, 1],
            )

            table.auto_set_font_size(False)
            table.set_fontsize(20)
            table.scale(1, 3)

            # Color code the table
            for i in range(1, len(table_data) + 1):
                pnl = sorted_stocks[i - 1][1]
                color = "lightgreen" if pnl > 0 else "lightcoral"
                table[(i, 2)].set_facecolor(color)  # P&L column
                table[(i, 3)].set_facecolor(color)  # Status column

            ax3.set_title("STOCK RANKINGS", fontsize=28, fontweight="bold", pad=30)

            # 4. Key Metrics (Bottom Right)
            ax4.axis("off")

            best_stock = max(stock_pnl.items(), key=lambda x: x[1])
            worst_stock = min(stock_pnl.items(), key=lambda x: x[1])
            win_rate = (winners / total_stocks * 100) if total_stocks > 0 else 0

            metrics_text = f"""
KEY METRICS

TOTAL P&L: ${total_pnl:+,.2f}

WIN RATE: {win_rate:.0f}%

BEST STOCK: {best_stock[0]}
${best_stock[1]:+.2f}

WORST STOCK: {worst_stock[0]}
${worst_stock[1]:+.2f}

STOCKS TRADED: {total_stocks}
            """

            ax4.text(
                0.5,
                0.5,
                metrics_text,
                transform=ax4.transAxes,
                fontsize=22,
                ha="center",
                va="center",
                fontweight="bold",
                bbox=dict(boxstyle="round,pad=1", facecolor="lightblue", alpha=0.8),
            )

            plt.tight_layout(rect=[0, 0.03, 1, 0.88])

            # Save dashboard
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dashboard_path = os.path.join(
                output_dir, f"simple_readable_dashboard_{timestamp}.png"
            )
            plt.savefig(dashboard_path, dpi=300, bbox_inches="tight", facecolor="white")
            plt.close()

            return dashboard_path

        except Exception as e:
            self.logger.error(f"Error creating simple dashboard: {e}")
            return None


def main():
    """Main function"""
    try:
        dashboard = SimpleReadableDashboard()

        print("Creating Simple, Readable Dashboard...")
        dashboard_path = dashboard.create_simple_dashboard()

        if dashboard_path:
            print(f"Simple Readable Dashboard created: {dashboard_path}")
        else:
            print("Failed to create dashboard")

    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
