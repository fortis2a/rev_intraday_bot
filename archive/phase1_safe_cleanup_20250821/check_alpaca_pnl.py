#!/usr/bin/env python3
"""
Check Alpaca Account P&L - Get actual trading performance
"""

import sys
import os
from pathlib import Path
from datetime import date, timedelta, datetime
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv

# Load environment
load_dotenv()

def check_alpaca_pnl():
    """Check Alpaca's actual P&L data"""
    
    # Initialize API
    api = tradeapi.REST(
        os.getenv('ALPACA_API_KEY'),
        os.getenv('ALPACA_SECRET_KEY'),
        os.getenv('ALPACA_BASE_URL'),
        api_version='v2'
    )
    
    print("📊 Alpaca Account P&L Check")
    print("=" * 40)
    
    try:
        # Get account info
        account = api.get_account()
        
        print(f"\n💼 Current Account Status:")
        print(f"   Portfolio Value: ${float(account.portfolio_value):,.2f}")
        print(f"   Cash: ${float(account.cash):,.2f}")
        print(f"   Buying Power: ${float(account.buying_power):,.2f}")
        
        # Check what P&L fields are available
        print(f"\n📈 Available P&L Fields:")
        pnl_fields = [attr for attr in dir(account) if 'pnl' in attr.lower() or 'pl' in attr.lower()]
        for field in pnl_fields:
            try:
                value = getattr(account, field)
                print(f"   {field}: {value}")
            except:
                print(f"   {field}: [unable to access]")
        
        # Get portfolio history
        print(f"\n📊 Portfolio History:")
        try:
            # Try different approaches for portfolio history
            portfolio_history = api.get_portfolio_history(
                period='1M',
                timeframe='1D'
            )
            
            if portfolio_history:
                print(f"   History available: ✅")
                if hasattr(portfolio_history, 'profit_loss') and portfolio_history.profit_loss:
                    recent_pnl = portfolio_history.profit_loss[-1] if portfolio_history.profit_loss else 0
                    print(f"   Most recent P&L: ${recent_pnl:.2f}")
                    
                    # Show last few days if available
                    if len(portfolio_history.profit_loss) > 1:
                        print(f"   Recent P&L history:")
                        for i, pnl in enumerate(portfolio_history.profit_loss[-5:]):
                            print(f"     Day {i-4}: ${pnl:.2f}")
                else:
                    print(f"   No P&L data in portfolio history")
            else:
                print(f"   No portfolio history available")
                
        except Exception as e:
            print(f"   ❌ Portfolio history error: {str(e)}")
        
        # Check positions
        print(f"\n📋 Current Positions:")
        try:
            positions = api.list_positions()
            if positions:
                total_unrealized = 0
                for pos in positions:
                    unrealized_pnl = float(pos.unrealized_pnl)
                    total_unrealized += unrealized_pnl
                    print(f"   {pos.symbol}: {pos.qty} shares, P&L: ${unrealized_pnl:.2f}")
                print(f"   Total Unrealized P&L: ${total_unrealized:.2f}")
            else:
                print(f"   No open positions")
        except Exception as e:
            print(f"   ❌ Positions error: {str(e)}")
            
        # Get orders to see if there were any failures
        print(f"\n📝 Recent Orders:")
        try:
            orders = api.list_orders(
                status='all',
                limit=10,
                after=datetime(2025, 8, 19).isoformat()
            )
            
            if orders:
                filled_orders = [o for o in orders if o.status == 'filled']
                cancelled_orders = [o for o in orders if o.status == 'cancelled']
                
                print(f"   Filled orders: {len(filled_orders)}")
                print(f"   Cancelled orders: {len(cancelled_orders)}")
                
                if cancelled_orders:
                    print(f"   Recent cancelled orders:")
                    for order in cancelled_orders[:3]:
                        print(f"     {order.symbol} {order.side} {order.qty} @ {order.limit_price or 'market'}")
            else:
                print(f"   No recent orders found")
                
        except Exception as e:
            print(f"   ❌ Orders error: {str(e)}")
            
    except Exception as e:
        print(f"❌ Error accessing account: {str(e)}")
    
    print(f"\n🤔 Key Question:")
    print(f"   If Alpaca shows ~$61 P&L for 8/19, but cash flow is -$1,147.27,")
    print(f"   this suggests positions were opened on 8/18 and closed on 8/19")
    print(f"   making the actual trading profit much different from cash flow.")

if __name__ == "__main__":
    check_alpaca_pnl()
