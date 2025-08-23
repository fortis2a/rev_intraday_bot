#!/usr/bin/env python3
"""
Test script to automatically test launcher.py option 5 then option 1
"""

import subprocess
import sys
import os
import time
from io import StringIO


def test_launcher_sequence():
    """Test the specific sequence: option 5 then option 1"""

    print("Testing launcher.py sequence: option 5 -> option 1")
    print("=" * 60)

    # Prepare the input sequence
    input_sequence = "5\n1\n"  # Option 5, then option 1

    try:
        # Start the launcher process
        venv_python = r"C:/Users/will7/OneDrive - Sygma Data Analytics/Stock Trading/Scalping Bot System/.venv/Scripts/python.exe"
        launcher_path = "launcher.py"

        print(f"Starting launcher: {venv_python} {launcher_path}")
        print(f"Input sequence: option 5 -> option 1")
        print("=" * 60)

        # Run the launcher with input
        process = subprocess.Popen(
            [venv_python, launcher_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True,
        )

        # Send the input sequence and wait a bit
        stdout, stderr = process.communicate(input=input_sequence, timeout=30)

        print("STDOUT:")
        print(stdout)
        print("\nSTDERR:")
        print(stderr)
        print(f"\nReturn code: {process.returncode}")

    except subprocess.TimeoutExpired:
        print("Process timed out - launcher may be running in background")
        process.kill()
        stdout, stderr = process.communicate()
        print("STDOUT:")
        print(stdout)
        print("\nSTDERR:")
        print(stderr)

    except Exception as e:
        print(f"Error running launcher: {e}")


if __name__ == "__main__":
    test_launcher_sequence()
