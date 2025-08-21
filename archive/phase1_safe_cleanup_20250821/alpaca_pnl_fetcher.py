#!/usr/bin/env python3
"""
Alpaca P&L Data Fetcher
Get actual P&L data directly from Alpaca's portfolio history
This is the source of truth, includes commissions/fees
"""

import sys
import os
from pathlib import Path
from datetime import date, datetime, timedelta
import pandas as pd
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database.trading_db import TradingDatabase

class AlpacaPnLFetcher:
    """Fetch actual P&L data from Alpaca"""
    
    def __init__(self):
        self.api = tradeapi.REST(
            os.getenv('ALPACA_API_KEY'),
            os.getenv('ALPACA_SECRET_KEY'),
            os.getenv('ALPACA_BASE_URL'),
            api_version='v2'
        )
    
    def get_daily_pnl(self, target_date: date) -> dict:
        """Get Alpaca's actual daily P&L for a specific date"""
        
        try:
            # Get portfolio history for a broader range
            portfolio_history = self.api.get_portfolio_history(
                period='1M',
                timeframe='1D'
            )
            
            if not portfolio_history:
                return {'error': 'No portfolio history available'}
            
            # Get the data arrays
            timestamps = portfolio_history.timestamp
            profit_loss = portfolio_history.profit_loss
            equity = portfolio_history.equity
            
            if not timestamps or not profit_loss:
                return {'error': 'No P&L data in portfolio history'}
            
            print(f"   📊 Found {len(timestamps)} days of portfolio history")
            
            # Find the closest date match
            target_datetime = datetime.combine(target_date, datetime.min.time())
            best_match_index = None
            best_match_date = None
            
            for i, ts in enumerate(timestamps):
                # Convert timestamp to datetime
                ts_datetime = datetime.fromtimestamp(ts)
                ts_date = ts_datetime.date()
                
                print(f"     Day {i}: {ts_date} -> P&L: ${profit_loss[i]:.2f}")
                
                if ts_date == target_date:
                    best_match_index = i
                    best_match_date = ts_date
                    break
            
            if best_match_index is not None:
                daily_pnl = profit_loss[best_match_index]
                daily_equity = equity[best_match_index] if equity else 0
                
                return {
                    'date': target_date,
                    'alpaca_pnl': daily_pnl,
                    'equity': daily_equity,
                    'data_source': 'alpaca_portfolio_history',
                    'includes_fees': True,
                    'error': None
                }
            else:
                # If no exact match, show what we found
                available_dates = []
                for i, ts in enumerate(timestamps[-5:]):  # Last 5 days
                    ts_date = datetime.fromtimestamp(ts).date()
                    available_dates.append(f"{ts_date}: ${profit_loss[i]:.2f}")
                
                return {
                    'error': f'No data for {target_date}. Recent dates: {", ".join(available_dates)}'
                }
                
        except Exception as e:
            return {'error': f'Error fetching Alpaca P&L: {str(e)}'}
    
    def get_account_pnl_summary(self) -> dict:
        """Get current account P&L summary"""
        
        try:
            account = self.api.get_account()
            
            # Extract available P&L fields
            pnl_data = {}
            
            # Check for various P&L attributes
            pnl_attributes = [
                'total_pnl', 'unrealized_pnl', 'realized_pnl', 
                'todays_pnl', 'pl_day', 'pl_total'
            ]
            
            for attr in pnl_attributes:
                if hasattr(account, attr):
                    value = getattr(account, attr)
                    if value is not None:
                        pnl_data[attr] = float(value)
            
            return {
                'portfolio_value': float(account.portfolio_value),
                'cash': float(account.cash),
                'buying_power': float(account.buying_power),
                'pnl_data': pnl_data,
                'account_blocked': getattr(account, 'account_blocked', False),
                'trading_blocked': getattr(account, 'trading_blocked', False),
                'error': None
            }
            
        except Exception as e:
            return {'error': f'Error fetching account data: {str(e)}'}

