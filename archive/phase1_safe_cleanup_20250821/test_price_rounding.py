#!/usr/bin/env python3
"""
Test price rounding utilities to ensure they fix sub-penny precision errors
"""

from utils.price_utils import (
    round_to_cent, 
    calculate_stop_loss_price, 
    calculate_take_profit_price,
    calculate_trailing_stop_price,
    validate_price_precision
)

def test_price_rounding():
    """Test various price calculations to ensure proper rounding"""
    
    print("=== Testing Price Rounding Utilities ===\n")
    
    # Test case that was causing the error: 28.348300000000002
    test_price = 28.9
    stop_loss_pct = 0.019  # 1.9%
    
    print(f"Test Case: Current Price = ${test_price}")
    print(f"Stop Loss Percentage = {stop_loss_pct:.3%}")
    
    # Old method (problematic)
    old_method = round(test_price * (1 - stop_loss_pct), 2)
    print(f"Old Method Result: {old_method}")
    print(f"Precision Issue? {abs(old_method - round(old_method, 2)) > 1e-10}")
    
    # New method (fixed)
    new_method = calculate_stop_loss_price(test_price, stop_loss_pct)
    print(f"New Method Result: {new_method}")
    print(f"Precision Valid? {validate_price_precision(new_method, 'test')}")
    
    print("\n" + "="*50)
    
    # Test multiple problematic cases
    test_cases = [
        (28.9, 0.019),  # Original problem case
        (15.67, 0.025), # Another potential issue
        (42.33, 0.015), # Different percentage
        (100.50, 0.005), # Small percentage
        (9.99, 0.050),  # Large percentage
    ]
    
    print("Testing Multiple Cases:")
    print("Price\t| Stop%\t| Old Method\t| New Method\t| Valid?")
    print("-" * 60)
    
    for price, pct in test_cases:
        old = round(price * (1 - pct), 2)
        new = calculate_stop_loss_price(price, pct)
        valid = validate_price_precision(new, 'test')
        
        print(f"${price:.2f}\t| {pct:.1%}\t| {old:.6f}\t| {new:.2f}\t\t| {valid}")
    
    print("\n" + "="*50)
    print("Testing Trailing Stop Calculations:")
    
    # Test trailing stop calculations
    highest_prices = [30.15, 25.67, 45.89]
    trailing_pcts = [0.015, 0.020, 0.025]
    
    for highest, trail_pct in zip(highest_prices, trailing_pcts):
        old_trail = round(highest * (1 - trail_pct), 2)
        new_trail = calculate_trailing_stop_price(highest, trail_pct)
        valid = validate_price_precision(new_trail, 'trail_test')
        
        print(f"Highest: ${highest:.2f}, Trail: {trail_pct:.1%}")
        print(f"  Old: {old_trail:.6f}, New: ${new_trail:.2f}, Valid: {valid}")

if __name__ == "__main__":
    test_price_rounding()
