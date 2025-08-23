#!/usr/bin/env python3
"""
Clean Trading Bot Starter
Ensures only the improved intraday engine runs
"""

import subprocess
import sys
import os
from pathlib import Path


def kill_existing_processes():
    """Kill any existing Python trading processes"""
    try:
        # Kill all Python processes (Windows)
        subprocess.run(["taskkill", "/f", "/im", "python.exe"], capture_output=True)
        print("[CLEANUP] Stopped all existing Python processes")
    except Exception as e:
        print(f"[CLEANUP] Note: {e}")


def start_intraday_engine():
    """Start only the improved intraday engine"""
    print("=" * 60)
    print("         STARTING IMPROVED INTRADAY ENGINE")
    print("=" * 60)
    print("[INFO] Old scalping engine removed")
    print("[INFO] Using main.py with IntradayEngine only")
    print("[INFO] Fixed momentum strategy - no wrong direction signals")
    print("[INFO] Enhanced confidence filtering ≥75%")
    print("=" * 60)

    # Get the Python executable from the virtual environment
    venv_python = Path(__file__).parent / ".venv" / "Scripts" / "python.exe"
    if venv_python.exists():
        python_cmd = str(venv_python)
    else:
        python_cmd = "python"

    try:
        # Start the main intraday engine
        cmd = [python_cmd, "main.py", "--mode", "LIVE"]
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n[STOP] Trading engine stopped by user")
    except Exception as e:
        print(f"[ERROR] Failed to start intraday engine: {e}")


if __name__ == "__main__":
    print("[START] Initializing clean trading environment...")
    kill_existing_processes()
    start_intraday_engine()
