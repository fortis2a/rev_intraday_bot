#!/usr/bin/env python3
"""
Debug the $83.65 JNJ price calculation issue
"""

def debug_price_calculation():
    print("🔍 DEBUGGING JNJ PRICE CALCULATION")
    print("=" * 50)
    
    # From the test output, we know:
    bid = 167.30
    ask = 0.00  # This is the problem!
    
    print(f"Raw Alpaca Data:")
    print(f"   JNJ Bid: ${bid:.2f}")
    print(f"   JNJ Ask: ${ask:.2f}")
    print()
    
    # Current calculation in data_manager.py line 318:
    mid_price = float(ask + bid) / 2
    
    print(f"Current Calculation:")
    print(f"   mid_price = (ask + bid) / 2")
    print(f"   mid_price = ({ask} + {bid}) / 2")
    print(f"   mid_price = {ask + bid} / 2")
    print(f"   mid_price = ${mid_price:.2f}")
    print()
    
    print(f"🚨 PROBLEM IDENTIFIED:")
    print(f"   • Ask price is $0.00 (invalid/stale after-hours data)")
    print(f"   • Mid-price calculation gives wrong result: ${mid_price:.2f}")
    print(f"   • Should use bid price when ask is invalid")
    print()
    
    # Better calculation logic:
    print(f"✅ CORRECT CALCULATION:")
    if ask <= 0:
        corrected_price = bid
        print(f"   • Ask is invalid ($0.00), use bid price: ${corrected_price:.2f}")
    elif bid <= 0:
        corrected_price = ask
        print(f"   • Bid is invalid, use ask price: ${corrected_price:.2f}")
    else:
        corrected_price = (ask + bid) / 2
        print(f"   • Both valid, use mid-price: ${corrected_price:.2f}")
    
    print()
    print(f"🎯 REAL JNJ PRICE: ${corrected_price:.2f} (not ${mid_price:.2f})")

if __name__ == "__main__":
    debug_price_calculation()
