#!/usr/bin/env python3
"""
Organize Untracked Files - Clean up VS Code file restoration
"""

import os
import shutil
from datetime import datetime
from pathlib import Path


def create_backup():
    """Create backup of today's new files"""
    print("🔄 Creating backup of today's new files...")
    
    # Create backup directory with timestamp
    backup_dir = f"backup_untracked_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    # Files that were created today and should be backed up
    todays_files = [
        "enhanced_daily_analysis.py",
        "close_trade.py", 
        "emergency_close_all.py",
        "force_close_all.py",
        "cleanup_and_close.py",
        "close_all_positions.bat",
        "close_stock.bat",
        "run_today_analysis.bat",
        "start_enhanced_command_center.bat",
        "today_analysis.py"
    ]
    
    for file in todays_files:
        if os.path.exists(file):
            shutil.copy2(file, backup_dir)
            print(f"  ✅ Backed up: {file}")
    
    print(f"📦 Backup created in: {backup_dir}")
    return backup_dir

def organize_files():
    """Organize files into proper directories"""
    print("\n🗂️  Organizing files into proper directories...")
    
    # Files created TODAY - KEEP IN ROOT
    keep_in_root = [
        "enhanced_daily_analysis.py",
        "close_trade.py", 
        "emergency_close_all.py",
        "force_close_all.py",
        "cleanup_and_close.py",
        "close_all_positions.bat",
        "close_stock.bat",
        "run_today_analysis.bat",
        "start_enhanced_command_center.bat",
        "today_analysis.py",
        "profit_protection_center.bat"
    ]
    
    # Create directories if they don't exist
    directories = {
        "archive": [
            "analyze_after_hours_positions.py",
            "analyze_confidence_monitor_integration.py", 
            "analyze_indicator_overlap.py",
            "analyze_monitoring_setup.py",
            "analyze_trade_visibility.py",
            "check_trades.py",
            "debug_engine.py",
            "debug_signals.py",
            "demo.py",
            "permanent_cleanup.py",
            "short_selling_summary.py",
            "signal_monitor.py",
            "verify_actual_trades.py",
            "verify_eod_generation.py"
        ],
        "scripts": [
            "continuous_position_monitor.py",
            "emergency_profit_protection.py", 
            "live_dashboard.py",
            "manual_protection.py"
        ],
        "tests": [
            "test_all_watchlist.py",
            "test_complete_pipeline.py",
            "test_confidence.py",
            "test_confidence_comparison.py",
            "test_data_retrieval.py",
            "test_launcher_fix.py",
            "test_live_signals.py",
            "test_optimized_system.py",
            "test_order_placement.py",
            "test_precision_error.py",
            "test_risk_limits.py",
            "test_signal_generation.py",
            "test_strategy_integration.py"
        ],
        "documentation": [
            "DASHBOARD_ENHANCEMENTS.md",
            "INTEGRATION_COMPLETE_FINAL.md",
            "INTEGRATION_REPORT.md", 
            "LAYOUT_OPTIMIZATION.md",
            "MONDAY_READY_REAL_TRADES.md",
            "PROFIT_PROTECTION_REPORT.md",
            "REAL_DATA_INTEGRATION_COMPLETE.md",
            "SINGLE_PAGE_OPTIMIZATION.md",
            "STRATEGY_INTEGRATION_SUMMARY.md",
            "TRADE_VISIBILITY_SOLUTION.md",
            "ULTRA_COMPACT_OPTIMIZATION.md"
        ]
    }
    
    # Move files to appropriate directories (skip files that should stay in root)
    for directory, files in directories.items():
        os.makedirs(directory, exist_ok=True)
        
        for file in files:
            if os.path.exists(file) and file not in keep_in_root:
                try:
                    shutil.move(file, os.path.join(directory, file))
                    print(f"  📁 Moved {file} → {directory}/")
                except Exception as e:
                    print(f"  ❌ Failed to move {file}: {e}")
            elif file in keep_in_root:
                print(f"  ✅ Keeping {file} in root (created today)")
    
    # Show what's staying in root
    print(f"\n🏠 FILES KEPT IN ROOT (created today):")
    for file in keep_in_root:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ⚠️  {file} (not found)")

def main():
    """Main organization function"""
    print("🧹 ORGANIZING UNTRACKED FILES")
    print("="*50)
    print("📝 Strategy: Keep today's new files in root, move old files to archive")
    
    # Step 1: Create backup of today's important files
    backup_dir = create_backup()
    
    # Step 2: Organize files into proper directories  
    organize_files()
    
    # Step 3: Handle special cases
    print("\n📂 Handling special directories...")
    
    # Move Futures Scalping Bot to proper location
    if os.path.exists("Futures Scalping Bot"):
        if not os.path.exists("archive/futures_scalping_bot"):
            shutil.move("Futures Scalping Bot", "archive/futures_scalping_bot")
            print("  📁 Moved Futures Scalping Bot → archive/futures_scalping_bot/")
    
    # The docs/ directory should stay as is (it's properly organized)
    
    # Step 4: Summary
    print(f"\n✅ ORGANIZATION COMPLETE!")
    print(f"📦 Backup location: {backup_dir}")
    print("🗂️  Files organized into:")
    print("   • ROOT/ - Today's new working files (kept)")
    print("   • archive/ - Analysis and debug scripts (moved)")
    print("   • scripts/ - Working utility scripts (moved)")  
    print("   • tests/ - Test files (moved)")
    print("   • documentation/ - Markdown documentation (moved)")
    print("   • docs/ - Existing organized documentation (untouched)")
    
    print(f"\n🎯 TODAY'S FILES KEPT IN ROOT:")
    important_files = [
        "enhanced_daily_analysis.py",
        "close_trade.py",
        "emergency_close_all.py", 
        "force_close_all.py",
        "cleanup_and_close.py",
        "today_analysis.py",
        "profit_protection_center.bat",
        "close_all_positions.bat",
        "close_stock.bat",
        "run_today_analysis.bat",
        "start_enhanced_command_center.bat"
    ]
    
    for file in important_files:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ⚠️  {file} (missing - check backup)")

if __name__ == "__main__":
    main()
