#!/usr/bin/env python3
"""
CI/CD Helper Script - Local Testing
Run the same checks that CI/CD will run, locally before pushing
"""

import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"\n🔍 {description}")
    print(f"Command: {cmd}")
    print("-" * 50)
    
    result = subprocess.run(cmd, shell=True, capture_output=False)
    success = result.returncode == 0
    
    if success:
        print(f"✅ {description} - PASSED")
    else:
        print(f"❌ {description} - FAILED")
    
    return success

def main():
    """Run all CI/CD checks locally"""
    print("🚀 Running CI/CD checks locally...")
    print("This will run the same checks that GitHub Actions will run")
    
    # Change to project root
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    checks = [
        ("black --check --diff .", "Code formatting check"),
        ("isort --check-only --diff .", "Import sorting check"), 
        ("flake8 .", "Code linting"),
        ("pytest tests/ -m 'unit or not integration' -v", "Unit tests"),
        ("pytest tests/ -m integration -v", "Integration tests"),
        ("safety check -r requirements.txt", "Security vulnerability check"),
        ("bandit -r . -x tests/,archive/,backup_*/ -ll", "Security linting"),
    ]
    
    passed = 0
    total = len(checks)
    
    for cmd, description in checks:
        if run_command(cmd, description):
            passed += 1
        print()
    
    print("=" * 70)
    print(f"📊 SUMMARY: {passed}/{total} checks passed")
    
    if passed == total:
        print("✅ All checks passed! Ready to push to GitHub")
        return 0
    else:
        print("❌ Some checks failed. Fix issues before pushing")
        print("\nQuick fixes:")
        print("- Run 'black .' to auto-format code")
        print("- Run 'isort .' to fix import sorting")
        print("- Check test failures and fix code")
        return 1

if __name__ == "__main__":
    import os
    sys.exit(main())
