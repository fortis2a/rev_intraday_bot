#!/usr/bin/env python3
"""
🔧 GitHub Repository Setup Helper
Helps create and configure the GitHub repository for the intraday trading bot
"""

import subprocess
import sys
import webbrowser
from pathlib import Path

def create_github_repo_instructions():
    """Show instructions for creating the GitHub repository"""
    
    print("🚀 GitHub Repository Setup Instructions")
    print("=" * 50)
    print()
    print("Follow these steps to create your repository:")
    print()
    print("1. 🌐 Go to GitHub and create a new repository:")
    print("   URL: https://github.com/new")
    print()
    print("2. 📝 Repository Settings:")
    print("   - Repository name: intraday-trading-bot")
    print("   - Description: Intelligent intraday trading system with orchestrator")
    print("   - Make it Private (recommended for trading systems)")
    print("   - DON'T initialize with README, .gitignore, or license (we have them)")
    print()
    print("3. ✅ After creating the repository, run:")
    print("   git push -u origin main")
    print()
    print("4. 🔄 To enable automatic daily backups, run:")
    print("   python setup_backup.py")
    print()
    
    # Ask if user wants to open GitHub
    choice = input("Do you want to open GitHub.com/new in your browser? (y/N): ")
    if choice.lower() == 'y':
        webbrowser.open('https://github.com/new')
        print("✅ GitHub opened in browser")
    
    return True

def check_git_status():
    """Check current git status"""
    print("\n📊 Current Git Status:")
    print("-" * 30)
    
    try:
        # Check if we're in a git repository
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            if result.stdout.strip():
                print("⚠️ Uncommitted changes found:")
                print(result.stdout)
            else:
                print("✅ Working directory clean")
        
        # Check remote
        result = subprocess.run(['git', 'remote', '-v'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            if result.stdout.strip():
                print("\n📡 Remote repositories:")
                print(result.stdout)
            else:
                print("\n❌ No remote repositories configured")
        
        # Check branch
        result = subprocess.run(['git', 'branch', '--show-current'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            branch = result.stdout.strip()
            print(f"\n🌳 Current branch: {branch}")
            
        # Check commits
        result = subprocess.run(['git', 'log', '--oneline', '-n', '5'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("\n📝 Recent commits:")
            print(result.stdout)
        
    except FileNotFoundError:
        print("❌ Git not found. Please install Git first.")
        return False
    
    return True

def prepare_for_push():
    """Prepare repository for pushing to GitHub"""
    print("\n🔧 Preparing repository for GitHub...")
    
    try:
        # Add any new files
        result = subprocess.run(['git', 'add', '.'], capture_output=True)
        if result.returncode != 0:
            print("❌ Failed to add files to git")
            return False
        
        # Check if there are changes to commit
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        
        if result.stdout.strip():
            # Commit changes
            commit_msg = "Update: Added GitHub setup and requirements"
            result = subprocess.run(['git', 'commit', '-m', commit_msg], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Changes committed successfully")
            else:
                print(f"⚠️ Commit failed: {result.stderr}")
        else:
            print("ℹ️ No changes to commit")
        
        print("\n🚀 Repository is ready for GitHub!")
        print("Next steps:")
        print("1. Create the repository on GitHub (as shown above)")
        print("2. Run: git push -u origin main")
        
        return True
        
    except Exception as e:
        print(f"❌ Error preparing repository: {e}")
        return False

def main():
    """Main setup function"""
    print("🎯 Intraday Trading Bot - GitHub Setup")
    print("=" * 40)
    
    # Check git status
    if not check_git_status():
        return
    
    # Show repository creation instructions
    create_github_repo_instructions()
    
    # Prepare for push
    prepare_for_push()
    
    print("\n" + "=" * 50)
    print("✅ Setup complete!")
    print("Remember to keep your repository private to protect your trading system.")
    print("=" * 50)

if __name__ == "__main__":
    main()
