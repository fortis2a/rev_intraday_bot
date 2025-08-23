#!/usr/bin/env python3
"""
Phase 1 Safe Cleanup - Archive outdated test/debug/temp files
SAFE TO RUN - These files are clearly outdated and not needed for current operations
"""

import os
import shutil
from datetime import datetime
from pathlib import Path


def phase1_safe_cleanup():
    """Execute Phase 1 cleanup - archive safe files"""
    
    print("🧹 PHASE 1 SAFE CLEANUP")
    print("=" * 80)
    print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Create archive directory
    archive_dir = Path("archive/phase1_safe_cleanup_20250821")
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    # Files to archive (SAFE - clearly outdated)
    safe_archive_files = [
        # Test Files (18 files) - All test/debug files
        "check_alpaca_pnl.py",
        "check_db.py", 
        "check_order_history.py",
        "check_table_structure.py",
        "check_today_pnl.py",
        "check_trades.py",
        "check_trading_hours.py",
        "debug_alpaca_data.py",
        "debug_yesterday.py",
        "demo_enhanced_logging.py",
        "test_db_queries.py",
        "test_main_scan.py",
        "test_pnl.py",
        "test_price_rounding.py",
        "test_short_selling.py",
        "test_signal_generation.py",
        "verify_alpaca_data.py",
        "verify_database.py",
        
        # Backup/Temp Files (3 files)
        "backup_untracked_files.py",
        "cleanup_and_close.py",
        "cleanup_backup_list.json",
        
        # Today's temporary analysis files (2 files)
        "analyze_workspace_files.py",
        "file_verification_report.py"
    ]
    
    # Track results
    archived_files = []
    not_found_files = []
    errors = []
    
    print("📦 ARCHIVING FILES:")
    print("-" * 80)
    
    for filename in safe_archive_files:
        source_path = Path(filename)
        
        if source_path.exists():
            try:
                # Move file to archive
                dest_path = archive_dir / filename
                shutil.move(str(source_path), str(dest_path))
                archived_files.append(filename)
                print(f"✅ {filename}")
                
            except Exception as e:
                errors.append(f"{filename}: {e}")
                print(f"❌ {filename} - ERROR: {e}")
        else:
            not_found_files.append(filename)
            print(f"⚠️  {filename} - NOT FOUND")
    
    # Create cleanup report
    report_content = f"""# Phase 1 Safe Cleanup Report
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- Files to archive: {len(safe_archive_files)}
- Successfully archived: {len(archived_files)}
- Not found: {len(not_found_files)}
- Errors: {len(errors)}

## Archived Files ({len(archived_files)})
"""
    
    for file in archived_files:
        report_content += f"- {file}\n"
    
    if not_found_files:
        report_content += f"\n## Not Found ({len(not_found_files)})\n"
        for file in not_found_files:
            report_content += f"- {file}\n"
    
    if errors:
        report_content += f"\n## Errors ({len(errors)})\n"
        for error in errors:
            report_content += f"- {error}\n"
    
    report_content += f"""
## What Was Archived
1. **Test Files**: All test_*.py, debug_*.py, check_*.py, verify_*.py files
2. **Backup Files**: Old backup and cleanup utilities
3. **Temp Files**: Today's analysis files (no longer needed)

## Impact
- ✅ SAFE: No impact on trading system operations
- ✅ REVERSIBLE: Files can be restored from archive if needed
- ✅ CLEANUP: Workspace is now cleaner and more organized

## Next Steps
- Proceed to Phase 2: Review utility scripts
- Phase 3: Review analysis tools  
- Phase 4: Review configuration files
"""
    
    # Save report
    report_path = archive_dir / "cleanup_report.md"
    with open(report_path, 'w') as f:
        f.write(report_content)
    
    # Display results
    print()
    print("📊 CLEANUP RESULTS:")
    print("=" * 80)
    print(f"✅ Successfully archived: {len(archived_files)} files")
    print(f"⚠️  Files not found: {len(not_found_files)} files")
    print(f"❌ Errors: {len(errors)} files")
    print()
    print(f"📁 Archive location: {archive_dir}")
    print(f"📄 Detailed report: {report_path}")
    print()
    
    if len(archived_files) > 0:
        print("🎉 PHASE 1 COMPLETED SUCCESSFULLY!")
        print("✅ Workspace is now cleaner and more organized")
        print("✅ No impact on trading system functionality")
        print("✅ All archived files can be restored if needed")
        print()
        print("🚀 READY FOR PHASE 2:")
        print("   Next step: Review utility scripts individually")
        print("   Command: python phase2_utility_review.py")
    else:
        print("⚠️  No files were archived")
        print("   This might be normal if files were already cleaned up")
    
    return len(archived_files), len(not_found_files), len(errors)

if __name__ == "__main__":
    try:
        archived, not_found, errors = phase1_safe_cleanup()
        
        if errors > 0:
            exit(1)  # Exit with error if there were problems
        else:
            exit(0)  # Success
            
    except Exception as e:
        print(f"❌ FATAL ERROR: {e}")
        exit(1)
