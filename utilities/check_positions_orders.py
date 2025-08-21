#!/usr/bin/env python3
"""Check positions vs orders"""

from alpaca.trading.client import TradingClient
from config import ALPACA_API_KEY, ALPACA_SECRET_KEY

def check_positions_and_orders():
    client = TradingClient(ALPACA_API_KEY, ALPACA_SECRET_KEY, paper=True)
    
    # Get positions
    positions = client.get_all_positions()
    print("=== OPEN POSITIONS ===")
    for p in positions:
        print(f"{p.symbol}: {p.qty} shares at ${p.avg_entry_price} (Side: {p.side})")
    print(f"Total Positions: {len(positions)}")
    
    # Get orders
    orders = client.get_orders()
    active_orders = [o for o in orders if o.status == 'new']
    
    print("\n=== ACTIVE ORDERS ===")
    for o in active_orders:
        print(f"{o.symbol}: {o.side} {o.qty} at ${o.limit_price or 'MARKET'} (Type: {o.order_type}, Status: {o.status})")
    print(f"Total Active Orders: {len(active_orders)}")
    
    # Analyze relationship
    print("\n=== ANALYSIS ===")
    for pos in positions:
        matching_orders = [o for o in active_orders if o.symbol == pos.symbol]
        if matching_orders:
            print(f"{pos.symbol} Position: {pos.qty} {pos.side}")
            for order in matching_orders:
                print(f"  -> Active Order: {order.side} {order.qty} ({order.order_type})")

if __name__ == "__main__":
    check_positions_and_orders()
