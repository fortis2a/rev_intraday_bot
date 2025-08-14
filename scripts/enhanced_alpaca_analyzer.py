#!/usr/bin/env python3
"""
Enhanced Alpaca Trading Data Analyzer
Demonstrates comprehensive trade analysis using actual Alpaca data

Features:
1. Retrieves all filled orders with detailed trade data
2. Calculates realized P&L with proper trade matching
3. Shows trade-by-trade breakdown
4. Validates against Alpaca's official P&L
5. Provides detailed trading statistics
"""

import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal
import pandas as pd

# Add the parent directory to sys.path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.data_manager import DataManager
from utils.logger import setup_logger

class EnhancedAlpacaAnalyzer:
    """Enhanced analyzer for Alpaca trading data"""
    
    def __init__(self):
        self.logger = setup_logger("EnhancedAlpacaAnalyzer")
        self.data_manager = DataManager()
        self.api = self.data_manager.api
        
    def get_detailed_orders(self, days_back=1):
        """Get detailed order information for analysis"""
        try:
            start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
            
            orders = self.api.list_orders(
                status='filled',
                limit=500,
                after=start_date
            )
            
            detailed_orders = []
            for order in orders:
                order_data = {
                    'id': order.id,
                    'symbol': order.symbol,
                    'side': order.side,
                    'qty': float(order.filled_qty or order.qty),
                    'price': float(order.filled_avg_price or 0),
                    'filled_at': order.filled_at,
                    'created_at': order.created_at,
                    'order_type': order.order_type,
                    'time_in_force': order.time_in_force,
                    'notional': float(order.notional) if hasattr(order, 'notional') and order.notional else None
                }
                detailed_orders.append(order_data)
            
            self.logger.info(f"Retrieved {len(detailed_orders)} detailed orders")
            return detailed_orders
            
        except Exception as e:
            self.logger.error(f"Error getting detailed orders: {e}")
            return []
    
    def analyze_trading_session(self, orders):
        """Analyze trading session with detailed trade matching"""
        try:
            if not orders:
                return {}
            
            # Group orders by symbol
            symbol_groups = {}
            for order in orders:
                symbol = order['symbol']
                if symbol not in symbol_groups:
                    symbol_groups[symbol] = {'buys': [], 'sells': []}
                
                if order['side'] == 'buy':
                    symbol_groups[symbol]['buys'].append(order)
                else:
                    symbol_groups[symbol]['sells'].append(order)
            
            # Analyze each symbol
            analysis_results = {}
            total_realized_pnl = 0.0
            total_trades = 0
            total_volume = 0.0
            
            for symbol, trades in symbol_groups.items():
                buys = sorted(trades['buys'], key=lambda x: x['filled_at'] or x['created_at'])
                sells = sorted(trades['sells'], key=lambda x: x['filled_at'] or x['created_at'])
                
                # Calculate statistics
                symbol_stats = {
                    'symbol': symbol,
                    'total_buys': len(buys),
                    'total_sells': len(sells),
                    'buy_volume': sum(order['qty'] for order in buys),
                    'sell_volume': sum(order['qty'] for order in sells),
                    'buy_value': sum(order['qty'] * order['price'] for order in buys),
                    'sell_value': sum(order['qty'] * order['price'] for order in sells),
                    'realized_pnl': 0.0,
                    'trades': [],
                    'avg_buy_price': 0.0,
                    'avg_sell_price': 0.0
                }
                
                if buys:
                    symbol_stats['avg_buy_price'] = symbol_stats['buy_value'] / symbol_stats['buy_volume']
                if sells:
                    symbol_stats['avg_sell_price'] = symbol_stats['sell_value'] / symbol_stats['sell_volume']
                
                # Match trades using FIFO
                buy_queue = buys.copy()
                realized_pnl = 0.0
                
                for sell in sells:
                    sell_qty_remaining = sell['qty']
                    
                    while sell_qty_remaining > 0 and buy_queue:
                        buy = buy_queue[0]
                        buy_qty_available = buy['qty']
                        
                        # Match quantities
                        matched_qty = min(sell_qty_remaining, buy_qty_available)
                        
                        # Calculate P&L for this trade pair
                        trade_pnl = matched_qty * (sell['price'] - buy['price'])
                        realized_pnl += trade_pnl
                        
                        # Record the trade
                        trade_record = {
                            'buy_order_id': buy['id'],
                            'sell_order_id': sell['id'],
                            'qty': matched_qty,
                            'buy_price': buy['price'],
                            'sell_price': sell['price'],
                            'pnl': trade_pnl,
                            'buy_time': buy['filled_at'] or buy['created_at'],
                            'sell_time': sell['filled_at'] or sell['created_at']
                        }
                        symbol_stats['trades'].append(trade_record)
                        
                        # Update quantities
                        sell_qty_remaining -= matched_qty
                        buy['qty'] -= matched_qty
                        
                        if buy['qty'] <= 0:
                            buy_queue.pop(0)
                
                symbol_stats['realized_pnl'] = realized_pnl
                analysis_results[symbol] = symbol_stats
                
                total_realized_pnl += realized_pnl
                total_trades += len(symbol_stats['trades'])
                total_volume += symbol_stats['buy_value']
            
            # Overall session statistics
            session_stats = {
                'total_realized_pnl': total_realized_pnl,
                'total_completed_trades': total_trades,
                'total_volume_traded': total_volume,
                'symbols_traded': len(analysis_results),
                'total_orders': len(orders),
                'profitable_symbols': len([s for s in analysis_results.values() if s['realized_pnl'] > 0]),
                'losing_symbols': len([s for s in analysis_results.values() if s['realized_pnl'] < 0])
            }
            
            return {
                'session_stats': session_stats,
                'symbol_analysis': analysis_results
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing trading session: {e}")
            return {}
    
    def display_enhanced_analysis(self):
        """Display comprehensive trading analysis"""
        print("=" * 100)
        print("📊 ENHANCED ALPACA TRADING DATA ANALYSIS")
        print("=" * 100)
        print()
        
        # Get today's orders
        orders = self.get_detailed_orders()
        
        if not orders:
            print("❌ No trading data found for today")
            return
        
        # Analyze the trading session
        analysis = self.analyze_trading_session(orders)
        
        if not analysis:
            print("❌ Unable to analyze trading data")
            return
        
        session_stats = analysis['session_stats']
        symbol_analysis = analysis['symbol_analysis']
        
        # Session Overview
        print("📋 SESSION OVERVIEW")
        print("-" * 50)
        print(f"Total Orders Executed:     {session_stats['total_orders']}")
        print(f"Completed Trade Pairs:     {session_stats['total_completed_trades']}")
        print(f"Symbols Traded:            {session_stats['symbols_traded']}")
        print(f"Total Volume Traded:       ${session_stats['total_volume_traded']:,.2f}")
        print(f"Profitable Symbols:        {session_stats['profitable_symbols']}")
        print(f"Losing Symbols:            {session_stats['losing_symbols']}")
        print(f"Realized P&L:              ${session_stats['total_realized_pnl']:+,.2f}")
        print()
        
        # Per-Symbol Analysis
        print("📈 PER-SYMBOL DETAILED ANALYSIS")
        print("-" * 50)
        
        for symbol, stats in symbol_analysis.items():
            print(f"\n🔍 {symbol}")
            print(f"   Orders: {stats['total_buys']} buys, {stats['total_sells']} sells")
            print(f"   Volume: {stats['buy_volume']:.0f} bought, {stats['sell_volume']:.0f} sold")
            print(f"   Avg Prices: Buy ${stats['avg_buy_price']:.4f}, Sell ${stats['avg_sell_price']:.4f}")
            print(f"   Total Value: ${stats['buy_value']:,.2f} bought, ${stats['sell_value']:,.2f} sold")
            print(f"   Realized P&L: ${stats['realized_pnl']:+,.2f}")
            
            if stats['trades']:
                print(f"   Completed Trades: {len(stats['trades'])}")
                
                # Show individual trades
                for i, trade in enumerate(stats['trades'][:5]):  # Show first 5 trades
                    pnl_per_share = trade['sell_price'] - trade['buy_price']
                    print(f"     Trade {i+1}: {trade['qty']:.0f} shares @ "
                          f"${trade['buy_price']:.4f} → ${trade['sell_price']:.4f} "
                          f"({pnl_per_share:+.4f}/share) = ${trade['pnl']:+.2f}")
                
                if len(stats['trades']) > 5:
                    print(f"     ... and {len(stats['trades']) - 5} more trades")
        
        print()
        
        # Comparison with Alpaca's Official P&L
        print("✅ VALIDATION AGAINST ALPACA'S OFFICIAL DATA")
        print("-" * 50)
        
        alpaca_pnl = self.data_manager.get_daily_pnl()
        if alpaca_pnl:
            official_pnl = alpaca_pnl['daily_pnl']
            calculated_pnl = session_stats['total_realized_pnl']
            
            print(f"Alpaca Official Daily P&L: ${official_pnl:+,.2f}")
            print(f"Calculated Realized P&L:   ${calculated_pnl:+,.2f}")
            
            difference = abs(official_pnl - calculated_pnl)
            if difference < 0.01:
                print("✅ Perfect match! Calculations are accurate.")
            elif difference < 1.00:
                print(f"✅ Close match (diff: ${difference:.2f}) - likely rounding/timing differences")
            else:
                print(f"⚠️  Significant difference: ${difference:.2f}")
                print("   This could be due to:")
                print("   - Overnight positions from previous day")
                print("   - Dividends or corporate actions")
                print("   - Fees/commissions (if in live trading)")
                print("   - Timing differences in order fills")
        
        print()
        
        # Trading Performance Metrics
        print("📊 TRADING PERFORMANCE METRICS")
        print("-" * 50)
        
        if session_stats['total_completed_trades'] > 0:
            avg_trade_pnl = session_stats['total_realized_pnl'] / session_stats['total_completed_trades']
            win_rate = len([s for s in symbol_analysis.values() if s['realized_pnl'] > 0]) / len(symbol_analysis) * 100
            
            print(f"Average P&L per Trade:     ${avg_trade_pnl:+.2f}")
            print(f"Symbol Win Rate:           {win_rate:.1f}%")
            print(f"Total Return on Volume:    {(session_stats['total_realized_pnl'] / session_stats['total_volume_traded'] * 100):+.3f}%")
            
            # Best and worst performing symbols
            if symbol_analysis:
                best_symbol = max(symbol_analysis.values(), key=lambda x: x['realized_pnl'])
                worst_symbol = min(symbol_analysis.values(), key=lambda x: x['realized_pnl'])
                
                print(f"Best Performer:            {best_symbol['symbol']} (${best_symbol['realized_pnl']:+.2f})")
                print(f"Worst Performer:           {worst_symbol['symbol']} (${worst_symbol['realized_pnl']:+.2f})")
        
        print()
        print("=" * 100)

def main():
    """Main function"""
    try:
        analyzer = EnhancedAlpacaAnalyzer()
        analyzer.display_enhanced_analysis()
        
    except Exception as e:
        print(f"❌ Error running enhanced analyzer: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
