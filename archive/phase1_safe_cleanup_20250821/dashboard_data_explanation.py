#!/usr/bin/env python3
"""
Dashboard Data Source Explanation
Detailed breakdown of what data powers each section and how it's calculated
"""


def explain_dashboard_data_sources():
    """Explain what data each dashboard section uses"""

    print("🔍 DASHBOARD DATA SOURCE ANALYSIS")
    print("=" * 80)
    print("Based on your screenshot, here's exactly what each section shows:")
    print()

    # Strategy Performance Section
    print("🎯 STRATEGY PERFORMANCE SECTION:")
    print("-" * 50)
    print("📊 DATA SOURCE: Cash Flow Calculations from Trading Activities")
    print()

    print("🕐 HOURLY P&L CALCULATIONS:")
    print("   Algorithm: sells - buys = hourly_pnl")
    print("   • 14:00: -$240.00 (11 trades) = CASH FLOW based")
    print("   • 15:00: $995.15 (18 trades) = CASH FLOW based")
    print("   • 19:00: -$737.07 (3 trades) = CASH FLOW based")
    print()

    print("🔢 CALCULATION METHOD:")
    print("   ```python")
    print("   side_totals = hour_trades.groupby('side')['value'].sum()")
    print("   sells = side_totals.get('sell', 0) + side_totals.get('sell_short', 0)")
    print("   buys = side_totals.get('buy', 0)")
    print("   hour_pnl = sells - buys  # <-- CASH FLOW METHOD")
    print("   ```")
    print()

    print("⚠️  IMPORTANT NOTE:")
    print("   • This is CASH FLOW, not actual P&L")
    print("   • Does NOT account for multi-day positions")
    print("   • Does NOT include fees/commissions")
    print("   • Best for intraday scalping analysis")
    print()

    # Risk Assessment Section
    print("🛡️ RISK ASSESSMENT SECTION:")
    print("-" * 50)
    print("📊 DATA SOURCE: Trading Activity Patterns & Position Sizing")
    print()

    print("🔴 RISK LEVEL: HIGH")
    print("   Based on: Risk Score 85.0/100")
    print()

    print("📏 RISK METRICS BREAKDOWN:")
    print("   • Risk Score: 85.0/100 = Calculated composite score")
    print("   • Max Trade: $920.40 = Largest single trade value")
    print("   • Avg Trade: $136.57 = Average trade size")
    print("   • Symbol Diversity: 2 symbols = Low diversification")
    print("   • Concentration Ratio: 62.5% = High concentration risk")
    print()

    print("🔢 RISK SCORE CALCULATION:")
    print("   ```python")
    print("   symbol_concentration = max_symbol_trades / total_trades")
    print("   value_cv = trade_value_std / trade_value_mean")
    print("   risk_score = (symbol_concentration * 40) + (min(value_cv, 1) * 60)")
    print("   # Higher score = Higher risk")
    print("   ```")
    print()

    print("📊 WHAT THIS MEANS:")
    print("   • 62.5% concentration = 20 of 32 trades in one symbol (INTC)")
    print("   • High trade size variance = Inconsistent position sizing")
    print("   • Low symbol diversity = Concentrated exposure")
    print("   • Risk assessment is ACTIVITY-based, not P&L-based")
    print()

    # Data Source Summary
    print("📋 COMPLETE DATA SOURCE BREAKDOWN:")
    print("-" * 50)

    data_sources = [
        {
            "section": "Strategy Performance",
            "data_type": "Cash Flow",
            "calculation": "Sells - Buys per hour",
            "includes_fees": "❌ No",
            "multi_day_positions": "❌ No",
            "use_case": "Intraday scalping analysis",
        },
        {
            "section": "Risk Assessment",
            "data_type": "Activity Patterns",
            "calculation": "Position sizing & concentration metrics",
            "includes_fees": "N/A",
            "multi_day_positions": "N/A",
            "use_case": "Risk management & exposure analysis",
        },
        {
            "section": "Today's P&L (Top)",
            "data_type": "Alpaca P&L (when available)",
            "calculation": "Portfolio history from Alpaca API",
            "includes_fees": "✅ Yes",
            "multi_day_positions": "✅ Yes",
            "use_case": "Actual trading performance",
        },
    ]

    for ds in data_sources:
        print(f"\n🔸 {ds['section']}:")
        print(f"   Data Type: {ds['data_type']}")
        print(f"   Calculation: {ds['calculation']}")
        print(f"   Includes Fees: {ds['includes_fees']}")
        print(f"   Multi-day Positions: {ds['multi_day_positions']}")
        print(f"   Use Case: {ds['use_case']}")

    print()
    print("💡 KEY INSIGHTS FROM YOUR 8/20 DATA:")
    print("-" * 50)

    insights = [
        "🕐 15:00 was your BEST hour with $995.15 cash flow (18 trades)",
        "🕐 19:00 was your WORST hour with -$737.07 cash flow (3 trades)",
        "⚠️  HIGH risk score (85/100) due to 62.5% concentration in INTC",
        "📊 Only 2 symbols traded (INTC, SOXL) = Low diversification",
        "💰 Max single trade was $920.40 (position sizing risk)",
        "📈 Net cash flow: $18.08 across 32 trades",
        "🎯 Average trade size: $136.57 (wide variance)",
    ]

    for insight in insights:
        print(f"   {insight}")

    print()
    print("🔄 CASH FLOW vs ALPACA P&L COMPARISON:")
    print("-" * 50)
    print("📊 For 8/20 (Today):")
    print("   • Cash Flow P&L: $18.08")
    print("   • Alpaca P&L: $18.08 (matches because single-day positions)")
    print()
    print("📊 For 8/19 (Yesterday - Multi-day positions):")
    print("   • Cash Flow P&L: -$1,147.27 (WRONG)")
    print("   • Alpaca P&L: $61.93 (CORRECT)")
    print()
    print("🎯 CONCLUSION:")
    print("   • Strategy Performance section = CASH FLOW based")
    print("   • Risk Assessment section = ACTIVITY PATTERN based")
    print("   • Main P&L display = ALPACA P&L (source of truth)")
    print("   • For scalping analysis, cash flow is appropriate")
    print("   • For actual performance, always use Alpaca P&L")

    print()
    print("=" * 80)
    print("✅ DATA SOURCE ANALYSIS COMPLETE")
    print("🎯 Strategy Performance = Cash Flow | Risk Assessment = Activity Patterns")
    print("💰 Main P&L = Alpaca Source of Truth")
    print("=" * 80)


if __name__ == "__main__":
    explain_dashboard_data_sources()
