#!/usr/bin/env python3
"""
Workspace Cleanup Action Plan
Step-by-step cleanup process for the trading bot workspace
"""

print("🧹 WORKSPACE CLEANUP ACTION PLAN")
print("=" * 80)

action_plan = {
    "Phase 1: Safe Archive (Immediate)": {
        "description": "Archive files that are clearly outdated and safe to remove",
        "files": [
            # Test Files (18 files) - Safe to archive
            "check_alpaca_pnl.py", "check_db.py", "check_order_history.py",
            "check_table_structure.py", "check_today_pnl.py", "check_trades.py",
            "check_trading_hours.py", "debug_alpaca_data.py", "debug_yesterday.py",
            "demo_enhanced_logging.py", "test_db_queries.py", "test_main_scan.py",
            "test_pnl.py", "test_price_rounding.py", "test_short_selling.py",
            "test_signal_generation.py", "verify_alpaca_data.py", "verify_database.py",
            
            # Backup/Temp Files (3 files) - Safe to archive
            "backup_untracked_files.py", "cleanup_and_close.py", "cleanup_backup_list.json",
            
            # Temporary analysis files created today
            "analyze_workspace_files.py", "file_verification_report.py"
        ],
        "action": "Move to archive/phase1_safe_cleanup/",
        "risk": "LOW - These are clearly test/debug/temp files"
    },
    
    "Phase 2: Utility Review (Manual)": {
        "description": "Review utility scripts individually",
        "files": [
            "close_trade.py",              # Keep - manual position closing
            "dashboard_data_explanation.py", # Review - may be old
            "emergency_close_all.py",      # Keep - emergency function
            "force_close_all.py",          # Keep - force close
            "launch_dashboard.py",         # Keep - dashboard launcher
            "monitor_trading_status.py",   # Review - may be redundant
            "organize_untracked_files.py", # Archive - cleanup utility
            "regenerate_summaries.py",     # Review - may be old
            "simple_debug.py",             # Archive - debug utility
            "start_intraday.py",           # Review - old launcher?
            "start_proper_engine.py",      # Review - old launcher?
            "start_proper_trading.py",     # Review - old launcher?
            "start_trading_session.py",    # Review - old launcher?
            "three_day_summary.py",        # Keep - analysis tool
            "trading_engine_diagnostics.py", # Review - debug tool
            "update_database_schema.py"    # Review - database tool
        ],
        "action": "Review each file individually",
        "risk": "MEDIUM - Need to verify current usage"
    },
    
    "Phase 3: Analysis Tools Review": {
        "description": "Review analysis and reporting tools",
        "files": [
            "advanced_market_analysis.py", "alpaca_pnl_fetcher.py",
            "enhanced_daily_analysis.py", "enhanced_pnl_calculator.py",
            "investigate_pnl.py", "pnl_enhancement_summary.py",
            "pnl_monitor.py", "report_enhancement_summary.py",
            "today_analysis.py"
        ],
        "action": "Keep recent, archive old duplicates",
        "risk": "LOW-MEDIUM - Analysis tools"
    },
    
    "Phase 4: Configuration Files": {
        "description": "Review configuration and script files", 
        "files": [
            "Various .bat files", "Config scripts", "Setup files"
        ],
        "action": "Keep active launchers, archive old ones",
        "risk": "MEDIUM - Some may be critical"
    }
}

print("📋 RECOMMENDED EXECUTION ORDER:")
print()

for phase, details in action_plan.items():
    print(f"🎯 {phase}")
    print(f"   Description: {details['description']}")
    print(f"   Files to process: {len(details['files'])} files")
    print(f"   Action: {details['action']}")
    print(f"   Risk Level: {details['risk']}")
    print()

print("🚀 READY TO START PHASE 1?")
print("=" * 80)
print("Phase 1 is SAFE - these are clearly outdated test/debug files.")
print("We can archive 23 files immediately with minimal risk.")
print()
print("Would you like to:")
print("1. 🟢 START Phase 1 cleanup (safe archive)")
print("2. 🔍 REVIEW specific files first")
print("3. 📊 SEE detailed file analysis")
print("4. ⏸️  PAUSE and plan further")

if __name__ == "__main__":
    print("\nNext command options:")
    print("• python start_phase1_cleanup.py  - Start safe archiving")
    print("• python review_specific_file.py <filename> - Review individual file")
    print("• python detailed_analysis.py - See detailed analysis")
