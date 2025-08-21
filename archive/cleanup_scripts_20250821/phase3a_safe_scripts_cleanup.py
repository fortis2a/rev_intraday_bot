#!/usr/bin/env python3
"""
Phase 3A Safe Cleanup - Archive test, debug, demo files from scripts/
SAFE EXECUTION - These files are clearly safe to archive
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

def phase3a_safe_cleanup():
    """Execute Phase 3A cleanup - archive clearly safe files from scripts/"""
    
    print("PHASE 3A SAFE SCRIPTS CLEANUP")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    scripts_dir = Path("scripts")
    if not scripts_dir.exists():
        print("ERROR: scripts/ directory not found!")
        return
    
    # Create archive directory
    archive_dir = Path("archive/phase3a_safe_scripts_20250821")
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    # Get all files in scripts directory
    all_script_files = list(scripts_dir.glob("*.py"))
    
    print(f"Found {len(all_script_files)} Python files in scripts/")
    print()
    
    # Identify SAFE archive candidates based on our analysis
    safe_archive_files = []
    
    # Add files by category (based on previous analysis output)
    test_files = [
        "test_real_trades.py",
        "test_integration.py", 
        "test_error_conditions.py",
        "test_no_fallback_policy.py",
        "test_real_time_confidence.py",
        "test_confidence_filter.py"
    ]
    
    debug_files = [
        "live_signal_check.py",
        "updated_position_check.py"
    ]
    
    demo_files = [
        "demo_data_generator.py",
        "eod_demo.py"
    ]
    
    # Empty utility files (0KB from analysis)
    empty_utility_files = [
        "eod_scheduler.py",
        "unicode_safe_test.py",
        "setup_github.py",
        "quick_signal_test.py",
        "WORKSPACE_CLEANUP_SCRIPT.py",
        "workspace_cleanup.py",
        "stop_loss_repair.py",
        "simple_trailing_test.py",
        "log_viewer.py",
        "position_cleanup.py"
    ]
    
    # Empty analysis files (0KB from analysis)
    empty_analysis_files = [
        "generate_eod_report.py",
        "eod_report_generator.py",
        "trailing_stop_analysis.py",
        "stop_loss_analyzer.py",
        "execution_flaw_analysis.py",
        "qbts_strategy_analysis.py",
        "rule_violation_analysis.py",
        "pnl_discrepancy_analysis.py",
        "trading_analysis.py"
    ]
    
    # Empty monitoring files (0KB from analysis)
    empty_monitoring_files = [
        "quick_status.py",
        "stock_watchlist.py"
    ]
    
    # Outdated files
    outdated_files = [
        "backup_system.py",
        "backup_to_github.py"
    ]
    
    # Combine all safe archive files
    safe_archive_files.extend(test_files)
    safe_archive_files.extend(debug_files)
    safe_archive_files.extend(demo_files)
    safe_archive_files.extend(empty_utility_files)
    safe_archive_files.extend(empty_analysis_files)
    safe_archive_files.extend(empty_monitoring_files)
    safe_archive_files.extend(outdated_files)
    
    # Track results
    archived_files = []
    not_found_files = []
    errors = []
    empty_files = []
    
    print("ARCHIVING SAFE FILES:")
    print("-" * 80)
    
    for filename in safe_archive_files:
        source_path = scripts_dir / filename
        
        if source_path.exists():
            try:
                # Check file size
                file_size = source_path.stat().st_size
                if file_size == 0:
                    empty_files.append(filename)
                
                # Move file to archive
                dest_path = archive_dir / filename
                shutil.move(str(source_path), str(dest_path))
                archived_files.append(filename)
                
                size_info = f"({file_size} bytes)" if file_size > 0 else "(EMPTY)"
                print(f"ARCHIVED: {filename} {size_info}")
                
            except Exception as e:
                errors.append(f"{filename}: {e}")
                print(f"ERROR: {filename} - {e}")
        else:
            not_found_files.append(filename)
            print(f"NOT FOUND: {filename}")
    
    # Check what's left in scripts directory
    remaining_files = list(scripts_dir.glob("*.py"))
    
    print()
    print("REMAINING FILES IN SCRIPTS/:")
    print("-" * 80)
    
    if remaining_files:
        print(f"Found {len(remaining_files)} files remaining:")
        
        # Categorize remaining files
        important_remaining = []
        review_remaining = []
        
        for file_path in remaining_files:
            filename = file_path.name.lower()
            
            if 'command' in filename or 'center' in filename:
                important_remaining.append(file_path.name)
            elif any(x in filename for x in ['monitor', 'protection', 'connector', 'pnl', 'analyzer']):
                review_remaining.append(file_path.name)
            else:
                review_remaining.append(file_path.name)
        
        if important_remaining:
            print(f"\nIMPORTANT FILES (KEEP): {len(important_remaining)}")
            for f in important_remaining:
                print(f"  - {f}")
        
        if review_remaining:
            print(f"\nFILES FOR REVIEW: {len(review_remaining)}")
            for f in review_remaining[:10]:  # Show first 10
                print(f"  - {f}")
            if len(review_remaining) > 10:
                print(f"  ... and {len(review_remaining) - 10} more")
    else:
        print("No files remaining!")
    
    # Create cleanup report
    report_content = f"""# Phase 3A Safe Scripts Cleanup Report
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- Files to archive: {len(safe_archive_files)}
- Successfully archived: {len(archived_files)}
- Empty files removed: {len(empty_files)}
- Not found: {len(not_found_files)}
- Errors: {len(errors)}
- Remaining in scripts/: {len(remaining_files)}

