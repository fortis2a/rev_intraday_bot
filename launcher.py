#!/usr/bin/env python3
"""
Intraday Trading Bot Launcher
ASCII-only, no Unicode characters
"""

import subprocess
import time
import os
import signal
from datetime import datetime
from pathlib import Path
from logger import setup_logger

class TradingLauncher:
    """Main launcher for the intraday trading system"""
    
    def __init__(self):
        self.logger = setup_logger('trading_launcher')
        self.processes = {}
        self.python_cmd = 'python'
        
        # Create logs directory
        Path('logs').mkdir(exist_ok=True)
        
        self.logger.info("[INIT] Trading System Launcher initialized")
    
    def show_status(self):
        """Show system status"""
        print("\n" + "="*70)
        print("           INTRADAY TRADING SYSTEM STATUS")
        print("="*70)
        
        # Check if components are running
        components = {
            'Main Trading Engine': self.is_process_running('main_engine'),
            'Live P&L Monitor': self.is_process_running('pnl_monitor'),
            'Dashboard': self.is_process_running('dashboard')
        }
        
        for name, status in components.items():
            status_text = "RUNNING" if status else "STOPPED"
            status_icon = "[ACTIVE]" if status else "[READY]"
            print(f"{status_icon} {name:<25} {status_text}")
        
        print("="*70)
        
        # Market status
        try:
            result = subprocess.run([self.python_cmd, '-c', 
                'from data_manager import DataManager; dm = DataManager(); status = dm.get_market_status(); print("OPEN" if status["is_open"] else "CLOSED")'], 
                capture_output=True, text=True, timeout=10)
            market_status = result.stdout.strip() if result.returncode == 0 else "UNKNOWN"
        except:
            market_status = "UNKNOWN"
        
        print(f"[{market_status}] Market Status: {market_status}")
        print(f"[TIME] Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
    
    def show_account_info(self):
        """Show Alpaca account information"""
        try:
            print("\n[ACCOUNT] Fetching account information...")
            result = subprocess.run([
                self.python_cmd, '-c',
                'from data_manager import DataManager; dm = DataManager(); account = dm.get_account_info(); '
                'print(f"Equity: ${account[\'equity\']:,.2f}") if account else print("Failed to get account info"); '
                'print(f"Buying Power: ${account[\'buying_power\']:,.2f}") if account else None; '
                'print(f"Cash: ${account[\'cash\']:,.2f}") if account else None'
            ], capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                print("[SUCCESS] Account connected!")
                print(result.stdout)
            else:
                print("[ERROR] Failed to get account info")
                print(result.stderr)
                
        except Exception as e:
            print(f"[ERROR] Account check failed: {e}")
    
    def is_process_running(self, name):
        """Check if a process is running"""
        return name in self.processes and self.processes[name].poll() is None
    
    def start_main_engine(self, mode="LIVE"):
        """Start the main trading engine"""
        try:
            if self.is_process_running('main_engine'):
                print("[INFO] Main engine already running")
                return True
            
            print(f"[START] Starting main trading engine in {mode} mode...")
            self.logger.info(f"[START] Starting main trading engine in {mode} mode")
            
            cmd = [self.python_cmd, 'main.py', '--mode', mode]
            process = subprocess.Popen(cmd, 
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE,
                                     text=True)
            
            self.processes['main_engine'] = process
            print(f"[SUCCESS] Main engine started (PID: {process.pid})")
            self.logger.info(f"[SUCCESS] Main engine started (PID: {process.pid})")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to start main engine: {e}")
            self.logger.error(f"[ERROR] Failed to start main engine: {e}")
            return False
    
    def start_pnl_monitor(self):
        """Start P&L monitoring"""
        try:
            if self.is_process_running('pnl_monitor'):
                print("[INFO] P&L monitor already running")
                return True
            
            print("[START] Starting P&L monitor...")
            self.logger.info("[START] Starting P&L monitor")
            
            # Create simple P&L monitor script
            pnl_script = '''
import time
import sys
sys.path.append(".")
from data_manager import DataManager
from logger import setup_logger

logger = setup_logger("pnl_monitor")
dm = DataManager()

logger.info("[START] P&L Monitor started")

while True:
    try:
        account = dm.get_account_info()
        positions = dm.get_positions()
        
        if account:
            total_unrealized = sum(p["unrealized_pl"] for p in positions)
            logger.info(f"[PNL] Equity: ${account['equity']:,.2f}")
            logger.info(f"[PNL] Unrealized P&L: ${total_unrealized:,.2f}")
            logger.info(f"[PNL] Positions: {len(positions)}")
            
            if positions:
                for pos in positions:
                    logger.info(f"[POS] {pos['symbol']}: {pos['qty']} shares, P&L: ${pos['unrealized_pl']:,.2f}")
        
        time.sleep(30)  # Update every 30 seconds
    except KeyboardInterrupt:
        logger.info("[STOP] P&L Monitor stopped")
        break
    except Exception as e:
        logger.error(f"[ERROR] P&L monitor error: {e}")
        time.sleep(60)
'''
            
            with open('pnl_monitor.py', 'w') as f:
                f.write(pnl_script)
            
            cmd = [self.python_cmd, 'pnl_monitor.py']
            process = subprocess.Popen(cmd,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     text=True)
            
            self.processes['pnl_monitor'] = process
            print(f"[SUCCESS] P&L monitor started (PID: {process.pid})")
            self.logger.info(f"[SUCCESS] P&L monitor started (PID: {process.pid})")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to start P&L monitor: {e}")
            self.logger.error(f"[ERROR] Failed to start P&L monitor: {e}")
            return False
    
    def start_dashboard(self):
        """Start dashboard mode"""
        try:
            print("[START] Starting dashboard mode...")
            self.logger.info("[START] Starting dashboard mode")
            
            cmd = [self.python_cmd, 'main.py', '--dashboard']
            process = subprocess.Popen(cmd,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     text=True)
            
            self.processes['dashboard'] = process
            print(f"[SUCCESS] Dashboard started (PID: {process.pid})")
            self.logger.info(f"[SUCCESS] Dashboard started (PID: {process.pid})")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to start dashboard: {e}")
            self.logger.error(f"[ERROR] Failed to start dashboard: {e}")
            return False
    
    def stop_process(self, name):
        """Stop a specific process"""
        try:
            if name in self.processes:
                process = self.processes[name]
                if process.poll() is None:  # Still running
                    process.terminate()
                    process.wait(timeout=10)
                    print(f"[STOP] {name} stopped")
                    self.logger.info(f"[STOP] {name} stopped")
                del self.processes[name]
                return True
        except Exception as e:
            print(f"[ERROR] Failed to stop {name}: {e}")
            self.logger.error(f"[ERROR] Failed to stop {name}: {e}")
        return False
    
    def stop_all(self):
        """Stop all processes"""
        print("[STOP] Stopping all processes...")
        self.logger.info("[STOP] Stopping all processes")
        
        for name in list(self.processes.keys()):
            self.stop_process(name)
        
        print("[STOP] All processes stopped")
        self.logger.info("[STOP] All processes stopped")
    
    def validate_environment(self):
        """Validate trading environment"""
        try:
            print("[VALIDATE] Testing environment...")
            self.logger.info("[VALIDATE] Testing environment")
            
            # Test main.py validation
            result = subprocess.run([self.python_cmd, 'main.py', '--validate-only'],
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("[SUCCESS] Environment validation passed")
                self.logger.info("[SUCCESS] Environment validation passed")
                return True
            else:
                print(f"[ERROR] Validation failed: {result.stderr}")
                self.logger.error(f"[ERROR] Validation failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"[ERROR] Validation error: {e}")
            self.logger.error(f"[ERROR] Validation error: {e}")
            return False
    
    def show_live_logs(self):
        """Show live log feed"""
        try:
            print("\n" + "="*70)
            print("               LIVE LOG MONITORING")
            print("="*70)
            print("[INFO] Showing recent activity from log files")
            print("[CTRL+C] Press Ctrl+C to return to menu")
            print("="*70)
            
            log_files = list(Path('logs').glob('*.log'))
            if not log_files:
                print("[INFO] No log files found")
                input("\nPress Enter to continue...")
                return
            
            # Show recent entries from the most recent log
            latest_log = max(log_files, key=lambda x: x.stat().st_mtime)
            print(f"[FILE] Monitoring: {latest_log.name}")
            print("-" * 70)
            
            # Show last 20 lines
            try:
                with open(latest_log, 'r', encoding='ascii', errors='replace') as f:
                    lines = f.readlines()[-20:]
                    for line in lines:
                        print(line.strip())
            except Exception as e:
                print(f"[ERROR] Could not read log file: {e}")
            
            print("-" * 70)
            input("\nPress Enter to continue...")
            
        except Exception as e:
            print(f"[ERROR] Failed to show logs: {e}")
            self.logger.error(f"[ERROR] Failed to show logs: {e}")
    
    def generate_report(self):
        """Generate trading report"""
        try:
            print("[REPORT] Generating trading report...")
            self.logger.info("[REPORT] Generating trading report")
            
            result = subprocess.run([self.python_cmd, 'main.py', '--pnl-report'],
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print(result.stdout)
                print("[SUCCESS] Report generated")
                self.logger.info("[SUCCESS] Report generated")
            else:
                print(f"[ERROR] Report generation failed: {result.stderr}")
                self.logger.error(f"[ERROR] Report generation failed: {result.stderr}")
                
        except Exception as e:
            print(f"[ERROR] Report generation error: {e}")
            self.logger.error(f"[ERROR] Report generation error: {e}")
    
    def run_eod_analysis(self):
        """Run comprehensive End-of-Day analysis"""
        try:
            print("\n" + "="*70)
            print("           END-OF-DAY COMPREHENSIVE ANALYSIS")
            print("="*70)
            print("[INFO] This will generate comprehensive EOD reports including:")
            print("       • Stock-by-stock P&L analysis")
            print("       • Long vs Short performance breakdown")
            print("       • Hourly trading patterns and timing")
            print("       • Win/loss distribution charts")
            print("       • Interactive HTML dashboard")
            print("       • Detailed summary statistics")
            print("="*70)
            
            choice = input("\nRun EOD Analysis now? (y/N): ").strip().lower()
            
            if choice in ['y', 'yes']:
                print("\n[START] Running comprehensive EOD analysis...")
                self.logger.info("[START] Running EOD analysis")
                
                result = subprocess.run([self.python_cmd, 'scripts/eod_analysis.py'],
                                      capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    print(result.stdout)
                    print("\n[SUCCESS] ✅ EOD Analysis completed!")
                    print("[INFO] 📁 Reports saved to: reports/[today]/")
                    
                    # Try to open dashboard
                    from datetime import datetime
                    import webbrowser
                    from pathlib import Path
                    
                    today = datetime.now().strftime('%Y-%m-%d')
                    dashboard_path = Path("reports") / today / "eod_dashboard.html"
                    
                    if dashboard_path.exists():
                        open_dashboard = input("\nOpen interactive dashboard? (Y/n): ").strip().lower()
                        if open_dashboard != 'n':
                            try:
                                webbrowser.open(f"file://{dashboard_path.absolute()}")
                                print(f"[SUCCESS] 🌐 Dashboard opened: {dashboard_path}")
                            except Exception as e:
                                print(f"[ERROR] Could not open dashboard: {e}")
                    
                    self.logger.info("[SUCCESS] EOD analysis completed")
                    
                else:
                    print(f"[ERROR] EOD Analysis failed: {result.stderr}")
                    self.logger.error(f"[ERROR] EOD analysis failed: {result.stderr}")
            else:
                print("[CANCEL] EOD Analysis cancelled")
                
        except Exception as e:
            print(f"[ERROR] EOD Analysis error: {e}")
            self.logger.error(f"[ERROR] EOD analysis error: {e}")
    
    def run_github_backup(self):
        """Run GitHub backup system - manual or scheduled"""
        try:
            print("\n" + "="*70)
            print("           GITHUB BACKUP SYSTEM")
            print("="*70)
            print("[INFO] Repository: https://github.com/fortis2a/rev_intraday_bot")
            print("[INFO] This will backup your complete trading system including:")
            print("       • All Python code and configurations")
            print("       • Trading strategies and core components")
            print("       • Launchers and utility scripts")
            print("       • Documentation and setup files")
            print()
            print("[EXCLUDED] For security and efficiency:")
            print("       • Environment variables (.env file)")
            print("       • Log files and reports (generated data)")
            print("       • Python cache files")
            print("="*70)
            print("1. Backup Now (Manual)")
            print("2. Start Auto Scheduler (Daily at midnight)")
            print("3. Cancel")
            print("="*70)
            
            choice = input("\nSelect backup option (1-3): ").strip()
            
            if choice == '1':
                print("\n[START] Running manual GitHub backup...")
                self.logger.info("[START] Running manual GitHub backup")
                
                result = subprocess.run([self.python_cmd, 'scripts/backup_system.py', 'backup'],
                                      capture_output=True, text=True, timeout=120)
                
                if result.returncode == 0:
                    print(result.stdout)
                    print("\n[SUCCESS] ✅ GitHub backup completed!")
                    print("[INFO] 📦 Repository: https://github.com/fortis2a/rev_intraday_bot")
                    self.logger.info("[SUCCESS] GitHub backup completed")
                else:
                    print(f"[ERROR] GitHub backup failed: {result.stderr}")
                    self.logger.error(f"[ERROR] GitHub backup failed: {result.stderr}")
                    
            elif choice == '2':
                print("\n[START] Starting auto backup scheduler...")
                print("[INFO] This will run backup daily at midnight")
                print("[INFO] Press Ctrl+C to stop the scheduler")
                self.logger.info("[START] Starting auto backup scheduler")
                
                try:
                    result = subprocess.run([self.python_cmd, 'scripts/backup_system.py', 'schedule'],
                                          timeout=None)  # No timeout for scheduler
                except KeyboardInterrupt:
                    print("\n[STOP] Backup scheduler stopped")
                    self.logger.info("[STOP] Backup scheduler stopped")
                    
            elif choice == '3':
                print("[CANCEL] GitHub backup cancelled")
            else:
                print("[ERROR] Invalid choice")
                
        except Exception as e:
            print(f"[ERROR] GitHub backup error: {e}")
            self.logger.error(f"[ERROR] GitHub backup error: {e}")
    
    def start_live_trading_with_signals(self):
        """Start live trading and show real-time signals"""
        try:
            print("\n" + "="*70)
            print("           STARTING LIVE TRADING WITH SIGNAL FEED")
            print("="*70)
            print("[INFO] This will start the trading engine and show live signals")
            print("[INFO] You'll see account info, trading decisions, and market data")
            print("[CTRL+C] Press Ctrl+C to stop and return to menu")
            print("="*70)
            
            # Show account info first
            self.show_account_info()
            
            # Start the main engine
            if self.start_main_engine("LIVE"):
                print("[INFO] Trading engine started - monitoring for signals...")
                
                # Monitor the process and show logs
                process = self.processes.get('main_engine')
                if process:
                    try:
                        # Let it run and show live output
                        while process.poll() is None:
                            time.sleep(2)
                            # Show recent logs
                            self.show_recent_activity()
                            
                    except KeyboardInterrupt:
                        print("\n[STOP] Stopping live trading...")
                        self.stop_process('main_engine')
                        print("[STOP] Live trading stopped")
            else:
                print("[ERROR] Failed to start trading engine")
                
        except Exception as e:
            print(f"[ERROR] Live trading failed: {e}")
            self.logger.error(f"[ERROR] Live trading failed: {e}")
    
    def show_recent_activity(self):
        """Show recent activity from logs"""
        try:
            log_files = list(Path('logs').glob('*intraday_engine*.log'))
            if log_files:
                latest_log = max(log_files, key=lambda x: x.stat().st_mtime)
                with open(latest_log, 'r', encoding='ascii', errors='replace') as f:
                    lines = f.readlines()[-5:]  # Last 5 lines
                    for line in lines:
                        if line.strip():
                            print(f"[LOG] {line.strip()}")
        except:
            pass  # Ignore errors in log reading
    
    def main_menu(self):
        """Main menu loop"""
        while True:
            try:
                self.show_status()
                
                print("\nIntraday Trading Bot - Main Menu:")
                print("1. Start Full Trading Session (Live Mode)")
                print("2. Start Demo Mode (Safe Testing)")
                print("3. Start Test Mode (Single Cycle)")
                print("4. Start P&L Monitor Only")
                print("5. Start Live Trading + Show Signal Feed")
                print("6. Start Dashboard")
                print("7. Show Live Logs")
                print("8. Show Account Information")
                print("9. Generate Trading Report")
                print("10. EOD Analysis (End-of-Day Reports)")
                print("11. GitHub Backup (Manual & Auto Scheduler)")
                print("12. Validate Environment")
                print("13. Test Enhanced Indicators (NEW)")
                print("14. Stop All Processes")
                print("15. Exit")
                
                choice = input("\nEnter your choice (1-15): ").strip()
                
                if choice == '1':
                    print("\n[START] Starting full trading session...")
                    if self.validate_environment():
                        if self.start_main_engine("LIVE"):
                            print("[SUCCESS] Full trading session started")
                            print("[INFO] Check logs for trading activity")
                        else:
                            print("[ERROR] Failed to start trading session")
                    else:
                        print("[ERROR] Environment validation failed")
                
                elif choice == '2':
                    print("\n[START] Starting demo mode...")
                    if self.validate_environment():
                        if self.start_main_engine("DEMO"):
                            print("[SUCCESS] Demo mode started")
                            print("[INFO] This is safe mode - no real trades")
                        else:
                            print("[ERROR] Failed to start demo mode")
                    else:
                        print("[ERROR] Environment validation failed")
                
                elif choice == '3':
                    print("\n[START] Starting test mode...")
                    if self.validate_environment():
                        if self.start_main_engine("TEST"):
                            print("[SUCCESS] Test mode started")
                            print("[INFO] Single test cycle - will auto-stop")
                        else:
                            print("[ERROR] Failed to start test mode")
                    else:
                        print("[ERROR] Environment validation failed")
                
                elif choice == '4':
                    print("\n[START] Starting P&L monitor...")
                    if self.start_pnl_monitor():
                        print("[SUCCESS] P&L monitor started")
                        print("[INFO] Check logs for P&L updates")
                    else:
                        print("[ERROR] Failed to start P&L monitor")
                
                elif choice == '5':
                    print("\n[START] Starting live trading with signal feed...")
                    if self.validate_environment():
                        self.start_live_trading_with_signals()
                    else:
                        print("[ERROR] Environment validation failed")
                
                elif choice == '6':
                    print("\n[START] Starting dashboard...")
                    if self.start_dashboard():
                        print("[SUCCESS] Dashboard started")
                    else:
                        print("[ERROR] Failed to start dashboard")
                
                elif choice == '7':
                    self.show_live_logs()
                
                elif choice == '8':
                    self.show_account_info()
                
                elif choice == '9':
                    self.generate_report()
                
                elif choice == '10':
                    self.run_eod_analysis()
                
                elif choice == '11':
                    self.run_github_backup()
                
                elif choice == '12':
                    if self.validate_environment():
                        print("[SUCCESS] Environment validation passed")
                    else:
                        print("[ERROR] Environment validation failed")
                
                elif choice == '13':
                    print("\n[TEST] Testing Enhanced Indicators...")
                    try:
                        result = subprocess.run([self.python_cmd, 'test_enhanced_indicators.py'], 
                                              capture_output=False, text=True)
                        if result.returncode == 0:
                            print("[SUCCESS] Enhanced indicators test completed successfully!")
                        else:
                            print("[WARNING] Enhanced indicators test completed with warnings")
                    except Exception as e:
                        print(f"[ERROR] Failed to run enhanced indicators test: {e}")
                
                elif choice == '14':
                    self.stop_all()
                    print("[SUCCESS] All processes stopped")
                
                elif choice == '15':
                    print("\n[EXIT] Shutting down trading system...")
                    self.stop_all()
                    print("[EXIT] Goodbye!")
                    break
                
                else:
                    print("[ERROR] Invalid choice. Please enter 1-15.")
                
                if choice != '15':
                    input("\nPress Enter to continue...")
                
            except KeyboardInterrupt:
                print("\n[STOP] Shutting down...")
                self.stop_all()
                break
            except Exception as e:
                print(f"[ERROR] Menu error: {e}")
                self.logger.error(f"[ERROR] Menu error: {e}")
                input("\nPress Enter to continue...")

def main():
    """Main entry point"""
    try:
        launcher = TradingLauncher()
        launcher.main_menu()
    except Exception as e:
        print(f"[ERROR] Launcher failed: {e}")
    finally:
        print("[CLEANUP] Cleaning up...")

if __name__ == "__main__":
    main()
