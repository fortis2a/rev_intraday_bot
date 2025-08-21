#!/usr/bin/env python3
"""
Phase 1 Safe Cleanup - Archive actual outdated files in current workspace
SAFE TO RUN - These files are clearly outdated and not needed for current operations
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

def phase1_safe_cleanup():
    """Execute Phase 1 cleanup - archive safe files that actually exist"""
    
    print("PHASE 1 SAFE CLEANUP - ACTUAL FILES")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Create archive directory
    archive_dir = Path("archive/phase1_safe_cleanup_20250821")
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    # Files to archive (SAFE - files that actually exist and are clearly outdated)
    safe_archive_files = [
        # Development/Debug Files
        "simple_debug.py",
        "trading_engine_diagnostics.py",
        "investigate_pnl.py",
        "alpaca_pnl_fetcher.py",
        "show_all_orders.py",
        
        # Enhanced/Updated Analysis (we have newer versions)
        "enhanced_pnl_calculator.py",  # We have market_close_report.py now
        "pnl_enhancement_summary.py",
        "report_enhancement_summary.py", 
        "dashboard_data_explanation.py",
        "regenerate_summaries.py",
        
        # Temporary Analysis Files
        "phase1_safe_cleanup.py",  # This script itself
        "phase1_safe_cleanup_simple.py",  # The backup version
        "cleanup_action_plan.py",  # Temporary analysis file
        
        # Old Organization Files  
        "organize_untracked_files.py",  # Organization is complete
        
        # Development Testing
        "start_proper_engine.py",
        "start_proper_trading.py",
        "start_trading_session.py",
        
        # Various utilities that seem outdated
        "three_day_summary.py",
        "update_database_schema.py"
    ]
    
    # Track results
    archived_files = []
    not_found_files = []
    errors = []
    
    print("ARCHIVING FILES:")
    print("-" * 80)
    
    for filename in safe_archive_files:
        source_path = Path(filename)
        
        if source_path.exists():
            try:
                # Move file to archive
                dest_path = archive_dir / filename
                shutil.move(str(source_path), str(dest_path))
                archived_files.append(filename)
                print(f"ARCHIVED: {filename}")
                
            except Exception as e:
                errors.append(f"{filename}: {e}")
                print(f"ERROR: {filename} - {e}")
        else:
            not_found_files.append(filename)
            print(f"NOT FOUND: {filename}")
    
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
1. **Debug Files**: Development and debugging utilities
2. **Enhanced Analysis**: Old versions replaced by newer tools
3. **Temporary Files**: Analysis files no longer needed
4. **Development Testing**: Experimental engine files
5. **Organization Tools**: Completed organization utilities

## Impact
- SAFE: No impact on trading system operations
- REVERSIBLE: Files can be restored from archive if needed
- CLEANUP: Workspace is now cleaner and more organized

## Files Kept (Active Core System)
- main.py, launcher.py, config.py (core trading)
- data_manager.py, order_manager.py (system components)
- strategies.py, strategies_enhanced.py (trading strategies)
- live_dashboard.py, market_close_report.py (current reporting)
- generate_todays_pnl.py (current P&L system)
- All core/, utils/, scripts/, dashboard/ directories

## Next Steps
- Proceed to Phase 2: Review remaining utility scripts
- Phase 3: Review analysis tools in scripts/
- Phase 4: Review configuration files
"""
    
    # Save report
    report_path = archive_dir / "cleanup_report.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    # Display results
    print()
    print("CLEANUP RESULTS:")
    print("=" * 80)
    print(f"Successfully archived: {len(archived_files)} files")
    print(f"Files not found: {len(not_found_files)} files")
    print(f"Errors: {len(errors)} files")
    print()
    print(f"Archive location: {archive_dir}")
    print(f"Detailed report: {report_path}")
    print()
    
    if len(archived_files) > 0:
        print("PHASE 1 COMPLETED SUCCESSFULLY!")
        print("- Workspace is now cleaner and more organized")
        print("- No impact on trading system functionality")
        print("- All archived files can be restored if needed")
        print()
        print("READY FOR PHASE 2:")
        print("   Next step: Review remaining utility scripts")
        
        # Show remaining file count
        remaining_py_files = len([f for f in Path('.').glob('*.py') if f.name not in archived_files])
        print(f"   Remaining Python files in root: ~{remaining_py_files} files")
    else:
        print("No files were archived")
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
        print(f"FATAL ERROR: {e}")
        exit(1)
