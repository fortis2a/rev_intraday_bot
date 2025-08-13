#!/usr/bin/env python3
"""
Live P&L Monitor - External Window Version
Colorized display with Windows PowerShell color support
"""

import time
import os
import sys
from datetime import datetime
from data_manager import DataManager
from config import config
import colorama
from colorama import Fore, Back, Style

# Initialize colorama for Windows color support
colorama.init(autoreset=True)

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def format_pnl(value):
    """Format P&L with color indicators and icons"""
    if value > 0:
        return f"{Fore.GREEN}{Style.BRIGHT}[^^^] ${value:,.2f} ([^^^] +{value/97299.21*100:.2f}%){Style.RESET_ALL}"
    elif value < 0:
        return f"{Fore.RED}{Style.BRIGHT}[vvv] ${value:,.2f} ([vvv] {value/97299.21*100:.2f}%){Style.RESET_ALL}"
    else:
        return f"{Fore.YELLOW}[---] ${value:,.2f} ([---] 0.00%){Style.RESET_ALL}"

def format_currency(value):
    """Format currency values with icon"""
    return f"{Fore.CYAN}${value:,.2f}{Style.RESET_ALL}"

def get_status_icon(status):
    """Get status icon"""
    if status == "WATCHING":
        return f"{Fore.BLUE}[>>]{Style.RESET_ALL}"
    elif status == "HOLDING":
        return f"{Fore.MAGENTA}[$$]{Style.RESET_ALL}"
    else:
        return f"{Fore.WHITE}[??]{Style.RESET_ALL}"

def get_market_prices(dm, symbols):
    """Get current market prices for symbols"""
    prices = {}
    for symbol in symbols:
        try:
            price = dm.get_current_price(symbol)
            prices[symbol] = price if price else 0.0
        except:
            prices[symbol] = 0.0
    return prices

