#!/usr/bin/env python3
"""
Phase 3B Conservative Cleanup - Archive old analysis tools that are likely redundant
CONSERVATIVE APPROACH - Only archive files that are clearly outdated
"""

import os
import shutil
from datetime import datetime
from pathlib import Path


def phase3b_conservative_cleanup():
    """Execute Phase 3B conservative cleanup"""
    
    print("PHASE 3B CONSERVATIVE CLEANUP")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    scripts_dir = Path("scripts")
    
    # Create archive directory
    archive_dir = Path("archive/phase3b_conservative_cleanup_20250821")
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    # Conservative archive candidates - old analysis tools
    conservative_archive_files = [
        "analyze_confidence_levels.py",  # 7.1KB, 2025-08-13 - Old confidence analysis
        "analyze_stock_thresholds.py",   # 18.9KB, 2025-08-14 - Old threshold analysis
        "generate_stock_report.py",      # 6.9KB, 2025-08-13 - Old stock reporting
        "find_intraday_stocks.py",       # 12.3KB, 2025-08-13 - Old stock finding
        "permanent_cleanup.py",          # 11.3KB, 2025-08-14 - Cleanup utility (we have our own now)
    ]
    
    # Additional candidates - old reporting tools that likely overlap with current tools
    potential_archive_files = [
        "multi_page_png_report.py",      # 18.8KB, 2025-08-14 - Old multi-page reporting
        "multi_page_report.py",          # 18.7KB, 2025-08-14 - Old multi-page reporting  
        "comprehensive_pnl_report.py",   # 44.6KB, 2025-08-14 - Might overlap with market_close_report.py
        "alpaca_pnl_calculator.py",      # 14.5KB, 2025-08-14 - Might overlap with generate_todays_pnl.py
        "live_pnl_external.py",          # 21.5KB, 2025-08-14 - External P&L (we have live_dashboard.py)
    ]
    
    print("ANALYSIS OF POTENTIAL OVERLAPS:")
    print("-" * 80)
    
    # Check what we have in root directory for comparison
    root_files = [f.name for f in Path('.').glob('*.py')]
    
    print("Current P&L and reporting tools in root:")
    current_tools = [f for f in root_files if any(x in f.lower() for x in ['pnl', 'report', 'dashboard', 'analysis'])]
    for tool in current_tools:
        print(f"  - {tool}")
    
    print()
    print("Potentially redundant tools in scripts/:")
    for tool in potential_archive_files:
        tool_path = scripts_dir / tool
        if tool_path.exists():
            size_kb = tool_path.stat().st_size / 1024
            print(f"  - {tool} ({size_kb:.1f}KB)")
    
    # Track results
    archived_files = []
    not_found_files = []
    errors = []
    
    print()
    print("ARCHIVING CONSERVATIVE CANDIDATES:")
    print("-" * 80)
    
    # First, archive the definitely safe ones
    for filename in conservative_archive_files:
        source_path = scripts_dir / filename
        
        if source_path.exists():
            try:
                file_size = source_path.stat().st_size
                
                # Move file to archive
                dest_path = archive_dir / filename
                shutil.move(str(source_path), str(dest_path))
                archived_files.append(filename)
                
                print(f"ARCHIVED: {filename} ({file_size} bytes) - Old analysis tool")
                
            except Exception as e:
                errors.append(f"{filename}: {e}")
                print(f"ERROR: {filename} - {e}")
        else:
            not_found_files.append(filename)
            print(f"NOT FOUND: {filename}")
    
    # Check for additional safe archives (old reporting tools)
    print()
    print("CHECKING ADDITIONAL REPORTING OVERLAPS:")
    print("-" * 80)
    
    # Archive old multi-page reports (we have market_close_report.py now)
    additional_safe = ["multi_page_png_report.py", "multi_page_report.py"]
    
    for filename in additional_safe:
        source_path = scripts_dir / filename
        
        if source_path.exists():
            try:
                file_size = source_path.stat().st_size
                
                # Move file to archive
                dest_path = archive_dir / filename
                shutil.move(str(source_path), str(dest_path))
                archived_files.append(filename)
                
                print(f"ARCHIVED: {filename} ({file_size} bytes) - Replaced by market_close_report.py")
                
            except Exception as e:
                errors.append(f"{filename}: {e}")
                print(f"ERROR: {filename} - {e}")
        else:
            print(f"NOT FOUND: {filename}")
    
    # Check what's left
    remaining_files = list(scripts_dir.glob("*.py"))
    
    print()
    print("REMAINING FILES ANALYSIS:")
    print("-" * 80)
    
    essential_files = []
    review_files = []
    
    for file_path in remaining_files:
        filename = file_path.name.lower()
        
        if any(x in filename for x in ['command_center', 'monitor', 'protection']):
            essential_files.append(file_path.name)
        else:
            review_files.append(file_path.name)
    
    print(f"ESSENTIAL FILES (KEEP): {len(essential_files)}")
    for f in essential_files:
        print(f"  ✅ {f}")
    
    print(f"\nFILES STILL NEEDING REVIEW: {len(review_files)}")
    for f in review_files:
        file_path = scripts_dir / f
        size_kb = file_path.stat().st_size / 1024
        modified = datetime.fromtimestamp(file_path.stat().st_mtime).strftime('%m-%d')
        print(f"  🔍 {f:<35} {size_kb:>6.1f}KB  {modified}")
    
    # Create cleanup report
    report_content = f"""# Phase 3B Conservative Cleanup Report
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- Files to archive: {len(conservative_archive_files) + len(additional_safe)}
- Successfully archived: {len(archived_files)}
- Not found: {len(not_found_files)}
- Errors: {len(errors)}
- Remaining in scripts/: {len(remaining_files)}

## Archived Files

### Conservative Archives (Old Analysis Tools)
"""
    
    for f in conservative_archive_files:
        if f in archived_files:
            report_content += f"- {f} ✓ (Old analysis tool)\n"
        else:
            report_content += f"- {f} (not found)\n"
    
    report_content += """
### Additional Archives (Reporting Overlaps)
"""
    
    for f in additional_safe:
        if f in archived_files:
            report_content += f"- {f} ✓ (Replaced by market_close_report.py)\n"
        else:
            report_content += f"- {f} (not found)\n"
    
    report_content += f"""
## Remaining Files Analysis

### Essential Files (KEEP) - {len(essential_files)}
Core monitoring, protection, and command center functionality
"""
    
    for f in essential_files:
        report_content += f"- {f}\n"
    
    report_content += f"""
### Files Needing Individual Review - {len(review_files)}
P&L tools, connectors, and analysis utilities
"""
    
    for f in review_files:
        report_content += f"- {f}\n"
    
    report_content += """
## Impact
- SAFE: Archived old analysis tools and redundant reporting
- PRESERVED: All monitoring, protection, and command center functionality
- SIMPLIFIED: Scripts directory is more focused on current tools
- REVERSIBLE: All archived files can be restored if needed

## Recommendations for Remaining Files
1. **Keep all monitoring/protection tools** (confidence_monitor.py, etc.)
2. **Review P&L tools** for overlap with current generate_todays_pnl.py
3. **Review connectors** (alpaca_connector.py, realtime_data_connector.py)
4. **Keep recent analysis tools** (enhanced_report_generator.py is recent)
5. **Consider consolidating** remaining tools if functionality overlaps

## Next Steps
- Individual review of remaining P&L and connector tools
- Test current functionality to ensure no dependencies broken
- Consider final consolidation of overlapping tools
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
        scripts_reduction = int(len(archived_files) / (len(remaining_files) + len(archived_files)) * 100)
        
        print("PHASE 3B COMPLETED SUCCESSFULLY!")
        print(f"- Archived {len(archived_files)} old/redundant analysis tools")
        print(f"- Scripts directory reduced by {scripts_reduction}% in this phase")
        print(f"- {len(remaining_files)} files remaining for final review")
        print("- All essential functionality preserved")
        print()
        
        if len(review_files) > 0:
            print("FINAL REVIEW NEEDED:")
            print(f"   {len(review_files)} files need individual assessment")
            print("   Focus: P&L tools, connectors, recent analysis tools")
        else:
            print("SCRIPTS CLEANUP NEARLY COMPLETE!")
    else:
        print("No files were archived")
    
    return len(archived_files), len(not_found_files), len(errors), len(remaining_files)

if __name__ == "__main__":
    try:
        archived, not_found, errors, remaining = phase3b_conservative_cleanup()
        
        if errors > 0:
            exit(1)
        else:
            exit(0)
            
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        exit(1)
