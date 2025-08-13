#!/usr/bin/env python3
"""
Comprehensive End-of-Day P&L Analysis System
Generates detailed trading reports with charts and graphs
Auto-runs at market close with full analysis
"""

import os
import sys
import pandas as pd
import numpy as np

# Set matplotlib backend before importing pyplot
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import json
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Set style for professional charts
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

from data_manager import DataManager
from config import config

class EODAnalyzer:
    def __init__(self):
        self.dm = DataManager()
        self.today = datetime.now().strftime('%Y-%m-%d')
        self.report_dir = Path("reports") / self.today
        self.report_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (self.report_dir / "charts").mkdir(exist_ok=True)
        (self.report_dir / "data").mkdir(exist_ok=True)
        
        print(f"[EOD] Initializing End-of-Day Analysis for {self.today}")
        print(f"[EOD] Report directory: {self.report_dir}")

    def get_todays_trades(self):
        """Get all trades from today"""
        try:
            # Get activities from Alpaca - using correct parameter name
            activities = self.dm.api.get_activities(
                activity_types='FILL',
                date=self.today
            )
            
            trades = []
            for activity in activities:
                trade = {
                    'symbol': activity.symbol,
                    'side': activity.side,  # 'buy' or 'sell'
                    'qty': float(activity.qty),
                    'price': float(activity.price),
                    'timestamp': activity.transaction_time,
                    'order_id': activity.order_id,
                    'trade_value': float(activity.qty) * float(activity.price)
                }
                trades.append(trade)
            
            df = pd.DataFrame(trades)
            if not df.empty:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df['time'] = df['timestamp'].dt.strftime('%H:%M:%S')
                df['hour'] = df['timestamp'].dt.hour
                
            return df
            
        except Exception as e:
            print(f"[ERROR] Failed to get trades: {e}")
            return pd.DataFrame()

    def calculate_trade_pairs(self, df):
        """Match buy/sell pairs to calculate P&L per trade"""
        if df.empty:
            return pd.DataFrame()
        
        trade_pairs = []
        
        # Group by symbol to match trades
        for symbol in df['symbol'].unique():
            symbol_trades = df[df['symbol'] == symbol].sort_values('timestamp')
            
            # Simple FIFO matching for demonstration
            buys = symbol_trades[symbol_trades['side'] == 'buy'].copy()
            sells = symbol_trades[symbol_trades['side'] == 'sell'].copy()
            
            for _, sell in sells.iterrows():
                if not buys.empty:
                    # Match with earliest buy
                    buy = buys.iloc[0]
                    
                    qty = min(buy['qty'], sell['qty'])
                    
                    # Calculate P&L
                    if buy['side'] == 'buy' and sell['side'] == 'sell':
                        # Long trade
                        pnl = (sell['price'] - buy['price']) * qty
                        direction = 'LONG'
                    else:
                        # Short trade (if applicable)
                        pnl = (buy['price'] - sell['price']) * qty
                        direction = 'SHORT'
                    
                    trade_pair = {
                        'symbol': symbol,
                        'direction': direction,
                        'entry_time': buy['timestamp'],
                        'exit_time': sell['timestamp'],
                        'entry_price': buy['price'],
                        'exit_price': sell['price'],
                        'quantity': qty,
                        'pnl': pnl,
                        'pnl_pct': (pnl / (buy['price'] * qty)) * 100,
                        'hold_time_minutes': (sell['timestamp'] - buy['timestamp']).total_seconds() / 60,
                        'entry_hour': buy['hour'],
                        'exit_hour': sell['hour']
                    }
                    trade_pairs.append(trade_pair)
                    
                    # Update quantities
                    buys.iloc[0, buys.columns.get_loc('qty')] -= qty
                    if buys.iloc[0]['qty'] <= 0:
                        buys = buys.iloc[1:]
        
        return pd.DataFrame(trade_pairs)

    def generate_summary_stats(self, trades_df, pairs_df):
        """Generate comprehensive summary statistics"""
        if trades_df.empty:
            return {
                'total_trades': 0,
                'symbols_traded': 0,
                'total_pnl': 0,
                'win_rate': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'profit_factor': 0
            }
        
        stats = {}
        
        # Basic stats
        stats['total_trades'] = len(trades_df)
        stats['symbols_traded'] = trades_df['symbol'].nunique()
        stats['total_volume'] = trades_df['trade_value'].sum()
        
        if not pairs_df.empty:
            # P&L Analysis
            stats['total_pnl'] = pairs_df['pnl'].sum()
            stats['completed_trades'] = len(pairs_df)
            
            # Win/Loss Analysis
            winners = pairs_df[pairs_df['pnl'] > 0]
            losers = pairs_df[pairs_df['pnl'] < 0]
            
            stats['winners'] = len(winners)
            stats['losers'] = len(losers)
            stats['win_rate'] = (len(winners) / len(pairs_df)) * 100 if len(pairs_df) > 0 else 0
            
            stats['avg_win'] = winners['pnl'].mean() if len(winners) > 0 else 0
            stats['avg_loss'] = losers['pnl'].mean() if len(losers) > 0 else 0
            stats['largest_win'] = winners['pnl'].max() if len(winners) > 0 else 0
            stats['largest_loss'] = losers['pnl'].min() if len(losers) > 0 else 0
            
            # Profit Factor
            gross_profit = winners['pnl'].sum() if len(winners) > 0 else 0
            gross_loss = abs(losers['pnl'].sum()) if len(losers) > 0 else 0
            stats['profit_factor'] = gross_profit / gross_loss if gross_loss > 0 else float('inf') if gross_profit > 0 else 0
            
            # Time Analysis
            stats['avg_hold_time'] = pairs_df['hold_time_minutes'].mean()
            stats['shortest_trade'] = pairs_df['hold_time_minutes'].min()
            stats['longest_trade'] = pairs_df['hold_time_minutes'].max()
            
            # Direction Analysis
            long_trades = pairs_df[pairs_df['direction'] == 'LONG']
            short_trades = pairs_df[pairs_df['direction'] == 'SHORT']
            
            stats['long_trades'] = len(long_trades)
            stats['short_trades'] = len(short_trades)
            stats['long_pnl'] = long_trades['pnl'].sum() if len(long_trades) > 0 else 0
            stats['short_pnl'] = short_trades['pnl'].sum() if len(short_trades) > 0 else 0
            stats['long_win_rate'] = (len(long_trades[long_trades['pnl'] > 0]) / len(long_trades)) * 100 if len(long_trades) > 0 else 0
            stats['short_win_rate'] = (len(short_trades[short_trades['pnl'] > 0]) / len(short_trades)) * 100 if len(short_trades) > 0 else 0
        
        return stats

    def create_pnl_by_stock_chart(self, pairs_df):
        """Create P&L by stock chart"""
        if pairs_df.empty:
            return None
            
        stock_pnl = pairs_df.groupby('symbol')['pnl'].sum().sort_values(ascending=True)
        
        # Create matplotlib chart
        fig, ax = plt.subplots(figsize=(12, 8))
        
        colors = ['red' if x < 0 else 'green' for x in stock_pnl.values]
        bars = ax.barh(stock_pnl.index, stock_pnl.values, color=colors, alpha=0.7)
        
        ax.set_title(f'P&L by Stock - {self.today}', fontsize=16, fontweight='bold')
        ax.set_xlabel('Profit/Loss ($)', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for bar, value in zip(bars, stock_pnl.values):
            ax.text(value + (0.01 * max(abs(stock_pnl.min()), abs(stock_pnl.max()))), 
                   bar.get_y() + bar.get_height()/2, 
                   f'${value:.2f}', 
                   va='center', ha='left' if value >= 0 else 'right')
        
        plt.tight_layout()
        chart_path = self.report_dir / "charts" / "pnl_by_stock.png"
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return chart_path

    def create_hourly_trading_chart(self, pairs_df):
        """Create hourly trading activity chart"""
        if pairs_df.empty:
            return None
            
        # Trading activity by hour
        hourly_trades = pairs_df.groupby('entry_hour').agg({
            'pnl': ['count', 'sum', 'mean']
        }).round(2)
        
        hourly_trades.columns = ['Trade_Count', 'Total_PnL', 'Avg_PnL']
        hourly_trades = hourly_trades.reset_index()
        
        # Create subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
        
        # Trade count by hour
        ax1.bar(hourly_trades['entry_hour'], hourly_trades['Trade_Count'], 
                color='steelblue', alpha=0.7)
        ax1.set_title('Trading Activity by Hour', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Hour of Day')
        ax1.set_ylabel('Number of Trades')
        ax1.grid(True, alpha=0.3)
        
        # P&L by hour
        colors = ['red' if x < 0 else 'green' for x in hourly_trades['Total_PnL']]
        ax2.bar(hourly_trades['entry_hour'], hourly_trades['Total_PnL'], 
                color=colors, alpha=0.7)
        ax2.set_title('P&L by Hour', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Hour of Day')
        ax2.set_ylabel('Total P&L ($)')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        chart_path = self.report_dir / "charts" / "hourly_activity.png"
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return chart_path

    def create_win_loss_distribution(self, pairs_df):
        """Create win/loss distribution chart"""
        if pairs_df.empty:
            return None
            
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Histogram of P&L
        ax1.hist(pairs_df['pnl'], bins=20, alpha=0.7, color='steelblue', edgecolor='black')
        ax1.axvline(x=0, color='red', linestyle='--', alpha=0.8)
        ax1.set_title('P&L Distribution', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Profit/Loss ($)')
        ax1.set_ylabel('Frequency')
        ax1.grid(True, alpha=0.3)
        
        # Win/Loss pie chart
        winners = len(pairs_df[pairs_df['pnl'] > 0])
        losers = len(pairs_df[pairs_df['pnl'] < 0])
        breakeven = len(pairs_df[pairs_df['pnl'] == 0])
        
        sizes = [winners, losers, breakeven]
        labels = [f'Winners ({winners})', f'Losers ({losers})', f'Breakeven ({breakeven})']
        colors = ['green', 'red', 'gray']
        
        # Remove zero values
        non_zero = [(size, label, color) for size, label, color in zip(sizes, labels, colors) if size > 0]
        if non_zero:
            sizes, labels, colors = zip(*non_zero)
            ax2.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        
        ax2.set_title('Win/Loss Distribution', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        chart_path = self.report_dir / "charts" / "win_loss_distribution.png"
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return chart_path

    def create_interactive_dashboard(self, trades_df, pairs_df, stats):
        """Create interactive HTML dashboard"""
        if pairs_df.empty:
            return None
            
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('P&L by Stock', 'Hourly P&L', 'Trade Timeline', 'Long vs Short Performance'),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "scatter"}, {"type": "bar"}]]
        )
        
        # P&L by Stock
        stock_pnl = pairs_df.groupby('symbol')['pnl'].sum().sort_values()
        fig.add_trace(
            go.Bar(x=stock_pnl.values, y=stock_pnl.index, 
                   orientation='h', name='P&L by Stock',
                   marker_color=['red' if x < 0 else 'green' for x in stock_pnl.values]),
            row=1, col=1
        )
        
        # Hourly P&L
        hourly_pnl = pairs_df.groupby('entry_hour')['pnl'].sum()
        fig.add_trace(
            go.Bar(x=hourly_pnl.index, y=hourly_pnl.values, 
                   name='Hourly P&L',
                   marker_color=['red' if x < 0 else 'green' for x in hourly_pnl.values]),
            row=1, col=2
        )
        
        # Trade Timeline
        fig.add_trace(
            go.Scatter(x=pairs_df['entry_time'], y=pairs_df['pnl'],
                      mode='markers', name='Trade P&L',
                      marker=dict(color=pairs_df['pnl'], 
                                colorscale='RdYlGn', 
                                size=10,
                                colorbar=dict(title="P&L ($)"))),
            row=2, col=1
        )
        
        # Long vs Short Performance
        direction_pnl = pairs_df.groupby('direction')['pnl'].sum()
        fig.add_trace(
            go.Bar(x=direction_pnl.index, y=direction_pnl.values,
                   name='Direction P&L',
                   marker_color=['green' if x > 0 else 'red' for x in direction_pnl.values]),
            row=2, col=2
        )
        
        fig.update_layout(
            title_text=f"EOD Trading Dashboard - {self.today}",
            showlegend=False,
            height=800
        )
        
        # Save as HTML
        dashboard_path = self.report_dir / "eod_dashboard.html"
        fig.write_html(dashboard_path)
        
        return dashboard_path

    def generate_detailed_report(self, trades_df, pairs_df, stats):
        """Generate detailed text report"""
        report_path = self.report_dir / "eod_report.txt"
        
        with open(report_path, 'w') as f:
            f.write("="*80 + "\n")
            f.write(f"         END-OF-DAY TRADING REPORT - {self.today}\n")
            f.write("="*80 + "\n\n")
            
            # Executive Summary
            f.write("EXECUTIVE SUMMARY\n")
            f.write("-"*40 + "\n")
            f.write(f"Total P&L: ${stats.get('total_pnl', 0):.2f}\n")
            f.write(f"Total Trades: {stats.get('completed_trades', 0)}\n")
            f.write(f"Win Rate: {stats.get('win_rate', 0):.1f}%\n")
            f.write(f"Profit Factor: {stats.get('profit_factor', 0):.2f}\n")
            f.write(f"Symbols Traded: {stats.get('symbols_traded', 0)}\n\n")
            
            # Performance Metrics
            f.write("PERFORMANCE METRICS\n")
            f.write("-"*40 + "\n")
            f.write(f"Winners: {stats.get('winners', 0)}\n")
            f.write(f"Losers: {stats.get('losers', 0)}\n")
            f.write(f"Average Win: ${stats.get('avg_win', 0):.2f}\n")
            f.write(f"Average Loss: ${stats.get('avg_loss', 0):.2f}\n")
            f.write(f"Largest Win: ${stats.get('largest_win', 0):.2f}\n")
            f.write(f"Largest Loss: ${stats.get('largest_loss', 0):.2f}\n\n")
            
            # Time Analysis
            f.write("TIME ANALYSIS\n")
            f.write("-"*40 + "\n")
            f.write(f"Average Hold Time: {stats.get('avg_hold_time', 0):.1f} minutes\n")
            f.write(f"Shortest Trade: {stats.get('shortest_trade', 0):.1f} minutes\n")
            f.write(f"Longest Trade: {stats.get('longest_trade', 0):.1f} minutes\n\n")
            
            # Direction Analysis
            f.write("LONG vs SHORT ANALYSIS\n")
            f.write("-"*40 + "\n")
            f.write(f"Long Trades: {stats.get('long_trades', 0)}\n")
            f.write(f"Long P&L: ${stats.get('long_pnl', 0):.2f}\n")
            f.write(f"Long Win Rate: {stats.get('long_win_rate', 0):.1f}%\n")
            f.write(f"Short Trades: {stats.get('short_trades', 0)}\n")
            f.write(f"Short P&L: ${stats.get('short_pnl', 0):.2f}\n")
            f.write(f"Short Win Rate: {stats.get('short_win_rate', 0):.1f}%\n\n")
            
            # Stock-by-Stock Analysis
            if not pairs_df.empty:
                f.write("STOCK-BY-STOCK ANALYSIS\n")
                f.write("-"*40 + "\n")
                stock_analysis = pairs_df.groupby('symbol').agg({
                    'pnl': ['count', 'sum', 'mean'],
                    'direction': lambda x: f"{sum(x=='LONG')}L/{sum(x=='SHORT')}S"
                }).round(2)
                
                for symbol in stock_analysis.index:
                    count = stock_analysis.loc[symbol, ('pnl', 'count')]
                    total_pnl = stock_analysis.loc[symbol, ('pnl', 'sum')]
                    avg_pnl = stock_analysis.loc[symbol, ('pnl', 'mean')]
                    directions = stock_analysis.loc[symbol, ('direction', '<lambda>')]
                    
                    f.write(f"{symbol}: {count} trades, ${total_pnl:.2f} total, ${avg_pnl:.2f} avg, {directions}\n")
            
            f.write("\n" + "="*80 + "\n")
            f.write(f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*80 + "\n")
        
        return report_path

    def save_data_exports(self, trades_df, pairs_df):
        """Save raw data as CSV files"""
        if not trades_df.empty:
            trades_path = self.report_dir / "data" / "raw_trades.csv"
            trades_df.to_csv(trades_path, index=False)
        
        if not pairs_df.empty:
            pairs_path = self.report_dir / "data" / "trade_pairs.csv"
            pairs_df.to_csv(pairs_path, index=False)
        
        return self.report_dir / "data"

    def run_full_analysis(self):
        """Run complete EOD analysis"""
        print(f"\n[EOD] Starting comprehensive End-of-Day analysis...")
        print(f"[EOD] Date: {self.today}")
        
        try:
            # Get data
            print("[EOD] Fetching today's trades...")
            trades_df = self.get_todays_trades()
            
            if trades_df.empty:
                print("[EOD] No trades found for today")
                print("[EOD] ✅ Analysis completed (no trading activity)")
                return {
                    'success': True,
                    'stats': {'total_trades': 0, 'total_pnl': 0},
                    'report_dir': str(self.report_dir),
                    'dashboard_path': None
                }
            
            print(f"[EOD] Found {len(trades_df)} trade executions")
            
            # Calculate trade pairs
            print("[EOD] Calculating trade pairs and P&L...")
            pairs_df = self.calculate_trade_pairs(trades_df)
            print(f"[EOD] Matched {len(pairs_df)} complete trade pairs")
            
            # Generate statistics
            print("[EOD] Generating summary statistics...")
            stats = self.generate_summary_stats(trades_df, pairs_df)
            
            # Create charts
            print("[EOD] Creating charts...")
            chart_paths = []
            
            chart_paths.append(self.create_pnl_by_stock_chart(pairs_df))
            chart_paths.append(self.create_hourly_trading_chart(pairs_df))
            chart_paths.append(self.create_win_loss_distribution(pairs_df))
            
            # Create interactive dashboard
            print("[EOD] Creating interactive dashboard...")
            dashboard_path = self.create_interactive_dashboard(trades_df, pairs_df, stats)
            
            # Generate reports
            print("[EOD] Generating detailed report...")
            report_path = self.generate_detailed_report(trades_df, pairs_df, stats)
            
            # Save data exports
            print("[EOD] Saving data exports...")
            data_dir = self.save_data_exports(trades_df, pairs_df)
            
            # Summary
            print(f"\n[EOD] ✅ Analysis Complete!")
            print(f"[EOD] 📊 Total P&L: ${stats.get('total_pnl', 0):.2f}")
            print(f"[EOD] 📈 Win Rate: {stats.get('win_rate', 0):.1f}%")
            print(f"[EOD] 🎯 Profit Factor: {stats.get('profit_factor', 0):.2f}")
            print(f"[EOD] 📁 Reports saved to: {self.report_dir}")
            
            if dashboard_path:
                print(f"[EOD] 🌐 Interactive Dashboard: {dashboard_path}")
            
            print(f"[EOD] 📊 Charts: {len([p for p in chart_paths if p])} created")
            print(f"[EOD] 📄 Detailed Report: {report_path}")
            
            return {
                'success': True,
                'stats': stats,
                'report_dir': str(self.report_dir),
                'dashboard_path': str(dashboard_path) if dashboard_path else None
            }
            
        except Exception as e:
            print(f"[ERROR] EOD Analysis failed: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}

def main():
    """Main execution function"""
    analyzer = EODAnalyzer()
    result = analyzer.run_full_analysis()
    
    if result['success']:
        print(f"\n[SUCCESS] EOD Analysis completed successfully!")
        return 0
    else:
        print(f"\n[FAILURE] EOD Analysis failed: {result.get('error', 'Unknown error')}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
