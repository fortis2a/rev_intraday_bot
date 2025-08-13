#!/usr/bin/env python3
"""
Trailing Stop Test Script
Demonstrates and tests trailing stop functionality
"""

import sys
from pathlib import Path
# Add parent directory to path to access main modules
sys.path.append(str(Path(__file__).parent.parent))

import time
from config import config
from data_manager import DataManager
from order_manager import OrderManager
from core.trailing_stop_manager import TrailingStopManager
from logger import setup_logger

def test_trailing_stop_system():
    """Test the trailing stop system with simulated price movements"""
    logger = setup_logger("trailing_stop_test")
    
    print("=" * 60)
    print("🎯 TRAILING STOP SYSTEM TEST")
    print("=" * 60)
    
    # Display configuration
    print(f"📊 CONFIGURATION:")
    print(f"  Trailing Stop Enabled: {config['TRAILING_STOP_ENABLED']}")
    print(f"  Trailing Distance: {config['TRAILING_STOP_PCT']:.1%}")
    print(f"  Activation Threshold: {config['TRAILING_STOP_ACTIVATION']:.1%}")
    print(f"  Minimum Move: {config['TRAILING_STOP_MIN_MOVE']:.1%}")
    print(f"  Initial Stop Loss: {config['STOP_LOSS_PCT']:.1%}")
    print(f"  Take Profit: {config['TAKE_PROFIT_PCT']:.1%}")
    
    # Initialize managers
    try:
        data_manager = DataManager()
        order_manager = OrderManager(data_manager)
        trailing_manager = order_manager.trailing_stop_manager
        
        # Test symbol and entry
        test_symbol = "IONQ"
        entry_price = 100.00
        quantity = 10
        
        print(f"\n📍 SIMULATED POSITION:")
        print(f"  Symbol: {test_symbol}")
        print(f"  Entry Price: ${entry_price:.2f}")
        print(f"  Quantity: {quantity} shares")
        print(f"  Position Value: ${entry_price * quantity:.2f}")
        
        # Add position to trailing stop manager
        initial_stop = entry_price * (1 - config['STOP_LOSS_PCT'])
        trailing_manager.add_position(
            symbol=test_symbol,
            entry_price=entry_price,
            quantity=quantity,
            side='long',
            initial_stop_price=initial_stop
        )
        
        # Simulate price movements
        price_scenarios = [
            (100.50, "Small move up (+0.5%)"),
            (101.00, "Move up (+1.0%)"),
            (101.50, "ACTIVATION THRESHOLD (+1.5%)"),  # Should activate trailing
            (102.00, "Further move up (+2.0%)"),
            (103.00, "Strong move up (+3.0%)"),
            (102.50, "Small pullback (+2.5%)"),
            (102.00, "Larger pullback (+2.0%)"),
            (101.50, "Back to activation level (+1.5%)"),
            (101.00, "Below activation (+1.0%)"),
            (100.50, "Further down (+0.5%)"),
            (100.00, "Back to entry (0.0%)"),
            (99.50, "Below entry (-0.5%)"),
            (99.00, "STOP TRIGGERED (-1.0%)"),
        ]
        
        print(f"\n🎬 SIMULATING PRICE MOVEMENTS:")
        print("=" * 60)
        
        for i, (price, description) in enumerate(price_scenarios, 1):
            print(f"\n[Step {i}] Price: ${price:.2f} - {description}")
            
            # Update position with new price
            update_info = trailing_manager.update_position_price(test_symbol, price)
            
            # Get current status
            status = trailing_manager.get_position_status(test_symbol)
            
            if status:
                trailing_active = "🚀 ACTIVE" if status['is_trailing_active'] else "⏳ WAITING"
                print(f"  Status: {trailing_active}")
                print(f"  Current Profit: {status['profit_pct']:.1%} (${status['unrealized_pnl']:.2f})")
                print(f"  Trailing Stop: ${status['trailing_stop_price']:.2f}")
                print(f"  Protected Profit: {status['profit_protected_pct']:.1%}")
                print(f"  Distance to Stop: {status['distance_to_stop']:.1%}")
                
                if update_info:
                    print(f"  🔄 STOP UPDATED: ${update_info['old_stop_price']:.2f} → ${update_info['new_stop_price']:.2f}")
            
            # Check if stop triggered
            if trailing_manager.check_stop_triggered(test_symbol, price):
                print(f"  🛑 STOP TRIGGERED! Position would be closed.")
                break
            
            # Small delay for readability
            time.sleep(0.1)
        
        # Final summary
        print(f"\n" + "=" * 60)
        print("📊 FINAL SUMMARY")
        print("=" * 60)
        
        final_status = trailing_manager.get_position_status(test_symbol)
        if final_status:
            print(f"Entry Price: ${final_status['entry_price']:.2f}")
            print(f"Final Price: ${final_status['current_price']:.2f}")
            print(f"Highest Price: ${final_status['highest_price']:.2f}")
            print(f"Final Stop: ${final_status['trailing_stop_price']:.2f}")
            print(f"Final Profit: {final_status['profit_pct']:.1%} (${final_status['unrealized_pnl']:.2f})")
            
            if final_status['is_trailing_active']:
                print(f"Protected Profit: {final_status['profit_protected_pct']:.1%}")
                protected_amount = final_status['profit_protected_pct'] * entry_price * quantity
                print(f"Protected Amount: ${protected_amount:.2f}")
        
        # Clean up
        trailing_manager.remove_position(test_symbol, "Test completed")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

