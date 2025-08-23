#!/usr/bin/env python3
"""
Interactive Streamlit Dashboard for Scalping Bot
Real-time trading analytics with live data updates and interactive controls
"""

import os
import sys
import time
from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Add path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.data_manager import DataManager

# Page config
st.set_page_config(
    page_title="🚀 Scalping Bot Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for ultra-compact single-page layout
st.markdown(
    """
<style>
    /* Main container optimization - ultra compact */
    .main .block-container {
        padding-top: 0.1rem !important;
        padding-bottom: 0.1rem !important;
        max-width: 100%;
    }
    
    /* Header styling - ultra compact */
    .main-header {
        font-size: 1.8rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.2rem !important;
        margin-top: 0 !important;
        padding: 0 !important;
        line-height: 1.2;
    }
    
    /* Remove subtitle spacing */
    .css-10trblm h3 {
        margin-top: 0 !important;
        margin-bottom: 0.3rem !important;
        font-size: 1rem;
        line-height: 1.1;
    }
    
    /* Ultra-compact metric cards */
    .metric-card {
        background-color: #f0f2f6;
        padding: 0.1rem;
        border-radius: 0.3rem;
        text-align: center;
        margin-bottom: 0.1rem;
    }
    
    /* Streamlit metric optimization - ultra minimal */
    div[data-testid="metric-container"] {
        background-color: #f0f2f6;
        border: 1px solid #d4d4d4;
        padding: 0.05rem !important;
        border-radius: 0.2rem;
        margin: 0.02rem 0 !important;
        min-height: 40px !important;
        max-height: 60px !important;
    }
    
    /* Make metric text smaller */
    div[data-testid="metric-container"] label {
        font-size: 0.7rem !important;
        line-height: 1 !important;
    }
    
    div[data-testid="metric-container"] [data-testid="metric-value"] {
        font-size: 1.1rem !important;
        line-height: 1 !important;
        font-weight: bold;
    }
    
    div[data-testid="metric-container"] [data-testid="metric-delta"] {
        font-size: 0.6rem !important;
        line-height: 1 !important;
    }
    
    /* Additional column header optimization */
    .main h1 {
        margin-top: 0.1rem !important;
        margin-bottom: 0.1rem !important;
        padding: 0 !important;
        font-size: 1.3rem !important;
        line-height: 1 !important;
    }
    
    .main h2 {
        margin-top: 0.1rem !important;
        margin-bottom: 0.1rem !important;
        padding: 0 !important;
        font-size: 1rem !important;
        line-height: 1 !important;
    }
    
    /* Metric labels and values - compact */
    div[data-testid="metric-container"] > div {
        gap: 0.1rem !important;
    }
    
    /* Chart container optimization - minimal spacing */
    div[data-testid="stPlotlyChart"] {
        margin-bottom: 0.1rem !important;
        margin-top: 0.1rem !important;
    }
    
    /* Sidebar optimization */
    .css-1d391kg {
        padding-top: 0.3rem;
    }
    
    /* Tab optimization - minimal padding */
    .stTabs > div > div > div {
        padding-top: 0.1rem !important;
    }
    
    /* Section headers - minimal */
    .css-10trblm {
        margin-bottom: 0.2rem !important;
        margin-top: 0.2rem !important;
    }
    
    /* Expander optimization */
    div[data-testid="stExpander"] {
        margin-bottom: 0.2rem !important;
        margin-top: 0.2rem !important;
    }
    
    /* Color coding */
    .positive {
        color: #00ff00;
        font-weight: bold;
    }
    .negative {
        color: #ff4444;
        font-weight: bold;
    }
    
    /* Reduce ALL vertical spacing to absolute minimum */
    .element-container {
        margin-bottom: 0.1rem !important;
        margin-top: 0.1rem !important;
    }
    
    /* Ultra-compact date selectors and filters */
    div[data-testid="stSelectbox"] {
        margin: 0.05rem 0 !important;
    }
    
    div[data-testid="stDateInput"] {
        margin: 0.05rem 0 !important;
    }
    
    /* Make filter sections more compact */
    .stSelectbox label, .stDateInput label {
        font-size: 0.8rem !important;
        margin-bottom: 0.1rem !important;
    }
    
    /* Compact dataframe */
    div[data-testid="stDataFrame"] {
        margin: 0.1rem 0 !important;
    }
    
    /* Ultra-compact columns */
    .css-1kyxreq {
        gap: 0.3rem !important;
    }
    
    /* Remove excess spacing from ALL markdown elements */
    .css-1629p8f h1, .css-1629p8f h2, .css-1629p8f h3, .css-1629p8f h4 {
        margin-bottom: 0.2rem !important;
        margin-top: 0.2rem !important;
        line-height: 1.1 !important;
    }
    
    /* Streamlit default spacing overrides */
    .row-widget {
        margin-bottom: 0.1rem !important;
        margin-top: 0.1rem !important;
    }
    
    /* Remove spacing from dividers */
    .css-1rs6os {
        margin: 0.2rem 0 !important;
    }
    
    /* Main content dataframe text visibility - for Live Trading Data tab */
    .main div[data-testid="stDataFrame"] table {
        color: #1f1f1f !important;
    }
    
    .main div[data-testid="stDataFrame"] table td {
        color: #1f1f1f !important;
        font-weight: 500 !important;
    }
    
    .main div[data-testid="stDataFrame"] table th {
        color: #1f1f1f !important;
        font-weight: bold !important;
    }
    
    /* Specifically target buy/sell text in main content */
    .main table tbody tr td:nth-child(2) {
        color: #1f1f1f !important;
        font-weight: 600 !important;
    }
    
    /* Force all main dataframe text to be dark */
    .main div[data-testid="stDataFrame"] * {
        color: #1f1f1f !important;
    }
    
    /* Compact column spacing */
    div[data-testid="column"] {
        padding: 0.1rem !important;
    }
</style>
""",
    unsafe_allow_html=True,
)


# Cache data loading with TTL
@st.cache_data(ttl=30)  # Refresh every 30 seconds
def load_trading_data():
    """Load fresh trading data from Alpaca"""
    try:
        data_manager = DataManager()

        # Get recent orders
        start_date = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")
        orders = data_manager.api.list_orders(
            status="filled", limit=500, after=start_date
        )

        # Get account info
        account = data_manager.api.get_account()

        # Process orders into DataFrame
        data = []
        for order in orders:
            if hasattr(order, "filled_at") and order.filled_at:
                data.append(
                    {
                        "symbol": order.symbol,
                        "side": order.side,
                        "qty": float(order.filled_qty or order.qty),
                        "price": float(order.filled_avg_price or 0),
                        "filled_at": order.filled_at,
                        "date": order.filled_at.date(),
                        "time": order.filled_at.time(),
                        "value": float(order.filled_qty or order.qty)
                        * float(order.filled_avg_price or 0),
                        "order_id": order.id,
                    }
                )

        df = pd.DataFrame(data)

        # Account metrics
        account_data = {
            "equity": float(account.equity),
            "buying_power": float(account.buying_power),
            "day_trade_count": (
                int(account.day_trade_count)
                if hasattr(account, "day_trade_count")
                else 0
            ),
            "last_equity": float(account.last_equity),
        }

        return df, account_data

    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame(), {}


def calculate_pnl(df):
    """Calculate P&L using FIFO method"""
    if df.empty:
        return {}

    stock_pnl = {}

    for symbol in df["symbol"].unique():
        symbol_data = df[df["symbol"] == symbol].sort_values("filled_at")

        buy_queue = []
        pnl = 0

        for _, row in symbol_data.iterrows():
            if row["side"] == "buy":
                buy_queue.append({"qty": row["qty"], "price": row["price"]})
            else:  # sell
                remaining_qty = row["qty"]

                while remaining_qty > 0 and buy_queue:
                    buy = buy_queue[0]
                    if buy["qty"] <= remaining_qty:
                        pnl += buy["qty"] * (row["price"] - buy["price"])
                        remaining_qty -= buy["qty"]
                        buy_queue.pop(0)
                    else:
                        pnl += remaining_qty * (row["price"] - buy["price"])
                        buy["qty"] -= remaining_qty
                        remaining_qty = 0

        stock_pnl[symbol] = round(pnl, 2)

    return stock_pnl


def create_stock_performance_chart(stock_pnl):
    """Create interactive stock performance chart"""
    if not stock_pnl:
        return go.Figure()

    symbols = list(stock_pnl.keys())
    pnls = list(stock_pnl.values())

    # Color mapping
    colors = ["#00ff00" if p > 0 else "#ff4444" if p < 0 else "#ffa500" for p in pnls]

    fig = go.Figure(
        data=[
            go.Bar(
                x=symbols,
                y=pnls,
                marker_color=colors,
                text=[f"${p:+.2f}" for p in pnls],
                textposition="auto",
                hovertemplate="<b>%{x}</b><br>P&L: <b>$%{y:+,.2f}</b><br>Click for details<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        title="📊 Stock Performance - Interactive P&L",
        xaxis_title="Stock Symbol",
        yaxis_title="Profit/Loss ($)",
        height=300,  # Increased for better readability
        margin=dict(l=30, r=30, t=35, b=30),  # Slightly more space for labels
        hovermode="x unified",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(tickformat="$.2f"),  # Format y-axis to 2 decimal places
    )

    # Add zero line
    fig.add_hline(y=0, line_dash="dash", line_color="gray")

    return fig


def create_timeline_chart(df):
    """Create trading activity timeline"""
    if df.empty:
        return go.Figure()

    # Group by hour and side
    df_copy = df.copy()
    df_copy["hour"] = pd.to_datetime(df_copy["filled_at"]).dt.hour

    hourly_data = (
        df_copy.groupby(["hour", "side"])
        .agg({"qty": "sum", "value": "sum"})
        .reset_index()
    )

    fig = go.Figure()

    # Buy orders
    buy_data = hourly_data[hourly_data["side"] == "buy"]
    if not buy_data.empty:
        fig.add_trace(
            go.Scatter(
                x=buy_data["hour"],
                y=buy_data["qty"],
                mode="lines+markers",
                name="📈 Buy Orders",
                line=dict(color="green", width=3),
                marker=dict(size=8),
                hovertemplate="Hour: %{x}<br>Buy Qty: %{y}<br>Value: $%{customdata:,.0f}<extra></extra>",
                customdata=buy_data["value"],
            )
        )

    # Sell orders
    sell_data = hourly_data[hourly_data["side"] == "sell"]
    if not sell_data.empty:
        fig.add_trace(
            go.Scatter(
                x=sell_data["hour"],
                y=sell_data["qty"],
                mode="lines+markers",
                name="📉 Sell Orders",
                line=dict(color="red", width=3),
                marker=dict(size=8),
                hovertemplate="Hour: %{x}<br>Sell Qty: %{y}<br>Value: $%{customdata:,.0f}<extra></extra>",
                customdata=sell_data["value"],
            )
        )

    fig.update_layout(
        title="⏰ Trading Activity Timeline - Hourly Breakdown",
        xaxis_title="Hour of Day",
        yaxis_title="Total Quantity",
        height=160,  # Ultra-compact for single-page view
        margin=dict(l=25, r=25, t=30, b=25),  # Minimal margins
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )

    return fig


def create_pnl_distribution(stock_pnl):
    """Create P&L distribution chart"""
    if not stock_pnl:
        return go.Figure()

    pnls = list(stock_pnl.values())

    fig = go.Figure(
        data=[
            go.Histogram(
                x=pnls,
                nbinsx=15,
                marker_color="lightblue",
                marker_line_color="black",
                marker_line_width=1,
                hovertemplate="P&L Range: $%{x:.2f}<br>Count: %{y}<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        title="📈 P&L Distribution - Stock Performance Spread",
        xaxis_title="P&L ($)",
        yaxis_title="Number of Stocks",
        height=160,  # Ultra-compact for single-page view
        margin=dict(l=25, r=25, t=30, b=25),  # Minimal margins
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(tickformat="$.2f"),  # Format x-axis to 2 decimal places
    )

    # Add mean line
    mean_pnl = sum(pnls) / len(pnls) if pnls else 0
    fig.add_vline(
        x=mean_pnl,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Mean: ${mean_pnl:+.2f}",
    )

    return fig


def create_cumulative_pnl_chart(stock_pnl):
    """Create cumulative P&L progression"""
    if not stock_pnl:
        return go.Figure()

    # Sort by P&L for better visualization
    sorted_items = sorted(stock_pnl.items(), key=lambda x: x[1])
    symbols = [item[0] for item in sorted_items]
    pnls = [item[1] for item in sorted_items]

    # Calculate cumulative
    cumulative = []
    running_total = 0
    for pnl in pnls:
        running_total += pnl
        cumulative.append(round(running_total, 2))

    # Color points based on individual P&L
    colors = ["green" if p > 0 else "red" for p in pnls]

    fig = go.Figure(
        data=[
            go.Scatter(
                x=list(range(len(symbols))),
                y=cumulative,
                mode="lines+markers",
                line=dict(color="blue", width=4),
                marker=dict(size=10, color=colors, line=dict(width=2, color="black")),
                text=symbols,
                hovertemplate="<b>%{text}</b><br>Individual P&L: $%{customdata:+.2f}<br>Cumulative: <b>$%{y:+,.2f}</b><extra></extra>",
                customdata=pnls,
            )
        ]
    )

    # Fill area
    fig.add_trace(
        go.Scatter(
            x=list(range(len(symbols))),
            y=cumulative,
            fill="tozeroy",
            mode="none",
            fillcolor=(
                "rgba(0,100,80,0.2)" if cumulative[-1] > 0 else "rgba(255,0,0,0.2)"
            ),
            showlegend=False,
            hoverinfo="skip",
        )
    )

    fig.update_layout(
        title="📈 Cumulative P&L Progression - Trading Journey",
        xaxis_title="Stock Sequence (Sorted by Performance)",
        yaxis_title="Cumulative P&L ($)",
        height=300,  # Match Stock Performance chart height
        margin=dict(l=25, r=25, t=30, b=25),  # Minimal margins
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(tickformat="$.2f"),  # Format y-axis to 2 decimal places
    )

    # Add zero line
    fig.add_hline(y=0, line_dash="dash", line_color="gray")

    return fig


def main():
    """Main Streamlit app"""

    # Ultra-compact header
    st.markdown(
        '<h1 class="main-header">🚀 Interactive Scalping Bot Dashboard</h1>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p style="text-align: center; font-size: 0.8rem; margin: 0; padding: 0; color: #666; line-height: 1;">Real-time trading analytics with live Alpaca data</p>',
        unsafe_allow_html=True,
    )

    # Enhanced Sidebar Controls
    st.sidebar.header("🎛️ Dashboard Controls")

    # Auto-refresh toggle
    auto_refresh = st.sidebar.checkbox("🔄 Auto-refresh (30s)", value=True)
    if auto_refresh:
        st.sidebar.success("Auto-refresh enabled")

    # Manual refresh button
    if st.sidebar.button("🔄 Refresh Now", type="primary"):
        st.cache_data.clear()
        st.rerun()

    st.sidebar.markdown("---")

    # Enhanced Date Filtering with Calendar
    st.sidebar.subheader("📅 Date Range Selection")

    # Get today's date first
    today = datetime.now().date()

    # Get available date range from data
    temp_df, _ = load_trading_data()
    if not temp_df.empty:
        data_min_date = temp_df["date"].min()
        data_max_date = temp_df["date"].max()

        # Ensure we include today even if no trading data exists for today
        min_date = data_min_date
        max_date = max(data_max_date, today)  # Always include today

        # Ensure date range is valid
        if min_date > max_date:
            min_date, max_date = max_date, min_date

    else:
        # Fallback dates if no data
        min_date = today - timedelta(days=30)
        max_date = today

    # Initialize session state for date filtering
    if "date_preset" not in st.session_state:
        st.session_state.date_preset = "last7d"

    # Quick date presets (simplified approach)
    st.sidebar.markdown("**🚀 Quick Presets:**")
    preset_col1, preset_col2 = st.sidebar.columns(2)

    with preset_col1:
        if st.button("📅 Today", key="today"):
            st.session_state.date_preset = "today"

        if st.button("📅 Last 3d", key="last3d"):
            st.session_state.date_preset = "last3d"

    with preset_col2:
        if st.button("📅 Last 7d", key="last7d"):
            st.session_state.date_preset = "last7d"

        if st.button("📅 All Data", key="all_data"):
            st.session_state.date_preset = "all_data"

    # Calculate default dates based on preset
    if st.session_state.date_preset == "today":
        default_start = today  # Use actual today, not max_date
        default_end = today  # Use actual today, not max_date
    elif st.session_state.date_preset == "last3d":
        default_start = max(min_date, today - timedelta(days=2))
        default_end = today
    elif st.session_state.date_preset == "last7d":
        default_start = max(min_date, today - timedelta(days=6))
        default_end = today
    elif st.session_state.date_preset == "all_data":
        default_start = min_date
        default_end = max_date
    else:
        # Default to last 7 days ending today
        default_start = max(min_date, today - timedelta(days=6))
        default_end = today

    # Date range selector
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input(
            "📅 From:",
            value=default_start,
            min_value=min_date,
            max_value=max_date,
            key="start_date",
        )
    with col2:
        end_date = st.date_input(
            "📅 To:",
            value=default_end,
            min_value=min_date,
            max_value=max_date,
            key="end_date",
        )

    # Show selected date range info
    days_selected = (end_date - start_date).days + 1
    st.sidebar.info(
        f"📊 Selected: {days_selected} day{'s' if days_selected != 1 else ''}"
    )

    st.sidebar.markdown("---")

    # Risk Management Filters
    st.sidebar.subheader("⚠️ Risk Management Filters")
    exclude_aug12 = st.sidebar.checkbox("❌ Exclude Aug 12 (No Risk Mgmt)", value=True)
    if exclude_aug12:
        st.sidebar.warning("August 12th excluded from analysis")

    # Additional filters
    min_trade_value = st.sidebar.number_input(
        "💰 Min Trade Value ($):",
        min_value=0.0,
        value=0.0,
        step=10.0,
        help="Filter out trades below this value",
    )

    st.sidebar.markdown("---")

    # Stock Selection Filters
    st.sidebar.subheader("🎯 Stock Filters")

    # Get unique symbols for filtering
    if not temp_df.empty:
        all_symbols = sorted(temp_df["symbol"].unique())
        selected_symbols = st.sidebar.multiselect(
            "📈 Select Stocks:",
            options=all_symbols,
            default=all_symbols,
            help="Leave empty to show all stocks",
        )
    else:
        selected_symbols = []

    st.sidebar.markdown("---")

    # Display Options
    st.sidebar.subheader("🎨 Display Options")
    show_volume = st.sidebar.checkbox("📊 Show Volume Data", value=True)
    show_time_analysis = st.sidebar.checkbox("⏰ Show Time Analysis", value=True)
    chart_height = st.sidebar.slider(
        "📏 Chart Height (px):",
        140,
        220,
        160,
        step=20,
        help="Ultra-compact for single-page view",
    )

    # Load data
    with st.spinner("🔄 Loading fresh trading data..."):
        df, account_data = load_trading_data()

    if df.empty:
        st.error("❌ No trading data found")
        st.stop()

    # Apply enhanced filters
    df_filtered = df.copy()

    # Date range filtering
    df_filtered = df_filtered[
        (df_filtered["date"] >= start_date) & (df_filtered["date"] <= end_date)
    ]

    # August 12th exclusion
    if exclude_aug12:
        df_filtered = df_filtered[
            df_filtered["date"] != pd.to_datetime("2025-08-12").date()
        ]

    # Stock symbol filtering
    if selected_symbols:
        df_filtered = df_filtered[df_filtered["symbol"].isin(selected_symbols)]

    # Trade value filtering
    if min_trade_value > 0:
        df_filtered = df_filtered[df_filtered["value"] >= min_trade_value]

    # Compact filtering summary - minimal space
    if not df_filtered.empty:
        # Use a single line instead of expander to save space
        st.markdown(
            f"<small>📊 **Data:** {len(df_filtered)} trades | {(end_date - start_date).days + 1} days | {len(df_filtered['symbol'].unique())} symbols</small>",
            unsafe_allow_html=True,
        )

    # Calculate P&L
    stock_pnl = calculate_pnl(df_filtered)

    # Account metrics row
    if account_data:
        daily_pnl = account_data["equity"] - account_data["last_equity"]

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                label="💰 Account Equity",
                value=f"${account_data['equity']:,.2f}",
                delta=f"{daily_pnl:+.2f} today",
            )

        with col2:
            st.metric(
                label="💵 Buying Power", value=f"${account_data['buying_power']:,.2f}"
            )

        with col3:
            st.metric(label="📊 Day Trades", value=account_data["day_trade_count"])

        with col4:
            st.metric(label="🎯 Active Orders", value=len(df_filtered))

    # Trading metrics row
    if stock_pnl:
        total_pnl = sum(stock_pnl.values())
        winners = len([p for p in stock_pnl.values() if p > 0])
        total_stocks = len(stock_pnl)
        win_rate = (winners / total_stocks * 100) if total_stocks > 0 else 0

        best_stock = max(stock_pnl.items(), key=lambda x: x[1])
        worst_stock = min(stock_pnl.items(), key=lambda x: x[1])

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                label="💹 Calculated P&L",
                value=f"${total_pnl:+,.2f}",
                delta=f"{total_pnl:+.2f}" if total_pnl != 0 else None,
            )

        with col2:
            st.metric(
                label="🏆 Win Rate",
                value=f"{win_rate:.0f}%",
                delta=f"{winners}/{total_stocks} winners",
            )

        with col3:
            st.metric(
                label="🥇 Best Stock",
                value=best_stock[0],
                delta=f"+${best_stock[1]:.2f}",
            )

        with col4:
            st.metric(
                label="🔻 Worst Stock",
                value=worst_stock[0],
                delta=f"{worst_stock[1]:+.2f}",
            )

    # Charts section - Optimized 2x2 Grid Layout (All charts on one page)
    st.markdown(
        '<h4 style="margin: 0.2rem 0; padding: 0;">📊 Interactive Analytics</h4>',
        unsafe_allow_html=True,
    )

    # First row - Stock Performance and Cumulative P&L
    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(
            create_stock_performance_chart(stock_pnl),
            use_container_width=True,
            key="stock_performance",
        )

    with col2:
        st.plotly_chart(
            create_cumulative_pnl_chart(stock_pnl),
            use_container_width=True,
            key="cumulative",
        )

    # Second row - Timeline and P&L Distribution
    col3, col4 = st.columns(2)

    with col3:
        st.plotly_chart(
            create_timeline_chart(df_filtered), use_container_width=True, key="timeline"
        )

    with col4:
        st.plotly_chart(
            create_pnl_distribution(stock_pnl),
            use_container_width=True,
            key="distribution",
        )

    # Separate section for detailed data table
    st.markdown("---")

    # Create tabs for different views
    tab1, tab2 = st.tabs(["📊 **Analytics Dashboard**", "📋 **Live Trading Data**"])

    with tab1:
        st.info(
            "🎯 **All analytics are displayed above** - Use sidebar filters to customize your view"
        )

        # Quick summary metrics in compact format
        if stock_pnl:
            total_pnl = sum(stock_pnl.values())
            winners = len([p for p in stock_pnl.values() if p > 0])
            total_stocks = len(stock_pnl)
            win_rate = (winners / total_stocks * 100) if total_stocks > 0 else 0

            # Compact summary row
            sum_col1, sum_col2, sum_col3, sum_col4 = st.columns(4)

            with sum_col1:
                st.metric("💰 Total P&L", f"${total_pnl:+,.2f}")
            with sum_col2:
                st.metric("🎯 Win Rate", f"{win_rate:.1f}%")
            with sum_col3:
                st.metric("� Winners", f"{winners}/{total_stocks}")
            with sum_col4:
                avg_pnl = total_pnl / total_stocks if total_stocks > 0 else 0
                st.metric("📊 Avg P&L", f"${avg_pnl:+.2f}")

    with tab2:
        st.subheader("📋 Live Trading Data")

        # Stock selector
        all_symbols = df_filtered["symbol"].unique()
        selected_stocks = st.multiselect(
            "🎯 Filter by stocks:",
            options=all_symbols,
            default=all_symbols[:5] if len(all_symbols) > 5 else all_symbols,
        )

        if selected_stocks:
            # Filter table data
            table_data = df_filtered[df_filtered["symbol"].isin(selected_stocks)].copy()
            table_data = table_data.sort_values("filled_at", ascending=False)

            # Format for display
            display_data = table_data[
                ["symbol", "side", "qty", "price", "value", "filled_at"]
            ].copy()
            display_data["filled_at"] = display_data["filled_at"].dt.strftime(
                "%m/%d %H:%M:%S"
            )
            display_data = display_data.round(2)

            # Color code the dataframe
            def color_side(val):
                if val == "buy":
                    return "background-color: #d4edda"  # Light green
                elif val == "sell":
                    return "background-color: #f8d7da"  # Light red
                return ""

            styled_df = display_data.style.map(color_side, subset=["side"])

            st.dataframe(
                styled_df, use_container_width=True, height=400
            )  # Full height for data page

            # Download button
            csv = table_data.to_csv(index=False)
            st.download_button(
                label="📥 Download filtered data as CSV",
                data=csv,
                file_name=f"scalping_bot_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
            )
        else:
            st.info("👆 Please select stocks to view trading data")

    # Status bar
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.success(f"✅ Last updated: {datetime.now().strftime('%H:%M:%S')}")

    with col2:
        st.info(f"📊 Showing {len(df_filtered)} trades")

    with col3:
        if exclude_aug12:
            st.warning("⚠️ Aug 12 data excluded")
        else:
            st.info("📅 All dates included")

    # Auto-refresh mechanism
    if auto_refresh:
        time.sleep(30)
        st.rerun()


if __name__ == "__main__":
    main()
