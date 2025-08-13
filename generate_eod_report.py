#!/usr/bin/env python3
"""
📊 End-of-Day Report Generator for Intraday Trading Bot
Generates comprehensive daily performance reports with cost analysis
"""

import sys
import json
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from config import config
from utils.logger import setup_logger
from utils.pnl_tracker import PnLTracker
from live_pnl_monitor import EnhancedPnLMonitor

class IntradayEODReportGenerator:
    """End-of-day report generator for intraday trading"""
    
    def __init__(self, date: Optional[str] = None):
        """Initialize EOD report generator
        
        Args:
            date: Date for report (YYYY-MM-DD), defaults to today
        """
        self.logger = setup_logger("eod_report")
        self.date = date or datetime.now().strftime('%Y-%m-%d')
        self.pnl_tracker = PnLTracker()
        self.enhanced_monitor = EnhancedPnLMonitor()
        
        # Report directories
        self.reports_dir = Path("reports") / "daily"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"📊 EOD Report Generator initialized for {self.date}")
    
    def get_daily_trades(self) -> pd.DataFrame:
        """Get all trades for the specified date"""
        try:
            db_path = self.pnl_tracker.db_path
            
            with sqlite3.connect(db_path) as conn:
                query = """
                    SELECT * FROM trades 
                    WHERE DATE(entry_time) = ? AND status = 'CLOSED'
                    ORDER BY entry_time
                """
                df = pd.read_sql_query(query, conn, params=[self.date])
                
            self.logger.info(f"📈 Retrieved {len(df)} completed trades for {self.date}")
            return df
            
        except Exception as e:
            self.logger.error(f"❌ Error retrieving trades: {e}")
            return pd.DataFrame()
    
    def calculate_performance_metrics(self, trades_df: pd.DataFrame) -> Dict:
        """Calculate comprehensive performance metrics"""
        if trades_df.empty:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'total_pnl': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'profit_factor': 0,
                'sharpe_ratio': 0,
                'max_drawdown': 0
            }
        
        # Basic metrics
        total_trades = len(trades_df)
        winning_trades = trades_df[trades_df['pnl'] > 0]
        losing_trades = trades_df[trades_df['pnl'] < 0]
        
        win_rate = len(winning_trades) / total_trades * 100
        total_pnl = trades_df['pnl'].sum()
        total_gross_pnl = trades_df['gross_pnl'].sum() if 'gross_pnl' in trades_df.columns else total_pnl
        total_costs = trades_df['total_transaction_costs'].sum() if 'total_transaction_costs' in trades_df.columns else 0
        
        avg_win = winning_trades['pnl'].mean() if len(winning_trades) > 0 else 0
        avg_loss = losing_trades['pnl'].mean() if len(losing_trades) > 0 else 0
        
        # Profit factor
        gross_profit = winning_trades['pnl'].sum() if len(winning_trades) > 0 else 0
        gross_loss = abs(losing_trades['pnl'].sum()) if len(losing_trades) > 0 else 1
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        # Drawdown calculation
        cumulative_pnl = trades_df['pnl'].cumsum()
        rolling_max = cumulative_pnl.expanding().max()
        drawdown = cumulative_pnl - rolling_max
        max_drawdown = drawdown.min()
        
        # Sharpe ratio (simplified daily calculation)
        returns = trades_df['pnl'] / (trades_df['entry_price'] * trades_df['quantity']) * 100
        sharpe_ratio = returns.mean() / returns.std() if returns.std() > 0 else 0
        
        return {
            'total_trades': total_trades,
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'total_gross_pnl': total_gross_pnl,
            'total_costs': total_costs,
            'cost_impact_pct': (total_costs / abs(total_gross_pnl) * 100) if total_gross_pnl != 0 else 0,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'largest_win': winning_trades['pnl'].max() if len(winning_trades) > 0 else 0,
            'largest_loss': losing_trades['pnl'].min() if len(losing_trades) > 0 else 0
        }
    
    def analyze_strategy_performance(self, trades_df: pd.DataFrame) -> Dict:
        """Analyze performance by strategy"""
        if trades_df.empty:
            return {}
        
        strategy_stats = {}
        
        for strategy in trades_df['strategy'].unique():
            strategy_trades = trades_df[trades_df['strategy'] == strategy]
            strategy_stats[strategy] = {
                'trades': len(strategy_trades),
                'total_pnl': strategy_trades['pnl'].sum(),
                'win_rate': len(strategy_trades[strategy_trades['pnl'] > 0]) / len(strategy_trades) * 100,
                'avg_pnl': strategy_trades['pnl'].mean()
            }
        
        return strategy_stats
    
    def analyze_time_patterns(self, trades_df: pd.DataFrame) -> Dict:
        """Analyze performance by time of day"""
        if trades_df.empty:
            return {}
        
        # Convert entry_time to datetime and extract hour
        trades_df['entry_hour'] = pd.to_datetime(trades_df['entry_time']).dt.hour
        
        hourly_stats = {}
        for hour in range(9, 16):  # Market hours 9 AM to 4 PM
            hour_trades = trades_df[trades_df['entry_hour'] == hour]
            if len(hour_trades) > 0:
                hourly_stats[f"{hour:02d}:00"] = {
                    'trades': len(hour_trades),
                    'total_pnl': hour_trades['pnl'].sum(),
                    'win_rate': len(hour_trades[hour_trades['pnl'] > 0]) / len(hour_trades) * 100
                }
        
        return hourly_stats
    
    def create_performance_charts(self, trades_df: pd.DataFrame, metrics: Dict):
        """Create performance visualization charts"""
        if trades_df.empty:
            return
        
        # Set up the plotting style
        plt.style.use('seaborn-v0_8')
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f'Intraday Trading Performance - {self.date}', fontsize=16, fontweight='bold')
        
        # 1. Cumulative PnL
        cumulative_pnl = trades_df['pnl'].cumsum()
        axes[0, 0].plot(cumulative_pnl.index, cumulative_pnl.values, linewidth=2, color='#2E86AB')
        axes[0, 0].axhline(y=0, color='red', linestyle='--', alpha=0.5)
        axes[0, 0].set_title('Cumulative PnL')
        axes[0, 0].set_xlabel('Trade Number')
        axes[0, 0].set_ylabel('Cumulative PnL ($)')
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. PnL Distribution
        axes[0, 1].hist(trades_df['pnl'], bins=20, alpha=0.7, color='#A23B72', edgecolor='black')
        axes[0, 1].axvline(x=0, color='red', linestyle='--', alpha=0.5)
        axes[0, 1].set_title('PnL Distribution')
        axes[0, 1].set_xlabel('PnL ($)')
        axes[0, 1].set_ylabel('Frequency')
        axes[0, 1].grid(True, alpha=0.3)
        
        # 3. Strategy Performance
        if 'strategy' in trades_df.columns:
            strategy_pnl = trades_df.groupby('strategy')['pnl'].sum()
            axes[1, 0].bar(strategy_pnl.index, strategy_pnl.values, color='#F18F01', alpha=0.8)
            axes[1, 0].set_title('PnL by Strategy')
            axes[1, 0].set_xlabel('Strategy')
            axes[1, 0].set_ylabel('Total PnL ($)')
            axes[1, 0].tick_params(axis='x', rotation=45)
            axes[1, 0].grid(True, alpha=0.3)
        
        # 4. Hourly Performance
        if len(trades_df) > 0:
            trades_df['entry_hour'] = pd.to_datetime(trades_df['entry_time']).dt.hour
            hourly_pnl = trades_df.groupby('entry_hour')['pnl'].sum()
            axes[1, 1].bar(hourly_pnl.index, hourly_pnl.values, color='#C73E1D', alpha=0.8)
            axes[1, 1].set_title('PnL by Hour')
            axes[1, 1].set_xlabel('Hour of Day')
            axes[1, 1].set_ylabel('Total PnL ($)')
            axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save chart
        chart_path = self.reports_dir / f"{self.date}_performance_charts.png"
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        self.logger.info(f"📊 Performance charts saved to {chart_path}")
    
    def generate_html_report(self, trades_df: pd.DataFrame, metrics: Dict, 
                           strategy_stats: Dict, time_stats: Dict) -> str:
        """Generate comprehensive HTML report"""
        
        # Calculate additional stats for intraday trading
        avg_hold_time = trades_df['hold_time_seconds'].mean() / 3600 if len(trades_df) > 0 else 0  # Convert to hours
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Intraday Trading Report - {self.date}</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; background-color: #f5f5f5; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; text-align: center; }}
                .section {{ background: white; margin: 20px 0; padding: 25px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }}
                .metric-card {{ background: #f8f9fa; padding: 15px; border-radius: 6px; text-align: center; border-left: 4px solid #667eea; }}
                .metric-value {{ font-size: 24px; font-weight: bold; color: #333; }}
                .metric-label {{ font-size: 12px; color: #666; text-transform: uppercase; }}
                .positive {{ color: #28a745; }}
                .negative {{ color: #dc3545; }}
                .neutral {{ color: #6c757d; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #667eea; color: white; }}
                tr:nth-child(even) {{ background-color: #f9f9f9; }}
                .summary {{ font-size: 18px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 Intraday Trading Performance Report</h1>
                <h2>{self.date}</h2>
                <p>Comprehensive analysis of swing trading performance and costs</p>
            </div>
            
            <div class="section">
                <h2>📈 Performance Summary</h2>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-value">{metrics['total_trades']}</div>
                        <div class="metric-label">Total Trades</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value {'positive' if metrics['total_pnl'] > 0 else 'negative'}">${metrics['total_pnl']:.2f}</div>
                        <div class="metric-label">Net PnL</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{metrics['win_rate']:.1f}%</div>
                        <div class="metric-label">Win Rate</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{avg_hold_time:.1f}h</div>
                        <div class="metric-label">Avg Hold Time</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{metrics['profit_factor']:.2f}</div>
                        <div class="metric-label">Profit Factor</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${metrics['total_costs']:.2f}</div>
                        <div class="metric-label">Total Costs</div>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>💰 Cost Analysis</h2>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-value">${metrics['total_gross_pnl']:.2f}</div>
                        <div class="metric-label">Gross PnL</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{metrics['cost_impact_pct']:.2f}%</div>
                        <div class="metric-label">Cost Impact</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${metrics['avg_win']:.2f}</div>
                        <div class="metric-label">Avg Win</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${metrics['avg_loss']:.2f}</div>
                        <div class="metric-label">Avg Loss</div>
                    </div>
                </div>
            </div>
        """
        
        # Strategy performance table
        if strategy_stats:
            html_content += """
            <div class="section">
                <h2>🎯 Strategy Performance</h2>
                <table>
                    <tr><th>Strategy</th><th>Trades</th><th>Total PnL</th><th>Win Rate</th><th>Avg PnL</th></tr>
            """
            for strategy, stats in strategy_stats.items():
                html_content += f"""
                    <tr>
                        <td>{strategy}</td>
                        <td>{stats['trades']}</td>
                        <td class="{'positive' if stats['total_pnl'] > 0 else 'negative'}">${stats['total_pnl']:.2f}</td>
                        <td>{stats['win_rate']:.1f}%</td>
                        <td class="{'positive' if stats['avg_pnl'] > 0 else 'negative'}">${stats['avg_pnl']:.2f}</td>
                    </tr>
                """
            html_content += "</table></div>"
        
        # Time analysis
        if time_stats:
            html_content += """
            <div class="section">
                <h2>🕐 Hourly Performance</h2>
                <table>
                    <tr><th>Time</th><th>Trades</th><th>Total PnL</th><th>Win Rate</th></tr>
            """
            for time_slot, stats in time_stats.items():
                html_content += f"""
                    <tr>
                        <td>{time_slot}</td>
                        <td>{stats['trades']}</td>
                        <td class="{'positive' if stats['total_pnl'] > 0 else 'negative'}">${stats['total_pnl']:.2f}</td>
                        <td>{stats['win_rate']:.1f}%</td>
                    </tr>
                """
            html_content += "</table></div>"
        
        html_content += """
        </body>
        </html>
        """
        
        # Save HTML report
        report_path = self.reports_dir / f"{self.date}_intraday_report.html"
        with open(report_path, 'w') as f:
            f.write(html_content)
        
        self.logger.info(f"📄 HTML report saved to {report_path}")
        return str(report_path)
    
    def generate_comprehensive_report(self) -> str:
        """Generate complete end-of-day report"""
        self.logger.info(f"📊 Generating comprehensive EOD report for {self.date}")
        
        # Get trade data
        trades_df = self.get_daily_trades()
        
        if trades_df.empty:
            self.logger.warning(f"⚠️ No completed trades found for {self.date}")
            return "No trades to report"
        
        # Calculate metrics
        metrics = self.calculate_performance_metrics(trades_df)
        strategy_stats = self.analyze_strategy_performance(trades_df)
        time_stats = self.analyze_time_patterns(trades_df)
        
        # Create visualizations
        self.create_performance_charts(trades_df, metrics)
        
        # Generate HTML report
        report_path = self.generate_html_report(trades_df, metrics, strategy_stats, time_stats)
        
        # Print summary to console
        print("=" * 60)
        print(f"📊 INTRADAY TRADING REPORT - {self.date}")
        print("=" * 60)
        print(f"📈 Total Trades: {metrics['total_trades']}")
        print(f"💰 Net PnL: ${metrics['total_pnl']:.2f}")
        print(f"📊 Win Rate: {metrics['win_rate']:.1f}%")
        print(f"💸 Total Costs: ${metrics['total_costs']:.2f}")
        print(f"📉 Cost Impact: {metrics['cost_impact_pct']:.2f}%")
        print(f"📄 Report saved: {report_path}")
        print("=" * 60)
        
        return report_path

def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate EOD report for intraday trading')
    parser.add_argument('--date', type=str, help='Date for report (YYYY-MM-DD)')
    
    args = parser.parse_args()
    
    try:
        generator = IntradayEODReportGenerator(args.date)
        report_path = generator.generate_comprehensive_report()
        
        if report_path != "No trades to report":
            print(f"\n✅ Report generation completed successfully!")
            print(f"📄 Report location: {report_path}")
        else:
            print(f"\n⚠️ No trades found for the specified date")
            
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
