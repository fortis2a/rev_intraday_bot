#!/usr/bin/env python3
"""
🎯 Stock Watchlist Configuration
Easy way to customize which stocks your intraday trading bot trades
"""

# =============================================================================
# 🚀 CUSTOM STOCK WATCHLISTS - EDIT THESE LISTS
# =============================================================================

# Option 1: Conservative Watchlist (Lower Risk, High Volume)
CONSERVATIVE_WATCHLIST = [
    # Blue chip tech stocks
    "AAPL", "MSFT", "GOOGL", "AMZN",
    
    # Large cap financial 
    "JPM", "BAC", "V", "MA",
    
    # Popular ETFs (most stable for scalping)
    "SPY", "QQQ", "IWM"
]

# Option 2: Aggressive Watchlist (Higher Risk, Higher Reward)
AGGRESSIVE_WATCHLIST = [
    # High volatility tech
    "TSLA", "NVDA", "AMD", "NFLX",
    
    # Momentum stocks
    "UBER", "ROKU", "ZOOM", "SHOP",
    
    # Biotech/Pharma momentum
    "MRNA", "BNTX", "GILD",
    
    # Crypto-related stocks
    "COIN", "MSTR", "RIOT"
]

# Option 3: Sector Focused (Customize by sector)
TECH_FOCUSED = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "AMD", "NFLX", "CRM"
]

FINANCE_FOCUSED = [
    "JPM", "BAC", "WFC", "C", "GS", "MS", "V", "MA", "AXP", "BLK"
]

ENERGY_FOCUSED = [
    "XOM", "CVX", "COP", "SLB", "EOG", "PXD", "MPC", "VLO"
]

# Option 4: ETF Only (Safest for beginners)
ETF_ONLY = [
    "SPY",   # S&P 500
    "QQQ",   # NASDAQ 100
    "IWM",   # Russell 2000
    "XLF",   # Financial Select
    "XLK",   # Technology Select
    "XLE",   # Energy Select
    "XLV",   # Health Care Select
    "GDX",   # Gold Miners
    "USO",   # Oil Fund
    "TLT"    # 20+ Year Treasury
]

# Option 5: Custom Small List (Your specific picks)
MY_CUSTOM_STOCKS = [
    # Quantum Computing Focus - Multi Stock Strategy
    "IONQ",  # IonQ (Pure Quantum Play)
    "PG",   # Procter & Gamble (Stable Consumer Goods)
    "QBTS",  # D-Wave Quantum (Quantum Annealing)
    "RGTI",  # Rigetti Computing (Quantum Cloud Services)
    "JNJ"  # Johnson & Johnson (Stable Healthcare)
]

# Option 6: Alternative custom list (no IONQ to avoid conflicts)
MY_ALTERNATIVE_STOCKS = [
    # High-volume alternatives
    "AAPL", "MSFT", "SPY"
]

# =============================================================================
# 🎯 CHOOSE YOUR WATCHLIST - UNCOMMENT ONE LINE BELOW
# =============================================================================

# Choose which watchlist to use (uncomment ONE of these lines):
#ACTIVE_WATCHLIST = CONSERVATIVE_WATCHLIST    # Safe choice for beginners
ACTIVE_WATCHLIST = MY_CUSTOM_STOCKS    # Quantum focus

# ACTIVE_WATCHLIST = AGGRESSIVE_WATCHLIST    # For experienced traders
# ACTIVE_WATCHLIST = TECH_FOCUSED           # Tech sector focus
# ACTIVE_WATCHLIST = FINANCE_FOCUSED        # Financial sector focus
# ACTIVE_WATCHLIST = ENERGY_FOCUSED         # Energy sector focus
# ACTIVE_WATCHLIST = ETF_ONLY               # ETFs only (safest)
# ACTIVE_WATCHLIST = MY_CUSTOM_STOCKS       # Your custom list

# =============================================================================
# 🔧 STOCK FILTERING CRITERIA
# =============================================================================

# The bot will automatically filter stocks based on these criteria:
# - Minimum daily volume: 1,000,000 shares
# - Price range: $10 - $200
# - Maximum bid-ask spread: 0.1%
# - Volatility range: 0.5% - 5.0% daily

# You can modify these in config.py if needed:
# MIN_VOLUME = 1000000
# MIN_PRICE = 10.0  
# MAX_PRICE = 200.0
# MAX_SPREAD_PCT = 0.1
# MIN_VOLATILITY = 0.5
# MAX_VOLATILITY = 5.0

# =============================================================================
# 📊 USAGE EXAMPLES
# =============================================================================

if __name__ == "__main__":
    print("🎯 Stock Watchlist Configuration")
    print("=" * 50)
    print(f"Active Watchlist: {len(ACTIVE_WATCHLIST)} stocks")
    print(f"Stocks: {', '.join(ACTIVE_WATCHLIST)}")
    print("\n📝 To change stocks:")
    print("1. Edit one of the watchlists above")
    print("2. Or uncomment a different ACTIVE_WATCHLIST")
    print("3. Or create your own MY_CUSTOM_STOCKS list")
    print("\n🚀 Ready for intraday trading with these stocks!")
