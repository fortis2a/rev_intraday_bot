#!/usr/bin/env python3
"""
Interactive Dashboard Options for Trading Analytics
Demonstrates multiple Python frameworks for building interactive dashboards
"""

import sys
import os
from datetime import datetime, timedelta

# Add the parent directory to sys.path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.data_manager import DataManager
from utils.logger import setup_logger


class InteractiveDashboardBuilder:
    """Builder for various types of interactive dashboards"""

    def __init__(self):
        self.logger = setup_logger("InteractiveDashboardBuilder")
        self.data_manager = DataManager()
        self.api = self.data_manager.api

    def display_options(self):
        """Display all available interactive dashboard options"""

        print("🚀 PYTHON INTERACTIVE DASHBOARD OPTIONS FOR TRADING DATA")
        print("=" * 80)
        print()

        print("1️⃣  PLOTLY DASH - MOST POPULAR")
        print("   ✅ Real-time updates")
        print("   ✅ Professional web interface")
        print("   ✅ Click/hover interactions")
        print("   ✅ Multi-page layouts")
        print("   ✅ Mobile responsive")
        print("   📊 Perfect for: Executive dashboards, client presentations")
        print()

        print("2️⃣  STREAMLIT - EASIEST TO BUILD")
        print("   ✅ Extremely simple Python code")
        print("   ✅ Auto-refresh widgets")
        print("   ✅ File upload/download")
        print("   ✅ Built-in authentication")
        print("   📊 Perfect for: Quick prototypes, data exploration")
        print()

        print("3️⃣  FLASK/FASTAPI + PLOTLY.JS - MOST FLEXIBLE")
        print("   ✅ Full control over everything")
        print("   ✅ Custom APIs")
        print("   ✅ Database integration")
        print("   ✅ Advanced authentication")
        print("   📊 Perfect for: Production systems, complex workflows")
        print()

        print("4️⃣  JUPYTER WIDGETS - FOR ANALYSIS")
        print("   ✅ Interactive notebooks")
        print("   ✅ Real-time parameter adjustment")
        print("   ✅ Embedded in Jupyter")
        print("   ✅ Great for research")
        print("   📊 Perfect for: Strategy development, backtesting")
        print()

        print("5️⃣  PANEL/BOKEH - ADVANCED FEATURES")
        print("   ✅ High-performance streaming")
        print("   ✅ Large dataset handling")
        print("   ✅ Custom JavaScript widgets")
        print("   ✅ Server deployment")
        print("   📊 Perfect for: Real-time trading monitoring")
        print()

        print("6️⃣  GRADIO - AI/ML FOCUSED")
        print("   ✅ Machine learning model interfaces")
        print("   ✅ Quick sharing")
        print("   ✅ Public/private hosting")
        print("   ✅ API integration")
        print("   📊 Perfect for: Strategy prediction, model testing")
        print()

        print("RECOMMENDATION FOR YOUR SCALPING BOT:")
        print("🎯 START WITH: Streamlit (easiest)")
        print("🎯 UPGRADE TO: Plotly Dash (most professional)")
        print("🎯 ADVANCED: Flask + Plotly.js (full control)")
        print()

        print("Would you like me to create:")
        print("A) Streamlit interactive dashboard (quickest to build)")
        print("B) Plotly Dash professional dashboard (most features)")
        print("C) Flask web app with real-time updates (most flexible)")
        print("D) All three examples for comparison")


