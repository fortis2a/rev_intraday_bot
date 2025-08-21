#!/usr/bin/env python3
"""
Workspace File Analysis Tool
Categorizes files by importance and usage to identify candidates for archiving
"""

from pathlib import Path
import os
from datetime import datetime

def analyze_workspace_files():
    """Analyze all files in the workspace and categorize them"""
    
    print("🔍 WORKSPACE FILE ANALYSIS")
    print("=" * 80)
    print(f"📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    root_dir = Path(".")
    
    # Define file categories
    categories = {
        "🎯 CORE_SYSTEM": {
            "description": "Essential system files - NEVER ARCHIVE",
            "files": []
        },
        "📁 ACTIVE_COMPONENTS": {
            "description": "Currently used components - KEEP",
            "files": []
        },
        "🔧 UTILITIES": {
            "description": "Utility scripts - REVIEW NEEDED",
            "files": []
        },
        "📊 ANALYSIS_TOOLS": {
            "description": "Analysis and reporting tools - REVIEW NEEDED", 
            "files": []
        },
        "🧪 TEST_FILES": {
            "description": "Test and debug files - CANDIDATE FOR ARCHIVE",
            "files": []
        },
        "📝 DOCUMENTATION": {
            "description": "Documentation files - KEEP RECENT",
            "files": []
        },
        "🗂️ BACKUP_TEMP": {
            "description": "Backup/temp files - CANDIDATE FOR ARCHIVE",
            "files": []
        },
        "❓ UNKNOWN": {
            "description": "Need manual review",
            "files": []
        }
    }
    
    # Core system files (never archive)
    core_files = {
        'launcher.py', 'main.py', 'config.py', 'data_manager.py', 'order_manager.py',
        'strategies.py', 'strategies_enhanced.py', 'stock_specific_config.py',
        'logger.py', '.env', '.env.example', 'requirements.txt', 'setup.py',
        'README.md'
    }
    
    # Active components
    active_files = {
        'market_close_report.py', 'live_dashboard.py', 'realtime_status_monitor.py',
        'system_status.py', 'check_positions_orders.py', 'generate_todays_pnl.py',
        'show_all_orders.py', 'simple_close_all.py', 'emergency_close_everything.py',
        'check_and_force_close.py', 'start_enhanced_command_center.bat'
    }
    
    # Test files patterns
    test_patterns = ['test_', 'debug_', 'demo_', 'verify_', 'check_']
    
    # Backup patterns
    backup_patterns = ['backup_', '_backup', 'cleanup_', 'temp_', 'TEMP']
    
    # Get all Python files in root
    for file_path in root_dir.iterdir():
        if file_path.is_file():
            filename = file_path.name
            
            # Categorize file
            if filename in core_files:
                categories["🎯 CORE_SYSTEM"]["files"].append(filename)
            elif filename in active_files:
                categories["📁 ACTIVE_COMPONENTS"]["files"].append(filename)
            elif any(filename.startswith(pattern) for pattern in test_patterns):
                categories["🧪 TEST_FILES"]["files"].append(filename)
            elif any(pattern in filename for pattern in backup_patterns):
                categories["🗂️ BACKUP_TEMP"]["files"].append(filename)
            elif filename.endswith('.md') or filename.endswith('.txt'):
                categories["📝 DOCUMENTATION"]["files"].append(filename)
            elif 'analysis' in filename.lower() or 'report' in filename.lower() or 'pnl' in filename.lower():
                categories["📊 ANALYSIS_TOOLS"]["files"].append(filename)
            elif filename.endswith('.py'):
                categories["🔧 UTILITIES"]["files"].append(filename)
            else:
                categories["❓ UNKNOWN"]["files"].append(filename)
    
    # Add note about related scripts
    if 'start_enhanced_command_center.bat' in categories["📁 ACTIVE_COMPONENTS"]["files"]:
        categories["📁 ACTIVE_COMPONENTS"]["files"].append("scripts/scalping_command_center.py (referenced)")
    
    # Print categorized analysis
    total_files = 0
    archive_candidates = 0
    
    for category, info in categories.items():
        files = info["files"]
        if files:
            print(f"{category} ({len(files)} files)")
            print(f"   Description: {info['description']}")
            
            # Sort files for better readability
            files.sort()
            
            # Show files in columns
            for i, filename in enumerate(files):
                if i % 3 == 0:
                    print("   ", end="")
                print(f"{filename:<35}", end="")
                if (i + 1) % 3 == 0 or i == len(files) - 1:
                    print()
            
            total_files += len(files)
            
            if "CANDIDATE FOR ARCHIVE" in info["description"]:
                archive_candidates += len(files)
            
            print()
    
    # Summary
    print("📊 SUMMARY")
    print("=" * 80)
    print(f"Total files analyzed: {total_files}")
    print(f"Archive candidates: {archive_candidates}")
    print(f"Files to keep: {total_files - archive_candidates}")
    
    print()
    print("🎯 RECOMMENDATIONS:")
    print("1. Core system files: NEVER ARCHIVE (essential for operation)")
    print("2. Active components: KEEP (currently in use)")
    print("3. Test/Debug files: REVIEW and likely archive (outdated testing)")
    print("4. Backup/Temp files: ARCHIVE (temporary files no longer needed)")
    print("5. Utilities: REVIEW each individually")
    print("6. Analysis tools: REVIEW (keep recent, archive old)")
    print()
    
    return categories

if __name__ == "__main__":
    analyze_workspace_files()
