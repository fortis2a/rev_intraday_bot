#!/usr/bin/env python3
"""
File Verification Report
Detailed analysis for workspace cleanup decisions
"""

print("📋 DETAILED FILE VERIFICATION REPORT")
print("=" * 80)

# Files that need individual verification
verification_queue = {
    "🔧 UTILITIES (Review Each)": [
        "analyze_workspace_files.py",  # NEW - Can archive after cleanup
        "close_trade.py",  # KEEP - Manual position closing
        "dashboard_data_explanation.py",  # REVIEW - May be old
        "emergency_close_all.py",  # KEEP - Emergency trading function
        "force_close_all.py",  # KEEP - Force close positions
        "launch_dashboard.py",  # KEEP - Dashboard launcher
        "monitor_trading_status.py",  # REVIEW - May be redundant
        "organize_untracked_files.py",  # ARCHIVE - Cleanup utility
        "regenerate_summaries.py",  # REVIEW - May be old
        "simple_debug.py",  # ARCHIVE - Debug utility
        "start_intraday.py",  # REVIEW - May be old launcher
        "start_proper_engine.py",  # REVIEW - May be old launcher
        "start_proper_trading.py",  # REVIEW - May be old launcher
        "start_trading_session.py",  # REVIEW - May be old launcher
        "three_day_summary.py",  # KEEP - Analysis tool
        "trading_engine_diagnostics.py",  # REVIEW - Debug tool
        "update_database_schema.py",  # REVIEW - Database tool
    ],
    "📊 ANALYSIS_TOOLS (Review Each)": [
        "advanced_market_analysis.py",  # REVIEW - Advanced tool
        "alpaca_pnl_fetcher.py",  # KEEP - Active P&L tool
        "enhanced_daily_analysis.py",  # KEEP - EOD analysis
        "enhanced_pnl_calculator.py",  # REVIEW - May be redundant
        "generate_market_close_report.bat",  # KEEP - Report generator
        "investigate_pnl.py",  # REVIEW - Debug tool
        "pnl_enhancement_summary.py",  # REVIEW - May be old
        "pnl_monitor.py",  # KEEP - Live P&L monitoring
        "report_enhancement_summary.py",  # REVIEW - May be old
        "run_enhanced_report.bat",  # KEEP - Report runner
        "run_today_analysis.bat",  # KEEP - Analysis runner
        "start_live_pnl.bat",  # KEEP - P&L monitor starter
        "start_live_pnl.ps1",  # KEEP - P&L monitor starter
        "start_pnl_external.bat",  # REVIEW - May be redundant
        "today_analysis.py",  # KEEP - Daily analysis
    ],
    "❓ UNKNOWN (Manual Review)": [
        ".gitignore",  # KEEP - Git configuration
        "close_all_positions.bat",  # KEEP - Emergency close script
        "close_stock.bat",  # KEEP - Stock closing script
        "close_trade.bat",  # KEEP - Trade closing script
        "decision_check.bat",  # REVIEW - May be old
        "launch_command_center.bat",  # KEEP - Command center launcher
        "start_enhanced_command_center.bat",  # KEEP - Enhanced command center (ACTIVE)
        "launch_dashboard.bat",  # KEEP - Dashboard launcher
        "permanent_cleanup.ps1",  # ARCHIVE - Cleanup script
        "profit_protection_center.bat",  # REVIEW - May be old
        "pytest.ini",  # KEEP - Test configuration
        "run_daily_collection.bat",  # REVIEW - May be old
        "setup_scheduler.ps1",  # REVIEW - Scheduler setup
        "start_all_windows.bat",  # REVIEW - May be old
        "start_confidence_monitor.bat",  # REVIEW - May be old
        "start_confidence_monitor.ps1",  # REVIEW - May be old
        "start_enhanced_command_center.bat",  # REVIEW - May be old
        "workspace.code-workspace",  # KEEP - VS Code workspace
    ],
}

print("\n🎯 FILES REQUIRING INDIVIDUAL VERIFICATION:")
print("=" * 80)

for category, files in verification_queue.items():
    print(f"\n{category}:")
    for file in files:
        parts = file.split(" # ")
        filename = parts[0]
        recommendation = parts[1] if len(parts) > 1 else "REVIEW"
        print(f"   📄 {filename:<35} -> {recommendation}")

print("\n" + "=" * 80)
print("🚀 READY FOR VERIFICATION PROCESS")
print("=" * 80)
print("\nNext Steps:")
print("1. We'll go through each file individually")
print("2. Determine if it's still needed for current operations")
print("3. Mark for KEEP or ARCHIVE")
print("4. Move archive candidates to archive/ directory")
print("\nShall we begin the verification process?")
