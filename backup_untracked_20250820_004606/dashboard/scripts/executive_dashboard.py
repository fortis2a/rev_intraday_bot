#!/usr/bin/env python3
"""
Executive Dashboard Generator
Creates a focused executive summary chart with key performance metrics
"""

import os
import sys
from datetime import datetime

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# Add the parent directory to sys.path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.data_manager import DataManager
from utils.logger import setup_logger


class ExecutiveDashboard:
    """Create executive summary dashboard"""

    def __init__(self):
        self.logger = setup_logger("ExecutiveDashboard")
        self.data_manager = DataManager()
        self.api = self.data_manager.api

        # Set up professional styling
        plt.style.use("seaborn-v0_8-whitegrid")
        plt.rcParams.update(
            {
                "figure.facecolor": "white",
                "axes.facecolor": "white",
                "axes.edgecolor": "black",
                "axes.linewidth": 1.5,
                "grid.alpha": 0.3,
                "font.size": 11,
                "axes.titlesize": 14,
                "axes.labelsize": 12,
                "xtick.labelsize": 10,
                "ytick.labelsize": 10,
                "legend.fontsize": 10,
                "figure.titlesize": 18,
            }
        )

    def get_trading_summary(self):
        """Get summarized trading data"""
        try:
            # Get today's orders
            today = datetime.now().strftime("%Y-%m-%d")
            orders = self.api.list_orders(status="filled", limit=200, after=today)

            # Process into trades (simplified)
            symbol_groups = {}
            for order in orders:
                symbol = order.symbol
                if symbol not in symbol_groups:
                    symbol_groups[symbol] = {"buys": [], "sells": []}

                order_data = {
                    "qty": float(order.filled_qty or order.qty),
                    "price": float(order.filled_avg_price or 0),
                    "time": order.filled_at or order.created_at,
                }

                if order.side == "buy":
                    symbol_groups[symbol]["buys"].append(order_data)
                else:
                    symbol_groups[symbol]["sells"].append(order_data)

            # Calculate summary metrics
            summary = {}
            total_pnl = 0
            total_trades = 0
            total_volume = 0

            for symbol, trades in symbol_groups.items():
                buys = sorted(trades["buys"], key=lambda x: x["time"])
                sells = sorted(trades["sells"], key=lambda x: x["time"])

                symbol_pnl = 0
                symbol_trades = 0
                symbol_volume = 0

                buy_queue = buys.copy()
                for sell in sells:
                    sell_qty_remaining = sell["qty"]

                    while sell_qty_remaining > 0 and buy_queue:
                        buy = buy_queue[0]
                        matched_qty = min(sell_qty_remaining, buy["qty"])

                        trade_pnl = matched_qty * (sell["price"] - buy["price"])
                        symbol_pnl += trade_pnl
                        symbol_trades += 1
                        symbol_volume += matched_qty * buy["price"]

                        sell_qty_remaining -= matched_qty
                        buy["qty"] -= matched_qty

                        if buy["qty"] <= 0:
                            buy_queue.pop(0)

                summary[symbol] = {
                    "pnl": symbol_pnl,
                    "trades": symbol_trades,
                    "volume": symbol_volume,
                }

                total_pnl += symbol_pnl
                total_trades += symbol_trades
                total_volume += symbol_volume

            # Get account data
            account = self.api.get_account()
            daily_pnl = float(account.equity) - float(account.last_equity)

            return {
                "symbols": summary,
                "total_pnl": total_pnl,
                "total_trades": total_trades,
                "total_volume": total_volume,
                "account_pnl": daily_pnl,
                "equity": float(account.equity),
            }

        except Exception as e:
            self.logger.error(f"Error getting trading summary: {e}")
            return None

    def create_executive_dashboard(self, output_dir="reports/daily"):
        """Create executive summary dashboard"""
        try:
            os.makedirs(output_dir, exist_ok=True)

            # Get data
            data = self.get_trading_summary()
            if not data:
                print("❌ Unable to retrieve trading data")
                return None

            # Create executive dashboard figure
            fig = plt.figure(figsize=(16, 10))
            fig.suptitle(
                "📊 Executive Trading Dashboard - Daily Performance Summary",
                fontsize=18,
                fontweight="bold",
                y=0.95,
            )

            # Add date and account info
            date_str = datetime.now().strftime("%B %d, %Y")
            account_info = f"Date: {date_str} | Account Equity: ${data['equity']:,.2f} | Daily P&L: ${data['account_pnl']:+,.2f}"
            fig.text(0.5, 0.91, account_info, ha="center", fontsize=12, style="italic")

            # 1. Stock Performance Overview (Top Left)
            ax1 = plt.subplot(2, 3, 1)
            symbols = list(data["symbols"].keys())
            pnls = [data["symbols"][s]["pnl"] for s in symbols]

            colors = ["#2E8B57" if pnl > 0 else "#DC143C" for pnl in pnls]
            bars = plt.bar(
                symbols, pnls, color=colors, edgecolor="black", linewidth=1.5
            )

            plt.title("💰 P&L by Stock", fontsize=14, fontweight="bold", pad=15)
            plt.ylabel("P&L ($)", fontweight="bold")
            plt.grid(True, alpha=0.3, axis="y")

            # Add value labels
            for bar, pnl in zip(bars, pnls):
                height = bar.get_height()
                plt.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    height + (abs(height) * 0.1 if height != 0 else 1),
                    f"${pnl:.2f}",
                    ha="center",
                    va="bottom" if height >= 0 else "top",
                    fontweight="bold",
                    fontsize=10,
                )

            # 2. Trade Distribution (Top Middle)
            ax2 = plt.subplot(2, 3, 2)
            trade_counts = [data["symbols"][s]["trades"] for s in symbols]

            plt.pie(
                trade_counts,
                labels=symbols,
                autopct="%1.0f%%",
                startangle=90,
                colors=["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4"],
                explode=[0.05] * len(symbols),
            )
            plt.title("📊 Trade Distribution", fontsize=14, fontweight="bold", pad=15)

            # 3. Key Metrics Summary (Top Right)
            ax3 = plt.subplot(2, 3, 3)
            ax3.axis("off")

            # Calculate additional metrics
            winning_stocks = len([s for s in symbols if data["symbols"][s]["pnl"] > 0])
            win_rate = (winning_stocks / len(symbols) * 100) if symbols else 0
            avg_pnl_per_trade = (
                data["total_pnl"] / data["total_trades"]
                if data["total_trades"] > 0
                else 0
            )

            metrics_text = f"""
📈 KEY PERFORMANCE METRICS

🎯 Trading Activity:
   • Total Trades: {data['total_trades']}
   • Stocks Traded: {len(symbols)}
   • Total Volume: ${data['total_volume']:,.0f}

💰 Profitability:
   • Total P&L: ${data['total_pnl']:+.2f}
   • Avg/Trade: ${avg_pnl_per_trade:+.2f}
   • Stock Win Rate: {win_rate:.0f}%

🏦 Account Status:
   • Daily P&L: ${data['account_pnl']:+.2f}
   • Current Equity: ${data['equity']:,.2f}
   • Return: {(data['account_pnl']/data['equity']*100):+.3f}%
            """

            plt.text(
                0.05,
                0.95,
                metrics_text,
                transform=ax3.transAxes,
                fontsize=11,
                verticalalignment="top",
                fontfamily="monospace",
                bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.8),
            )

            # 4. Performance Gauge (Bottom Left)
            ax4 = plt.subplot(2, 3, 4)

            # Create a gauge chart for daily performance
            angles = np.linspace(0, np.pi, 100)

            # Performance zones
            plt.fill_between(
                angles,
                0,
                1,
                where=(angles <= np.pi / 3),
                color="red",
                alpha=0.3,
                label="Poor",
            )
            plt.fill_between(
                angles,
                0,
                1,
                where=((angles > np.pi / 3) & (angles <= 2 * np.pi / 3)),
                color="yellow",
                alpha=0.3,
                label="Average",
            )
            plt.fill_between(
                angles,
                0,
                1,
                where=(angles > 2 * np.pi / 3),
                color="green",
                alpha=0.3,
                label="Good",
            )

            # Calculate performance score (0-100)
            score = max(
                0, min(100, (data["account_pnl"] + 50) * 2)
            )  # Normalize around break-even
            score_angle = score / 100 * np.pi

            # Draw needle
            plt.arrow(
                0,
                0,
                0.8 * np.cos(score_angle),
                0.8 * np.sin(score_angle),
                head_width=0.05,
                head_length=0.1,
                fc="black",
                ec="black",
                linewidth=3,
            )

            plt.xlim(-1.2, 1.2)
            plt.ylim(-0.2, 1.2)
            plt.axis("off")
            plt.title("📊 Performance Gauge", fontsize=14, fontweight="bold", pad=15)
            plt.text(
                0,
                -0.1,
                f"Score: {score:.0f}/100",
                ha="center",
                fontsize=12,
                fontweight="bold",
            )

            # 5. Stock Comparison Matrix (Bottom Middle)
            ax5 = plt.subplot(2, 3, 5)

            # Create comparison table
            table_data = []
            for symbol in symbols:
                pnl = data["symbols"][symbol]["pnl"]
                trades = data["symbols"][symbol]["trades"]
                avg_pnl = pnl / trades if trades > 0 else 0
                table_data.append([symbol, f"${pnl:+.2f}", trades, f"${avg_pnl:+.2f}"])

            table = plt.table(
                cellText=table_data,
                colLabels=["Stock", "Total P&L", "Trades", "Avg P&L"],
                cellLoc="center",
                loc="center",
                bbox=[0, 0, 1, 1],
            )

            table.auto_set_font_size(False)
            table.set_fontsize(10)
            table.scale(1, 2)

            # Color code the P&L cells
            for i in range(1, len(table_data) + 1):
                pnl = data["symbols"][symbols[i - 1]]["pnl"]
                color = "#90EE90" if pnl > 0 else "#FFB6C1"  # Light green or light red
                table[(i, 1)].set_facecolor(color)

            plt.axis("off")
            plt.title(
                "📋 Stock Performance Matrix", fontsize=14, fontweight="bold", pad=15
            )

            # 6. Trading Timeline (Bottom Right)
            ax6 = plt.subplot(2, 3, 6)

            # Simplified timeline showing cumulative performance
            cumulative_pnl = []
            running_total = 0

            for symbol in symbols:
                running_total += data["symbols"][symbol]["pnl"]
                cumulative_pnl.append(running_total)

            x_pos = range(len(symbols))
            plt.plot(
                x_pos,
                cumulative_pnl,
                marker="o",
                linewidth=3,
                markersize=8,
                color="#1f77b4",
                markerfacecolor="white",
                markeredgecolor="#1f77b4",
                markeredgewidth=2,
            )

            # Fill area
            plt.fill_between(
                x_pos,
                cumulative_pnl,
                0,
                alpha=0.3,
                color="green" if cumulative_pnl[-1] > 0 else "red",
            )

            plt.title(
                "📈 Cumulative Performance", fontsize=14, fontweight="bold", pad=15
            )
            plt.xlabel("Stock Order", fontweight="bold")
            plt.ylabel("Cumulative P&L ($)", fontweight="bold")
            plt.xticks(x_pos, symbols)
            plt.grid(True, alpha=0.3)

            # Add final value annotation
            if cumulative_pnl:
                plt.annotate(
                    f"Final: ${cumulative_pnl[-1]:.2f}",
                    xy=(len(symbols) - 1, cumulative_pnl[-1]),
                    xytext=(10, 20),
                    textcoords="offset points",
                    bbox=dict(
                        boxstyle="round,pad=0.3",
                        facecolor="green" if cumulative_pnl[-1] > 0 else "red",
                        alpha=0.7,
                    ),
                    arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0"),
                    fontweight="bold",
                    color="white",
                )

            plt.tight_layout(rect=[0, 0.03, 1, 0.88])

            # Save dashboard
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dashboard_path = os.path.join(
                output_dir, f"executive_dashboard_{timestamp}.png"
            )
            plt.savefig(dashboard_path, dpi=300, bbox_inches="tight", facecolor="white")
            plt.close()

            return dashboard_path

        except Exception as e:
            self.logger.error(f"Error creating executive dashboard: {e}")
            return None


def main():
    """Main function"""
    try:
        dashboard = ExecutiveDashboard()

        print("🔍 Creating Executive Dashboard...")
        dashboard_path = dashboard.create_executive_dashboard()

        if dashboard_path:
            print(f"✅ Executive Dashboard created: {dashboard_path}")
        else:
            print("❌ Failed to create dashboard")

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
