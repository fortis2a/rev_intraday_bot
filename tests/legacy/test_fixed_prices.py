#!/usr/bin/env python3
"""
Test the fixed price calculation (legacy diagnostic)
"""
import pytest
pytestmark = pytest.mark.legacy

from core.data_manager import DataManager

def test_fixed_prices():
    dm = DataManager()
    
    print("🔧 TESTING FIXED PRICE CALCULATION")
    print("=" * 50)
    
    # Test JNJ specifically
    jnj_data = dm.get_current_market_data('JNJ', force_fresh=True)
    if jnj_data:
        print(f"JNJ Fixed Price: ${jnj_data['price']:.2f}")
        print(f"JNJ Bid: ${jnj_data['bid']:.2f}")
        print(f"JNJ Ask: ${jnj_data['ask']:.2f}")
        print(f"JNJ Spread: {jnj_data['spread_pct']:.3f}%")
        print(f"Source: {jnj_data.get('source', 'Unknown')}")
        
        # Verify the fix worked
        if jnj_data['ask'] == 0.0 and jnj_data['price'] == jnj_data['bid']:
            print("✅ Fix working: Using bid price when ask is invalid")
        elif jnj_data['price'] == (jnj_data['bid'] + jnj_data['ask']) / 2:
            print("✅ Fix working: Using mid-price when both valid")
        else:
            print("⚠️ Unexpected price calculation")
    else:
        print("❌ Failed to get JNJ data")
    
    # Test PG as well
    print()
    pg_data = dm.get_current_market_data('PG', force_fresh=True)
    if pg_data:
        print(f"PG Price: ${pg_data['price']:.2f}")
        print(f"PG Bid: ${pg_data['bid']:.2f}")
        print(f"PG Ask: ${pg_data['ask']:.2f}")
        print(f"PG Spread: {pg_data['spread_pct']:.3f}%")
        
        # Verify the fix
        if pg_data['ask'] > 0 and pg_data['bid'] > 0:
            expected_mid = (pg_data['bid'] + pg_data['ask']) / 2
            if abs(pg_data['price'] - expected_mid) < 0.01:
                print("✅ Fix working: Correct mid-price calculation")
            else:
                print(f"⚠️ Price mismatch: {pg_data['price']:.2f} vs expected {expected_mid:.2f}")

if __name__ == "__main__":
    test_fixed_prices()
