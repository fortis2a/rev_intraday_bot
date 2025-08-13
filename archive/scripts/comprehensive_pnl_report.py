#!/usr/bin/env python3
"""
📊 Comprehensive P&L Report Generator with Graphs
Advanced trading analytics and visualization for scalping bot
"""

import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np
from typing import Dict, List, Optional, Tuple
import pytz

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from core.order_manager import OrderManager
from core.risk_manager import RiskManager
import warnings
warnings.filterwarnings('ignore')

class ComprehensivePnLReporter:
    """Advanced P&L reporting with graphs and detailed analytics"""
    
    def __init__(self):
        """Initialize the P&L reporter"""
        self.order_manager = OrderManager()
        self.risk_manager = RiskManager()
        self.et_timezone = pytz.timezone('US/Eastern')
        
    def generate_comprehensive_report(self, target_date: str = None, save_path: str = None) -> Dict:
        """Generate comprehensive P&L report with graphs"""
        try:
            # Default to today if no date specified
            if target_date is None:
                target_date = datetime.now(self.et_timezone).strftime('%Y-%m-%d')
            
            print(f"📊 Generating Comprehensive P&L Report for {target_date}...")
            
            # Initialize order manager connection
            if not self.order_manager.initialize_trading():
                print("❌ Failed to connect to broker")
                return {}
            
            # Get trade data
            trades_data = self._get_trades_data(target_date)
            
            if not trades_data:
                print(f"📭 No trades found for {target_date}")
                return self._generate_empty_report(target_date)
            
            # Create comprehensive analysis
            report = self._create_comprehensive_analysis(trades_data, target_date)
            
            # Generate visualizations
            if save_path is None:
                save_path = f"reports/pnl_report_{target_date.replace('-', '')}"
            
            self._create_visualizations(trades_data, report, save_path)
            
            # Print summary to console
            self._print_summary_report(report)
            
            return report
            
        except Exception as e:
            print(f"❌ Error generating P&L report: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def _get_trades_data(self, target_date: str) -> List[Dict]:
        """Extract detailed trade data from broker"""
        try:
            # Get all orders for the target date
            all_orders = self.order_manager.alpaca_trader.get_orders(status='all')
            
            if not all_orders:
                return []
            
            # Filter and process orders for target date
            daily_orders = []
            target_date_str = target_date
            
            for order in all_orders:
                order_date = None
                
                # Extract date from various timestamp fields
                for date_field in ['filled_at', 'created_at', 'submitted_at']:
                    if date_field in order and order[date_field]:
                        try:
                            if isinstance(order[date_field], str):
                                order_datetime = datetime.fromisoformat(order[date_field].replace('Z', '+00:00'))
                            else:
                                order_datetime = order[date_field]
                            order_date = order_datetime.strftime('%Y-%m-%d')
                            break
                        except:
                            continue
                
                # Include orders from target date that are filled
                if (order_date == target_date_str and 
                    order.get('status') == 'filled' and 
                    order.get('filled_avg_price') and 
                    float(order.get('filled_avg_price', 0)) > 0):
                    
                    # Convert to our format
                    trade_data = {
                        'order_id': order.get('id', ''),
                        'symbol': order.get('symbol', ''),
                        'side': order.get('side', ''),
                        'qty': float(order.get('qty', 0)),
                        'filled_price': float(order.get('filled_avg_price', 0)),
                        'filled_at': order.get('filled_at', ''),
                        'created_at': order.get('created_at', ''),
                        'submitted_at': order.get('submitted_at', ''),
                        'order_type': order.get('order_type', 'market'),
                        'time_in_force': order.get('time_in_force', 'day'),
                        'notional': float(order.get('notional', 0)) if order.get('notional') else 0
                    }
                    
                    # Parse timestamp for time analysis - use created_at if filled_at is not available
                    timestamp_to_use = trade_data['filled_at'] or trade_data['created_at'] or trade_data['submitted_at']
                    if timestamp_to_use:
                        try:
                            if isinstance(timestamp_to_use, str):
                                filled_time = datetime.fromisoformat(timestamp_to_use.replace('Z', '+00:00'))
                            else:
                                filled_time = timestamp_to_use
                            
                            # Convert to ET
                            filled_time_et = filled_time.astimezone(self.et_timezone)
                            trade_data['filled_time_et'] = filled_time_et
                            trade_data['hour'] = filled_time_et.hour
                            trade_data['minute'] = filled_time_et.minute
                            trade_data['time_str'] = filled_time_et.strftime('%H:%M:%S')
                        except:
                            trade_data['filled_time_et'] = None
                            trade_data['hour'] = 0
                            trade_data['minute'] = 0
                            trade_data['time_str'] = 'Unknown'
                    else:
                        trade_data['filled_time_et'] = None
                        trade_data['hour'] = 0
                        trade_data['minute'] = 0
                        trade_data['time_str'] = 'Unknown'
                    
                    daily_orders.append(trade_data)
            
            return sorted(daily_orders, key=lambda x: x.get('filled_time_et') if x.get('filled_time_et') else datetime.min.replace(tzinfo=self.et_timezone))
            
        except Exception as e:
            print(f"❌ Error getting trades data: {e}")
            return []
    
    def _create_comprehensive_analysis(self, trades_data: List[Dict], target_date: str) -> Dict:
        """Create detailed analysis of trading data"""
        try:
            # Group trades by symbol for round-trip analysis
            symbol_groups = {}
            for trade in trades_data:
                symbol = trade['symbol']
                if symbol not in symbol_groups:
                    symbol_groups[symbol] = {'buys': [], 'sells': []}
                
                if trade['side'] == 'buy':
                    symbol_groups[symbol]['buys'].append(trade)
                else:
                    symbol_groups[symbol]['sells'].append(trade)
            
            # Calculate comprehensive metrics
            total_trades = len(trades_data)
            total_volume = sum(trade['qty'] * trade['filled_price'] for trade in trades_data)
            
            # Symbol-level analysis
            symbol_analysis = {}
            total_pnl = 0
            profitable_symbols = 0
            round_trips = []
            
            for symbol, trades in symbol_groups.items():
                buys = sorted(trades['buys'], key=lambda x: x.get('filled_time_et') if x.get('filled_time_et') else datetime.min.replace(tzinfo=self.et_timezone))
                sells = sorted(trades['sells'], key=lambda x: x.get('filled_time_et') if x.get('filled_time_et') else datetime.min.replace(tzinfo=self.et_timezone))
                
                # Calculate P&L and metrics for this symbol
                buy_volume = sum(t['qty'] * t['filled_price'] for t in buys)
                sell_volume = sum(t['qty'] * t['filled_price'] for t in sells)
                symbol_pnl = sell_volume - buy_volume
                total_pnl += symbol_pnl
                
                if symbol_pnl > 0:
                    profitable_symbols += 1
                
                # Analyze round trips (buy-sell pairs)
                symbol_round_trips = self._analyze_round_trips(buys, sells, symbol)
                round_trips.extend(symbol_round_trips)
                
                # Time analysis for this symbol
                all_symbol_trades = buys + sells
                trade_times = [t['hour'] + t['minute']/60 for t in all_symbol_trades if t.get('filled_time_et')]
                
                symbol_analysis[symbol] = {
                    'total_trades': len(all_symbol_trades),
                    'buy_trades': len(buys),
                    'sell_trades': len(sells),
                    'buy_volume': buy_volume,
                    'sell_volume': sell_volume,
                    'net_pnl': symbol_pnl,
                    'avg_buy_price': np.mean([t['filled_price'] for t in buys]) if buys else 0,
                    'avg_sell_price': np.mean([t['filled_price'] for t in sells]) if sells else 0,
                    'first_trade_time': min(trade_times) if trade_times else 0,
                    'last_trade_time': max(trade_times) if trade_times else 0,
                    'round_trips': len(symbol_round_trips),
                    'profitable_round_trips': len([rt for rt in symbol_round_trips if rt['pnl'] > 0])
                }
            
            # Time-based analysis
            hourly_analysis = self._analyze_by_hour(trades_data)
            
            # Round trip analysis
            round_trip_analysis = self._analyze_round_trip_performance(round_trips)
            
            # Performance metrics
            win_rate = (profitable_symbols / len(symbol_groups)) * 100 if symbol_groups else 0
            avg_trade_value = total_volume / total_trades if total_trades > 0 else 0
            
            # Side analysis (long vs short performance)
            side_analysis = self._analyze_long_vs_short_performance(round_trips)
            
            return {
                'date': target_date,
                'summary': {
                    'total_pnl': total_pnl,
                    'total_trades': total_trades,
                    'total_volume': total_volume,
                    'avg_trade_value': avg_trade_value,
                    'symbols_traded': len(symbol_groups),
                    'profitable_symbols': profitable_symbols,
                    'win_rate': win_rate,
                    'total_round_trips': len(round_trips),
                    'profitable_round_trips': len([rt for rt in round_trips if rt['pnl'] > 0])
                },
                'symbol_analysis': symbol_analysis,
                'hourly_analysis': hourly_analysis,
                'round_trip_analysis': round_trip_analysis,
                'side_analysis': side_analysis,
                'raw_trades': trades_data,
                'round_trips': round_trips
            }
            
        except Exception as e:
            print(f"❌ Error creating analysis: {e}")
            return {}
    
    def _analyze_round_trips(self, buys: List[Dict], sells: List[Dict], symbol: str) -> List[Dict]:
        """Analyze round-trip trades (buy-sell pairs)"""
        round_trips = []
        
        try:
            # Simple FIFO matching for round trips
            buy_queue = buys.copy()
            sell_queue = sells.copy()
            
            for sell in sell_queue:
                for i, buy in enumerate(buy_queue):
                    if buy.get('filled_time_et') and sell.get('filled_time_et') and buy['filled_time_et'] <= sell['filled_time_et']:
                        # Calculate trade duration
                        duration = sell['filled_time_et'] - buy['filled_time_et']
                        duration_minutes = duration.total_seconds() / 60
                        
                        # Calculate P&L for this round trip
                        qty = min(buy['qty'], sell['qty'])
                        pnl = (sell['filled_price'] - buy['filled_price']) * qty
                        
                        round_trip = {
                            'symbol': symbol,
                            'buy_time': buy['filled_time_et'],
                            'sell_time': sell['filled_time_et'],
                            'buy_price': buy['filled_price'],
                            'sell_price': sell['filled_price'],
                            'qty': qty,
                            'duration_minutes': duration_minutes,
                            'duration_str': str(duration).split('.')[0],  # Remove microseconds
                            'pnl': pnl,
                            'side': 'LONG',  # Buy then sell = long position
                            'profitable': pnl > 0,
                            'buy_hour': buy['hour'],
                            'sell_hour': sell['hour'],
                            'entry_time_str': buy['time_str'],
                            'exit_time_str': sell['time_str']
                        }
                        
                        round_trips.append(round_trip)
                        
                        # Remove or reduce quantities
                        buy['qty'] -= qty
                        sell['qty'] -= qty
                        
                        if buy['qty'] <= 0:
                            buy_queue.pop(i)
                        if sell['qty'] <= 0:
                            break
                        
                        break
            
            # Handle short positions (sell first, then buy to close)
            remaining_sells = [s for s in sell_queue if s['qty'] > 0]
            remaining_buys = [b for b in buy_queue if b['qty'] > 0]
            
            for sell in remaining_sells:
                for i, buy in enumerate(remaining_buys):
                    if sell.get('filled_time_et') and buy.get('filled_time_et') and sell['filled_time_et'] <= buy['filled_time_et']:
                        duration = buy['filled_time_et'] - sell['filled_time_et']
                        duration_minutes = duration.total_seconds() / 60
                        
                        qty = min(sell['qty'], buy['qty'])
                        pnl = (sell['filled_price'] - buy['filled_price']) * qty  # Short P&L
                        
                        round_trip = {
                            'symbol': symbol,
                            'buy_time': sell['filled_time_et'],  # Entry time (sell for short)
                            'sell_time': buy['filled_time_et'],   # Exit time (buy to cover)
                            'buy_price': sell['filled_price'],   # Entry price
                            'sell_price': buy['filled_price'],   # Exit price
                            'qty': qty,
                            'duration_minutes': duration_minutes,
                            'duration_str': str(duration).split('.')[0],
                            'pnl': pnl,
                            'side': 'SHORT',  # Sell then buy = short position
                            'profitable': pnl > 0,
                            'buy_hour': sell['hour'],   # Entry hour
                            'sell_hour': buy['hour'],   # Exit hour
                            'entry_time_str': sell['time_str'],
                            'exit_time_str': buy['time_str']
                        }
                        
                        round_trips.append(round_trip)
                        
                        sell['qty'] -= qty
                        buy['qty'] -= qty
                        
                        if sell['qty'] <= 0:
                            break
                        if buy['qty'] <= 0:
                            remaining_buys.pop(i)
                            break
        
        except Exception as e:
            print(f"❌ Error analyzing round trips for {symbol}: {e}")
        
        return round_trips
    
    def _analyze_by_hour(self, trades_data: List[Dict]) -> Dict:
        """Analyze trading performance by hour of day"""
        hourly_data = {}
        
        for trade in trades_data:
            if not trade.get('filled_time_et'):
                continue
                
            hour = trade['hour']
            if hour not in hourly_data:
                hourly_data[hour] = {
                    'trades': 0,
                    'volume': 0,
                    'buy_trades': 0,
                    'sell_trades': 0
                }
            
            hourly_data[hour]['trades'] += 1
            hourly_data[hour]['volume'] += trade['qty'] * trade['filled_price']
            
            if trade['side'] == 'buy':
                hourly_data[hour]['buy_trades'] += 1
            else:
                hourly_data[hour]['sell_trades'] += 1
        
        return hourly_data
    
    def _analyze_round_trip_performance(self, round_trips: List[Dict]) -> Dict:
        """Analyze round trip trading performance"""
        if not round_trips:
            return {}
        
        profitable_trips = [rt for rt in round_trips if rt['profitable']]
        losing_trips = [rt for rt in round_trips if not rt['profitable']]
        
        # Duration analysis
        durations = [rt['duration_minutes'] for rt in round_trips]
        profitable_durations = [rt['duration_minutes'] for rt in profitable_trips]
        losing_durations = [rt['duration_minutes'] for rt in losing_trips]
        
        # P&L analysis
        pnls = [rt['pnl'] for rt in round_trips]
        profitable_pnls = [rt['pnl'] for rt in profitable_trips]
        losing_pnls = [rt['pnl'] for rt in losing_trips]
        
        return {
            'total_round_trips': len(round_trips),
            'profitable_trips': len(profitable_trips),
            'losing_trips': len(losing_trips),
            'win_rate': (len(profitable_trips) / len(round_trips)) * 100,
            'total_pnl': sum(pnls),
            'avg_profit': np.mean(profitable_pnls) if profitable_pnls else 0,
            'avg_loss': np.mean(losing_pnls) if losing_pnls else 0,
            'best_trade': max(pnls) if pnls else 0,
            'worst_trade': min(pnls) if pnls else 0,
            'avg_duration': np.mean(durations) if durations else 0,
            'avg_profitable_duration': np.mean(profitable_durations) if profitable_durations else 0,
            'avg_losing_duration': np.mean(losing_durations) if losing_durations else 0,
            'profit_factor': sum(profitable_pnls) / abs(sum(losing_pnls)) if losing_pnls and sum(losing_pnls) != 0 else float('inf')
        }
    
    def _analyze_long_vs_short_performance(self, round_trips: List[Dict]) -> Dict:
        """Analyze long vs short position performance"""
        long_trips = [rt for rt in round_trips if rt['side'] == 'LONG']
        short_trips = [rt for rt in round_trips if rt['side'] == 'SHORT']
        
        def analyze_side(trips, side_name):
            if not trips:
                return {
                    'side': side_name,
                    'total_trades': 0,
                    'profitable_trades': 0,
                    'win_rate': 0,
                    'total_pnl': 0,
                    'avg_pnl': 0,
                    'best_trade': 0,
                    'worst_trade': 0,
                    'avg_duration': 0
                }
            
            profitable = [t for t in trips if t['profitable']]
            pnls = [t['pnl'] for t in trips]
            durations = [t['duration_minutes'] for t in trips]
            
            return {
                'side': side_name,
                'total_trades': len(trips),
                'profitable_trades': len(profitable),
                'win_rate': (len(profitable) / len(trips)) * 100,
                'total_pnl': sum(pnls),
                'avg_pnl': np.mean(pnls),
                'best_trade': max(pnls),
                'worst_trade': min(pnls),
                'avg_duration': np.mean(durations)
            }
        
        return {
            'long': analyze_side(long_trips, 'LONG'),
            'short': analyze_side(short_trips, 'SHORT')
        }
    
    def _create_visualizations(self, trades_data: List[Dict], report: Dict, save_path: str):
        """Create comprehensive visualizations"""
        try:
            # Ensure reports directory exists
            Path("reports").mkdir(exist_ok=True)
            
            # Set up the plotting style
            plt.style.use('seaborn-v0_8')
            sns.set_palette("husl")
            
            # Create figure with subplots
            fig = plt.figure(figsize=(20, 16))
            
            # 1. P&L by Symbol (Top Left)
            ax1 = plt.subplot(3, 3, 1)
            symbol_pnl = {symbol: data['net_pnl'] for symbol, data in report['symbol_analysis'].items()}
            colors = ['green' if pnl > 0 else 'red' for pnl in symbol_pnl.values()]
            bars1 = ax1.bar(symbol_pnl.keys(), symbol_pnl.values(), color=colors, alpha=0.7)
            ax1.set_title('📊 P&L by Symbol', fontsize=14, fontweight='bold')
            ax1.set_ylabel('P&L ($)')
            ax1.axhline(y=0, color='black', linestyle='-', alpha=0.3)
            ax1.grid(True, alpha=0.3)
            
            # Add value labels on bars
            for bar in bars1:
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height,
                        f'${height:.2f}', ha='center', va='bottom' if height > 0 else 'top')
            
            # 2. Trading Activity by Hour (Top Middle)
            ax2 = plt.subplot(3, 3, 2)
            hourly = report['hourly_analysis']
            hours = sorted(hourly.keys())
            trade_counts = [hourly[h]['trades'] for h in hours]
            ax2.bar(hours, trade_counts, color='skyblue', alpha=0.7)
            ax2.set_title('⏰ Trading Activity by Hour', fontsize=14, fontweight='bold')
            ax2.set_xlabel('Hour of Day (ET)')
            ax2.set_ylabel('Number of Trades')
            ax2.grid(True, alpha=0.3)
            
            # 3. Round Trip P&L Distribution (Top Right)
            ax3 = plt.subplot(3, 3, 3)
            if report['round_trips']:
                pnls = [rt['pnl'] for rt in report['round_trips']]
                ax3.hist(pnls, bins=20, color='lightgreen', alpha=0.7, edgecolor='black')
                ax3.axvline(x=0, color='red', linestyle='--', label='Break Even')
                ax3.set_title('📈 Round Trip P&L Distribution', fontsize=14, fontweight='bold')
                ax3.set_xlabel('P&L per Round Trip ($)')
                ax3.set_ylabel('Frequency')
                ax3.legend()
                ax3.grid(True, alpha=0.3)
            
            # 4. Trade Duration Analysis (Middle Left)
            ax4 = plt.subplot(3, 3, 4)
            if report['round_trips']:
                durations = [rt['duration_minutes'] for rt in report['round_trips']]
                profitable_durations = [rt['duration_minutes'] for rt in report['round_trips'] if rt['profitable']]
                losing_durations = [rt['duration_minutes'] for rt in report['round_trips'] if not rt['profitable']]
                
                ax4.hist([profitable_durations, losing_durations], bins=15, 
                        label=['Profitable', 'Losing'], color=['green', 'red'], alpha=0.7)
                ax4.set_title('⏱️ Trade Duration Analysis', fontsize=14, fontweight='bold')
                ax4.set_xlabel('Duration (minutes)')
                ax4.set_ylabel('Number of Trades')
                ax4.legend()
                ax4.grid(True, alpha=0.3)
            
            # 5. Long vs Short Performance (Middle Center)
            ax5 = plt.subplot(3, 3, 5)
            side_analysis = report['side_analysis']
            sides = ['LONG', 'SHORT']
            side_pnl = [side_analysis['long']['total_pnl'], side_analysis['short']['total_pnl']]
            side_colors = ['blue', 'orange']
            bars5 = ax5.bar(sides, side_pnl, color=side_colors, alpha=0.7)
            ax5.set_title('📊 Long vs Short Performance', fontsize=14, fontweight='bold')
            ax5.set_ylabel('Total P&L ($)')
            ax5.axhline(y=0, color='black', linestyle='-', alpha=0.3)
            ax5.grid(True, alpha=0.3)
            
            # Add value labels
            for bar in bars5:
                height = bar.get_height()
                ax5.text(bar.get_x() + bar.get_width()/2., height,
                        f'${height:.2f}', ha='center', va='bottom' if height > 0 else 'top')
            
            # 6. Win Rate by Symbol (Middle Right)
            ax6 = plt.subplot(3, 3, 6)
            symbol_win_rates = {}
            for symbol, data in report['symbol_analysis'].items():
                if data['round_trips'] > 0:
                    symbol_win_rates[symbol] = (data['profitable_round_trips'] / data['round_trips']) * 100
            
            if symbol_win_rates:
                ax6.bar(symbol_win_rates.keys(), symbol_win_rates.values(), color='lightcoral', alpha=0.7)
                ax6.set_title('🎯 Win Rate by Symbol', fontsize=14, fontweight='bold')
                ax6.set_ylabel('Win Rate (%)')
                ax6.set_ylim(0, 100)
                ax6.axhline(y=50, color='gray', linestyle='--', alpha=0.5, label='50%')
                ax6.grid(True, alpha=0.3)
            
            # 7. Cumulative P&L Timeline (Bottom Left - spans 2 columns)
            ax7 = plt.subplot(3, 3, (7, 8))
            if report['round_trips']:
                # Sort round trips by time
                sorted_trips = sorted(report['round_trips'], key=lambda x: x['sell_time'])
                cumulative_pnl = np.cumsum([rt['pnl'] for rt in sorted_trips])
                times = [rt['sell_time'].strftime('%H:%M') for rt in sorted_trips]
                
                ax7.plot(range(len(cumulative_pnl)), cumulative_pnl, marker='o', linewidth=2, markersize=4)
                ax7.set_title('📈 Cumulative P&L Timeline', fontsize=14, fontweight='bold')
                ax7.set_xlabel('Trade Number')
                ax7.set_ylabel('Cumulative P&L ($)')
                ax7.axhline(y=0, color='black', linestyle='-', alpha=0.3)
                ax7.grid(True, alpha=0.3)
                
                # Add final P&L text
                final_pnl = cumulative_pnl[-1]
                ax7.text(0.02, 0.98, f'Final P&L: ${final_pnl:.2f}', 
                        transform=ax7.transAxes, fontsize=12, fontweight='bold',
                        bbox=dict(boxstyle='round', facecolor='lightgreen' if final_pnl > 0 else 'lightcoral', alpha=0.7))
            
            # 8. Summary Statistics Table (Bottom Right)
            ax8 = plt.subplot(3, 3, 9)
            ax8.axis('off')
            
            # Create summary text
            summary = report['summary']
            rt_analysis = report['round_trip_analysis']
            
            summary_text = f"""
📊 TRADING SUMMARY - {report['date']}
{'='*35}

💰 Financial Performance:
   Total P&L: ${summary['total_pnl']:.2f}
   Total Volume: ${summary['total_volume']:,.0f}
   Avg Trade Value: ${summary['avg_trade_value']:.2f}

🎯 Trade Statistics:
   Total Trades: {summary['total_trades']}
   Round Trips: {summary['total_round_trips']}
   Win Rate: {rt_analysis.get('win_rate', 0):.1f}%
   
📈 Best/Worst:
   Best Trade: ${rt_analysis.get('best_trade', 0):.2f}
   Worst Trade: ${rt_analysis.get('worst_trade', 0):.2f}
   Avg Duration: {rt_analysis.get('avg_duration', 0):.1f} min

🏢 Symbols: {summary['symbols_traded']}
   Profitable: {summary['profitable_symbols']}
"""
            
            ax8.text(0.05, 0.95, summary_text, transform=ax8.transAxes, fontsize=10,
                    verticalalignment='top', fontfamily='monospace',
                    bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
            
            # Add main title
            fig.suptitle(f'📊 Comprehensive Trading Report - {report["date"]}', 
                        fontsize=20, fontweight='bold', y=0.98)
            
            # Adjust layout
            plt.tight_layout()
            plt.subplots_adjust(top=0.94)
            
            # Save the plot
            report_file = f"{save_path}_comprehensive.png"
            plt.savefig(report_file, dpi=300, bbox_inches='tight', facecolor='white')
            print(f"📊 Comprehensive chart saved: {report_file}")
            
            # Save detailed data to CSV
            self._save_detailed_csv(report, f"{save_path}_detailed.csv")
            
            plt.show()
            
        except Exception as e:
            print(f"❌ Error creating visualizations: {e}")
            import traceback
            traceback.print_exc()
    
    def _save_detailed_csv(self, report: Dict, filename: str):
        """Save detailed trade data to CSV"""
        try:
            # Round trips data
            if report['round_trips']:
                df_round_trips = pd.DataFrame(report['round_trips'])
                df_round_trips['buy_time'] = df_round_trips['buy_time'].dt.strftime('%Y-%m-%d %H:%M:%S')
                df_round_trips['sell_time'] = df_round_trips['sell_time'].dt.strftime('%Y-%m-%d %H:%M:%S')
                
                # Save to CSV
                csv_file = filename.replace('.csv', '_round_trips.csv')
                df_round_trips.to_csv(csv_file, index=False)
                print(f"📄 Round trips data saved: {csv_file}")
            
            # Raw trades data
            df_trades = pd.DataFrame(report['raw_trades'])
            if 'filled_time_et' in df_trades.columns:
                df_trades['filled_time_et'] = df_trades['filled_time_et'].dt.strftime('%Y-%m-%d %H:%M:%S')
            
            trades_file = filename.replace('.csv', '_all_trades.csv')
            df_trades.to_csv(trades_file, index=False)
            print(f"📄 All trades data saved: {trades_file}")
            
        except Exception as e:
            print(f"❌ Error saving CSV data: {e}")
    
    def _print_summary_report(self, report: Dict):
        """Print detailed summary to console"""
        try:
            print("\n" + "="*80)
            print(f"📊 COMPREHENSIVE TRADING REPORT - {report['date']}")
            print("="*80)
            
            summary = report['summary']
            rt_analysis = report.get('round_trip_analysis', {})
            side_analysis = report.get('side_analysis', {})
            
            print(f"\n💰 FINANCIAL SUMMARY:")
            print(f"   Total P&L: ${summary['total_pnl']:.2f}")
            print(f"   Total Volume: ${summary['total_volume']:,.0f}")
            print(f"   Average Trade Value: ${summary['avg_trade_value']:.2f}")
            
            print(f"\n🎯 TRADING STATISTICS:")
            print(f"   Total Trades: {summary['total_trades']}")
            print(f"   Round Trip Trades: {summary['total_round_trips']}")
            print(f"   Symbols Traded: {summary['symbols_traded']}")
            print(f"   Profitable Symbols: {summary['profitable_symbols']}")
            print(f"   Overall Win Rate: {rt_analysis.get('win_rate', 0):.1f}%")
            
            if rt_analysis:
                print(f"\n📈 PERFORMANCE METRICS:")
                print(f"   Best Trade: ${rt_analysis.get('best_trade', 0):.2f}")
                print(f"   Worst Trade: ${rt_analysis.get('worst_trade', 0):.2f}")
                print(f"   Average Profit: ${rt_analysis.get('avg_profit', 0):.2f}")
                print(f"   Average Loss: ${rt_analysis.get('avg_loss', 0):.2f}")
                print(f"   Profit Factor: {rt_analysis.get('profit_factor', 0):.2f}")
                print(f"   Average Duration: {rt_analysis.get('avg_duration', 0):.1f} minutes")
            
            if side_analysis:
                print(f"\n📊 LONG vs SHORT PERFORMANCE:")
                long_data = side_analysis.get('long', {})
                short_data = side_analysis.get('short', {})
                
                print(f"   LONG Positions:")
                print(f"     Trades: {long_data.get('total_trades', 0)}")
                print(f"     Win Rate: {long_data.get('win_rate', 0):.1f}%")
                print(f"     Total P&L: ${long_data.get('total_pnl', 0):.2f}")
                print(f"     Avg Duration: {long_data.get('avg_duration', 0):.1f} min")
                
                print(f"   SHORT Positions:")
                print(f"     Trades: {short_data.get('total_trades', 0)}")
                print(f"     Win Rate: {short_data.get('win_rate', 0):.1f}%")
                print(f"     Total P&L: ${short_data.get('total_pnl', 0):.2f}")
                print(f"     Avg Duration: {short_data.get('avg_duration', 0):.1f} min")
            
            print(f"\n📋 SYMBOL BREAKDOWN:")
            for symbol, data in report['symbol_analysis'].items():
                print(f"   {symbol}:")
                print(f"     Total Trades: {data['total_trades']}")
                print(f"     Round Trips: {data['round_trips']}")
                print(f"     Net P&L: ${data['net_pnl']:.2f}")
                print(f"     Win Rate: {(data['profitable_round_trips']/data['round_trips']*100) if data['round_trips'] > 0 else 0:.1f}%")
            
            print("\n" + "="*80)
            
        except Exception as e:
            print(f"❌ Error printing summary: {e}")
    
    def _generate_empty_report(self, target_date: str) -> Dict:
        """Generate empty report structure for days with no trades"""
        return {
            'date': target_date,
            'summary': {
                'total_pnl': 0,
                'total_trades': 0,
                'total_volume': 0,
                'avg_trade_value': 0,
                'symbols_traded': 0,
                'profitable_symbols': 0,
                'win_rate': 0,
                'total_round_trips': 0,
                'profitable_round_trips': 0
            },
            'symbol_analysis': {},
            'hourly_analysis': {},
            'round_trip_analysis': {},
            'side_analysis': {'long': {}, 'short': {}},
            'raw_trades': [],
            'round_trips': []
        }

def main():
    """Main function for running comprehensive P&L report"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Comprehensive P&L Report Generator")
    parser.add_argument("--date", help="Target date (YYYY-MM-DD)", default=None)
    parser.add_argument("--save-path", help="Save path prefix for files", default=None)
    
    args = parser.parse_args()
    
    # Create and run report
    reporter = ComprehensivePnLReporter()
    report = reporter.generate_comprehensive_report(
        target_date=args.date,
        save_path=args.save_path
    )
    
    if report and report['summary']['total_trades'] > 0:
        print(f"\n✅ Report generated successfully!")
        print(f"📊 Charts and data saved to reports/ directory")
    else:
        print(f"\n📭 No trading activity found for the specified date")

if __name__ == "__main__":
    main()
