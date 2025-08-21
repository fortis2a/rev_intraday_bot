#!/usr/bin/env python3
"""
Comprehensive Workspace Cleanup Script
Prevents VS Code auto-restore by using proper git commands
Can be re-run safely to maintain clean workspace
"""

import os
import subprocess
import shutil
from pathlib import Path
import json

class WorkspaceCleanup:
    def __init__(self):
        self.root_path = Path(__file__).parent
        self.files_to_remove = []
        self.dirs_to_remove = []
        self.protected_files = {
            # Core system files
            'launcher.py', 'main.py', 'config.py', 'data_manager.py',
            'order_manager.py', 'stock_specific_config.py', 'strategies.py',
            'logger.py', 'requirements.txt', 'README.md', 'setup.py',
            
            # Configuration files
            '.env', '.env.example', '.gitignore', 'pytest.ini',
            
            # Documentation
            'CLEANUP_SUMMARY.md', 'INSTALLATION_COMPLETE.md',
            'SYSTEM_DOCUMENTATION.md', 'INTERFACE_GUIDE.md',
        }
        self.protected_dirs = {
            'core', 'docs', 'logs', 'reports', 'tests', 'scripts',
            'strategies', 'utils', '.git', '.github', '.venv', '.vscode'
        }
        
    def identify_files_to_remove(self):
        """Identify files that should be removed"""
        print("🔍 Scanning workspace for files to remove...")
        
        # Patterns for files to remove
        removal_patterns = [
            # Test and demo files (root level only)
            'test_*.py', 'demo_*.py', '*_demo.py', 'debug_*.py',
            # Analysis and temporary files
            'analyze_*.py', 'check_*.py', 'fix_*.py', 'diagnose_*.py',
            'investigate_*.py', 'verify_*.py', 'validate_*.py',
            # Cleanup and maintenance files
            'cleanup_*.py', 'clear_*.py', 'emergency_*.py', 'force_*.py',
            'reset_*.py', 'restart_*.py', 'move_*.py',
            # Legacy and outdated files
            'legacy_*.py', 'scalping_bot.py', 'intraday_trading_bot.py',
            'main_simple.py', 'minimal_main.py', 'dashboard.py',
            'dashboard_enhanced.py', 'live_dashboard.py',
            # Monitoring files (duplicates)
            'pnl_monitor.py', 'live_pnl_monitor.py', 'rgti_*.py',
            # Manual tools
            'manual_closer.py', 'adopt_positions.py',
            # Batch and script files
            '*.bat', '*.ps1', '*.sh',
            # Analysis summaries and guides (duplicates)
            '*_SUMMARY.md', '*_GUIDE.md', '*_ANALYSIS.md',
            '*_COMPLETE.md', '*_FIX*.md',
        ]
        
        # Directories to remove
        removal_dirs = [
            'analysis', 'batch', 'archive', 'demo_reports',
            'Futures Scalping Bot'
        ]
        
        # Scan for files to remove
        for pattern in removal_patterns:
            matches = list(self.root_path.glob(pattern))
            for file_path in matches:
                if file_path.is_file() and file_path.name not in self.protected_files:
                    self.files_to_remove.append(file_path)
        
        # Scan for directories to remove
        for dir_name in removal_dirs:
            dir_path = self.root_path / dir_name
            if dir_path.exists() and dir_path.is_dir():
                self.dirs_to_remove.append(dir_path)
        
        print(f"📄 Found {len(self.files_to_remove)} files to remove")
        print(f"📁 Found {len(self.dirs_to_remove)} directories to remove")
        
    def create_backup_list(self):
        """Create a list of files being removed for potential restoration"""
        backup_list = {
            'removed_files': [str(f) for f in self.files_to_remove],
            'removed_dirs': [str(d) for d in self.dirs_to_remove],
            'timestamp': str(Path(__file__).stat().st_mtime)
        }
        
        with open(self.root_path / 'cleanup_backup_list.json', 'w') as f:
            json.dump(backup_list, f, indent=2)
        
        print("💾 Created backup list: cleanup_backup_list.json")
    
    def remove_from_git(self):
        """Remove files from git tracking to prevent VS Code restore"""
        print("🔧 Removing files from git tracking...")
        
        try:
            # Stage all files for removal from git (but keep locally temporarily)
            for file_path in self.files_to_remove:
                if file_path.exists():
                    rel_path = file_path.relative_to(self.root_path)
                    subprocess.run(['git', 'rm', '--cached', str(rel_path)], 
                                 cwd=self.root_path, capture_output=True)
            
            for dir_path in self.dirs_to_remove:
                if dir_path.exists():
                    rel_path = dir_path.relative_to(self.root_path)
                    subprocess.run(['git', 'rm', '-r', '--cached', str(rel_path)], 
                                 cwd=self.root_path, capture_output=True)
            
            print("✅ Files removed from git tracking")
            
        except Exception as e:
            print(f"⚠️ Git removal warning: {e}")
    
    def physical_removal(self):
        """Physically remove the files and directories"""
        print("🗑️ Physically removing files...")
        
        removed_count = 0
        
        # Remove files
        for file_path in self.files_to_remove:
            try:
                if file_path.exists():
                    file_path.unlink()
                    removed_count += 1
                    print(f"  ❌ {file_path.name}")
            except Exception as e:
                print(f"  ⚠️ Could not remove {file_path.name}: {e}")
        
        # Remove directories
        for dir_path in self.dirs_to_remove:
            try:
                if dir_path.exists():
                    shutil.rmtree(dir_path)
                    removed_count += 1
                    print(f"  ❌ {dir_path.name}/")
            except Exception as e:
                print(f"  ⚠️ Could not remove {dir_path.name}/: {e}")
        
        print(f"✅ Removed {removed_count} items")
    
    def clean_pycache(self):
        """Remove all __pycache__ directories"""
        print("🧹 Cleaning Python cache files...")
        
        pycache_dirs = list(self.root_path.rglob('__pycache__'))
        for cache_dir in pycache_dirs:
            try:
                shutil.rmtree(cache_dir)
                print(f"  ❌ {cache_dir.relative_to(self.root_path)}")
            except Exception as e:
                print(f"  ⚠️ Could not remove cache: {e}")
    
    def update_gitignore(self):
        """Update .gitignore to prevent future issues"""
        print("📝 Updating .gitignore...")
        
        gitignore_additions = """
# === WORKSPACE CLEANUP PROTECTION ===
# Prevent VS Code auto-restore of unwanted files

# Development and testing files (root level only)
/test_*.py
/demo_*.py
/*_demo.py
/debug_*.py
/temp_*.py
/tmp_*.py

# Analysis and diagnostic files
/analyze_*.py
/check_*.py
/fix_*.py
/diagnose_*.py
/investigate_*.py
/verify_*.py
/validate_*.py

# Cleanup and maintenance files
/cleanup_*.py
/clear_*.py
/emergency_*.py
/force_*.py
/reset_*.py
/restart_*.py
/move_*.py

# Legacy and outdated files
/legacy_*.py
/scalping_bot.py
/intraday_trading_bot.py
/main_simple.py
/minimal_main.py

# Duplicate dashboards
/dashboard.py
/dashboard_enhanced.py
/live_dashboard.py

# Batch and script files
*.bat
*.ps1
*.sh

# Analysis summaries and guides (excessive)
/*_SUMMARY.md
/*_GUIDE.md
/*_ANALYSIS.md
/*_COMPLETE.md
/*_FIX*.md

# Temporary directories
/analysis/
/batch/
/archive/
/demo_reports/

# Backup files
cleanup_backup_list.json

# Exclude legitimate files in subdirectories
!scripts/test_*.py
!tests/test_*.py
!docs/*_GUIDE.md
!docs/*_SUMMARY.md
"""
        
        gitignore_path = self.root_path / '.gitignore'
        with open(gitignore_path, 'a', encoding='utf-8') as f:
            f.write(gitignore_additions)
        
        print("✅ Updated .gitignore with protection rules")
    
    def configure_vscode(self):
        """Configure VS Code to prevent auto-restore"""
        print("⚙️ Configuring VS Code settings...")
        
        vscode_dir = self.root_path / '.vscode'
        vscode_dir.mkdir(exist_ok=True)
        
        settings = {
            "files.watcherExclude": {
                "**/test_*.py": True,
                "**/demo_*.py": True,
                "**/*_demo.py": True,
                "**/debug_*.py": True,
                "**/analyze_*.py": True,
                "**/cleanup_*.py": True,
                "**/*.bat": True,
                "**/*.ps1": True,
                "**/analysis/**": True,
                "**/batch/**": True,
                "**/archive/**": True
            },
            "files.exclude": {
                "**/test_*.py": True,
                "**/demo_*.py": True,
                "**/*_demo.py": True,
                "**/debug_*.py": True
            },
            "search.exclude": {
                "**/test_*.py": True,
                "**/demo_*.py": True,
                "**/*_demo.py": True,
                "**/debug_*.py": True,
                "**/analyze_*.py": True,
                "**/cleanup_*.py": True
            }
        }
        
        settings_path = vscode_dir / 'settings.json'
        with open(settings_path, 'w') as f:
            json.dump(settings, f, indent=2)
        
        print("✅ VS Code configured to ignore temporary files")
    
    def run_cleanup(self):
        """Run the complete cleanup process"""
        print("🧹 " + "="*60)
        print("🧹 COMPREHENSIVE WORKSPACE CLEANUP")
        print("🧹 " + "="*60)
        
        self.identify_files_to_remove()
        
        if not self.files_to_remove and not self.dirs_to_remove:
            print("✅ Workspace is already clean!")
            return
        
        print("\n📋 Files/directories to be removed:")
        for f in self.files_to_remove[:10]:  # Show first 10
            print(f"  - {f.name}")
        if len(self.files_to_remove) > 10:
            print(f"  ... and {len(self.files_to_remove) - 10} more files")
        
        for d in self.dirs_to_remove:
            print(f"  - {d.name}/")
        
        response = input("\n🤔 Proceed with cleanup? (y/N): ")
        if response.lower() != 'y':
            print("❌ Cleanup cancelled")
            return
        
        print("\n🚀 Starting cleanup...")
        self.create_backup_list()
        self.remove_from_git()
        self.physical_removal()
        self.clean_pycache()
        self.update_gitignore()
        self.configure_vscode()
        
        print("\n" + "="*60)
        print("✅ WORKSPACE CLEANUP COMPLETE!")
        print("✅ VS Code protection configured")
        print("✅ Git tracking updated")
        print("✅ .gitignore enhanced")
        print("="*60)
        
        print("\n📋 Next steps:")
        print("1. Restart VS Code to apply settings")
        print("2. Run: git add . && git commit -m 'Clean workspace'")
        print("3. If files reappear, re-run this script")

if __name__ == "__main__":
    cleanup = WorkspaceCleanup()
    cleanup.run_cleanup()
