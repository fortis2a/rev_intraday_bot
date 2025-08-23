#!/usr/bin/env python3
"""
Comprehensive P&L Report Generator with Charts and Analytics
Uses actual Alpaca trading data to generate detailed performance analysis

Features:
1. Stock-by-stock profitability analysis
2. Long/short position performance
3. Time-based profitability (morning/midday/evening)
4. Win rate and risk metrics
5. Risk-adjusted returns and ratios
6. Visual charts and graphs
7. Comprehensive summary statistics
"""

import os
import sys
import warnings
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages

warnings.filterwarnings("ignore")

# Add the parent directory to sys.path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.data_manager import DataManager
from utils.logger import setup_logger


class ComprehensivePnLReportGenerator:
    """Generate comprehensive P&L reports with charts and analytics"""

    def __init__(self):
        self.logger = setup_logger("ComprehensivePnLReport")
        self.data_manager = DataManager()
        self.api = self.data_manager.api

        # Set up matplotlib style for professional appearance with LARGER text
        plt.style.use("seaborn-v0_8-whitegrid")
        plt.rcParams.update(
            {
                "figure.facecolor": "white",
                "axes.facecolor": "white",
                "axes.edgecolor": "black",
                "axes.linewidth": 1.5,
                "grid.alpha": 0.3,
                "font.size": 14,  # Increased from 10
                "axes.titlesize": 18,  # Increased from 12
                "axes.labelsize": 16,  # Increased from 10
                "xtick.labelsize": 14,  # Increased from 9
                "ytick.labelsize": 14,  # Increased from 9
                "legend.fontsize": 14,  # Increased from 9
                "figure.titlesize": 22,  # Increased from 16
            }
        )
        sns.set_palette("Set2")

    def get_trading_data(self, days_back=5):
        """Get comprehensive trading data for analysis, excluding August 12th"""
        try:
            from datetime import date

            start_date = (datetime.now() - timedelta(days=days_back)).strftime(
                "%Y-%m-%d"
            )

            # Define the date to exclude (August 12, 2025)
            exclude_date = date(2025, 8, 12)

            print(f"📅 Analyzing trades from {start_date} to now")
            print(f"🚫 Will exclude trades from: {exclude_date}")

            # Get filled orders
            orders = self.api.list_orders(status="filled", limit=500, after=start_date)

            # Filter out orders from August 12th
            filtered_orders = []
            excluded_count = 0
            excluded_trades_info = []

            for order in orders:
                if hasattr(order, "filled_at") and order.filled_at:
                    order_date = order.filled_at.date()
                    if order_date != exclude_date:
                        filtered_orders.append(order)
                    else:
                        excluded_count += 1
                        excluded_trades_info.append(
                            f"{order.symbol} {order.side} {order.filled_qty}@${order.filled_avg_price}"
                        )

            print(f"🔍 Total orders retrieved: {len(orders)}")
            print(f"❌ Excluded orders from August 12th: {excluded_count}")
            if excluded_trades_info:
                print(
                    f"📋 Excluded trades: {', '.join(excluded_trades_info[:5])}{'...' if len(excluded_trades_info) > 5 else ''}"
                )
            print(f"✅ Orders included in analysis: {len(filtered_orders)}")

            # Get portfolio history for time-based analysis
            portfolio_history = self.api.get_portfolio_history(
                period="1D", timeframe="1Min"
            )

            # Get account data
            account = self.api.get_account()

            return {
                "orders": filtered_orders,
                "portfolio_history": portfolio_history,
                "account": account,
            }

        except Exception as e:
            self.logger.error(f"Error getting trading data: {e}")
            return None

    def process_trades(self, orders):
        """Process orders into completed trades with detailed analysis (excluding August 12th)"""
        try:
            from datetime import date

            # Define the date to exclude
            exclude_date = date(2025, 8, 12)

            # Convert orders to detailed format, excluding August 12th
            detailed_orders = []
            for order in orders:
                # Skip if this is from August 12th
                if hasattr(order, "filled_at") and order.filled_at:
                    order_date = order.filled_at.date()
                    if order_date == exclude_date:
                        continue

                filled_qty = float(order.filled_qty or order.qty)
                filled_price = float(order.filled_avg_price or 0)

                order_data = {
                    "id": order.id,
                    "symbol": order.symbol,
                    "side": order.side,
                    "qty": filled_qty,
                    "price": filled_price,
                    "filled_at": order.filled_at,
                    "created_at": order.created_at,
                    "order_type": order.order_type,
                    "notional": (
                        float(order.notional)
                        if hasattr(order, "notional") and order.notional
                        else filled_qty * filled_price
                    ),
                }
                detailed_orders.append(order_data)

            # Group by symbol and match trades
            symbol_groups = {}
            for order in detailed_orders:
                symbol = order["symbol"]
                if symbol not in symbol_groups:
                    symbol_groups[symbol] = {"buys": [], "sells": []}

                if order["side"] == "buy":
                    symbol_groups[symbol]["buys"].append(order)
                else:
                    symbol_groups[symbol]["sells"].append(order)

            # Match trades using FIFO and create trade records
            all_trades = []

            for symbol, trades in symbol_groups.items():
                buys = sorted(
                    trades["buys"], key=lambda x: x["filled_at"] or x["created_at"]
                )
                sells = sorted(
                    trades["sells"], key=lambda x: x["filled_at"] or x["created_at"]
                )

                buy_queue = buys.copy()

                for sell in sells:
                    sell_qty_remaining = sell["qty"]

                    while sell_qty_remaining > 0 and buy_queue:
                        buy = buy_queue[0]
                        buy_qty_available = buy["qty"]

                        # Match quantities
                        matched_qty = min(sell_qty_remaining, buy_qty_available)

                        # Calculate trade metrics
                        buy_price = buy["price"]
                        sell_price = sell["price"]
                        trade_pnl = matched_qty * (sell_price - buy_price)
                        trade_value = matched_qty * buy_price
                        trade_return = (sell_price - buy_price) / buy_price * 100

                        # Determine time periods
                        buy_time = buy["filled_at"] or buy["created_at"]
                        sell_time = sell["filled_at"] or sell["created_at"]

                        if isinstance(buy_time, str):
                            buy_time = datetime.fromisoformat(
                                buy_time.replace("Z", "+00:00")
                            )
                        if isinstance(sell_time, str):
                            sell_time = datetime.fromisoformat(
                                sell_time.replace("Z", "+00:00")
                            )

                        # Convert to local time (ET)
                        buy_hour = (
                            buy_time.hour
                            if buy_time.tzinfo
                            else (buy_time - timedelta(hours=4)).hour
                        )
                        sell_hour = (
                            sell_time.hour
                            if sell_time.tzinfo
                            else (sell_time - timedelta(hours=4)).hour
                        )

                        # Determine trading period
                        avg_hour = (buy_hour + sell_hour) / 2
                        if (
                            6 <= avg_hour < 11
                        ):  # 6 AM - 11 AM ET (10 AM - 3 PM market time)
                            period = "Morning"
                        elif 11 <= avg_hour < 14:  # 11 AM - 2 PM ET
                            period = "Midday"
                        else:  # 2 PM - 7:30 PM ET (market close at 3:30 PM)
                            period = "Evening"

                        # Create trade record
                        trade_record = {
                            "symbol": symbol,
                            "side": "long",  # All trades are long positions in this system
                            "qty": matched_qty,
                            "buy_price": buy_price,
                            "sell_price": sell_price,
                            "pnl": trade_pnl,
                            "return_pct": trade_return,
                            "trade_value": trade_value,
                            "buy_time": buy_time,
                            "sell_time": sell_time,
                            "period": period,
                            "hold_duration": (sell_time - buy_time).total_seconds()
                            / 60,  # minutes
                            "is_profitable": trade_pnl > 0,
                            "buy_order_id": buy["id"],
                            "sell_order_id": sell["id"],
                        }

                        all_trades.append(trade_record)

                        # Update quantities
                        sell_qty_remaining -= matched_qty
                        buy["qty"] -= matched_qty

                        if buy["qty"] <= 0:
                            buy_queue.pop(0)

            return all_trades

        except Exception as e:
            self.logger.error(f"Error processing trades: {e}")
            return []

    def calculate_performance_metrics(self, trades):
        """Calculate comprehensive performance metrics"""
        try:
            if not trades:
                return {}

            df = pd.DataFrame(trades)

            # Basic metrics
            total_trades = len(trades)
            profitable_trades = sum(1 for t in trades if t["is_profitable"])
            losing_trades = total_trades - profitable_trades

            total_pnl = sum(t["pnl"] for t in trades)
            total_value = sum(t["trade_value"] for t in trades)

            # Win rate
            win_rate = (
                (profitable_trades / total_trades * 100) if total_trades > 0 else 0
            )

            # Average P&L per trade
            avg_pnl_per_trade = total_pnl / total_trades if total_trades > 0 else 0

            # Profit factor (sum of profits / abs(sum of losses))
            total_profits = sum(t["pnl"] for t in trades if t["pnl"] > 0)
            total_losses = abs(sum(t["pnl"] for t in trades if t["pnl"] < 0))
            profit_factor = (
                total_profits / total_losses if total_losses > 0 else float("inf")
            )

            # Expected value
            expected_value = avg_pnl_per_trade

            # Risk metrics
            returns = [t["return_pct"] for t in trades]
            avg_return = np.mean(returns) if returns else 0
            std_return = np.std(returns) if len(returns) > 1 else 0

            # Sharpe ratio (assuming risk-free rate = 0 for intraday)
            sharpe_ratio = avg_return / std_return if std_return > 0 else 0

            # Risk-reward ratio
            avg_win = (
                np.mean([t["pnl"] for t in trades if t["pnl"] > 0])
                if profitable_trades > 0
                else 0
            )
            avg_loss = (
                abs(np.mean([t["pnl"] for t in trades if t["pnl"] < 0]))
                if losing_trades > 0
                else 0
            )
            risk_reward_ratio = avg_win / avg_loss if avg_loss > 0 else float("inf")

            # Maximum consecutive wins/losses
            consecutive_wins = 0
            consecutive_losses = 0
            max_consecutive_wins = 0
            max_consecutive_losses = 0

            for trade in trades:
                if trade["is_profitable"]:
                    consecutive_wins += 1
                    consecutive_losses = 0
                    max_consecutive_wins = max(max_consecutive_wins, consecutive_wins)
                else:
                    consecutive_losses += 1
                    consecutive_wins = 0
                    max_consecutive_losses = max(
                        max_consecutive_losses, consecutive_losses
                    )

            # Drawdown analysis
            cumulative_pnl = []
            running_total = 0
            for trade in trades:
                running_total += trade["pnl"]
                cumulative_pnl.append(running_total)

            peak = cumulative_pnl[0]
            max_drawdown = 0
            for value in cumulative_pnl:
                if value > peak:
                    peak = value
                drawdown = peak - value
                if drawdown > max_drawdown:
                    max_drawdown = drawdown

            max_drawdown_pct = (max_drawdown / peak * 100) if peak > 0 else 0

            return {
                "total_trades": total_trades,
                "profitable_trades": profitable_trades,
                "losing_trades": losing_trades,
                "win_rate": win_rate,
                "total_pnl": total_pnl,
                "total_value_traded": total_value,
                "avg_pnl_per_trade": avg_pnl_per_trade,
                "profit_factor": profit_factor,
                "expected_value": expected_value,
                "avg_return_pct": avg_return,
                "std_return_pct": std_return,
                "sharpe_ratio": sharpe_ratio,
                "risk_reward_ratio": risk_reward_ratio,
                "avg_win": avg_win,
                "avg_loss": avg_loss,
                "max_consecutive_wins": max_consecutive_wins,
                "max_consecutive_losses": max_consecutive_losses,
                "max_drawdown": max_drawdown,
                "max_drawdown_pct": max_drawdown_pct,
                "total_profits": total_profits,
                "total_losses": total_losses,
            }

        except Exception as e:
            self.logger.error(f"Error calculating performance metrics: {e}")
            return {}

    def create_visualizations(self, trades, metrics, output_dir="reports/daily"):
        """Create comprehensive visualizations with professional formatting"""
        try:
            if not trades:
                return None

            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)

            df = pd.DataFrame(trades)

            # Create figure with larger size and better spacing
            fig = plt.figure(figsize=(30, 40))  # Increased from 24x32
            fig.suptitle(
                "Comprehensive Trading Performance Analysis",
                fontsize=28,
                fontweight="bold",
                y=0.98,
            )  # Increased from 20

            # Add date and summary info
            date_str = datetime.now().strftime("%B %d, %Y")
            summary_text = f"Analysis Date: {date_str} | Total Trades: {len(trades)} | Total P&L: ${metrics['total_pnl']:+,.2f} | Win Rate: {metrics['win_rate']:.1f}%"
            fig.text(
                0.5, 0.96, summary_text, ha="center", fontsize=18, style="italic"
            )  # Increased from 12

            # 1. Stock Performance Analysis (Enhanced)
            plt.subplot(4, 3, 1)
            stock_pnl = df.groupby("symbol")["pnl"].sum().sort_values(ascending=False)
            colors = ["#2E8B57" if x > 0 else "#DC143C" for x in stock_pnl.values]
            bars = stock_pnl.plot(
                kind="bar", color=colors, edgecolor="black", linewidth=1
            )
            plt.title(
                "P&L by Stock", fontsize=18, fontweight="bold", pad=20
            )  # Increased from 14
            plt.ylabel("P&L ($)", fontweight="bold")
            plt.xlabel("Stock Symbol", fontweight="bold")
            plt.xticks(rotation=0)
            plt.grid(True, alpha=0.3, axis="y")

            # Enhanced value labels with better positioning
            for i, v in enumerate(stock_pnl.values):
                color = (
                    "white" if abs(v) > max(abs(stock_pnl.values)) * 0.5 else "black"
                )
                plt.text(
                    i,
                    v / 2,
                    f"${v:.2f}",
                    ha="center",
                    va="center",
                    fontweight="bold",
                    color=color,
                    fontsize=10,
                )
                plt.text(
                    i,
                    v
                    + (
                        max(stock_pnl.values) * 0.05
                        if v >= 0
                        else min(stock_pnl.values) * 0.05
                    ),
                    f"${v:.2f}",
                    ha="center",
                    va="bottom" if v >= 0 else "top",
                    fontweight="bold",
                    fontsize=9,
                )

            # 2. Trade Count by Stock (Enhanced)
            plt.subplot(4, 3, 2)
            trade_counts = df["symbol"].value_counts().sort_index()
            bars = trade_counts.plot(
                kind="bar", color="#4682B4", edgecolor="black", linewidth=1
            )
            plt.title(
                "📊 Trade Volume by Stock", fontsize=14, fontweight="bold", pad=20
            )
            plt.ylabel("Number of Trades", fontweight="bold")
            plt.xlabel("Stock Symbol", fontweight="bold")
            plt.xticks(rotation=0)
            plt.grid(True, alpha=0.3, axis="y")

            # Add value labels
            for i, v in enumerate(trade_counts.values):
                plt.text(
                    i, v + 0.5, str(v), ha="center", va="bottom", fontweight="bold"
                )

            # 3. Win Rate by Stock (Enhanced)
            plt.subplot(4, 3, 3)
            stock_winrate = df.groupby("symbol")["is_profitable"].mean() * 100
            colors_wr = [
                "#228B22" if x >= 50 else "#FF6347" if x >= 30 else "#DC143C"
                for x in stock_winrate.values
            ]
            stock_winrate.plot(
                kind="bar", color=colors_wr, edgecolor="black", linewidth=1
            )
            plt.title("🎯 Win Rate by Stock", fontsize=14, fontweight="bold", pad=20)
            plt.ylabel("Win Rate (%)", fontweight="bold")
            plt.xlabel("Stock Symbol", fontweight="bold")
            plt.xticks(rotation=0)
            plt.grid(True, alpha=0.3, axis="y")

            # Add benchmark lines
            plt.axhline(
                y=50,
                color="gold",
                linestyle="--",
                alpha=0.8,
                linewidth=2,
                label="Target: 50%",
            )
            plt.axhline(
                y=30,
                color="orange",
                linestyle="--",
                alpha=0.6,
                linewidth=1,
                label="Minimum: 30%",
            )
            plt.legend(loc="upper right")

            # Add value labels
            for i, v in enumerate(stock_winrate.values):
                plt.text(
                    i, v + 1, f"{v:.1f}%", ha="center", va="bottom", fontweight="bold"
                )

            # 4. Period Performance (Enhanced)
            plt.subplot(4, 3, 4)
            period_pnl = df.groupby("period")["pnl"].sum()
            colors_period = [
                "#2E8B57" if x > 0 else "#DC143C" for x in period_pnl.values
            ]
            bars = period_pnl.plot(
                kind="bar", color=colors_period, edgecolor="black", linewidth=1
            )
            plt.title(
                "⏰ P&L by Trading Period", fontsize=14, fontweight="bold", pad=20
            )
            plt.ylabel("P&L ($)", fontweight="bold")
            plt.xlabel("Trading Period", fontweight="bold")
            plt.xticks(rotation=0)
            plt.grid(True, alpha=0.3, axis="y")

            # Add value labels
            for i, v in enumerate(period_pnl.values):
                plt.text(
                    i,
                    v + (abs(v) * 0.1 if v != 0 else 1),
                    f"${v:.2f}",
                    ha="center",
                    va="bottom" if v >= 0 else "top",
                    fontweight="bold",
                )

            # 5. Cumulative P&L (Enhanced)
            plt.subplot(4, 3, 5)
            df_sorted = df.sort_values("buy_time")
            cumulative_pnl = df_sorted["pnl"].cumsum()

            # Create line plot with gradient fill
            plt.plot(
                range(len(cumulative_pnl)),
                cumulative_pnl,
                linewidth=3,
                color="#1f77b4",
                label="Cumulative P&L",
            )

            # Fill area with different colors for positive/negative regions
            plt.fill_between(
                range(len(cumulative_pnl)),
                cumulative_pnl,
                0,
                where=(cumulative_pnl >= 0),
                color="green",
                alpha=0.3,
                label="Profit Zone",
            )
            plt.fill_between(
                range(len(cumulative_pnl)),
                cumulative_pnl,
                0,
                where=(cumulative_pnl < 0),
                color="red",
                alpha=0.3,
                label="Loss Zone",
            )

            plt.title(
                "📈 Cumulative P&L Progression", fontsize=14, fontweight="bold", pad=20
            )
            plt.xlabel("Trade Number", fontweight="bold")
            plt.ylabel("Cumulative P&L ($)", fontweight="bold")
            plt.grid(True, alpha=0.3)
            plt.legend()

            # Add annotations for key points
            max_point = cumulative_pnl.idxmax()
            min_point = cumulative_pnl.idxmin()
            plt.annotate(
                f"Peak: ${cumulative_pnl.iloc[max_point]:.2f}",
                xy=(max_point, cumulative_pnl.iloc[max_point]),
                xytext=(10, 20),
                textcoords="offset points",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="green", alpha=0.7),
                arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0"),
            )

            plt.annotate(
                f"Trough: ${cumulative_pnl.iloc[min_point]:.2f}",
                xy=(min_point, cumulative_pnl.iloc[min_point]),
                xytext=(10, -20),
                textcoords="offset points",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="red", alpha=0.7),
                arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0"),
            )

            # 6. P&L Distribution (Enhanced)
            plt.subplot(4, 3, 6)
            n, bins, patches = plt.hist(
                df["pnl"], bins=20, alpha=0.8, edgecolor="black", linewidth=1
            )

            # Color bars based on positive/negative
            for i, p in enumerate(patches):
                if bins[i] >= 0:
                    p.set_facecolor("#2E8B57")
                else:
                    p.set_facecolor("#DC143C")

            plt.axvline(
                x=0,
                color="black",
                linestyle="-",
                linewidth=3,
                label="Break-even",
                alpha=0.8,
            )
            plt.axvline(
                x=df["pnl"].mean(),
                color="gold",
                linestyle="--",
                linewidth=2,
                label=f'Mean: ${df["pnl"].mean():.2f}',
            )
            plt.axvline(
                x=df["pnl"].median(),
                color="orange",
                linestyle="--",
                linewidth=2,
                label=f'Median: ${df["pnl"].median():.2f}',
            )

            plt.title("📊 P&L Distribution", fontsize=14, fontweight="bold", pad=20)
            plt.xlabel("P&L per Trade ($)", fontweight="bold")
            plt.ylabel("Frequency", fontweight="bold")
            plt.legend()
            plt.grid(True, alpha=0.3, axis="y")

            # 7. Return Distribution (Enhanced)
            plt.subplot(4, 3, 7)
            n, bins, patches = plt.hist(
                df["return_pct"], bins=20, alpha=0.8, edgecolor="black", linewidth=1
            )

            # Color bars based on positive/negative returns
            for i, p in enumerate(patches):
                if bins[i] >= 0:
                    p.set_facecolor("#4169E1")
                else:
                    p.set_facecolor("#FF4500")

            plt.axvline(x=0, color="black", linestyle="-", linewidth=3, alpha=0.8)
            plt.axvline(
                x=df["return_pct"].mean(),
                color="gold",
                linestyle="--",
                linewidth=2,
                label=f'Mean: {df["return_pct"].mean():.3f}%',
            )
            plt.title("📈 Return Distribution", fontsize=14, fontweight="bold", pad=20)
            plt.xlabel("Return per Trade (%)", fontweight="bold")
            plt.ylabel("Frequency", fontweight="bold")
            plt.legend()
            plt.grid(True, alpha=0.3, axis="y")

            # 8. Trade Duration Analysis (Enhanced)
            plt.subplot(4, 3, 8)
            n, bins, patches = plt.hist(
                df["hold_duration"],
                bins=15,
                alpha=0.8,
                color="#20B2AA",
                edgecolor="black",
                linewidth=1,
            )

            mean_duration = df["hold_duration"].mean()
            plt.axvline(
                x=mean_duration,
                color="red",
                linestyle="-",
                linewidth=3,
                label=f"Mean: {mean_duration:.1f} min",
            )
            plt.axvline(
                x=df["hold_duration"].median(),
                color="orange",
                linestyle="--",
                linewidth=2,
                label=f'Median: {df["hold_duration"].median():.1f} min',
            )

            plt.title(
                "⏱️ Trade Duration Distribution", fontsize=14, fontweight="bold", pad=20
            )
            plt.xlabel("Hold Duration (minutes)", fontweight="bold")
            plt.ylabel("Frequency", fontweight="bold")
            plt.legend()
            plt.grid(True, alpha=0.3, axis="y")

            # 9. Win/Loss by Period (Enhanced)
            plt.subplot(4, 3, 9)
            period_stats = (
                df.groupby(["period", "is_profitable"]).size().unstack(fill_value=0)
            )
            bars = period_stats.plot(
                kind="bar",
                stacked=True,
                color=["#DC143C", "#2E8B57"],
                edgecolor="black",
                linewidth=1,
            )
            plt.title(
                "🎯 Win/Loss Distribution by Period",
                fontsize=14,
                fontweight="bold",
                pad=20,
            )
            plt.ylabel("Trade Count", fontweight="bold")
            plt.xlabel("Trading Period", fontweight="bold")
            plt.xticks(rotation=0)
            plt.legend(["Losses", "Wins"], loc="upper right")
            plt.grid(True, alpha=0.3, axis="y")

            # Add percentage labels on bars
            for container in bars.containers:
                plt.bar_label(
                    container, label_type="center", fontweight="bold", color="white"
                )

            # 10. Risk-Return Scatter (Enhanced)
            plt.subplot(4, 3, 10)
            stock_stats = (
                df.groupby("symbol")
                .agg({"return_pct": ["mean", "std"], "pnl": "sum"})
                .round(3)
            )

            colors_scatter = []
            sizes = []

            for stock in stock_stats.index:
                mean_return = stock_stats.loc[stock, ("return_pct", "mean")]
                std_return = stock_stats.loc[stock, ("return_pct", "std")]
                total_pnl = stock_stats.loc[stock, ("pnl", "sum")]

                color = "#2E8B57" if total_pnl > 0 else "#DC143C"
                size = max(abs(total_pnl) * 15 + 100, 100)  # Minimum size of 100

                plt.scatter(
                    std_return,
                    mean_return,
                    s=size,
                    alpha=0.7,
                    color=color,
                    edgecolors="black",
                    linewidth=2,
                )
                plt.annotate(
                    stock,
                    (std_return, mean_return),
                    xytext=(8, 8),
                    textcoords="offset points",
                    fontweight="bold",
                    fontsize=11,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8),
                )

            plt.axhline(y=0, color="black", linestyle="--", alpha=0.5, linewidth=1)
            plt.axvline(x=0, color="black", linestyle="--", alpha=0.5, linewidth=1)
            plt.title(
                "🎯 Risk-Return Analysis by Stock",
                fontsize=14,
                fontweight="bold",
                pad=20,
            )
            plt.xlabel("Risk (Return Volatility %)", fontweight="bold")
            plt.ylabel("Expected Return (%)", fontweight="bold")
            plt.grid(True, alpha=0.3)

            # Add quadrant labels
            plt.text(
                0.95,
                0.95,
                "High Return\nHigh Risk",
                transform=plt.gca().transAxes,
                ha="right",
                va="top",
                fontsize=9,
                style="italic",
                bbox=dict(boxstyle="round", facecolor="lightgreen", alpha=0.5),
            )
            plt.text(
                0.05,
                0.05,
                "Low Return\nLow Risk",
                transform=plt.gca().transAxes,
                ha="left",
                va="bottom",
                fontsize=9,
                style="italic",
                bbox=dict(boxstyle="round", facecolor="lightcoral", alpha=0.5),
            )

            # 11. Performance Metrics Dashboard (Enhanced)
            plt.subplot(4, 3, 11)
            plt.axis("off")

            # Create a professional metrics dashboard with LARGER text
            metrics_text = f"""
PERFORMANCE DASHBOARD

TRADING METRICS
Total Trades: {metrics['total_trades']}
Win Rate: {metrics['win_rate']:.1f}%
Total P&L: ${metrics['total_pnl']:,.2f}

PROFITABILITY
Avg P&L/Trade: ${metrics['avg_pnl_per_trade']:.2f}
Profit Factor: {metrics['profit_factor']:.2f}
Risk-Reward: {metrics['risk_reward_ratio']:.2f}

RISK METRICS
Sharpe Ratio: {metrics['sharpe_ratio']:.3f}
Max Drawdown: ${metrics['max_drawdown']:.2f}
Max DD %: {metrics['max_drawdown_pct']:.1f}%

STREAKS
Best: {metrics['max_consecutive_wins']} wins
Worst: {metrics['max_consecutive_losses']} losses

WIN/LOSS STATS
Avg Win: ${metrics['avg_win']:.2f}
Avg Loss: ${metrics['avg_loss']:.2f}
            """

            plt.text(
                0.05,
                0.95,
                metrics_text,
                transform=plt.gca().transAxes,
                fontsize=16,
                verticalalignment="top",
                fontfamily="monospace",
                bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.8),
            )

            # 12. Period Win Rates with Volume (Enhanced)
            plt.subplot(4, 3, 12)

            # Create grouped bar chart
            period_data = df.groupby("period").agg(
                {"is_profitable": "mean", "pnl": "count"}
            ) * [
                100,
                1,
            ]  # Convert win rate to percentage

            x = np.arange(len(period_data.index))
            width = 0.35

            bars1 = plt.bar(
                x - width / 2,
                period_data["is_profitable"],
                width,
                label="Win Rate (%)",
                color="#4682B4",
                alpha=0.8,
                edgecolor="black",
            )

            # Secondary y-axis for trade count
            ax2 = plt.gca().twinx()
            bars2 = ax2.bar(
                x + width / 2,
                period_data["pnl"],
                width,
                label="Trade Count",
                color="#FF6347",
                alpha=0.8,
                edgecolor="black",
            )

            plt.gca().set_xlabel("Trading Period", fontweight="bold")
            plt.gca().set_ylabel("Win Rate (%)", fontweight="bold", color="#4682B4")
            ax2.set_ylabel("Trade Count", fontweight="bold", color="#FF6347")
            plt.gca().set_title(
                "📊 Win Rate & Volume by Period", fontsize=14, fontweight="bold", pad=20
            )

            plt.gca().set_xticks(x)
            plt.gca().set_xticklabels(period_data.index)
            plt.gca().axhline(
                y=50, color="gold", linestyle="--", alpha=0.8, linewidth=2
            )

            # Add value labels
            for bar in bars1:
                height = bar.get_height()
                plt.gca().text(
                    bar.get_x() + bar.get_width() / 2.0,
                    height + 1,
                    f"{height:.1f}%",
                    ha="center",
                    va="bottom",
                    fontweight="bold",
                )

            for bar in bars2:
                height = bar.get_height()
                ax2.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    height + 0.5,
                    f"{int(height)}",
                    ha="center",
                    va="bottom",
                    fontweight="bold",
                )

            # Combined legend
            lines1, labels1 = plt.gca().get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            plt.gca().legend(lines1 + lines2, labels1 + labels2, loc="upper right")

            plt.gca().grid(True, alpha=0.3, axis="y")

            # Adjust layout with more spacing
            plt.tight_layout(rect=[0, 0.03, 1, 0.94])

            # Save the comprehensive chart with high quality
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            chart_path = os.path.join(
                output_dir, f"comprehensive_pnl_analysis_{timestamp}.png"
            )
            plt.savefig(
                chart_path,
                dpi=300,
                bbox_inches="tight",
                facecolor="white",
                edgecolor="none",
                format="png",
            )
            plt.close()

            return chart_path

        except Exception as e:
            self.logger.error(f"Error creating visualizations: {e}")
            return None

    def generate_detailed_report(self, trades, metrics, output_dir="reports/daily"):
        """Generate detailed text report"""
        try:
            os.makedirs(output_dir, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = os.path.join(
                output_dir, f"comprehensive_pnl_report_{timestamp}.txt"
            )

            df = pd.DataFrame(trades)

            with open(report_path, "w", encoding="utf-8") as f:
                f.write("=" * 100 + "\n")
                f.write("COMPREHENSIVE P&L ANALYSIS REPORT\n")
                f.write("=" * 100 + "\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Analysis Period: {datetime.now().strftime('%Y-%m-%d')}\n\n")

                # Executive Summary
                f.write("EXECUTIVE SUMMARY\n")
                f.write("-" * 50 + "\n")
                f.write(f"Total Trades Executed:      {metrics['total_trades']}\n")
                f.write(f"Total P&L:                  ${metrics['total_pnl']:+,.2f}\n")
                f.write(f"Win Rate:                   {metrics['win_rate']:.1f}%\n")
                f.write(
                    f"Average P&L per Trade:      ${metrics['avg_pnl_per_trade']:+.2f}\n"
                )
                f.write(
                    f"Total Volume Traded:        ${metrics['total_value_traded']:,.2f}\n"
                )
                f.write(
                    f"Return on Volume:           {(metrics['total_pnl']/metrics['total_value_traded']*100):+.3f}%\n\n"
                )

                # Stock Performance Analysis
                f.write("1. STOCK PROFITABILITY ANALYSIS\n")
                f.write("-" * 50 + "\n")
                stock_analysis = (
                    df.groupby("symbol")
                    .agg(
                        {
                            "pnl": ["sum", "count", "mean"],
                            "is_profitable": ["mean", "sum"],
                            "trade_value": "sum",
                        }
                    )
                    .round(2)
                )

                f.write(
                    f"{'Stock':<8} {'Total P&L':<12} {'Trades':<8} {'Avg P&L':<10} {'Win Rate':<10} {'Volume':<12}\n"
                )
                f.write("-" * 70 + "\n")

                for stock in stock_analysis.index:
                    total_pnl = stock_analysis.loc[stock, ("pnl", "sum")]
                    trade_count = int(stock_analysis.loc[stock, ("pnl", "count")])
                    avg_pnl = stock_analysis.loc[stock, ("pnl", "mean")]
                    win_rate = (
                        stock_analysis.loc[stock, ("is_profitable", "mean")] * 100
                    )
                    volume = stock_analysis.loc[stock, ("trade_value", "sum")]

                    f.write(
                        f"{stock:<8} ${total_pnl:+9.2f} {trade_count:>7} ${avg_pnl:+8.2f} {win_rate:>8.1f}% ${volume:>10,.0f}\n"
                    )

                # Determine most/least profitable
                stock_pnl = (
                    df.groupby("symbol")["pnl"].sum().sort_values(ascending=False)
                )
                f.write(
                    f"\nMost Profitable Stock:  {stock_pnl.index[0]} (${stock_pnl.iloc[0]:+.2f})\n"
                )
                f.write(
                    f"Least Profitable Stock: {stock_pnl.index[-1]} (${stock_pnl.iloc[-1]:+.2f})\n\n"
                )

                # Position Analysis (Long/Short)
                f.write("2. POSITION DIRECTION ANALYSIS\n")
                f.write("-" * 50 + "\n")
                position_analysis = (
                    df.groupby("side")
                    .agg({"pnl": ["sum", "count", "mean"], "is_profitable": "mean"})
                    .round(2)
                )

                for side in position_analysis.index:
                    total_pnl = position_analysis.loc[side, ("pnl", "sum")]
                    trade_count = int(position_analysis.loc[side, ("pnl", "count")])
                    avg_pnl = position_analysis.loc[side, ("pnl", "mean")]
                    win_rate = (
                        position_analysis.loc[side, ("is_profitable", "mean")] * 100
                    )

                    f.write(f"{side.upper()} Positions:\n")
                    f.write(f"  Total P&L:        ${total_pnl:+.2f}\n")
                    f.write(f"  Trade Count:      {trade_count}\n")
                    f.write(f"  Avg P&L:          ${avg_pnl:+.2f}\n")
                    f.write(f"  Win Rate:         {win_rate:.1f}%\n\n")

                # Time Period Analysis
                f.write("3. TIME PERIOD PROFITABILITY\n")
                f.write("-" * 50 + "\n")
                period_analysis = (
                    df.groupby("period")
                    .agg(
                        {
                            "pnl": ["sum", "count", "mean"],
                            "is_profitable": "mean",
                            "trade_value": "sum",
                        }
                    )
                    .round(2)
                )

                f.write(
                    f"{'Period':<10} {'Total P&L':<12} {'Trades':<8} {'Avg P&L':<10} {'Win Rate':<10}\n"
                )
                f.write("-" * 60 + "\n")

                for period in ["Morning", "Midday", "Evening"]:
                    if period in period_analysis.index:
                        total_pnl = period_analysis.loc[period, ("pnl", "sum")]
                        trade_count = int(period_analysis.loc[period, ("pnl", "count")])
                        avg_pnl = period_analysis.loc[period, ("pnl", "mean")]
                        win_rate = (
                            period_analysis.loc[period, ("is_profitable", "mean")] * 100
                        )

                        f.write(
                            f"{period:<10} ${total_pnl:+9.2f} {trade_count:>7} ${avg_pnl:+8.2f} {win_rate:>8.1f}%\n"
                        )

                # Most profitable period
                period_pnl = (
                    df.groupby("period")["pnl"].sum().sort_values(ascending=False)
                )
                if not period_pnl.empty:
                    f.write(
                        f"\nMost Profitable Period: {period_pnl.index[0]} (${period_pnl.iloc[0]:+.2f})\n\n"
                    )

                # Performance Metrics
                f.write("4. RISK & PERFORMANCE METRICS\n")
                f.write("-" * 50 + "\n")
                f.write(f"Win Rate:                   {metrics['win_rate']:.1f}%\n")
                f.write(f"Profit Factor:              {metrics['profit_factor']:.2f}\n")
                f.write(
                    f"Risk-Reward Ratio:          {metrics['risk_reward_ratio']:.2f}\n"
                )
                f.write(
                    f"Expected Value:             ${metrics['expected_value']:+.2f}\n"
                )
                f.write(
                    f"Average P&L per Trade:      ${metrics['avg_pnl_per_trade']:+.2f}\n\n"
                )

                f.write("Risk-Adjusted Returns:\n")
                f.write(
                    f"  Average Return:           {metrics['avg_return_pct']:+.3f}%\n"
                )
                f.write(
                    f"  Return Volatility:        {metrics['std_return_pct']:.3f}%\n"
                )
                f.write(
                    f"  Sharpe Ratio:             {metrics['sharpe_ratio']:+.3f}\n\n"
                )

                f.write("Drawdown Analysis:\n")
                f.write(f"  Maximum Drawdown:         ${metrics['max_drawdown']:.2f}\n")
                f.write(
                    f"  Max Drawdown %:           {metrics['max_drawdown_pct']:.1f}%\n\n"
                )

                f.write("Win/Loss Statistics:\n")
                f.write(f"  Average Win:              ${metrics['avg_win']:.2f}\n")
                f.write(f"  Average Loss:             ${metrics['avg_loss']:.2f}\n")
                f.write(
                    f"  Total Profits:            ${metrics['total_profits']:.2f}\n"
                )
                f.write(f"  Total Losses:             ${metrics['total_losses']:.2f}\n")
                f.write(
                    f"  Max Consecutive Wins:     {metrics['max_consecutive_wins']}\n"
                )
                f.write(
                    f"  Max Consecutive Losses:   {metrics['max_consecutive_losses']}\n\n"
                )

                # Detailed Trade List
                f.write("5. DETAILED TRADE HISTORY\n")
                f.write("-" * 50 + "\n")
                f.write(
                    f"{'#':<4} {'Stock':<6} {'Qty':<5} {'Buy':<8} {'Sell':<8} {'P&L':<8} {'Return':<8} {'Period':<8}\n"
                )
                f.write("-" * 70 + "\n")

                for i, trade in enumerate(trades, 1):
                    f.write(
                        f"{i:<4} {trade['symbol']:<6} {trade['qty']:<5.0f} "
                        f"${trade['buy_price']:<7.2f} ${trade['sell_price']:<7.2f} "
                        f"${trade['pnl']:+7.2f} {trade['return_pct']:+6.2f}% {trade['period']:<8}\n"
                    )

                f.write("\n" + "=" * 100 + "\n")
                f.write("Report generated by Alpaca Trading Bot P&L Analyzer\n")
                f.write("=" * 100 + "\n")

            return report_path

        except Exception as e:
            self.logger.error(f"Error generating detailed report: {e}")
            return None

    def generate_comprehensive_report(self):
        """Generate complete comprehensive P&L report"""
        try:
            print("🔍 Generating Comprehensive P&L Report...")
            print("=" * 60)

            # Get trading data
            print("📊 Retrieving trading data from Alpaca...")
            data = self.get_trading_data()

            if not data:
                print("❌ Unable to retrieve trading data")
                return

            # Process trades
            print("🔄 Processing trades and matching buy/sell orders...")
            trades = self.process_trades(data["orders"])

            if not trades:
                print("❌ No completed trades found")
                return

            print(f"✅ Found {len(trades)} completed trades")

            # Calculate metrics
            print("📈 Calculating performance metrics...")
            metrics = self.calculate_performance_metrics(trades)

            # Create visualizations
            print("📊 Creating charts and visualizations...")
            chart_path = self.create_visualizations(trades, metrics)

            # Generate detailed report
            print("📝 Generating detailed text report...")
            report_path = self.generate_detailed_report(trades, metrics)

            # Print summary to console
            print("\n" + "=" * 60)
            print("📋 EXECUTIVE SUMMARY")
            print("=" * 60)
            print(f"Total Trades:           {metrics['total_trades']}")
            print(f"Total P&L:              ${metrics['total_pnl']:+,.2f}")
            print(f"Win Rate:               {metrics['win_rate']:.1f}%")
            print(f"Avg P&L per Trade:      ${metrics['avg_pnl_per_trade']:+.2f}")
            print(f"Profit Factor:          {metrics['profit_factor']:.2f}")
            print(f"Risk-Reward Ratio:      {metrics['risk_reward_ratio']:.2f}")
            print(f"Sharpe Ratio:           {metrics['sharpe_ratio']:+.3f}")
            print(f"Max Drawdown:           ${metrics['max_drawdown']:.2f}")

            # Stock performance summary
            df = pd.DataFrame(trades)
            stock_pnl = df.groupby("symbol")["pnl"].sum().sort_values(ascending=False)
            print(f"\n📈 Stock Performance:")
            for stock, pnl in stock_pnl.items():
                status = "✅" if pnl > 0 else "❌"
                print(f"  {status} {stock}: ${pnl:+.2f}")

            # Period performance
            period_pnl = df.groupby("period")["pnl"].sum().sort_values(ascending=False)
            print(
                f"\n⏰ Best Trading Period: {period_pnl.index[0]} (${period_pnl.iloc[0]:+.2f})"
            )

            print("\n" + "=" * 60)
            print("📁 FILES GENERATED:")
            if chart_path:
                print(f"📊 Charts: {chart_path}")
            if report_path:
                print(f"📝 Report: {report_path}")
            print("=" * 60)

        except Exception as e:
            self.logger.error(f"Error generating comprehensive report: {e}")
            print(f"❌ Error: {e}")


def main():
    """Main function"""
    try:
        generator = ComprehensivePnLReportGenerator()
        generator.generate_comprehensive_report()

    except Exception as e:
        print(f"❌ Error running comprehensive P&L report generator: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
