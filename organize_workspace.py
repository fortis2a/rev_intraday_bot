#!/usr/bin/env python3
"""
File Organization Script
Moves files to appropriate organized folders based on their purpose
"""

import os
import shutil
from pathlib import Path

class FileOrganizer:
    def __init__(self):
        self.root_path = Path(__file__).parent
        
        # Define target directories and their purposes
        self.organization_plan = {
            'scripts/': [
                # Analysis and diagnostic files
                'analyze_*.py', 'check_*.py', 'diagnose_*.py', 'investigate_*.py',
                'verify_*.py', 'validate_*.py', 'quick_*.py',
                # Utility scripts
                'backup_*.py', 'setup_*.py', 'eod_*.py', 'generate_*.py',
                'live_signal_check.py', 'live_pnl_external.py', 'log_viewer.py',
                'position_cleanup.py', 'stock_watchlist.py', 'workspace_cleanup.py',
                'WORKSPACE_CLEANUP_SCRIPT.py', 'permanent_cleanup.py',
                # Trading analysis
                'trading_analysis.py', 'stop_loss_analyzer.py', 'stop_loss_repair.py',
                'trailing_stop_analysis.py', 'qbts_strategy_analysis.py',
                'rule_violation_analysis.py', 'pnl_discrepancy_analysis.py',
                'execution_flaw_analysis.py',
                # Comprehensive reports
                'comprehensive_pnl_report.py', 'eod_report_generator.py',
                'unicode_safe_test.py', 'updated_position_check.py',
                'simple_trailing_test.py'
            ],
            
            'docs/summaries/': [
                # Summary files
                'datamanager_fix_summary.py', 'data_consistency_fixes_summary.py',
                'data_safety_summary.py', 'ENHANCED_INDICATORS_SUMMARY.py',
                'enhanced_stop_loss_summary.py', 'immediate_closure_fixes_summary.py',
                'parameter_fix_summary.py', 'phantom_position_fix_summary.py',
                'position_fixes_summary.py', 'trailing_stop_fix_summary.py',
                'trailing_stop_fixes_complete.py'
            ],
            
            'docs/': [
                # Documentation files
                'CLEANUP_PLAN.md', 'CLEANUP_SUMMARY.md', 'FUTURES_README.md',
                'INSTALLATION_COMPLETE.md', 'INTERFACE_GUIDE.md', 
                'PREVENTION_STRATEGY.md', 'SYSTEM_DOCUMENTATION.md'
            ],
            
            'utils/': [
                # Manager files that are utilities
                'pnl_manager.py', 'logger.py'
            ],
            
            'core/': [
                # Core system files that aren't in core yet
                'data_manager.py', 'order_manager.py'
            ]
        }
        
        # Files that should stay in root
        self.root_files = {
            'launcher.py', 'main.py', 'config.py', 'stock_specific_config.py',
            'strategies.py', 'strategies_enhanced.py', 'requirements.txt', 
            'setup.py', 'pytest.ini', 'README.md', '.env', '.env.example',
            '.gitignore', 'demo.py'
        }
    
    def create_directories(self):
        """Create target directories if they don't exist"""
        print("📁 Creating target directories...")
        
        for dir_path in self.organization_plan.keys():
            target_dir = self.root_path / dir_path
            target_dir.mkdir(parents=True, exist_ok=True)
            print(f"  ✅ {dir_path}")
    
    def organize_files(self):
        """Move files to their appropriate directories"""
        print("🗂️ Organizing files...")
        
        moved_count = 0
        
        for target_dir, patterns in self.organization_plan.items():
            target_path = self.root_path / target_dir
            
            for pattern in patterns:
                # Handle exact filenames
                if not ('*' in pattern):
                    source_file = self.root_path / pattern
                    if source_file.exists() and source_file.is_file():
                        dest_file = target_path / pattern
                        try:
                            shutil.move(str(source_file), str(dest_file))
                            print(f"  ➡️ {pattern} → {target_dir}")
                            moved_count += 1
                        except Exception as e:
                            print(f"  ⚠️ Could not move {pattern}: {e}")
                else:
                    # Handle glob patterns
                    matches = list(self.root_path.glob(pattern))
                    for match in matches:
                        if match.is_file() and match.name not in self.root_files:
                            dest_file = target_path / match.name
                            try:
                                shutil.move(str(match), str(dest_file))
                                print(f"  ➡️ {match.name} → {target_dir}")
                                moved_count += 1
                            except Exception as e:
                                print(f"  ⚠️ Could not move {match.name}: {e}")
        
        print(f"✅ Moved {moved_count} files")
    
    def show_current_structure(self):
        """Show the organized directory structure"""
        print("\n📋 Current Organized Structure:")
        
        def show_directory(path, indent=0):
            prefix = "  " * indent
            if path.is_dir():
                print(f"{prefix}📁 {path.name}/")
                try:
                    items = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
                    for item in items[:5]:  # Show first 5 items
                        if item.name.startswith('.'):
                            continue
                        if item.is_dir():
                            show_directory(item, indent + 1)
                        else:
                            print(f"{prefix}  📄 {item.name}")
                    
                    # Count remaining files
                    remaining = [f for f in items[5:] if not f.name.startswith('.')]
                    if remaining:
                        print(f"{prefix}  ... and {len(remaining)} more items")
                except PermissionError:
                    print(f"{prefix}  (access denied)")
        
        # Show main directories
        main_dirs = ['core', 'strategies', 'utils', 'scripts', 'docs', 'tests']
        for dir_name in main_dirs:
            dir_path = self.root_path / dir_name
            if dir_path.exists():
                show_directory(dir_path)
        
        # Show root files
        print("\n📁 Root files:")
        root_files = [f for f in self.root_path.iterdir() 
                     if f.is_file() and not f.name.startswith('.')]
        for file in sorted(root_files, key=lambda x: x.name.lower())[:10]:
            print(f"  📄 {file.name}")
        if len(root_files) > 10:
            print(f"  ... and {len(root_files) - 10} more files")
    
    def update_gitignore_for_organization(self):
        """Update .gitignore to reflect the new organization"""
        print("📝 Updating .gitignore for organized structure...")
        
        gitignore_additions = """
# === ORGANIZED STRUCTURE RULES ===
# Allow organized files in proper directories
!scripts/analyze_*.py
!scripts/check_*.py
!scripts/diagnose_*.py
!scripts/backup_*.py
!scripts/setup_*.py
!scripts/trading_*.py
!docs/summaries/*_summary.py
!docs/summaries/*_SUMMARY.py
!docs/*_GUIDE.md
!docs/*_README.md
!utils/pnl_*.py
!utils/live_*.py
"""
        
        gitignore_path = self.root_path / '.gitignore'
        with open(gitignore_path, 'a', encoding='utf-8') as f:
            f.write(gitignore_additions)
        
        print("✅ Updated .gitignore")
    
    def run_organization(self):
        """Run the complete file organization process"""
        print("🗂️ " + "="*60)
        print("🗂️ FILE ORGANIZATION - RESTORE FOLDER STRUCTURE")
        print("🗂️ " + "="*60)
        
        # Show current state
        root_files = [f for f in self.root_path.iterdir() if f.is_file()]
        disorganized_files = [f for f in root_files if f.name not in self.root_files 
                            and not f.name.startswith('.')]
        
        print(f"📊 Found {len(disorganized_files)} files to organize")
        print("📋 Sample files to organize:")
        for file in disorganized_files[:10]:
            print(f"  - {file.name}")
        if len(disorganized_files) > 10:
            print(f"  ... and {len(disorganized_files) - 10} more files")
        
        if not disorganized_files:
            print("✅ Files are already organized!")
            return
        
        response = input("\n🤔 Proceed with file organization? (y/N): ")
        if response.lower() != 'y':
            print("❌ Organization cancelled")
            return
        
        print("\n🚀 Starting file organization...")
        self.create_directories()
        self.organize_files()
        self.update_gitignore_for_organization()
        
        print("\n" + "="*60)
        print("✅ FILE ORGANIZATION COMPLETE!")
        print("✅ Files moved to appropriate directories")
        print("✅ .gitignore updated for organized structure")
        print("="*60)
        
        self.show_current_structure()
        
        print("\n📋 Next steps:")
        print("1. Review the organized structure above")
        print("2. Run: git add . && git commit -m 'Organize files into folders'")
        print("3. Your workspace is now properly organized!")

if __name__ == "__main__":
    organizer = FileOrganizer()
    organizer.run_organization()
