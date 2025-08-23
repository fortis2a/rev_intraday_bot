#!/usr/bin/env python3
"""
Debug script to check engine status and configuration
"""

from config import config
from core.data_manager import DataManager


def main():
    print("=== ENGINE DEBUG DIAGNOSTICS ===")

    # Check risk limits
    print(f"MAX_DAILY_LOSS: ${config['MAX_DAILY_LOSS']}")
    print(f"MAX_POSITIONS: {config['MAX_POSITIONS']}")
    print(f"WATCHLIST: {config['INTRADAY_WATCHLIST']}")

    # Check data manager
    try:
        dm = DataManager()
        account_info = dm.get_account_info()
        if account_info:
            print(f"Account Equity: ${account_info['equity']:,.2f}")
            print(f"Account Cash: ${account_info['cash']:,.2f}")

        positions = dm.get_positions()
        print(f"Current Positions: {len(positions)}")

        # Check if market is open
        market_status = dm.get_market_status()
        print(f"Market Open: {market_status.get('is_open', 'Unknown')}")

    except Exception as e:
        print(f"Data Manager Error: {e}")

    print("=== END DIAGNOSTICS ===")


if __name__ == "__main__":
    main()
