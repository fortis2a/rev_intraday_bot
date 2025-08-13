#!/usr/bin/env python3
"""
🔄 Automatic GitHub Backup Script
Automatically backs up the trading system to GitHub with timestamps
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

def run_git_command(command, description=""):
    """Run a git command and return success status"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            if description:
                print(f"✅ {description}")
            return True, result.stdout
        else:
            print(f"❌ Failed: {description}")
            print(f"Error: {result.stderr}")
            return False, result.stderr
            
    except Exception as e:
        print(f"❌ Exception during {description}: {e}")
        return False, str(e)

def backup_to_github():
    """Backup current state to GitHub"""
    print("🔄 Starting automatic backup to GitHub...")
    print("=" * 50)
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Check if we're in a git repository
    success, output = run_git_command("git status", "Checking git status")
    if not success:
        print("❌ Not in a git repository or git not available")
        return False
    
    # Add all changes
    success, _ = run_git_command("git add .", "Adding files to staging")
    if not success:
        return False
    
    # Check if there are changes to commit
    success, status_output = run_git_command("git status --porcelain", "Checking for changes")
    
    if not status_output.strip():
        print("ℹ️ No changes to backup")
        return True
    
    # Create commit message
    commit_message = f"Automatic backup: {timestamp}"
    commit_cmd = f'git commit -m "{commit_message}"'
    
    success, _ = run_git_command(commit_cmd, "Creating commit")
    if not success:
        return False
    
    # Push to GitHub
    success, _ = run_git_command("git push origin main", "Pushing to GitHub")
    if not success:
        print("⚠️ Push failed. Repository might not be set up on GitHub yet.")
        print("Run 'python setup_github.py' to set up the repository.")
        return False
    
    print(f"✅ Backup completed successfully at {timestamp}")
    return True

def setup_daily_backup():
    """Setup instructions for daily automatic backup"""
    print("\n🕐 Setting up daily automatic backup...")
    print("-" * 40)
    
    script_path = Path(__file__).absolute()
    
    print("To set up automatic daily backups, you can:")
    print()
    print("1. 🪟 Windows Task Scheduler:")
    print(f"   Create a task that runs: python {script_path}")
    print("   Schedule: Daily at a convenient time (e.g., end of trading day)")
    print()
    print("2. 🐧 Linux/Mac Cron Job:")
    print("   Add to crontab: 0 17 * * 1-5 python", str(script_path))
    print("   (Runs Monday-Friday at 5 PM)")
    print()
    print("3. 🔧 Manual backup anytime:")
    print(f"   Run: python {script_path}")
    print()

def main():
    """Main backup function"""
    if len(sys.argv) > 1 and sys.argv[1] == "--setup":
        setup_daily_backup()
        return
    
    print("💾 Intraday Trading Bot - GitHub Backup")
    print("=" * 40)
    
    # Perform backup
    success = backup_to_github()
    
    if success:
        print("\n🎉 Backup completed successfully!")
        print("Your trading system is safely backed up to GitHub.")
    else:
        print("\n❌ Backup failed!")
        print("Check the errors above and try again.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
