#!/usr/bin/env python3
"""
Debug script to test risk limits check
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import config
from core.data_manager import DataManager


def test_risk_limits():
    print("=== RISK LIMITS DEBUG ===")

    # Initialize data manager
    dm = DataManager()

    # Check daily P&L (simulate main.py logic)
    daily_pnl = 0.0  # This should be calculated from actual trades
    print(f"Daily P&L: ${daily_pnl:.2f}")
    print(f"Max Daily Loss Limit: ${config['MAX_DAILY_LOSS']}")
    print(
        f"Risk Check - Daily Loss: {daily_pnl <= -config['MAX_DAILY_LOSS']} (should be False)"
    )

    # Check maximum positions
    positions = dm.get_positions()
    print(f"Current Positions: {len(positions)}")
    print(f"Max Positions Limit: {config['MAX_POSITIONS']}")
    print(
        f"Risk Check - Max Positions: {len(positions) >= config['MAX_POSITIONS']} (should be False)"
    )

    # Overall risk check result
    risk_daily_loss = daily_pnl <= -config["MAX_DAILY_LOSS"]
    risk_max_positions = len(positions) >= config["MAX_POSITIONS"]
    risk_check_passes = not risk_daily_loss and not risk_max_positions

    print(f"\nOverall Risk Check Result: {risk_check_passes} (should be True)")

    if not risk_check_passes:
        print("❌ RISK LIMITS FAILED - This would stop the engine!")
        if risk_daily_loss:
            print(
                f"   - Daily loss limit exceeded: ${daily_pnl:.2f} <= -${config['MAX_DAILY_LOSS']}"
            )
        if risk_max_positions:
            print(
                f"   - Maximum positions limit exceeded: {len(positions)} >= {config['MAX_POSITIONS']}"
            )
    else:
        print("✅ Risk limits check would pass")


if __name__ == "__main__":
    test_risk_limits()
