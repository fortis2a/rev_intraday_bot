#!/usr/bin/env python3
"""
📊 Stock Performance Monitor
Comprehensive analysis of watchlist stocks to guide strategic trading decisions
"""

import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import logging
import time
import json

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from config import config
from core.data_manager import DataManager
from utils.logger import setup_logger

class StockPerformanceMonitor:
    """Monitor and analyze performance of watchlist stocks"""
    
    def __init__(self):
        """Initialize the performance monitor"""
        self.logger = setup_logger("stock_monitor")
        self.data_manager = DataManager()
        self.watchlist = config.SCALPING_WATCHLIST  # Using your current quantum watchlist
        self.performance_data = {}
        
        # Analysis timeframes
        self.timeframes = {
            '1D': 1,      # 1 day
            '5D': 5,      # 1 week
            '30D': 30,    # 1 month
            '90D': 90     # 3 months
        }
        
        self.logger.info(f"📊 Initialized monitor for {len(self.watchlist)} stocks: {', '.join(self.watchlist)}")
    
    def get_stock_data(self, symbol: str, days: int) -> Optional[pd.DataFrame]:
        """Get historical data for a stock"""
        try:
            # Calculate the number of bars needed (accounting for market days)
            # Roughly 252 trading days per year, so about 1.26 bars per calendar day
            bars_needed = max(days + 10, int(days * 1.4))  # Add buffer for weekends/holidays
            
            # Use the existing data manager
            df = self.data_manager.get_market_data(
                symbol=symbol,
                timeframe="1Day",
                limit=bars_needed,
                context="performance_analysis",
                force_fresh=True
            )
            
            if df is not None and len(df) > 0:
                # Ensure we have the required columns
                if all(col in df.columns for col in ['open', 'high', 'low', 'close', 'volume']):
                    return df.tail(days)  # Get only the requested days
                else:
                    self.logger.warning(f"⚠️ Missing required columns for {symbol}")
            
        except Exception as e:
            self.logger.error(f"❌ Error getting data for {symbol}: {e}")
        
        return None
    
    def calculate_performance_metrics(self, df: pd.DataFrame) -> Dict:
        """Calculate comprehensive performance metrics"""
        if df is None or len(df) < 2:
            return {}
        
        # Basic metrics
        current_price = df['close'].iloc[-1]
        start_price = df['close'].iloc[0]
        total_return = ((current_price - start_price) / start_price) * 100
        
        # Volatility (standard deviation of daily returns)
        daily_returns = df['close'].pct_change().dropna()
        volatility = daily_returns.std() * np.sqrt(252) * 100  # Annualized
        
        # Volume analysis
        avg_volume = df['volume'].mean()
        recent_volume = df['volume'].tail(5).mean()  # Last 5 days
        volume_trend = ((recent_volume - avg_volume) / avg_volume) * 100
        
        # Price movement analysis
        high_price = df['high'].max()
        low_price = df['low'].min()
        price_range = ((high_price - low_price) / start_price) * 100
        
        # Trend analysis (simple moving average)
        if len(df) >= 20:
            df['sma_20'] = df['close'].rolling(20).mean()
            trend_direction = "Bullish" if current_price > df['sma_20'].iloc[-1] else "Bearish"
        else:
            trend_direction = "Neutral"
        
        # Support/Resistance levels
        support_level = df['low'].tail(20).min() if len(df) >= 20 else df['low'].min()
        resistance_level = df['high'].tail(20).max() if len(df) >= 20 else df['high'].max()
        
        return {
            'current_price': round(current_price, 2),
            'start_price': round(start_price, 2),
            'total_return_pct': round(total_return, 2),
            'volatility_pct': round(volatility, 2),
            'avg_volume': int(avg_volume),
            'recent_volume': int(recent_volume),
            'volume_trend_pct': round(volume_trend, 2),
            'price_range_pct': round(price_range, 2),
            'trend_direction': trend_direction,
            'support_level': round(support_level, 2),
            'resistance_level': round(resistance_level, 2),
            'days_analyzed': len(df)
        }
    
    def analyze_trading_suitability(self, metrics: Dict, symbol: str) -> Dict:
        """Analyze suitability for different trading strategies"""
        if not metrics:
            return {'suitability': 'No Data', 'reason': 'Insufficient data'}
        
        volatility = metrics.get('volatility_pct', 0)
        volume_trend = metrics.get('volume_trend_pct', 0)
        total_return = metrics.get('total_return_pct', 0)
        
        # Scoring system
        scores = {
            'day_trading': 0,
            'swing_trading': 0,
            'position_trading': 0
        }
        
        # Day trading suitability
        if volatility > 25:  # High volatility
            scores['day_trading'] += 2
        elif volatility > 15:
            scores['day_trading'] += 1
        
        if volume_trend > 20:  # High volume
            scores['day_trading'] += 2
        elif volume_trend > 0:
            scores['day_trading'] += 1
        
        # Swing trading suitability  
        if 15 <= volatility <= 35:  # Moderate volatility
            scores['swing_trading'] += 2
        elif 10 <= volatility <= 45:
            scores['swing_trading'] += 1
        
        if abs(total_return) > 5:  # Trending
            scores['swing_trading'] += 2
        elif abs(total_return) > 2:
            scores['swing_trading'] += 1
        
        # Position trading suitability
        if volatility < 25:  # Lower volatility
            scores['position_trading'] += 2
        
        if total_return > 0:  # Positive trend
            scores['position_trading'] += 1
        
        # Determine best strategy
        best_strategy = max(scores, key=scores.get)
        best_score = scores[best_strategy]
        
        # Risk assessment
        risk_level = "High" if volatility > 30 else "Medium" if volatility > 15 else "Low"
        
        return {
            'best_strategy': best_strategy,
            'strategy_score': best_score,
            'risk_level': risk_level,
            'day_trading_score': scores['day_trading'],
            'swing_trading_score': scores['swing_trading'],
            'position_trading_score': scores['position_trading'],
            'recommendation': self._get_recommendation(symbol, best_strategy, best_score, risk_level)
        }
    
    def _get_recommendation(self, symbol: str, strategy: str, score: int, risk: str) -> str:
        """Generate trading recommendation"""
        quantum_stocks = ['IONQ', 'QBTS', 'RGTI']
        stable_stocks = ['PG', 'JNJ']
        
        if symbol in quantum_stocks:
            if strategy == 'swing_trading' and score >= 3:
                return f"Excellent for swing trading - High volatility quantum play"
            elif strategy == 'day_trading' and score >= 3:
                return f"Good for day trading - Monitor for momentum"
            else:
                return f"Moderate opportunity - Wait for better setup"
        
        elif symbol in stable_stocks:
            if strategy == 'position_trading' and score >= 2:
                return f"Good for position/overnight holds - Stable large cap"
            elif strategy == 'swing_trading' and score >= 2:
                return f"Suitable for swing trading - Conservative play"
            else:
                return f"Hold for stability - Low volatility environment"
        
        return f"Monitor closely - Strategy: {strategy}, Risk: {risk}"
    
    def monitor_all_stocks(self) -> Dict:
        """Monitor performance of all stocks in watchlist"""
        print("📊 STOCK PERFORMANCE ANALYSIS")
        print("=" * 60)
        print(f"🕐 Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎯 Watchlist: {', '.join(self.watchlist)}")
        print("=" * 60)
        
        all_analysis = {}
        
        for symbol in self.watchlist:
            print(f"\n🔍 Analyzing {symbol}...")
            stock_analysis = {}
            
            # Analyze multiple timeframes
            for timeframe, days in self.timeframes.items():
                data = self.get_stock_data(symbol, days)
                metrics = self.calculate_performance_metrics(data)
                
                if metrics:
                    stock_analysis[timeframe] = metrics
                    print(f"  📈 {timeframe}: {metrics['total_return_pct']:+.1f}% | Vol: {metrics['volatility_pct']:.1f}% | ${metrics['current_price']}")
            
            # Overall trading suitability analysis
            if '30D' in stock_analysis:
                suitability = self.analyze_trading_suitability(stock_analysis['30D'], symbol)
                stock_analysis['trading_analysis'] = suitability
                
                print(f"  🎯 Best Strategy: {suitability['best_strategy']} (Score: {suitability['strategy_score']}/4)")
                print(f"  ⚠️  Risk Level: {suitability['risk_level']}")
                print(f"  💡 Recommendation: {suitability['recommendation']}")
            
            all_analysis[symbol] = stock_analysis
            time.sleep(0.5)  # Rate limiting
        
        # Summary analysis
        self._print_summary_analysis(all_analysis)
        
        # Save analysis to file
        self._save_analysis(all_analysis)
        
        return all_analysis
    
    def _print_summary_analysis(self, analysis: Dict):
        """Print summary analysis for strategic decision making"""
        print(f"\n{'='*60}")
        print("📋 STRATEGIC SUMMARY")
        print(f"{'='*60}")
        
        # Categorize stocks
        day_trading_candidates = []
        swing_trading_candidates = []
        position_trading_candidates = []
        
        for symbol, data in analysis.items():
            if 'trading_analysis' in data:
                best_strategy = data['trading_analysis']['best_strategy']
                score = data['trading_analysis']['strategy_score']
                
                if best_strategy == 'day_trading' and score >= 3:
                    day_trading_candidates.append(symbol)
                elif best_strategy == 'swing_trading' and score >= 2:
                    swing_trading_candidates.append(symbol)
                elif best_strategy == 'position_trading' and score >= 2:
                    position_trading_candidates.append(symbol)
        
        print(f"🚀 Day Trading Ready: {', '.join(day_trading_candidates) if day_trading_candidates else 'None'}")
        print(f"📈 Swing Trading Ready: {', '.join(swing_trading_candidates) if swing_trading_candidates else 'None'}")
        print(f"🏦 Position Trading Ready: {', '.join(position_trading_candidates) if position_trading_candidates else 'None'}")
        
        # PDT Strategy Recommendation
        print(f"\n💡 PDT STRATEGY RECOMMENDATIONS:")
        
        total_candidates = len(day_trading_candidates) + len(swing_trading_candidates)
        
        if total_candidates >= 3:
            print("✅ Good opportunities available - Consider selective day trading (3 trades/week)")
        elif len(swing_trading_candidates) >= 2:
            print("📊 Moderate opportunities - Focus on swing trading approach")
        else:
            print("⏳ Limited opportunities - Wait for better setups or consider position trading")
        
        # Best quantum vs stable allocation
        quantum_ready = sum(1 for s in ['IONQ', 'QBTS', 'RGTI'] if s in swing_trading_candidates + day_trading_candidates)
        stable_ready = sum(1 for s in ['PG', 'JNJ'] if s in swing_trading_candidates + position_trading_candidates)
        
        print(f"\n🎯 PORTFOLIO ALLOCATION SUGGESTION:")
        print(f"   🔬 Quantum Stocks Ready: {quantum_ready}/3")
        print(f"   🏢 Stable Stocks Ready: {stable_ready}/2")
        
        if quantum_ready >= 2:
            print("   💡 Focus on quantum momentum plays with stable stock hedge")
        elif stable_ready >= 1:
            print("   💡 Conservative approach - emphasize stable stocks")
        else:
            print("   💡 Market conditions challenging - consider cash position")
    
    def _save_analysis(self, analysis: Dict):
        """Save analysis to JSON file for historical tracking"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"stock_analysis_{timestamp}.json"
        filepath = Path("reports") / filename
        
        # Create reports directory if it doesn't exist
        filepath.parent.mkdir(exist_ok=True)
        
        # Add metadata
        analysis['metadata'] = {
            'timestamp': datetime.now().isoformat(),
            'watchlist': self.watchlist,
            'analysis_type': 'comprehensive_performance'
        }
        
        try:
            with open(filepath, 'w') as f:
                json.dump(analysis, f, indent=2, default=str)
            
            print(f"\n💾 Analysis saved to: {filepath}")
            self.logger.info(f"Analysis saved to {filepath}")
            
        except Exception as e:
            self.logger.error(f"Error saving analysis: {e}")
    
    def run_continuous_monitoring(self, interval_minutes: int = 30):
        """Run continuous monitoring with specified interval"""
        print(f"🔄 Starting continuous monitoring (every {interval_minutes} minutes)")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                self.monitor_all_stocks()
                print(f"\n⏰ Next update in {interval_minutes} minutes...")
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped by user")
            self.logger.info("Continuous monitoring stopped")

def main():
    """Main function to run stock performance monitoring"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Stock Performance Monitor")
    parser.add_argument("--continuous", action="store_true", help="Run continuous monitoring")
    parser.add_argument("--interval", type=int, default=30, help="Monitoring interval in minutes (default: 30)")
    
    args = parser.parse_args()
    
    monitor = StockPerformanceMonitor()
    
    if args.continuous:
        monitor.run_continuous_monitoring(args.interval)
    else:
        monitor.monitor_all_stocks()

if __name__ == "__main__":
    main()