def create_streamlit_example():
    """Create a Streamlit interactive dashboard example"""

    streamlit_code = '''
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Add path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.data_manager import DataManager

# Page config
st.set_page_config(
    page_title="Scalping Bot Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cache data loading
@st.cache_data(ttl=30)  # Refresh every 30 seconds
def load_trading_data():
    """Load fresh trading data"""
    data_manager = DataManager()
    
    # Get recent orders
    orders = data_manager.api.list_orders(
        status='filled',
        limit=200,
        after=(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    )
    
    # Process orders into DataFrame
    data = []
    for order in orders:
        if hasattr(order, 'filled_at') and order.filled_at:
            data.append({
                'symbol': order.symbol,
                'side': order.side,
                'qty': float(order.filled_qty or order.qty),
                'price': float(order.filled_avg_price or 0),
                'filled_at': order.filled_at,
                'date': order.filled_at.date()
            })
    
    return pd.DataFrame(data)

# Main dashboard
def main():
    st.title("🚀 Interactive Scalping Bot Dashboard")
    st.markdown("Real-time trading analytics with live data updates")
    
    # Sidebar controls
    st.sidebar.header("📊 Dashboard Controls")
    
    # Auto-refresh toggle
    auto_refresh = st.sidebar.checkbox("Auto-refresh (30s)", value=True)
    if auto_refresh:
        st.sidebar.info("Dashboard updates every 30 seconds")
    
    # Date filter
    days_back = st.sidebar.slider("Days to analyze", 1, 14, 7)
    
    # Load data
    with st.spinner("Loading trading data..."):
        df = load_trading_data()
    
    if df.empty:
        st.error("No trading data found")
        return
    
    # Filter by date range
    cutoff_date = datetime.now().date() - timedelta(days=days_back)
    df_filtered = df[df['date'] >= cutoff_date]
    
    # Exclude August 12th option
    exclude_aug12 = st.sidebar.checkbox("Exclude Aug 12 (No Risk Mgmt)", value=True)
    if exclude_aug12:
        df_filtered = df_filtered[df_filtered['date'] != pd.to_datetime('2025-08-12').date()]
        st.sidebar.warning("August 12th excluded from analysis")
    
    # Calculate P&L
    stock_pnl = calculate_pnl(df_filtered)
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    total_pnl = sum(stock_pnl.values())
    winners = len([p for p in stock_pnl.values() if p > 0])
    total_stocks = len(stock_pnl)
    win_rate = (winners / total_stocks * 100) if total_stocks > 0 else 0
    
    col1.metric("Total P&L", f"${total_pnl:+,.2f}", delta=f"{total_pnl:+.2f}")
    col2.metric("Win Rate", f"{win_rate:.0f}%", delta=f"{winners}/{total_stocks}")
    col3.metric("Best Stock", max(stock_pnl.items(), key=lambda x: x[1])[0] if stock_pnl else "N/A")
    col4.metric("Total Trades", len(df_filtered))
    
    # Interactive charts
    st.subheader("📊 Interactive Stock Performance")
    
    # Stock performance chart with Plotly
    fig_stocks = px.bar(
        x=list(stock_pnl.keys()),
        y=list(stock_pnl.values()),
        color=list(stock_pnl.values()),
        color_continuous_scale=['red', 'gray', 'green'],
        title="Stock P&L Performance",
        labels={'x': 'Stock Symbol', 'y': 'P&L ($)'}
    )
    fig_stocks.update_layout(height=500, showlegend=False)
    st.plotly_chart(fig_stocks, use_container_width=True)
    
    # Time series chart
    st.subheader("⏰ Trading Timeline")
    
    # Group by hour for timeline
    df_filtered['hour'] = pd.to_datetime(df_filtered['filled_at']).dt.hour
    hourly_trades = df_filtered.groupby('hour').size()
    
    fig_timeline = px.line(
        x=hourly_trades.index,
        y=hourly_trades.values,
        title="Trading Activity by Hour",
        labels={'x': 'Hour of Day', 'y': 'Number of Trades'}
    )
    fig_timeline.update_layout(height=400)
    st.plotly_chart(fig_timeline, use_container_width=True)
    
    # Data table with filtering
    st.subheader("📋 Trade Details")
    
    # Stock selector
    selected_stocks = st.multiselect(
        "Filter by stocks:",
        options=df_filtered['symbol'].unique(),
        default=df_filtered['symbol'].unique()[:5]  # First 5 by default
    )
    
    if selected_stocks:
        filtered_table = df_filtered[df_filtered['symbol'].isin(selected_stocks)]
        st.dataframe(
            filtered_table[['symbol', 'side', 'qty', 'price', 'filled_at']],
            use_container_width=True
        )
        
        # Download button
        csv = filtered_table.to_csv(index=False)
        st.download_button(
            label="📥 Download filtered data as CSV",
            data=csv,
            file_name=f"trading_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    # Real-time status
    st.sidebar.success(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
    
    # Auto-refresh
    if auto_refresh:
        st.rerun()

def calculate_pnl(df):
    """Calculate P&L using FIFO method"""
    stock_pnl = {}
    
    for symbol in df['symbol'].unique():
        symbol_data = df[df['symbol'] == symbol].sort_values('filled_at')
        
        buys = symbol_data[symbol_data['side'] == 'buy']
        sells = symbol_data[symbol_data['side'] == 'sell']
        
        buy_queue = []
        for _, buy in buys.iterrows():
            buy_queue.append({'qty': buy['qty'], 'price': buy['price']})
        
        pnl = 0
        for _, sell in sells.iterrows():
            remaining_qty = sell['qty']
            
            while remaining_qty > 0 and buy_queue:
                buy = buy_queue[0]
                if buy['qty'] <= remaining_qty:
                    pnl += buy['qty'] * (sell['price'] - buy['price'])
                    remaining_qty -= buy['qty']
                    buy_queue.pop(0)
                else:
                    pnl += remaining_qty * (sell['price'] - buy['price'])
                    buy['qty'] -= remaining_qty
                    remaining_qty = 0
        
        stock_pnl[symbol] = pnl
    
    return stock_pnl

if __name__ == "__main__":
    main()
    '''

    return streamlit_code


