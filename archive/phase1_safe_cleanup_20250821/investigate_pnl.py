#!/usr/bin/env python3
"""
P&L Investigation - Compare Cash Flow vs Alpaca Net P&L
Understanding the difference between our calculation and Alpaca's actual P&L
"""

import sys
import os
from pathlib import Path
from datetime import date, timedelta
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database.trading_db import TradingDatabase

def investigate_pnl_difference():
    """Compare our cash flow calculation vs Alpaca's actual P&L"""
    
    # Initialize API
    api = tradeapi.REST(
        os.getenv('ALPACA_API_KEY'),
        os.getenv('ALPACA_SECRET_KEY'),
        os.getenv('ALPACA_BASE_URL'),
        api_version='v2'
    )
    
    yesterday = date(2025, 8, 19)
    
    print("🔍 P&L Investigation for 8/19/25")
    print("=" * 50)
    
    # 1. Get our cash flow calculation
    db = TradingDatabase()
    db_summary = db.get_daily_summary(yesterday)
    
    print(f"\n💰 Our Cash Flow Calculation:")
    print(f"   Database P&L: ${db_summary['net_pnl']:.2f}")
    
    # 2. Get Alpaca's portfolio history for that day
    try:
        print(f"\n📊 Alpaca Portfolio History:")
        
        # Get portfolio history for yesterday
        portfolio_history = api.get_portfolio_history(
            period='1D',
            timeframe='1Day',
            end=yesterday.isoformat()
        )
        
        if portfolio_history and len(portfolio_history.profit_loss) > 0:
            alpaca_pnl = portfolio_history.profit_loss[-1]
            print(f"   Alpaca Net P&L: ${alpaca_pnl:.2f}")
            
            difference = db_summary['net_pnl'] - alpaca_pnl
            print(f"   Difference: ${difference:.2f}")
            
            if abs(difference) > 10:
                print(f"   🚨 SIGNIFICANT DIFFERENCE DETECTED!")
            else:
                print(f"   ✅ Values are reasonably close")
        else:
            print(f"   ❌ No portfolio history data available")
            
    except Exception as e:
        print(f"   ❌ Error getting portfolio history: {str(e)}")
    
    # 3. Get account information
    try:
        print(f"\n💼 Account Information:")
        account = api.get_account()
        
        print(f"   Today's P&L: ${float(account.todays_pnl):.2f}")
        print(f"   Unrealized P&L: ${float(account.unrealized_pnl):.2f}")
        print(f"   Realized P&L: ${float(account.realized_pnl or 0):.2f}")
        
    except Exception as e:
        print(f"   ❌ Error getting account info: {str(e)}")
    
    # 4. Analyze individual trades for yesterday
    print(f"\n📋 Trade Analysis for {yesterday}:")
    
    try:
        activities = api.get_activities(
            activity_types='FILL',
            date=yesterday.strftime('%Y-%m-%d'),
            direction='desc',
            page_size=100
        )
        
        if activities:
            print(f"   Total Activities: {len(activities)}")
            
            # Group by symbol
            symbol_trades = {}
            total_cash_flow = 0
            
            for activity in activities:
                symbol = activity.symbol
                side = activity.side
                qty = float(activity.qty)
                price = float(activity.price)
                value = qty * price
                
                if symbol not in symbol_trades:
                    symbol_trades[symbol] = {'buys': 0, 'sells': 0, 'cash_flow': 0}
                
                if side in ['buy']:
                    symbol_trades[symbol]['buys'] += value
                    symbol_trades[symbol]['cash_flow'] -= value  # Money out
                    total_cash_flow -= value
                elif side in ['sell', 'sell_short']:
                    symbol_trades[symbol]['sells'] += value
                    symbol_trades[symbol]['cash_flow'] += value  # Money in
                    total_cash_flow += value
            
            print(f"\n   Cash Flow by Symbol:")
            for symbol, data in symbol_trades.items():
                print(f"     {symbol}: ${data['cash_flow']:.2f} (Buys: ${data['buys']:.2f}, Sells: ${data['sells']:.2f})")
            
            print(f"\n   Total Cash Flow: ${total_cash_flow:.2f}")
            print(f"   Database Cash Flow: ${db_summary['net_pnl']:.2f}")
            print(f"   Match: {'✅' if abs(total_cash_flow - db_summary['net_pnl']) < 0.01 else '❌'}")
            
    except Exception as e:
        print(f"   ❌ Error analyzing trades: {str(e)}")
    
    print(f"\n🧠 Analysis:")
    print(f"   • Cash Flow P&L = Money In - Money Out")
    print(f"   • Alpaca Net P&L = Actual profit/loss from position changes")
    print(f"   • Difference occurs when positions span multiple days")
    print(f"   • Example: Buy AAPL on 8/18 at $100, sell on 8/19 at $105")
    print(f"     - Cash flow on 8/19: +$105 (just the sell)")
    print(f"     - Actual P&L: +$5 (the profit)")

if __name__ == "__main__":
    investigate_pnl_difference()
