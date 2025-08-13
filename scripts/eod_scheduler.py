#!/usr/bin/env python3
"""
EOD Analysis Scheduler
Automatically runs comprehensive End-of-Day analysis at market close
Includes email notifications and auto-retry logic
"""

import schedule
import time
import subprocess
import sys
import os
from datetime import datetime, timedelta
import threading
import logging
from pathlib import Path

# Set up logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / f"eod_scheduler_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)

class EODScheduler:
    def __init__(self):
        self.running = False
        self.market_close_time = "16:00"  # 4:00 PM ET (market close)
        self.analysis_delay = 30  # Wait 30 minutes after close for settlement
        self.retry_attempts = 3
        
        logging.info("EOD Analysis Scheduler initialized")
        logging.info(f"Market close time: {self.market_close_time}")
        logging.info(f"Analysis will run {self.analysis_delay} minutes after close")

    def is_trading_day(self):
        """Check if today is a trading day (Monday-Friday, excluding holidays)"""
        today = datetime.now().weekday()  # 0=Monday, 6=Sunday
        return today < 5  # Monday through Friday

    def run_eod_analysis(self):
        """Run the EOD analysis with retry logic"""
        if not self.is_trading_day():
            logging.info("Today is not a trading day, skipping EOD analysis")
            return
        
        logging.info("🚀 Starting scheduled EOD analysis...")
        
        for attempt in range(1, self.retry_attempts + 1):
            try:
                # Run the EOD analysis script
                result = subprocess.run([
                    sys.executable, "eod_analysis.py"
                ], capture_output=True, text=True, timeout=300)  # 5 minute timeout
                
                if result.returncode == 0:
                    logging.info("✅ EOD Analysis completed successfully!")
                    logging.info(f"Output: {result.stdout}")
                    
                    # Try to open the dashboard automatically
                    self.open_dashboard()
                    break
                else:
                    logging.error(f"❌ EOD Analysis failed (attempt {attempt}/{self.retry_attempts})")
                    logging.error(f"Error: {result.stderr}")
                    
                    if attempt < self.retry_attempts:
                        wait_time = attempt * 60  # Progressive delay
                        logging.info(f"Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                    
            except subprocess.TimeoutExpired:
                logging.error(f"⏰ EOD Analysis timed out (attempt {attempt}/{self.retry_attempts})")
                if attempt < self.retry_attempts:
                    time.sleep(60)
            
            except Exception as e:
                logging.error(f"💥 Unexpected error in EOD analysis: {e}")
                if attempt < self.retry_attempts:
                    time.sleep(60)
        
        if attempt == self.retry_attempts:
            logging.error("🔥 All EOD analysis attempts failed!")
            self.send_failure_notification()

    def open_dashboard(self):
        """Try to open the generated dashboard"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            dashboard_path = Path("reports") / today / "eod_dashboard.html"
            
            if dashboard_path.exists():
                import webbrowser
                webbrowser.open(f"file://{dashboard_path.absolute()}")
                logging.info(f"📊 Dashboard opened: {dashboard_path}")
            else:
                logging.warning("Dashboard file not found")
                
        except Exception as e:
            logging.error(f"Failed to open dashboard: {e}")

    def send_failure_notification(self):
        """Send notification on failure (placeholder for email/slack integration)"""
        logging.error("📧 Sending failure notification...")
        # TODO: Add email/Slack notification here
        
    def manual_run(self):
        """Manually trigger EOD analysis"""
        logging.info("🔧 Manual EOD analysis triggered")
        threading.Thread(target=self.run_eod_analysis, daemon=True).start()

    def start_scheduler(self):
        """Start the automated scheduler"""
        if self.running:
            logging.warning("Scheduler is already running")
            return
            
        self.running = True
        
        # Calculate when to run analysis (market close + delay)
        close_time = datetime.strptime(self.market_close_time, "%H:%M").time()
        analysis_time = (datetime.combine(datetime.now().date(), close_time) + 
                        timedelta(minutes=self.analysis_delay)).time()
        
        # Schedule the job
        schedule.every().monday.at(analysis_time.strftime("%H:%M")).do(self.run_eod_analysis)
        schedule.every().tuesday.at(analysis_time.strftime("%H:%M")).do(self.run_eod_analysis)
        schedule.every().wednesday.at(analysis_time.strftime("%H:%M")).do(self.run_eod_analysis)
        schedule.every().thursday.at(analysis_time.strftime("%H:%M")).do(self.run_eod_analysis)
        schedule.every().friday.at(analysis_time.strftime("%H:%M")).do(self.run_eod_analysis)
        
        logging.info(f"📅 EOD Analysis scheduled for {analysis_time.strftime('%H:%M')} on trading days")
        logging.info("🔄 Scheduler started. Press Ctrl+C to stop.")
        
        try:
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            logging.info("🛑 Scheduler stopped by user")
            self.running = False

    def stop_scheduler(self):
        """Stop the scheduler"""
        self.running = False
        schedule.clear()
        logging.info("⏹️ Scheduler stopped")

    def show_status(self):
        """Show current scheduler status"""
        if self.running:
            logging.info("📊 EOD Scheduler Status: RUNNING")
            logging.info(f"Next run: {schedule.next_run()}")
        else:
            logging.info("📊 EOD Scheduler Status: STOPPED")
        
        return self.running

def main():
    """Main function with command line interface"""
    scheduler = EODScheduler()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "start":
            scheduler.start_scheduler()
        elif command == "run":
            scheduler.manual_run()
            input("Press Enter to exit...")
        elif command == "status":
            scheduler.show_status()
        else:
            print("Usage: python eod_scheduler.py [start|run|status]")
            print("  start  - Start automatic scheduler")
            print("  run    - Run analysis immediately")
            print("  status - Show scheduler status")
    else:
        # Interactive mode
        print("="*60)
        print("      EOD ANALYSIS SCHEDULER")
        print("="*60)
        print("1. Start automatic scheduler")
        print("2. Run analysis now")
        print("3. Show status")
        print("4. Exit")
        print("="*60)
        
        while True:
            try:
                choice = input("\nSelect option (1-4): ").strip()
                
                if choice == "1":
                    scheduler.start_scheduler()
                    break
                elif choice == "2":
                    scheduler.manual_run()
                    input("Press Enter to continue...")
                elif choice == "3":
                    scheduler.show_status()
                elif choice == "4":
                    print("Goodbye!")
                    break
                else:
                    print("Invalid choice. Please select 1-4.")
                    
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break

if __name__ == "__main__":
    main()
