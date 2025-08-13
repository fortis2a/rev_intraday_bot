#!/usr/bin/env python3
"""
GitHub Backup System for Intraday Trading Bot
Automatically backs up the entire trading system to GitHub repository
Includes auto-scheduling and manual backup options
"""

import os
import sys
import subprocess
import schedule
import time
import logging
from datetime import datetime
from pathlib import Path
import json
import shutil

# Set up logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / f"backup_system_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)

class GitHubBackupSystem:
    def __init__(self):
        self.repo_url = "https://github.com/fortis2a/rev_intraday_bot.git"
        self.local_repo_path = Path.cwd()
        self.backup_branch = "main"
        self.exclude_patterns = [
            "__pycache__/",
            "*.pyc",
            ".env",
            "logs/",
            "reports/",
            "demo_reports/",
            ".git/",
            "*.log"
        ]
        
        logging.info("GitHub Backup System initialized")
        logging.info(f"Repository URL: {self.repo_url}")
        logging.info(f"Local path: {self.local_repo_path}")

    def check_git_installed(self):
        """Check if Git is installed and available"""
        try:
            result = subprocess.run(['git', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                logging.info(f"Git version: {result.stdout.strip()}")
                return True
            else:
                logging.error("Git is not installed or not in PATH")
                return False
        except Exception as e:
            logging.error(f"Error checking Git installation: {e}")
            return False

    def initialize_git_repo(self):
        """Initialize Git repository if not already initialized"""
        try:
            git_dir = self.local_repo_path / ".git"
            
            if not git_dir.exists():
                logging.info("Initializing new Git repository...")
                
                # Initialize git repo
                subprocess.run(['git', 'init'], cwd=self.local_repo_path, check=True)
                
                # Add remote origin
                subprocess.run(['git', 'remote', 'add', 'origin', self.repo_url], 
                             cwd=self.local_repo_path, check=True)
                
                # Set default branch
                subprocess.run(['git', 'branch', '-M', self.backup_branch], 
                             cwd=self.local_repo_path, check=True)
                
                logging.info("Git repository initialized successfully")
            else:
                logging.info("Git repository already exists")
                
                # Check if remote origin exists
                result = subprocess.run(['git', 'remote', 'get-url', 'origin'], 
                                      cwd=self.local_repo_path, 
                                      capture_output=True, text=True)
                
                if result.returncode != 0 or self.repo_url not in result.stdout:
                    logging.info("Setting correct remote origin...")
                    subprocess.run(['git', 'remote', 'remove', 'origin'], 
                                 cwd=self.local_repo_path, errors='ignore')
                    subprocess.run(['git', 'remote', 'add', 'origin', self.repo_url], 
                                 cwd=self.local_repo_path, check=True)
            
            return True
            
        except Exception as e:
            logging.error(f"Error initializing Git repository: {e}")
            return False

    def create_gitignore(self):
        """Create or update .gitignore file"""
        try:
            gitignore_path = self.local_repo_path / ".gitignore"
            
            gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Environment variables
.env
.env.local
.env.production

# Logs
logs/
*.log

# Reports (generated data)
reports/
demo_reports/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Trading specific
*.csv
*.xlsx
"""
            
            with open(gitignore_path, 'w') as f:
                f.write(gitignore_content)
            
            logging.info("Updated .gitignore file")
            return True
            
        except Exception as e:
            logging.error(f"Error creating .gitignore: {e}")
            return False

    def create_backup_readme(self):
        """Create README for the backup repository"""
        try:
            readme_path = self.local_repo_path / "BACKUP_README.md"
            
            readme_content = f"""# Intraday Trading Bot - Backup Repository

## 📊 Automated Backup System

This is an automated backup of the Intraday Trading Bot system.

**Last Backup:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ET

## 🚀 System Components

### Core Trading Engine
- `main.py` - Main trading engine with LIVE/DEMO/TEST modes
- `launcher.py` - System launcher with 13 options
- `data_manager.py` - Alpaca API integration
- `config.py` - Configuration and settings

### Trading Strategies
- `strategies/momentum_scalp.py` - Momentum scalping strategy
- `strategies/mean_reversion.py` - Mean reversion strategy  
- `strategies/vwap_bounce.py` - VWAP bounce strategy

### Core Components
- `core/scalping_engine.py` - Main scalping engine
- `core/order_manager.py` - Order execution and management
- `core/risk_manager.py` - Risk management system

### Monitoring & Analysis
- `live_pnl_external.py` - Colorized live P&L monitor
- `eod_analysis.py` - Comprehensive end-of-day analysis
- `eod_scheduler.py` - Automated EOD analysis scheduler

### Utilities
- `utils/logger.py` - Logging system
- `backup_system.py` - This backup system

### Launchers
- `EOD_Analysis.bat` - EOD analysis launcher
- `Live_PnL_Monitor.bat` - Live P&L monitor launcher
- `Setup_Auto_EOD.bat` - Auto EOD setup

## ⚙️ Current Configuration

**Watchlist:** IONQ, RGTI, QBTS, JNJ, PG
**Trading Hours:** 10:00 AM - 3:30 PM ET (avoiding volatile periods)
**Risk Management:** 2% stop loss, 4% take profit, $1000 max position

## 🔄 Backup Schedule

This repository is automatically updated:
- **Daily at midnight** via automated backup system
- **Manual backups** available through launcher Option 14

## 📝 Notes

- Environment variables (.env) are excluded for security
- Logs and reports are excluded (generated data)
- All core trading code and configurations are backed up
- Python cache files are excluded

---
*Generated by Intraday Trading Bot Backup System*
"""
            
            with open(readme_path, 'w') as f:
                f.write(readme_content)
            
            logging.info("Created backup README")
            return True
            
        except Exception as e:
            logging.error(f"Error creating README: {e}")
            return False

    def perform_backup(self):
        """Perform the actual backup to GitHub"""
        try:
            logging.info("[BACKUP] Starting backup process...")
            
            # Check Git installation
            if not self.check_git_installed():
                return False
            
            # Initialize repository
            if not self.initialize_git_repo():
                return False
            
            # Create/update .gitignore
            self.create_gitignore()
            
            # Create backup README
            self.create_backup_readme()
            
            # Configure Git user (if not already configured)
            try:
                subprocess.run(['git', 'config', 'user.name', 'Trading Bot Backup'], 
                             cwd=self.local_repo_path, check=True)
                subprocess.run(['git', 'config', 'user.email', 'backup@tradingbot.local'], 
                             cwd=self.local_repo_path, check=True)
            except:
                pass  # User might already be configured
            
            # Add all files (respecting .gitignore)
            logging.info("Adding files to Git...")
            subprocess.run(['git', 'add', '.'], cwd=self.local_repo_path, check=True)
            
            # Check if there are changes to commit
            result = subprocess.run(['git', 'diff', '--cached', '--exit-code'], 
                                  cwd=self.local_repo_path, capture_output=True)
            
            if result.returncode == 0:
                logging.info("No changes detected - backup is up to date")
                return True
            
            # Commit changes
            commit_message = f"Automated backup - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            logging.info(f"Committing changes: {commit_message}")
            subprocess.run(['git', 'commit', '-m', commit_message], 
                         cwd=self.local_repo_path, check=True)
            
            # Push to remote
            logging.info("Pushing to GitHub...")
            result = subprocess.run(['git', 'push', '-u', 'origin', self.backup_branch], 
                                  cwd=self.local_repo_path, 
                                  capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                logging.info("[SUCCESS] Backup completed successfully!")
                logging.info(f"Repository: {self.repo_url}")
                return True
            else:
                logging.error(f"Push failed: {result.stderr}")
                return False
            
        except subprocess.TimeoutExpired:
            logging.error("[TIMEOUT] Backup timed out - network issues?")
            return False
        except Exception as e:
            logging.error(f"[ERROR] Backup failed: {e}")
            return False

    def schedule_auto_backup(self):
        """Schedule automatic daily backup at midnight"""
        logging.info("[SCHEDULE] Scheduling automatic backup at midnight...")
        schedule.every().day.at("00:00").do(self.run_scheduled_backup)
        
        logging.info("[SCHEDULE] Backup scheduler started. Press Ctrl+C to stop.")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logging.info("[STOP] Backup scheduler stopped by user")

    def run_scheduled_backup(self):
        """Run backup as scheduled job"""
        logging.info("[SCHEDULE] Scheduled backup triggered")
        success = self.perform_backup()
        
        if success:
            logging.info("[SUCCESS] Scheduled backup completed successfully")
        else:
            logging.error("[ERROR] Scheduled backup failed")
        
        return success

    def manual_backup(self):
        """Run manual backup immediately"""
        logging.info("[MANUAL] Manual backup triggered")
        success = self.perform_backup()
        
        if success:
            print("[SUCCESS] Manual backup completed successfully!")
            print(f"[REPO] Repository: {self.repo_url}")
        else:
            print("[ERROR] Manual backup failed - check logs for details")
        
        return success

def main():
    """Main function with command line interface"""
    backup_system = GitHubBackupSystem()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "schedule":
            backup_system.schedule_auto_backup()
        elif command == "backup":
            backup_system.manual_backup()
        else:
            print("Usage: python backup_system.py [schedule|backup]")
            print("  schedule - Start automatic midnight backup scheduler")
            print("  backup   - Run backup immediately")
    else:
        # Interactive mode
        print("="*60)
        print("      GITHUB BACKUP SYSTEM")
        print("="*60)
        print(f"Repository: {backup_system.repo_url}")
        print("="*60)
        print("1. Run backup now")
        print("2. Start automatic scheduler (midnight daily)")
        print("3. Exit")
        print("="*60)
        
        while True:
            try:
                choice = input("\nSelect option (1-3): ").strip()
                
                if choice == "1":
                    backup_system.manual_backup()
                    input("Press Enter to continue...")
                elif choice == "2":
                    backup_system.schedule_auto_backup()
                    break
                elif choice == "3":
                    print("Goodbye!")
                    break
                else:
                    print("Invalid choice. Please select 1-3.")
                    
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break

if __name__ == "__main__":
    main()
