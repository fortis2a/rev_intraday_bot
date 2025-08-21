#!/usr/bin/env python3
"""
Enhanced Market Close Report Generator - Uses Database Cache
Generates comprehensive trading reports using cached database data
Scheduled to run at 4:30 PM after data collection at 4:15 PM
"""

import sys
import os
from pathlib import Path
from datetime import date, datetime, timedelta
import pandas as pd
import logging

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.trading_db import TradingDatabase

class DatabaseReportGenerator:
    """Generate trading reports using database cache"""
    
    def __init__(self):
        self.db = TradingDatabase()
        self.report_dir = Path("reports")
        self.report_dir.mkdir(exist_ok=True)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
    
    def generate_market_close_report(self, target_date: date = None) -> str:
        """Generate comprehensive market close report"""
        if target_date is None:
            target_date = date.today()
        
        self.logger.info(f"Generating market close report for {target_date}")
        
        # Get today's and yesterday's summaries
        today_summary = self.db.get_daily_summary(target_date)
        yesterday = target_date - timedelta(days=1)
        
        # Find last trading day for comparison
        while yesterday.weekday() >= 5:  # Skip weekends
            yesterday -= timedelta(days=1)
        
        yesterday_summary = self.db.get_daily_summary(yesterday)
        
        # Get detailed activities
        today_activities = self.db.get_activities(target_date)
        
        # Generate HTML report
        html_content = self._generate_html_report(
            target_date, today_summary, yesterday_summary, today_activities
        )
        
        # Save report
        report_file = self.report_dir / f"market_close_report_{target_date.strftime('%Y%m%d')}.html"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.logger.info(f"Report saved to: {report_file}")
        return str(report_file)
    
    def _generate_html_report(self, target_date: date, today: dict, yesterday: dict, activities: pd.DataFrame) -> str:
        """Generate HTML report content"""
        
        # Format date
        date_str = target_date.strftime("%B %d, %Y")
        
        # Today's metrics (use summary if available, otherwise calculate from activities)
        if today:
            today_trades = today['total_trades']
            today_cash_flow_pnl = today.get('cash_flow_pnl', today.get('net_pnl', 0))
            today_alpaca_pnl = today.get('alpaca_pnl', today_cash_flow_pnl)
            today_trading_pnl = today.get('trading_pnl', today_alpaca_pnl)  # Use Alpaca as fallback
            today_symbols = today['symbols_traded']
            today_unique_symbols = today['unique_symbols']
            today_volume = today['total_volume']
            today_positions_opened = today.get('positions_opened', 0)
            today_positions_closed = today.get('positions_closed', 0)
            today_day_trades = today.get('day_trades', 0)
        elif not activities.empty:
            today_trades = len(activities)
            # Calculate P&L from activities
            side_totals = activities.groupby('side')['value'].sum()
            sells = side_totals.get('sell', 0) + side_totals.get('sell_short', 0)
            buys = side_totals.get('buy', 0)
            today_cash_flow_pnl = sells - buys
            today_alpaca_pnl = today_cash_flow_pnl  # Fallback
            today_trading_pnl = today_cash_flow_pnl  # Fallback
            today_symbols = ', '.join(activities['symbol'].unique())
            today_unique_symbols = activities['symbol'].nunique()
            today_volume = activities['value'].sum()
            today_positions_opened = 0
            today_positions_closed = 0
            today_day_trades = 0
        else:
            today_trades = 0
            today_cash_flow_pnl = 0.0
            today_alpaca_pnl = 0.0
            today_trading_pnl = 0.0
            today_symbols = "No trading activity"
            today_unique_symbols = 0
            today_volume = 0.0
            today_positions_opened = 0
            today_positions_closed = 0
            today_day_trades = 0
        
        # Yesterday's metrics
        yesterday_cash_flow_pnl = yesterday.get('cash_flow_pnl', yesterday.get('net_pnl', 0)) if yesterday else 0.0
        yesterday_alpaca_pnl = yesterday.get('alpaca_pnl', yesterday_cash_flow_pnl) if yesterday else 0.0
        yesterday_trading_pnl = yesterday.get('trading_pnl', yesterday_alpaca_pnl) if yesterday else 0.0
        yesterday_trades = yesterday['total_trades'] if yesterday else 0
        
        # P&L comparison (use Alpaca P&L as primary - source of truth)
        pnl_change = today_alpaca_pnl - yesterday_alpaca_pnl
        pnl_trend = "📈" if pnl_change > 0 else "📉" if pnl_change < 0 else "➡️"
        
        # Performance metrics
        if today_trades > 0:
            avg_pnl_per_trade = today_alpaca_pnl / today_trades  # Use Alpaca P&L
        else:
            avg_pnl_per_trade = 0.0
        
        # Symbol breakdown
        symbol_breakdown = ""
        if not activities.empty:
            symbol_stats = activities.groupby('symbol').agg({
                'id': 'count',
                'value': 'sum'
            }).rename(columns={'id': 'trades', 'value': 'volume'})
            
            # Calculate P&L per symbol
            symbol_pnl = {}
            for symbol in activities['symbol'].unique():
                symbol_data = activities[activities['symbol'] == symbol]
                side_totals = symbol_data.groupby('side')['value'].sum()
                sells = side_totals.get('sell', 0) + side_totals.get('sell_short', 0)
                buys = side_totals.get('buy', 0)
                symbol_pnl[symbol] = sells - buys
            
            for symbol in symbol_stats.index:
                trades = symbol_stats.loc[symbol, 'trades']
                volume = symbol_stats.loc[symbol, 'volume']
                pnl = symbol_pnl[symbol]
                pnl_color = "green" if pnl > 0 else "red" if pnl < 0 else "gray"
                
                symbol_breakdown += f"""
                <tr>
                    <td style="padding: 8px; border: 1px solid #444;">{symbol}</td>
                    <td style="padding: 8px; border: 1px solid #444; text-align: center;">{trades}</td>
                    <td style="padding: 8px; border: 1px solid #444; text-align: right;">${volume:,.2f}</td>
                    <td style="padding: 8px; border: 1px solid #444; text-align: right; color: {pnl_color}; font-weight: bold;">${pnl:,.2f}</td>
                </tr>
                """
        
        # Recent trades table
        recent_trades = ""
        if not activities.empty:
            # Sort by transaction time and get last 10 trades
            recent = activities.sort_values('transaction_time').tail(10)
            
            for _, trade in recent.iterrows():
                time_str = pd.to_datetime(trade['transaction_time']).strftime('%H:%M:%S')
                side_color = "green" if trade['side'] in ['sell', 'sell_short'] else "red"
                side_icon = "💰" if trade['side'] in ['sell', 'sell_short'] else "🛒"
                
                recent_trades += f"""
                <tr>
                    <td style="padding: 6px; border: 1px solid #444;">{time_str}</td>
                    <td style="padding: 6px; border: 1px solid #444; font-weight: bold;">{trade['symbol']}</td>
                    <td style="padding: 6px; border: 1px solid #444; color: {side_color};">{side_icon} {trade['side'].upper()}</td>
                    <td style="padding: 6px; border: 1px solid #444; text-align: right;">{trade['quantity']:.0f}</td>
                    <td style="padding: 6px; border: 1px solid #444; text-align: right;">${trade['price']:.2f}</td>
                    <td style="padding: 6px; border: 1px solid #444; text-align: right;">${trade['value']:.2f}</td>
                </tr>
                """
        
        # Generate HTML
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Market Close Report - {date_str}</title>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #1a1a1a; color: #ffffff; margin: 0; padding: 20px; }}
                .container {{ max-width: 1200px; margin: 0 auto; }}
                .header {{ text-align: center; margin-bottom: 30px; padding: 20px; background: linear-gradient(135deg, #2c3e50, #3498db); border-radius: 10px; }}
                .header h1 {{ margin: 0; font-size: 2.2em; text-shadow: 2px 2px 4px rgba(0,0,0,0.5); }}
                .header p {{ margin: 5px 0 0 0; font-size: 1.1em; opacity: 0.9; }}
                .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }}
                .metric-card {{ background: #2c3e50; padding: 20px; border-radius: 10px; text-align: center; border-left: 4px solid #3498db; }}
                .metric-card h3 {{ margin: 0 0 10px 0; color: #ecf0f1; font-size: 1.1em; }}
                .metric-card .value {{ font-size: 2em; font-weight: bold; margin: 10px 0; }}
                .positive {{ color: #27ae60; }}
                .negative {{ color: #e74c3c; }}
                .neutral {{ color: #95a5a6; }}
                .comparison-section {{ background: #34495e; padding: 20px; border-radius: 10px; margin-bottom: 30px; }}
                .comparison-section h2 {{ margin-top: 0; color: #3498db; }}
                .symbol-breakdown {{ background: #2c3e50; padding: 20px; border-radius: 10px; margin-bottom: 30px; }}
                .recent-trades {{ background: #2c3e50; padding: 20px; border-radius: 10px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
                th {{ background: #34495e; padding: 12px; border: 1px solid #444; color: #3498db; font-weight: bold; }}
                td {{ padding: 8px; border: 1px solid #444; }}
                .footer {{ text-align: center; margin-top: 30px; padding: 15px; background: #2c3e50; border-radius: 10px; font-size: 0.9em; color: #95a5a6; }}
                .data-source {{ background: #27ae60; color: white; padding: 5px 10px; border-radius: 5px; font-size: 0.8em; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 Market Close Report</h1>
                    <p>{date_str} • <span class="data-source">DATABASE CACHED</span></p>
                </div>
                
                <div class="metrics-grid">
                    <div class="metric-card">
                        <h3>💰 Alpaca P&L</h3>
                        <div class="value {'positive' if today_alpaca_pnl > 0 else 'negative' if today_alpaca_pnl < 0 else 'neutral'}">${today_alpaca_pnl:,.2f}</div>
                        <small style="color: #95a5a6;">✅ Includes fees & commissions</small>
                    </div>
                    <div class="metric-card">
                        <h3>📈 Total Trades</h3>
                        <div class="value neutral">{today_trades}</div>
                        <small style="color: #95a5a6;">Opened: {today_positions_opened} | Closed: {today_positions_closed}</small>
                    </div>
                    <div class="metric-card">
                        <h3>🎯 Symbols Traded</h3>
                        <div class="value neutral">{today_unique_symbols}</div>
                        <small style="color: #95a5a6;">Day Trades: {today_day_trades}</small>
                    </div>
                    <div class="metric-card">
                        <h3>📊 Average per Trade</h3>
                        <div class="value {'positive' if avg_pnl_per_trade > 0 else 'negative' if avg_pnl_per_trade < 0 else 'neutral'}">${avg_pnl_per_trade:,.2f}</div>
                        <small style="color: #95a5a6;">Cash Flow: ${today_cash_flow_pnl:,.2f}</small>
                    </div>
                </div>
                
                <div class="comparison-section">
                    <h2>{pnl_trend} Performance Comparison</h2>
                    <table>
                        <tr>
                            <th>Metric</th>
                            <th>Today</th>
                            <th>Yesterday</th>
                            <th>Change</th>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border: 1px solid #444; font-weight: bold;">Alpaca P&L</td>
                            <td style="padding: 8px; border: 1px solid #444; text-align: right; color: {'green' if today_alpaca_pnl > 0 else 'red' if today_alpaca_pnl < 0 else 'gray'}; font-weight: bold;">${today_alpaca_pnl:,.2f}</td>
                            <td style="padding: 8px; border: 1px solid #444; text-align: right; color: {'green' if yesterday_alpaca_pnl > 0 else 'red' if yesterday_alpaca_pnl < 0 else 'gray'};">${yesterday_alpaca_pnl:,.2f}</td>
                            <td style="padding: 8px; border: 1px solid #444; text-align: right; color: {'green' if pnl_change > 0 else 'red' if pnl_change < 0 else 'gray'}; font-weight: bold;">{'$' + f'{pnl_change:+,.2f}' if pnl_change != 0 else '$0.00'}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border: 1px solid #444; font-weight: bold;">Cash Flow</td>
                            <td style="padding: 8px; border: 1px solid #444; text-align: right; color: {'green' if today_cash_flow_pnl > 0 else 'red' if today_cash_flow_pnl < 0 else 'gray'};">${today_cash_flow_pnl:,.2f}</td>
                            <td style="padding: 8px; border: 1px solid #444; text-align: right; color: {'green' if yesterday_cash_flow_pnl > 0 else 'red' if yesterday_cash_flow_pnl < 0 else 'gray'};">${yesterday_cash_flow_pnl:,.2f}</td>
                            <td style="padding: 8px; border: 1px solid #444; text-align: right; color: gray;">-</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border: 1px solid #444; font-weight: bold;">Total Trades</td>
                            <td style="padding: 8px; border: 1px solid #444; text-align: right;">{today_trades}</td>
                            <td style="padding: 8px; border: 1px solid #444; text-align: right;">{yesterday_trades}</td>
                            <td style="padding: 8px; border: 1px solid #444; text-align: right; color: {'green' if (today_trades - yesterday_trades) > 0 else 'red' if (today_trades - yesterday_trades) < 0 else 'gray'};">{'+'if (today_trades - yesterday_trades) > 0 else ''}{today_trades - yesterday_trades}</td>
                        </tr>
                    </table>
                </div>
                
                <div class="symbol-breakdown">
                    <h2>🎯 Symbol Performance</h2>
                    <p><strong>Symbols:</strong> {today_symbols}</p>
                    {f'''
                    <table>
                        <tr>
                            <th>Symbol</th>
                            <th>Trades</th>
                            <th>Volume</th>
                            <th>P&L</th>
                        </tr>
                        {symbol_breakdown}
                    </table>
                    ''' if symbol_breakdown else '<p style="text-align: center; color: #95a5a6; font-style: italic;">No trading activity</p>'}
                </div>
                
                <div class="recent-trades">
                    <h2>⏰ Recent Trades</h2>
                    {f'''
                    <table>
                        <tr>
                            <th>Time</th>
                            <th>Symbol</th>
                            <th>Side</th>
                            <th>Quantity</th>
                            <th>Price</th>
                            <th>Value</th>
                        </tr>
                        {recent_trades}
                    </table>
                    ''' if recent_trades else '<p style="text-align: center; color: #95a5a6; font-style: italic;">No trades executed</p>'}
                </div>
                
                <div class="footer">
                    <p>📊 Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} • 🗄️ Database Cached Data • ⚡ Scalping Bot System</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def generate_weekly_summary(self) -> str:
        """Generate weekly performance summary"""
        end_date = date.today()
        start_date = end_date - timedelta(days=7)
        
        summaries = self.db.get_date_range_summaries(start_date, end_date)
        
        if summaries.empty:
            self.logger.info("No data available for weekly summary")
            return None
        
        # Calculate totals
        total_trades = summaries['total_trades'].sum()
        total_pnl = summaries['net_pnl'].sum()
        trading_days = len(summaries)
        
        # Generate simple weekly report
        report_file = self.report_dir / f"weekly_summary_{end_date.strftime('%Y%m%d')}.html"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Weekly Trading Summary</title>
            <style>
                body {{ font-family: Arial, sans-serif; background: #1a1a1a; color: #ffffff; padding: 20px; }}
                .container {{ max-width: 800px; margin: 0 auto; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ padding: 10px; border: 1px solid #444; text-align: right; }}
                th {{ background: #34495e; color: #3498db; }}
                .positive {{ color: #27ae60; }}
                .negative {{ color: #e74c3c; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📊 Weekly Trading Summary</h1>
                <p>Period: {start_date} to {end_date}</p>
                
                <h2>Overview</h2>
                <ul>
                    <li>Trading Days: {trading_days}</li>
                    <li>Total Trades: {total_trades}</li>
                    <li>Net P&L: <span class="{'positive' if total_pnl > 0 else 'negative'}">${total_pnl:,.2f}</span></li>
                    <li>Average per Day: ${total_pnl/trading_days if trading_days > 0 else 0:.2f}</li>
                </ul>
                
                <h2>Daily Breakdown</h2>
                <table>
                    <tr>
                        <th>Date</th>
                        <th>Trades</th>
                        <th>Symbols</th>
                        <th>Net P&L</th>
                    </tr>
        """
        
        for _, row in summaries.iterrows():
            pnl_class = "positive" if row['net_pnl'] > 0 else "negative" if row['net_pnl'] < 0 else ""
            html += f"""
                    <tr>
                        <td>{row['trade_date']}</td>
                        <td>{row['total_trades']}</td>
                        <td>{row['unique_symbols']}</td>
                        <td class="{pnl_class}">${row['net_pnl']:,.2f}</td>
                    </tr>
            """
        
        html += """
                </table>
            </div>
        </body>
        </html>
        """
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        self.logger.info(f"Weekly summary saved to: {report_file}")
        return str(report_file)

def main():
    """Main execution for scheduled report generation"""
    logger = logging.getLogger(__name__)
    
    try:
        # Generate reports
        generator = DatabaseReportGenerator()
        
        # Generate today's market close report
        today_report = generator.generate_market_close_report()
        print(f"✅ Market close report: {today_report}")
        
        # Generate weekly summary on Fridays
        if date.today().weekday() == 4:  # Friday
            weekly_report = generator.generate_weekly_summary()
            if weekly_report:
                print(f"✅ Weekly summary: {weekly_report}")
        
        return True
        
    except Exception as e:
        logger.error(f"🚨 Error generating reports: {str(e)}")
        return False

if __name__ == "__main__":
    print(f"📊 Generating Market Close Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success = main()
    
    if success:
        print("✅ Report generation completed successfully")
        sys.exit(0)
    else:
        print("❌ Report generation failed")
        sys.exit(1)
