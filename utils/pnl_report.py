#!/usr/bin/env python3
"""
📈 PnL Report Generator - Comprehensive trading performance reports with graphs
Generates detailed end-of-day and historical performance reports
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import json
from typing import Dict, List, Optional
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from utils.pnl_tracker import get_pnl_tracker
from utils.logger import setup_scalping_loggers

# Set style for better-looking plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class PnLReportGenerator:
    """Generate comprehensive P&L reports with visualizations"""
    
    def __init__(self):
        """Initialize report generator"""
        self.loggers = setup_scalping_loggers()
        self.logger = self.loggers['pnl_report']
        self.pnl_tracker = get_pnl_tracker()
        
        # Report output directory
        self.reports_dir = Path(__file__).parent.parent / "reports"
        self.reports_dir.mkdir(exist_ok=True)
        
        self.logger.info("📈 PnL Report Generator initialized")
    
    def generate_session_report(self, session_summary: Dict = None) -> str:
        """Generate end-of-session comprehensive report"""
        try:
            if session_summary is None:
                session_summary = self.pnl_tracker.get_current_session_pnl()
            
            if not session_summary:
                self.logger.warning("⚠️ No session data available for report")
                return None
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = self.reports_dir / f"session_report_{timestamp}.html"
            
            # Get trade history for this session
            trade_history = self.pnl_tracker.get_trade_history(days=1)
            
            # Generate visualizations
            charts = self._generate_session_charts(session_summary, trade_history)
            
            # Generate HTML report
            html_content = self._generate_html_report(session_summary, trade_history, charts)
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Also save as PDF if possible
            pdf_path = self._save_as_pdf(report_path)
            
            self.logger.info(f"📊 Session report generated: {report_path}")
            return str(report_path)
            
        except Exception as e:
            self.logger.error(f"❌ Session report generation error: {e}")
            return None
    
    def _generate_session_charts(self, session_summary: Dict, trade_history: pd.DataFrame) -> Dict[str, str]:
        """Generate all charts for session report"""
        charts = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            # 1. Cumulative P&L Chart
            if not trade_history.empty:
                charts['cumulative_pnl'] = self._create_cumulative_pnl_chart(trade_history, timestamp)
            
            # 2. Trade Distribution Chart
            if not trade_history.empty:
                charts['trade_distribution'] = self._create_trade_distribution_chart(trade_history, timestamp)
            
            # 3. Strategy Performance Chart
            if not trade_history.empty:
                charts['strategy_performance'] = self._create_strategy_performance_chart(trade_history, timestamp)
            
            # 4. Win/Loss Analysis
            if not trade_history.empty:
                charts['win_loss_analysis'] = self._create_win_loss_chart(trade_history, timestamp)
            
            # 5. Hourly Performance
            if not trade_history.empty:
                charts['hourly_performance'] = self._create_hourly_performance_chart(trade_history, timestamp)
            
            # 6. Risk Metrics Dashboard
            charts['risk_dashboard'] = self._create_risk_dashboard(session_summary, timestamp)
            
        except Exception as e:
            self.logger.error(f"❌ Chart generation error: {e}")
        
        return charts
    
    def _create_cumulative_pnl_chart(self, trade_history: pd.DataFrame, timestamp: str) -> str:
        """Create cumulative P&L over time chart"""
        try:
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # Sort by entry time and calculate cumulative P&L
            df = trade_history.copy()
            df['entry_time'] = pd.to_datetime(df['entry_time'])
            df = df.sort_values('entry_time')
            df['cumulative_pnl'] = df['pnl'].cumsum()
            
            # Plot cumulative P&L
            ax.plot(df['entry_time'], df['cumulative_pnl'], linewidth=2, marker='o', markersize=4)
            ax.axhline(y=0, color='red', linestyle='--', alpha=0.7)
            
            # Fill areas
            ax.fill_between(df['entry_time'], df['cumulative_pnl'], 0, 
                           where=(df['cumulative_pnl'] >= 0), alpha=0.3, color='green', label='Profit')
            ax.fill_between(df['entry_time'], df['cumulative_pnl'], 0, 
                           where=(df['cumulative_pnl'] < 0), alpha=0.3, color='red', label='Loss')
            
            ax.set_title('Cumulative P&L Over Time', fontsize=16, fontweight='bold')
            ax.set_xlabel('Time')
            ax.set_ylabel('Cumulative P&L ($)')
            ax.grid(True, alpha=0.3)
            ax.legend()
            
            # Format x-axis
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
            plt.xticks(rotation=45)
            
            plt.tight_layout()
            
            chart_path = self.reports_dir / f"cumulative_pnl_{timestamp}.png"
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return str(chart_path)
            
        except Exception as e:
            self.logger.error(f"❌ Cumulative P&L chart error: {e}")
            return None
    
    def _create_trade_distribution_chart(self, trade_history: pd.DataFrame, timestamp: str) -> str:
        """Create trade P&L distribution histogram"""
        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # P&L Distribution Histogram
            profits = trade_history[trade_history['pnl'] > 0]['pnl']
            losses = trade_history[trade_history['pnl'] < 0]['pnl']
            
            ax1.hist(profits, bins=10, alpha=0.7, color='green', label=f'Profits ({len(profits)})')
            ax1.hist(losses, bins=10, alpha=0.7, color='red', label=f'Losses ({len(losses)})')
            ax1.axvline(x=0, color='black', linestyle='--', alpha=0.7)
            
            ax1.set_title('Trade P&L Distribution', fontsize=14, fontweight='bold')
            ax1.set_xlabel('P&L ($)')
            ax1.set_ylabel('Number of Trades')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Win/Loss Pie Chart
            win_count = len(profits)
            loss_count = len(losses)
            
            if win_count > 0 or loss_count > 0:
                sizes = [win_count, loss_count]
                labels = [f'Wins ({win_count})', f'Losses ({loss_count})']
                colors = ['green', 'red']
                
                ax2.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
                ax2.set_title('Win/Loss Ratio', fontsize=14, fontweight='bold')
            
            plt.tight_layout()
            
            chart_path = self.reports_dir / f"trade_distribution_{timestamp}.png"
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return str(chart_path)
            
        except Exception as e:
            self.logger.error(f"❌ Trade distribution chart error: {e}")
            return None
    
    def _create_strategy_performance_chart(self, trade_history: pd.DataFrame, timestamp: str) -> str:
        """Create strategy performance comparison chart"""
        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # Strategy P&L
            strategy_pnl = trade_history.groupby('strategy')['pnl'].sum().sort_values(ascending=False)
            colors = ['green' if x >= 0 else 'red' for x in strategy_pnl.values]
            
            bars1 = ax1.bar(strategy_pnl.index, strategy_pnl.values, color=colors, alpha=0.7)
            ax1.axhline(y=0, color='black', linestyle='-', alpha=0.8)
            ax1.set_title('Strategy P&L Performance', fontsize=14, fontweight='bold')
            ax1.set_xlabel('Strategy')
            ax1.set_ylabel('Total P&L ($)')
            ax1.grid(True, alpha=0.3)
            
            # Add value labels on bars
            for bar in bars1:
                height = bar.get_height()
                ax1.annotate(f'${height:.2f}',
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3),  # 3 points vertical offset
                            textcoords="offset points",
                            ha='center', va='bottom')
            
            # Strategy Trade Count
            strategy_counts = trade_history.groupby('strategy').size()
            ax2.bar(strategy_counts.index, strategy_counts.values, alpha=0.7)
            ax2.set_title('Trades per Strategy', fontsize=14, fontweight='bold')
            ax2.set_xlabel('Strategy')
            ax2.set_ylabel('Number of Trades')
            ax2.grid(True, alpha=0.3)
            
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            chart_path = self.reports_dir / f"strategy_performance_{timestamp}.png"
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return str(chart_path)
            
        except Exception as e:
            self.logger.error(f"❌ Strategy performance chart error: {e}")
            return None
    
    def _create_win_loss_chart(self, trade_history: pd.DataFrame, timestamp: str) -> str:
        """Create detailed win/loss analysis chart"""
        try:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
            
            # 1. Hold Time vs P&L
            df = trade_history.copy()
            df['hold_time_minutes'] = df['hold_time_seconds'] / 60
            
            colors = ['green' if x >= 0 else 'red' for x in df['pnl']]
            scatter = ax1.scatter(df['hold_time_minutes'], df['pnl'], c=colors, alpha=0.7)
            ax1.axhline(y=0, color='black', linestyle='--', alpha=0.7)
            ax1.set_title('Hold Time vs P&L', fontsize=12, fontweight='bold')
            ax1.set_xlabel('Hold Time (minutes)')
            ax1.set_ylabel('P&L ($)')
            ax1.grid(True, alpha=0.3)
            
            # 2. Entry Price vs P&L
            ax2.scatter(df['entry_price'], df['pnl'], c=colors, alpha=0.7)
            ax2.axhline(y=0, color='black', linestyle='--', alpha=0.7)
            ax2.set_title('Entry Price vs P&L', fontsize=12, fontweight='bold')
            ax2.set_xlabel('Entry Price ($)')
            ax2.set_ylabel('P&L ($)')
            ax2.grid(True, alpha=0.3)
            
            # 3. Confidence vs P&L
            if 'confidence' in df.columns:
                ax3.scatter(df['confidence'], df['pnl'], c=colors, alpha=0.7)
                ax3.axhline(y=0, color='black', linestyle='--', alpha=0.7)
                ax3.set_title('Signal Confidence vs P&L', fontsize=12, fontweight='bold')
                ax3.set_xlabel('Confidence')
                ax3.set_ylabel('P&L ($)')
                ax3.grid(True, alpha=0.3)
            
            # 4. Side Performance
            side_pnl = df.groupby('side')['pnl'].agg(['sum', 'count', 'mean'])
            x_pos = range(len(side_pnl.index))
            
            bars = ax4.bar(x_pos, side_pnl['sum'], alpha=0.7)
            ax4.set_title('Long vs Short Performance', fontsize=12, fontweight='bold')
            ax4.set_xlabel('Side')
            ax4.set_ylabel('Total P&L ($)')
            ax4.set_xticks(x_pos)
            ax4.set_xticklabels(side_pnl.index)
            ax4.grid(True, alpha=0.3)
            
            # Color bars based on performance
            for i, bar in enumerate(bars):
                if side_pnl['sum'].iloc[i] >= 0:
                    bar.set_color('green')
                else:
                    bar.set_color('red')
            
            plt.tight_layout()
            
            chart_path = self.reports_dir / f"win_loss_analysis_{timestamp}.png"
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return str(chart_path)
            
        except Exception as e:
            self.logger.error(f"❌ Win/loss analysis chart error: {e}")
            return None
    
    def _create_hourly_performance_chart(self, trade_history: pd.DataFrame, timestamp: str) -> str:
        """Create hourly performance breakdown"""
        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # Extract hour from entry time
            df = trade_history.copy()
            df['entry_time'] = pd.to_datetime(df['entry_time'])
            df['hour'] = df['entry_time'].dt.hour
            
            # Hourly P&L
            hourly_pnl = df.groupby('hour')['pnl'].sum()
            colors = ['green' if x >= 0 else 'red' for x in hourly_pnl.values]
            
            bars1 = ax1.bar(hourly_pnl.index, hourly_pnl.values, color=colors, alpha=0.7)
            ax1.axhline(y=0, color='black', linestyle='-', alpha=0.8)
            ax1.set_title('Hourly P&L Performance', fontsize=14, fontweight='bold')
            ax1.set_xlabel('Hour of Day')
            ax1.set_ylabel('Total P&L ($)')
            ax1.set_xticks(range(9, 16))  # Market hours
            ax1.grid(True, alpha=0.3)
            
            # Hourly Trade Count
            hourly_count = df.groupby('hour').size()
            ax2.bar(hourly_count.index, hourly_count.values, alpha=0.7, color='blue')
            ax2.set_title('Trades per Hour', fontsize=14, fontweight='bold')
            ax2.set_xlabel('Hour of Day')
            ax2.set_ylabel('Number of Trades')
            ax2.set_xticks(range(9, 16))  # Market hours
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            chart_path = self.reports_dir / f"hourly_performance_{timestamp}.png"
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return str(chart_path)
            
        except Exception as e:
            self.logger.error(f"❌ Hourly performance chart error: {e}")
            return None
    
    def _create_risk_dashboard(self, session_summary: Dict, timestamp: str) -> str:
        """Create risk metrics dashboard"""
        try:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
            
            # 1. Portfolio Value Gauge
            start_value = session_summary['start_balance']
            current_value = session_summary['current_balance']
            pnl_pct = ((current_value - start_value) / start_value * 100) if start_value > 0 else 0
            
            colors = ['red' if pnl_pct < 0 else 'green']
            ax1.bar(['Portfolio'], [abs(pnl_pct)], color=colors, alpha=0.7)
            ax1.set_title(f'Portfolio Performance: {pnl_pct:.2f}%', fontsize=12, fontweight='bold')
            ax1.set_ylabel('Percentage Change')
            ax1.grid(True, alpha=0.3)
            
            # 2. Risk Metrics Text Box
            risk_text = f"""
