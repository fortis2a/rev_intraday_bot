#!/usr/bin/env python3
"""
📊 Live Stock Performance Dashboard
Real-time monitoring dashboard for watchlist performance analysis
"""

import sys
import time
import os
from datetime import datetime, timedelta
from pathlib import Path
import json

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from stock_performance_monitor import StockPerformanceMonitor

class LiveStockDashboard:
    """Live dashboard for stock performance monitoring"""
    
    def __init__(self):
        self.monitor = StockPerformanceMonitor()
        self.last_update = None
        self.analysis_history = []
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_header(self):
        """Display dashboard header"""
        now = datetime.now()
        print("╔" + "═" * 78 + "╗")
        print("║" + " " * 15 + "📊 LIVE STOCK PERFORMANCE DASHBOARD" + " " * 25 + "║")
        print("║" + f" Time: {now.strftime('%Y-%m-%d %H:%M:%S')}" + " " * 45 + "║")
        print("║" + f" Watchlist: IONQ, PG, QBTS, RGTI, JNJ" + " " * 33 + "║")
        print("╚" + "═" * 78 + "╝")
    
    def display_quick_stats(self, analysis: dict):
        """Display quick performance statistics"""
        print("\n📈 QUICK PERFORMANCE OVERVIEW")
        print("─" * 50)
        
        for symbol in self.monitor.watchlist:
            if symbol in analysis and '1D' in analysis[symbol]:
                data_1d = analysis[symbol]['1D']
                data_5d = analysis[symbol].get('5D', {})
                
                price = data_1d.get('current_price', 0)
                return_1d = data_1d.get('total_return_pct', 0)
                return_5d = data_5d.get('total_return_pct', 0)
                volatility = data_1d.get('volatility_pct', 0)
                
                # Color coding for returns
                color_1d = "🟢" if return_1d > 0 else "🔴" if return_1d < 0 else "⚪"
                color_5d = "🟢" if return_5d > 0 else "🔴" if return_5d < 0 else "⚪"
                
                print(f"{symbol:>5} │ ${price:7.2f} │ {color_1d} {return_1d:+6.1f}% │ {color_5d} {return_5d:+6.1f}% │ Vol: {volatility:4.1f}%")
        
        print("─" * 50)
        print("      │   Price   │  1-Day   │  5-Day   │ Volatility")
    
    def display_strategy_recommendations(self, analysis: dict):
        """Display trading strategy recommendations"""
        print("\n🎯 STRATEGY RECOMMENDATIONS")
        print("─" * 65)
        
        day_trading = []
        swing_trading = []
        position_trading = []
        
        for symbol in self.monitor.watchlist:
            if symbol in analysis and 'trading_analysis' in analysis[symbol]:
                ta = analysis[symbol]['trading_analysis']
                best_strategy = ta.get('best_strategy', 'Unknown')
                score = ta.get('strategy_score', 0)
                risk = ta.get('risk_level', 'Unknown')
                
                symbol_info = f"{symbol} (Score: {score}/4, Risk: {risk})"
                
                if best_strategy == 'day_trading' and score >= 3:
                    day_trading.append(symbol_info)
                elif best_strategy == 'swing_trading' and score >= 2:
                    swing_trading.append(symbol_info)
                elif best_strategy == 'position_trading' and score >= 2:
                    position_trading.append(symbol_info)
        
        print(f"🚀 Day Trading:    {', '.join(day_trading) if day_trading else 'None suitable'}")
        print(f"📈 Swing Trading:  {', '.join(swing_trading) if swing_trading else 'None suitable'}")
        print(f"🏦 Position:       {', '.join(position_trading) if position_trading else 'None suitable'}")
        
        # PDT Compliance suggestion
        total_active = len(day_trading) + len(swing_trading)
        print(f"\n💡 PDT Compliance: ", end="")
        if total_active >= 3:
            print("✅ Good for selective day trading (3 trades/week)")
        elif total_active >= 1:
            print("📊 Consider swing trading approach")
        else:
            print("⏳ Limited opportunities - wait for better setups")
    
    def display_detailed_analysis(self, analysis: dict):
        """Display detailed analysis for each stock"""
        print("\n📊 DETAILED STOCK ANALYSIS")
        print("═" * 80)
        
        for symbol in self.monitor.watchlist:
            if symbol not in analysis:
                continue
                
            print(f"\n🔍 {symbol} Analysis:")
            print("─" * 40)
            
            # Multi-timeframe view
            timeframes = ['1D', '5D', '30D']
            for tf in timeframes:
                if tf in analysis[symbol]:
                    data = analysis[symbol][tf]
                    ret = data.get('total_return_pct', 0)
                    vol = data.get('volatility_pct', 0)
                    volume_trend = data.get('volume_trend_pct', 0)
                    
                    ret_color = "🟢" if ret > 0 else "🔴" if ret < 0 else "⚪"
                    vol_status = "High" if vol > 25 else "Med" if vol > 15 else "Low"
                    
                    print(f"  {tf:>3}: {ret_color} {ret:+6.1f}% │ Vol: {vol:4.1f}% ({vol_status}) │ Volume: {volume_trend:+4.0f}%")
            
            # Trading recommendation
            if 'trading_analysis' in analysis[symbol]:
                ta = analysis[symbol]['trading_analysis']
                print(f"  💡 Best: {ta.get('best_strategy', 'N/A')} │ Risk: {ta.get('risk_level', 'N/A')}")
                print(f"  📝 {ta.get('recommendation', 'No recommendation')}")
    
    def display_market_summary(self, analysis: dict):
        """Display overall market conditions summary"""
        print("\n🌐 MARKET CONDITIONS SUMMARY")
        print("─" * 50)
        
        # Calculate aggregate metrics
        total_stocks = len(self.monitor.watchlist)
        positive_1d = sum(1 for s in self.monitor.watchlist 
                         if s in analysis and '1D' in analysis[s] 
                         and analysis[s]['1D'].get('total_return_pct', 0) > 0)
        
        high_vol_stocks = sum(1 for s in self.monitor.watchlist 
                             if s in analysis and '1D' in analysis[s] 
                             and analysis[s]['1D'].get('volatility_pct', 0) > 25)
        
        market_sentiment = "Bullish" if positive_1d > total_stocks/2 else "Bearish"
        volatility_env = "High" if high_vol_stocks > total_stocks/2 else "Normal"
        
        print(f"Market Sentiment: {market_sentiment} ({positive_1d}/{total_stocks} stocks positive)")
        print(f"Volatility Environment: {volatility_env} ({high_vol_stocks}/{total_stocks} high vol)")
        
        # Trading environment assessment
        if market_sentiment == "Bullish" and volatility_env == "High":
            print("🟢 Excellent trading environment - High opportunity")
        elif market_sentiment == "Bullish" and volatility_env == "Normal":
            print("🟡 Good trading environment - Moderate opportunity")
        elif volatility_env == "High":
            print("🟠 Volatile environment - High risk/reward")
        else:
            print("🔴 Challenging environment - Limited opportunity")
    
    def run_dashboard(self, update_interval: int = 30):
        """Run the live dashboard"""
        print("🚀 Starting Live Stock Performance Dashboard")
        print(f"📊 Monitoring: {', '.join(self.monitor.watchlist)}")
        print(f"🔄 Update interval: {update_interval} seconds")
        print("\nPress Ctrl+C to stop\n")
        
        try:
            while True:
                # Get fresh analysis
                analysis = self.monitor.monitor_all_stocks()
                
                # Clear screen and display dashboard
                self.clear_screen()
                self.display_header()
                self.display_quick_stats(analysis)
                self.display_strategy_recommendations(analysis)
                self.display_market_summary(analysis)
                
                # Display update info
                self.last_update = datetime.now()
                print(f"\n⏰ Last Updated: {self.last_update.strftime('%H:%M:%S')}")
                print(f"🔄 Next Update: {(self.last_update + timedelta(seconds=update_interval)).strftime('%H:%M:%S')}")
                print("\nPress Ctrl+C to stop monitoring...")
                
                # Store analysis for trending
                self.analysis_history.append({
                    'timestamp': self.last_update,
                    'analysis': analysis
                })
                
                # Keep only last 10 updates
                if len(self.analysis_history) > 10:
                    self.analysis_history = self.analysis_history[-10:]
                
                # Wait for next update
                time.sleep(update_interval)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Dashboard stopped by user")
            print("📊 Final analysis saved to reports/")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Live Stock Performance Dashboard")
    parser.add_argument("--interval", type=int, default=60, 
                       help="Update interval in seconds (default: 60)")
    parser.add_argument("--detailed", action="store_true",
                       help="Show detailed analysis for each stock")
    
    args = parser.parse_args()
    
    dashboard = LiveStockDashboard()
    
    if args.detailed:
        # Show detailed analysis once
        analysis = dashboard.monitor.monitor_all_stocks()
        dashboard.clear_screen()
        dashboard.display_header()
        dashboard.display_detailed_analysis(analysis)
    else:
        # Run live dashboard
        dashboard.run_dashboard(args.interval)

if __name__ == "__main__":
    main()
