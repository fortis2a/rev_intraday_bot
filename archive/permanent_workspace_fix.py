#!/usr/bin/env python3
"""
PERMANENT WORKSPACE ORGANIZATION FIX
=====================================

This script will:
1. Move files to proper directories (AGAIN)
2. Create .vscode settings to maintain organization
3. Add .gitignore entries to prevent Git from reverting changes
4. Create workspace shortcuts for easy access

Run this script whenever VS Code reverts to unorganized state.
"""

import json
import os
import shutil
from pathlib import Path


def create_directories():
    """Create organized directory structure"""
    dirs = [
        "core",
        "strategies",
        "scripts/utilities",
        "scripts/monitoring",
        "scripts/emergency",
        "batch_files",
        "analysis_tools",
        "dashboard",
        "database",
        "reporting",
        "emergency",
        "monitoring",
        "tests",
        "docs/system_reports",
        "docs/implementation",
        "archive/old_analysis",
        "archive/old_debug",
        "utilities/cleanup",
        "utilities/verification",
    ]

    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created: {dir_path}")


def organize_files():
    """Move files to organized structure"""

    # Core trading files (KEEP IN ROOT - these are essential)
    core_files = [
        "main.py",
        "launcher.py",
        "config.py",
        "stock_specific_config.py",
        "strategies.py",
        "logger.py",
    ]

    # Files to organize by category
    file_moves = {
        # Analysis tools
        "analysis_tools/": [
            "enhanced_daily_analysis.py",
            "today_analysis.py",
            "three_day_summary.py",
            "advanced_market_analysis.py",
            "market_close_report.py",
            "pnl_enhancement_summary.py",
        ],
        # Emergency scripts
        "scripts/emergency/": [
            "emergency_close_all.py",
            "force_close_all.py",
            "emergency_close_everything.py",
            "simple_close_all.py",
            "cleanup_and_close.py",
            "close_trade.py",
        ],
        # Monitoring scripts
        "scripts/monitoring/": [
            "monitor_trading_status.py",
            "realtime_status_monitor.py",
            "system_status.py",
            "trading_engine_diagnostics.py",
        ],
        # Batch files
        "batch_files/": [file for file in os.listdir(".") if file.endswith(".bat")]
        + [file for file in os.listdir(".") if file.endswith(".ps1")],
        # Database files
        "database/": [
            "check_db.py",
            "check_table_structure.py",
            "update_database_schema.py",
            "verify_database.py",
        ],
        # Dashboard files
        "dashboard/": [
            "live_dashboard.py",
            "interactive_dashboard.py",
            "launch_dashboard.py",
            "debug_dashboard_direct.py",
        ],
        # Utilities
        "utilities/": [
            file
            for file in os.listdir(".")
            if file.startswith("organize_") and file.endswith(".py")
        ]
        + [
            file
            for file in os.listdir(".")
            if file.startswith("phase") and file.endswith(".py")
        ]
        + [
            "file_verification_report.py",
            "analyze_workspace_files.py",
            "backup_untracked_files.py",
        ],
        # Tests
        "tests/": [
            file
            for file in os.listdir(".")
            if file.startswith("test_") and file.endswith(".py")
        ],
        # Archive old files
        "archive/": [
            file
            for file in os.listdir(".")
            if file.startswith("debug_") and file.endswith(".py")
        ]
        + [
            file
            for file in os.listdir(".")
            if file.startswith("check_") and file.endswith(".py")
        ]
        + [
            file
            for file in os.listdir(".")
            if file.startswith("verify_") and file.endswith(".py")
        ],
    }

    # Move files
    for dest_dir, files in file_moves.items():
        for file in files:
            if os.path.exists(file) and file not in core_files:
                try:
                    shutil.move(file, dest_dir + file)
                    print(f"📁 Moved: {file} -> {dest_dir}")
                except Exception as e:
                    print(f"❌ Error moving {file}: {e}")