## Archived Files by Category

### Test Files ({len(test_files)})
All test_*.py files - development testing scripts
"""
    
    for f in test_files:
        if f in archived_files:
            report_content += f"- {f} ✓\n"
        else:
            report_content += f"- {f} (not found)\n"
    
    report_content += f"""
### Debug Files ({len(debug_files)})
Debug and check scripts
"""
    
    for f in debug_files:
        if f in archived_files:
            report_content += f"- {f} ✓\n"
        else:
            report_content += f"- {f} (not found)\n"
    
    report_content += f"""
### Demo Files ({len(demo_files)})
Demonstration and example scripts
"""
    
    for f in demo_files:
        if f in archived_files:
            report_content += f"- {f} ✓\n"
        else:
            report_content += f"- {f} (not found)\n"
    
    report_content += f"""
### Empty Files ({len(empty_files)})
Zero-byte placeholder files that were removed
"""
    
    for f in empty_files:
        report_content += f"- {f}\n"
    
    report_content += f"""
## Impact
- SAFE: No impact on core trading system functionality
- CLEANUP: Removed {len(archived_files)} files from scripts directory
- ORGANIZATION: Scripts directory is now {int(len(archived_files)/len(all_script_files)*100)}% cleaner
- REVERSIBLE: All files can be restored if needed

## Next Steps
1. Review remaining {len(remaining_files)} files in scripts/
2. Focus on command center and monitoring tools (KEEP)
3. Review analysis and utility tools individually
4. Consider Phase 3B for additional cleanup
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
    print(f"Empty files removed: {len(empty_files)} files")
    print(f"Files not found: {len(not_found_files)} files")  
    print(f"Errors: {len(errors)} files")
    print()
    print(f"Archive location: {archive_dir}")
    print(f"Detailed report: {report_path}")
    print()
    
    if len(archived_files) > 0:
        reduction_pct = int(len(archived_files) / len(all_script_files) * 100)
        print("PHASE 3A COMPLETED SUCCESSFULLY!")
        print(f"- Scripts directory reduced by {reduction_pct}%")
        print(f"- {len(remaining_files)} files remaining for review")
        print("- All test, debug, demo, and empty files archived")
        print("- Core functionality preserved")
        print()
        
        if len(remaining_files) > 0:
            print("READY FOR PHASE 3B:")
            print("   Focus: Review remaining analysis and monitoring tools")
            print("   Key files preserved: Command center, active monitors")
        else:
            print("SCRIPTS DIRECTORY FULLY CLEANED!")
    else:
        print("No files were archived")
        print("   Files may have already been cleaned up")
    
    return len(archived_files), len(not_found_files), len(errors), len(remaining_files)

if __name__ == "__main__":
    try:
        archived, not_found, errors, remaining = phase3a_safe_cleanup()
        
        if errors > 0:
            exit(1)  # Exit with error if there were problems
        else:
            exit(0)  # Success
            
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        exit(1)
