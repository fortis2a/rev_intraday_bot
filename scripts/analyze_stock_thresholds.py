#!/usr/bin/env python3
"""
Stock-Specific Threshold Analysis
Analyzes 15-minute historical data for watchlist stocks to determine optimal profit/loss thresholds
"""

import sys
from pathlib import Path
# Add parent directory to path to access main modules
sys.path.append(str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
from config import config
from utils.logger import setup_logger
import warnings
warnings.filterwarnings('ignore')

class ThresholdAnalyzer:
    """Analyzes historical data to determine stock-specific thresholds"""
    
    def __init__(self):
        self.logger = setup_logger("threshold_analyzer")
        self.watchlist = config['INTRADAY_WATCHLIST']
        self.logger.info("Threshold Analyzer initialized with Yahoo Finance data source")
        
    def get_historical_data(self, symbol: str, days: int = 60) -> pd.DataFrame:
        """Get 15-minute historical data using Yahoo Finance"""
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            self.logger.info(f"[{symbol}] Fetching 15M data from Yahoo Finance: {start_date.date()} to {end_date.date()}")
            
            # Create yfinance ticker object
            ticker = yf.Ticker(symbol)
            
            # Try to get intraday data (15-minute intervals)
            # Yahoo Finance supports 1m, 2m, 5m, 15m, 30m, 60m, 90m for recent data
            try:
                # For 60 days, we need to split into smaller chunks as Yahoo limits intraday data
                # Yahoo typically allows up to 60 days of 1m data, 2 years of 15m data
                
                hist_data = ticker.history(
                    start=start_date,
                    end=end_date,
                    interval="15m",
                    prepost=False,  # Regular trading hours only
                    auto_adjust=True,
                    back_adjust=False
                )
                
                if hist_data.empty:
                    self.logger.warning(f"[{symbol}] No 15-minute data available, trying daily data")
                    return self.get_daily_data_fallback(symbol, days)
                
                # Rename columns to match our expected format
                hist_data.columns = [col.lower() for col in hist_data.columns]
                
                # Filter to regular trading hours (9:30 AM - 4:00 PM ET)
                hist_data = hist_data.between_time('09:30', '16:00')
                
                self.logger.info(f"[{symbol}] Retrieved {len(hist_data)} 15-minute bars")
                return hist_data
                
            except Exception as intraday_error:
                self.logger.warning(f"[{symbol}] 15-minute data failed: {intraday_error}")
                return self.get_daily_data_fallback(symbol, days)
            
        except Exception as e:
            self.logger.error(f"[{symbol}] Error fetching data: {e}")
            return pd.DataFrame()
    
    def get_daily_data_fallback(self, symbol: str, days: int) -> pd.DataFrame:
        """Fallback to daily data and simulate 15-minute movements"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            self.logger.info(f"[{symbol}] Fetching daily data for simulation")
            
            ticker = yf.Ticker(symbol)
            daily_data = ticker.history(
                start=start_date,
                end=end_date,
                interval="1d",
                auto_adjust=True
            )
            
            if daily_data.empty:
                self.logger.error(f"[{symbol}] No daily data available")
                return pd.DataFrame()
            
            # Rename columns to lowercase
            daily_data.columns = [col.lower() for col in daily_data.columns]
            
            # Simulate 15-minute bars from daily data
            simulated_15m = self.simulate_intraday_from_daily(daily_data, symbol)
            
            self.logger.info(f"[{symbol}] Simulated {len(simulated_15m)} 15-minute bars from daily data")
            return simulated_15m
            
        except Exception as e:
            self.logger.error(f"[{symbol}] Daily data fallback failed: {e}")
            return pd.DataFrame()
    
    def simulate_intraday_from_daily(self, daily_df: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """Simulate 15-minute bars from daily data using statistical models"""
        simulated_bars = []
        
        for idx, row in daily_df.iterrows():
            date = idx.date()
            open_price = row['open']
            high_price = row['high']
            low_price = row['low']
            close_price = row['close']
            volume = row['volume']
            
            # Calculate daily return and volatility
            daily_return = (close_price - open_price) / open_price
            daily_range = (high_price - low_price) / open_price
            
            # Generate 26 15-minute bars (6.5 hours * 4 bars per hour)
            bars_per_day = 26
            volume_per_bar = volume / bars_per_day
            
            # Use GBM (Geometric Brownian Motion) to simulate intraday path
            dt = 1/bars_per_day  # Time step
            
            # Estimate volatility from daily range (rough approximation)
            estimated_vol = daily_range * 2  # Rough conversion
            
            current_price = open_price
            current_time = pd.Timestamp.combine(date, pd.Timestamp('09:30:00').time())
            
            for bar in range(bars_per_day):
                # Generate random walk component
                random_shock = np.random.normal(0, estimated_vol * np.sqrt(dt))
                
                # Add trend component to reach close price
                trend_component = daily_return * dt
                
                # Calculate price movement
                price_change = trend_component + random_shock
                new_price = current_price * (1 + price_change)
                
                # Ensure price stays within daily high/low bounds
                new_price = max(low_price, min(high_price, new_price))
                
                # Create bar data
                bar_open = current_price
                bar_close = new_price
                
                # Simulate high/low within the bar
                intrabar_range = abs(price_change) * current_price * 1.5  # Add some intrabar movement
                bar_high = max(bar_open, bar_close) + intrabar_range/2
                bar_low = min(bar_open, bar_close) - intrabar_range/2
                
                # Bound within daily limits
                bar_high = min(high_price, bar_high)
                bar_low = max(low_price, bar_low)
                
                simulated_bars.append({
                    'timestamp': current_time + timedelta(minutes=15*bar),
                    'open': bar_open,
                    'high': bar_high,
                    'low': bar_low,
                    'close': bar_close,
                    'volume': volume_per_bar
                })
                
                current_price = new_price
        
        # Convert to DataFrame
        sim_df = pd.DataFrame(simulated_bars)
        sim_df.set_index('timestamp', inplace=True)
        
        return sim_df
    
    def calculate_price_movements(self, df: pd.DataFrame) -> dict:
        """Calculate various price movement statistics"""
        if df.empty:
            return {}
        
        # Calculate bar-to-bar movements
        df['pct_change'] = df['close'].pct_change()
        df['high_low_range'] = (df['high'] - df['low']) / df['open']
        df['open_close_move'] = (df['close'] - df['open']) / df['open']
        
        # Remove outliers (beyond 3 standard deviations)
        pct_changes = df['pct_change'].dropna()
        mean_change = pct_changes.mean()
        std_change = pct_changes.std()
        filtered_changes = pct_changes[np.abs(pct_changes - mean_change) <= 3 * std_change]
        
        # Calculate statistics
        stats = {
            'total_bars': len(df),
            'avg_price': df['close'].mean(),
            'volatility': df['pct_change'].std() * 100,  # Convert to percentage
            
            # Movement percentiles
            'move_5th': np.percentile(filtered_changes, 5) * 100,
            'move_10th': np.percentile(filtered_changes, 10) * 100,
            'move_25th': np.percentile(filtered_changes, 25) * 100,
            'move_50th': np.percentile(filtered_changes, 50) * 100,
            'move_75th': np.percentile(filtered_changes, 75) * 100,
            'move_90th': np.percentile(filtered_changes, 90) * 100,
            'move_95th': np.percentile(filtered_changes, 95) * 100,
            
            # Range statistics
            'avg_range': df['high_low_range'].mean() * 100,
            'range_75th': np.percentile(df['high_low_range'], 75) * 100,
            'range_90th': np.percentile(df['high_low_range'], 90) * 100,
            
            # Directional bias
            'up_moves': len(df[df['pct_change'] > 0]),
            'down_moves': len(df[df['pct_change'] < 0]),
            'flat_moves': len(df[df['pct_change'] == 0]),
            
            # Extreme moves
            'moves_over_1pct': len(df[np.abs(df['pct_change']) > 0.01]),
            'moves_over_2pct': len(df[np.abs(df['pct_change']) > 0.02]),
            'moves_over_3pct': len(df[np.abs(df['pct_change']) > 0.03]),
        }
        
        return stats
    
    def calculate_optimal_thresholds(self, stats: dict) -> dict:
        """Calculate recommended thresholds based on statistics"""
        if not stats:
            return {}
        
        # Base thresholds on volatility and percentiles
        volatility = stats['volatility']
        
        # Stop loss: Use 75th percentile of negative moves as baseline
        # But ensure it's reasonable (0.5% to 4.0%)
        base_stop = max(0.5, min(4.0, abs(stats['move_25th']) * 1.2))
        
        # Take profit: Use 75th percentile of positive moves
        # Scale based on win rate and volatility
        base_profit = max(1.0, min(6.0, stats['move_75th'] * 1.1))
        
        # Trailing stop activation: 50-70% of take profit
        trailing_activation = base_profit * 0.6
        
        # Trailing distance: Based on average range but capped
        trailing_distance = min(3.0, max(1.0, stats['avg_range'] * 0.7))
        
        return {
            'stop_loss_pct': round(base_stop, 2),
            'take_profit_pct': round(base_profit, 2),
            'trailing_activation_pct': round(trailing_activation, 2),
            'trailing_distance_pct': round(trailing_distance, 2),
            'confidence_adjustment': 1.0 + (volatility - 2.0) / 10.0  # Adjust for volatility
        }
    
    def analyze_all_stocks(self):
        """Analyze all stocks in the watchlist"""
        results = {}
        
        print("=" * 80)
        print("🎯 STOCK-SPECIFIC THRESHOLD ANALYSIS")
        print("=" * 80)
        print(f"📊 Analyzing {len(self.watchlist)} stocks with 60 days of 15-minute data")
        print(f"📅 Analysis period: {(datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d')} to {datetime.now().strftime('%Y-%m-%d')}")
        
        for symbol in self.watchlist:
            print(f"\n🔍 Analyzing {symbol}...")
            
            # Get historical data
            df = self.get_historical_data(symbol)
            
            if df.empty:
                print(f"❌ No data available for {symbol}")
                continue
            
            # Calculate statistics
            stats = self.calculate_price_movements(df)
            thresholds = self.calculate_optimal_thresholds(stats)
            
            results[symbol] = {
                'stats': stats,
                'thresholds': thresholds
            }
            
            # Display results
            self.display_stock_analysis(symbol, stats, thresholds)
        
        # Generate summary and recommendations
        self.generate_summary_report(results)
        self.generate_config_recommendations(results)
        
        return results
    
    def display_stock_analysis(self, symbol: str, stats: dict, thresholds: dict):
        """Display analysis results for a single stock"""
        print(f"\n📈 {symbol} - MOVEMENT ANALYSIS")
        print("-" * 50)
        print(f"Total 15-min bars analyzed: {stats['total_bars']:,}")
        print(f"Average price: ${stats['avg_price']:.2f}")
        print(f"Volatility (std dev): {stats['volatility']:.2f}%")
        
        print(f"\n📊 Price Movement Percentiles:")
        print(f"  5th percentile:  {stats['move_5th']:+.2f}%")
        print(f"  25th percentile: {stats['move_25th']:+.2f}%")
        print(f"  50th percentile: {stats['move_50th']:+.2f}%")
        print(f"  75th percentile: {stats['move_75th']:+.2f}%")
        print(f"  95th percentile: {stats['move_95th']:+.2f}%")
        
        print(f"\n📏 Range Analysis:")
        print(f"  Average high-low range: {stats['avg_range']:.2f}%")
        print(f"  75th percentile range: {stats['range_75th']:.2f}%")
        print(f"  90th percentile range: {stats['range_90th']:.2f}%")
        
        print(f"\n🎯 Movement Frequency:")
        up_pct = stats['up_moves'] / (stats['up_moves'] + stats['down_moves']) * 100
        print(f"  Up moves: {stats['up_moves']} ({up_pct:.1f}%)")
        print(f"  Down moves: {stats['down_moves']} ({100-up_pct:.1f}%)")
        print(f"  Moves >1%: {stats['moves_over_1pct']} ({stats['moves_over_1pct']/stats['total_bars']*100:.1f}%)")
        print(f"  Moves >2%: {stats['moves_over_2pct']} ({stats['moves_over_2pct']/stats['total_bars']*100:.1f}%)")
        
        print(f"\n🎯 RECOMMENDED THRESHOLDS:")
        print(f"  Stop Loss: {thresholds['stop_loss_pct']:.2f}%")
        print(f"  Take Profit: {thresholds['take_profit_pct']:.2f}%")
        print(f"  Trailing Activation: {thresholds['trailing_activation_pct']:.2f}%")
        print(f"  Trailing Distance: {thresholds['trailing_distance_pct']:.2f}%")
    
    def generate_summary_report(self, results: dict):
        """Generate a summary comparison report"""
        print(f"\n" + "=" * 80)
        print("📊 STOCK COMPARISON SUMMARY")
        print("=" * 80)
        
        if not results:
            print("❌ No data available for analysis")
            return
        
        # Create comparison table
        print(f"{'Stock':<6} {'Volatility':<10} {'Stop':<6} {'Profit':<7} {'Trail Act':<9} {'Trail Dist':<10} {'Avg Range':<10}")
        print("-" * 70)
        
        for symbol, data in results.items():
            stats = data['stats']
            thresholds = data['thresholds']
            print(f"{symbol:<6} {stats['volatility']:<10.2f} {thresholds['stop_loss_pct']:<6.2f} "
                  f"{thresholds['take_profit_pct']:<7.2f} {thresholds['trailing_activation_pct']:<9.2f} "
                  f"{thresholds['trailing_distance_pct']:<10.2f} {stats['avg_range']:<10.2f}")
        
        # Calculate portfolio averages
        volatilities = [data['stats']['volatility'] for data in results.values()]
        stop_losses = [data['thresholds']['stop_loss_pct'] for data in results.values()]
        take_profits = [data['thresholds']['take_profit_pct'] for data in results.values()]
        
        print("-" * 70)
        print(f"{'AVG':<6} {np.mean(volatilities):<10.2f} {np.mean(stop_losses):<6.2f} "
              f"{np.mean(take_profits):<7.2f} {np.mean([data['thresholds']['trailing_activation_pct'] for data in results.values()]):<9.2f} "
              f"{np.mean([data['thresholds']['trailing_distance_pct'] for data in results.values()]):<10.2f} "
              f"{np.mean([data['stats']['avg_range'] for data in results.values()]):<10.2f}")
    
    def generate_config_recommendations(self, results: dict):
        """Generate configuration file recommendations"""
        print(f"\n" + "=" * 80)
        print("⚙️ CONFIGURATION RECOMMENDATIONS")
        print("=" * 80)
        
        if not results:
            return
        
        print("\n🔧 Stock-Specific Configuration:")
        print("```python")
        print("# Stock-specific thresholds based on 60-day 15M analysis")
        print("STOCK_SPECIFIC_THRESHOLDS = {")
        
        for symbol, data in results.items():
            thresholds = data['thresholds']
            print(f"    '{symbol}': {{")
            print(f"        'stop_loss_pct': {thresholds['stop_loss_pct']:.3f},")
            print(f"        'take_profit_pct': {thresholds['take_profit_pct']:.3f},")
            print(f"        'trailing_activation_pct': {thresholds['trailing_activation_pct']:.3f},")
            print(f"        'trailing_distance_pct': {thresholds['trailing_distance_pct']:.3f},")
            print(f"        'confidence_multiplier': {thresholds['confidence_adjustment']:.3f}")
            print(f"    }},")
        
        print("}")
        print("```")
        
        # Calculate recommended defaults
        stop_losses = [data['thresholds']['stop_loss_pct'] for data in results.values()]
        take_profits = [data['thresholds']['take_profit_pct'] for data in results.values()]
        trail_acts = [data['thresholds']['trailing_activation_pct'] for data in results.values()]
        trail_dists = [data['thresholds']['trailing_distance_pct'] for data in results.values()]
        
        print(f"\n🎯 Recommended Default Settings (Conservative):")
        print(f"STOP_LOSS_PCT = {max(stop_losses):.3f}  # Use highest for safety")
        print(f"TAKE_PROFIT_PCT = {min(take_profits):.3f}  # Use lowest for reliability") 
        print(f"TRAILING_STOP_ACTIVATION = {np.median(trail_acts):.3f}")
        print(f"TRAILING_STOP_PCT = {np.median(trail_dists):.3f}")
        
        print(f"\n🚀 Aggressive Settings (Higher Risk/Reward):")
        print(f"STOP_LOSS_PCT = {np.median(stop_losses):.3f}")
        print(f"TAKE_PROFIT_PCT = {max(take_profits):.3f}")
        print(f"TRAILING_STOP_ACTIVATION = {min(trail_acts):.3f}")
        print(f"TRAILING_STOP_PCT = {min(trail_dists):.3f}")

def main():
    """Run the threshold analysis"""
    analyzer = ThresholdAnalyzer()
    
    try:
        results = analyzer.analyze_all_stocks()
        
        print(f"\n✅ Analysis complete!")
        print(f"📝 Results for {len(results)} stocks analyzed")
        print(f"🎯 Use the recommendations above to optimize your trading thresholds")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