def demonstrate_trailing_vs_fixed_stop():
    """Compare trailing stop vs fixed stop performance"""
    print("\n" + "=" * 60)
    print("📊 TRAILING STOP vs FIXED STOP COMPARISON")
    print("=" * 60)
    
    entry_price = 100.00
    quantity = 10
    
    # Fixed stop scenario
    fixed_stop = entry_price * (1 - config['STOP_LOSS_PCT'])  # $98.00
    
    # Price scenarios
    scenarios = [
        ("Scenario 1: Small gain then reversal", [100, 102, 99]),
        ("Scenario 2: Large gain then reversal", [100, 110, 105]),
        ("Scenario 3: Steady uptrend", [100, 105, 108, 106]),
    ]
    
    for scenario_name, prices in scenarios:
        print(f"\n🎯 {scenario_name}")
        print(f"Prices: {' → '.join([f'${p:.2f}' for p in prices])}")
        
        # Fixed stop result
        final_price = prices[-1]
        if final_price <= fixed_stop:
            fixed_result = f"STOPPED OUT at ${fixed_stop:.2f} (Loss: ${(fixed_stop - entry_price) * quantity:.2f})"
        else:
            fixed_result = f"Still holding at ${final_price:.2f} (P&L: ${(final_price - entry_price) * quantity:.2f})"
        
        # Trailing stop simulation
        trailing_stop = entry_price * (1 - config['STOP_LOSS_PCT'])
        highest_price = entry_price
        trailing_active = False
        
        for price in prices[1:]:  # Skip entry price
            highest_price = max(highest_price, price)
            
            # Check if trailing should activate
            activation_threshold = entry_price * (1 + config['TRAILING_STOP_ACTIVATION'])
            if not trailing_active and price >= activation_threshold:
                trailing_active = True
            
            # Update trailing stop if active
            if trailing_active:
                new_trailing_stop = highest_price * (1 - config['TRAILING_STOP_PCT'])
                trailing_stop = max(trailing_stop, new_trailing_stop)
        
        final_price = prices[-1]
        if final_price <= trailing_stop:
            trailing_result = f"STOPPED OUT at ${trailing_stop:.2f} (P&L: ${(trailing_stop - entry_price) * quantity:.2f})"
        else:
            trailing_result = f"Still holding at ${final_price:.2f} (P&L: ${(final_price - entry_price) * quantity:.2f})"
        
        print(f"  Fixed Stop ({config['STOP_LOSS_PCT']:.1%}):   {fixed_result}")
        print(f"  Trailing Stop: {trailing_result}")
        
        # Calculate advantage
        if final_price <= fixed_stop and final_price > trailing_stop:
            advantage = (trailing_stop - fixed_stop) * quantity
            print(f"  🎯 Trailing Stop Advantage: ${advantage:.2f}")
        elif final_price > fixed_stop and final_price <= trailing_stop:
            advantage = (fixed_stop - trailing_stop) * quantity
            print(f"  📊 Fixed Stop Advantage: ${advantage:.2f}")
        else:
            print(f"  🤝 Same result for both approaches")

if __name__ == "__main__":
    print("🚀 Starting Trailing Stop System Tests...")
    
    # Test 1: Full system test
    test_trailing_stop_system()
    
    # Test 2: Comparison demonstration
    demonstrate_trailing_vs_fixed_stop()
    
    print(f"\n✅ All tests completed!")
    print(f"📝 Check logs for detailed trailing stop activity")
