#!/usr/bin/env python3
"""
Organize Root Directory Files by Function
Group similar functionality together for better workspace organization
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

def organize_by_function():
    """Organize files into functional subdirectories"""
    
    print("📁 ORGANIZING FILES BY FUNCTION")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Define functional groupings
    functional_groups = {
        "core": {
            "description": "Core System Files - Essential trading engine components",
            "files": [
                "main.py",
                "launcher.py", 
                "config.py",
                "strategies.py",
                "stock_specific_config.py"
            ]
        },
        "monitoring": {
            "description": "Monitoring & Dashboard Files - Live system monitoring",
            "files": [
                "live_dashboard.py",
                "launch_dashboard.py",
                "realtime_status_monitor.py",
                "system_status.py"
            ]
        },
        "reporting": {
            "description": "Reporting & Analysis Files - P&L and trading analysis",
            "files": [
                "market_close_report.py",
                "enhanced_daily_analysis.py",
                "generate_todays_pnl.py",
                "today_analysis.py"
            ]
        },
        "emergency": {
            "description": "Emergency & Position Control - Critical trading controls",
            "files": [
                "emergency_close_all.py",
                "force_close_all.py",
                "check_and_force_close.py"
            ]
        },
        "utilities": {
            "description": "Trading Utilities - Support tools and helpers",
            "files": [
                "check_positions_orders.py",
                "start_intraday.py"
            ]
        }
    }
    
    # Check which files exist
    root_py_files = list(Path('.').glob('*.py'))
    existing_files = [f.name for f in root_py_files]
    
    print("CURRENT ROOT DIRECTORY PYTHON FILES:")
    print("-" * 40)
    for i, filename in enumerate(sorted(existing_files), 1):
        file_size = Path(filename).stat().st_size / 1024
        print(f"{i:2d}. {filename:<35} {file_size:>6.1f}KB")
    
    print(f"\nTotal: {len(existing_files)} Python files")
    print()
    
    # Show proposed organization
    print("PROPOSED FUNCTIONAL ORGANIZATION:")
    print("=" * 80)
    
    total_files_to_move = 0
    organization_plan = {}
    
    for group_name, group_info in functional_groups.items():
        print(f"\n📂 {group_name.upper()}/ - {group_info['description']}")
        print("-" * 60)
        
        group_files = []
        for filename in group_info['files']:
            if filename in existing_files:
                file_size = Path(filename).stat().st_size / 1024
                status = "✅ FOUND"
                group_files.append(filename)
                if group_name != "core":  # Don't move core files
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
        print(f"\n📁 UNGROUPED FILES:")
        print("-" * 40)
        for filename in ungrouped_files:
            file_size = Path(filename).stat().st_size / 1024
            print(f"  {filename:<35} {file_size:>6.1f}KB  ❓ REVIEW NEEDED")
    
    print()
    print("ORGANIZATION STRATEGY:")
    print("=" * 80)
    print("🎯 OBJECTIVE: Group files by function while preserving core system")
    print()
    print("📋 PROPOSED ACTIONS:")
    print(f"   • KEEP IN ROOT: {len(organization_plan['core'])} core system files")
    print(f"   • CREATE monitoring/: {len(organization_plan['monitoring'])} dashboard files")
    print(f"   • CREATE reporting/: {len(organization_plan['reporting'])} analysis files")
    print(f"   • CREATE emergency/: {len(organization_plan['emergency'])} control files")
    print(f"   • CREATE utilities/: {len(organization_plan['utilities'])} helper files")
    if ungrouped_files:
        print(f"   • REVIEW: {len(ungrouped_files)} ungrouped files need categorization")
    
    print()
    print("🔍 ANALYSIS:")
    print(f"   • Total files to organize: {len(existing_files)}")
    print(f"   • Files staying in root: {len(organization_plan['core'])}")
    print(f"   • Files moving to subdirs: {total_files_to_move}")
    print(f"   • New subdirectories: {len([g for g in functional_groups.keys() if g != 'core'])}")
    
    # Ask for confirmation
    print()
    response = input("📝 Proceed with functional organization? (y/N): ").strip().lower()
    
    if response != 'y':
        print("❌ Organization cancelled by user")
        return False
    
    print()
    print("EXECUTING FUNCTIONAL ORGANIZATION:")
    print("=" * 80)
    
    # Create directories and move files
    moved_files = []
    created_dirs = []
    errors = []
    
    for group_name, group_files in organization_plan.items():
        if group_name == "core":
            # Core files stay in root
            print(f"📂 {group_name.upper()}/ - Files staying in root directory")
            for filename in group_files:
                print(f"   ✅ KEEP: {filename}")
            continue
        
        # Create directory if it doesn't exist
        group_dir = Path(group_name)
        if not group_dir.exists():
            group_dir.mkdir()
            created_dirs.append(group_name)
            print(f"📁 CREATED: {group_name}/")
        
        # Move files to group directory
        print(f"📂 {group_name.upper()}/ - Moving {len(group_files)} files")
        
        for filename in group_files:
            source_path = Path(filename)
            dest_path = group_dir / filename
            
            try:
                shutil.move(str(source_path), str(dest_path))
                moved_files.append((filename, group_name))
                print(f"   ✅ MOVED: {filename} → {group_name}/")
                
            except Exception as e:
                errors.append(f"{filename}: {e}")
                print(f"   ❌ ERROR: {filename} - {e}")
    
    # Handle ungrouped files
    if ungrouped_files:
        print(f"\n📁 UNGROUPED FILES - Need manual categorization:")
        for filename in ungrouped_files:
            print(f"   ❓ {filename} - Review and categorize manually")
    
    # Create organization report
    print()
    print("FINAL FUNCTIONAL ORGANIZATION:")
    print("=" * 80)
    
    # Check final root directory
    final_root_files = list(Path('.').glob('*.py'))
    print(f"📁 ROOT DIRECTORY: {len(final_root_files)} Python files")
    for f in sorted(final_root_files, key=lambda x: x.name):
        size_kb = f.stat().st_size / 1024
        print(f"   🔧 {f.name:<35} {size_kb:>6.1f}KB")
    
    # Show created subdirectories
    for group_name in created_dirs:
        group_files = list(Path(group_name).glob('*.py'))
        if group_files:
            print(f"\n📂 {group_name.upper()}/: {len(group_files)} files")
            for f in sorted(group_files, key=lambda x: x.name):
                size_kb = f.stat().st_size / 1024
                icon = {"monitoring": "📊", "reporting": "📋", "emergency": "🚨", "utilities": "🔧"}.get(group_name, "📁")
                print(f"   {icon} {f.name:<35} {size_kb:>6.1f}KB")
    
    # Create summary report
    report_content = f"""# Functional Organization Report
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- Files organized: {len(moved_files)}
- Directories created: {len(created_dirs)}
- Files remaining in root: {len(final_root_files)}
- Errors: {len(errors)}