def create_plotly_dash_example():
    """Create a Plotly Dash interactive dashboard example"""

    dash_code = '''
import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Add path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.data_manager import DataManager

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])
app.title = "Scalping Bot Dashboard"

# Layout
app.layout = html.Div([
    # Header
    html.H1("🚀 Scalping Bot Interactive Dashboard", 
            style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': 30}),
    
    # Controls
    html.Div([
        html.Div([
            html.Label("Days to Analyze:"),
            dcc.Slider(
                id='days-slider',
                min=1, max=14, value=7,
                marks={i: str(i) for i in [1, 3, 7, 14]},
                tooltip={"placement": "bottom", "always_visible": True}
            )
        ], className='four columns'),
        
        html.Div([
            html.Label("Exclude August 12th:"),
            dcc.Checklist(
                id='exclude-aug12',
                options=[{'label': ' No Risk Management Day', 'value': 'exclude'}],
                value=['exclude']
            )
        ], className='four columns'),
        
        html.Div([
            html.Label("Auto Refresh:"),
            dcc.Interval(
                id='interval-component',
                interval=30*1000,  # 30 seconds
                n_intervals=0
            ),
            html.Button('🔄 Refresh Now', id='refresh-button', n_clicks=0)
        ], className='four columns'),
        
    ], className='row', style={'marginBottom': 30}),
    
    # Metrics Cards
    html.Div(id='metrics-cards', className='row', style={'marginBottom': 30}),
    
    # Charts
    html.Div([
        html.Div([
            dcc.Graph(id='stock-performance-chart')
        ], className='six columns'),
        
        html.Div([
            dcc.Graph(id='timeline-chart')
        ], className='six columns'),
    ], className='row'),
    
    html.Div([
        html.Div([
            dcc.Graph(id='pnl-distribution')
        ], className='six columns'),
        
        html.Div([
            dcc.Graph(id='cumulative-pnl')
        ], className='six columns'),
    ], className='row'),
    
    # Data Table
    html.H3("📊 Live Trading Data"),
    html.Div(id='data-table'),
    
    # Status
    html.Div(id='status-bar', style={'textAlign': 'center', 'marginTop': 20})
])

# Callbacks
@app.callback(
    [Output('metrics-cards', 'children'),
     Output('stock-performance-chart', 'figure'),
     Output('timeline-chart', 'figure'),
     Output('pnl-distribution', 'figure'),
     Output('cumulative-pnl', 'figure'),
     Output('data-table', 'children'),
     Output('status-bar', 'children')],
    [Input('days-slider', 'value'),
     Input('exclude-aug12', 'value'),
     Input('interval-component', 'n_intervals'),
     Input('refresh-button', 'n_clicks')]
)
def update_dashboard(days_back, exclude_aug12, n_intervals, refresh_clicks):
    """Update all dashboard components"""
    
    # Load data
    data_manager = DataManager()
    
    try:
        # Get orders
        start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        orders = data_manager.api.list_orders(
            status='filled',
            limit=500,
            after=start_date
        )
        
        # Process to DataFrame
        data = []
        for order in orders:
            if hasattr(order, 'filled_at') and order.filled_at:
                # Exclude Aug 12 if requested
                if 'exclude' in exclude_aug12 and order.filled_at.date().strftime('%Y-%m-%d') == '2025-08-12':
                    continue
                
                data.append({
                    'symbol': order.symbol,
                    'side': order.side,
                    'qty': float(order.filled_qty or order.qty),
                    'price': float(order.filled_avg_price or 0),
                    'filled_at': order.filled_at,
                    'value': float(order.filled_qty or order.qty) * float(order.filled_avg_price or 0)
                })
        
        df = pd.DataFrame(data)
        
        if df.empty:
            # Return empty components
            return create_empty_dashboard()
        
        # Calculate P&L
        stock_pnl = calculate_stock_pnl(df)
        
        # Metrics Cards
        metrics = create_metrics_cards(stock_pnl, df)
        
        # Stock Performance Chart
        stock_chart = create_stock_performance_chart(stock_pnl)
        
        # Timeline Chart
        timeline_chart = create_timeline_chart(df)
        
        # P&L Distribution
        pnl_dist_chart = create_pnl_distribution_chart(stock_pnl)
        
        # Cumulative P&L
        cumulative_chart = create_cumulative_pnl_chart(stock_pnl)
        
        # Data Table
        data_table = create_data_table(df)
        
        # Status
        status = html.Div([
            html.Span(f"✅ Last Updated: {datetime.now().strftime('%H:%M:%S')} | "),
            html.Span(f"📊 {len(df)} trades | "),
            html.Span(f"💰 Total P&L: ${sum(stock_pnl.values()):+,.2f}")
        ], style={'color': '#27ae60', 'fontWeight': 'bold'})
        
        return metrics, stock_chart, timeline_chart, pnl_dist_chart, cumulative_chart, data_table, status
        
    except Exception as e:
        error_msg = html.Div([
            html.H3("❌ Error Loading Data"),
            html.P(f"Error: {str(e)}")
        ], style={'color': 'red', 'textAlign': 'center'})
        
        return error_msg, {}, {}, {}, {}, {}, error_msg

def create_metrics_cards(stock_pnl, df):
    """Create metrics cards"""
    total_pnl = sum(stock_pnl.values())
    winners = len([p for p in stock_pnl.values() if p > 0])
    total_stocks = len(stock_pnl)
    win_rate = (winners / total_stocks * 100) if total_stocks > 0 else 0
    
    best_stock = max(stock_pnl.items(), key=lambda x: x[1]) if stock_pnl else ('N/A', 0)
    
    return html.Div([
        html.Div([
            html.H4(f"${total_pnl:+,.2f}"),
            html.P("Total P&L")
        ], className='three columns', style={'textAlign': 'center', 'backgroundColor': '#ecf0f1', 'padding': 20}),
        
        html.Div([
            html.H4(f"{win_rate:.0f}%"),
            html.P(f"Win Rate ({winners}/{total_stocks})")
        ], className='three columns', style={'textAlign': 'center', 'backgroundColor': '#ecf0f1', 'padding': 20}),
        
        html.Div([
            html.H4(best_stock[0]),
            html.P(f"Best Stock (${best_stock[1]:+.2f})")
        ], className='three columns', style={'textAlign': 'center', 'backgroundColor': '#ecf0f1', 'padding': 20}),
        
        html.Div([
            html.H4(len(df)),
            html.P("Total Trades")
        ], className='three columns', style={'textAlign': 'center', 'backgroundColor': '#ecf0f1', 'padding': 20}),
    ], className='row')

def calculate_stock_pnl(df):
    """Calculate P&L by stock using FIFO"""
    stock_pnl = {}
    
    for symbol in df['symbol'].unique():
        symbol_data = df[df['symbol'] == symbol].sort_values('filled_at')
        
        buys = []
        pnl = 0
        
        for _, row in symbol_data.iterrows():
            if row['side'] == 'buy':
                buys.append({'qty': row['qty'], 'price': row['price']})
            else:  # sell
                remaining_qty = row['qty']
                while remaining_qty > 0 and buys:
                    buy = buys[0]
                    if buy['qty'] <= remaining_qty:
                        pnl += buy['qty'] * (row['price'] - buy['price'])
                        remaining_qty -= buy['qty']
                        buys.pop(0)
                    else:
                        pnl += remaining_qty * (row['price'] - buy['price'])
                        buy['qty'] -= remaining_qty
                        remaining_qty = 0
        
        stock_pnl[symbol] = pnl
    
    return stock_pnl

def create_stock_performance_chart(stock_pnl):
    """Create interactive stock performance chart"""
    if not stock_pnl:
        return {}
    
    symbols = list(stock_pnl.keys())
    pnls = list(stock_pnl.values())
    colors = ['green' if p > 0 else 'red' for p in pnls]
    
    fig = go.Figure(data=[
        go.Bar(
            x=symbols,
            y=pnls,
            marker_color=colors,
            text=[f'${p:+.2f}' for p in pnls],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>P&L: $%{y:+,.2f}<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title="📊 Stock Performance (Click to drill down)",
        xaxis_title="Stock Symbol",
        yaxis_title="P&L ($)",
        height=400,
        hovermode='x'
    )
    
    return fig

def create_timeline_chart(df):
    """Create trading timeline chart"""
    if df.empty:
        return {}
    
    # Group by hour
    df['hour'] = pd.to_datetime(df['filled_at']).dt.hour
    hourly_data = df.groupby(['hour', 'side']).size().unstack(fill_value=0)
    
    fig = go.Figure()
    
    if 'buy' in hourly_data.columns:
        fig.add_trace(go.Scatter(
            x=hourly_data.index,
            y=hourly_data['buy'],
            mode='lines+markers',
            name='Buy Orders',
            line=dict(color='green')
        ))
    
    if 'sell' in hourly_data.columns:
        fig.add_trace(go.Scatter(
            x=hourly_data.index,
            y=hourly_data['sell'],
            mode='lines+markers',
            name='Sell Orders',
            line=dict(color='red')
        ))
    
    fig.update_layout(
        title="⏰ Trading Activity Timeline",
        xaxis_title="Hour of Day",
        yaxis_title="Number of Trades",
        height=400
    )
    
    return fig

def create_pnl_distribution_chart(stock_pnl):
    """Create P&L distribution histogram"""
    if not stock_pnl:
        return {}
    
    pnls = list(stock_pnl.values())
    
    fig = go.Figure(data=[
        go.Histogram(
            x=pnls,
            nbinsx=10,
            marker_color='lightblue',
            marker_line_color='black',
            marker_line_width=1
        )
    ])
    
    fig.update_layout(
        title="📈 P&L Distribution",
        xaxis_title="P&L ($)",
        yaxis_title="Number of Stocks",
        height=400
    )
    
    return fig

def create_cumulative_pnl_chart(stock_pnl):
    """Create cumulative P&L chart"""
    if not stock_pnl:
        return {}
    
    symbols = list(stock_pnl.keys())
    pnls = list(stock_pnl.values())
    cumulative = [sum(pnls[:i+1]) for i in range(len(pnls))]
    
    fig = go.Figure(data=[
        go.Scatter(
            x=list(range(len(symbols))),
            y=cumulative,
            mode='lines+markers',
            line=dict(color='blue', width=3),
            marker=dict(size=8),
            text=symbols,
            hovertemplate='<b>%{text}</b><br>Cumulative P&L: $%{y:+,.2f}<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title="📈 Cumulative P&L Progression",
        xaxis_title="Stock Order",
        yaxis_title="Cumulative P&L ($)",
        height=400
    )
    
    return fig

def create_data_table(df):
    """Create interactive data table"""
    if df.empty:
        return html.Div("No data available")
    
    # Prepare table data
    table_df = df[['symbol', 'side', 'qty', 'price', 'value', 'filled_at']].copy()
    table_df['filled_at'] = table_df['filled_at'].dt.strftime('%H:%M:%S')
    table_df = table_df.round(2)
    
    return dash_table.DataTable(
        data=table_df.to_dict('records'),
        columns=[
            {"name": "Symbol", "id": "symbol"},
            {"name": "Side", "id": "side"},
            {"name": "Qty", "id": "qty", "type": "numeric"},
            {"name": "Price", "id": "price", "type": "numeric", "format": {"specifier": "$,.2f"}},
            {"name": "Value", "id": "value", "type": "numeric", "format": {"specifier": "$,.2f"}},
            {"name": "Time", "id": "filled_at"}
        ],
        style_cell={'textAlign': 'center'},
        style_data_conditional=[
            {
                'if': {'filter_query': '{side} = buy'},
                'backgroundColor': '#d5f4e6',
                'color': 'black',
            },
            {
                'if': {'filter_query': '{side} = sell'},
                'backgroundColor': '#ffeaa7',
                'color': 'black',
            }
        ],
        sort_action="native",
        filter_action="native",
        page_action="native",
        page_current=0,
        page_size=10
    )

def create_empty_dashboard():
    """Return empty dashboard components"""
    empty_msg = html.Div("No data available", style={'textAlign': 'center'})
    return empty_msg, {}, {}, {}, {}, empty_msg, empty_msg

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
    '''

    return dash_code


def main():
    """Main function to display options"""
    builder = InteractiveDashboardBuilder()
    builder.display_options()

    print("\n🎯 RECOMMENDED NEXT STEPS:")
    print("1. Install required packages:")
    print("   pip install streamlit plotly dash")
    print()
    print("2. Choose your preferred framework")
    print("3. I'll create the complete interactive dashboard code")
    print()
    print("Which framework would you like me to implement first?")


if __name__ == "__main__":
    main()
