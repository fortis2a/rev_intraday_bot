#!/usr/bin/env python3
"""
Advanced Market Analysis Report - Enhanced for 8/20
Deep-dive analysis with position tracking, strategy performance, and risk assessment
"""

import json
import logging
import os
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database.trading_db import TradingDatabase


class AdvancedMarketAnalyzer:
    """Advanced market analysis with enhanced reporting for 8/20"""
    
    def __init__(self):
        self.db = TradingDatabase()
        self.report_dir = Path("reports")
        self.report_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def generate_advanced_report(self, target_date: date = None) -> str:
        """Generate advanced market analysis report for 8/20"""
        if target_date is None:
            target_date = date.today()
        
        self.logger.info(f"Generating advanced analysis for {target_date}")
        
        # Collect comprehensive data
        analysis_data = self._perform_comprehensive_analysis(target_date)
        
        # Generate enhanced HTML report
        html_content = self._generate_advanced_html(target_date, analysis_data)
        
        # Save report
        report_file = self.report_dir / f"advanced_analysis_{target_date.strftime('%Y%m%d')}.html"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.logger.info(f"Advanced analysis saved to: {report_file}")
        return str(report_file)
    
    def _perform_comprehensive_analysis(self, target_date: date) -> dict:
        """Perform comprehensive market analysis"""
        
        # Get today's data
        today_summary = self.db.get_daily_summary(target_date)
        today_activities = self.db.get_activities(target_date)
        
        # Position analysis
        position_analysis = self._analyze_positions(today_activities)
        
        # Strategy performance
        strategy_performance = self._analyze_strategy_performance(today_activities)
        
        # Risk assessment
        risk_assessment = self._assess_trading_risk(today_activities)
        
        # Time-based analysis
        time_analysis = self._analyze_time_patterns(today_activities)
        
        # Volume analysis
        volume_analysis = self._analyze_volume_patterns(today_activities)
        
        # P&L breakdown
        pnl_breakdown = self._detailed_pnl_breakdown(today_activities)
        
        return {
            'today_summary': today_summary,
            'today_activities': today_activities,
            'position_analysis': position_analysis,
            'strategy_performance': strategy_performance,
            'risk_assessment': risk_assessment,
            'time_analysis': time_analysis,
            'volume_analysis': volume_analysis,
            'pnl_breakdown': pnl_breakdown,
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def _analyze_positions(self, activities: pd.DataFrame) -> dict:
        """Analyze position management and lifecycle"""
        if activities.empty:
            return {}
        
        position_data = {}
        
        for symbol in activities['symbol'].unique():
            symbol_trades = activities[activities['symbol'] == symbol].copy()
            symbol_trades = symbol_trades.sort_values('transaction_time')
            
            # Track position changes
            position = 0
            max_position = 0
            min_position = 0
            position_changes = []
            
            for _, trade in symbol_trades.iterrows():
                if trade['side'] == 'buy':
                    position += trade['quantity']
                elif trade['side'] in ['sell', 'sell_short']:
                    position -= trade['quantity']
                
                position_changes.append({
                    'time': trade['transaction_time'],
                    'side': trade['side'],
                    'quantity': trade['quantity'],
                    'position': position,
                    'price': trade['price']
                })
                
                max_position = max(max_position, position)
                min_position = min(min_position, position)
            
            # Calculate metrics
            total_volume = symbol_trades['value'].sum()
            avg_price = symbol_trades['price'].mean()
            price_range = symbol_trades['price'].max() - symbol_trades['price'].min()
            
            # P&L calculation
            side_totals = symbol_trades.groupby('side')['value'].sum()
            sells = side_totals.get('sell', 0) + side_totals.get('sell_short', 0)
            buys = side_totals.get('buy', 0)
            symbol_pnl = sells - buys
            
            position_data[symbol] = {
                'total_trades': len(symbol_trades),
                'total_volume': total_volume,
                'net_pnl': symbol_pnl,
                'avg_price': avg_price,
                'price_range': price_range,
                'max_position': max_position,
                'min_position': min_position,
                'final_position': position,
                'position_changes': position_changes,
                'first_trade': symbol_trades.iloc[0]['transaction_time'],
                'last_trade': symbol_trades.iloc[-1]['transaction_time']
            }
        
        return position_data
    
    def _analyze_strategy_performance(self, activities: pd.DataFrame) -> dict:
        """Analyze strategy effectiveness"""
        if activities.empty:
            return {}
        
        # Group trades by hour to identify strategy patterns
        activities['hour'] = pd.to_datetime(activities['transaction_time']).dt.hour
        
        hourly_performance = {}
        for hour in activities['hour'].unique():
            hour_trades = activities[activities['hour'] == hour]
            
            # Calculate hourly P&L
            side_totals = hour_trades.groupby('side')['value'].sum()
            sells = side_totals.get('sell', 0) + side_totals.get('sell_short', 0)
            buys = side_totals.get('buy', 0)
            hour_pnl = sells - buys
            
            hourly_performance[hour] = {
                'trades': len(hour_trades),
                'volume': hour_trades['value'].sum(),
                'pnl': hour_pnl,
                'symbols': hour_trades['symbol'].nunique()
            }
        
        # Identify best/worst performing hours
        best_hour = max(hourly_performance.keys(), key=lambda h: hourly_performance[h]['pnl'])
        worst_hour = min(hourly_performance.keys(), key=lambda h: hourly_performance[h]['pnl'])
        
        return {
            'hourly_performance': hourly_performance,
            'best_hour': best_hour,
            'worst_hour': worst_hour,
            'total_trading_hours': len(hourly_performance)
        }
    
    def _assess_trading_risk(self, activities: pd.DataFrame) -> dict:
        """Assess trading risk metrics"""
        if activities.empty:
            return {}
        
        # Position size risk
        max_trade_value = activities['value'].max()
        avg_trade_value = activities['value'].mean()
        trade_value_std = activities['value'].std()
        
        # Concentration risk
        symbol_concentration = activities['symbol'].value_counts()
        max_symbol_trades = symbol_concentration.max()
        symbol_diversity = len(symbol_concentration)
        
        # Time concentration risk
        activities['hour'] = pd.to_datetime(activities['transaction_time']).dt.hour
        time_concentration = activities['hour'].value_counts()
        
        return {
            'max_trade_value': max_trade_value,
            'avg_trade_value': avg_trade_value,
            'trade_value_volatility': trade_value_std,
            'symbol_concentration_ratio': max_symbol_trades / len(activities),
            'symbol_diversity': symbol_diversity,
            'time_concentration': time_concentration.to_dict(),
            'risk_score': self._calculate_risk_score(activities)
        }
    
    def _calculate_risk_score(self, activities: pd.DataFrame) -> float:
        """Calculate overall risk score (0-100, lower is better)"""
        if activities.empty:
            return 0
        
        # Factors: concentration, volatility, position size
        symbol_concentration = activities['symbol'].value_counts().max() / len(activities)
        value_cv = activities['value'].std() / activities['value'].mean() if activities['value'].mean() > 0 else 0
        
        # Risk score (0-100)
        risk_score = (symbol_concentration * 40) + (min(value_cv, 1) * 60)
        return min(risk_score, 100)
    
    def _analyze_time_patterns(self, activities: pd.DataFrame) -> dict:
        """Analyze time-based trading patterns"""
        if activities.empty:
            return {}
        
        activities['hour'] = pd.to_datetime(activities['transaction_time']).dt.hour
        activities['minute'] = pd.to_datetime(activities['transaction_time']).dt.minute
        
        # Trading frequency by hour
        hourly_frequency = activities['hour'].value_counts().sort_index()
        
        # Identify trading sessions
        trading_start = activities['hour'].min()
        trading_end = activities['hour'].max()
        
        return {
            'trading_start_hour': trading_start,
            'trading_end_hour': trading_end,
            'total_trading_hours': trading_end - trading_start + 1,
            'hourly_frequency': hourly_frequency.to_dict(),
            'peak_trading_hour': hourly_frequency.idxmax(),
            'avg_trades_per_hour': len(activities) / len(hourly_frequency)
        }
    
    def _analyze_volume_patterns(self, activities: pd.DataFrame) -> dict:
        """Analyze volume patterns and distribution"""
        if activities.empty:
            return {}
        
        total_volume = activities['value'].sum()
        
        # Volume by symbol
        symbol_volumes = activities.groupby('symbol')['value'].sum().sort_values(ascending=False)
        
        # Volume by side
        side_volumes = activities.groupby('side')['value'].sum()
        
        # Volume distribution
        volume_quartiles = activities['value'].quantile([0.25, 0.5, 0.75])
        
        return {
            'total_volume': total_volume,
            'symbol_volumes': symbol_volumes.to_dict(),
            'side_volumes': side_volumes.to_dict(),
            'avg_trade_size': activities['value'].mean(),
            'volume_quartiles': volume_quartiles.to_dict(),
            'largest_trade': activities['value'].max(),
            'smallest_trade': activities['value'].min()
        }
    
    def _detailed_pnl_breakdown(self, activities: pd.DataFrame) -> dict:
        """Detailed P&L breakdown analysis"""
        if activities.empty:
            return {}
        
        # Overall P&L
        side_totals = activities.groupby('side')['value'].sum()
        total_buys = side_totals.get('buy', 0)
        total_sells = side_totals.get('sell', 0) + side_totals.get('sell_short', 0)
        net_pnl = total_sells - total_buys
        
        # P&L by symbol
        symbol_pnl = {}
        for symbol in activities['symbol'].unique():
            symbol_trades = activities[activities['symbol'] == symbol]
            symbol_side_totals = symbol_trades.groupby('side')['value'].sum()
            symbol_sells = symbol_side_totals.get('sell', 0) + symbol_side_totals.get('sell_short', 0)
            symbol_buys = symbol_side_totals.get('buy', 0)
            symbol_pnl[symbol] = symbol_sells - symbol_buys
        
        # P&L by hour
        activities['hour'] = pd.to_datetime(activities['transaction_time']).dt.hour
        hourly_pnl = {}
        for hour in activities['hour'].unique():
            hour_trades = activities[activities['hour'] == hour]
            hour_side_totals = hour_trades.groupby('side')['value'].sum()
            hour_sells = hour_side_totals.get('sell', 0) + hour_side_totals.get('sell_short', 0)
            hour_buys = hour_side_totals.get('buy', 0)
            hourly_pnl[hour] = hour_sells - hour_buys
        
        return {
            'net_pnl': net_pnl,
            'total_buys': total_buys,
            'total_sells': total_sells,
            'symbol_pnl': symbol_pnl,
            'hourly_pnl': hourly_pnl,
            'best_symbol': max(symbol_pnl.keys(), key=lambda k: symbol_pnl[k]) if symbol_pnl else None,
            'worst_symbol': min(symbol_pnl.keys(), key=lambda k: symbol_pnl[k]) if symbol_pnl else None
        }
    
    def _generate_advanced_html(self, target_date: date, data: dict) -> str:
        """Generate advanced HTML report"""
        
        date_str = target_date.strftime("%B %d, %Y")
        today = data.get('today_summary', {})
        positions = data.get('position_analysis', {})
        strategy = data.get('strategy_performance', {})
        risk = data.get('risk_assessment', {})
        time_analysis = data.get('time_analysis', {})
        volume = data.get('volume_analysis', {})
        pnl_breakdown = data.get('pnl_breakdown', {})
        
        # Today's metrics
        today_pnl = today.get('alpaca_pnl', today.get('cash_flow_pnl', 0))
        today_trades = today.get('total_trades', 0)
        today_volume = today.get('total_volume', 0)
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Advanced Market Analysis - {date_str}</title>
            <meta charset="UTF-8">
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{ 
                    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
                    background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
                    color: #ffffff;
                    line-height: 1.6;
                }}
                
                .header {{
                    background: linear-gradient(135deg, #2c3e50, #e74c3c, #f39c12);
                    padding: 30px;
                    text-align: center;
                    box-shadow: 0 6px 12px rgba(0,0,0,0.4);
                }}
                
                .header h1 {{
                    font-size: 3em;
                    margin-bottom: 15px;
                    text-shadow: 3px 3px 6px rgba(0,0,0,0.7);
                    background: linear-gradient(45deg, #ffffff, #ecf0f1);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                }}
                
                .container {{
                    max-width: 1600px;
                    margin: 0 auto;
                    padding: 30px;
                }}
                
                .analysis-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
                    gap: 30px;
                    margin-bottom: 40px;
                }}
                
                .analysis-card {{
                    background: rgba(44, 62, 80, 0.95);
                    border-radius: 20px;
                    padding: 30px;
                    box-shadow: 0 10px 20px rgba(0,0,0,0.4);
                    border: 2px solid transparent;
                    background-clip: padding-box;
                    position: relative;
                    overflow: hidden;
                }}
                
                .analysis-card::before {{
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    height: 6px;
                    background: linear-gradient(90deg, #3498db, #e74c3c, #f39c12, #27ae60);
                }}
                
                .card-title {{
                    font-size: 1.5em;
                    margin-bottom: 20px;
                    color: #3498db;
                    font-weight: 700;
                    display: flex;
                    align-items: center;
                }}
                
                .card-icon {{
                    font-size: 1.2em;
                    margin-right: 12px;
                }}
                
                .metric-row {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 12px 0;
                    border-bottom: 1px solid rgba(255,255,255,0.1);
                }}
                
                .metric-label {{
                    font-weight: 600;
                    color: #ecf0f1;
                }}
                
                .metric-value {{
                    font-weight: bold;
                    font-size: 1.1em;
                }}
                
                .positive {{ color: #27ae60; }}
                .negative {{ color: #e74c3c; }}
                .neutral {{ color: #95a5a6; }}
                .warning {{ color: #f39c12; }}
                
                .risk-indicator {{
                    display: inline-block;
                    padding: 6px 12px;
                    border-radius: 20px;
                    font-size: 0.85em;
                    font-weight: 600;
                    text-transform: uppercase;
                }}
                
                .risk-low {{ background: #27ae60; color: white; }}
                .risk-medium {{ background: #f39c12; color: white; }}
                .risk-high {{ background: #e74c3c; color: white; }}
                
                .chart-container {{
                    background: rgba(44, 62, 80, 0.95);
                    border-radius: 20px;
                    padding: 30px;
                    margin: 30px 0;
                    box-shadow: 0 10px 20px rgba(0,0,0,0.4);
                }}
                
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                    background: rgba(52, 73, 94, 0.6);
                    border-radius: 12px;
                    overflow: hidden;
                }}
                
                th {{
                    background: linear-gradient(135deg, #34495e, #2c3e50);
                    padding: 16px 12px;
                    color: #3498db;
                    font-weight: 700;
                    text-align: left;
                }}
                
                td {{
                    padding: 14px 12px;
                    border-bottom: 1px solid rgba(255,255,255,0.08);
                }}
                
                tr:hover {{
                    background: rgba(52, 152, 219, 0.15);
                }}
                
                .highlight-box {{
                    background: linear-gradient(135deg, rgba(52, 152, 219, 0.2), rgba(155, 89, 182, 0.2));
                    border: 2px solid rgba(52, 152, 219, 0.4);
                    border-radius: 15px;
                    padding: 25px;
                    margin: 25px 0;
                    text-align: center;
                }}
                
                .footer {{
                    text-align: center;
                    margin-top: 50px;
                    padding: 25px;
                    background: rgba(44, 62, 80, 0.8);
                    border-radius: 15px;
                    color: #95a5a6;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🔬 Advanced Market Analysis</h1>
                <p>{date_str} • Deep-dive Trading Performance Analysis • Generated: {data['generated_at']}</p>
            </div>
            
            <div class="container">
                <!-- Key Performance Summary -->
                <div class="highlight-box">
                    <h2 style="margin-bottom: 20px; color: #3498db;">📊 Executive Summary</h2>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px;">
                        <div>
                            <div style="font-size: 2.5em; font-weight: bold;" class="{'positive' if today_pnl > 0 else 'negative' if today_pnl < 0 else 'neutral'}">${today_pnl:.2f}</div>
                            <div style="color: #95a5a6;">Net P&L</div>
                        </div>
                        <div>
                            <div style="font-size: 2.5em; font-weight: bold;" class="neutral">{today_trades}</div>
                            <div style="color: #95a5a6;">Total Trades</div>
                        </div>
                        <div>
                            <div style="font-size: 2.5em; font-weight: bold;" class="neutral">${today_volume:,.0f}</div>
                            <div style="color: #95a5a6;">Total Volume</div>
                        </div>
                        <div>
                            <div style="font-size: 2.5em; font-weight: bold;" class="{'risk-low' if risk.get('risk_score', 50) < 30 else 'risk-medium' if risk.get('risk_score', 50) < 60 else 'risk-high'}">{risk.get('risk_score', 0):.0f}</div>
                            <div style="color: #95a5a6;">Risk Score</div>
                        </div>
                    </div>
                </div>
                
                <!-- Analysis Grid -->
                <div class="analysis-grid">
                    <!-- Position Analysis -->
                    <div class="analysis-card">
                        <div class="card-title">
                            <span class="card-icon">📍</span>
                            Position Analysis
                        </div>
                        {self._generate_position_analysis_content(positions)}
                    </div>
                    
                    <!-- Strategy Performance -->
                    <div class="analysis-card">
                        <div class="card-title">
                            <span class="card-icon">🎯</span>
                            Strategy Performance
                        </div>
                        {self._generate_strategy_content(strategy)}
                    </div>
                    
                    <!-- Risk Assessment -->
                    <div class="analysis-card">
                        <div class="card-title">
                            <span class="card-icon">🛡️</span>
                            Risk Assessment
                        </div>
                        {self._generate_risk_content(risk)}
                    </div>
                    
                    <!-- Time Patterns -->
                    <div class="analysis-card">
                        <div class="card-title">
                            <span class="card-icon">⏰</span>
                            Time Patterns
                        </div>
                        {self._generate_time_content(time_analysis)}
                    </div>
                    
                    <!-- Volume Analysis -->
                    <div class="analysis-card">
                        <div class="card-title">
                            <span class="card-icon">📊</span>
                            Volume Distribution
                        </div>
                        {self._generate_volume_content(volume)}
                    </div>
                    
                    <!-- P&L Breakdown -->
                    <div class="analysis-card">
                        <div class="card-title">
                            <span class="card-icon">💰</span>
                            P&L Breakdown
                        </div>
                        {self._generate_pnl_content(pnl_breakdown)}
                    </div>
                </div>
                
                <!-- Detailed Tables Section -->
                <div class="chart-container">
                    <div class="card-title">📋 Detailed Trading Activity</div>
                    {self._generate_detailed_activity_table(data.get('today_activities', pd.DataFrame()))}
                </div>
            </div>
            
            <div class="footer">
                <p>🔬 Advanced Market Analysis • 🤖 Scalping Bot System • 📊 Database-Powered Insights</p>
                <p>Generated: {data['generated_at']} • Report ID: ADV-{target_date.strftime('%Y%m%d')}</p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _generate_position_analysis_content(self, positions: dict) -> str:
        """Generate position analysis content"""
        if not positions:
            return '<p style="text-align: center; color: #95a5a6; font-style: italic;">No position data available</p>'
        
        html = ""
        for symbol, data in positions.items():
            final_pos_color = 'positive' if data['final_position'] > 0 else 'negative' if data['final_position'] < 0 else 'neutral'
            pnl_color = 'positive' if data['net_pnl'] > 0 else 'negative' if data['net_pnl'] < 0 else 'neutral'
            
            html += f"""
            <div style="margin-bottom: 20px; padding: 15px; background: rgba(52, 73, 94, 0.4); border-radius: 10px;">
                <h4 style="color: #3498db; margin-bottom: 10px;">{symbol}</h4>
                <div class="metric-row">
                    <span class="metric-label">Final Position:</span>
                    <span class="metric-value {final_pos_color}">{data['final_position']} shares</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Net P&L:</span>
                    <span class="metric-value {pnl_color}">${data['net_pnl']:.2f}</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Trades:</span>
                    <span class="metric-value neutral">{data['total_trades']}</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Avg Price:</span>
                    <span class="metric-value neutral">${data['avg_price']:.2f}</span>
                </div>
            </div>
            """
        
        return html
    
    def _generate_strategy_content(self, strategy: dict) -> str:
        """Generate strategy performance content"""
        if not strategy:
            return '<p style="text-align: center; color: #95a5a6; font-style: italic;">No strategy data available</p>'
        
        best_hour = strategy.get('best_hour')
        worst_hour = strategy.get('worst_hour')
        hourly_perf = strategy.get('hourly_performance', {})
        
        html = f"""
        <div class="metric-row">
            <span class="metric-label">Trading Hours:</span>
            <span class="metric-value neutral">{strategy.get('total_trading_hours', 0)}</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">Best Hour:</span>
            <span class="metric-value positive">{best_hour}:00 (${hourly_perf.get(best_hour, {}).get('pnl', 0):.2f})</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">Worst Hour:</span>
            <span class="metric-value negative">{worst_hour}:00 (${hourly_perf.get(worst_hour, {}).get('pnl', 0):.2f})</span>
        </div>
        """
        
        if hourly_perf:
            html += "<h4 style='margin-top: 20px; color: #3498db;'>Hourly Performance:</h4>"
            for hour in sorted(hourly_perf.keys()):
                perf = hourly_perf[hour]
                pnl_color = 'positive' if perf['pnl'] > 0 else 'negative' if perf['pnl'] < 0 else 'neutral'
                html += f"""
                <div style="display: flex; justify-content: space-between; padding: 5px 0; font-size: 0.9em;">
                    <span>{hour}:00</span>
                    <span class="{pnl_color}">${perf['pnl']:.2f} ({perf['trades']} trades)</span>
                </div>
                """
        
        return html
    
    def _generate_risk_content(self, risk: dict) -> str:
        """Generate risk assessment content"""
        if not risk:
            return '<p style="text-align: center; color: #95a5a6; font-style: italic;">No risk data available</p>'
        
        risk_score = risk.get('risk_score', 0)
        risk_level = 'Low' if risk_score < 30 else 'Medium' if risk_score < 60 else 'High'
        risk_class = 'risk-low' if risk_score < 30 else 'risk-medium' if risk_score < 60 else 'risk-high'
        
        html = f"""
        <div class="metric-row">
            <span class="metric-label">Risk Level:</span>
            <span class="risk-indicator {risk_class}">{risk_level}</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">Risk Score:</span>
            <span class="metric-value warning">{risk_score:.1f}/100</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">Max Trade:</span>
            <span class="metric-value neutral">${risk.get('max_trade_value', 0):,.2f}</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">Avg Trade:</span>
            <span class="metric-value neutral">${risk.get('avg_trade_value', 0):,.2f}</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">Symbol Diversity:</span>
            <span class="metric-value neutral">{risk.get('symbol_diversity', 0)} symbols</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">Concentration Ratio:</span>
            <span class="metric-value warning">{risk.get('symbol_concentration_ratio', 0):.1%}</span>
        </div>
        """
        
        return html
    
    def _generate_time_content(self, time_analysis: dict) -> str:
        """Generate time analysis content"""
        if not time_analysis:
            return '<p style="text-align: center; color: #95a5a6; font-style: italic;">No time data available</p>'
        
        html = f"""
        <div class="metric-row">
            <span class="metric-label">Trading Start:</span>
            <span class="metric-value neutral">{time_analysis.get('trading_start_hour', 0)}:00</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">Trading End:</span>
            <span class="metric-value neutral">{time_analysis.get('trading_end_hour', 0)}:00</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">Peak Hour:</span>
            <span class="metric-value positive">{time_analysis.get('peak_trading_hour', 0)}:00</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">Avg Trades/Hour:</span>
            <span class="metric-value neutral">{time_analysis.get('avg_trades_per_hour', 0):.1f}</span>
        </div>
        """
        
        return html
    
    def _generate_volume_content(self, volume: dict) -> str:
        """Generate volume analysis content"""
        if not volume:
            return '<p style="text-align: center; color: #95a5a6; font-style: italic;">No volume data available</p>'
        
        symbol_volumes = volume.get('symbol_volumes', {})
        
        html = f"""
        <div class="metric-row">
            <span class="metric-label">Total Volume:</span>
            <span class="metric-value neutral">${volume.get('total_volume', 0):,.2f}</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">Avg Trade Size:</span>
            <span class="metric-value neutral">${volume.get('avg_trade_size', 0):.2f}</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">Largest Trade:</span>
            <span class="metric-value warning">${volume.get('largest_trade', 0):.2f}</span>
        </div>
        """
        
        if symbol_volumes:
            html += "<h4 style='margin-top: 20px; color: #3498db;'>Volume by Symbol:</h4>"
            for symbol, vol in list(symbol_volumes.items())[:5]:  # Top 5
                html += f"""
                <div style="display: flex; justify-content: space-between; padding: 5px 0; font-size: 0.9em;">
                    <span>{symbol}</span>
                    <span>${vol:,.2f}</span>
                </div>
                """
        
        return html
    
    def _generate_pnl_content(self, pnl_breakdown: dict) -> str:
        """Generate P&L breakdown content"""
        if not pnl_breakdown:
            return '<p style="text-align: center; color: #95a5a6; font-style: italic;">No P&L data available</p>'
        
        net_pnl = pnl_breakdown.get('net_pnl', 0)
        pnl_color = 'positive' if net_pnl > 0 else 'negative' if net_pnl < 0 else 'neutral'
        
        html = f"""
        <div class="metric-row">
            <span class="metric-label">Net P&L:</span>
            <span class="metric-value {pnl_color}">${net_pnl:.2f}</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">Total Buys:</span>
            <span class="metric-value neutral">${pnl_breakdown.get('total_buys', 0):,.2f}</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">Total Sells:</span>
            <span class="metric-value neutral">${pnl_breakdown.get('total_sells', 0):,.2f}</span>
        </div>
        """
        
        symbol_pnl = pnl_breakdown.get('symbol_pnl', {})
        if symbol_pnl:
            html += "<h4 style='margin-top: 20px; color: #3498db;'>P&L by Symbol:</h4>"
            for symbol in sorted(symbol_pnl.keys()):
                pnl = symbol_pnl[symbol]
                pnl_color = 'positive' if pnl > 0 else 'negative' if pnl < 0 else 'neutral'
                html += f"""
                <div style="display: flex; justify-content: space-between; padding: 5px 0; font-size: 0.9em;">
                    <span>{symbol}</span>
                    <span class="{pnl_color}">${pnl:.2f}</span>
                </div>
                """
        
        return html
    
    def _generate_detailed_activity_table(self, activities: pd.DataFrame) -> str:
        """Generate detailed activity table"""
        if activities.empty:
            return '<p style="text-align: center; color: #95a5a6; font-style: italic;">No trading activity data available</p>'
        
        # Get recent trades (last 20)
        recent_trades = activities.tail(20)
        
        html = '''
        <table>
            <tr>
                <th>Time</th>
                <th>Symbol</th>
                <th>Side</th>
                <th>Quantity</th>
                <th>Price</th>
                <th>Value</th>
            </tr>
        '''
        
        for _, trade in recent_trades.iterrows():
            timestamp = pd.to_datetime(trade['transaction_time'])
            time_str = timestamp.strftime('%H:%M:%S')
            
            side_icon = {
                'buy': '🛒 BUY',
                'sell': '💰 SELL',
                'sell_short': '💰 SHORT'
            }.get(trade['side'], trade['side'])
            
            side_color = 'negative' if trade['side'] == 'buy' else 'positive'
            
            html += f'''
            <tr>
                <td>{time_str}</td>
                <td style="font-weight: bold; color: #3498db;">{trade['symbol']}</td>
                <td class="{side_color}">{side_icon}</td>
                <td style="text-align: right;">{trade['quantity']}</td>
                <td style="text-align: right;">${trade['price']:.2f}</td>
                <td style="text-align: right;">${trade['value']:.2f}</td>
            </tr>
            '''
        
        html += '</table>'
        return html

def main():
    """Generate advanced market analysis report"""
    try:
        analyzer = AdvancedMarketAnalyzer()
        report_file = analyzer.generate_advanced_report()
        print(f"✅ Advanced analysis report: {report_file}")
        return report_file
        
    except Exception as e:
        print(f"❌ Error generating advanced analysis: {str(e)}")
        return None

if __name__ == "__main__":
    main()
