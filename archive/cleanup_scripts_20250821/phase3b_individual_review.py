#!/usr/bin/env python3
"""
Phase 3B Individual Script Review - Analyze remaining 24 files for targeted cleanup
CAREFUL REVIEW - Individual assessment of each remaining script
"""

import os
import shutil
from pathlib import Path
from datetime import datetime, timedelta

def analyze_remaining_scripts():
    """Analyze the remaining 24 files in scripts/ directory"""
    
    print("PHASE 3B INDIVIDUAL SCRIPT REVIEW")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    scripts_dir = Path("scripts")
    remaining_files = list(scripts_dir.glob("*.py"))
    remaining_files.sort()
    
    print(f"Found {len(remaining_files)} remaining files in scripts/")
    print()
    
    # Analyze each file individually
    file_analysis = []
    
    print("INDIVIDUAL FILE ANALYSIS:")
    print("=" * 80)
    
    for file_path in remaining_files:
        stat = file_path.stat()
        size_kb = stat.st_size / 1024
        modified = datetime.fromtimestamp(stat.st_mtime)
        modified_str = modified.strftime('%Y-%m-%d %H:%M')
        
        # Try to read first few lines for content analysis
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                first_lines = [f.readline().strip() for _ in range(5)]
                first_content = '\n'.join(first_lines)
        except:
            first_content = "Could not read file"
        
        analysis = {
            'name': file_path.name,
            'size_kb': size_kb,
            'modified': modified,
            'modified_str': modified_str,
            'first_content': first_content,
            'category': 'unknown',
            'recommendation': 'review',
            'reason': ''
        }
        
        # Categorize and recommend based on filename and content
        filename_lower = file_path.name.lower()
        
        if 'command_center' in filename_lower or 'scalping_command' in filename_lower:
            analysis['category'] = 'CRITICAL'
            analysis['recommendation'] = 'KEEP'
            analysis['reason'] = 'Main command center - essential functionality'
            
        elif any(x in filename_lower for x in ['monitor', 'protection']):
            analysis['category'] = 'MONITORING'
            analysis['recommendation'] = 'KEEP'
            analysis['reason'] = 'Active monitoring/protection tool'
            
        elif 'pnl' in filename_lower and size_kb > 10:
            analysis['category'] = 'PNL_ANALYSIS'
            analysis['recommendation'] = 'REVIEW'
            analysis['reason'] = 'P&L analysis - check for overlap with current tools'
            
        elif 'report' in filename_lower and size_kb > 15:
            analysis['category'] = 'REPORTING'
            analysis['recommendation'] = 'REVIEW'
            analysis['reason'] = 'Reporting tool - check for overlap with market_close_report.py'
            
        elif 'connector' in filename_lower or 'alpaca' in filename_lower:
            analysis['category'] = 'CONNECTOR'
            analysis['recommendation'] = 'REVIEW'
            analysis['reason'] = 'Data connector - check if still needed'
            
        elif 'data' in filename_lower:
            analysis['category'] = 'DATA_TOOL'
            analysis['recommendation'] = 'REVIEW'
            analysis['reason'] = 'Data collection tool'
            
        elif modified < datetime.now() - timedelta(days=30):
            analysis['category'] = 'OLD_TOOL'
            analysis['recommendation'] = 'ARCHIVE'
            analysis['reason'] = f'Old file (>30 days) - last modified {modified_str}'
            
        elif size_kb < 5:
            analysis['category'] = 'SMALL_UTILITY'
            analysis['recommendation'] = 'REVIEW'
            analysis['reason'] = 'Small utility - check if still needed'
            
        else:
            analysis['category'] = 'GENERAL_TOOL'
            analysis['recommendation'] = 'REVIEW'
            analysis['reason'] = 'General analysis tool'
        
        file_analysis.append(analysis)
        
        # Print analysis
        print(f"{analysis['name']:<35} {size_kb:>6.1f}KB  {modified_str}  {analysis['recommendation']}")
        print(f"    Category: {analysis['category']}")
        print(f"    Reason: {analysis['reason']}")
        print()
    
    # Group by recommendation
    keep_files = [f for f in file_analysis if f['recommendation'] == 'KEEP']
    archive_candidates = [f for f in file_analysis if f['recommendation'] == 'ARCHIVE']
    review_files = [f for f in file_analysis if f['recommendation'] == 'REVIEW']
    
    print("RECOMMENDATION SUMMARY:")
    print("=" * 80)
    print(f"KEEP (Essential): {len(keep_files)} files")
    print(f"ARCHIVE (Safe): {len(archive_candidates)} files") 
    print(f"REVIEW (Individual): {len(review_files)} files")
    print()
    
    # Show specific recommendations
    if keep_files:
        print("KEEP - Essential Files:")
        for f in keep_files:
            print(f"  ✅ {f['name']} - {f['reason']}")
        print()
    
    if archive_candidates:
        print("ARCHIVE - Safe to Remove:")
        for f in archive_candidates:
            print(f"  📦 {f['name']} - {f['reason']}")
        print()
    
    if review_files:
        print("REVIEW - Individual Assessment Needed:")
        for f in review_files:
            print(f"  🔍 {f['name']} - {f['reason']}")
        print()
    
    # Check for potential duplicates with root directory
    print("DUPLICATE CHECK WITH ROOT DIRECTORY:")
    print("=" * 80)
    
    root_py_files = [f.name for f in Path('.').glob('*.py')]
    
    potential_duplicates = []
    for script_file in file_analysis:
        script_name = script_file['name']
        
        # Check for similar names in root
        for root_file in root_py_files:
            if (script_name.replace('_', '').lower() in root_file.replace('_', '').lower() or
                root_file.replace('_', '').lower() in script_name.replace('_', '').lower()):
                
                if script_name != root_file:  # Not exact same name
                    potential_duplicates.append((script_name, root_file))
    
    if potential_duplicates:
        print("Potential duplicate functionality found:")
        for script, root in potential_duplicates:
            print(f"  scripts/{script} ↔ {root}")
    else:
        print("No obvious duplicates found with root directory")
    
    print()
    
    return file_analysis, keep_files, archive_candidates, review_files

