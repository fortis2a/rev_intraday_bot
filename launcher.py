#!/usr/bin/env python3
"""
🚀 Intraday Trading System Launcher/Orchestrator
Intelligent agent that manages and coordinates all trading system components
"""

import sys
import time
import threading
import subprocess
import signal
import argparse
from pathlib import Path
from datetime import datetime, timedelta
import pytz
import logging
from typing import Dict, List, Optional
import json

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from config import config, validate_config
from utils.logger import setup_logger

class TradingSystemOrchestrator:
    """Main orchestrator for the intraday trading system"""
    
    def __init__(self):
        """Initialize the trading system orchestrator"""
        self.logger = setup_logger("trading_orchestrator")
        self.processes: Dict[str, subprocess.Popen] = {}
        self.status: Dict[str, str] = {}
        self.running = False
        self.config = config
        
        # Use virtual environment Python if available
        venv_python = Path(__file__).parent / ".venv" / "Scripts" / "python.exe"
        self.python_cmd = str(venv_python) if venv_python.exists() else sys.executable
        
        # Component definitions
        self.components = {
            'main_bot': {
                'script': 'intraday_trading_bot.py',
                'description': 'Main intraday trading bot',
                'critical': True,
                'restart_on_failure': True,
                'args': []
            },
            'dashboard': {
                'script': 'intraday_trading_bot.py',
                'description': 'Trading dashboard interface',
                'critical': False,
                'restart_on_failure': False,
                'args': ['--dashboard']
            },
            'live_pnl': {
                'script': 'live_pnl_monitor.py',
                'description': 'Live P&L monitoring service',
                'critical': False,
                'restart_on_failure': True,
                'args': ['--monitor']
            },
            'demo_bot': {
                'script': 'demo.py',
                'description': 'Demo trading bot (safe mode)',
                'critical': False,
                'restart_on_failure': False,
                'args': []
            },
            'eod_report': {
                'script': 'generate_eod_report.py',
                'description': 'End-of-day report generator',
                'critical': False,
                'restart_on_failure': False,
                'args': ['--auto']
            }
        }
        
        self.logger.info("🚀 Trading System Orchestrator initialized")
        
    def validate_environment(self, bypass_market_hours: bool = False, auto_wait: bool = False) -> bool:
        """Validate trading environment before starting"""
        self.logger.info("🔍 Validating trading environment...")
        
        try:
            # Validate configuration
            validate_config()
            
            # Check market hours
            if not bypass_market_hours:
                if not self.is_market_hours():
                    if auto_wait:
                        # Automatically wait for market open
                        if not self.wait_for_market_open():
                            return False
                    else:
                        self.logger.warning("⚠️ Market is currently closed")
                        return False
            elif bypass_market_hours and not self.is_market_hours():
                self.logger.info("⚠️ Market is closed but bypassing for testing")
                
            # Check required files exist
            required_files = [
                'intraday_trading_bot.py',
                'config.py',
                'core/intraday_engine.py'
            ]
            
            for file_path in required_files:
                if not Path(file_path).exists():
                    self.logger.error(f"❌ Required file missing: {file_path}")
                    return False
                    
            # Test API connectivity
            self.logger.info("📡 Testing API connectivity...")
            test_result = subprocess.run([
                self.python_cmd, 'intraday_trading_bot.py', '--validate-only'
            ], capture_output=True, text=True, timeout=30)
            
            if test_result.returncode != 0:
                self.logger.error(f"❌ API validation failed: {test_result.stderr}")
                return False
                
            self.logger.info("✅ Environment validation passed")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Environment validation failed: {e}")
            return False
    
    def is_market_hours(self) -> bool:
        """Check if market is currently open"""
        try:
            est = pytz.timezone('US/Eastern')
            now = datetime.now(est)
            
            # Skip weekends
            if now.weekday() >= 5:  # Saturday = 5, Sunday = 6
                return False
                
            # Market hours: 9:30 AM - 4:00 PM EST
            market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
            market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
            
            return market_open <= now <= market_close
            
        except Exception as e:
            self.logger.error(f"Error checking market hours: {e}")
            return False
    
    def get_next_market_open(self) -> datetime:
        """Get the next market open time"""
        try:
            est = pytz.timezone('US/Eastern')
            now = datetime.now(est)
            
            # If it's a weekday and before 9:30 AM, market opens today
            if now.weekday() < 5 and now.hour < 9 or (now.hour == 9 and now.minute < 30):
                next_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
            else:
                # Find next weekday
                days_ahead = 1
                next_day = now + timedelta(days=days_ahead)
                
                # Skip weekends
                while next_day.weekday() >= 5:
                    days_ahead += 1
                    next_day = now + timedelta(days=days_ahead)
                
                next_open = next_day.replace(hour=9, minute=30, second=0, microsecond=0)
            
            return next_open
            
        except Exception as e:
            self.logger.error(f"Error calculating next market open: {e}")
            # Default to tomorrow 9:30 AM
            est = pytz.timezone('US/Eastern')
            tomorrow = datetime.now(est) + timedelta(days=1)
            return tomorrow.replace(hour=9, minute=30, second=0, microsecond=0)
    
    def wait_for_market_open(self):
        """Wait for market to open with countdown display"""
        if self.is_market_hours():
            return  # Market is already open
        
        est = pytz.timezone('US/Eastern')
        next_open = self.get_next_market_open()
        
        print("\n" + "="*60)
        print("🕐 MARKET IS CURRENTLY CLOSED")
        print("="*60)
        print(f"📅 Current Time: {datetime.now(est).strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"🚀 Next Market Open: {next_open.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        
        # Calculate wait time
        wait_seconds = (next_open - datetime.now(est)).total_seconds()
        
        if wait_seconds <= 0:
            return  # Market should be open now
        
        hours = int(wait_seconds // 3600)
        minutes = int((wait_seconds % 3600) // 60)
        seconds = int(wait_seconds % 60)
        
        print(f"⏱️ Time Until Open: {hours:02d}:{minutes:02d}:{seconds:02d}")
        print("="*60)
        
        # Ask user if they want to wait
        if wait_seconds > 300:  # More than 5 minutes
            print("\n🤔 Options:")
            print("1. Wait for market open (automatic)")
            print("2. Exit and return later")
            print("3. Continue in test mode (bypass market hours)")
            
            choice = input("\nEnter your choice (1-3): ").strip()
            
            if choice == "2":
                print("👋 Goodbye! Come back when markets are open.")
                return False
            elif choice == "3":
                print("🧪 Continuing in test mode...")
                return True
        
        print(f"\n⏳ Waiting for market open... ({hours:02d}:{minutes:02d}:{seconds:02d} remaining)")
        print("Press Ctrl+C to cancel")
        
        try:
            # Show countdown every minute for long waits, every 10 seconds for short waits
            update_interval = 60 if wait_seconds > 600 else 10
            
            while not self.is_market_hours():
                current_wait = (next_open - datetime.now(est)).total_seconds()
                
                if current_wait <= 0:
                    break
                
                hours = int(current_wait // 3600)
                minutes = int((current_wait % 3600) // 60)
                seconds = int(current_wait % 60)
                
                print(f"\r⏳ Time until market open: {hours:02d}:{minutes:02d}:{seconds:02d}", end="", flush=True)
                
                # Sleep for update interval or remaining time, whichever is shorter
                sleep_time = min(update_interval, current_wait)
                time.sleep(sleep_time)
            
            print(f"\n\n🎉 Market is now open! Starting trading session...")
            return True
            
        except KeyboardInterrupt:
            print(f"\n\n🛑 Wait cancelled by user")
            return False
    
    def start_component(self, component_name: str, extra_args: List[str] = None) -> bool:
        """Start a specific component"""
        if component_name not in self.components:
            self.logger.error(f"❌ Unknown component: {component_name}")
            return False
            
        comp = self.components[component_name]
        script_path = Path(comp['script'])
        
        if not script_path.exists():
            self.logger.error(f"❌ Script not found: {script_path}")
            return False
            
        # Build command
        cmd = [self.python_cmd, str(script_path)]
        cmd.extend(comp['args'])
        if extra_args:
            cmd.extend(extra_args)
            
        try:
            self.logger.info(f"🚀 Starting {comp['description']}...")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.processes[component_name] = process
            self.status[component_name] = "running"
            
            self.logger.info(f"✅ {comp['description']} started (PID: {process.pid})")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to start {comp['description']}: {e}")
            self.status[component_name] = "failed"
            return False
    
    def stop_component(self, component_name: str) -> bool:
        """Stop a specific component"""
        if component_name not in self.processes:
            return True
            
        try:
            process = self.processes[component_name]
            if process.poll() is None:  # Process is still running
                self.logger.info(f"🛑 Stopping {component_name}...")
                process.terminate()
                
                # Wait for graceful shutdown
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    self.logger.warning(f"⚠️ Force killing {component_name}...")
                    process.kill()
                    process.wait()
                    
            del self.processes[component_name]
            self.status[component_name] = "stopped"
            
            self.logger.info(f"✅ {component_name} stopped")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error stopping {component_name}: {e}")
            return False
    
    def monitor_components(self):
        """Monitor running components and restart if needed"""
        while self.running:
            try:
                failed_components = []
                
                for name, process in list(self.processes.items()):
                    if process.poll() is not None:  # Process has terminated
                        exit_code = process.returncode
                        comp = self.components[name]
                        
                        if exit_code != 0:
                            self.logger.error(f"❌ {comp['description']} crashed (exit code: {exit_code})")
                            failed_components.append(name)
                        else:
                            self.logger.info(f"ℹ️ {comp['description']} exited normally")
                            
                        del self.processes[name]
                        self.status[name] = "failed" if exit_code != 0 else "stopped"
                
                # Restart failed critical components
                for name in failed_components:
                    comp = self.components[name]
                    if comp['restart_on_failure'] and self.running:
                        self.logger.info(f"🔄 Restarting {comp['description']}...")
                        time.sleep(5)  # Brief delay before restart
                        self.start_component(name)
                
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                self.logger.error(f"❌ Error in component monitoring: {e}")
                time.sleep(10)
    
    def print_status(self):
        """Print current status of all components"""
        print("\n" + "="*60)
        print("📊 TRADING SYSTEM STATUS")
        print("="*60)
        
        for name, comp in self.components.items():
            status = self.status.get(name, "not_started")
            status_icon = {
                "running": "🟢",
                "stopped": "🔴", 
                "failed": "❌",
                "not_started": "⚪"
            }.get(status, "❓")
            
            pid = ""
            if name in self.processes and self.processes[name].poll() is None:
                pid = f" (PID: {self.processes[name].pid})"
                
            print(f"{status_icon} {comp['description']:<30} {status.upper()}{pid}")
        
        print("="*60)
        
        if self.is_market_hours():
            print("🟢 Market Status: OPEN")
        else:
            print("🔴 Market Status: CLOSED")
            
        print(f"⏰ Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60 + "\n")
    
    def start_trading_session(self, mode: str = "full", bypass_market_hours: bool = False, auto_wait: bool = True):
        """Start a complete trading session"""
        self.logger.info(f"🚀 Starting trading session in {mode} mode...")
        
        if not self.validate_environment(bypass_market_hours, auto_wait):
            self.logger.error("❌ Environment validation failed - cannot start trading")
            return False
            
        self.running = True
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=self.monitor_components, daemon=True)
        monitor_thread.start()
        
        # Start components based on mode
        if mode == "full":
            # Start main trading bot
            if not self.start_component('main_bot'):
                self.logger.error("❌ Failed to start main trading bot")
                return False
                
            # Start dashboard if requested
            if "--dashboard" in sys.argv:
                time.sleep(2)  # Brief delay
                self.start_component('dashboard')
                
        elif mode == "demo":
            # Start demo mode
            if not self.start_component('main_bot', ['--dry-run']):
                self.logger.error("❌ Failed to start demo mode")
                return False
                
        elif mode == "test":
            # Start test mode with specific symbol
            symbol = input("Enter symbol to test (e.g., AAPL): ").strip().upper()
            if symbol:
                if not self.start_component('main_bot', ['--test', symbol, '--dry-run']):
                    self.logger.error("❌ Failed to start test mode")
                    return False
        
        self.logger.info("✅ Trading session started successfully")
        return True
    
    def stop_trading_session(self):
        """Stop the trading session and all components"""
        self.logger.info("🛑 Stopping trading session...")
        self.running = False
        
        # Stop all components
        for component_name in list(self.processes.keys()):
            self.stop_component(component_name)
            
        self.logger.info("✅ Trading session stopped")
    
    def interactive_menu(self):
        """Show interactive menu for managing the trading system"""
        while True:
            self.print_status()
            
            print("Available Commands:")
            print("1. Start Full Trading Session (Auto-wait for market)")
            print("2. Start Demo Mode (Safe Testing)")
            print("3. Start Test Mode (Single Symbol)")
            print("4. Start Live P&L Monitor Only")
            print("5. 🧪 Test Mode (Bypass Market Hours)")
            print("6. 🕐 Show Market Status & Countdown")
            print("7. 💾 Backup to GitHub")
            print("8. Stop Trading Session")
            print("9. Restart Component")
            print("10. Generate P&L Report")
            print("11. Generate EOD Report")
            print("12. View Live Dashboard")
            print("13. Validate Environment")
            print("14. Exit")
            
            choice = input("\nEnter your choice (1-14): ").strip()
            
            if choice == "1":
                if not any(self.processes.values()):
                    print("🚀 Starting full trading session...")
                    if not self.is_market_hours():
                        print("⏰ Market is closed. The bot will wait for market open.")
                    self.start_trading_session("full", auto_wait=True)
                else:
                    print("❌ Trading session is already running")
                    
            elif choice == "2":
                if not any(self.processes.values()):
                    self.start_component('demo_bot')
                else:
                    print("❌ Components are already running")
                    
            elif choice == "3":
                if not any(self.processes.values()):
                    self.start_trading_session("test", auto_wait=True)
                else:
                    print("❌ Trading session is already running")
                    
            elif choice == "4":
                if 'live_pnl' not in self.processes:
                    self.start_component('live_pnl')
                else:
                    print("ℹ️ P&L monitor is already running")
                    
            elif choice == "5":
                if not any(self.processes.values()):
                    print("🧪 Testing mode - bypassing market hours check")
                    mode = input("Choose mode (full/demo/test): ").strip().lower()
                    if mode in ['full', 'demo', 'test']:
                        if mode == 'test':
                            symbol = input("Enter symbol to test (e.g., AAPL): ").strip().upper()
                            if symbol:
                                # Override component args for test mode
                                self.components['main_bot']['args'] = ['--test', symbol, '--dry-run']
                        self.start_trading_session(mode, bypass_market_hours=True, auto_wait=False)
                    else:
                        print("❌ Invalid mode")
                else:
                    print("❌ Trading session is already running")
                    
            elif choice == "6":
                self.show_market_status()
                
            elif choice == "7":
                self.backup_to_github()
                    
            elif choice == "8":
                self.stop_trading_session()
                
            elif choice == "9":
                self.restart_component_menu()
                
            elif choice == "10":
                self.generate_pnl_report()
                
            elif choice == "11":
                self.generate_eod_report()
                
            elif choice == "12":
                self.launch_dashboard()
                
            elif choice == "13":
                print("🔍 Validating environment...")
                if self.validate_environment(bypass_market_hours=True):
                    print("✅ Environment validation passed")
                else:
                    print("❌ Environment validation failed")
                    
            elif choice == "14":
                if any(self.processes.values()):
                    confirm = input("Trading session is running. Stop and exit? (y/N): ")
                    if confirm.lower() == 'y':
                        self.stop_trading_session()
                        break
                else:
                    break
            else:
                print("❌ Invalid choice")
                
            input("\nPress Enter to continue...")
    
    def restart_component_menu(self):
        """Show menu for restarting specific components"""
        running_components = [name for name, proc in self.processes.items() 
                            if proc.poll() is None]
        
        if not running_components:
            print("❌ No components are currently running")
            return
            
        print("\nRunning Components:")
        for i, name in enumerate(running_components, 1):
            comp = self.components[name]
            print(f"{i}. {comp['description']}")
            
        try:
            choice = int(input("\nSelect component to restart (0 to cancel): "))
            if 1 <= choice <= len(running_components):
                component_name = running_components[choice - 1]
                comp = self.components[component_name]
                
                print(f"🔄 Restarting {comp['description']}...")
                self.stop_component(component_name)
                time.sleep(2)
                self.start_component(component_name)
                
        except (ValueError, IndexError):
            print("❌ Invalid selection")
    
    def generate_pnl_report(self):
        """Generate P&L report"""
        try:
            print("📊 Generating P&L report...")
            result = subprocess.run([
                self.python_cmd, 'intraday_trading_bot.py', '--pnl-report'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print(result.stdout)
            else:
                print(f"❌ Error generating report: {result.stderr}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def generate_eod_report(self):
        """Generate end-of-day report"""
        try:
            print("📊 Generating end-of-day report...")
            result = subprocess.run([
                self.python_cmd, 'generate_eod_report.py'
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print(result.stdout)
                print("✅ EOD report generated successfully")
            else:
                print(f"❌ Error generating EOD report: {result.stderr}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def backup_to_github(self):
        """Manual backup to GitHub"""
        try:
            print("💾 Starting GitHub backup...")
            
            # Check if git repository exists
            if not Path(".git").exists():
                print("❌ No git repository found. Please run setup_github.ps1 first.")
                return
            
            # Run the backup script
            backup_script = Path("backup_to_github.ps1")
            if backup_script.exists():
                result = subprocess.run([
                    "powershell.exe", "-ExecutionPolicy", "Bypass", "-File", str(backup_script)
                ], capture_output=True, text=True, timeout=120)
                
                if result.returncode == 0:
                    print("✅ GitHub backup completed successfully!")
                    print(result.stdout)
                else:
                    print("❌ Backup failed:")
                    print(result.stderr)
            else:
                print("❌ Backup script not found. Please run setup_github.ps1 first.")
                
        except Exception as e:
            print(f"❌ Error during backup: {e}")
    
    def show_market_status(self):
        """Display current market status and countdown to next open"""
        est = pytz.timezone('US/Eastern')
        now = datetime.now(est)
        
        print("\n" + "="*60)
        print("📊 MARKET STATUS INFORMATION")
        print("="*60)
        print(f"📅 Current Time: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        
        if self.is_market_hours():
            print("🟢 Market Status: OPEN")
            market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
            time_to_close = (market_close - now).total_seconds()
            
            if time_to_close > 0:
                hours = int(time_to_close // 3600)
                minutes = int((time_to_close % 3600) // 60)
                print(f"⏰ Time Until Close: {hours:02d}:{minutes:02d}")
            else:
                print("⏰ Market closing soon")
        else:
            print("🔴 Market Status: CLOSED")
            next_open = self.get_next_market_open()
            print(f"🚀 Next Market Open: {next_open.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            
            time_to_open = (next_open - now).total_seconds()
            
            if time_to_open > 0:
                days = int(time_to_open // 86400)
                hours = int((time_to_open % 86400) // 3600)
                minutes = int((time_to_open % 3600) // 60)
                
                if days > 0:
                    print(f"⏰ Time Until Open: {days} day(s), {hours:02d}:{minutes:02d}")
                else:
                    print(f"⏰ Time Until Open: {hours:02d}:{minutes:02d}")
                    
                # Show day of week info for weekends
                if now.weekday() >= 5:
                    print("📅 Weekend - Markets closed until Monday")
        
        print("="*60 + "\n")
    
    def launch_dashboard(self):
        """Launch live dashboard"""
        if 'dashboard' not in self.processes:
            self.start_component('dashboard')
        else:
            print("ℹ️ Dashboard is already running")

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print("\n🛑 Shutdown signal received...")
    global orchestrator
    if 'orchestrator' in globals():
        orchestrator.stop_trading_session()
    sys.exit(0)

def main():
    """Main entry point"""
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    parser = argparse.ArgumentParser(description="Intraday Trading System Orchestrator")
    parser.add_argument('--mode', choices=['full', 'demo', 'test', 'interactive'], 
                       default='interactive', help='Launch mode')
    parser.add_argument('--symbol', help='Symbol for test mode')
    parser.add_argument('--dashboard', action='store_true', help='Include dashboard')
    parser.add_argument('--status', action='store_true', help='Show status and exit')
    
    args = parser.parse_args()
    
    global orchestrator
    orchestrator = TradingSystemOrchestrator()
    
    if args.status:
        orchestrator.print_status()
        return
    
    try:
        if args.mode == 'interactive':
            orchestrator.interactive_menu()
        else:
            if args.mode == 'test' and args.symbol:
                # Override component args for test mode
                orchestrator.components['main_bot']['args'] = ['--test', args.symbol, '--dry-run']
                
            success = orchestrator.start_trading_session(args.mode)
            if success:
                print("🚀 Trading system started. Press Ctrl+C to stop...")
                
                # Keep running until interrupted
                try:
                    while orchestrator.running:
                        time.sleep(1)
                except KeyboardInterrupt:
                    pass
                    
            orchestrator.stop_trading_session()
            
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        orchestrator.stop_trading_session()
        sys.exit(1)

if __name__ == "__main__":
    main()
