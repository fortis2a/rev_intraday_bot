#!/usr/bin/env python3
"""
🚀 Quick Stock Monitor Setup
Easy launcher for stock performance monitoring and analysis
"""

import sys
import subprocess
from pathlib import Path

def main():
    """Main launcher with options"""
    print("📊 STOCK PERFORMANCE MONITORING SYSTEM")
    print("=" * 50)
    print("🎯 Monitoring: IONQ, PG, QBTS, RGTI, JNJ")
    print("=" * 50)
    print()
    print("Choose monitoring option:")
    print("1. 📈 One-time comprehensive analysis")
    print("2. 🔄 Continuous monitoring (30 min intervals)")
    print("3. 📺 Live dashboard (60 second updates)")
    print("4. 📊 Detailed analysis with recommendations")
    print("5. 🎯 Quick performance check")
    print("0. ❌ Exit")
    print()
    
    choice = input("Enter your choice (0-5): ").strip()
    
    if choice == "1":
        print("\n🚀 Running comprehensive analysis...")
        subprocess.run([sys.executable, "stock_performance_monitor.py"])
        
    elif choice == "2":
        print("\n🔄 Starting continuous monitoring...")
        subprocess.run([sys.executable, "stock_performance_monitor.py", "--continuous"])
        
    elif choice == "3":
        print("\n📺 Starting live dashboard...")
        subprocess.run([sys.executable, "live_stock_dashboard.py"])
        
    elif choice == "4":
        print("\n📊 Running detailed analysis...")
        subprocess.run([sys.executable, "live_stock_dashboard.py", "--detailed"])
        
    elif choice == "5":
        print("\n🎯 Quick performance check...")
        subprocess.run([sys.executable, "live_stock_dashboard.py", "--interval", "10"])
        
    elif choice == "0":
        print("👋 Goodbye!")
        
    else:
        print("❌ Invalid choice. Please try again.")
        main()

if __name__ == "__main__":
    main()