Risk Metrics:
• Max Drawdown: ${session_summary['max_drawdown']:.2f}
• Best Trade: ${session_summary['best_trade']:.2f}
• Worst Trade: ${session_summary['worst_trade']:.2f}
• Avg Trade: ${session_summary['avg_trade']:.2f}
• Win Rate: {session_summary['win_rate']:.1f}%
• Total Trades: {session_summary['total_trades']}
            """
            
            ax2.text(0.1, 0.5, risk_text.strip(), transform=ax2.transAxes, 
                    fontsize=12, verticalalignment='center',
                    bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.5))
            ax2.set_xlim(0, 1)
            ax2.set_ylim(0, 1)
            ax2.axis('off')
            ax2.set_title('Risk Summary', fontsize=12, fontweight='bold')
            
            # 3. Daily Loss Limit Progress
            daily_loss_limit = start_value * 0.05  # 5% daily loss limit
            current_loss = max(0, start_value - current_value)
            loss_pct = (current_loss / daily_loss_limit * 100) if daily_loss_limit > 0 else 0
            
            ax3.barh(['Daily Loss Limit'], [min(100, loss_pct)], color='red', alpha=0.7)
            ax3.set_xlim(0, 100)
            ax3.set_title(f'Daily Loss Limit Usage: {loss_pct:.1f}%', fontsize=12, fontweight='bold')
            ax3.set_xlabel('Percentage of Limit Used')
            ax3.grid(True, alpha=0.3)
            
            # 4. Performance Score
            # Simple scoring: win_rate * avg_trade_size / max_drawdown
            if session_summary['max_drawdown'] > 0:
                score = (session_summary['win_rate'] * abs(session_summary['avg_trade'])) / session_summary['max_drawdown']
            else:
                score = session_summary['win_rate']
            
            score_color = 'green' if score > 50 else 'yellow' if score > 25 else 'red'
            ax4.pie([score, 100-score], labels=[f'Score: {score:.1f}', ''], 
                   colors=[score_color, 'lightgray'], startangle=90,
                   wedgeprops=dict(width=0.3))
            ax4.set_title('Performance Score', fontsize=12, fontweight='bold')
            
            plt.tight_layout()
            
            chart_path = self.reports_dir / f"risk_dashboard_{timestamp}.png"
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return str(chart_path)
            
        except Exception as e:
            self.logger.error(f"❌ Risk dashboard chart error: {e}")
            return None
    
    def _generate_html_report(self, session_summary: Dict, trade_history: pd.DataFrame, charts: Dict) -> str:
        """Generate comprehensive HTML report"""
        try:
            html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Scalping Bot - Trading Session Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .header {{ background-color: #2c3e50; color: white; padding: 20px; border-radius: 10px; }}
        .summary {{ background-color: white; padding: 20px; margin: 20px 0; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .metrics {{ display: flex; flex-wrap: wrap; gap: 20px; }}
        .metric {{ flex: 1; min-width: 200px; background-color: #ecf0f1; padding: 15px; border-radius: 5px; text-align: center; }}
        .metric.positive {{ background-color: #d5f4e6; }}
        .metric.negative {{ background-color: #ffeaa7; }}
        .chart {{ text-align: center; margin: 20px 0; }}
        .chart img {{ max-width: 100%; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .trades-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        .trades-table th, .trades-table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        .trades-table th {{ background-color: #f2f2f2; }}
        .profit {{ color: green; font-weight: bold; }}
        .loss {{ color: red; font-weight: bold; }}
        h1, h2 {{ color: #2c3e50; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Scalping Bot Trading Session Report</h1>
        <p><strong>Session:</strong> {session_id}</p>
        <p><strong>Date:</strong> {session_date}</p>
        <p><strong>Duration:</strong> {session_duration}</p>
        <p><strong>Generated:</strong> {generated_time}</p>
    </div>
    
    <div class="summary">
        <h2>📊 Performance Summary</h2>
        <div class="metrics">
            <div class="metric {total_pnl_class}">
                <h3>Total P&L</h3>
                <p style="font-size: 24px; margin: 0;">${total_pnl:.2f}</p>
                <p style="margin: 5px 0 0 0;">({pnl_percentage:.2f}%)</p>
            </div>
            <div class="metric">
                <h3>Total Trades</h3>
                <p style="font-size: 24px; margin: 0;">{total_trades}</p>
                <p style="margin: 5px 0 0 0;">W: {winning_trades} | L: {losing_trades}</p>
            </div>
            <div class="metric">
                <h3>Win Rate</h3>
                <p style="font-size: 24px; margin: 0;">{win_rate:.1f}%</p>
                <p style="margin: 5px 0 0 0;">Avg: ${avg_trade:.2f}</p>
            </div>
            <div class="metric">
                <h3>Max Drawdown</h3>
                <p style="font-size: 24px; margin: 0;">${max_drawdown:.2f}</p>
                <p style="margin: 5px 0 0 0;">Best: ${best_trade:.2f}</p>
            </div>
        </div>
    </div>
    
    {charts_html}
    
    <div class="summary">
        <h2>📋 Recent Trades</h2>
        {trades_table}
    </div>
    
    <div class="summary">
        <h2>⚙️ Configuration</h2>
        <p><strong>Portfolio Mode:</strong> Simulated ($2,000)</p>
        <p><strong>Risk Management:</strong> 5% daily loss limit, 2% per trade</p>
        <p><strong>Strategies:</strong> Momentum, Mean Reversion, VWAP Bounce</p>
        <p><strong>Timeframe:</strong> 1-minute scalping</p>
        <p><strong>Watchlist:</strong> IONQ</p>
    </div>
    
    <div style="text-align: center; margin-top: 30px; color: #7f8c8d;">
        <p>Generated by Scalping Bot System v1.0</p>
        <p>This report contains simulated trading data for analysis purposes only</p>
    </div>
</body>
</html>
            """
            
            # Prepare data for template
            pnl_percentage = ((session_summary['current_balance'] - session_summary['start_balance']) / session_summary['start_balance'] * 100) if session_summary['start_balance'] > 0 else 0
            total_pnl_class = 'positive' if session_summary['total_pnl'] >= 0 else 'negative'
            
            # Generate charts HTML
            charts_html = ""
            chart_titles = {
                'cumulative_pnl': '📈 Cumulative P&L Over Time',
                'trade_distribution': '📊 Trade Distribution Analysis',
                'strategy_performance': '🎯 Strategy Performance Comparison',
                'win_loss_analysis': '🔍 Win/Loss Analysis',
                'hourly_performance': '⏰ Hourly Performance Breakdown',
                'risk_dashboard': '⚠️ Risk Management Dashboard'
            }
            
            for chart_key, chart_path in charts.items():
                if chart_path and Path(chart_path).exists():
                    title = chart_titles.get(chart_key, chart_key.replace('_', ' ').title())
                    charts_html += f"""
                    <div class="summary">
                        <h2>{title}</h2>
                        <div class="chart">
                            <img src="file://{chart_path}" alt="{title}">
                        </div>
                    </div>
                    """
            
            # Generate trades table
            trades_table = ""
            if not trade_history.empty:
                trades_table = "<table class='trades-table'>"
                trades_table += "<tr><th>Time</th><th>Symbol</th><th>Strategy</th><th>Side</th><th>Quantity</th><th>Entry</th><th>Exit</th><th>P&L</th><th>Hold Time</th></tr>"
                
                for _, trade in trade_history.head(20).iterrows():  # Show last 20 trades
                    pnl_class = 'profit' if trade['pnl'] >= 0 else 'loss'
                    hold_time = f"{trade['hold_time_seconds']//60}m {trade['hold_time_seconds']%60}s" if pd.notna(trade['hold_time_seconds']) else 'N/A'
                    
                    trades_table += f"""
                    <tr>
                        <td>{pd.to_datetime(trade['entry_time']).strftime('%H:%M:%S')}</td>
                        <td>{trade['symbol']}</td>
                        <td>{trade['strategy']}</td>
                        <td>{trade['side']}</td>
                        <td>{trade['quantity']}</td>
                        <td>${trade['entry_price']:.2f}</td>
                        <td>${trade['exit_price']:.2f}</td>
                        <td class="{pnl_class}">${trade['pnl']:.2f}</td>
                        <td>{hold_time}</td>
                    </tr>
                    """
                trades_table += "</table>"
            else:
                trades_table = "<p>No completed trades in this session.</p>"
            
            # Fill template
            html_content = html_template.format(
                session_id=session_summary['session_id'],
                session_date=session_summary['session_date'],
                session_duration=session_summary['session_duration'],
                generated_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                total_pnl=session_summary['total_pnl'],
                pnl_percentage=pnl_percentage,
                total_pnl_class=total_pnl_class,
                total_trades=session_summary['total_trades'],
                winning_trades=session_summary['winning_trades'],
                losing_trades=session_summary['losing_trades'],
                win_rate=session_summary['win_rate'],
                avg_trade=session_summary['avg_trade'],
                max_drawdown=session_summary['max_drawdown'],
                best_trade=session_summary['best_trade'],
                charts_html=charts_html,
                trades_table=trades_table
            )
            
            return html_content
            
        except Exception as e:
            self.logger.error(f"❌ HTML report generation error: {e}")
            return "<html><body><h1>Error generating report</h1></body></html>"
    
    def _save_as_pdf(self, html_path: str) -> Optional[str]:
        """Save HTML report as PDF (if wkhtmltopdf is available)"""
        try:
            import pdfkit
            
            pdf_path = str(html_path).replace('.html', '.pdf')
            pdfkit.from_file(html_path, pdf_path)
            
            self.logger.info(f"📄 PDF report saved: {pdf_path}")
            return pdf_path
            
        except ImportError:
            self.logger.info("📄 PDF generation not available (install wkhtmltopdf and pdfkit)")
            return None
        except Exception as e:
            self.logger.error(f"❌ PDF generation error: {e}")
            return None

