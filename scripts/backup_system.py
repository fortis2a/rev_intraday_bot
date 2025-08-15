#!/usr/bin/env python3
"""
GitHub Backup System with Automatic Scheduling
Handles manual and scheduled backups to GitHub repository.
Schedule: Daily at 10:00 PM (22:00)
"""

import os
import sys
import subprocess
import schedule
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path for imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

from utils.logger import setup_logger

class GitHubBackupSystem:
    def __init__(self):
        self.logger = setup_logger('backup_system')
        self.repo_url = "https://github.com/fortis2a/rev_intraday_bot.git"
        self.project_root = parent_dir
        
        # Files to exclude from backup
        self.exclude_patterns = [
            '.env',
            '*.log',
            '__pycache__/',
            '*.pyc',
            'logs/',
            'data/*.csv',
            'data/*.json',
            '.git/',
            'reports/',
            '*.png',
            '*.pdf'
        ]
        
    def run_git_command(self, command, cwd=None):
        """Execute git command and return result"""
        try:
            if cwd is None:
                cwd = self.project_root
                
            result = subprocess.run(
                command, 
                shell=True, 
                cwd=cwd,
                capture_output=True, 
                text=True, 
                timeout=60
            )
            
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            self.logger.error("Git command timed out")
            return False, "", "Command timed out"
        except Exception as e:
            self.logger.error(f"Git command failed: {e}")
            return False, "", str(e)
    
    def setup_gitignore(self):
        """Create or update .gitignore file"""
        gitignore_path = self.project_root / '.gitignore'
        
        gitignore_content = """
# Environment variables
.env
*.env

# Logs
*.log
logs/
reports/

# Python cache
__pycache__/
*.py[cod]
*$py.class

# Data files (generated)
data/*.csv
data/*.json
data/trades_*.json
data/positions_*.json

# Output files
*.png
*.pdf
reports/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
"""
        
        try:
            with open(gitignore_path, 'w') as f:
                f.write(gitignore_content.strip())
            self.logger.info("✅ .gitignore file updated")
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to create .gitignore: {e}")
            return False
    
    def initialize_git_repo(self):
        """Initialize git repository if not exists"""
        git_dir = self.project_root / '.git'
        
        if not git_dir.exists():
            self.logger.info("🔧 Initializing Git repository...")
            success, stdout, stderr = self.run_git_command("git init")
            if not success:
                self.logger.error(f"❌ Failed to initialize Git: {stderr}")
                return False
                
            # Set remote origin
            success, stdout, stderr = self.run_git_command(f"git remote add origin {self.repo_url}")
            if not success and "already exists" not in stderr:
                self.logger.error(f"❌ Failed to add remote: {stderr}")
                return False
                
            self.logger.info("✅ Git repository initialized")
        
        return True
    
    def perform_backup(self):
        """Perform the actual backup to GitHub"""
        try:
            self.logger.info("🚀 Starting GitHub backup process...")
            
            # Setup gitignore
            if not self.setup_gitignore():
                return False
            
            # Initialize git if needed
            if not self.initialize_git_repo():
                return False
            
            # Configure git user (if not set)
            self.run_git_command("git config user.name 'Scalping Bot System'")
            self.run_git_command("git config user.email 'scalping.bot@example.com'")
            
            # Add all files (respecting .gitignore)
            success, stdout, stderr = self.run_git_command("git add .")
            if not success:
                self.logger.error(f"❌ Failed to add files: {stderr}")
                return False
            
            # Check if there are changes to commit
            success, stdout, stderr = self.run_git_command("git status --porcelain")
            if not success:
                self.logger.error(f"❌ Failed to check status: {stderr}")
                return False
            
            if not stdout.strip():
                self.logger.info("ℹ️  No changes to backup")
                return True
            
            # Commit changes
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            commit_message = f"Auto backup: {timestamp}"
            
            success, stdout, stderr = self.run_git_command(f'git commit -m "{commit_message}"')
            if not success:
                self.logger.error(f"❌ Failed to commit: {stderr}")
                return False
            
            # Push to GitHub
            success, stdout, stderr = self.run_git_command("git push -u origin main")
            if not success:
                # Try master branch if main fails
                success, stdout, stderr = self.run_git_command("git push -u origin master")
                if not success:
                    self.logger.error(f"❌ Failed to push: {stderr}")
                    return False
            
            self.logger.info("✅ GitHub backup completed successfully!")
            self.logger.info(f"📦 Repository: {self.repo_url}")
            
            # Print summary
            success, stdout, stderr = self.run_git_command("git log --oneline -5")
            if success:
                print("\n📝 Recent commits:")
                for line in stdout.strip().split('\n'):
                    if line.strip():
                        print(f"   • {line}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Backup failed: {e}")
            return False
    
    def backup_job(self):
        """Scheduled backup job"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.logger.info(f"🕙 Scheduled backup started at {current_time}")
        
        success = self.perform_backup()
        
        if success:
            print(f"\n✅ [{current_time}] GitHub backup completed successfully!")
            self.logger.info("✅ Scheduled backup completed successfully")
        else:
            print(f"\n❌ [{current_time}] GitHub backup failed!")
            self.logger.error("❌ Scheduled backup failed")
    
    def start_scheduler(self):
        """Start the backup scheduler (Daily at 10:00 PM)"""
        self.logger.info("⏰ Starting backup scheduler...")
        self.logger.info("📅 Schedule: Daily at 10:00 PM (22:00)")
        
        # Schedule backup at 10:00 PM (22:00) daily
        schedule.every().day.at("22:00").do(self.backup_job)
        
        print("\n" + "="*70)
        print("🔄 GITHUB BACKUP SCHEDULER ACTIVE")
        print("="*70)
        print("📅 Schedule: Daily at 10:00 PM (22:00)")
        print(f"📦 Repository: {self.repo_url}")
        print("⏹️  Press Ctrl+C to stop the scheduler")
        print("="*70)
        
        # Show next scheduled run
        next_run = schedule.next_run()
        if next_run:
            print(f"⏰ Next backup: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            self.logger.info("🛑 Backup scheduler stopped by user")
            print("\n🛑 Backup scheduler stopped")

def main():
    if len(sys.argv) < 2:
        print("Usage: python backup_system.py [backup|schedule]")
        sys.exit(1)
    
    backup_system = GitHubBackupSystem()
    
    if sys.argv[1] == 'backup':
        # Manual backup
        success = backup_system.perform_backup()
        sys.exit(0 if success else 1)
    
    elif sys.argv[1] == 'schedule':
        # Start scheduler
        backup_system.start_scheduler()
    
    else:
        print("Invalid command. Use 'backup' or 'schedule'")
        sys.exit(1)

if __name__ == "__main__":
    main()