def display_live_pnl():
    """Display live P&L monitor"""
    try:
        # Initialize data manager
        dm = DataManager()
        
        # Get watchlist from config - use the quantum symbols you specified
        watchlist = ['IONQ', 'PG', 'QBTS', 'RGTI', 'JNJ']
        
        iteration = 0
        
        while True:
            try:
                clear_screen()
                
                # Get current data
                account = dm.get_account_info()
                positions = dm.get_positions()
                market_prices = get_market_prices(dm, watchlist)
                
                if not account:
                    print("[ERROR] Could not retrieve account information")
                    time.sleep(5)
                    continue
                
                # Calculate P&L values
                total_unrealized = sum(pos['unrealized_pl'] for pos in positions)
                equity = account['equity']
                cash = account['cash']
                buying_power = account['buying_power']
                
                # Assume starting equity for P&L calculation
                starting_equity = 97299.21
                daily_pnl = equity - starting_equity
                session_pnl = total_unrealized
                
                # Calculate portfolio utilization
                position_value = sum(abs(pos['market_value']) for pos in positions)
                utilization = (position_value / equity * 100) if equity > 0 else 0
                
                # Count day trades (placeholder)
                day_trades = 0
                
                # Display header
                print(f"{Back.BLUE}{Fore.WHITE}{'='*79}{Style.RESET_ALL}")
                print(f"{Back.BLUE}{Fore.YELLOW}    $$$ COMPLETE LIVE P&L MONITOR - ALPACA DATA $$${Style.RESET_ALL}")
                print(f"{Back.BLUE}{Fore.WHITE}{'='*79}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}[^^^] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ET{Style.RESET_ALL}")
                print(f"{Fore.CYAN}[>>>] Quantum Watchlist: {Fore.WHITE}{', '.join(watchlist)}{Style.RESET_ALL}")
                print(f"{Fore.BLUE}{'='*79}{Style.RESET_ALL}")
                print()
                
                # Account Summary
                print(f"{Back.GREEN}{Fore.BLACK}[$$$] COMPLETE ACCOUNT SUMMARY:{Style.RESET_ALL}")
                print(f"   {Fore.WHITE}[=] Current Equity: {format_currency(equity)}")
                print(f"   {Fore.WHITE}[=] Previous Close: {format_currency(starting_equity)}")
                print(f"   {Fore.WHITE}[=] Cash Available: {format_currency(cash)}")
                print(f"   {Fore.WHITE}[=] Buying Power: {format_currency(buying_power)}")
                print(f"   {Fore.YELLOW}{'~'*64}{Style.RESET_ALL}")
                print(f"   {Fore.WHITE}[^^^] Daily P&L (Total): {format_pnl(daily_pnl)}")
                print(f"   {Fore.WHITE}[>>>] Session P&L: {format_pnl(session_pnl)}")
                print(f"   {Fore.WHITE}[^^^] Long Positions: {format_currency(sum(pos['market_value'] for pos in positions if float(pos['qty']) > 0))}")
                print(f"   {Fore.WHITE}[vvv] Short Positions: {format_currency(sum(pos['market_value'] for pos in positions if float(pos['qty']) < 0))}")
                print(f"   {Fore.WHITE}[<>] Day Trades: {Fore.YELLOW}{day_trades}/3{Style.RESET_ALL}")
                print()
                
                # Enhanced Technical Indicators Display
                print(f"{Back.MAGENTA}{Fore.WHITE}[IND] ENHANCED TECHNICAL INDICATORS:{Style.RESET_ALL}")
                for symbol in watchlist[:3]:  # Show indicators for first 3 symbols
                    try:
                        df = dm.get_bars(symbol, '15Min', limit=30)
                        if not df.empty and len(df) >= 26:
                            df = dm.calculate_indicators(df)
                            latest = df.iloc[-1]
                            
                            rsi_color = Fore.RED if latest['rsi'] > 70 else Fore.GREEN if latest['rsi'] < 30 else Fore.YELLOW
                            macd_color = Fore.GREEN if latest['macd'] > latest['macd_signal'] else Fore.RED
                            vwap_color = Fore.GREEN if latest['price_vs_vwap'] > 0 else Fore.RED
                            
                            print(f"   {Fore.CYAN}[{symbol}] {Fore.WHITE}RSI: {rsi_color}{latest['rsi']:.1f}{Style.RESET_ALL} "
                                  f"{Fore.WHITE}MACD: {macd_color}{latest['macd']:.4f}{Style.RESET_ALL} "
                                  f"{Fore.WHITE}VWAP: {vwap_color}{latest['price_vs_vwap']:.1%}{Style.RESET_ALL}")
                    except:
                        print(f"   {Fore.CYAN}[{symbol}] {Fore.RED}Data unavailable{Style.RESET_ALL}")
                print()
                
                # Position Breakdown
                print(f"{Back.RED}{Fore.WHITE}[***] LIVE POSITION BREAKDOWN:{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}{'~'*79}{Style.RESET_ALL}")
                print(f"{Back.BLACK}{Fore.WHITE}{'Symbol':<8} {'Side':<6} {'Qty':<8} {'Entry$':<10} {'Current$':<10} {'P&L':<15} {'P&L%'}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}{'~'*79}{Style.RESET_ALL}")
                
                # Show positions
                position_dict = {pos['symbol']: pos for pos in positions}
                
                for symbol in watchlist:
                    if symbol in position_dict:
                        pos = position_dict[symbol]
                        qty = float(pos['qty'])
                        side = "LONG" if qty > 0 else "SHORT" if qty < 0 else "--"
                        entry_price = float(pos['avg_entry_price'])
                        current_price = market_prices.get(symbol, 0.0)
                        pnl = float(pos['unrealized_pl'])
                        pnl_pct = (pnl / abs(qty * entry_price) * 100) if entry_price > 0 else 0.0
                        
                        # Color coding for positions
                        side_color = Fore.GREEN if side == "LONG" else Fore.RED if side == "SHORT" else Fore.WHITE
                        pnl_display = format_pnl(pnl)
                        
                        print(f"{Fore.CYAN}{symbol:<8}{Style.RESET_ALL} {side_color}{side:<6}{Style.RESET_ALL} {Fore.WHITE}{abs(qty):<8.0f}{Style.RESET_ALL} {Fore.YELLOW}${entry_price:<9.2f}{Style.RESET_ALL} {Fore.CYAN}${current_price:<9.2f}{Style.RESET_ALL} {pnl_display} {Fore.WHITE}{pnl_pct:>6.2f}%{Style.RESET_ALL}")
                    else:
                        current_price = market_prices.get(symbol, 0.0)
                        print(f"{Fore.CYAN}{symbol:<8}{Style.RESET_ALL} {Fore.WHITE}{'--':<6}{Style.RESET_ALL} {Fore.WHITE}{'--':<8}{Style.RESET_ALL} {Fore.WHITE}{'--':<10}{Style.RESET_ALL} {Fore.CYAN}${current_price:<9.2f}{Style.RESET_ALL} {Fore.BLUE}[>>] {'No Position':<11}{Style.RESET_ALL} {Fore.WHITE}{'--'}{Style.RESET_ALL}")
                
                print(f"{Fore.YELLOW}{'~'*79}{Style.RESET_ALL}")
                print(f"{Back.MAGENTA}{Fore.WHITE}[SUM] TOTALS{'':<50} {format_pnl(total_unrealized)}{Style.RESET_ALL}")
                print()
                
                # P&L Analysis
                print(f"{Back.CYAN}{Fore.BLACK}[###] P&L BREAKDOWN ANALYSIS:{Style.RESET_ALL}")
                print(f"   {Fore.WHITE}[***] Unrealized P&L (Open Positions): {format_pnl(total_unrealized)}")
                print(f"   {Fore.WHITE}[+++] Estimated Realized P&L: {format_pnl(daily_pnl - total_unrealized)}")
                print(f"   {Fore.WHITE}[===] Total Daily P&L: {format_pnl(daily_pnl)}")
                print(f"   {Fore.WHITE}[%%%] Portfolio Utilization: {Fore.YELLOW}{utilization:.1f}%{Style.RESET_ALL}")
                print()
                
                # Current Market Prices
                print(f"{Back.MAGENTA}{Fore.WHITE}[$$$] CURRENT MARKET PRICES:{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}{'~'*58}{Style.RESET_ALL}")
                for symbol in watchlist:
                    price = market_prices.get(symbol, 0.0)
                    status = "WATCHING" if symbol not in position_dict else "HOLDING"
                    status_icon = get_status_icon(status)
                    status_color = Fore.BLUE if status == "WATCHING" else Fore.MAGENTA
                    print(f"{Fore.CYAN}{symbol:<8}{Style.RESET_ALL} {format_currency(price):<12} {status_icon} {status_color}{status}{Style.RESET_ALL}")
                print()
                
                # Footer
                print(f"{Back.GREEN}{Fore.BLACK}[<>] LIVE ALPACA DATA | Updates every 5 seconds{Style.RESET_ALL}")
                print(f"{Back.YELLOW}{Fore.BLACK}[!] Shows COMPLETE P&L: Realized trades + Open positions{Style.RESET_ALL}")
                print(f"{Back.BLUE}{Fore.WHITE}[*] Data source: Alpaca account equity & position tracking{Style.RESET_ALL}")
                print(f"{Fore.RED}{'='*79}{Style.RESET_ALL}")
                print(f"{Back.RED}{Fore.WHITE}[X] Press Ctrl+C to close{Style.RESET_ALL}")
                print(f"{Fore.RED}{'='*79}{Style.RESET_ALL}")
                
                # Update counter
                iteration += 1
                if iteration % 12 == 0:  # Every minute
                    print(f"[INFO] Update #{iteration} - Monitor running normally")
                
                # Wait 5 seconds before next update
                time.sleep(5)
                
            except KeyboardInterrupt:
                print("\n[STOP] Live P&L Monitor stopped by user")
                break
            except Exception as e:
                print(f"[ERROR] Monitor error: {e}")
                print("[INFO] Retrying in 10 seconds...")
                time.sleep(10)
                
    except Exception as e:
        print(f"[ERROR] Failed to initialize P&L monitor: {e}")
        input("Press Enter to close...")

if __name__ == "__main__":
    display_live_pnl()
