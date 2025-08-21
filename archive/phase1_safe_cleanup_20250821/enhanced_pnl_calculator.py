#!/usr/bin/env python3
"""
Enhanced P&L Calculator
Calculate true trading P&L using position tracking across days
"""

import sys
import os
from pathlib import Path
from datetime import date, timedelta
import pandas as pd
from collections import defaultdict

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database.trading_db import TradingDatabase

class TradingPnLCalculator:
    """Calculate true trading P&L by tracking positions across days"""
    
    def __init__(self):
        self.db = TradingDatabase()
    
    def calculate_true_pnl(self, target_date: date) -> dict:
        """Calculate true P&L for a date considering position tracking"""
        
        # Get data from start date to target date to track positions
        start_date = target_date - timedelta(days=30)  # Look back 30 days
        
        # Get all activities in range
        activities_df = self.db.get_activities(start_date, target_date)
        
        if activities_df.empty:
            return {
                'cash_flow_pnl': 0.0,
                'trading_pnl': 0.0,
                'positions_opened': 0,
                'positions_closed': 0,
                'day_trades': 0
            }
        
        # Convert transaction_time to datetime
        activities_df['transaction_time'] = pd.to_datetime(activities_df['transaction_time'])
        
        # Track positions by symbol
        positions = defaultdict(list)  # symbol -> list of (qty, price, date, time)
        target_date_pnl = 0.0
        target_date_cash_flow = 0.0
        positions_opened = 0
        positions_closed = 0
        day_trades = 0
        
        # Sort by transaction time
        activities_df = activities_df.sort_values('transaction_time')
        
        for _, activity in activities_df.iterrows():
            symbol = activity['symbol']
            side = activity['side']
            qty = activity['quantity']
            price = activity['price']
            value = activity['value']
            trade_date = activity['trade_date']
            
            # Track cash flow for target date
            if str(trade_date) == str(target_date):
                if side in ['sell', 'sell_short']:
                    target_date_cash_flow += value
                else:  # buy
                    target_date_cash_flow -= value
            
            # Position tracking
            if side == 'buy':
                # Add to position
                positions[symbol].append({
                    'qty': qty,
                    'price': price,
                    'date': trade_date,
                    'time': activity['transaction_time'],
                    'type': 'long'
                })
                
                if str(trade_date) == str(target_date):
                    positions_opened += 1
                    
            elif side == 'sell':
                # Close long position (FIFO)
                remaining_qty = qty
                trade_pnl = 0.0
                
                while remaining_qty > 0 and positions[symbol]:
                    # Find oldest long position
                    long_positions = [p for p in positions[symbol] if p['type'] == 'long' and p['qty'] > 0]
                    if not long_positions:
                        break
                    
                    oldest_pos = min(long_positions, key=lambda x: x['time'])
                    
                    # Calculate how much we can close
                    close_qty = min(remaining_qty, oldest_pos['qty'])
                    
                    # Calculate P&L for this portion
                    pnl = close_qty * (price - oldest_pos['price'])
                    trade_pnl += pnl
                    
                    # Check if this is a day trade (same day open/close)
                    if str(oldest_pos['date']) == str(trade_date):
                        day_trades += 1
                    
                    # Update position
                    oldest_pos['qty'] -= close_qty
                    remaining_qty -= close_qty
                    
                    # Add to target date P&L if closed on target date
                    if str(trade_date) == str(target_date):
                        target_date_pnl += pnl
                        positions_closed += 1
                
                # Clean up empty positions
                positions[symbol] = [p for p in positions[symbol] if p['qty'] > 0]
                
            elif side == 'sell_short':
                # Open short position
                positions[symbol].append({
                    'qty': qty,
                    'price': price,
                    'date': trade_date,
                    'time': activity['transaction_time'],
                    'type': 'short'
                })
                
                if str(trade_date) == str(target_date):
                    positions_opened += 1
        
        return {
            'cash_flow_pnl': target_date_cash_flow,
            'trading_pnl': target_date_pnl,
            'positions_opened': positions_opened,
            'positions_closed': positions_closed,
            'day_trades': day_trades,
            'open_positions': sum(len([p for p in pos_list if p['qty'] > 0]) for pos_list in positions.values())
        }

def analyze_yesterday_pnl():
    """Analyze yesterday's P&L using enhanced calculation"""
    
    calculator = TradingPnLCalculator()
    yesterday = date(2025, 8, 19)
    
    print("🔍 Enhanced P&L Analysis for 8/19/25")
    print("=" * 50)
    
    # Calculate enhanced P&L
    pnl_data = calculator.calculate_true_pnl(yesterday)
    
    print(f"\n💰 P&L Breakdown:")
    print(f"   Cash Flow P&L: ${pnl_data['cash_flow_pnl']:,.2f}")
    print(f"   Trading P&L: ${pnl_data['trading_pnl']:,.2f}")
    print(f"   Positions Opened: {pnl_data['positions_opened']}")
    print(f"   Positions Closed: {pnl_data['positions_closed']}")
    print(f"   Day Trades: {pnl_data['day_trades']}")
    print(f"   Open Positions: {pnl_data['open_positions']}")
    
    print(f"\n📊 Comparison:")
    print(f"   Our Database (Cash Flow): ${pnl_data['cash_flow_pnl']:,.2f}")
    print(f"   Our Trading P&L: ${pnl_data['trading_pnl']:,.2f}")
    print(f"   Alpaca Reported: ~$61.93")
    
    difference_trading = abs(pnl_data['trading_pnl'] - 61.93)
    difference_cash = abs(pnl_data['cash_flow_pnl'] - 61.93)
    
    print(f"\n🎯 Accuracy Check:")
    print(f"   Trading P&L vs Alpaca: ${difference_trading:.2f} difference")
    print(f"   Cash Flow vs Alpaca: ${difference_cash:.2f} difference")
    
    if difference_trading < difference_cash:
        print(f"   ✅ Trading P&L is more accurate!")
    else:
        print(f"   🤔 Cash flow is closer (unexpected)")
    
    print(f"\n💡 Explanation:")
    print(f"   • Cash Flow = Money in/out on specific day")
    print(f"   • Trading P&L = Profit/loss from completed positions")
    print(f"   • Alpaca's $61.93 represents actual trading profit")
    print(f"   • Large cash flow difference suggests positions from previous day")

if __name__ == "__main__":
    analyze_yesterday_pnl()
