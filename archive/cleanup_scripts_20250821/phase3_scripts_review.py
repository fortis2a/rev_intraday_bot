#!/usr/bin/env python3
"""
Phase 3 Scripts Directory Review - Analyze and organize the scripts/ directory
MAJOR CLEANUP OPPORTUNITY - 57 files to review and organize
"""

import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path


def analyze_scripts_directory():
    """Analyze all Python files in the scripts/ directory"""
    
    print("PHASE 3 SCRIPTS DIRECTORY REVIEW")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    scripts_dir = Path("scripts")
    if not scripts_dir.exists():
        print("ERROR: scripts/ directory not found!")
        return
    
    # Get all Python files in scripts directory
    script_files = list(scripts_dir.glob("*.py"))
    script_files.sort()
    
    print(f"Found {len(script_files)} Python files in scripts/ directory")
    print()
    
    # Categorize files by naming patterns and likely purpose
    categories = {
        "TEST_FILES": [],
        "DEBUG_FILES": [],
        "ANALYSIS_TOOLS": [],
        "MONITORING_TOOLS": [],
        "UTILITY_SCRIPTS": [],
        "DATA_SCRIPTS": [],
        "DEMO_FILES": [],
        "COMMAND_CENTER": [],
        "OUTDATED_LIKELY": [],
        "REVIEW_NEEDED": []
    }
    
    # Get file info for analysis
    file_info = []
    for file_path in script_files:
        stat = file_path.stat()
        file_info.append({
            'name': file_path.name,
            'path': str(file_path),
            'size': stat.st_size,
            'modified': datetime.fromtimestamp(stat.st_mtime),
            'modified_str': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
        })
    
    # Categorize each file based on naming patterns
    for info in file_info:
        filename = info['name'].lower()
        
        if filename.startswith('test_'):
            categories["TEST_FILES"].append(info)
        elif 'debug' in filename or 'check' in filename or 'verify' in filename:
            categories["DEBUG_FILES"].append(info)
        elif 'analysis' in filename or 'analyze' in filename or 'report' in filename:
            categories["ANALYSIS_TOOLS"].append(info)
        elif 'monitor' in filename or 'status' in filename or 'watch' in filename:
            categories["MONITORING_TOOLS"].append(info)
        elif 'demo' in filename or 'example' in filename:
            categories["DEMO_FILES"].append(info)
        elif 'command' in filename or 'center' in filename or 'dashboard' in filename:
            categories["COMMAND_CENTER"].append(info)
        elif 'data' in filename or 'db' in filename or 'database' in filename:
            categories["DATA_SCRIPTS"].append(info)
        elif any(x in filename for x in ['old', 'backup', 'temp', 'bak', 'legacy']):
            categories["OUTDATED_LIKELY"].append(info)
        elif info['size'] < 1000:  # Very small files, likely utilities or abandoned
            categories["UTILITY_SCRIPTS"].append(info)
        else:
            categories["REVIEW_NEEDED"].append(info)
    
    # Display categorization
    print("SCRIPTS CATEGORIZATION:")
    print("=" * 80)
    
    total_categorized = 0
    for category, files in categories.items():
        if files:
            print(f"\n{category.replace('_', ' ')} ({len(files)} files):")
            print("-" * 40)
            total_categorized += len(files)
            
            # Sort by modification date (newest first) within each category
            files.sort(key=lambda x: x['modified'], reverse=True)
            
            for file_info in files:
                size_kb = file_info['size'] / 1024
                print(f"  - {file_info['name']:<40} {size_kb:>6.1f}KB  {file_info['modified_str']}")
    
    print(f"\nTotal files categorized: {total_categorized}")
    
    # Identify Phase 3 cleanup candidates
    print()
    print("PHASE 3 CLEANUP ANALYSIS:")
    print("=" * 80)
    
    # Files that are definitely safe to archive
    safe_archive_candidates = []
    safe_archive_candidates.extend([f['name'] for f in categories["TEST_FILES"]])
    safe_archive_candidates.extend([f['name'] for f in categories["DEBUG_FILES"]])
    safe_archive_candidates.extend([f['name'] for f in categories["DEMO_FILES"]])
    safe_archive_candidates.extend([f['name'] for f in categories["OUTDATED_LIKELY"]])
    
    # Small utility files that might be obsolete
    small_utilities = [f for f in categories["UTILITY_SCRIPTS"] if f['size'] < 500]
    safe_archive_candidates.extend([f['name'] for f in small_utilities])
    
    # Old analysis files (older than 30 days)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    old_analysis = [f for f in categories["ANALYSIS_TOOLS"] if f['modified'] < thirty_days_ago]
    
    print(f"SAFE ARCHIVE CANDIDATES: {len(safe_archive_candidates)} files")
    print("- Test files (test_*.py)")
    print("- Debug files (debug_*, check_*, verify_*)")  
    print("- Demo files")
    print("- Files with 'old', 'backup', 'temp' in name")
    print("- Very small utility files (<500 bytes)")
    print()
    
    print(f"REVIEW CANDIDATES: {len(old_analysis)} old analysis files")
    print("- Analysis files older than 30 days")
    print()
    
    print(f"KEEP: {len(categories['COMMAND_CENTER']) + len(categories['MONITORING_TOOLS'])} important files")
    print("- Command center and dashboard files")
    print("- Current monitoring tools")
    print("- Recent analysis tools")
    
    # Check for very recent files (modified today)
    today = datetime.now().date()
    recent_files = [f for f in file_info if f['modified'].date() == today]
    
    if recent_files:
        print()
        print(f"RECENTLY MODIFIED ({len(recent_files)} files modified today):")
        print("-" * 40)
        for f in recent_files:
            print(f"  - {f['name']} ({f['modified_str']})")
    
    # Generate detailed report
    report_content = f"""# Phase 3 Scripts Directory Review Report
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- Total Python files in scripts/: {len(script_files)}
- Safe archive candidates: {len(safe_archive_candidates)}
- Review needed: {len(categories['REVIEW_NEEDED'])}
- Command center files: {len(categories['COMMAND_CENTER'])}
- Monitoring tools: {len(categories['MONITORING_TOOLS'])}

## File Categories
"""
    
    for category, files in categories.items():
        if files:
            report_content += f"\n### {category.replace('_', ' ')} ({len(files)} files)\n"
            for f in files:
                report_content += f"- {f['name']} ({f['size']} bytes, {f['modified_str']})\n"
    
    report_content += f"""
## Phase 3 Cleanup Recommendations

### IMMEDIATE SAFE ARCHIVES ({len(safe_archive_candidates)} files)
These files can be safely archived with minimal risk:

#### Test Files ({len(categories['TEST_FILES'])})
All test_*.py files - development testing scripts
"""
    
    for f in categories["TEST_FILES"]:
        report_content += f"- {f['name']}\n"
    
    report_content += f"""
#### Debug Files ({len(categories['DEBUG_FILES'])})
Debug, check, and verification scripts
"""
    
    for f in categories["DEBUG_FILES"]:
        report_content += f"- {f['name']}\n"
    
    report_content += f"""
#### Demo Files ({len(categories['DEMO_FILES'])})
Demonstration and example files
"""
    
    for f in categories["DEMO_FILES"]:
        report_content += f"- {f['name']}\n"
    
    report_content += f"""
### CAREFUL REVIEW NEEDED
#### Command Center Files ({len(categories['COMMAND_CENTER'])})
Important dashboard and command center functionality - KEEP
"""
    
    for f in categories["COMMAND_CENTER"]:
        report_content += f"- {f['name']} (KEEP)\n"
    
    report_content += f"""
#### Monitoring Tools ({len(categories['MONITORING_TOOLS'])})
Current monitoring and status tools - REVIEW individually
"""
    
    for f in categories["MONITORING_TOOLS"]:
        report_content += f"- {f['name']}\n"
    
    report_content += """
## Cleanup Strategy
1. **Phase 3A**: Archive all test files, debug files, demo files (SAFE)
2. **Phase 3B**: Review small utility files individually  
3. **Phase 3C**: Review old analysis files (>30 days)
4. **Phase 3D**: Consolidate remaining monitoring tools

## Impact Estimate
- Safe archive: ~{0} files (low risk)
- Workspace reduction: ~{1}% of scripts directory
- Preserved functionality: All command center and active monitoring
""".format(len(safe_archive_candidates), int(len(safe_archive_candidates) / len(script_files) * 100))
    
    # Save report
    report_path = Path("reports/phase3_scripts_review.md")
    report_path.parent.mkdir(exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print()
    print("ANALYSIS COMPLETE:")
    print("=" * 80)
    print(f"Detailed report saved: {report_path}")
    print()
    print("NEXT STEPS:")
    print("1. Execute Phase 3A: Archive safe files (test, debug, demo)")
    print("2. Review command center and monitoring files")
    print("3. Consider individual review of analysis tools")
    print()
    
    return categories, safe_archive_candidates

if __name__ == "__main__":
    try:
        categories, candidates = analyze_scripts_directory()
        
        print("READY FOR PHASE 3A EXECUTION:")
        print(f"- {len(candidates)} files ready for safe archiving")
        print("- Command center and monitoring files identified for preservation")
        print("- Detailed analysis complete")
        
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        exit(1)