def create_vscode_settings():
    """Create VS Code settings to maintain organization"""

    vscode_settings = {
        "files.exclude": {
            "**/archive/**": True,
            "**/backup_untracked_*/**": True,
            "**/__pycache__/**": True,
            "**/*.pyc": True,
            "**/.git": True,
            "**/.DS_Store": True,
            "**/Thumbs.db": True,
            "**/node_modules": True,
            "**/tests/**": False,  # Show tests but collapsed
            "**/docs/**": False,  # Show docs but collapsed
        },
        "search.exclude": {
            "**/archive/**": True,
            "**/backup_untracked_*/**": True,
            "**/__pycache__/**": True,
            "**/*.pyc": True,
            "**/.git": True,
            "**/node_modules": True,
            "**/*.min.js": True,
        },
        "files.watcherExclude": {
            "**/archive/**": True,
            "**/backup_untracked_*/**": True,
            "**/__pycache__/**": True,
            "**/.git/objects/**": True,
            "**/.git/subtree-cache/**": True,
            "**/node_modules/*/**": True,
        },
        "explorer.fileNesting.enabled": True,
        "explorer.fileNesting.expand": False,
        "explorer.fileNesting.patterns": {
            "launcher.py": "main.py",
            "config.py": "stock_specific_config.py",
            "*.bat": "*.ps1",
            "requirements.txt": "requirements*.txt, setup.py, pytest.ini",
            "README.md": "*.md",
        },
        "python.defaultInterpreterPath": "./.venv/Scripts/python.exe",
        "python.terminal.activateEnvironment": True,
        "files.associations": {"*.bat": "batch", "*.ps1": "powershell"},
        "explorer.compactFolders": False,
        "explorer.sortOrder": "type",
    }

    # Create .vscode directory if it doesn't exist
    os.makedirs(".vscode", exist_ok=True)

    # Write settings
    with open(".vscode/settings.json", "w", encoding="utf-8") as f:
        json.dump(vscode_settings, f, indent=2)

    print("✅ Created VS Code settings to maintain organization")


def create_workspace_file():
    """Create a proper VS Code workspace file"""

    workspace_config = {
        "folders": [{"name": "🎯 Core Trading System", "path": "."}],
        "settings": {
            "files.exclude": {
                "**/archive/**": True,
                "**/backup_untracked_*/**": True,
                "**/__pycache__/**": True,
                "**/*.pyc": True,
            },
            "explorer.fileNesting.enabled": True,
            "python.defaultInterpreterPath": "./.venv/Scripts/python.exe",
        },
        "extensions": {
            "recommendations": [
                "ms-python.python",
                "ms-python.flake8",
                "ms-python.autopep8",
            ]
        },
    }

    with open("TradingSystem.code-workspace", "w", encoding="utf-8") as f:
        json.dump(workspace_config, f, indent=2)

    print("✅ Created TradingSystem.code-workspace file")


def update_gitignore():
    """Update .gitignore to preserve organization"""

    gitignore_additions = [
        "",
        "# Prevent reverting organization",
        "!core/",
        "!scripts/",
        "!analysis_tools/",
        "!batch_files/",
        "!database/",
        "!dashboard/",
        "!utilities/",
        "",
        "# But still ignore cache files in organized dirs",
        "**/.__pycache__/",
        "**/*.pyc",
    ]

    try:
        with open(".gitignore", "a", encoding="utf-8") as f:
            f.write("\n".join(gitignore_additions))
        print("✅ Updated .gitignore to preserve organization")
    except Exception as e:
        print(f"⚠️ Could not update .gitignore: {e}")


def create_quick_access():
    """Create quick access shortcuts"""

    shortcuts = {
        "run_trading.bat": "@echo off\necho Starting Trading System...\npython launcher.py\npause",
        "run_analysis.bat": "@echo off\necho Running Today's Analysis...\npython analysis_tools/today_analysis.py\npause",
        "emergency_stop.bat": "@echo off\necho EMERGENCY STOP - Closing all positions...\npython scripts/emergency/emergency_close_all.py\npause",
    }

    for filename, content in shortcuts.items():
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ Created: {filename}")


def main():
    """Run the complete organization fix"""
    print("🔧 PERMANENT WORKSPACE ORGANIZATION FIX")
    print("=" * 50)

    print("\n1. Creating directory structure...")
    create_directories()

    print("\n2. Organizing files...")
    organize_files()

    print("\n3. Creating VS Code settings...")
    create_vscode_settings()

    print("\n4. Creating workspace file...")
    create_workspace_file()

    print("\n5. Updating .gitignore...")
    update_gitignore()

    print("\n6. Creating quick access shortcuts...")
    create_quick_access()

    print("\n" + "=" * 50)
    print("✅ WORKSPACE ORGANIZATION COMPLETE!")
    print("\n📋 NEXT STEPS:")
    print("1. Restart VS Code")
    print("2. Open 'TradingSystem.code-workspace'")
    print("3. Use run_trading.bat for quick start")
    print("\n🔒 Organization is now PERMANENT and Git-protected!")


if __name__ == "__main__":
    main()
