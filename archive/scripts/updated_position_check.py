#!/usr/bin/env python3
"""
Updated position limits check with correct JNJ price
"""

def check_updated_limits():
    # Updated prices
    pg_price = 150.23
    jnj_price = 167.11  # Corrected price
    position_limit = 800.0
    
    print("🔍 Updated Position Limits Analysis")
    print("=" * 50)
    
    # PG calculation
    pg_10_shares = pg_price * 10
    print(f"📊 PG: ${pg_price:.2f} per share")
    print(f"💰 10 shares of PG: ${pg_10_shares:.2f}")
    print(f"🚫 Exceeds $800 limit: {pg_10_shares > position_limit}")
    if pg_10_shares > position_limit:
        max_pg_shares = int(position_limit / pg_price)
        print(f"✅ Max PG shares at $800 limit: {max_pg_shares} shares (${max_pg_shares * pg_price:.2f})")
    
    print()
    
    # JNJ calculation with corrected price
    jnj_10_shares = jnj_price * 10
    print(f"📊 JNJ: ${jnj_price:.2f} per share")
    print(f"💰 10 shares of JNJ: ${jnj_10_shares:.2f}")
    print(f"🚫 Exceeds $800 limit: {jnj_10_shares > position_limit}")
    if jnj_10_shares > position_limit:
        max_jnj_shares = int(position_limit / jnj_price)
        print(f"✅ Max JNJ shares at $800 limit: {max_jnj_shares} shares (${max_jnj_shares * jnj_price:.2f})")
    
    print()
    print("📋 Summary:")
    print(f"   • Current MAX_POSITION_VALUE: ${position_limit:.0f}")
    print(f"   • PG: {'❌ Cannot' if pg_10_shares > position_limit else '✅ Can'} trade 10 shares")
    print(f"   • JNJ: {'❌ Cannot' if jnj_10_shares > position_limit else '✅ Can'} trade 10 shares")
    
    if jnj_10_shares > position_limit or pg_10_shares > position_limit:
        required_limit = max(pg_10_shares, jnj_10_shares)
        print()
        print("💡 To allow 10 shares of both stocks:")
        print(f"   • Increase MAX_POSITION_VALUE to ${required_limit:.0f}")

if __name__ == "__main__":
    check_updated_limits()
