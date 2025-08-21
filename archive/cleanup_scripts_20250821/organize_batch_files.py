#!/usr/bin/env python3
"""
Organize Batch Files by Function
Group .bat files with similar purposes together
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

def organize_batch_files():
    """Organize batch files into functional subdirectories"""
    
    print("📁 ORGANIZING BATCH FILES BY FUNCTION")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Define functional groupings for batch files
    batch_groups = {
        "launchers": {
            "description": "Dashboard & System Launchers - Start various interfaces",
            "files": [
                "launch_dashboard.bat",
                "launch_command_center.bat", 
                "start_enhanced_command_center.bat",
                "start_all_windows.bat",
                "start_confidence_monitor.bat"
            ]
        },
        "reports": {
            "description": "Report Generators - Generate various trading reports",
            "files": [
                "generate_market_close_report.bat",
                "run_today_analysis.bat",
                "run_enhanced_report.bat",
                "run_daily_collection.bat",
                "start_live_pnl.bat",
                "start_pnl_external.bat"
            ]
        },
        "emergency": {
            "description": "Emergency Controls - Position closure and protection",
            "files": [
                "close_all_positions.bat",
                "close_stock.bat", 
                "close_trade.bat",
                "profit_protection_center.bat"
            ]
        },
        "utilities": {
            "description": "Utility Scripts - Decision checks and other tools",
            "files": [
                "decision_check.bat"
            ]
        }
    }
    
    # Check which files exist
    root_bat_files = list(Path('.').glob('*.bat'))
    existing_files = [f.name for f in root_bat_files]
    
    print("CURRENT ROOT DIRECTORY BATCH FILES:")
    print("-" * 40)
    for i, filename in enumerate(sorted(existing_files), 1):
        file_size = Path(filename).stat().st_size / 1024
        print(f"{i:2d}. {filename:<35} {file_size:>6.1f}KB")
    
    print(f"\nTotal: {len(existing_files)} batch files")
    print()
    
    # Show proposed organization
    print("PROPOSED BATCH FILE ORGANIZATION:")
    print("=" * 80)
    
    total_files_to_move = 0
    organization_plan = {}
    
    for group_name, group_info in batch_groups.items():
        print(f"\n📂 batch_{group_name.upper()}/ - {group_info['description']}")
        print("-" * 60)
        
        group_files = []
        for filename in group_info['files']:
            if filename in existing_files:
                file_size = Path(filename).stat().st_size / 1024
                status = "✅ FOUND"
                group_files.append(filename)
                total_files_to_move += 1
            else:
                file_size = 0
                status = "❌ NOT FOUND"
            
            print(f"  {filename:<35} {file_size:>6.1f}KB  {status}")
        
        organization_plan[group_name] = group_files
    
    # Show files not in any group
    all_grouped_files = []
    for group_files in organization_plan.values():
        all_grouped_files.extend(group_files)
    
    ungrouped_files = [f for f in existing_files if f not in all_grouped_files]
    
    if ungrouped_files:
        print(f"\n📁 UNGROUPED BATCH FILES:")
        print("-" * 40)
        for filename in ungrouped_files:
            file_size = Path(filename).stat().st_size / 1024
            print(f"  {filename:<35} {file_size:>6.1f}KB  ❓ REVIEW NEEDED")
    
    print()
    print("BATCH FILE ORGANIZATION STRATEGY:")
    print("=" * 80)
    print("🎯 OBJECTIVE: Group batch files by function for easy access")
    print()
    print("📋 PROPOSED ACTIONS:")
    print(f"   • CREATE batch_launchers/: {len(organization_plan['launchers'])} dashboard/system starters")
    print(f"   • CREATE batch_reports/: {len(organization_plan['reports'])} report generators")
    print(f"   • CREATE batch_emergency/: {len(organization_plan['emergency'])} position controls")
    print(f"   • CREATE batch_utilities/: {len(organization_plan['utilities'])} utility scripts")
    if ungrouped_files:
        print(f"   • REVIEW: {len(ungrouped_files)} ungrouped files need categorization")
    
    print()
    print("🔍 ANALYSIS:")
    print(f"   • Total batch files: {len(existing_files)}")
    print(f"   • Files to organize: {total_files_to_move}")
    print(f"   • New subdirectories: {len(batch_groups)}")
    
    # Ask for confirmation
    print()
    response = input("📝 Proceed with batch file organization? (y/N): ").strip().lower()
    
    if response != 'y':
        print("❌ Batch file organization cancelled by user")
        return False
    
    print()
    print("EXECUTING BATCH FILE ORGANIZATION:")
    print("=" * 80)
    
    # Create directories and move files
    moved_files = []
    created_dirs = []
    errors = []
    
    for group_name, group_files in organization_plan.items():
        if not group_files:
            continue
            
        # Create directory with "batch_" prefix
        group_dir = Path(f"batch_{group_name}")
        if not group_dir.exists():
            group_dir.mkdir()
            created_dirs.append(f"batch_{group_name}")
            print(f"📁 CREATED: batch_{group_name}/")
        
        # Move files to group directory
        print(f"📂 BATCH_{group_name.upper()}/ - Moving {len(group_files)} files")
        
        for filename in group_files:
            source_path = Path(filename)
            dest_path = group_dir / filename
            
            try:
                shutil.move(str(source_path), str(dest_path))
                moved_files.append((filename, f"batch_{group_name}"))
                print(f"   ✅ MOVED: {filename} → batch_{group_name}/")
                
            except Exception as e:
                errors.append(f"{filename}: {e}")
                print(f"   ❌ ERROR: {filename} - {e}")
    
    # Handle ungrouped files
    if ungrouped_files:
        print(f"\n📁 UNGROUPED BATCH FILES - Need manual categorization:")
        for filename in ungrouped_files:
            print(f"   ❓ {filename} - Review and categorize manually")
    
    # Create organization report
    print()
    print("FINAL BATCH FILE ORGANIZATION:")
    print("=" * 80)
    
    # Check final root directory
    final_root_bat_files = list(Path('.').glob('*.bat'))
    if final_root_bat_files:
        print(f"📁 ROOT DIRECTORY: {len(final_root_bat_files)} batch files remaining")
        for f in sorted(final_root_bat_files, key=lambda x: x.name):
            size_kb = f.stat().st_size / 1024
            print(f"   ⚠️ {f.name:<35} {size_kb:>6.1f}KB (ungrouped)")
    else:
        print(f"📁 ROOT DIRECTORY: ✅ Clean - all batch files organized")
    
    # Show created subdirectories
    for group_dir_name in created_dirs:
        group_files = list(Path(group_dir_name).glob('*.bat'))
        if group_files:
            print(f"\n📂 {group_dir_name.upper()}/: {len(group_files)} files")
            for f in sorted(group_files, key=lambda x: x.name):
                size_kb = f.stat().st_size / 1024
                icon = {
                    "batch_launchers": "🚀", 
                    "batch_reports": "📊", 
                    "batch_emergency": "🚨", 
                    "batch_utilities": "🔧"
                }.get(group_dir_name, "📁")
                print(f"   {icon} {f.name:<35} {size_kb:>6.1f}KB")
    
    # Create summary report
    report_content = f"""# Batch File Organization Report
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- Batch files organized: {len(moved_files)}
- Directories created: {len(created_dirs)}
- Files remaining in root: {len(final_root_bat_files)}
- Errors: {len(errors)}

