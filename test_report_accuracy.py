#!/usr/bin/env python3
"""
Test script to analyze accuracy of all sections in market close report
"""
import sys
sys.path.append('.')
from reporting.market_close_report import MarketCloseReportGenerator

def analyze_report_accuracy():
    print("🔍 COMPREHENSIVE MARKET CLOSE REPORT ACCURACY ANALYSIS")
    print("=" * 70)

    try:
        generator = MarketCloseReportGenerator()
        
        # Get the full analysis data
        print("📊 Gathering complete analysis data...")
        today_orders, yesterday_orders = generator.get_extended_orders()
        analysis_data = generator.analyze_trade_performance(today_orders, yesterday_orders)
        
        print("\n1. 📈 TRADE SUMMARY SECTION")
        print("=" * 40)
        trade_summary = analysis_data.get('trade_summary', {})
        net_pnl = trade_summary.get('net_pnl', 0)
        total_trades = trade_summary.get('total_trades', 0)
        total_volume = trade_summary.get('total_volume', 0)
        unique_symbols = trade_summary.get('unique_symbols', 0)
        
        print(f"   Net P&L: ${net_pnl:.2f}")
        print(f"   Total Trades: {total_trades}")
        print(f"   Total Volume: ${total_volume:,.2f}")
        print(f"   Unique Symbols: {unique_symbols}")
        
        print("\n2. 📊 SYMBOL PERFORMANCE SECTION")
        print("=" * 40)
        symbol_perf = analysis_data.get('symbol_performance', {})
        symbol_total_pnl = sum(data.get('pnl', 0) for data in symbol_perf.values())
        print(f"   Symbols Analyzed: {len(symbol_perf)}")
        print(f"   Total Symbol P&L: ${symbol_total_pnl:.2f}")
        match_symbol = abs(symbol_total_pnl - net_pnl) < 0.01
        print(f"   Match with Trade Summary: {'✅' if match_symbol else '❌'}")
        
        if symbol_perf:
            print("   Symbol Breakdown:")
            for symbol, data in list(symbol_perf.items())[:5]:
                pnl = data.get('pnl', 0)
                trades = data.get('total_trades', 0)
                volume = data.get('total_volume', 0)
                print(f"     {symbol}: P&L=${pnl:.2f}, Trades={trades}, Volume=${volume:.2f}")
        
        print("\n3. 📈 STATISTICAL ANALYSIS SECTION")
        print("=" * 40)
        stats = analysis_data.get('statistical_analysis', {})
        stats_pnl = stats.get('total_pnl', 0)
        win_rate = stats.get('win_rate', 0)
        profit_factor = stats.get('profit_factor', 0)
        completed_trades = stats.get('total_completed_trades', 0)
        avg_pnl = stats.get('avg_pnl', 0)
        
        print(f"   Total P&L: ${stats_pnl:.2f}")
        print(f"   Completed Trades: {completed_trades}")
        print(f"   Win Rate: {win_rate:.1f}%")
        print(f"   Profit Factor: {profit_factor:.2f}")
        print(f"   Average P&L: ${avg_pnl:.2f}")
        match_stats = abs(stats_pnl - net_pnl) < 0.01
        print(f"   Match with Trade Summary: {'✅' if match_stats else '❌'}")
        
        print("\n4. ⚠️ RISK METRICS SECTION")
        print("=" * 40)
        risk = analysis_data.get('risk_metrics', {})
        sharpe = risk.get('sharpe_ratio', 0)
        max_dd = risk.get('max_drawdown', 0)
        var_95 = risk.get('var_95', 0)
        volatility = risk.get('volatility', 0)
        
        print(f"   Sharpe Ratio: {sharpe:.3f}")
        print(f"   Max Drawdown: ${max_dd:.2f}")
        print(f"   VaR 95%: ${var_95:.2f}")
        print(f"   Volatility: ${volatility:.2f}")
        
        print("\n5. 🧠 TRADING PSYCHOLOGY SECTION")
        print("=" * 40)
        psychology = analysis_data.get('trading_psychology', {})
        max_wins = psychology.get('max_consecutive_wins', 0)
        max_losses = psychology.get('max_consecutive_losses', 0)
        overtrading = psychology.get('potential_overtrading', False)
        
        print(f"   Max Consecutive Wins: {max_wins}")
        print(f"   Max Consecutive Losses: {max_losses}")
        print(f"   Overtrading Detected: {overtrading}")
        
        print("\n6. ⏰ TIME ANALYSIS SECTION")
        print("=" * 40)
        time_analysis = analysis_data.get('time_analysis', {})
        if time_analysis:
            total_time_pnl = sum(hour_data.get('pnl', 0) for hour_data in time_analysis.values())
            best_hour = max(time_analysis.items(), key=lambda x: x[1].get('pnl', 0))[0] if time_analysis else "N/A"
            print(f"   Hours Analyzed: {len(time_analysis)}")
            print(f"   Total Time P&L: ${total_time_pnl:.2f}")
            print(f"   Best Hour: {best_hour}:00")
        else:
            print("   No time analysis data available")
        
        print("\n🎯 CONSISTENCY CHECK SUMMARY")
        print("=" * 40)
        print(f"   Target P&L (99.6% accurate): $706.20")
        print(f"   Trade Summary P&L: ${net_pnl:.2f}")
        print(f"   Symbol Total P&L: ${symbol_total_pnl:.2f}")
        print(f"   Statistical P&L: ${stats_pnl:.2f}")
        
        # Check consistency
        target_match = abs(net_pnl - 706.20) < 0.01
        print(f"   ✅ Trade Summary matches target: {target_match}")
        print(f"   ✅ Symbol analysis matches Trade Summary: {match_symbol}")
        print(f"   ✅ Statistical analysis matches Trade Summary: {match_stats}")
        
        print("\n📋 SECTION ACCURACY ASSESSMENT")
        print("=" * 40)
        
        # Individual section assessments
        sections_status = []
        
        if target_match:
            sections_status.append("✅ Trade Summary: ACCURATE ($706.20)")
        else:
            sections_status.append(f"❌ Trade Summary: INACCURATE (${net_pnl:.2f} vs $706.20)")
            
        if match_symbol:
            sections_status.append("✅ Symbol Performance: CONSISTENT")
        else:
            sections_status.append(f"❌ Symbol Performance: INCONSISTENT (${symbol_total_pnl:.2f} vs ${net_pnl:.2f})")
            
        if match_stats:
            sections_status.append("✅ Statistical Analysis: CONSISTENT")
        else:
            sections_status.append(f"❌ Statistical Analysis: INCONSISTENT (${stats_pnl:.2f} vs ${net_pnl:.2f})")
            
        # Display results
        for status in sections_status:
            print(f"   {status}")
        
        if target_match and match_symbol and match_stats:
            print("\n🎉 OVERALL RESULT: ALL SECTIONS ACCURATE AND CONSISTENT!")
            print("   The market close report is using the correct $706.20 calculation throughout.")
        else:
            print("\n⚠️ OVERALL RESULT: INCONSISTENCIES DETECTED")
            print("   Some sections need to be updated to use the corrected calculation method.")
            
            # Provide specific recommendations
            print("\n🔧 RECOMMENDATIONS:")
            if not target_match:
                print("   - Fix Trade Summary to use the $706.20 method")
            if not match_symbol:
                print("   - Fix Symbol Performance calculation inconsistency")
            if not match_stats:
                print("   - Fix Statistical Analysis calculation inconsistency")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_report_accuracy()
