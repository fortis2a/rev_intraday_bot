#!/usr/bin/env python3
"""
Test subprocess environment to identify launcher issues
"""

import subprocess
import sys
import time

def test_subprocess():
    """Test main.py running as subprocess like launcher does"""
    print("[TEST] Starting main.py as subprocess...")
    
    # Use the same subprocess call as the launcher
    cmd = [sys.executable, 'main.py']
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True
    )
    
    print(f"[TEST] Process started with PID: {process.pid}")
    
    # Monitor output for 60 seconds
    start_time = time.time()
    output_lines = []
    
    try:
        while time.time() - start_time < 60:  # Monitor for 1 minute
            # Check if process is still running
            poll_result = process.poll()
            if poll_result is not None:
                print(f"[TEST] Process exited with code: {poll_result}")
                break
                
            # Read output if available
            try:
                line = process.stdout.readline()
                if line:
                    output_lines.append(line.strip())
                    print(f"[OUTPUT] {line.strip()}")
                    
                    # Check for key milestones
                    if "Trading Cycle" in line:
                        print("[MILESTONE] ✅ Reached trading cycle!")
                    elif "[INIT]" in line:
                        print("[MILESTONE] 🔄 Engine initializing...")
                    elif "[FINAL]" in line:
                        print("[MILESTONE] ❌ Engine stopping!")
                        
            except:
                pass
                
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("[TEST] Manual stop")
        
    finally:
        # Clean up
        if process.poll() is None:
            print("[TEST] Terminating process...")
            process.terminate()
            process.wait(timeout=5)
        
        print(f"[TEST] Total output lines: {len(output_lines)}")
        
        # Show last few lines
        if output_lines:
            print("[TEST] Last few lines of output:")
            for line in output_lines[-5:]:
                print(f"  {line}")

if __name__ == "__main__":
    test_subprocess()
