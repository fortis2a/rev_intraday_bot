#!/usr/bin/env python3
"""
Dashboard Launcher - Main entry point for Interactive Trading Dashboard
================================================================

This script launches the interactive trading dashboard from its organized location.
Use this as the main entry point instead of navigating to the dashboard folder.

Usage:
    python launch_dashboard.py

Features:
    - Starts interactive dashboard on http://localhost:8050
    - Real-time trading analytics
    - Dark theme with professional UI
    - Calendar date picker for filtering
    - Comprehensive charts and metrics

Author: GitHub Copilot
Date: August 19, 2025
"""

import os
import sys
import subprocess

def main():
    """Launch the interactive trading dashboard"""
    
    # Get the current script directory (monitoring folder) and then parent (root of project)
    monitoring_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(monitoring_dir)
    
    # Path to the dashboard script (in monitoring directory)
    dashboard_path = os.path.join(monitoring_dir, 'live_dashboard.py')
    
    # Check if dashboard exists
    if not os.path.exists(dashboard_path):
        print("❌ Error: Dashboard not found at expected location")
        print(f"Expected: {dashboard_path}")
        return 1
    
    # Get the virtual environment python path
    venv_python = os.path.join(project_root, '.venv', 'Scripts', 'python.exe')
    
    if not os.path.exists(venv_python):
        print("❌ Error: Virtual environment not found")
        print(f"Expected: {venv_python}")
        print("Please run: python -m venv .venv")
        return 1
    
    print("🚀 Launching Interactive Trading Dashboard...")
    print(f"📁 Dashboard Location: {dashboard_path}")
    print(f"🐍 Python Environment: {venv_python}")
    print("=" * 60)
    
    try:
        # Launch the dashboard with proper working directory
        subprocess.run([venv_python, dashboard_path], cwd=project_root, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error launching dashboard: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n⏹️  Dashboard stopped by user")
        return 0

if __name__ == "__main__":
    sys.exit(main())