## Organization Structure
"""
    
    for group_dir_name in created_dirs:
        group_files = list(Path(group_dir_name).glob('*.bat'))
        if group_files:
            group_name = group_dir_name.replace('batch_', '')
            group_desc = batch_groups[group_name]['description']
            report_content += f"\n### {group_dir_name.title().replace('_', ' ')} Directory\n{group_desc}\n"
            for f in sorted(group_files, key=lambda x: x.name):
                size_kb = f.stat().st_size / 1024
                report_content += f"- {f.name} ({size_kb:.1f}KB)\n"
    
    if moved_files:
        report_content += f"\n## Files Moved\n"
        for filename, destination in moved_files:
            report_content += f"- {filename} → {destination}/\n"
    
    if errors:
        report_content += f"\n## Errors\n"
        for error in errors:
            report_content += f"- {error}\n"
    
    # Save report
    report_path = Path("batch_organization_report.md")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print()
    print("BATCH ORGANIZATION RESULTS:")
    print("=" * 80)
    print(f"✅ Successfully organized: {len(moved_files)} batch files")
    print(f"📁 Directories created: {len(created_dirs)}")
    print(f"🏠 Files in root: {len(final_root_bat_files)}")
    print(f"📋 Report saved: {report_path}")
    
    if len(moved_files) > 0:
        print()
        print("🎉 BATCH FILE ORGANIZATION COMPLETE!")
        print("=" * 80)
        print("🎯 RESULTS:")
        print(f"   📊 Batch files organized by function")
        print(f"   🗂️ {len(created_dirs)} functional batch directories created")
        print(f"   🚀 Easy access to launchers, reports, and emergency tools")
        print(f"   📁 Clean separation of batch file purposes")
        print()
        print("🚀 YOUR BATCH FILES ARE NOW FUNCTIONALLY ORGANIZED!")
        print("   - Launchers grouped for easy dashboard/system startup")
        print("   - Report generators grouped for analysis workflows")
        print("   - Emergency controls grouped for crisis management")
        print("   - Utilities grouped for supporting tasks")
    
    return len(moved_files) > 0

if __name__ == "__main__":
    try:
        success = organize_batch_files()
        if success:
            print("\n🏆 BATCH FILE ORGANIZATION COMPLETED SUCCESSFULLY! 🏆")
        else:
            print("\n📝 Batch organization cancelled or no changes made")
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
