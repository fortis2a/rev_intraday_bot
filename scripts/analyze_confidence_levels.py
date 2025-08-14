"""
Confidence Level Analysis for Budget-Friendly Stocks
Analyzes which stocks meet industry standard 70-80% confidence for intraday trading
"""

def analyze_confidence_levels():
    """
    Analyze confidence levels for budget-friendly stocks
    Base confidence starts at 85% with various bonuses/penalties
    Industry standard: 70-80% for reliable intraday trading
    """
    
    # Base confidence calculation (from your enhanced system)
    BASE_CONFIDENCE = 85  # Your enhanced system base
    
    stocks_analysis = {
        'SOXL': {
            'score': 87.7,
            'confidence_multiplier': 1.077,
            'volatility_profile': 'moderate_volatility_leveraged',
            'confidence_boost': 0.02,  # +2% for leveraged ETF performance
            'volume_score': 30,  # Perfect volume score
            'volatility_score': 25,  # Perfect volatility score
            'consistency_score': 7.7,  # Lower consistency (high volume variation)
            'range_score': 25  # Perfect daily range
        },
        'SOFI': {
            'score': 84.6,
            'confidence_multiplier': 1.046,
            'volatility_profile': 'moderate_volatility_fintech',
            'confidence_boost': 0.02,  # +2% for strong fundamentals
            'volume_score': 30,
            'volatility_score': 20,  # Good volatility
            'consistency_score': 9.6,  # Better consistency
            'range_score': 25
        },
        'TQQQ': {
            'score': 81.2,
            'confidence_multiplier': 1.012,
            'volatility_profile': 'low_volatility_leveraged',
            'confidence_boost': 0.03,  # +3% for stable leveraged ETF
            'volume_score': 30,
            'volatility_score': 15,  # Lower volatility score
            'consistency_score': 11.2,  # Best consistency
            'range_score': 25
        },
        'INTC': {
            'score': 79.8,
            'confidence_multiplier': 0.998,
            'volatility_profile': 'low_volatility_tech',
            'confidence_boost': 0.03,  # +3% for established tech
            'volume_score': 30,
            'volatility_score': 15,
            'consistency_score': 9.8,
            'range_score': 25
        },
        'NIO': {
            'score': 79.6,
            'confidence_multiplier': 0.996,
            'volatility_profile': 'moderate_volatility_ev',
            'confidence_boost': 0.0,  # No adjustment for EV volatility
            'volume_score': 30,
            'volatility_score': 15,  # Moderate volatility
            'consistency_score': 6.7,  # Lower consistency
            'range_score': 25
        }
    }
    
    print("📊 CONFIDENCE LEVEL ANALYSIS FOR BUDGET-FRIENDLY STOCKS")
    print("=" * 70)
    print(f"Base Confidence: {BASE_CONFIDENCE}%")
    print(f"Industry Target: 70-80% for reliable intraday trading")
    print()
    
    results = []
    
    for symbol, data in stocks_analysis.items():
        # Calculate enhanced confidence
        base_conf = BASE_CONFIDENCE
        
        # Apply score-based adjustment (score/100 as multiplier)
        score_adjustment = (data['score'] / 100) * base_conf - base_conf
        
        # Apply profile boost
        profile_boost = data['confidence_boost'] * 100
        
        # Apply consistency bonus (higher consistency = more confidence)
        consistency_bonus = (data['consistency_score'] / 20) * 5  # Max 5% bonus
        
        # Apply volume bonus (perfect volume = confidence boost)
        volume_bonus = (data['volume_score'] / 30) * 3  # Max 3% bonus
        
        # Calculate final confidence
        final_confidence = (
            base_conf + 
            score_adjustment + 
            profile_boost + 
            consistency_bonus + 
            volume_bonus
        )
        
        # Industry standards check
        industry_compliant = 70 <= final_confidence <= 80
        above_industry = final_confidence > 80
        below_industry = final_confidence < 70
        
        rating = "🎯 INDUSTRY STANDARD" if industry_compliant else \
                "🚀 ABOVE INDUSTRY" if above_industry else \
                "⚠️  BELOW INDUSTRY"
        
        results.append({
            'symbol': symbol,
            'final_confidence': final_confidence,
            'score': data['score'],
            'industry_compliant': industry_compliant,
            'rating': rating,
            'base_conf': base_conf,
            'score_adj': score_adjustment,
            'profile_boost': profile_boost,
            'consistency_bonus': consistency_bonus,
            'volume_bonus': volume_bonus
        })
        
        print(f"{symbol} ({data['volatility_profile']})")
        print(f"  Trading Score: {data['score']:.1f}/100")
        print(f"  Base Confidence: {base_conf:.1f}%")
        print(f"  Score Adjustment: {score_adjustment:+.1f}%")
        print(f"  Profile Boost: {profile_boost:+.1f}%")
        print(f"  Consistency Bonus: {consistency_bonus:+.1f}%")
        print(f"  Volume Bonus: {volume_bonus:+.1f}%")
        print(f"  📈 Final Confidence: {final_confidence:.1f}% {rating}")
        print()
    
    # Sort by confidence level
    results.sort(key=lambda x: x['final_confidence'], reverse=True)
    
    print("🏆 RANKING BY CONFIDENCE LEVEL")
    print("=" * 50)
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['symbol']}: {result['final_confidence']:.1f}% {result['rating']}")
    
    print()
    print("📋 INDUSTRY COMPLIANCE SUMMARY")
    print("=" * 40)
    
    industry_compliant = [r for r in results if r['industry_compliant']]
    above_industry = [r for r in results if r['final_confidence'] > 80]
    below_industry = [r for r in results if r['final_confidence'] < 70]
    
    print(f"🎯 Industry Standard (70-80%): {len(industry_compliant)} stocks")
    for stock in industry_compliant:
        print(f"   • {stock['symbol']}: {stock['final_confidence']:.1f}%")
    
    print(f"🚀 Above Industry (>80%): {len(above_industry)} stocks")
    for stock in above_industry:
        print(f"   • {stock['symbol']}: {stock['final_confidence']:.1f}%")
    
    print(f"⚠️  Below Industry (<70%): {len(below_industry)} stocks")
    for stock in below_industry:
        print(f"   • {stock['symbol']}: {stock['final_confidence']:.1f}%")
    
    print()
    print("💡 RECOMMENDATIONS")
    print("=" * 20)
    
    if industry_compliant:
        print("✅ OPTIMAL FOR INTRADAY TRADING:")
        for stock in industry_compliant:
            print(f"   • {stock['symbol']} - Perfect balance of performance and reliability")
    
    if above_industry:
        print("⚡ HIGH CONFIDENCE (Use with position size limits):")
        for stock in above_industry:
            print(f"   • {stock['symbol']} - Excellent but may be over-optimistic")
    
    if below_industry:
        print("🔧 NEEDS OPTIMIZATION:")
        for stock in below_industry:
            print(f"   • {stock['symbol']} - Consider additional filters or skip")
    
    return results

if __name__ == "__main__":
    results = analyze_confidence_levels()
