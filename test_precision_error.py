#!/usr/bin/env python3
"""
Test for the specific precision error that was occurring
"""

from utils.price_utils import round_to_cent, calculate_stop_loss_price

def test_specific_error():
    """Test the specific case that was causing sub-penny errors"""
    
    print("=== Testing Specific Sub-Penny Error Case ===\n")
    
    # Let's create a case that would produce 28.348300000000002
    # Working backwards: if stop price is 28.3483..., what was the original price?
    # If stop_price = price * (1 - 0.019), then price = stop_price / (1 - 0.019)
    
    # Let's try a case that would produce floating point errors
    test_price = 28.90132  # A price with more precision
    stop_loss_pct = 0.01929  # A percentage with more precision
    
    print(f"Test Price: ${test_price}")
    print(f"Stop Loss %: {stop_loss_pct:.5%}")
    
    # Calculate using floating point arithmetic (problematic)
    raw_calculation = test_price * (1 - stop_loss_pct)
    rounded_old = round(raw_calculation, 2)
    
    print(f"Raw calculation: {raw_calculation}")
    print(f"Old round method: {rounded_old}")
    print(f"Has precision beyond 2 decimals: {raw_calculation != rounded_old}")
    
    # Calculate using our new method
    new_calculation = calculate_stop_loss_price(test_price, stop_loss_pct)
    print(f"New method: {new_calculation}")
    print(f"New method type: {type(new_calculation)}")
    
    # Check if they're equal
    print(f"Results equal: {rounded_old == new_calculation}")
    
    # Test a bunch of random prices that might cause floating point errors
    print("\n" + "="*60)
    print("Testing Random Prices for Floating Point Errors:")
    
    import random
    random.seed(42)  # For reproducible results
    
    problem_cases = []
    
    for i in range(50):
        price = random.uniform(10, 100)
        pct = random.uniform(0.005, 0.05)
        
        raw = price * (1 - pct)
        old_rounded = round(raw, 2)
        new_method = calculate_stop_loss_price(price, pct)
        
        # Check for precision differences
        precision_diff = abs(raw - old_rounded)
        if precision_diff > 1e-10:
            problem_cases.append((price, pct, raw, old_rounded, new_method))
    
    print(f"Found {len(problem_cases)} cases with precision issues:")
    
    for price, pct, raw, old, new in problem_cases[:5]:  # Show first 5
        print(f"Price: ${price:.6f}, Stop%: {pct:.4%}")
        print(f"  Raw: {raw}")
        print(f"  Old: {old}, New: {new}")
        print(f"  Precision diff: {abs(raw - old):.2e}")
        print()

if __name__ == "__main__":
    test_specific_error()
