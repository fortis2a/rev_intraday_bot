#!/usr/bin/env python3
"""
Quick test script to verify option 6 works
"""
import subprocess
import sys
import time
import os

def test_option6():
    """Test launcher option 6"""
    print("Testing launcher option 6...")
    
    # Create a script that will automatically select option 6
    script_content = "6\n"
    
    try:
        # Run launcher with option 6
        proc = subprocess.Popen(
            [sys.executable, 'launcher.py'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        # Send option 6
        stdout, stderr = proc.communicate(input=script_content, timeout=30)
        
        print("=== LAUNCHER OUTPUT ===")
        print(stdout[-1000:] if stdout else "No stdout")
        
        if stderr:
            print("=== LAUNCHER ERRORS ===")
            print(stderr[-500:])
            
        print(f"Launcher exit code: {proc.returncode}")
        
        # Now check if the bot actually started and is running
        print("\nChecking if trading bot is running...")
        time.sleep(3)
        
        # Look for log files to see if bot started
        log_files = [f for f in os.listdir('logs') if 'intraday_engine' in f]
        if log_files:
            latest_log = max(log_files, key=lambda x: os.path.getmtime(os.path.join('logs', x)))
            print(f"Latest log file: {latest_log}")
            
            # Check last modification time
            log_path = os.path.join('logs', latest_log)
            mtime = os.path.getmtime(log_path)
            current_time = time.time()
            age_seconds = current_time - mtime
            
            if age_seconds < 60:  # Modified within last minute
                print(f"✅ Log file recently updated ({age_seconds:.1f}s ago) - bot appears to be running!")
                return True
            else:
                print(f"❌ Log file is old ({age_seconds:.1f}s ago) - bot may not be running")
                return False
        else:
            print("❌ No intraday_engine log files found")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Launcher timed out after 30 seconds")
        proc.kill()
        return False
    except Exception as e:
        print(f"❌ Error testing option 6: {e}")
        return False

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    success = test_option6()
    print(f"\nOption 6 test result: {'SUCCESS' if success else 'FAILED'}")