## Organization Structure

### Core System Files (Root Directory)
Essential trading system components that remain in root:
"""
    
    for f in sorted(final_root_files, key=lambda x: x.name):
        size_kb = f.stat().st_size / 1024
        report_content += f"- {f.name} ({size_kb:.1f}KB)\n"
    
    for group_name in created_dirs:
        group_files = list(Path(group_name).glob('*.py'))
        if group_files:
            group_desc = functional_groups[group_name]['description']
            report_content += f"\n### {group_name.title()} Directory\n{group_desc}\n"
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
    report_path = Path("functional_organization_report.md")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print()
    print("ORGANIZATION RESULTS:")
    print("=" * 80)
    print(f"✅ Successfully organized: {len(moved_files)} files")
    print(f"📁 Directories created: {len(created_dirs)}")
    print(f"🏠 Files in root: {len(final_root_files)}")
    print(f"📋 Report saved: {report_path}")
    
    if len(moved_files) > 0:
        print()
        print("🎉 FUNCTIONAL ORGANIZATION COMPLETE!")
        print("=" * 80)
        print("🎯 RESULTS:")
        print(f"   📊 Trading system organized by function")
        print(f"   🗂️ {len(created_dirs)} functional subdirectories created")
        print(f"   🔧 Core system files remain easily accessible in root")
        print(f"   📁 Support files organized by purpose")
        print()
        print("🚀 YOUR WORKSPACE IS NOW FUNCTIONALLY ORGANIZED!")
        print("   - Core trading files remain in root for easy access")
        print("   - Related functionality grouped together")
        print("   - Clean separation of concerns")
        print("   - Easy to find and maintain specific types of tools")
    
    return len(moved_files) > 0

if __name__ == "__main__":
    try:
        success = organize_by_function()
        if success:
            print("\n🏆 FUNCTIONAL ORGANIZATION COMPLETED SUCCESSFULLY! 🏆")
        else:
            print("\n📝 Organization cancelled or no changes made")
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
