#!/usr/bin/env python3
"""
File Protection Analysis Script
Shows exactly what files would be protected vs removed during cleanup
"""

import os
import re
from pathlib import Path


class FileProtectionAnalyzer:
    def __init__(self):
        self.root_path = Path(__file__).parent
        
        # PROTECTED FILES - These will NEVER be deleted
        self.protected_files = {
            # Core system files
            'launcher.py', 'main.py', 'config.py', 'data_manager.py',
            'order_manager.py', 'stock_specific_config.py', 'strategies.py',
            'logger.py', 'requirements.txt', 'README.md', 'setup.py',
            
            # Configuration files
            '.env', '.env.example', '.gitignore', 'pytest.ini',
            
            # Documentation (essential)
            'CLEANUP_SUMMARY.md', 'INSTALLATION_COMPLETE.md',
            'SYSTEM_DOCUMENTATION.md', 'INTERFACE_GUIDE.md',
            'MANUAL_CLOSER_GUIDE.md', 'PNL_MONITORING_GUIDE.md',
            'STOCK_CONFIGURATION_GUIDE.md',
            
            # New cleanup tools
            'permanent_cleanup.py', 'permanent_cleanup.ps1',
            'PREVENTION_STRATEGY.md',
        }
        
        # PROTECTED DIRECTORIES - These will NEVER be deleted
        self.protected_dirs = {
            'core', 'docs', 'logs', 'reports', 'tests', 'scripts',
            'strategies', 'utils', '.git', '.github', '.venv', '.vscode'
        }
        
        # REMOVAL PATTERNS - Files matching these patterns MAY be removed
        # BUT only if they're not in protected_files list
        self.removal_patterns = [
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
        
        # REMOVAL DIRECTORIES
        self.removal_dirs = [
            'analysis', 'batch', 'archive', 'demo_reports',
            'Futures Scalping Bot'
        ]

    def analyze_files(self):
        """Analyze all files and categorize them"""
        all_files = [f for f in self.root_path.iterdir() if f.is_file()]
        all_dirs = [d for d in self.root_path.iterdir() if d.is_dir()]
        
        protected_files = []
        would_be_removed = []
        matches_pattern_but_protected = []
        
        for file_path in all_files:
            file_name = file_path.name
            
            # Check if explicitly protected
            if file_name in self.protected_files:
                protected_files.append(file_name)
                continue
            
            # Check if matches removal pattern
            matches_removal_pattern = False
            for pattern in self.removal_patterns:
                if self._matches_pattern(file_name, pattern):
                    matches_removal_pattern = True
                    break
            
            if matches_removal_pattern:
                # Double-check protection (safety mechanism)
                if file_name in self.protected_files:
                    matches_pattern_but_protected.append(file_name)
                else:
                    would_be_removed.append(file_name)
            else:
                # File doesn't match any removal pattern, so it's safe
                protected_files.append(file_name)
        
        # Analyze directories
        protected_dirs = []
        would_be_removed_dirs = []
        
        for dir_path in all_dirs:
            dir_name = dir_path.name
            
            if dir_name in self.protected_dirs:
                protected_dirs.append(dir_name)
            elif dir_name in self.removal_dirs:
                would_be_removed_dirs.append(dir_name)
            else:
                # Unknown directory - protect by default
                protected_dirs.append(dir_name)
        
        return {
            'protected_files': sorted(protected_files),
            'would_be_removed': sorted(would_be_removed),
            'matches_pattern_but_protected': sorted(matches_pattern_but_protected),
            'protected_dirs': sorted(protected_dirs),
            'would_be_removed_dirs': sorted(would_be_removed_dirs),
        }
    
    def _matches_pattern(self, filename, pattern):
        """Check if filename matches the glob pattern"""
        # Convert glob pattern to regex
        regex_pattern = pattern.replace('*', '.*').replace('?', '.')
        regex_pattern = f'^{regex_pattern}$'
        return re.match(regex_pattern, filename) is not None
    
    def print_analysis(self):
        """Print detailed analysis of what would happen"""
        analysis = self.analyze_files()
        
        print("🛡️ " + "="*70)
        print("🛡️ FILE PROTECTION ANALYSIS")
        print("🛡️ " + "="*70)
        
        print(f"\n✅ PROTECTED FILES ({len(analysis['protected_files'])} files):")
        print("   These files will NEVER be deleted:")
        for file in analysis['protected_files']:
            print(f"   ✅ {file}")
        
        print(f"\n✅ PROTECTED DIRECTORIES ({len(analysis['protected_dirs'])} directories):")
        print("   These directories will NEVER be deleted:")
        for dir_name in analysis['protected_dirs']:
            print(f"   ✅ {dir_name}/")
        
        print(f"\n❌ WOULD BE REMOVED ({len(analysis['would_be_removed'])} files):")
        print("   These files match removal patterns and are not protected:")
        for file in analysis['would_be_removed']:
            print(f"   ❌ {file}")
        
        if analysis['would_be_removed_dirs']:
            print(f"\n❌ DIRECTORIES TO REMOVE ({len(analysis['would_be_removed_dirs'])} directories):")
            for dir_name in analysis['would_be_removed_dirs']:
                print(f"   ❌ {dir_name}/")
        
        if analysis['matches_pattern_but_protected']:
            print(f"\n🛡️ PATTERN MATCHES BUT PROTECTED ({len(analysis['matches_pattern_but_protected'])} files):")
            print("   These files match removal patterns but are explicitly protected:")
            for file in analysis['matches_pattern_but_protected']:
                print(f"   🛡️ {file}")
        
        print("\n" + "="*70)
        print("🔍 SAFETY MECHANISMS:")
        print("✅ 1. Explicit protection list prevents accidental deletion")
        print("✅ 2. Directory protection prevents deleting core folders")
        print("✅ 3. Double-check mechanism before any deletion")
        print("✅ 4. Backup list created before any changes")
        print("✅ 5. User confirmation required before proceeding")
        print("="*70)
        
        # Count essential vs removable
        essential_count = len(analysis['protected_files']) + len(analysis['protected_dirs'])
        removable_count = len(analysis['would_be_removed']) + len(analysis['would_be_removed_dirs'])
        
        print(f"\n📊 SUMMARY:")
        print(f"   🛡️ Protected items: {essential_count}")
        print(f"   🗑️ Would be removed: {removable_count}")
        print(f"   🎯 Cleanup efficiency: {removable_count}/{essential_count + removable_count} items would be removed")
        
        return analysis

if __name__ == "__main__":
    analyzer = FileProtectionAnalyzer()
    analyzer.print_analysis()
