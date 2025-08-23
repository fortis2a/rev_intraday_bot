#!/usr/bin/env python3
"""
EOD Analysis Demo - Shows comprehensive analysis with sample data
Demonstrates all charts and reports that would be generated with real trades
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from pathlib import Path
import warnings

warnings.filterwarnings("ignore")

# Set professional chart style
plt.style.use("seaborn-v0_8")
sns.set_palette("husl")


def create_sample_data():
    """Create sample trading data for demonstration"""
    np.random.seed(42)  # For reproducible results

    # Create sample trades
    symbols = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA", "META", "AMZN"]
    directions = ["LONG", "SHORT"]

    trades = []
    for i in range(50):  # 50 sample trades
        symbol = np.random.choice(symbols)
        direction = np.random.choice(directions)

        # Generate realistic trade times during market hours
        base_time = datetime.now().replace(hour=9, minute=30, second=0, microsecond=0)
        random_minutes = np.random.randint(0, 390)  # 6.5 hours * 60 minutes
        entry_time = base_time + timedelta(minutes=random_minutes)

        # Hold time between 5 minutes to 2 hours
        hold_minutes = np.random.exponential(30)  # Exponential distribution
        hold_minutes = max(5, min(120, hold_minutes))  # Clamp between 5-120 minutes

        exit_time = entry_time + timedelta(minutes=hold_minutes)

        # Generate realistic price movement
        entry_price = np.random.uniform(50, 500)  # Random entry price

        # P&L with some skill bias (60% win rate)
        if np.random.random() < 0.6:  # 60% winners
            pnl_pct = np.random.lognormal(0, 0.5) * 0.01  # Small positive gains
        else:  # 40% losers
            pnl_pct = (
                -np.random.lognormal(0, 0.7) * 0.01
            )  # Larger losses (risk management)

        quantity = np.random.randint(10, 200)
        pnl = entry_price * quantity * pnl_pct
        exit_price = entry_price * (1 + pnl_pct)

        trade = {
            "symbol": symbol,
            "direction": direction,
            "entry_time": entry_time,
            "exit_time": exit_time,
            "entry_price": entry_price,
            "exit_price": exit_price,
            "quantity": quantity,
            "pnl": pnl,
            "pnl_pct": pnl_pct * 100,
            "hold_time_minutes": hold_minutes,
            "entry_hour": entry_time.hour,
            "exit_hour": exit_time.hour,
        }
        trades.append(trade)

    return pd.DataFrame(trades)


def create_demo_charts(df):
    """Create all demo charts with sample data"""
    report_dir = Path("demo_reports") / datetime.now().strftime("%Y-%m-%d")
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "charts").mkdir(exist_ok=True)

    print(f"[DEMO] Creating demo charts in: {report_dir}")

    # 1. P&L by Stock Chart
    stock_pnl = df.groupby("symbol")["pnl"].sum().sort_values(ascending=True)

    fig, ax = plt.subplots(figsize=(12, 8))
    colors = ["red" if x < 0 else "green" for x in stock_pnl.values]
    bars = ax.barh(stock_pnl.index, stock_pnl.values, color=colors, alpha=0.7)

    ax.set_title("P&L by Stock - Demo Data", fontsize=16, fontweight="bold")
    ax.set_xlabel("Profit/Loss ($)", fontsize=12)
    ax.grid(True, alpha=0.3)

    # Add value labels
    for bar, value in zip(bars, stock_pnl.values):
        ax.text(
            value + (0.01 * max(abs(stock_pnl.min()), abs(stock_pnl.max()))),
            bar.get_y() + bar.get_height() / 2,
            f"${value:.0f}",
            va="center",
            ha="left" if value >= 0 else "right",
        )

    plt.tight_layout()
    plt.savefig(
        report_dir / "charts" / "demo_pnl_by_stock.png", dpi=300, bbox_inches="tight"
    )
    plt.close()

    # 2. Hourly Trading Activity
    hourly_trades = (
        df.groupby("entry_hour").agg({"pnl": ["count", "sum", "mean"]}).round(2)
    )
    hourly_trades.columns = ["Trade_Count", "Total_PnL", "Avg_PnL"]
    hourly_trades = hourly_trades.reset_index()

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

    # Trade count by hour
    ax1.bar(
        hourly_trades["entry_hour"],
        hourly_trades["Trade_Count"],
        color="steelblue",
        alpha=0.7,
    )
    ax1.set_title(
        "Trading Activity by Hour - Demo Data", fontsize=14, fontweight="bold"
    )
    ax1.set_xlabel("Hour of Day")
    ax1.set_ylabel("Number of Trades")
    ax1.grid(True, alpha=0.3)

    # P&L by hour
    colors = ["red" if x < 0 else "green" for x in hourly_trades["Total_PnL"]]
    ax2.bar(
        hourly_trades["entry_hour"], hourly_trades["Total_PnL"], color=colors, alpha=0.7
    )
    ax2.set_title("P&L by Hour - Demo Data", fontsize=14, fontweight="bold")
    ax2.set_xlabel("Hour of Day")
    ax2.set_ylabel("Total P&L ($)")
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(
        report_dir / "charts" / "demo_hourly_activity.png", dpi=300, bbox_inches="tight"
    )
    plt.close()

    # 3. Win/Loss Distribution
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # Histogram of P&L
    ax1.hist(df["pnl"], bins=20, alpha=0.7, color="steelblue", edgecolor="black")
    ax1.axvline(x=0, color="red", linestyle="--", alpha=0.8)
    ax1.set_title("P&L Distribution - Demo Data", fontsize=14, fontweight="bold")
    ax1.set_xlabel("Profit/Loss ($)")
    ax1.set_ylabel("Frequency")
    ax1.grid(True, alpha=0.3)

    # Win/Loss pie chart
    winners = len(df[df["pnl"] > 0])
    losers = len(df[df["pnl"] < 0])
    breakeven = len(df[df["pnl"] == 0])

    sizes = [winners, losers, breakeven]
    labels = [f"Winners ({winners})", f"Losers ({losers})", f"Breakeven ({breakeven})"]
    colors = ["green", "red", "gray"]

    # Remove zero values
    non_zero = [
        (size, label, color)
        for size, label, color in zip(sizes, labels, colors)
        if size > 0
    ]
    if non_zero:
        sizes, labels, colors = zip(*non_zero)
        ax2.pie(sizes, labels=labels, colors=colors, autopct="%1.1f%%", startangle=90)

    ax2.set_title("Win/Loss Distribution - Demo Data", fontsize=14, fontweight="bold")

    plt.tight_layout()
    plt.savefig(
        report_dir / "charts" / "demo_win_loss_distribution.png",
        dpi=300,
        bbox_inches="tight",
    )
    plt.close()

    # 4. Interactive Dashboard
    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=(
            "P&L by Stock",
            "Hourly P&L",
            "Trade Timeline",
            "Long vs Short Performance",
        ),
        specs=[
            [{"type": "bar"}, {"type": "bar"}],
            [{"type": "scatter"}, {"type": "bar"}],
        ],
    )

    # P&L by Stock
    fig.add_trace(
        go.Bar(
            x=stock_pnl.values,
            y=stock_pnl.index,
            orientation="h",
            name="P&L by Stock",
            marker_color=["red" if x < 0 else "green" for x in stock_pnl.values],
        ),
        row=1,
        col=1,
    )

    # Hourly P&L
    hourly_pnl = df.groupby("entry_hour")["pnl"].sum()
    fig.add_trace(
        go.Bar(
            x=hourly_pnl.index,
            y=hourly_pnl.values,
            name="Hourly P&L",
            marker_color=["red" if x < 0 else "green" for x in hourly_pnl.values],
        ),
        row=1,
        col=2,
    )

    # Trade Timeline
    fig.add_trace(
        go.Scatter(
            x=df["entry_time"],
            y=df["pnl"],
            mode="markers",
            name="Trade P&L",
            marker=dict(
                color=df["pnl"],
                colorscale="RdYlGn",
                size=10,
                colorbar=dict(title="P&L ($)"),
            ),
        ),
        row=2,
        col=1,
    )

    # Long vs Short Performance
    direction_pnl = df.groupby("direction")["pnl"].sum()
    fig.add_trace(
        go.Bar(
            x=direction_pnl.index,
            y=direction_pnl.values,
            name="Direction P&L",
            marker_color=["green" if x > 0 else "red" for x in direction_pnl.values],
        ),
        row=2,
        col=2,
    )

    fig.update_layout(
        title_text="EOD Trading Dashboard - DEMO DATA", showlegend=False, height=800
    )

    dashboard_path = report_dir / "demo_dashboard.html"
    fig.write_html(dashboard_path)

    return report_dir, len(df)


def generate_demo_stats(df):
    """Generate demo statistics"""
    stats = {}

    # Basic stats
    stats["total_trades"] = len(df)
    stats["symbols_traded"] = df["symbol"].nunique()
    stats["total_pnl"] = df["pnl"].sum()

    # Win/Loss Analysis
    winners = df[df["pnl"] > 0]
    losers = df[df["pnl"] < 0]

    stats["winners"] = len(winners)
    stats["losers"] = len(losers)
    stats["win_rate"] = (len(winners) / len(df)) * 100

    stats["avg_win"] = winners["pnl"].mean() if len(winners) > 0 else 0
    stats["avg_loss"] = losers["pnl"].mean() if len(losers) > 0 else 0
    stats["largest_win"] = winners["pnl"].max() if len(winners) > 0 else 0
    stats["largest_loss"] = losers["pnl"].min() if len(losers) > 0 else 0

    # Profit Factor
    gross_profit = winners["pnl"].sum() if len(winners) > 0 else 0
    gross_loss = abs(losers["pnl"].sum()) if len(losers) > 0 else 0
    stats["profit_factor"] = (
        gross_profit / gross_loss
        if gross_loss > 0
        else float("inf") if gross_profit > 0 else 0
    )

    # Time Analysis
    stats["avg_hold_time"] = df["hold_time_minutes"].mean()

    # Direction Analysis
    long_trades = df[df["direction"] == "LONG"]
    short_trades = df[df["direction"] == "SHORT"]

    stats["long_trades"] = len(long_trades)
    stats["short_trades"] = len(short_trades)
    stats["long_pnl"] = long_trades["pnl"].sum() if len(long_trades) > 0 else 0
    stats["short_pnl"] = short_trades["pnl"].sum() if len(short_trades) > 0 else 0

    return stats


def main():
    """Run the demo"""
    print("=" * 80)
    print("                   EOD ANALYSIS DEMO")
    print("=" * 80)
    print("[DEMO] Creating sample trading data...")

    # Create sample data
    df = create_sample_data()
    print(f"[DEMO] Generated {len(df)} sample trades")

    # Generate statistics
    stats = generate_demo_stats(df)

    # Create charts
    print("[DEMO] Creating comprehensive charts and dashboard...")
    report_dir, trade_count = create_demo_charts(df)

    # Display results
    print("\n" + "=" * 80)
    print("                   DEMO RESULTS SUMMARY")
    print("=" * 80)
    print(f"📊 Total Trades: {stats['total_trades']}")
    print(f"💰 Total P&L: ${stats['total_pnl']:.2f}")
    print(f"🎯 Win Rate: {stats['win_rate']:.1f}%")
    print(f"📈 Profit Factor: {stats['profit_factor']:.2f}")
    print(f"🔢 Symbols Traded: {stats['symbols_traded']}")
    print(f"⏱️  Avg Hold Time: {stats['avg_hold_time']:.1f} minutes")
    print()
    print(f"🟢 Winners: {stats['winners']} (Avg: ${stats['avg_win']:.2f})")
    print(f"🔴 Losers: {stats['losers']} (Avg: ${stats['avg_loss']:.2f})")
    print()
    print(f"📈 Long Trades: {stats['long_trades']} (P&L: ${stats['long_pnl']:.2f})")
    print(f"📉 Short Trades: {stats['short_trades']} (P&L: ${stats['short_pnl']:.2f})")
    print()
    print("=" * 80)
    print("                   DEMO FILES CREATED")
    print("=" * 80)
    print(f"📁 Report Directory: {report_dir}")
    print("📊 Charts Created:")
    print("   • demo_pnl_by_stock.png")
    print("   • demo_hourly_activity.png")
    print("   • demo_win_loss_distribution.png")
    print("🌐 Interactive Dashboard: demo_dashboard.html")
    print()
    print("[INFO] This demonstrates the full EOD analysis capabilities")
    print("[INFO] With real trading data, you'll get the same comprehensive analysis")
    print("=" * 80)

    # Try to open dashboard
    try:
        import webbrowser

        dashboard_path = report_dir / "demo_dashboard.html"
        open_demo = input("\nOpen demo dashboard? (Y/n): ").strip().lower()
        if open_demo != "n":
            webbrowser.open(f"file://{dashboard_path.absolute()}")
            print(f"🌐 Demo dashboard opened: {dashboard_path}")
    except Exception as e:
        print(f"[INFO] Dashboard available at: {report_dir / 'demo_dashboard.html'}")


if __name__ == "__main__":
    main()
