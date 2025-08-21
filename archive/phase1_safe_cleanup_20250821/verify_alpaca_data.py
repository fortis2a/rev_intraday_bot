#!/usr/bin/env python3
"""
Verify actual Alpaca trade activities vs report data
"""

import sys
import os
from datetime import datetime, date, timedelta
sys.path.append('.')

from config import config
import alpaca_trade_api as tradeapi

def get_actual_alpaca_activities():
    """Get actual activities from Alpaca API"""
    
    api = tradeapi.REST(
        config['ALPACA_API_KEY'],
        config['ALPACA_SECRET_KEY'], 
        config['ALPACA_BASE_URL']
    )
    
    today = date.today()
    
    print(f"🔍 ALPACA ACTIVITIES VERIFICATION - {today}")
    print("="*60)
    
    # Get today's activities
    try:
        # Try activities first
        try:
            activities = api.get_activities(
                activity_types='FILL'
            )
            
            print(f"Found {len(activities)} activities:")
            
            total_pnl = 0
            trade_count = 0
            
            for activity in activities:
                # Only show today's activities
                if activity.transaction_time.date() != today:
                    continue
                    
                trade_count += 1
                side = activity.side
                qty = float(activity.qty)
                price = float(activity.price)
                symbol = activity.symbol
                timestamp = activity.transaction_time
                
                # Calculate value
                value = qty * price
                sign = "+" if side in ['sell', 'sell_short'] else "-"
                
                print(f"{trade_count:2d}. {side.upper()} {qty} {symbol} @ ${price:.2f} = {sign}${value:.2f} | {timestamp}")
                
                # Add to P&L calculation (simplified)
                if side in ['sell', 'sell_short']:
                    total_pnl += value
                else:
                    total_pnl -= value
            
        except Exception as e1:
            print(f"Activities API failed: {e1}")
            print("Trying orders API instead...")
            
            # Fall back to orders
            yesterday_start = datetime.combine(today - timedelta(days=1), datetime.min.time())
            formatted_date = yesterday_start.strftime('%Y-%m-%dT%H:%M:%SZ')
            
            orders = api.list_orders(
                status='filled',
                after=formatted_date
            )
            
            # Filter for today only
            today_orders = [o for o in orders if o.filled_at and o.filled_at.date() == today]
            
            print(f"Found {len(today_orders)} filled orders today:")
            
            total_pnl = 0
            trade_count = 0
            
            for order in today_orders:
                trade_count += 1
                side = order.side
                qty = float(order.filled_qty)
                price = float(order.filled_avg_price)
                symbol = order.symbol
                timestamp = order.filled_at
                
                # Calculate value
                value = qty * price
                sign = "+" if side in ['sell'] else "-"
                
                print(f"{trade_count:2d}. {side.upper()} {qty} {symbol} @ ${price:.2f} = {sign}${value:.2f} | {timestamp}")
                
                # Add to P&L calculation (simplified)
                if side == 'sell':
                    total_pnl += value
                else:
                    total_pnl -= value
        
        print(f"\n📊 SUMMARY:")
        print(f"Total Trades: {trade_count}")
        print(f"Net Cash Flow: ${total_pnl:.2f}")
        
        return activities
        
    except Exception as e:
        print(f"❌ Error getting activities: {e}")
        return []

if __name__ == "__main__":
    get_actual_alpaca_activities()
