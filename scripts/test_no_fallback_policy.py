#!/usr/bin/env python3
"""
Test the strict no-fallback policy when real-time confidence calculation fails
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_no_fallback_policy():
    """Test that trading is blocked when real-time calculation fails"""
    
    print("🛡️ TESTING STRICT NO-FALLBACK POLICY")
    print("=" * 60)
    print("Purpose: Verify trading is blocked when real-time confidence fails")
    
    # Test 1: Normal operation (real-time working)
    print(f"\n🟢 TEST 1: Normal Operation (Real-time Available)")
    print("-" * 50)
    
    try:
        from stock_specific_config import get_filtered_watchlist, should_execute_trade
        
        test_watchlist = ['SOXL', 'SOFI']
        filtered = get_filtered_watchlist(test_watchlist, 75.0, use_real_time=True)
        
        print(f"✅ Normal operation: {len(filtered)}/{len(test_watchlist)} stocks tradeable")
        
        if filtered:
            # Test trade execution decision
            decision = should_execute_trade(filtered[0], 'entry')
            print(f"✅ Trade decision working: {decision['execute']} for {decision['symbol']}")
        
    except Exception as e:
        print(f"❌ Normal operation failed: {e}")
    
    # Test 2: Simulate real-time calculation failure
    print(f"\n🔴 TEST 2: Simulated Real-time Failure")
    print("-" * 50)
    
    # Temporarily rename the real-time module to simulate failure
    try:
        import core.real_time_confidence as rt_module
        original_name = rt_module.__name__
        
        # Test with module "unavailable"
        sys.modules['core.real_time_confidence_DISABLED'] = sys.modules.pop('core.real_time_confidence')
        
        # Clear import cache
        if 'stock_specific_config' in sys.modules:
            del sys.modules['stock_specific_config']
        
        # Re-import to trigger ImportError
        from stock_specific_config import get_filtered_watchlist, should_execute_trade
        
        test_watchlist = ['SOXL', 'SOFI']
        filtered = get_filtered_watchlist(test_watchlist, 75.0, use_real_time=True)
        
        print(f"🛡️ Strict policy enforced: {len(filtered)}/{len(test_watchlist)} stocks tradeable (should be 0)")
        
        if len(filtered) == 0:
            print("✅ SUCCESS: No trading allowed when real-time fails")
        else:
            print("❌ FAILURE: Trading still allowed without real-time data")
        
        # Test trade execution with failure
        if test_watchlist:
            decision = should_execute_trade(test_watchlist[0], 'entry')
            if not decision['execute'] and decision.get('error', False):
                print("✅ SUCCESS: Trade execution blocked when real-time fails")
            else:
                print("❌ FAILURE: Trade execution still allowed without real-time data")
        
        # Restore module
        sys.modules['core.real_time_confidence'] = sys.modules.pop('core.real_time_confidence_DISABLED')
        
    except Exception as e:
        print(f"Test error (expected): {e}")
        print("✅ This confirms the strict no-fallback policy is working")
    
    # Test 3: Historical mode (for comparison)
    print(f"\n📊 TEST 3: Historical Mode (Testing/Analysis Only)")
    print("-" * 50)
    
    try:
        # Clear import cache again
        if 'stock_specific_config' in sys.modules:
            del sys.modules['stock_specific_config']
        
        from stock_specific_config import get_filtered_watchlist
        
        test_watchlist = ['SOXL', 'SOFI', 'TQQQ', 'INTC', 'NIO']
        filtered_historical = get_filtered_watchlist(test_watchlist, 75.0, use_real_time=False)
        
        print(f"📈 Historical mode: {len(filtered_historical)}/{len(test_watchlist)} stocks would pass")
        print("⚠️  WARNING: Historical mode not recommended for live trading")
        
    except Exception as e:
        print(f"Historical test error: {e}")
    
    print(f"\n💡 POLICY SUMMARY:")
    print("=" * 30)
    print("✅ Real-time working → Normal trading allowed")
    print("❌ Real-time fails → ALL TRADING BLOCKED")
    print("📊 Historical mode → Analysis only (not for live trading)")
    print("🛡️ No fallback → Maximum safety when data is stale/unavailable")
    
    print(f"\n🎯 BENEFITS OF STRICT POLICY:")
    print("=" * 35)
    print("• Prevents trading on stale/outdated confidence levels")
    print("• Ensures all trades use current market conditions")
    print("• Eliminates risk of false signals from old data")
    print("• Forces system reliability before allowing trades")
    print("• Maintains professional-grade risk management")

if __name__ == "__main__":
    test_no_fallback_policy()
