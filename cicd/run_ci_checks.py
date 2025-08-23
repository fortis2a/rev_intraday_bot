#!/usr/bin/env python3
"""
CI/CD Helper Script - Local Testing
Run the same checks that CI/CD will run, locally before pushing
"""

import subprocess
import sys
from pathlib import Path


import subprocess
import sys
import os
from pathlib import Path


def get_python_cmd():
    """Get the correct Python command for this environment"""
    # Check if we're in a virtual environment
    venv_python = Path(__file__).parent.parent / ".venv" / "Scripts" / "python.exe"
    if venv_python.exists():
        return f'& "{venv_python}"'
    return "python"


def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"\n🔍 {description}")
    print(f"Command: {cmd}")
    print("-" * 50)

    # Use PowerShell execution for commands with &
    if cmd.startswith("& "):
        result = subprocess.run(["powershell", "-Command", cmd], capture_output=False)
    else:
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

    # Change to project root (parent of cicd folder)
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    # Get the correct Python command
    python_cmd = get_python_cmd()

    checks = [
        (f"{python_cmd} -m black --check --diff .", "Code formatting check"),
        (f"{python_cmd} -m isort --check-only --diff .", "Import sorting check"),
        (f"{python_cmd} -m flake8 .", "Code linting"),
        (
            f"{python_cmd} -m pytest tests/ -m 'unit or not integration' -v",
            "Unit tests",
        ),
        (f"{python_cmd} -m pytest tests/ -m integration -v", "Integration tests"),
        (
            f"{python_cmd} -m safety check -r requirements.txt",
            "Security vulnerability check",
        ),
        (
            f"{python_cmd} -m bandit -r . -x tests/,archive/,backup_*/ -ll",
            "Security linting",
        ),
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
