#!/usr/bin/env python3
"""
Test main.py directly without launcher to see if it runs continuously
"""

import subprocess
import time

def test_main_directly():
    """Test running main.py directly"""
    print("Testing main.py directly...")
    
    try:
        # Run main.py directly with LIVE mode
        cmd = [r"C:\Users\will7\OneDrive - Sygma Data Analytics\Stock Trading\Scalping Bot System\.venv\Scripts\python.exe", 
               "main.py", "--mode", "LIVE"]
        
        print(f"Running command: {' '.join(cmd)}")
        
        # Start the process
        process = subprocess.Popen(cmd, 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE,
                                   text=True,
                                   cwd=r"C:\Users\will7\OneDrive - Sygma Data Analytics\Stock Trading\Scalping Bot System")
        
        print(f"Process started with PID: {process.pid}")
        
        # Monitor for 3 minutes
        start_time = time.time()
        while time.time() - start_time < 180:  # 3 minutes
            # Check if process is still running
            if process.poll() is not None:
                print(f"Process exited with code: {process.returncode}")
                stdout, stderr = process.communicate()
                print(f"STDOUT: {stdout}")
                print(f"STDERR: {stderr}")
                break
            
            print(f"Process still running... ({time.time() - start_time:.1f}s)")
            time.sleep(10)
        else:
            print("Process ran for 3 minutes - terminating test")
            process.terminate()
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_main_directly()
