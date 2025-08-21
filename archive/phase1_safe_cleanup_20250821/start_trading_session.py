#!/usr/bin/env python3
"""
Start Trading Session via Launcher
"""

import subprocess
import sys
from pathlib import Path

# Use the virtual environment python
venv_python = Path(__file__).parent / '.venv' / 'Scripts' / 'python.exe'
python_cmd = str(venv_python) if venv_python.exists() else 'python'

print("="*60)
print("      STARTING TRADING SESSION VIA LAUNCHER")
print("="*60)
print("✅ Using fixed main.py with trading hour restrictions")
print("✅ Trading hours: 10:00 AM - 3:30 PM")
print("✅ Current time: 9:54 AM (trading starts in 6 minutes)")
print("="*60)

# Start the main trading engine directly via launcher
cmd = [python_cmd, 'main.py', '--mode', 'LIVE']

try:
    print("[START] Starting trading engine...")
    subprocess.run(cmd)
except KeyboardInterrupt:
    print("\n[STOP] Trading stopped by user")
except Exception as e:
    print(f"[ERROR] Failed to start: {e}")
