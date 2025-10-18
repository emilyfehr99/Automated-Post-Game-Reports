#!/usr/bin/env python3
"""
Polymarket AI Predictor - Demo Script
Demonstrates the key features of the AI prediction system
"""

import json
import time
from datetime import datetime
from polymarket_ai_predictor import PolymarketAIPredictor

def demo_basic_functionality():
    """Demonstrate basic functionality"""
    print("🎯 Polymarket AI Predictor - Demo")
    print("=" * 50)
    
    # Initialize predictor
    print("\n🚀 Initializing AI Predictor...")
    predictor = PolymarketAIPredictor()
    
    # Get exchange rate
    print("\n💱 Fetching CAD/USD exchange rate...")
    rate = predictor.get_cad_usd_rate()
    print(f"Current rate: 1 CAD = {rate:.4f} USD")
    
    # Fetch some events
    print("\n📊 Fetching active events...")
    events = predictor.fetch_polymarket_events(limit=5)
    
    if events:
        print(f"Found {len(events)} active events:")
        for i, event in enumerate(events[:3], 1):
            print(f"  {i}. {event.get('question', 'Unknown')[:60]}...")
            print(f"     Category: {event.get('category', 'Other')}")
            print(f"     Volume: ${event.get('volume', 0):,.0f}")
    else:
        print("No events found (this is normal for demo)")
    
    return predictor

def demo_prediction_analysis(predictor, portfolio_value=1000):
    """Demonstrate prediction analysis"""
    print(f"\n🎯 Generating recommendations for ${portfolio_value} CAD portfolio...")
    
    # Generate recommendations
    recommendations = predictor.generate_trading_recommendations(portfolio_value)
    
    if recommendations:
        print(f"\n📈 Generated {len(recommendations)} recommendations:")
        
        for i, rec in enumerate(recommendations[:3], 1):
            print(f"\n{i}. {rec['question'][:50]}...")
            print(f"   Current Price: {rec['current_price']:.1%}")
            print(f"   AI Prediction: {rec['prediction']:.1%} YES")
            print(f"   Confidence: {rec['confidence']:.1%}")
            print(f"   Recommendation: {rec['recommendation']}")
            print(f"   Position Size: ${rec['position_size_cad']:.2f} CAD")
            print(f"   Expected Value: {rec['expected_value']:.3f}")
    else:
        print("No recommendations generated (this is normal for demo)")
    
    return recommendations

def demo_risk_analysis(predictor):
    """Demonstrate risk analysis features"""
    print("\n🛡️ Risk Analysis Demo")
    print("-" * 30)
    
    # Sample market data for demo
    sample_market = {
        'price': 0.45,
        'volume': 50000,
        'liquidity': 25000,
        'question': 'Will Bitcoin reach $100,000 by end of 2024?',
        'category': 'Cryptocurrency',
        'endDate': '2024-12-31T23:59:59Z'
    }
    
    # Sample historical data
    import pandas as pd
    import numpy as np
    
    dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
    prices = np.random.normal(0.45, 0.05, 30)
    historical_data = pd.DataFrame({
        'close': prices,
        'high': prices + np.random.uniform(0, 0.02, 30),
        'low': prices - np.random.uniform(0, 0.02, 30),
        'volume': np.random.uniform(1000, 10000, 30)
    }, index=dates)
    
    # Extract features
    features = predictor.extract_features(sample_market, historical_data)
    
    print("Sample market features:")
    for key, value in features.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.4f}")
        else:
            print(f"  {key}: {value}")
    
    # Calculate risk score
    sample_prediction = {
        'features': features,
        'confidence': 0.75,
        'prediction': 0.65
    }
    
    risk_score = predictor.calculate_risk_score(sample_prediction, sample_market)
    print(f"\nRisk Score: {risk_score:.1%}")
    
    if risk_score < 0.3:
        print("🟢 Low Risk")
    elif risk_score < 0.6:
        print("🟡 Medium Risk")
    else:
        print("🔴 High Risk")

def demo_position_sizing(predictor):
    """Demonstrate position sizing calculations"""
    print("\n💰 Position Sizing Demo")
    print("-" * 30)
    
    portfolio_values = [500, 1000, 5000, 10000]
    
    # Sample prediction
    sample_prediction = {
        'prediction': 0.65,  # 65% chance of YES
        'confidence': 0.75,  # 75% confidence
        'current_price': 0.45,  # 45% current price
        'recommendation': 'BUY YES'
    }
    
    print("Portfolio Value | Position Size (CAD) | Position Size (USD) | Kelly Fraction")
    print("-" * 80)
    
    for portfolio_value in portfolio_values:
        position_info = predictor.calculate_position_size(sample_prediction, portfolio_value)
        
        print(f"${portfolio_value:>12,.0f} | "
              f"${position_info['position_size_cad']:>15.2f} | "
              f"${position_info['position_size_usd']:>15.2f} | "
              f"{position_info.get('kelly_fraction', 0):>12.1%}")

def demo_configuration():
    """Demonstrate configuration options"""
    print("\n⚙️ Configuration Demo")
    print("-" * 30)
    
    try:
        with open('polymarket_config.json', 'r') as f:
            config = json.load(f)
        
        print("Current configuration:")
        print(f"  Max Position Size: {config['polymarket_ai_config']['trading_parameters']['max_position_size']:.1%}")
        print(f"  Min Confidence: {config['polymarket_ai_config']['trading_parameters']['min_confidence_threshold']:.1%}")
        print(f"  Base Currency: {config['polymarket_ai_config']['currency_settings']['base_currency']}")
        print(f"  Update Frequency: {config['polymarket_ai_config']['currency_settings']['update_frequency_minutes']} minutes")
        
    except FileNotFoundError:
        print("Configuration file not found. Using default settings.")

def main():
    """Main demo function"""
    print("🎯 Welcome to the Polymarket AI Predictor Demo!")
    print("This demo showcases the key features of the AI prediction system.")
    print("\n⚠️ Note: This is a demonstration. Real trading involves risk.")
    
    try:
        # Basic functionality
        predictor = demo_basic_functionality()
        
        # Prediction analysis
        recommendations = demo_prediction_analysis(predictor)
        
        # Risk analysis
        demo_risk_analysis(predictor)
        
        # Position sizing
        demo_position_sizing(predictor)
        
        # Configuration
        demo_configuration()
        
        # Summary
        print("\n" + "=" * 50)
        print("🎉 Demo completed successfully!")
        print("\n📋 What you've seen:")
        print("• Real-time data fetching from Polymarket API")
        print("• CAD/USD exchange rate integration")
        print("• AI prediction model capabilities")
        print("• Risk analysis and scoring")
        print("• Position sizing with Kelly Criterion")
        print("• Configuration management")
        
        print("\n🚀 Next steps:")
        print("1. Run the full system: python polymarket_ai_predictor.py")
        print("2. Try the web interface: streamlit run polymarket_web_interface.py")
        print("3. Read the documentation: README_Polymarket_AI.md")
        
        print("\n⚠️ Remember:")
        print("• Check local regulations before trading")
        print("• Only invest what you can afford to lose")
        print("• Consult financial professionals")
        
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        print("This is normal if the Polymarket API is not accessible.")
        print("The demo shows the system structure and capabilities.")

if __name__ == "__main__":
    main()
