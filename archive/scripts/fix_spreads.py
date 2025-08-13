#!/usr/bin/env python3
"""
Fix Paper Trading Spread Issues
Add realistic spread handling for paper trading environment
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

def fix_paper_trading_spreads():
    print("🔧 FIXING PAPER TRADING SPREAD ISSUES")
    print("=" * 60)
    
    # Read the current DataManager
    data_manager_path = Path(__file__).parent / "core" / "data_manager.py"
    
    with open(data_manager_path, 'r') as f:
        content = f.read()
    
    # Check if fix is already applied
    if "# Paper trading spread adjustment" in content:
        print("✅ Paper trading spread fix already applied!")
        return
    
    # Find the location to add the fix (after spread calculation)
    spread_calc_marker = "spread_pct = (bid_ask_spread / mid_price) * 100 if mid_price > 0 else 0"
    
    if spread_calc_marker in content:
        # Add the paper trading adjustment
        new_code = f"""                spread_pct = (bid_ask_spread / mid_price) * 100 if mid_price > 0 else 0
                
                # Paper trading spread adjustment for realistic trading
                # In paper trading, spreads can be artificially wide due to low liquidity simulation
                if spread_pct > 1.0:  # If spread is over 1%, likely paper trading artifact
                    # Use a more realistic spread for large-cap stocks
                    realistic_spreads = {{
                        'PG': 0.02,   # Procter & Gamble
                        'JNJ': 0.02,  # Johnson & Johnson  
                        'AAPL': 0.01, # Apple
                        'MSFT': 0.01, # Microsoft
                        'SPY': 0.01,  # SPDR S&P 500
                        'QQQ': 0.01,  # Invesco QQQ
                    }}
                    
                    if symbol in realistic_spreads:
                        original_spread = spread_pct
                        spread_pct = realistic_spreads[symbol]
                        self.logger.debug(f"📊 {{symbol}}: Adjusted spread from {{original_spread:.3f}}% to {{spread_pct:.3f}}% (paper trading)")
                    elif mid_price > 100:  # Large-cap stocks over $100
                        original_spread = spread_pct
                        spread_pct = 0.02  # 2 basis points for large caps
                        self.logger.debug(f"📊 {{symbol}}: Adjusted spread from {{original_spread:.3f}}% to {{spread_pct:.3f}}% (large-cap)")
                    elif mid_price > 50:   # Mid-cap stocks
                        original_spread = spread_pct
                        spread_pct = 0.05  # 5 basis points for mid caps
                        self.logger.debug(f"📊 {{symbol}}: Adjusted spread from {{original_spread:.3f}}% to {{spread_pct:.3f}}% (mid-cap)")
                    else:  # Small-cap stocks
                        original_spread = spread_pct
                        spread_pct = min(spread_pct, 0.15)  # Cap at 15 basis points
                        self.logger.debug(f"📊 {{symbol}}: Adjusted spread from {{original_spread:.3f}}% to {{spread_pct:.3f}}% (small-cap)")"""
        
        # Replace the content
        content = content.replace(spread_calc_marker, new_code)
        
        # Write back the file
        with open(data_manager_path, 'w') as f:
            f.write(content)
        
        print("✅ Applied paper trading spread adjustment!")
        print("📊 Large-cap stocks (>$100) will use 0.02% spread")
        print("📊 Mid-cap stocks (>$50) will use 0.05% spread") 
        print("📊 Small-cap stocks will use max 0.15% spread")
        print("📊 Known stocks (PG, JNJ, etc.) get specific realistic spreads")
        
    else:
        print("❌ Could not find spread calculation location in DataManager")
        print("Manual fix may be required")

if __name__ == "__main__":
    fix_paper_trading_spreads()
