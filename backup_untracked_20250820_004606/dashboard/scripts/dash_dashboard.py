#!/usr/bin/env python3
"""
Interactive Plotly Dash Dashboard for Scalping Bot
Professional web-based dashboard with real-time updates
"""

import dash
from dash import dcc, html, Input, Output, dash_table, callback
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
app = dash.Dash(__name__, external_stylesheets=[
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap'
])
app.title = "🚀 Scalping Bot Dashboard"

# Custom CSS
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                font-family: 'Inter', sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                margin: 0;
                min-height: 100vh;
            }
            .main-container {
                background: white;
                margin: 20px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                padding: 20px;
            }
            .header {
                text-align: center;
                color: #2c3e50;
                margin-bottom: 30px;
            }
            .metric-card {
                background: linear-gradient(45deg, #f39c12, #e67e22);
                color: white;
                padding: 20px;
                border-radius: 10px;
                text-align: center;
                margin: 10px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }
            .chart-container {
                background: #f8f9fa;
                border-radius: 10px;
                padding: 15px;
                margin: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Global data manager
data_manager = DataManager()

def load_data():
    """Load trading data"""
    try:
        # Get recent orders
        start_date = (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d')
        orders = data_manager.api.list_orders(
            status='filled',
            limit=500,
            after=start_date
        )
        
        # Get account info
        account = data_manager.api.get_account()
        
        # Process orders
        data = []
        for order in orders:
            if hasattr(order, 'filled_at') and order.filled_at:
                data.append({
                    'symbol': order.symbol,
                    'side': order.side,
                    'qty': float(order.filled_qty or order.qty),
                    'price': float(order.filled_avg_price or 0),
                    'filled_at': order.filled_at,
                    'date': order.filled_at.date(),
                    'value': float(order.filled_qty or order.qty) * float(order.filled_avg_price or 0)
                })
        
        df = pd.DataFrame(data)
        
        account_data = {
            'equity': float(account.equity),
            'buying_power': float(account.buying_power),
            'day_trade_count': int(account.day_trade_count) if hasattr(account, 'day_trade_count') else 0,
            'last_equity': float(account.last_equity)
        }
        
        return df, account_data
        
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame(), {}

def calculate_pnl(df):
    """Calculate P&L using FIFO"""
    if df.empty:
        return {}
    
    stock_pnl = {}
    
    for symbol in df['symbol'].unique():
        symbol_data = df[df['symbol'] == symbol].sort_values('filled_at')
        
        buy_queue = []
        pnl = 0
        
        for _, row in symbol_data.iterrows():
            if row['side'] == 'buy':
                buy_queue.append({'qty': row['qty'], 'price': row['price']})
            else:  # sell
                remaining_qty = row['qty']
                
                while remaining_qty > 0 and buy_queue:
                    buy = buy_queue[0]
                    if buy['qty'] <= remaining_qty:
                        pnl += buy['qty'] * (row['price'] - buy['price'])
                        remaining_qty -= buy['qty']
                        buy_queue.pop(0)
                    else:
                        pnl += remaining_qty * (row['price'] - buy['price'])
                        buy['qty'] -= remaining_qty
                        remaining_qty = 0
        
        stock_pnl[symbol] = pnl
    
    return stock_pnl

# Layout
app.layout = html.Div([
    html.Div([
        # Header
        html.Div([
            html.H1("🚀 Interactive Scalping Bot Dashboard", className="header"),
            html.P("Professional real-time trading analytics", style={'textAlign': 'center', 'color': '#7f8c8d'})
        ]),
        
        # Controls Row
        html.Div([
            html.Div([
                html.Label("📅 Days to Analyze:", style={'fontWeight': 'bold'}),
                dcc.Slider(
                    id='days-slider',
                    min=1, max=14, value=7, step=1,
                    marks={i: {'label': f'{i}d', 'style': {'fontSize': '12px'}} for i in [1, 3, 7, 14]},
                    tooltip={"placement": "bottom", "always_visible": True}
                )
            ], className='four columns'),
            
            html.Div([
                html.Label("⚠️ Filters:", style={'fontWeight': 'bold'}),
                dcc.Checklist(
                    id='exclude-aug12',
                    options=[{'label': ' Exclude Aug 12 (No Risk Mgmt)', 'value': 'exclude'}],
                    value=['exclude'],
                    style={'marginTop': '10px'}
                )
            ], className='four columns'),
            
            html.Div([
                html.Label("🔄 Auto Refresh:", style={'fontWeight': 'bold'}),
                dcc.Interval(
                    id='interval-component',
                    interval=30*1000,  # 30 seconds
                    n_intervals=0
                ),
                html.Button('🔄 Refresh Now', id='refresh-button', n_clicks=0,
                           style={'marginTop': '10px', 'width': '100%', 'padding': '10px',
                                 'backgroundColor': '#3498db', 'color': 'white', 'border': 'none',
                                 'borderRadius': '5px', 'cursor': 'pointer'})
            ], className='four columns'),
        ], className='row', style={'marginBottom': '30px', 'padding': '20px', 
                                  'backgroundColor': '#ecf0f1', 'borderRadius': '10px'}),
        
        # Metrics Cards
        html.Div(id='metrics-cards', className='row', style={'marginBottom': '30px'}),
        
        # Main Charts Row
        html.Div([
            html.Div([
                html.Div(id='stock-performance-container', className='chart-container')
            ], className='six columns'),
            
            html.Div([
                html.Div(id='timeline-container', className='chart-container')
            ], className='six columns'),
        ], className='row'),
        
        # Secondary Charts Row
        html.Div([
            html.Div([
                html.Div(id='distribution-container', className='chart-container')
            ], className='six columns'),
            
            html.Div([
                html.Div(id='cumulative-container', className='chart-container')
            ], className='six columns'),
        ], className='row'),
        
        # Data Table Section
        html.Div([
            html.H3("📊 Live Trading Data", style={'color': '#2c3e50', 'marginBottom': '20px'}),
            html.Div(id='data-table-container', className='chart-container')
        ], style={'marginTop': '30px'}),
        
        # Status Bar
        html.Div(id='status-bar', style={
            'textAlign': 'center', 'marginTop': '20px', 'padding': '15px',
            'backgroundColor': '#2ecc71', 'color': 'white', 'borderRadius': '10px',
            'fontWeight': 'bold'
        })
        
    ], className='main-container')
])

# Main callback
@app.callback(
    [Output('metrics-cards', 'children'),
     Output('stock-performance-container', 'children'),
     Output('timeline-container', 'children'),
     Output('distribution-container', 'children'),
     Output('cumulative-container', 'children'),
     Output('data-table-container', 'children'),
     Output('status-bar', 'children')],
    [Input('days-slider', 'value'),
     Input('exclude-aug12', 'value'),
     Input('interval-component', 'n_intervals'),
     Input('refresh-button', 'n_clicks')]
)
def update_dashboard(days_back, exclude_aug12, n_intervals, refresh_clicks):
    """Update all dashboard components"""
    
    try:
        # Load data
        df, account_data = load_data()
        
        if df.empty:
            error_msg = html.Div("❌ No trading data available", 
                               style={'textAlign': 'center', 'color': 'red', 'fontSize': '20px'})
            return error_msg, error_msg, error_msg, error_msg, error_msg, error_msg, error_msg
        
        # Apply filters
        cutoff_date = datetime.now().date() - timedelta(days=days_back)
        df_filtered = df[df['date'] >= cutoff_date].copy()
        
        if 'exclude' in exclude_aug12:
            df_filtered = df_filtered[df_filtered['date'] != pd.to_datetime('2025-08-12').date()]
        
        # Calculate P&L
        stock_pnl = calculate_pnl(df_filtered)
        
        # Create components
        metrics = create_metrics_cards(stock_pnl, df_filtered, account_data)
        stock_chart = create_stock_performance_chart(stock_pnl)
        timeline_chart = create_timeline_chart(df_filtered)
        distribution_chart = create_distribution_chart(stock_pnl)
        cumulative_chart = create_cumulative_chart(stock_pnl)
        data_table = create_data_table(df_filtered)
        
        # Status
        total_pnl = sum(stock_pnl.values()) if stock_pnl else 0
        status = html.Div([
            html.Span(f"✅ Updated: {datetime.now().strftime('%H:%M:%S')} | "),
            html.Span(f"📊 {len(df_filtered)} trades | "),
            html.Span(f"💰 P&L: ${total_pnl:+,.2f} | "),
            html.Span(f"🏆 {len([p for p in stock_pnl.values() if p > 0])}/{len(stock_pnl)} winners" if stock_pnl else "No data")
        ])
        
        return metrics, stock_chart, timeline_chart, distribution_chart, cumulative_chart, data_table, status
        
    except Exception as e:
        error_msg = html.Div(f"❌ Error: {str(e)}", style={'color': 'red', 'textAlign': 'center'})
        return error_msg, error_msg, error_msg, error_msg, error_msg, error_msg, error_msg

def create_metrics_cards(stock_pnl, df, account_data):
    """Create metrics cards"""
    total_pnl = sum(stock_pnl.values()) if stock_pnl else 0
    winners = len([p for p in stock_pnl.values() if p > 0]) if stock_pnl else 0
    total_stocks = len(stock_pnl) if stock_pnl else 0
    win_rate = (winners / total_stocks * 100) if total_stocks > 0 else 0
    
    daily_pnl = account_data.get('equity', 0) - account_data.get('last_equity', 0)
    
    return html.Div([
        html.Div([
            html.H2(f"${account_data.get('equity', 0):,.2f}", style={'margin': '0', 'fontSize': '24px'}),
            html.P("Account Equity", style={'margin': '0', 'fontSize': '14px'}),
            html.P(f"${daily_pnl:+.2f} today", style={'margin': '0', 'fontSize': '12px', 'opacity': '0.8'})
        ], className='three columns metric-card'),
        
        html.Div([
            html.H2(f"${total_pnl:+,.2f}", style={'margin': '0', 'fontSize': '24px'}),
            html.P("Calculated P&L", style={'margin': '0', 'fontSize': '14px'}),
            html.P(f"{total_stocks} stocks", style={'margin': '0', 'fontSize': '12px', 'opacity': '0.8'})
        ], className='three columns metric-card'),
        
        html.Div([
            html.H2(f"{win_rate:.0f}%", style={'margin': '0', 'fontSize': '24px'}),
            html.P("Win Rate", style={'margin': '0', 'fontSize': '14px'}),
            html.P(f"{winners}/{total_stocks} winners", style={'margin': '0', 'fontSize': '12px', 'opacity': '0.8'})
        ], className='three columns metric-card'),
        
        html.Div([
            html.H2(f"{len(df)}", style={'margin': '0', 'fontSize': '24px'}),
            html.P("Total Trades", style={'margin': '0', 'fontSize': '14px'}),
            html.P(f"${df['value'].sum():,.0f} volume" if not df.empty else "$0 volume", style={'margin': '0', 'fontSize': '12px', 'opacity': '0.8'})
        ], className='three columns metric-card'),
    ], className='row')

def create_stock_performance_chart(stock_pnl):
    """Create stock performance chart"""
    if not stock_pnl:
        return dcc.Graph(figure={})
    
    symbols = list(stock_pnl.keys())
    pnls = list(stock_pnl.values())
    colors = ['#2ecc71' if p > 0 else '#e74c3c' if p < 0 else '#f39c12' for p in pnls]
    
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
        title="📊 Stock Performance Analysis",
        xaxis_title="Stock Symbol",
        yaxis_title="Profit/Loss ($)",
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12)
    )
    
    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    
    return dcc.Graph(figure=fig)

def create_timeline_chart(df):
    """Create timeline chart"""
    if df.empty:
        return dcc.Graph(figure={})
    
    df_copy = df.copy()
    df_copy['hour'] = pd.to_datetime(df_copy['filled_at']).dt.hour
    hourly_data = df_copy.groupby(['hour', 'side']).size().unstack(fill_value=0)
    
    fig = go.Figure()
    
    if 'buy' in hourly_data.columns:
        fig.add_trace(go.Scatter(
            x=hourly_data.index,
            y=hourly_data['buy'],
            mode='lines+markers',
            name='📈 Buy Orders',
            line=dict(color='#2ecc71', width=3),
            marker=dict(size=8)
        ))
    
    if 'sell' in hourly_data.columns:
        fig.add_trace(go.Scatter(
            x=hourly_data.index,
            y=hourly_data['sell'],
            mode='lines+markers',
            name='📉 Sell Orders',
            line=dict(color='#e74c3c', width=3),
            marker=dict(size=8)
        ))
    
    fig.update_layout(
        title="⏰ Trading Activity Timeline",
        xaxis_title="Hour of Day",
        yaxis_title="Number of Orders",
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return dcc.Graph(figure=fig)

def create_distribution_chart(stock_pnl):
    """Create P&L distribution chart"""
    if not stock_pnl:
        return dcc.Graph(figure={})
    
    pnls = list(stock_pnl.values())
    
    fig = go.Figure(data=[
        go.Histogram(
            x=pnls,
            nbinsx=12,
            marker_color='rgba(54, 162, 235, 0.7)',
            marker_line_color='black',
            marker_line_width=1
        )
    ])
    
    fig.update_layout(
        title="📈 P&L Distribution",
        xaxis_title="P&L ($)",
        yaxis_title="Number of Stocks",
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return dcc.Graph(figure=fig)

def create_cumulative_chart(stock_pnl):
    """Create cumulative P&L chart"""
    if not stock_pnl:
        return dcc.Graph(figure={})
    
    symbols = list(stock_pnl.keys())
    pnls = list(stock_pnl.values())
    cumulative = [sum(pnls[:i+1]) for i in range(len(pnls))]
    
    fig = go.Figure(data=[
        go.Scatter(
            x=list(range(len(symbols))),
            y=cumulative,
            mode='lines+markers',
            line=dict(color='#3498db', width=4),
            marker=dict(size=10),
            text=symbols,
            hovertemplate='<b>%{text}</b><br>Cumulative: $%{y:+,.2f}<extra></extra>'
        )
    ])
    
    fig.add_trace(go.Scatter(
        x=list(range(len(symbols))),
        y=cumulative,
        fill='tozeroy',
        mode='none',
        fillcolor='rgba(52, 152, 219, 0.2)',
        showlegend=False
    ))
    
    fig.update_layout(
        title="📈 Cumulative P&L Progression",
        xaxis_title="Stock Sequence",
        yaxis_title="Cumulative P&L ($)",
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    
    return dcc.Graph(figure=fig)

def create_data_table(df):
    """Create data table"""
    if df.empty:
        return html.Div("No data available")
    
    table_df = df[['symbol', 'side', 'qty', 'price', 'value', 'filled_at']].copy()
    table_df['filled_at'] = table_df['filled_at'].dt.strftime('%m/%d %H:%M:%S')
    table_df = table_df.round(2).tail(20)  # Show last 20 trades
    
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
        style_cell={'textAlign': 'center', 'fontSize': '12px', 'padding': '10px'},
        style_header={'backgroundColor': '#34495e', 'color': 'white', 'fontWeight': 'bold'},
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
        page_size=10,
        style_table={'overflowX': 'auto'}
    )

if __name__ == '__main__':
    print("🚀 Starting Plotly Dash Dashboard...")
    print("📊 Dashboard will be available at: http://localhost:8050")
    print("🔄 Auto-refresh every 30 seconds")
    print("📱 Mobile responsive design")
    
    app.run_server(debug=True, host='0.0.0.0', port=8050)
