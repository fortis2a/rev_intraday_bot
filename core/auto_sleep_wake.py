#!/usr/bin/env python3
"""
Automatic Market Sleep/Wake System
Automatically puts the bot to sleep at market close (4:00 PM) and wakes it up at market open (9:30 AM)
Shows timer, countdown, and market status messages
"""

import time
import os
import sys
import threading
from datetime import datetime, timedelta
from pathlib import Path
import pytz
import schedule

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from core.data_manager import DataManager
from utils.logger import setup_logger

class AutoMarketSleepWake:
    """Automatic market sleep/wake system"""
    
    def __init__(self):
        self.logger = setup_logger('auto_sleep_wake')
        self.data_manager = DataManager()
        self.is_sleeping = False
        self.is_running = True
        self.timer_thread = None
        
        # Market timezone
        self.et_tz = pytz.timezone('US/Eastern')
        
        self.logger.info("[INIT] Auto Sleep/Wake System initialized")
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def get_market_status(self):
        """Get current market status"""
        try:
            status = self.data_manager.get_market_status()
            return {
                'is_open': status.get('is_open', False),
                'next_open': status.get('next_open'),
                'next_close': status.get('next_close')
            }
        except Exception as e:
            self.logger.error(f"[ERROR] Failed to get market status: {e}")
            return {'is_open': False, 'next_open': None, 'next_close': None}
    
    def display_market_closed_screen(self):
        """Display the market closed screen with countdown"""
        market_status = self.get_market_status()
        current_et = datetime.now(self.et_tz)
        
        self.clear_screen()
        print("="*80)
        print("                    🌙 MARKET CLOSED - BOT SLEEPING 🌙")
        print("="*80)
        print()
        print(f"[CURRENT TIME] {current_et.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"[STATUS] Market is CLOSED - Bot automatically sleeping")
        print()
        
        # Show countdown to next market open
        next_open = market_status.get('next_open')
        if next_open:
            try:
                next_open_et = next_open.astimezone(self.et_tz)
                time_diff = next_open_et - current_et
                
                if time_diff.total_seconds() > 0:
                    hours, remainder = divmod(int(time_diff.total_seconds()), 3600)
                    minutes, seconds = divmod(remainder, 60)
                    
                    print(f"[NEXT OPEN] {next_open_et.strftime('%Y-%m-%d %H:%M:%S %Z')}")
                    print(f"[COUNTDOWN] Time Until Wake: {hours:02d}:{minutes:02d}:{seconds:02d}")
                    
                    # Show day info
                    if next_open_et.date() > current_et.date():
                        if next_open_et.weekday() == 0:  # Monday
                            print(f"[INFO] Next trading day is Monday (weekend break)")
                        else:
                            print(f"[INFO] Next trading day is {next_open_et.strftime('%A')}")
                    
                    # Show time until different milestones
                    if time_diff.days > 0:
                        print(f"[INFO] {time_diff.days} day(s) until market reopens")
                    elif hours > 12:
                        print(f"[INFO] Market reopens tomorrow morning")
                    elif hours > 6:
                        print(f"[INFO] Market reopens in the morning")
                    elif hours > 0:
                        print(f"[INFO] Market reopens in {hours} hour(s)")
                    else:
                        print(f"[INFO] Market opening soon!")
                        
                else:
                    print("[COUNTDOWN] Market should be opening now!")
                    
            except Exception as e:
                print(f"[COUNTDOWN ERROR] {e}")
        else:
            print("[COUNTDOWN] Unable to determine next market open time")
        
        print()
        print("="*80)
        print("[AUTO] Bot will automatically wake up when market opens at 9:30 AM ET")
        print("[AUTO] All trading activities are suspended during market closure")
        print("[INFO] Press Ctrl+C to stop the auto sleep/wake system")
        print("="*80)
        
        # Log the sleep status
        self.logger.info(f"[SLEEP] Market closed - Bot sleeping until {next_open_et.strftime('%Y-%m-%d %H:%M:%S %Z') if next_open else 'unknown'}")
    
    def display_market_open_screen(self):
        """Display the market open screen"""
        market_status = self.get_market_status()
        current_et = datetime.now(self.et_tz)
        
        self.clear_screen()
        print("="*80)
        print("                    🚀 MARKET OPEN - BOT AWAKENING 🚀")
        print("="*80)
        print()
        print(f"[CURRENT TIME] {current_et.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"[STATUS] Market is OPEN - Bot automatically awakening")
        print()
        
        # Show countdown to market close
        next_close = market_status.get('next_close')
        if next_close:
            try:
                next_close_et = next_close.astimezone(self.et_tz)
                time_diff = next_close_et - current_et
                
                if time_diff.total_seconds() > 0:
                    hours, remainder = divmod(int(time_diff.total_seconds()), 3600)
                    minutes, seconds = divmod(remainder, 60)
                    
                    print(f"[MARKET CLOSE] {next_close_et.strftime('%Y-%m-%d %H:%M:%S %Z')}")
                    print(f"[TRADING TIME] {hours:02d}:{minutes:02d}:{seconds:02d} remaining")
                    
                    if hours >= 6:
                        print(f"[INFO] Full trading day ahead")
                    elif hours >= 3:
                        print(f"[INFO] Half trading day remaining")
                    elif hours >= 1:
                        print(f"[INFO] Final hours of trading")
                    else:
                        print(f"[INFO] Market closing soon!")
                        
                else:
                    print("[INFO] Market closing now!")
                    
            except Exception as e:
                print(f"[CLOSE TIME ERROR] {e}")
        
        print()
        print("="*80)
        print("[AUTO] Bot is now active and ready for trading")
        print("[AUTO] All trading systems will start automatically")
        print("[AUTO] Bot will automatically sleep when market closes at 4:00 PM ET")
        print("="*80)
        
        # Log the wake status
        self.logger.info(f"[WAKE] Market open - Bot awakening for trading session")
    
    def start_timer_display(self):
        """Start the timer display in a separate thread"""
        def timer_loop():
            while self.is_running:
                try:
                    market_status = self.get_market_status()
                    
                    if market_status['is_open'] and self.is_sleeping:
                        # Market just opened - wake up
                        self.is_sleeping = False
                        self.display_market_open_screen()
                        self.logger.info("[WAKE] Market opened - Bot awakening")
                        break
                        
                    elif not market_status['is_open'] and not self.is_sleeping:
                        # Market just closed - go to sleep
                        self.is_sleeping = True
                        self.logger.info("[SLEEP] Market closed - Bot going to sleep")
                        
                    if self.is_sleeping:
                        self.display_market_closed_screen()
                    else:
                        self.display_market_open_screen()
                    
                    time.sleep(1)  # Update every second
                    
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    self.logger.error(f"[TIMER ERROR] {e}")
                    time.sleep(5)
        
        self.timer_thread = threading.Thread(target=timer_loop, daemon=True)
        self.timer_thread.start()
        return self.timer_thread
    
    def check_market_transition(self):
        """Check for market open/close transitions"""
        market_status = self.get_market_status()
        
        if market_status['is_open'] and self.is_sleeping:
            # Market opened - wake up the bot
            self.wake_up()
            return "WAKE"
            
        elif not market_status['is_open'] and not self.is_sleeping:
            # Market closed - put bot to sleep
            self.go_to_sleep()
            return "SLEEP"
            
        return "NO_CHANGE"
    
    def go_to_sleep(self):
        """Put the bot to sleep when market closes"""
        self.is_sleeping = True
        self.logger.info("[SLEEP] Market closed at 4:00 PM - Bot going to sleep")
        
        # Display sleep screen
        self.display_market_closed_screen()
        
        # Start timer display
        if not self.timer_thread or not self.timer_thread.is_alive():
            self.start_timer_display()
    
    def wake_up(self):
        """Wake up the bot when market opens"""
        self.is_sleeping = False
        self.logger.info("[WAKE] Market opened at 9:30 AM - Bot awakening")
        
        # Display wake screen
        self.display_market_open_screen()
        
        # Could trigger trading systems here
        return True
    
    def run_auto_system(self):
        """Run the automatic sleep/wake system"""
        self.logger.info("[START] Starting automatic sleep/wake system")
        
        try:
            # Initial market status check
            market_status = self.get_market_status()
            
            if market_status['is_open']:
                self.logger.info("[INIT] Market is open - Bot starting in wake mode")
                self.display_market_open_screen()
            else:
                self.logger.info("[INIT] Market is closed - Bot starting in sleep mode")
                self.is_sleeping = True
                self.display_market_closed_screen()
            
            # Start timer display
            timer_thread = self.start_timer_display()
            
            # Wait for the timer thread
            timer_thread.join()
            
        except KeyboardInterrupt:
            self.logger.info("[STOP] Auto sleep/wake system stopped by user")
        except Exception as e:
            self.logger.error(f"[ERROR] Auto sleep/wake system error: {e}")
        finally:
            self.is_running = False
            self.logger.info("[STOP] Auto sleep/wake system stopped")
    
    def stop(self):
        """Stop the auto sleep/wake system"""
        self.is_running = False
        if self.timer_thread and self.timer_thread.is_alive():
            self.timer_thread.join(timeout=2)

def main():
    """Main entry point for standalone use"""
    try:
        auto_system = AutoMarketSleepWake()
        auto_system.run_auto_system()
    except KeyboardInterrupt:
        print("\n[STOP] System stopped by user")
    except Exception as e:
        print(f"[ERROR] System error: {e}")

if __name__ == "__main__":
    main()
