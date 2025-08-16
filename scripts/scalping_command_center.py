"""
Scalping Bot Command Center - Professional Desktop GUI
Advanced real-time monitoring with multiple panels and professional interface
"""

import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkFont
from datetime import datetime, timedelta
import threading
import time
import json
import os
import sys
from pathlib import Path
import pandas as pd
import requests
from typing import Dict, List, Optional, Tuple
import logging

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from config import ALPACA_CONFIG, SYMBOLS
from utils.logger import setup_logger
from core.data_manager import DataManager
from core.risk_manager import RiskManager

class ScalpingCommandCenter:
    """Professional desktop application for scalping bot monitoring"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.setup_styles()
        self.setup_variables()
        self.setup_logger()
        self.setup_data_sources()
        self.create_interface()
        self.start_monitoring()
        
    def setup_window(self):
        """Configure main window"""
        self.root.title("🚀 Scalping Bot Command Center v2.0")
        self.root.geometry("1920x1080")  # Full HD optimized
        self.root.configure(bg='#0a0a0a')  # Dark theme
        self.root.state('zoomed')  # Maximize on Windows
        
        # Set window icon and properties
        self.root.resizable(True, True)
        self.root.minsize(1400, 900)
        
        # Handle close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_styles(self):
        """Configure professional dark theme styles"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Dark theme configuration
        self.colors = {
            'bg_primary': '#0a0a0a',      # Main background
            'bg_secondary': '#1a1a1a',    # Panel backgrounds
            'bg_tertiary': '#2a2a2a',     # Widget backgrounds
            'fg_primary': '#ffffff',      # Main text
            'fg_secondary': '#cccccc',    # Secondary text
            'fg_accent': '#00ff88',       # Success/profit color
            'fg_warning': '#ffaa00',      # Warning color
            'fg_danger': '#ff4444',       # Danger/loss color
            'fg_info': '#44aaff',         # Info color
            'border': '#444444'           # Border color
        }
        
        # Configure ttk styles
        self.style.configure('Dark.TFrame', background=self.colors['bg_secondary'])
        self.style.configure('Dark.TLabel', background=self.colors['bg_secondary'], 
                           foreground=self.colors['fg_primary'])
        self.style.configure('Title.TLabel', background=self.colors['bg_secondary'],
                           foreground=self.colors['fg_accent'], font=('Arial', 12, 'bold'))
        self.style.configure('Value.TLabel', background=self.colors['bg_secondary'],
                           foreground=self.colors['fg_accent'], font=('Consolas', 11, 'bold'))
        self.style.configure('Warning.TLabel', background=self.colors['bg_secondary'],
                           foreground=self.colors['fg_warning'], font=('Arial', 10, 'bold'))
        self.style.configure('Danger.TLabel', background=self.colors['bg_secondary'],
                           foreground=self.colors['fg_danger'], font=('Arial', 10, 'bold'))
        
    def setup_variables(self):
        """Initialize data variables"""
        self.is_running = True
        self.refresh_rate = 2  # seconds
        self.last_update = datetime.now()
        
        # Data storage
        self.account_data = {}
        self.positions_data = {}
        self.confidence_data = {}
        self.trade_alerts = []
        self.strategy_performance = {}
        self.market_status = {}
        self.bot_health = {}
        
        # GUI Variables
        self.account_vars = {}
        self.confidence_vars = {}
        self.trade_vars = {}
        self.strategy_vars = {}
        self.market_vars = {}
        
    def setup_logger(self):
        """Initialize logging"""
        self.logger = setup_logger("command_center", "command_center")
        self.logger.info("Scalping Command Center initializing...")
        
    def setup_data_sources(self):
        """Initialize data manager and connections"""
        try:
            self.data_manager = DataManager()
            self.risk_manager = RiskManager()
            self.logger.info("Data sources initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize data sources: {e}")
            messagebox.showerror("Initialization Error", 
                               f"Failed to connect to data sources: {e}")
            
    def create_interface(self):
        """Create the main interface layout"""
        # Main container
        self.main_frame = tk.Frame(self.root, bg=self.colors['bg_primary'])
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create layout sections
        self.create_header()
        self.create_main_content()
        self.create_status_bar()
        
    def create_header(self):
        """Create header with title and system status"""
        header_frame = tk.Frame(self.main_frame, bg=self.colors['bg_secondary'], 
                               relief=tk.RAISED, bd=2)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Title
        title_label = tk.Label(header_frame, text="🚀 SCALPING BOT COMMAND CENTER",
                              font=('Arial', 16, 'bold'), 
                              bg=self.colors['bg_secondary'],
                              fg=self.colors['fg_accent'])
        title_label.pack(side=tk.LEFT, padx=20, pady=10)
        
        # System status
        self.system_status_frame = tk.Frame(header_frame, bg=self.colors['bg_secondary'])
        self.system_status_frame.pack(side=tk.RIGHT, padx=20, pady=10)
        
        self.bot_status_var = tk.StringVar(value="🟡 INITIALIZING")
        self.market_status_var = tk.StringVar(value="📊 LOADING")
        self.connection_status_var = tk.StringVar(value="🔌 CONNECTING")
        
        tk.Label(self.system_status_frame, textvariable=self.bot_status_var,
                font=('Arial', 10, 'bold'), bg=self.colors['bg_secondary'],
                fg=self.colors['fg_primary']).pack(anchor=tk.E)
        tk.Label(self.system_status_frame, textvariable=self.market_status_var,
                font=('Arial', 10, 'bold'), bg=self.colors['bg_secondary'],
                fg=self.colors['fg_primary']).pack(anchor=tk.E)
        tk.Label(self.system_status_frame, textvariable=self.connection_status_var,
                font=('Arial', 10, 'bold'), bg=self.colors['bg_secondary'],
                fg=self.colors['fg_primary']).pack(anchor=tk.E)
        
    def create_main_content(self):
        """Create main content area with multiple panels"""
        content_frame = tk.Frame(self.main_frame, bg=self.colors['bg_primary'])
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Top row - Account & P&L Summary
        self.create_account_panel(content_frame)
        
        # Middle row - Three main panels
        middle_frame = tk.Frame(content_frame, bg=self.colors['bg_primary'])
        middle_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.create_confidence_panel(middle_frame)
        self.create_trade_execution_panel(middle_frame)
        self.create_strategy_performance_panel(middle_frame)
        
        # Bottom row - Market Status & Bot Health
        bottom_frame = tk.Frame(content_frame, bg=self.colors['bg_primary'])
        bottom_frame.pack(fill=tk.X, pady=10)
        
        self.create_market_status_panel(bottom_frame)
        self.create_bot_health_panel(bottom_frame)
        
    def create_account_panel(self, parent):
        """Create account and P&L summary panel"""
        panel = ttk.LabelFrame(parent, text="💰 ACCOUNT & P&L SUMMARY", 
                              style='Dark.TFrame')
        panel.pack(fill=tk.X, pady=(0, 10))
        
        # Create grid layout for account metrics
        metrics_frame = tk.Frame(panel, bg=self.colors['bg_secondary'])
        metrics_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Account metrics
        self.account_vars = {
            'equity': tk.StringVar(value="$0.00"),
            'cash': tk.StringVar(value="$0.00"),
            'day_pnl': tk.StringVar(value="$0.00"),
            'unrealized_pnl': tk.StringVar(value="$0.00"),
            'realized_pnl': tk.StringVar(value="$0.00"),
            'buying_power': tk.StringVar(value="$0.00"),
            'positions': tk.StringVar(value="0"),
            'trades_today': tk.StringVar(value="0")
        }
        
        # Layout account metrics in 4x2 grid
        metrics = [
            ("Account Equity", self.account_vars['equity']),
            ("Available Cash", self.account_vars['cash']),
            ("Day P&L", self.account_vars['day_pnl']),
            ("Unrealized P&L", self.account_vars['unrealized_pnl']),
            ("Realized P&L", self.account_vars['realized_pnl']),
            ("Buying Power", self.account_vars['buying_power']),
            ("Open Positions", self.account_vars['positions']),
            ("Trades Today", self.account_vars['trades_today'])
        ]
        
        for i, (label, var) in enumerate(metrics):
            row = i // 4
            col = i % 4
            
            metric_frame = tk.Frame(metrics_frame, bg=self.colors['bg_tertiary'], 
                                  relief=tk.RAISED, bd=1)
            metric_frame.grid(row=row, column=col, padx=5, pady=5, sticky=tk.EW)
            
            tk.Label(metric_frame, text=label, font=('Arial', 9),
                    bg=self.colors['bg_tertiary'], fg=self.colors['fg_secondary']).pack()
            tk.Label(metric_frame, textvariable=var, font=('Consolas', 12, 'bold'),
                    bg=self.colors['bg_tertiary'], fg=self.colors['fg_accent']).pack()
            
        # Configure grid weights
        for i in range(4):
            metrics_frame.grid_columnconfigure(i, weight=1)
            
    def create_confidence_panel(self, parent):
        """Create confidence monitoring panel"""
        panel = ttk.LabelFrame(parent, text="🎯 CONFIDENCE MONITOR", 
                              style='Dark.TFrame')
        panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Create scrollable frame for symbols
        canvas = tk.Canvas(panel, bg=self.colors['bg_secondary'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(panel, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg_secondary'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create confidence entries for each symbol
        self.confidence_vars = {}
        for symbol in SYMBOLS:
            self.confidence_vars[symbol] = {
                'confidence': tk.StringVar(value="0%"),
                'signal': tk.StringVar(value="HOLD"),
                'price': tk.StringVar(value="$0.00"),
                'change': tk.StringVar(value="0.00%")
            }
            
            symbol_frame = tk.Frame(scrollable_frame, bg=self.colors['bg_tertiary'],
                                  relief=tk.RAISED, bd=1)
            symbol_frame.pack(fill=tk.X, padx=5, pady=2)
            
            # Symbol header
            header = tk.Frame(symbol_frame, bg=self.colors['bg_tertiary'])
            header.pack(fill=tk.X, padx=5, pady=2)
            
            tk.Label(header, text=symbol, font=('Arial', 10, 'bold'),
                    bg=self.colors['bg_tertiary'], fg=self.colors['fg_primary']).pack(side=tk.LEFT)
            tk.Label(header, textvariable=self.confidence_vars[symbol]['price'],
                    font=('Consolas', 9), bg=self.colors['bg_tertiary'],
                    fg=self.colors['fg_secondary']).pack(side=tk.RIGHT)
            
            # Metrics row
            metrics = tk.Frame(symbol_frame, bg=self.colors['bg_tertiary'])
            metrics.pack(fill=tk.X, padx=5, pady=(0, 5))
            
            tk.Label(metrics, textvariable=self.confidence_vars[symbol]['confidence'],
                    font=('Consolas', 11, 'bold'), bg=self.colors['bg_tertiary'],
                    fg=self.colors['fg_accent']).pack(side=tk.LEFT)
            tk.Label(metrics, textvariable=self.confidence_vars[symbol]['signal'],
                    font=('Arial', 9, 'bold'), bg=self.colors['bg_tertiary'],
                    fg=self.colors['fg_info']).pack(side=tk.LEFT, padx=(10, 0))
            tk.Label(metrics, textvariable=self.confidence_vars[symbol]['change'],
                    font=('Consolas', 9), bg=self.colors['bg_tertiary'],
                    fg=self.colors['fg_secondary']).pack(side=tk.RIGHT)
        
    def create_trade_execution_panel(self, parent):
        """Create trade execution and alerts panel"""
        panel = ttk.LabelFrame(parent, text="⚡ TRADE EXECUTION & ALERTS", 
                              style='Dark.TFrame')
        panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Trade log
        log_frame = tk.Frame(panel, bg=self.colors['bg_secondary'])
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create treeview for trade log
        columns = ("Time", "Symbol", "Action", "Qty", "Price", "P&L", "Strategy")
        self.trade_tree = ttk.Treeview(log_frame, columns=columns, show="headings",
                                      height=15)
        
        # Configure columns
        column_widths = {"Time": 80, "Symbol": 60, "Action": 50, "Qty": 50, 
                        "Price": 70, "P&L": 70, "Strategy": 100}
        
        for col in columns:
            self.trade_tree.heading(col, text=col)
            self.trade_tree.column(col, width=column_widths.get(col, 80), minwidth=50)
        
        # Scrollbars for trade log
        trade_v_scroll = ttk.Scrollbar(log_frame, orient="vertical", 
                                      command=self.trade_tree.yview)
        trade_h_scroll = ttk.Scrollbar(log_frame, orient="horizontal", 
                                      command=self.trade_tree.xview)
        
        self.trade_tree.configure(yscrollcommand=trade_v_scroll.set,
                                 xscrollcommand=trade_h_scroll.set)
        
        self.trade_tree.pack(side="left", fill="both", expand=True)
        trade_v_scroll.pack(side="right", fill="y")
        trade_h_scroll.pack(side="bottom", fill="x")
        
        # Trade summary at bottom
        summary_frame = tk.Frame(panel, bg=self.colors['bg_tertiary'], 
                                relief=tk.RAISED, bd=1)
        summary_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.trade_vars = {
            'total_trades': tk.StringVar(value="0"),
            'winning_trades': tk.StringVar(value="0"),
            'losing_trades': tk.StringVar(value="0"),
            'win_rate': tk.StringVar(value="0%"),
            'avg_win': tk.StringVar(value="$0.00"),
            'avg_loss': tk.StringVar(value="$0.00")
        }
        
        # Layout trade summary
        summary_items = [
            ("Total Trades", self.trade_vars['total_trades']),
            ("Wins", self.trade_vars['winning_trades']),
            ("Losses", self.trade_vars['losing_trades']),
            ("Win Rate", self.trade_vars['win_rate']),
            ("Avg Win", self.trade_vars['avg_win']),
            ("Avg Loss", self.trade_vars['avg_loss'])
        ]
        
        for i, (label, var) in enumerate(summary_items):
            item_frame = tk.Frame(summary_frame, bg=self.colors['bg_tertiary'])
            item_frame.grid(row=i//3, column=i%3, padx=5, pady=2, sticky=tk.EW)
            
            tk.Label(item_frame, text=label, font=('Arial', 8),
                    bg=self.colors['bg_tertiary'], fg=self.colors['fg_secondary']).pack()
            tk.Label(item_frame, textvariable=var, font=('Consolas', 9, 'bold'),
                    bg=self.colors['bg_tertiary'], fg=self.colors['fg_accent']).pack()
            
        for i in range(3):
            summary_frame.grid_columnconfigure(i, weight=1)
        
    def create_strategy_performance_panel(self, parent):
        """Create strategy performance and risk panel"""
        panel = ttk.LabelFrame(parent, text="📊 STRATEGY PERFORMANCE & RISK", 
                              style='Dark.TFrame')
        panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Strategy performance
        perf_frame = tk.Frame(panel, bg=self.colors['bg_secondary'])
        perf_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Strategy metrics
        strategies = ["Mean Reversion", "Momentum Scalp", "VWAP Bounce"]
        self.strategy_vars = {}
        
        for i, strategy in enumerate(strategies):
            self.strategy_vars[strategy] = {
                'trades': tk.StringVar(value="0"),
                'pnl': tk.StringVar(value="$0.00"),
                'win_rate': tk.StringVar(value="0%"),
                'status': tk.StringVar(value="INACTIVE")
            }
            
            strat_frame = tk.Frame(perf_frame, bg=self.colors['bg_tertiary'],
                                  relief=tk.RAISED, bd=1)
            strat_frame.pack(fill=tk.X, pady=2)
            
            # Strategy header
            header = tk.Frame(strat_frame, bg=self.colors['bg_tertiary'])
            header.pack(fill=tk.X, padx=5, pady=2)
            
            tk.Label(header, text=strategy, font=('Arial', 10, 'bold'),
                    bg=self.colors['bg_tertiary'], fg=self.colors['fg_primary']).pack(side=tk.LEFT)
            tk.Label(header, textvariable=self.strategy_vars[strategy]['status'],
                    font=('Arial', 8, 'bold'), bg=self.colors['bg_tertiary'],
                    fg=self.colors['fg_info']).pack(side=tk.RIGHT)
            
            # Strategy metrics
            metrics = tk.Frame(strat_frame, bg=self.colors['bg_tertiary'])
            metrics.pack(fill=tk.X, padx=5, pady=(0, 5))
            
            tk.Label(metrics, textvariable=self.strategy_vars[strategy]['trades'],
                    font=('Consolas', 9), bg=self.colors['bg_tertiary'],
                    fg=self.colors['fg_secondary']).pack(side=tk.LEFT)
            tk.Label(metrics, textvariable=self.strategy_vars[strategy]['pnl'],
                    font=('Consolas', 9, 'bold'), bg=self.colors['bg_tertiary'],
                    fg=self.colors['fg_accent']).pack(side=tk.LEFT, padx=(10, 0))
            tk.Label(metrics, textvariable=self.strategy_vars[strategy]['win_rate'],
                    font=('Consolas', 9), bg=self.colors['bg_tertiary'],
                    fg=self.colors['fg_info']).pack(side=tk.RIGHT)
        
        # Risk metrics
        risk_frame = tk.Frame(panel, bg=self.colors['bg_tertiary'], 
                             relief=tk.RAISED, bd=1)
        risk_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(risk_frame, text="⚠️ RISK METRICS", font=('Arial', 10, 'bold'),
                bg=self.colors['bg_tertiary'], fg=self.colors['fg_warning']).pack(pady=5)
        
        self.risk_vars = {
            'portfolio_risk': tk.StringVar(value="0%"),
            'max_drawdown': tk.StringVar(value="0%"),
            'var_1d': tk.StringVar(value="$0.00"),
            'exposure': tk.StringVar(value="0%")
        }
        
        risk_items = [
            ("Portfolio Risk", self.risk_vars['portfolio_risk']),
            ("Max Drawdown", self.risk_vars['max_drawdown']),
            ("VaR (1-Day)", self.risk_vars['var_1d']),
            ("Total Exposure", self.risk_vars['exposure'])
        ]
        
        for i, (label, var) in enumerate(risk_items):
            item_frame = tk.Frame(risk_frame, bg=self.colors['bg_tertiary'])
            item_frame.grid(row=i//2, column=i%2, padx=5, pady=2, sticky=tk.EW)
            
            tk.Label(item_frame, text=label, font=('Arial', 8),
                    bg=self.colors['bg_tertiary'], fg=self.colors['fg_secondary']).pack()
            tk.Label(item_frame, textvariable=var, font=('Consolas', 9, 'bold'),
                    bg=self.colors['bg_tertiary'], fg=self.colors['fg_warning']).pack()
            
        for i in range(2):
            risk_frame.grid_columnconfigure(i, weight=1)
            
    def create_market_status_panel(self, parent):
        """Create market status panel"""
        panel = ttk.LabelFrame(parent, text="📈 MARKET STATUS", 
                              style='Dark.TFrame')
        panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        status_frame = tk.Frame(panel, bg=self.colors['bg_secondary'])
        status_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.market_vars = {
            'session_status': tk.StringVar(value="CLOSED"),
            'time_to_open': tk.StringVar(value="--:--:--"),
            'spy_price': tk.StringVar(value="$0.00"),
            'spy_change': tk.StringVar(value="0.00%"),
            'vix_level': tk.StringVar(value="0.00"),
            'volume_profile': tk.StringVar(value="NORMAL")
        }
        
        market_items = [
            ("Session", self.market_vars['session_status']),
            ("Time to Open", self.market_vars['time_to_open']),
            ("SPY Price", self.market_vars['spy_price']),
            ("SPY Change", self.market_vars['spy_change']),
            ("VIX Level", self.market_vars['vix_level']),
            ("Volume", self.market_vars['volume_profile'])
        ]
        
        for i, (label, var) in enumerate(market_items):
            item_frame = tk.Frame(status_frame, bg=self.colors['bg_tertiary'],
                                 relief=tk.RAISED, bd=1)
            item_frame.grid(row=i//3, column=i%3, padx=2, pady=2, sticky=tk.EW)
            
            tk.Label(item_frame, text=label, font=('Arial', 9),
                    bg=self.colors['bg_tertiary'], fg=self.colors['fg_secondary']).pack()
            tk.Label(item_frame, textvariable=var, font=('Consolas', 10, 'bold'),
                    bg=self.colors['bg_tertiary'], fg=self.colors['fg_accent']).pack()
            
        for i in range(3):
            status_frame.grid_columnconfigure(i, weight=1)
            
    def create_bot_health_panel(self, parent):
        """Create bot health monitoring panel"""
        panel = ttk.LabelFrame(parent, text="🤖 BOT HEALTH", 
                              style='Dark.TFrame')
        panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        health_frame = tk.Frame(panel, bg=self.colors['bg_secondary'])
        health_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.health_vars = {
            'uptime': tk.StringVar(value="00:00:00"),
            'cpu_usage': tk.StringVar(value="0%"),
            'memory_usage': tk.StringVar(value="0%"),
            'api_latency': tk.StringVar(value="0ms"),
            'data_feeds': tk.StringVar(value="0/5"),
            'last_signal': tk.StringVar(value="Never")
        }
        
        health_items = [
            ("Uptime", self.health_vars['uptime']),
            ("CPU Usage", self.health_vars['cpu_usage']),
            ("Memory", self.health_vars['memory_usage']),
            ("API Latency", self.health_vars['api_latency']),
            ("Data Feeds", self.health_vars['data_feeds']),
            ("Last Signal", self.health_vars['last_signal'])
        ]
        
        for i, (label, var) in enumerate(health_items):
            item_frame = tk.Frame(health_frame, bg=self.colors['bg_tertiary'],
                                 relief=tk.RAISED, bd=1)
            item_frame.grid(row=i//3, column=i%3, padx=2, pady=2, sticky=tk.EW)
            
            tk.Label(item_frame, text=label, font=('Arial', 9),
                    bg=self.colors['bg_tertiary'], fg=self.colors['fg_secondary']).pack()
            tk.Label(item_frame, textvariable=var, font=('Consolas', 10, 'bold'),
                    bg=self.colors['bg_tertiary'], fg=self.colors['fg_info']).pack()
            
        for i in range(3):
            health_frame.grid_columnconfigure(i, weight=1)
            
    def create_status_bar(self):
        """Create status bar at bottom"""
        status_frame = tk.Frame(self.main_frame, bg=self.colors['bg_tertiary'],
                               relief=tk.SUNKEN, bd=1)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_var = tk.StringVar(value="🚀 Command Center initialized - Ready for monitoring")
        self.update_time_var = tk.StringVar(value="Last Update: Never")
        
        tk.Label(status_frame, textvariable=self.status_var, 
                font=('Arial', 9), bg=self.colors['bg_tertiary'],
                fg=self.colors['fg_secondary']).pack(side=tk.LEFT, padx=10, pady=5)
        tk.Label(status_frame, textvariable=self.update_time_var,
                font=('Arial', 9), bg=self.colors['bg_tertiary'],
                fg=self.colors['fg_secondary']).pack(side=tk.RIGHT, padx=10, pady=5)
        
    def start_monitoring(self):
        """Start background monitoring threads"""
        self.start_time = datetime.now()
        
        # Start data update thread
        self.update_thread = threading.Thread(target=self.update_loop, daemon=True)
        self.update_thread.start()
        
        # Start GUI update timer
        self.schedule_gui_update()
        
        self.logger.info("Monitoring started successfully")
        
    def update_loop(self):
        """Main data update loop running in background thread"""
        while self.is_running:
            try:
                self.fetch_account_data()
                self.fetch_confidence_data()
                self.fetch_trade_data()
                self.fetch_strategy_performance()
                self.fetch_market_status()
                self.fetch_bot_health()
                
                self.last_update = datetime.now()
                
            except Exception as e:
                self.logger.error(f"Error in update loop: {e}")
                
            time.sleep(self.refresh_rate)
            
    def fetch_account_data(self):
        """Fetch account and P&L data"""
        try:
            # This would connect to Alpaca API in real implementation
            # For now, simulate some data
            import random
            
            base_equity = 50000
            day_change = random.uniform(-500, 500)
            
            self.account_data = {
                'equity': base_equity + day_change,
                'cash': base_equity * 0.3,
                'day_pnl': day_change,
                'unrealized_pnl': random.uniform(-200, 200),
                'realized_pnl': day_change - random.uniform(-50, 50),
                'buying_power': base_equity * 4,
                'positions': random.randint(0, 5),
                'trades_today': random.randint(0, 20)
            }
            
        except Exception as e:
            self.logger.error(f"Error fetching account data: {e}")
            
    def fetch_confidence_data(self):
        """Fetch confidence and signal data"""
        try:
            import random
            
            for symbol in SYMBOLS:
                confidence = random.uniform(0, 100)
                price_change = random.uniform(-3, 3)
                
                # Determine signal based on confidence
                if confidence > 75:
                    signal = "BUY" if random.random() > 0.5 else "SELL"
                elif confidence > 60:
                    signal = "WATCH"
                else:
                    signal = "HOLD"
                    
                self.confidence_data[symbol] = {
                    'confidence': confidence,
                    'signal': signal,
                    'price': random.uniform(50, 500),
                    'change': price_change
                }
                
        except Exception as e:
            self.logger.error(f"Error fetching confidence data: {e}")
            
    def fetch_trade_data(self):
        """Fetch recent trade execution data"""
        try:
            # Read from trade logs or simulate
            import random
            
            # Simulate some trade data
            if random.random() < 0.1:  # 10% chance of new trade
                trade = {
                    'time': datetime.now().strftime("%H:%M:%S"),
                    'symbol': random.choice(SYMBOLS),
                    'action': random.choice(['BUY', 'SELL']),
                    'quantity': random.randint(10, 100),
                    'price': random.uniform(50, 500),
                    'pnl': random.uniform(-50, 100),
                    'strategy': random.choice(['Mean Reversion', 'Momentum', 'VWAP'])
                }
                self.trade_alerts.append(trade)
                
                # Keep only last 50 trades
                if len(self.trade_alerts) > 50:
                    self.trade_alerts = self.trade_alerts[-50:]
                    
        except Exception as e:
            self.logger.error(f"Error fetching trade data: {e}")
            
    def fetch_strategy_performance(self):
        """Fetch strategy performance metrics"""
        try:
            import random
            
            strategies = ["Mean Reversion", "Momentum Scalp", "VWAP Bounce"]
            
            for strategy in strategies:
                self.strategy_performance[strategy] = {
                    'trades': random.randint(0, 10),
                    'pnl': random.uniform(-200, 300),
                    'win_rate': random.uniform(40, 80),
                    'status': random.choice(['ACTIVE', 'INACTIVE', 'PAUSED'])
                }
                
        except Exception as e:
            self.logger.error(f"Error fetching strategy performance: {e}")
            
    def fetch_market_status(self):
        """Fetch market status and conditions"""
        try:
            import random
            from datetime import time
            
            now = datetime.now()
            market_open = time(9, 30)
            market_close = time(16, 0)
            current_time = now.time()
            
            if market_open <= current_time <= market_close and now.weekday() < 5:
                session_status = "OPEN"
                time_to_open = "Market Open"
            else:
                session_status = "CLOSED"
                # Calculate time to next open
                time_to_open = "06:30:00"  # Simplified
                
            self.market_status = {
                'session_status': session_status,
                'time_to_open': time_to_open,
                'spy_price': random.uniform(400, 450),
                'spy_change': random.uniform(-2, 2),
                'vix_level': random.uniform(15, 30),
                'volume_profile': random.choice(['LOW', 'NORMAL', 'HIGH'])
            }
            
        except Exception as e:
            self.logger.error(f"Error fetching market status: {e}")
            
    def fetch_bot_health(self):
        """Fetch bot health metrics"""
        try:
            import psutil
            import random
            
            uptime = datetime.now() - self.start_time
            uptime_str = str(uptime).split('.')[0]  # Remove microseconds
            
            self.bot_health = {
                'uptime': uptime_str,
                'cpu_usage': psutil.cpu_percent(),
                'memory_usage': psutil.virtual_memory().percent,
                'api_latency': random.randint(10, 100),
                'data_feeds': f"{random.randint(4, 5)}/5",
                'last_signal': "2 min ago"
            }
            
        except Exception as e:
            self.logger.error(f"Error fetching bot health: {e}")
            
    def schedule_gui_update(self):
        """Schedule periodic GUI updates"""
        if self.is_running:
            self.update_gui()
            self.root.after(1000, self.schedule_gui_update)  # Update every second
            
    def update_gui(self):
        """Update all GUI elements with latest data"""
        try:
            self.update_account_display()
            self.update_confidence_display()
            self.update_trade_display()
            self.update_strategy_display()
            self.update_market_display()
            self.update_health_display()
            self.update_status_display()
            
        except Exception as e:
            self.logger.error(f"Error updating GUI: {e}")
            
    def update_account_display(self):
        """Update account panel"""
        if self.account_data:
            self.account_vars['equity'].set(f"${self.account_data['equity']:,.2f}")
            self.account_vars['cash'].set(f"${self.account_data['cash']:,.2f}")
            
            day_pnl = self.account_data['day_pnl']
            pnl_color = self.colors['fg_accent'] if day_pnl >= 0 else self.colors['fg_danger']
            self.account_vars['day_pnl'].set(f"${day_pnl:+.2f}")
            
            unrealized = self.account_data['unrealized_pnl']
            self.account_vars['unrealized_pnl'].set(f"${unrealized:+.2f}")
            
            realized = self.account_data['realized_pnl']
            self.account_vars['realized_pnl'].set(f"${realized:+.2f}")
            
            self.account_vars['buying_power'].set(f"${self.account_data['buying_power']:,.0f}")
            self.account_vars['positions'].set(str(self.account_data['positions']))
            self.account_vars['trades_today'].set(str(self.account_data['trades_today']))
            
    def update_confidence_display(self):
        """Update confidence panel"""
        for symbol, data in self.confidence_data.items():
            if symbol in self.confidence_vars:
                self.confidence_vars[symbol]['confidence'].set(f"{data['confidence']:.1f}%")
                self.confidence_vars[symbol]['signal'].set(data['signal'])
                self.confidence_vars[symbol]['price'].set(f"${data['price']:.2f}")
                
                change = data['change']
                change_text = f"{change:+.2f}%"
                self.confidence_vars[symbol]['change'].set(change_text)
                
    def update_trade_display(self):
        """Update trade execution panel"""
        # Clear existing items
        for item in self.trade_tree.get_children():
            self.trade_tree.delete(item)
            
        # Add recent trades
        for trade in self.trade_alerts[-20:]:  # Show last 20 trades
            values = (
                trade['time'],
                trade['symbol'],
                trade['action'],
                trade['quantity'],
                f"${trade['price']:.2f}",
                f"${trade['pnl']:+.2f}",
                trade['strategy']
            )
            
            item = self.trade_tree.insert("", 0, values=values)
            
            # Color code based on P&L
            if trade['pnl'] > 0:
                self.trade_tree.set(item, "P&L", f"+${trade['pnl']:.2f}")
            else:
                self.trade_tree.set(item, "P&L", f"-${abs(trade['pnl']):.2f}")
                
        # Update trade summary
        if self.trade_alerts:
            total_trades = len(self.trade_alerts)
            winning_trades = sum(1 for t in self.trade_alerts if t['pnl'] > 0)
            losing_trades = total_trades - winning_trades
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
            
            wins = [t['pnl'] for t in self.trade_alerts if t['pnl'] > 0]
            losses = [t['pnl'] for t in self.trade_alerts if t['pnl'] <= 0]
            
            avg_win = sum(wins) / len(wins) if wins else 0
            avg_loss = sum(losses) / len(losses) if losses else 0
            
            self.trade_vars['total_trades'].set(str(total_trades))
            self.trade_vars['winning_trades'].set(str(winning_trades))
            self.trade_vars['losing_trades'].set(str(losing_trades))
            self.trade_vars['win_rate'].set(f"{win_rate:.1f}%")
            self.trade_vars['avg_win'].set(f"${avg_win:.2f}")
            self.trade_vars['avg_loss'].set(f"${avg_loss:.2f}")
            
    def update_strategy_display(self):
        """Update strategy performance panel"""
        for strategy, data in self.strategy_performance.items():
            if strategy in self.strategy_vars:
                self.strategy_vars[strategy]['trades'].set(f"{data['trades']} trades")
                
                pnl = data['pnl']
                pnl_text = f"${pnl:+.2f}"
                self.strategy_vars[strategy]['pnl'].set(pnl_text)
                
                self.strategy_vars[strategy]['win_rate'].set(f"{data['win_rate']:.1f}%")
                self.strategy_vars[strategy]['status'].set(data['status'])
                
    def update_market_display(self):
        """Update market status panel"""
        if self.market_status:
            self.market_vars['session_status'].set(self.market_status['session_status'])
            self.market_vars['time_to_open'].set(self.market_status['time_to_open'])
            self.market_vars['spy_price'].set(f"${self.market_status['spy_price']:.2f}")
            
            spy_change = self.market_status['spy_change']
            self.market_vars['spy_change'].set(f"{spy_change:+.2f}%")
            
            self.market_vars['vix_level'].set(f"{self.market_status['vix_level']:.2f}")
            self.market_vars['volume_profile'].set(self.market_status['volume_profile'])
            
    def update_health_display(self):
        """Update bot health panel"""
        if self.bot_health:
            self.health_vars['uptime'].set(self.bot_health['uptime'])
            self.health_vars['cpu_usage'].set(f"{self.bot_health['cpu_usage']:.1f}%")
            self.health_vars['memory_usage'].set(f"{self.bot_health['memory_usage']:.1f}%")
            self.health_vars['api_latency'].set(f"{self.bot_health['api_latency']}ms")
            self.health_vars['data_feeds'].set(self.bot_health['data_feeds'])
            self.health_vars['last_signal'].set(self.bot_health['last_signal'])
            
    def update_status_display(self):
        """Update status bar"""
        # Update system status
        if self.market_status.get('session_status') == 'OPEN':
            self.bot_status_var.set("🟢 ACTIVE")
            self.market_status_var.set("📊 MARKET OPEN")
        else:
            self.bot_status_var.set("🟡 STANDBY")
            self.market_status_var.set("📊 MARKET CLOSED")
            
        self.connection_status_var.set("🟢 CONNECTED")
        
        # Update status bar
        current_time = datetime.now().strftime("%H:%M:%S")
        self.update_time_var.set(f"Last Update: {current_time}")
        
        if self.is_running:
            self.status_var.set("🚀 Command Center active - Monitoring all systems")
        else:
            self.status_var.set("⚠️ Command Center shutting down...")
            
    def on_closing(self):
        """Handle application close"""
        self.logger.info("Command Center shutting down...")
        self.is_running = False
        
        # Give threads time to clean up
        time.sleep(1)
        
        self.root.destroy()
        
    def run(self):
        """Start the application"""
        self.logger.info("Starting Scalping Command Center...")
        self.status_var.set("🚀 Command Center starting...")
        self.root.mainloop()

def main():
    """Main entry point"""
    try:
        app = ScalpingCommandCenter()
        app.run()
    except Exception as e:
        print(f"Failed to start Command Center: {e}")
        logging.error(f"Failed to start Command Center: {e}")

if __name__ == "__main__":
    main()
