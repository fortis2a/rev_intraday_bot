"""
Run intraday stock analysis and generate comprehensive report
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.find_intraday_stocks import IntradayStockFinder
from datetime import datetime
import json

def generate_markdown_report(results, filename):
    """Generate comprehensive markdown report"""
    
    report = f"""# 📈 Intraday Trading Stock Analysis Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Criteria:** Price <$100, Volume >1M, 60-day 15-minute analysis  
**Total Analyzed:** {len(results)} stocks

---

## 🏆 Executive Summary

### Top 5 Recommendations
"""
    
    # Top 5 table
    if results:
        report += """
| Rank | Symbol | Price | Score | Rating | Volatility | Suggested Stop | Suggested Profit |
|------|--------|-------|-------|--------|------------|----------------|------------------|
"""
        for i, stock in enumerate(results[:5]):
            report += f"| {i+1} | **{stock['symbol']}** | ${stock['current_price']:.2f} | {stock['total_score']:.1f}/100 | {stock['trading_suitability']} | {stock['volatility_profile']} | {stock['suggested_stop_loss']:.2f}% | {stock['suggested_take_profit']:.2f}% |\n"
    
    report += f"""

### Key Insights
- **Best Overall:** {results[0]['symbol'] if results else 'N/A'} ({results[0]['total_score']:.1f}/100)
- **Most Liquid:** {max(results, key=lambda x: x['avg_daily_volume'])['symbol'] if results else 'N/A'}
- **Most Stable:** {min([s for s in results if s['volatility_profile'] != 'Very High'], key=lambda x: x['avg_volatility_15m'])['symbol'] if results else 'N/A'}

---

## 📊 Complete Analysis Results

"""

    for i, stock in enumerate(results):
        report += f"""
### {i+1}. {stock['symbol']} - {stock['trading_suitability']} ({stock['total_score']:.1f}/100)

**Basic Info:**
- **Current Price:** ${stock['current_price']:.2f}
- **Sector:** {stock['sector']}
- **Market Cap:** ${stock['market_cap']:,} (if available)

**Volume Analysis:**
- **Avg 15m Volume:** {stock['avg_volume_15m']:,}
- **Avg Daily Volume:** {stock['avg_daily_volume']:,}
- **Volume Consistency:** {stock['volume_consistency']:.2f} (lower is better)
- **Volume Score:** {stock['volume_score']:.1f}/30

**Volatility Analysis:**
- **15m Volatility:** {stock['avg_volatility_15m']:.2f}%
- **Typical Move:** {stock['typical_move_pct']:.2f}%
- **Daily Range:** {stock['avg_daily_range_pct']:.2f}%
- **Profile:** {stock['volatility_profile']}
- **Volatility Score:** {stock['volatility_score']:.1f}/25

**Trading Thresholds:**
- **Stop Loss:** {stock['suggested_stop_loss']:.2f}%
- **Take Profit:** {stock['suggested_take_profit']:.2f}%
- **Trailing Distance:** {stock['suggested_trailing_distance']:.2f}%

**Scoring Breakdown:**
- **Volume Score:** {stock['volume_score']:.1f}/30
- **Volatility Score:** {stock['volatility_score']:.1f}/25
- **Consistency Score:** {stock['consistency_score']:.1f}/20
- **Range Score:** {stock['range_score']:.1f}/25
- **Total Score:** {stock['total_score']:.1f}/100

---
"""

    # Comparison with current watchlist
    report += """
## 🔄 Comparison with Current Watchlist

| Stock | Current Watchlist | New Analysis | Comparison |
|-------|------------------|--------------|------------|
| IONQ | 0.50% stop, 1.00% profit | N/A | Current watchlist stock |
| RGTI | 0.51% stop, 1.00% profit | N/A | Current watchlist stock |
| QBTS | 1.54% stop, 1.33% profit | N/A | Current watchlist stock |
| JNJ | 0.50% stop, 1.00% profit | N/A | Current watchlist stock |
| PG | 0.50% stop, 1.00% profit | N/A | Current watchlist stock |

## 📋 Selection Criteria Used

### Volume Requirements
- **Minimum Daily Volume:** 1,000,000 shares
- **Consistency Check:** Lower standard deviation preferred
- **Scoring:** Up to 30 points for high liquidity

### Volatility Sweet Spot
- **Optimal Range:** 0.8% - 2.0% (15-minute volatility)
- **Acceptable Low:** 0.5% - 0.8%
- **Acceptable High:** 2.0% - 3.0%
- **Scoring:** Up to 25 points for optimal volatility

### Price Movement Analysis
- **Typical Move:** 70th percentile of 15-minute price changes
- **Daily Range:** Average high-low range as % of close
- **Scoring:** Up to 25 points for good intraday movement

### Consistency Metrics
- **Volume Stability:** Lower coefficient of variation preferred
- **Predictable Patterns:** Consistent intraday behavior
- **Scoring:** Up to 20 points for reliability

## 🎯 Implementation Recommendations

### For Budget Trading (<$100 stocks):
1. **Start with top 3-5 rated stocks**
2. **Paper trade first** to validate thresholds
3. **Use suggested stop/profit levels** as starting points
4. **Monitor for 1-2 weeks** before live trading

### Position Sizing for Budget:
- **High Score (80+):** Standard position size
- **Good Score (65-79):** 0.8x position size
- **Fair Score (50-64):** 0.6x position size
- **Below 50:** Avoid or use minimal size

### Risk Management:
- **Maximum 3-4 positions** simultaneously
- **Daily loss limit:** $200-300 for budget trading
- **Use trailing stops** as analyzed
- **Monitor during active hours** (10 AM - 3:30 PM ET)

---

**Disclaimer:** This analysis is for educational purposes. Past performance does not guarantee future results. Always use proper risk management and only trade with money you can afford to lose.
"""
    
    # Write to file
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"📄 Report saved to: {filename}")

def main():
    """Run analysis and generate report"""
    print("🚀 Starting comprehensive intraday stock analysis...")
    
    # Run the analysis
    finder = IntradayStockFinder(max_price=100, min_volume=1000000)
    results = finder.run_analysis()
    
    if not results:
        print("❌ No suitable stocks found")
        return
    
    # Generate report filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"C:\\Users\\will7\\OneDrive - Sygma Data Analytics\\Stock Trading\\Scalping Bot System\\docs\\intraday_stock_analysis_{timestamp}.md"
    
    # Generate markdown report
    generate_markdown_report(results, filename)
    
    # Also save raw data as JSON for further analysis
    json_filename = filename.replace('.md', '.json')
    with open(json_filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"✅ Analysis complete!")
    print(f"📊 Found {len(results)} suitable stocks")
    print(f"📄 Report: {filename}")
    print(f"📄 Raw data: {json_filename}")
    
    # Show top 5 summary
    print(f"\n🏆 Top 5 Stocks:")
    for i, stock in enumerate(results[:5]):
        print(f"{i+1}. {stock['symbol']}: ${stock['current_price']:.2f} - {stock['total_score']:.1f}/100 ({stock['trading_suitability']})")

if __name__ == "__main__":
    main()