# Global report generator instance
report_generator = None

def get_report_generator() -> PnLReportGenerator:
    """Get or create global report generator instance"""
    global report_generator
    if report_generator is None:
        report_generator = PnLReportGenerator()
    return report_generator

if __name__ == "__main__":
    """Test the PnL report generator when run directly"""
    print("🧪 Testing PnL Report Generator...")
    
    try:
        # Check dependencies
        print("📦 Checking dependencies...")
        
        try:
            import matplotlib.pyplot as plt
            print("✅ matplotlib available")
        except ImportError:
            print("❌ matplotlib not available - install with: pip install matplotlib")
            
        try:
            import seaborn as sns
            print("✅ seaborn available")
        except ImportError:
            print("❌ seaborn not available - install with: pip install seaborn")
            
        try:
            import pandas as pd
            print("✅ pandas available")
        except ImportError:
            print("❌ pandas not available - install with: pip install pandas")
        
        # Initialize report generator
        print("\n📈 Initializing report generator...")
        generator = get_report_generator()
        print("✅ Report generator initialized successfully")
        
        # Check directories
        reports_dir = generator.reports_dir
        print(f"📁 Reports directory: {reports_dir}")
        
        if reports_dir.exists():
            print("✅ Reports directory exists")
        else:
            print("📁 Creating reports directory...")
            reports_dir.mkdir(exist_ok=True)
            print("✅ Reports directory created")
        
        # Test session summary
        print("\n📊 Testing session data...")
        summary = generator.pnl_tracker.get_current_session_pnl()
        print(f"✅ Session ID: {summary.get('session_id', 'Unknown')}")
        print(f"💰 Current P&L: ${summary.get('total_pnl', 0):,.2f}")
        
        print("\n✅ All tests passed! Report generator is ready.")
        print(f"📈 To generate a report, call: generator.generate_session_report()")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
