#!/usr/bin/env python3
"""
Phase 2 Utility Review - Analyze remaining files for targeted cleanup
CAREFUL REVIEW - These files need individual assessment before archiving
"""

import os
from pathlib import Path
from datetime import datetime

def analyze_remaining_files():
    """Analyze remaining Python files in root directory"""
    
    print("PHASE 2 UTILITY REVIEW")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Get all remaining Python files in root
    root_py_files = [f.name for f in Path('.').glob('*.py')]
    root_py_files.sort()
    
    print(f"Found {len(root_py_files)} Python files in root directory")
    print()
    
    # Categorize remaining files
    categories = {
        "CORE_SYSTEM": [],
        "ACTIVE_UTILITIES": [],
        "EMERGENCY_TOOLS": [],
        "REPORTING_TOOLS": [],
        "ANALYSIS_TOOLS": [],
        "CONFIGURATION": [],
        "REVIEW_NEEDED": []
    }
    
    # Categorize each file
    for filename in root_py_files:
        if filename in ['main.py', 'launcher.py', 'config.py', 'data_manager.py', 'order_manager.py']:
            categories["CORE_SYSTEM"].append(filename)
        elif filename in ['live_dashboard.py', 'launch_dashboard.py', 'system_status.py', 'realtime_status_monitor.py']:
            categories["ACTIVE_UTILITIES"].append(filename)
        elif 'emergency' in filename.lower() or 'force_close' in filename.lower() or 'close_all' in filename.lower():
            categories["EMERGENCY_TOOLS"].append(filename)
        elif 'report' in filename.lower() or 'pnl' in filename.lower() or 'analysis' in filename.lower():
            categories["REPORTING_TOOLS"].append(filename)
        elif filename in ['strategies.py', 'strategies_enhanced.py', 'stock_specific_config.py']:
            categories["CONFIGURATION"].append(filename)
        elif filename in ['today_analysis.py', 'enhanced_daily_analysis.py', 'monitor_trading_status.py']:
            categories["ANALYSIS_TOOLS"].append(filename)
        else:
            categories["REVIEW_NEEDED"].append(filename)
    
    # Display categorization
    print("FILE CATEGORIZATION:")
    print("=" * 80)
    
    for category, files in categories.items():
        if files:
            print(f"\n{category} ({len(files)} files):")
            print("-" * 40)
            for file in files:
                print(f"  - {file}")
    
    # Identify candidates for Phase 2 cleanup
    phase2_candidates = []
    
    # Check for potential duplicates or old utilities
    potential_archive = [
        'close_trade.py',  # Might be duplicate of utils/close_trade.py
        'emergency_close_everything.py',  # Might be redundant with emergency_close_all.py
        'simple_close_all.py',  # Simplified version, might prefer force_close_all.py
        'advanced_market_analysis.py',  # Might be replaced by newer analysis
        'pnl_monitor.py',  # Might be replaced by live_dashboard.py
        'monitor_trading_status.py',  # Might be duplicate functionality
        'phase1_actual_cleanup.py'  # Our own temporary file
    ]
    
    for candidate in potential_archive:
        if candidate in root_py_files:
            phase2_candidates.append(candidate)
    
    print()
    print("PHASE 2 CLEANUP CANDIDATES:")
    print("=" * 80)
    print(f"Found {len(phase2_candidates)} files that may be ready for archiving:")
    
    for candidate in phase2_candidates:
        print(f"  - {candidate}")
    
    # Create detailed analysis report
    report_content = f"""# Phase 2 Utility Review Report
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- Total Python files in root: {len(root_py_files)}
- Core system files: {len(categories['CORE_SYSTEM'])}
- Active utilities: {len(categories['ACTIVE_UTILITIES'])}
- Emergency tools: {len(categories['EMERGENCY_TOOLS'])}
- Reporting tools: {len(categories['REPORTING_TOOLS'])}
- Analysis tools: {len(categories['ANALYSIS_TOOLS'])}
- Configuration files: {len(categories['CONFIGURATION'])}
- Files needing review: {len(categories['REVIEW_NEEDED'])}

## File Categories

### CORE SYSTEM (KEEP - Essential for trading)
"""
    
    for category, files in categories.items():
        if files:
            report_content += f"\n### {category.replace('_', ' ')} ({len(files)} files)\n"
            for file in files:
                report_content += f"- {file}\n"
    
    report_content += f"""
## Phase 2 Cleanup Candidates ({len(phase2_candidates)} files)
These files may be safe to archive but need individual review:

"""
    
    for candidate in phase2_candidates:
        report_content += f"- {candidate}\n"
    
    report_content += """
## Recommended Phase 2 Actions

### IMMEDIATE SAFE ARCHIVES (Low Risk)
1. `phase1_actual_cleanup.py` - Our own temporary cleanup script
2. Review duplicate utilities (close_trade.py vs utils/close_trade.py)
3. Review monitoring duplicates (pnl_monitor.py vs live_dashboard.py)

### CAREFUL REVIEW NEEDED (Medium Risk)
1. Emergency tools - Keep active ones, archive redundant
2. Analysis tools - Keep current versions, archive old
3. Reporting tools - Consolidate if duplicated

### KEEP (High Value)
1. All core system files
2. Active utilities and dashboards
3. Current strategies and configuration
4. Emergency close tools (at least one working version)

## Next Steps
1. Review individual files in REVIEW_NEEDED category
2. Check for functional duplicates
3. Archive safe candidates
4. Proceed to Phase 3 (scripts/ directory review)
"""
    
    # Save report
    report_path = Path("reports/phase2_utility_review.md")
    report_path.parent.mkdir(exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print()
    print("ANALYSIS COMPLETE:")
    print("=" * 80)
    print(f"Detailed report saved: {report_path}")
    print()
    print("NEXT STEPS:")
    print("1. Review individual files flagged for cleanup")
    print("2. Archive safe candidates")
    print("3. Check for functional duplicates")
    print()
    
    return categories, phase2_candidates

def check_file_sizes_and_dates():
    """Check file sizes and modification dates for additional insights"""
    
    print("FILE ANALYSIS:")
    print("=" * 80)
    
    root_py_files = list(Path('.').glob('*.py'))
    file_info = []
    
    for file_path in root_py_files:
        stat = file_path.stat()
        file_info.append({
            'name': file_path.name,
            'size': stat.st_size,
            'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
        })
    
    # Sort by modification date (newest first)
    file_info.sort(key=lambda x: x['modified'], reverse=True)
    
    print("Recent files (modified today or recently):")
    print("-" * 40)
    today = datetime.now().strftime('%Y-%m-%d')
    
    for info in file_info[:10]:  # Show top 10 most recent
        print(f"  {info['name']:<30} {info['size']:>8} bytes  {info['modified']}")
    
    print()
    print("Smaller files (potential utilities/tests):")
    print("-" * 40)
    
    # Sort by size
    file_info.sort(key=lambda x: x['size'])
    
    for info in file_info[:10]:  # Show 10 smallest
        if info['size'] < 5000:  # Less than 5KB
            print(f"  {info['name']:<30} {info['size']:>8} bytes  {info['modified']}")

if __name__ == "__main__":
    try:
        categories, candidates = analyze_remaining_files()
        print()
        check_file_sizes_and_dates()
        
        print()
        print("READY FOR PHASE 2 CLEANUP:")
        print(f"- {len(candidates)} files identified for potential archiving")
        print("- Detailed analysis report generated")
        print("- Ready to proceed with targeted cleanup")
        
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        exit(1)
