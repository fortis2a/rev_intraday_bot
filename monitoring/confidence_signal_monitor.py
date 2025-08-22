#!/usr/bin/env python3
"""
CONFIDENCE SIGNAL FLOW MONITOR
==============================

Tracks the complete signal flow from confidence monitor to order execution.
Identifies where signals are getting lost in the pipeline.
"""

import os
import time
import subprocess
from datetime import datetime

def get_latest_log_content(log_file, lines=50):
    """Get latest content from log file"""
    try:
        result = subprocess.run([
            "powershell", "-Command", 
            f"Get-Content 'logs\\{log_file}' -Tail {lines} 2>$null"
        ], capture_output=True, text=True, timeout=3)
        
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip().split('\n')
        return []
    except:
        return []

def count_signals_in_timeframe(lines, keywords, timeframe_hours=["10:", "11:", "12:", "13:", "14:", "15:"]):
    """Count signals in recent timeframe"""
    count = 0
    for line in lines:
        if any(hour in line for hour in timeframe_hours):
            if any(keyword.upper() in line.upper() for keyword in keywords):
                count += 1
    return count

def get_recent_entries(lines, max_entries=5):
    """Get recent entries from today"""
    recent = []
    for line in lines:
        if any(hour in line for hour in ["10:", "11:", "12:", "13:", "14:", "15:"]):
            recent.append(line.strip())
    return recent[-max_entries:]

def main():
    print("🧠 CONFIDENCE SIGNAL FLOW MONITOR")
    print("="*70)
    print("🎯 Tracking: CONFIDENCE → ENGINE → ORDERS → EXECUTION")
    print("="*70)
    
    today = datetime.now().strftime("%Y%m%d")
    
    while True:
        print(f"\n⏰ {datetime.now().strftime('%H:%M:%S')} - Signal Flow Analysis")
        print("-" * 70)
        
        # 1. CONFIDENCE MONITOR - Signal Generation
        conf_logs = get_latest_log_content(f"intraday_confidence_monitor_{today}.log", 100)
        print("🧠 CONFIDENCE MONITOR (Signal Source):")
        
        if conf_logs:
            recent_conf = get_recent_entries(conf_logs, 5)
            signal_count = count_signals_in_timeframe(conf_logs, ["signal", "buy", "sell", "confidence"])
            
            for line in recent_conf:
                if "SIGNAL" in line.upper() or "BUY" in line.upper() or "SELL" in line.upper():
                    print(f"   ⚡ {line}")
                elif "CONFIDENCE" in line.upper():
                    print(f"   📊 {line}")
                else:
                    print(f"   📋 {line}")
            
            print(f"   📈 Signals generated today: {signal_count}")
        else:
            print("   ❌ No confidence monitor log found")
            print("   💡 Check if confidence monitor is running")
        
        # 2. REAL-TIME CONFIDENCE - Live Signal Processing
        rt_conf_logs = get_latest_log_content(f"intraday_real_time_confidence_{today}.log", 100)
        print("\n⚡ REAL-TIME CONFIDENCE (Signal Processing):")
        
        if rt_conf_logs:
            recent_rt = get_recent_entries(rt_conf_logs, 4)
            rt_signal_count = count_signals_in_timeframe(rt_conf_logs, ["signal", "generated", "confidence"])
            
            for line in recent_rt:
                if "SIGNAL" in line.upper():
                    print(f"   🎯 {line}")
                elif "CONFIDENCE" in line.upper():
                    print(f"   📈 {line}")
                else:
                    print(f"   📊 {line}")
            
            print(f"   📊 Real-time signals: {rt_signal_count}")
        else:
            print("   ⚠️ No real-time confidence log found")
        
        # 3. INTRADAY ENGINE - Signal Reception & Processing
        engine_logs = get_latest_log_content(f"intraday_intraday_engine_{today}.log", 100)
        print("\n🔄 INTRADAY ENGINE (Signal Reception):")
        
        if engine_logs:
            recent_engine = get_recent_entries(engine_logs, 4)
            engine_signal_count = count_signals_in_timeframe(engine_logs, ["signal", "cycle", "scanning"])
            
            for line in recent_engine:
                if "SIGNAL" in line.upper():
                    print(f"   ⚡ {line}")
                elif "CYCLE" in line.upper():
                    print(f"   🔄 {line}")
                elif "SCANNING" in line.upper():
                    print(f"   🔍 {line}")
                else:
                    print(f"   📊 {line}")
            
            print(f"   🔄 Engine signal events: {engine_signal_count}")
        else:
            print("   ❌ No engine log found")
        
        # 4. ORDER MANAGER - Trade Execution
        order_logs = get_latest_log_content(f"intraday_order_manager_{today}.log", 100)
        print("\n💰 ORDER MANAGER (Trade Execution):")
        
        if order_logs:
            recent_orders = get_recent_entries(order_logs, 4)
            order_count = count_signals_in_timeframe(order_logs, ["buy", "sell", "order", "execution"])
            
            for line in recent_orders:
                if "BUY" in line.upper() or "SELL" in line.upper():
                    print(f"   🚀 {line}")
                elif "ORDER" in line.upper():
                    print(f"   📋 {line}")
                else:
                    print(f"   💼 {line}")
            
            print(f"   💰 Orders placed: {order_count}")
        else:
            print("   ❌ No order manager log found")
        
        # 5. SIGNAL FLOW ANALYSIS
        print("\n🔗 SIGNAL FLOW HEALTH CHECK:")
        
        if conf_logs:
            conf_signals = count_signals_in_timeframe(conf_logs, ["signal", "buy", "sell"])
            engine_signals = count_signals_in_timeframe(engine_logs, ["signal"]) if engine_logs else 0
            orders_placed = count_signals_in_timeframe(order_logs, ["buy", "sell"]) if order_logs else 0
            
            print(f"   1️⃣ Confidence Signals: {conf_signals}")
            print(f"   2️⃣ Engine Received: {engine_signals}")
            print(f"   3️⃣ Orders Placed: {orders_placed}")
            
            # Diagnose issues
            if conf_signals > 0 and engine_signals == 0:
                print("   ⚠️ ISSUE: Signals not reaching engine - Check signal routing!")
            elif engine_signals > 0 and orders_placed == 0:
                print("   ⚠️ ISSUE: Engine receiving signals but not placing orders!")
            elif conf_signals == 0:
                print("   ℹ️ No signals generated (normal in low-volatility periods)")
            elif conf_signals == orders_placed:
                print("   ✅ Perfect signal flow - All signals converted to orders!")
            else:
                print(f"   📊 Signal conversion rate: {(orders_placed/conf_signals*100):.1f}%")
        
        # 6. CURRENT BOT STATUS
        launcher_logs = get_latest_log_content(f"intraday_trading_launcher_{today}.log", 5)
        if launcher_logs:
            print(f"\n🤖 BOT STATUS: {launcher_logs[-1] if launcher_logs else 'Unknown'}")
        
        print("\n" + "="*70)
        print("🔍 Next update in 5 seconds | Press Ctrl+C to stop")
        time.sleep(5)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Signal flow monitoring stopped")
