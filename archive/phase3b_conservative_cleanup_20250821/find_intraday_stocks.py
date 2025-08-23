"""
Intraday Stock Finder and Analyzer
Finds stocks under $100 suitable for intraday trading with heavy volume and optimal volatility
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import warnings

warnings.filterwarnings("ignore")


class IntradayStockFinder:
    def __init__(self, max_price=100, min_volume=1000000):
        self.max_price = max_price
        self.min_volume = min_volume
        self.results = []

    def get_candidate_stocks(self):
        """
        Get list of candidate stocks under $100 with good volume
        Focus on popular, liquid stocks from major exchanges
        """
        # Popular stocks often under $100 with good volume
        candidates = [
            # Tech/Growth
            "AMD",
            "NVDA",
            "TSLA",
            "PLTR",
            "SOFI",
            "NIO",
            "BABA",
            "F",
            "BAC",
            "INTC",
            "CSCO",
            "ORCL",
            "CRM",
            "ADBE",
            "PYPL",
            "SQ",
            "ROKU",
            "ZM",
            "UBER",
            "LYFT",
            "SNAP",
            "TWTR",
            "PINS",
            "SPOT",
            "COIN",
            "HOOD",
            # Financial
            "JPM",
            "WFC",
            "C",
            "GS",
            "MS",
            "AXP",
            "V",
            "MA",
            "COF",
            "SCHW",
            # Healthcare/Biotech
            "JNJ",
            "PFE",
            "ABBV",
            "MRK",
            "UNH",
            "CVS",
            "GILD",
            "AMGN",
            "BIIB",
            "MRNA",
            "BNTX",
            "NVAX",
            "PFE",
            "ABT",
            "TMO",
            "DHR",
            # Consumer
            "DIS",
            "NFLX",
            "SBUX",
            "MCD",
            "KO",
            "PEP",
            "WMT",
            "TGT",
            "HD",
            "LOW",
            "NKE",
            "LULU",
            "COST",
            "AMZN",
            "ETSY",
            "SHOP",
            # Energy/Materials
            "XOM",
            "CVX",
            "COP",
            "EOG",
            "SLB",
            "HAL",
            "OXY",
            "DVN",
            "FANG",
            "FCX",
            "NEM",
            "GOLD",
            "AA",
            "X",
            "CLF",
            # Industrial/Transport
            "CAT",
            "DE",
            "BA",
            "LMT",
            "RTX",
            "GE",
            "MMM",
            "UPS",
            "FDX",
            "DAL",
            "UAL",
            # ETFs with good intraday movement
            "SPY",
            "QQQ",
            "IWM",
            "XLF",
            "XLE",
            "XLK",
            "XLV",
            "XLI",
            "XLU",
            "SOXL",
            "TQQQ",
            "SPXL",
            "FAS",
            "TNA",
            "LABU",
        ]

        return candidates

    def filter_by_price_volume(self, stocks):
        """Filter stocks by current price and average volume"""
        filtered_stocks = []

        print(
            f"📊 Filtering {len(stocks)} stocks by price (<${self.max_price}) and volume (>{self.min_volume:,})..."
        )

        for i, symbol in enumerate(stocks):
            try:
                if i % 10 == 0:
                    print(f"   Processing {i+1}/{len(stocks)}...")

                ticker = yf.Ticker(symbol)
                info = ticker.info

                # Get current price
                current_price = (
                    info.get("currentPrice") or info.get("regularMarketPrice") or 0
                )

                # Get average volume
                avg_volume = (
                    info.get("averageVolume") or info.get("averageVolume10days") or 0
                )

                # Filter criteria
                if (
                    current_price > 0
                    and current_price <= self.max_price
                    and avg_volume >= self.min_volume
                ):
                    filtered_stocks.append(
                        {
                            "symbol": symbol,
                            "price": current_price,
                            "avg_volume": avg_volume,
                            "market_cap": info.get("marketCap", 0),
                            "sector": info.get("sector", "Unknown"),
                        }
                    )
                    print(f"   ✅ {symbol}: ${current_price:.2f}, Vol: {avg_volume:,}")

                # Rate limiting
                time.sleep(0.1)

            except Exception as e:
                print(f"   ❌ Error processing {symbol}: {e}")
                continue

        print(f"✅ Found {len(filtered_stocks)} stocks meeting price/volume criteria")
        return filtered_stocks

    def analyze_intraday_suitability(self, stock_info):
        """Analyze 60-day 15m data for intraday trading suitability"""
        symbol = stock_info["symbol"]

        try:
            print(f"📈 Analyzing {symbol} intraday characteristics...")

            # Get 60 days of 15-minute data
            ticker = yf.Ticker(symbol)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=60)

            # Download 15-minute data
            data = ticker.history(period="60d", interval="15m")

            if data.empty or len(data) < 100:
                print(f"   ❌ Insufficient data for {symbol}")
                return None

            # Calculate intraday metrics
            data["returns"] = data["Close"].pct_change()
            data["volatility"] = data["returns"].rolling(window=20).std()
            data["range_pct"] = ((data["High"] - data["Low"]) / data["Close"]) * 100

            # Remove outliers (beyond 3 standard deviations)
            returns_clean = data["returns"].dropna()
            mean_return = returns_clean.mean()
            std_return = returns_clean.std()
            clean_returns = returns_clean[
                abs(returns_clean - mean_return) <= 3 * std_return
            ]

            # Calculate key metrics
            avg_volatility = data["volatility"].mean() * 100  # Convert to percentage
            avg_range = data["range_pct"].mean()
            avg_volume = data["Volume"].mean()
            volume_consistency = (
                data["Volume"].std() / avg_volume if avg_volume > 0 else float("inf")
            )

            # Calculate 15-minute typical moves (similar to our current analysis)
            price_changes = abs(data["Close"].diff())
            typical_move_dollars = price_changes.quantile(0.7)  # 70th percentile move
            typical_move_pct = (typical_move_dollars / data["Close"].mean()) * 100

            # Intraday range analysis
            daily_data = data.groupby(data.index.date).agg(
                {"High": "max", "Low": "min", "Close": "last", "Volume": "sum"}
            )
            daily_data["daily_range_pct"] = (
                (daily_data["High"] - daily_data["Low"]) / daily_data["Close"]
            ) * 100
            avg_daily_range = daily_data["daily_range_pct"].mean()

            # Trading hours analysis (9:30 AM - 4:00 PM ET)
            data["hour"] = data.index.hour
            trading_hours = data[(data["hour"] >= 9) & (data["hour"] <= 16)]
            active_volume = trading_hours["Volume"].mean()

            # Calculate optimal thresholds using our established methodology
            volatility_profile = self.classify_volatility(avg_volatility)
            suggested_stop = min(max(typical_move_pct * 0.8, 0.3), 2.0)  # 0.3% to 2.0%
            suggested_profit = suggested_stop * 1.8  # 1.8:1 risk/reward
            suggested_trailing = suggested_stop * 1.5

            # Scoring system (0-100)
            volume_score = min(
                (avg_volume / 2000000) * 30, 30
            )  # Max 30 points for volume
            volatility_score = self.score_volatility(avg_volatility)  # Max 25 points
            consistency_score = max(0, 20 - (volume_consistency * 10))  # Max 20 points
            range_score = min(
                (avg_daily_range / 3) * 25, 25
            )  # Max 25 points for 3%+ daily range

            total_score = (
                volume_score + volatility_score + consistency_score + range_score
            )

            analysis = {
                "symbol": symbol,
                "current_price": stock_info["price"],
                "sector": stock_info["sector"],
                "market_cap": stock_info["market_cap"],
                # Volume metrics
                "avg_volume_15m": int(avg_volume),
                "avg_daily_volume": int(daily_data["Volume"].mean()),
                "volume_consistency": round(volume_consistency, 2),
                # Volatility metrics
                "avg_volatility_15m": round(avg_volatility, 2),
                "typical_move_pct": round(typical_move_pct, 2),
                "avg_daily_range_pct": round(avg_daily_range, 2),
                "volatility_profile": volatility_profile,
                # Suggested thresholds
                "suggested_stop_loss": round(suggested_stop, 2),
                "suggested_take_profit": round(suggested_profit, 2),
                "suggested_trailing_distance": round(suggested_trailing, 2),
                # Scoring
                "volume_score": round(volume_score, 1),
                "volatility_score": round(volatility_score, 1),
                "consistency_score": round(consistency_score, 1),
                "range_score": round(range_score, 1),
                "total_score": round(total_score, 1),
                "trading_suitability": self.get_suitability_rating(total_score),
            }

            print(
                f"   ✅ {symbol}: Score {total_score:.1f}/100 ({analysis['trading_suitability']})"
            )
            return analysis

        except Exception as e:
            print(f"   ❌ Error analyzing {symbol}: {e}")
            return None

    def classify_volatility(self, volatility_pct):
        """Classify volatility level"""
        if volatility_pct < 0.5:
            return "Low"
        elif volatility_pct < 1.5:
            return "Moderate"
        elif volatility_pct < 3.0:
            return "High"
        else:
            return "Very High"

    def score_volatility(self, volatility_pct):
        """Score volatility for intraday trading (sweet spot is 0.8-2.0%)"""
        if 0.8 <= volatility_pct <= 2.0:
            return 25  # Perfect range
        elif 0.5 <= volatility_pct < 0.8:
            return 20  # Acceptable low
        elif 2.0 < volatility_pct <= 3.0:
            return 20  # Acceptable high
        elif 0.3 <= volatility_pct < 0.5:
            return 15  # Too low
        elif 3.0 < volatility_pct <= 5.0:
            return 15  # Too high
        else:
            return 5  # Unsuitable

    def get_suitability_rating(self, score):
        """Convert score to rating"""
        if score >= 80:
            return "Excellent"
        elif score >= 65:
            return "Good"
        elif score >= 50:
            return "Fair"
        elif score >= 35:
            return "Poor"
        else:
            return "Unsuitable"

    def run_analysis(self):
        """Run complete analysis pipeline"""
        print("🚀 Starting Intraday Stock Analysis...")
        print(f"   Criteria: Price <${self.max_price}, Volume >{self.min_volume:,}")

        # Step 1: Get candidate stocks
        candidates = self.get_candidate_stocks()

        # Step 2: Filter by price and volume
        filtered_stocks = self.filter_by_price_volume(candidates)

        if not filtered_stocks:
            print("❌ No stocks found meeting criteria")
            return []

        # Step 3: Analyze top candidates (limit to prevent rate limiting)
        print(
            f"\n📊 Analyzing top {min(len(filtered_stocks), 20)} candidates for intraday suitability..."
        )

        # Sort by volume and take top candidates
        filtered_stocks.sort(key=lambda x: x["avg_volume"], reverse=True)
        top_candidates = filtered_stocks[:20]

        analyzed_stocks = []
        for i, stock in enumerate(top_candidates):
            print(f"\n[{i+1}/20] Analyzing {stock['symbol']}...")
            analysis = self.analyze_intraday_suitability(stock)
            if analysis:
                analyzed_stocks.append(analysis)

            # Rate limiting to avoid getting blocked
            time.sleep(1)

        # Sort by total score
        analyzed_stocks.sort(key=lambda x: x["total_score"], reverse=True)

        print(f"\n✅ Analysis complete! Found {len(analyzed_stocks)} suitable stocks")
        return analyzed_stocks


def main():
    finder = IntradayStockFinder(max_price=100, min_volume=1000000)
    results = finder.run_analysis()

    if results:
        print(f"\n🏆 Top 10 Results:")
        for i, stock in enumerate(results[:10]):
            print(
                f"{i+1}. {stock['symbol']}: {stock['total_score']:.1f}/100 ({stock['trading_suitability']})"
            )

    return results


if __name__ == "__main__":
    results = main()