def create_phase3b_cleanup():
    """Create cleanup script for Phase 3B based on analysis"""
    
    print("CREATING PHASE 3B CLEANUP PLAN:")
    print("=" * 80)
    
    # Based on our analysis, identify specific files to archive
    # These are conservative choices - files that are clearly outdated or redundant
    
    # Check what files actually exist
    scripts_dir = Path("scripts")
    existing_files = [f.name for f in scripts_dir.glob("*.py")]
    
    # Conservative archive candidates (files that are likely safe to archive)
    conservative_archive = []
    
    # Old analysis files that might be replaced by newer tools
    old_analysis_candidates = [
        "analyze_confidence_levels.py",  # Old confidence analysis
        "analyze_stock_thresholds.py",   # Old threshold analysis  
        "generate_stock_report.py",      # Old stock reporting
        "find_intraday_stocks.py",       # Old stock finding
    ]
    
    # Check which exist and are old
    for candidate in old_analysis_candidates:
        if candidate in existing_files:
            file_path = scripts_dir / candidate
            modified = datetime.fromtimestamp(file_path.stat().st_mtime)
            if modified < datetime.now() - timedelta(days=7):  # More than a week old
                conservative_archive.append(candidate)
    
    # Backup/cleanup utilities that might be outdated
    utility_candidates = [
        "permanent_cleanup.py",  # Cleanup utility
    ]
    
    for candidate in utility_candidates:
        if candidate in existing_files:
            conservative_archive.append(candidate)
    
    print(f"Conservative archive candidates: {len(conservative_archive)} files")
    
    if conservative_archive:
        for f in conservative_archive:
            print(f"  - {f}")
    else:
        print("  No obvious safe candidates for automatic archiving")
        print("  All remaining files need individual review")
    
    print()
    print("RECOMMENDATION:")
    print("- Keep all monitoring and command center files")
    print("- Review P&L and reporting tools for overlap")
    print("- Consider archiving old analysis tools individually")
    print("- Preserve recent and actively used tools")
    
    return conservative_archive

if __name__ == "__main__":
    try:
        file_analysis, keep_files, archive_candidates, review_files = analyze_remaining_scripts()
        
        print()
        conservative_candidates = create_phase3b_cleanup()
        
        print()
        print("PHASE 3B ANALYSIS COMPLETE:")
        print("=" * 80)
        print(f"Total files analyzed: {len(file_analysis)}")
        print(f"Essential files (KEEP): {len(keep_files)}")
        print(f"Conservative archive candidates: {len(conservative_candidates)}")
        print(f"Files needing individual review: {len(review_files)}")
        print()
        print("Next steps:")
        print("1. Archive conservative candidates (if any)")
        print("2. Individual review of remaining analysis tools") 
        print("3. Check for functional overlap with current tools")
        
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        exit(1)
