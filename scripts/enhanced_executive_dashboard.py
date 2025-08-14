#!/usr/bin/env python3
"""
Enhanced Executive Dashboard Generator
Creates a focused executive summary chart with clear, intuitive visualizations
"""

import sys
import os
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.patches as mpatches

# Add the parent directory to sys.path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.data_manager import DataManager
from utils.logger import setup_logger

class EnhancedExecutiveDashboard:
    """Create enhanced executive summary dashboard with clearer visualizations"""
    
    def __init__(self):
        self.logger = setup_logger("EnhancedExecutiveDashboard")
        self.data_manager = DataManager()
        self.api = self.data_manager.api
        
        # Set up professional styling
        plt.style.use('seaborn-v0_8-whitegrid')
        plt.rcParams.update({
            'figure.facecolor': 'white',
            'axes.facecolor': 'white',
            'axes.edgecolor': 'black',
            'axes.linewidth': 1.5,
            'grid.alpha': 0.3,
            'font.size': 11,
            'axes.titlesize': 14,
            'axes.labelsize': 12,
            'xtick.labelsize': 10,
            'ytick.labelsize': 10,
            'legend.fontsize': 10,
            'figure.titlesize': 18
        })
    
    def get_trading_summary(self):
        """Get summarized trading data excluding August 12th trades"""
        try:
            from datetime import datetime, date, timedelta
            
            # Define the date to exclude (August 12, 2025)
            exclude_date = date(2025, 8, 12)
            
            # Get orders from the last 5 days instead of just today
            start_date = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
            print(f"📅 Getting orders from {start_date} to now")
            
            orders = self.api.list_orders(
                status='all',
                limit=500,
                nested=False,
                after=start_date
            )
            
            if not orders:
                return None
            
            # Filter out orders from August 12th
            filtered_orders = []
            excluded_count = 0
            for order in orders:
                if hasattr(order, 'filled_at') and order.filled_at:
                    order_date = order.filled_at.date()
                    if order_date != exclude_date:
                        filtered_orders.append(order)
                    else:
                        excluded_count += 1
                        filtered_orders.append(order)
            
            print(f"🔍 Total orders retrieved: {len(orders)}")
            print(f"❌ Excluded {excluded_count} orders from August 12th")
            print(f"📅 Orders after excluding August 12th: {len(filtered_orders)}")
            
            # Get account info
            account = self.api.get_account()
            portfolio_history = self.api.get_portfolio_history(
                period='1D',
                timeframe='1Min'
            )
            
            daily_pnl = float(portfolio_history.equity[-1]) - float(portfolio_history.equity[0]) if len(portfolio_history.equity) > 1 else 0
            
            # Process filtered orders by symbol
            symbol_data = {}
            total_trades = 0
            total_volume = 0
            total_pnl = 0
            
            for order in filtered_orders:
                if hasattr(order, 'filled_at') and order.filled_at:
                    symbol = order.symbol
                    qty = int(order.filled_qty) if order.filled_qty else 0
                    price = float(order.filled_avg_price) if order.filled_avg_price else 0
                    
                    if symbol not in symbol_data:
                        symbol_data[symbol] = {'buys': [], 'sells': [], 'pnl': 0, 'trades': 0}
                    
                    if order.side == 'buy':
                        symbol_data[symbol]['buys'].append({'qty': qty, 'price': price})
                    else:
                        symbol_data[symbol]['sells'].append({'qty': qty, 'price': price})
                    
                    symbol_data[symbol]['trades'] += 1
                    total_trades += 1
                    total_volume += qty * price
            
            # Calculate P&L for each symbol using FIFO
            summary = {}
            for symbol, data in symbol_data.items():
                buys = data['buys'].copy()
                sells = data['sells'].copy()
                pnl = 0
                
                for sell in sells:
                    remaining_sell_qty = sell['qty']
                    while remaining_sell_qty > 0 and buys:
                        buy = buys[0]
                        if buy['qty'] <= remaining_sell_qty:
                            pnl += buy['qty'] * (sell['price'] - buy['price'])
                            remaining_sell_qty -= buy['qty']
                            buys.pop(0)
                        else:
                            pnl += remaining_sell_qty * (sell['price'] - buy['price'])
                            buy['qty'] -= remaining_sell_qty
                            remaining_sell_qty = 0
                
                symbol_data[symbol]['pnl'] = pnl
                total_pnl += pnl
                summary[symbol] = {
                    'pnl': pnl,
                    'trades': data['trades']
                }
            
            return {
                'symbols': summary,
                'total_pnl': total_pnl,
                'total_trades': total_trades,
                'total_volume': total_volume,
                'account_pnl': daily_pnl,
                'equity': float(account.equity)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting trading summary: {e}")
            return None
    
    def create_performance_score_explanation(self, score, daily_pnl):
        """Create a clear explanation of how the performance score is calculated"""
        explanation = f"""
PERFORMANCE SCORE EXPLANATION:

Your Score: {score:.0f}/100

How It's Calculated:
* Based on daily P&L performance
* Score = (Daily P&L + $50) × 2 (normalized)
* Range: 0-100 points

Your Performance:
* Daily P&L: ${daily_pnl:+.2f}
* Break-even point: $0.00 (Score: 100)
* Excellent day: +$25+ (Score: 150+ capped at 100)
* Poor day: -$25+ (Score: 0)

Color Zones:
* Red (0-33): Significant Loss Day
* Yellow (34-66): Break-even/Small Loss
* Green (67-100): Profitable Day
        """
        return explanation
    
    def create_stock_order_explanation(self, symbols, data):
        """Create a clear explanation of the stock order chart"""
        explanation = f"""
STOCK ORDER CHART EXPLANATION:

What This Shows:
* How your P&L builds up throughout the day
* Each point = after trading each stock
* Line shows cumulative (running total) profit/loss

Your Trading Sequence:
"""
        
        running_total = 0
        for i, symbol in enumerate(symbols, 1):
            stock_pnl = data['symbols'][symbol]['pnl']
            running_total += stock_pnl
            explanation += f"   {i}. {symbol}: ${stock_pnl:+.2f} -> Total: ${running_total:+.2f}\n"
        
        explanation += f"""
Key Insights:
* Final P&L: ${running_total:+.2f}
* Best performing stock: {max(symbols, key=lambda s: data['symbols'][s]['pnl'])}
* Worst performing stock: {min(symbols, key=lambda s: data['symbols'][s]['pnl'])}
* Trading momentum: {'Improving' if running_total > 0 else 'Declining'}
        """
        
        return explanation

    def create_enhanced_dashboard(self, output_dir='reports/daily'):
        """Create enhanced executive summary dashboard with clear explanations"""
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            # Get data
            data = self.get_trading_summary()
            if not data:
                print("Unable to retrieve trading data")
                return None
            
            symbols = list(data['symbols'].keys())
            
            # Create enhanced dashboard figure
            fig = plt.figure(figsize=(20, 14))
            fig.suptitle('ENHANCED Executive Trading Dashboard - Clear Performance Insights', 
                        fontsize=20, fontweight='bold', y=0.96)
            
            # Add date and account info
            date_str = datetime.now().strftime('%B %d, %Y')
            account_info = f"Date: {date_str} | Account Equity: ${data['equity']:,.2f} | Daily P&L: ${data['account_pnl']:+,.2f}"
            fig.text(0.5, 0.93, account_info, ha='center', fontsize=14, 
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='lightblue', alpha=0.8))
            
            # 1. Stock P&L Overview (Top Left)
            ax1 = plt.subplot(3, 4, (1, 2))
            
            if symbols:
                pnls = [data['symbols'][symbol]['pnl'] for symbol in symbols]
                colors = ['#2E8B57' if pnl > 0 else '#DC143C' for pnl in pnls]
                
                bars = plt.bar(symbols, pnls, color=colors, edgecolor='black', linewidth=1.5)
                
                # Add value labels on bars
                for bar, pnl in zip(bars, pnls):
                    height = bar.get_height()
                    plt.text(bar.get_x() + bar.get_width()/2., height + (0.5 if height > 0 else -1.5),
                            f'${pnl:.2f}', ha='center', va='bottom' if height > 0 else 'top', 
                            fontweight='bold', fontsize=11)
                
                plt.title('Stock Performance Breakdown', fontsize=16, fontweight='bold', pad=20)
                plt.xlabel('Stock Symbol', fontweight='bold', fontsize=12)
                plt.ylabel('Profit/Loss ($)', fontweight='bold', fontsize=12)
                plt.axhline(y=0, color='black', linestyle='-', alpha=0.8)
                plt.grid(True, alpha=0.3)
                plt.xticks(rotation=45)
            
            # 2. Trade Distribution (Top Right)
            ax2 = plt.subplot(3, 4, (3, 4))
            
            if symbols:
                trade_counts = [data['symbols'][symbol]['trades'] for symbol in symbols]
                colors_pie = plt.cm.Set3(np.linspace(0, 1, len(symbols)))
                
                wedges, texts, autotexts = plt.pie(trade_counts, labels=symbols, autopct='%1.0f%%',
                                                  colors=colors_pie, startangle=90, 
                                                  explode=[0.05]*len(symbols))
                
                # Enhance text
                for text in texts:
                    text.set_fontsize(11)
                    text.set_fontweight('bold')
                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontweight('bold')
                    autotext.set_fontsize(10)
                
                plt.title('Trade Distribution by Stock', fontsize=16, fontweight='bold', pad=20)
            
            # 3. Enhanced Performance Gauge (Middle Left)
            ax3 = plt.subplot(3, 4, (5, 6))
            
            # Calculate performance score with better logic
            daily_pnl = data['account_pnl']
            # Normalize score: -$50 = 0, $0 = 50, +$50 = 100
            score = max(0, min(100, 50 + daily_pnl))
            
            # Create semicircle gauge
            theta = np.linspace(0, np.pi, 100)
            
            # Performance zones with clear boundaries
            zone1 = theta[theta <= np.pi/3]  # Red zone (0-33)
            zone2 = theta[(theta > np.pi/3) & (theta <= 2*np.pi/3)]  # Yellow zone (34-66)
            zone3 = theta[theta > 2*np.pi/3]  # Green zone (67-100)
            
            # Draw zones
            plt.fill_between(zone1, 0, 1, color='#FF4444', alpha=0.7, label='Poor (0-33)')
            plt.fill_between(zone2, 0, 1, color='#FFAA00', alpha=0.7, label='Average (34-66)')
            plt.fill_between(zone3, 0, 1, color='#44AA44', alpha=0.7, label='Good (67-100)')
            
            # Add zone labels
            plt.text(np.pi/6, 0.5, 'POOR', ha='center', va='center', fontweight='bold', fontsize=12, color='white')
            plt.text(np.pi/2, 0.5, 'AVERAGE', ha='center', va='center', fontweight='bold', fontsize=12, color='white')
            plt.text(5*np.pi/6, 0.5, 'GOOD', ha='center', va='center', fontweight='bold', fontsize=12, color='white')
            
            # Calculate needle position
            needle_angle = (score / 100) * np.pi
            
            # Draw needle with better styling
            needle_x = 0.9 * np.cos(needle_angle)
            needle_y = 0.9 * np.sin(needle_angle)
            plt.arrow(0, 0, needle_x, needle_y, head_width=0.08, head_length=0.12, 
                     fc='black', ec='black', linewidth=4, zorder=10)
            
            # Add center circle
            circle = plt.Circle((0, 0), 0.1, color='black', zorder=11)
            plt.gca().add_patch(circle)
            
            # Styling
            plt.xlim(-1.3, 1.3)
            plt.ylim(-0.3, 1.3)
            plt.axis('off')
            plt.title('PERFORMANCE GAUGE (Clearer Version)', fontsize=16, fontweight='bold', pad=20)
            
            # Score display with explanation
            score_text = f'Score: {score:.0f}/100\nDaily P&L: ${daily_pnl:+.2f}'
            plt.text(0, -0.2, score_text, ha='center', va='center', fontsize=14, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgray', alpha=0.8))
            
            # 4. Stock Performance Matrix (Middle Right)
            ax4 = plt.subplot(3, 4, (7, 8))
            
            if symbols:
                # Create enhanced comparison table
                table_data = []
                for symbol in symbols:
                    pnl = data['symbols'][symbol]['pnl']
                    trades = data['symbols'][symbol]['trades']
                    avg_pnl = pnl / trades if trades > 0 else 0
                    status = 'PROFIT' if pnl > 0 else 'LOSS' if pnl < 0 else 'BREAK-EVEN'
                    table_data.append([symbol, f'${pnl:+.2f}', trades, f'${avg_pnl:+.2f}', status])
                
                table = plt.table(cellText=table_data,
                                 colLabels=['Stock', 'Total P&L', 'Trades', 'Avg/Trade', 'Status'],
                                 cellLoc='center',
                                 loc='center',
                                 bbox=[0, 0, 1, 1])
                
                table.auto_set_font_size(False)
                table.set_fontsize(10)
                table.scale(1, 2.2)
                
                # Enhanced color coding
                for i in range(1, len(table_data) + 1):
                    pnl = data['symbols'][symbols[i-1]]['pnl']
                    if pnl > 0:
                        color = '#90EE90'  # Light green
                    elif pnl < 0:
                        color = '#FFB6C1'  # Light red
                    else:
                        color = '#FFFFE0'  # Light yellow
                    
                    table[(i, 1)].set_facecolor(color)  # P&L column
                    table[(i, 4)].set_facecolor(color)  # Status column
                
                plt.axis('off')
                plt.title('ENHANCED Stock Performance Matrix', fontsize=16, fontweight='bold', pad=20)
            
            # 5. Enhanced Stock Order Timeline (Bottom Left)
            ax5 = plt.subplot(3, 4, (9, 10))
            
            if symbols:
                # Calculate cumulative P&L step by step
                cumulative_pnl = []
                running_total = 0
                step_labels = []
                
                for i, symbol in enumerate(symbols):
                    running_total += data['symbols'][symbol]['pnl']
                    cumulative_pnl.append(running_total)
                    step_labels.append(f"{i+1}.\n{symbol}")
                
                x_pos = range(len(symbols))
                
                # Enhanced line plot
                plt.plot(x_pos, cumulative_pnl, marker='o', linewidth=4, markersize=10, 
                        color='#1f77b4', markerfacecolor='white', markeredgecolor='#1f77b4', 
                        markeredgewidth=3, label='Cumulative P&L')
                
                # Add step-by-step annotations
                for i, (x, y) in enumerate(zip(x_pos, cumulative_pnl)):
                    step_pnl = data['symbols'][symbols[i]]['pnl']
                    plt.annotate(f'${step_pnl:+.2f}', xy=(x, y), xytext=(0, 15), 
                               textcoords='offset points', ha='center', va='bottom',
                               fontweight='bold', fontsize=9,
                               bbox=dict(boxstyle='round,pad=0.3', 
                                       facecolor='green' if step_pnl > 0 else 'red', 
                                       alpha=0.7, edgecolor='black'),
                               color='white')
                
                # Fill area with gradient effect
                plt.fill_between(x_pos, cumulative_pnl, 0, alpha=0.3, 
                               color='green' if cumulative_pnl[-1] > 0 else 'red',
                               label=f'Final: ${cumulative_pnl[-1]:+.2f}')
                
                # Zero line
                plt.axhline(y=0, color='black', linestyle='--', alpha=0.8, linewidth=2)
                
                plt.title('TRADING ORDER TIMELINE (Step-by-Step P&L)', fontsize=16, fontweight='bold', pad=20)
                plt.xlabel('Trading Sequence (Order of Execution)', fontweight='bold', fontsize=12)
                plt.ylabel('Cumulative P&L ($)', fontweight='bold', fontsize=12)
                plt.xticks(x_pos, step_labels, fontsize=10)
                plt.grid(True, alpha=0.3)
                plt.legend(loc='upper left')
                
                # Final result box
                final_text = f'FINAL RESULT: ${cumulative_pnl[-1]:+.2f}'
                plt.text(0.98, 0.98, final_text, transform=ax5.transAxes, 
                        ha='right', va='top', fontweight='bold', fontsize=12,
                        bbox=dict(boxstyle='round,pad=0.5', 
                                facecolor='green' if cumulative_pnl[-1] > 0 else 'red', 
                                alpha=0.8, edgecolor='black'),
                        color='white')
            
            # 6. Performance Explanation Panel (Bottom Right)
            ax6 = plt.subplot(3, 4, (11, 12))
            
            # Create detailed explanation
            explanation_text = f"""
DASHBOARD EXPLANATION:

PERFORMANCE GAUGE:
* Shows daily performance on 0-100 scale
* Red (0-33): Significant loss day
* Yellow (34-66): Break-even/small loss  
* Green (67-100): Profitable day
* Your score: {score:.0f} (Daily P&L: ${daily_pnl:+.2f})

STOCK ORDER TIMELINE:
* Shows how P&L builds throughout day
* Each point = after trading each stock
* Green annotations = profit on that stock
* Red annotations = loss on that stock
* Line shows running total

KEY METRICS:
* Total Stocks Traded: {len(symbols)}
* Total Trades: {data['total_trades']}
* Best Stock: {max(symbols, key=lambda s: data['symbols'][s]['pnl']) if symbols else 'N/A'}
* Worst Stock: {min(symbols, key=lambda s: data['symbols'][s]['pnl']) if symbols else 'N/A'}
* Win Rate: {len([s for s in symbols if data['symbols'][s]['pnl'] > 0])/len(symbols)*100:.0f}% if symbols else 0
            """
            
            plt.text(0.05, 0.95, explanation_text, transform=ax6.transAxes, fontsize=11,
                    verticalalignment='top', fontfamily='monospace',
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='lightblue', alpha=0.8))
            plt.axis('off')
            plt.title('CHART EXPLANATIONS', fontsize=16, fontweight='bold', pad=20)
            
            plt.tight_layout(rect=[0, 0.03, 1, 0.91])
            
            # Save enhanced dashboard
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            dashboard_path = os.path.join(output_dir, f'enhanced_executive_dashboard_{timestamp}.png')
            plt.savefig(dashboard_path, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
            # Create separate explanation document
            explanation_path = os.path.join(output_dir, f'dashboard_explanation_{timestamp}.txt')
            with open(explanation_path, 'w') as f:
                f.write(self.create_performance_score_explanation(score, daily_pnl))
                f.write("\n" + "="*50 + "\n")
                f.write(self.create_stock_order_explanation(symbols, data))
            
            return dashboard_path, explanation_path
            
        except Exception as e:
            self.logger.error(f"Error creating enhanced dashboard: {e}")
            return None, None

def main():
    """Main function"""
    try:
        dashboard = EnhancedExecutiveDashboard()
        
        print("Creating Enhanced Executive Dashboard with Clear Explanations...")
        dashboard_path, explanation_path = dashboard.create_enhanced_dashboard()
        
        if dashboard_path:
            print(f"Enhanced Executive Dashboard created: {dashboard_path}")
            if explanation_path:
                print(f"Detailed explanations saved: {explanation_path}")
        else:
            print("Failed to create dashboard")
            
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