def update_database_with_alpaca_pnl():
    """Update database daily summaries with Alpaca's actual P&L"""
    
    fetcher = AlpacaPnLFetcher()
    db = TradingDatabase()
    
    print("📊 Updating Database with Alpaca's Actual P&L")
    print("=" * 50)
    
    # Dates to update
    dates_to_update = [
        date(2025, 8, 18),
        date(2025, 8, 19)
    ]
    
    for target_date in dates_to_update:
        print(f"\n📅 Processing {target_date}...")
        
        # Get Alpaca's actual P&L
        alpaca_pnl = fetcher.get_daily_pnl(target_date)
        
        if alpaca_pnl.get('error'):
            print(f"   ❌ Alpaca P&L Error: {alpaca_pnl['error']}")
            continue
        
        # Get current database summary
        db_summary = db.get_daily_summary(target_date)
        
        if not db_summary:
            print(f"   ❌ No database summary found for {target_date}")
            continue
        
        # Update with Alpaca's actual P&L
        print(f"   💰 Alpaca P&L: ${alpaca_pnl['alpaca_pnl']:,.2f}")
        print(f"   📊 Database Cash Flow: ${db_summary.get('cash_flow_pnl', 0):,.2f}")
        
        # Update database summary with Alpaca's actual P&L
        import sqlite3
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE daily_summaries 
                SET trading_pnl = ?, updated_at = CURRENT_TIMESTAMP
                WHERE trade_date = ?
            """, (alpaca_pnl['alpaca_pnl'], target_date))
            conn.commit()
        
        print(f"   ✅ Updated database with Alpaca's actual P&L")
    
    # Show account summary
    print(f"\n💼 Current Account Status:")
    account_data = fetcher.get_account_pnl_summary()
    
    if account_data.get('error'):
        print(f"   ❌ Account Error: {account_data['error']}")
    else:
        print(f"   Portfolio Value: ${account_data['portfolio_value']:,.2f}")
        print(f"   Cash: ${account_data['cash']:,.2f}")
        print(f"   Available P&L Data: {list(account_data['pnl_data'].keys())}")
        
        for pnl_type, value in account_data['pnl_data'].items():
            print(f"     {pnl_type}: ${value:,.2f}")

def test_alpaca_pnl_for_yesterday():
    """Test Alpaca P&L fetching for yesterday specifically"""
    
    fetcher = AlpacaPnLFetcher()
    yesterday = date(2025, 8, 19)
    
    print(f"🧪 Testing Alpaca P&L for {yesterday}")
    print("=" * 40)
    
    # Get Alpaca P&L
    result = fetcher.get_daily_pnl(yesterday)
    
    if result.get('error'):
        print(f"❌ Error: {result['error']}")
    else:
        print(f"✅ Success!")
        print(f"   Date: {result['date']}")
        print(f"   Alpaca P&L: ${result['alpaca_pnl']:,.2f}")
        print(f"   Equity: ${result['equity']:,.2f}")
        print(f"   Includes Fees: {result['includes_fees']}")
        print(f"   Data Source: {result['data_source']}")
    
    # Compare with your stated value
    if not result.get('error'):
        stated_pnl = 61.0  # Your stated value
        actual_pnl = result['alpaca_pnl']
        difference = abs(actual_pnl - stated_pnl)
        
        print(f"\n📊 Comparison:")
        print(f"   Your Stated P&L: ~${stated_pnl:.2f}")
        print(f"   Alpaca Actual P&L: ${actual_pnl:.2f}")
        print(f"   Difference: ${difference:.2f}")
        
        if difference < 5:
            print(f"   ✅ Values match closely!")
        else:
            print(f"   🤔 Significant difference detected")

if __name__ == "__main__":
    print("🎯 Alpaca P&L Data Fetcher")
    print("Using Alpaca as source of truth for P&L calculations")
    print()
    
    # Test yesterday's P&L first
    test_alpaca_pnl_for_yesterday()
    
    print("\n" + "="*60 + "\n")
    
    # Update database with Alpaca's actual P&L
    update_database_with_alpaca_pnl()
