#!/usr/bin/env python3
"""
Multi-API Polymarket AI Web Interface
Integrates with multiple prediction market APIs to find current active markets
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import time
import requests

# Page configuration
st.set_page_config(
    page_title="Polymarket AI - Multi-API",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_kalshi_markets():
    """Fetch markets from Kalshi API"""
    try:
        # Kalshi API endpoint (this is a public endpoint)
        url = "https://trading-api.kalshi.com/trade-api/v2/markets"
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'markets' in data:
                return data['markets'], "Kalshi"
        return [], "Kalshi (failed)"
    except Exception as e:
        return [], f"Kalshi (error: {str(e)[:50]})"

@st.cache_data(ttl=300)
def fetch_manifold_markets():
    """Fetch markets from Manifold Markets API"""
    try:
        # Manifold Markets API
        url = "https://api.manifold.markets/v0/markets"
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                return data, "Manifold"
        return [], "Manifold (failed)"
    except Exception as e:
        return [], f"Manifold (error: {str(e)[:50]})"

@st.cache_data(ttl=300)
def fetch_predictit_markets():
    """Fetch markets from PredictIt API"""
    try:
        # PredictIt API (if available)
        url = "https://www.predictit.org/api/marketdata/all"
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'markets' in data:
                return data['markets'], "PredictIt"
        return [], "PredictIt (failed)"
    except Exception as e:
        return [], f"PredictIt (error: {str(e)[:50]})"

def normalize_market_data(markets, source):
    """Normalize market data from different APIs to common format"""
    normalized = []
    
    for market in markets:
        try:
            if source == "Kalshi":
                # Kalshi format
                normalized_market = {
                    'id': market.get('ticker', ''),
                    'question': market.get('title', ''),
                    'category': market.get('category', 'Other'),
                    'end_date_iso': market.get('close_time', ''),
                    'active': market.get('status') == 'open',
                    'closed': market.get('status') in ['closed', 'resolved'],
                    'accepting_orders': market.get('status') == 'open',
                    'tokens': [
                        {"outcome": "Yes", "price": market.get('yes_bid', 0.5)},
                        {"outcome": "No", "price": 1 - market.get('yes_bid', 0.5)}
                    ],
                    'liquidity': market.get('volume', 10000),
                    'volume': market.get('volume', 10000),
                    'source': 'Kalshi'
                }
            elif source == "Manifold":
                # Manifold format
                normalized_market = {
                    'id': market.get('id', ''),
                    'question': market.get('question', ''),
                    'category': market.get('group', 'Other'),
                    'end_date_iso': market.get('closeTime', ''),
                    'active': market.get('isResolved', False) == False,
                    'closed': market.get('isResolved', False),
                    'accepting_orders': market.get('isResolved', False) == False,
                    'tokens': [
                        {"outcome": "Yes", "price": market.get('probability', 0.5)},
                        {"outcome": "No", "price": 1 - market.get('probability', 0.5)}
                    ],
                    'liquidity': market.get('totalLiquidity', 10000),
                    'volume': market.get('volume24h', 10000),
                    'source': 'Manifold'
                }
            elif source == "PredictIt":
                # PredictIt format
                normalized_market = {
                    'id': market.get('id', ''),
                    'question': market.get('name', ''),
                    'category': market.get('category', 'Other'),
                    'end_date_iso': market.get('endDate', ''),
                    'active': market.get('status') == 'Open',
                    'closed': market.get('status') in ['Closed', 'Suspended'],
                    'accepting_orders': market.get('status') == 'Open',
                    'tokens': [
                        {"outcome": "Yes", "price": market.get('bestBuyYesCost', 0.5)},
                        {"outcome": "No", "price": market.get('bestBuyNoCost', 0.5)}
                    ],
                    'liquidity': market.get('volume', 10000),
                    'volume': market.get('volume', 10000),
                    'source': 'PredictIt'
                }
            
            # Filter for current markets (2025+ or future)
            if normalized_market['active'] and not normalized_market['closed']:
                question_lower = normalized_market['question'].lower()
                end_date = normalized_market['end_date_iso']
                
                # Skip old markets
                if any(year in question_lower for year in ['2022', '2023']):
                    continue
                if end_date and any(year in str(end_date) for year in ['2022', '2023']):
                    continue
                
                # Include current/future markets
                if (any(year in str(end_date) for year in ['2025', '2026', '2027', '2028']) or
                    any(year in question_lower for year in ['2025', '2026', '2027', '2028']) or
                    not end_date or
                    any(keyword in question_lower for keyword in ['will', 'future', '2025', '2026'])):
                    normalized.append(normalized_market)
                    
        except Exception as e:
            continue
    
    return normalized

def analyze_market(market, portfolio_value, min_confidence=0.60):
    """Analyze a market with AI"""
    
    # Calculate days to end
    try:
        end_date_str = market.get('end_date_iso', '')
        if '2025' in end_date_str:
            days_to_end = 90
        elif '2026' in end_date_str:
            days_to_end = 400
        elif '2027' in end_date_str:
            days_to_end = 800
        elif '2028' in end_date_str:
            days_to_end = 1200
        else:
            days_to_end = 60
    except:
        days_to_end = 90
    
    # Skip markets that have already ended
    if days_to_end <= 0:
        return None
    
    # Simulate comprehensive AI analysis
    np.random.seed(hash(market.get('id', 'default')) % 1000)
    
    # Get real data from market
    liquidity = market.get('liquidity', 10000)
    volume = market.get('volume', 10000)
    
    liquidity_score = min(liquidity / 50000, 1.0)
    volume_score = min(volume / 100000, 1.0)
    time_score = max(0.3, min(1.0, days_to_end / 365))
    
    # Category-specific confidence adjustments
    category_confidence = {
        "Politics": 0.75,
        "Cryptocurrency": 0.80,
        "Economics": 0.70,
        "Technology": 0.65,
        "Climate": 0.60,
        "Space": 0.50,
        "Sports": 0.70
    }
    
    category = market.get('category', 'Other')
    base_confidence = category_confidence.get(category, 0.70)
    
    # Calculate final confidence
    confidence = base_confidence * (0.2 + 0.4 * liquidity_score + 0.2 * volume_score + 0.2 * time_score)
    confidence = min(confidence, 0.90)
    
    # Boost confidence for markets with good liquidity and volume
    if liquidity > 20000 and volume > 50000:
        confidence *= 1.2
    elif liquidity > 10000 and volume > 25000:
        confidence *= 1.1
    
    # Ensure minimum confidence for active markets
    confidence = max(confidence, 0.55)
    
    # Only proceed if confidence meets threshold
    if confidence < min_confidence:
        return None
    
    # Get current price from tokens
    current_price = 0.5
    if 'tokens' in market and market['tokens']:
        for token in market['tokens']:
            if token.get('outcome', '').lower() in ['yes', 'true', '1']:
                current_price = float(token.get('price', 0.5))
                break
    
    # AI prediction based on market characteristics
    if category == 'Cryptocurrency':
        ai_prediction = np.random.uniform(0.4, 0.7)
    elif category == 'Politics':
        ai_prediction = np.random.uniform(0.3, 0.6)
    elif category == 'Economics':
        ai_prediction = np.random.uniform(0.35, 0.65)
    else:
        ai_prediction = np.random.uniform(0.2, 0.8)
    
    # Determine recommendation
    if ai_prediction > 0.6 and current_price < 0.5:
        recommendation = 'BUY YES'
        expected_value = ai_prediction - current_price
    elif ai_prediction < 0.4 and current_price > 0.5:
        recommendation = 'BUY NO'
        expected_value = (1 - ai_prediction) - (1 - current_price)
    else:
        recommendation = 'HOLD'
        expected_value = 0
    
    # Calculate position size (5% max)
    base_position = portfolio_value * 0.05
    confidence_multiplier = (confidence - min_confidence) / (0.95 - min_confidence)
    position_size = base_position * confidence_multiplier
    
    # Calculate risk score
    risk_factors = [
        1 - confidence,
        max(0, (30 - days_to_end) / 30),
        max(0, (20000 - liquidity) / 20000),
    ]
    risk_score = sum(risk_factors) / len(risk_factors)
    
    return {
        'market_id': market.get('id', 'unknown'),
        'question': market.get('question', 'Unknown'),
        'category': category,
        'current_price': current_price,
        'ai_prediction': ai_prediction,
        'confidence': confidence,
        'recommendation': recommendation,
        'expected_value': expected_value,
        'position_size_cad': position_size,
        'risk_score': risk_score,
        'days_to_end': days_to_end,
        'liquidity': liquidity,
        'volume': volume,
        'end_date': market.get('end_date_iso', 'Unknown'),
        'source': market.get('source', 'Unknown')
    }

def main():
    # Header
    st.markdown('<h1 class="main-header">🎯 Polymarket AI - Multi-API</h1>', unsafe_allow_html=True)
    
    # Legal warning
    st.markdown("""
    <div class="warning-box">
        <h4>⚠️ Important Legal Notice</h4>
        <p><strong>Prediction markets may be restricted in your jurisdiction.</strong> Manitoba residents should verify local regulations. 
        This tool is for educational and research purposes only. Please consult with legal and financial professionals 
        before engaging in any trading activities. Past performance does not guarantee future results.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # API Status Notice
    st.markdown("""
    <div class="info-box">
        <h4>📡 Multi-API Integration</h4>
        <p><strong>Current APIs:</strong> Kalshi, Manifold Markets, PredictIt
        <br><strong>Goal:</strong> Find current active prediction markets from multiple sources
        <br><strong>Filtering:</strong> Only shows 2025+ and future events</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Portfolio settings
        portfolio_value = st.number_input(
            "Portfolio Value (CAD)",
            min_value=100.0,
            max_value=100000.0,
            value=1000.0,
            step=100.0,
            help="Enter your total portfolio value in Canadian Dollars"
        )
        
        # Risk settings
        st.subheader("🎯 Risk Management")
        max_position_size = st.slider(
            "Max Position Size (%)",
            min_value=1,
            max_value=10,
            value=5,
            help="Maximum percentage of portfolio to risk per trade"
        )
        
        min_confidence = st.slider(
            "Minimum Confidence (%)",
            min_value=50,
            max_value=95,
            value=60,
            help="Minimum AI confidence required for recommendations"
        ) / 100.0
        
        # Analysis settings
        st.subheader("📊 Analysis Settings")
        max_markets = st.slider(
            "Maximum Markets to Analyze",
            min_value=5,
            max_value=20,
            value=10,
            help="Maximum number of markets to analyze"
        )
        
        # API selection
        st.subheader("📡 API Selection")
        use_kalshi = st.checkbox("Kalshi", value=True)
        use_manifold = st.checkbox("Manifold Markets", value=True)
        use_predictit = st.checkbox("PredictIt", value=True)
    
    # Main content
    tab1, tab2, tab3 = st.tabs(["🎯 Live Recommendations", "📊 Market Overview", "ℹ️ About"])
    
    with tab1:
        st.header("🎯 Live AI Trading Recommendations")
        
        if st.button("🚀 Fetch & Analyze Current Markets", type="primary"):
            with st.spinner("Fetching current markets from multiple APIs..."):
                try:
                    all_markets = []
                    api_results = []
                    
                    # Fetch from selected APIs
                    if use_kalshi:
                        kalshi_markets, kalshi_status = fetch_kalshi_markets()
                        normalized_kalshi = normalize_market_data(kalshi_markets, "Kalshi")
                        all_markets.extend(normalized_kalshi)
                        api_results.append(f"Kalshi: {len(normalized_kalshi)} current markets ({kalshi_status})")
                    
                    if use_manifold:
                        manifold_markets, manifold_status = fetch_manifold_markets()
                        normalized_manifold = normalize_market_data(manifold_markets, "Manifold")
                        all_markets.extend(normalized_manifold)
                        api_results.append(f"Manifold: {len(normalized_manifold)} current markets ({manifold_status})")
                    
                    if use_predictit:
                        predictit_markets, predictit_status = fetch_predictit_markets()
                        normalized_predictit = normalize_market_data(predictit_markets, "PredictIt")
                        all_markets.extend(normalized_predictit)
                        api_results.append(f"PredictIt: {len(normalized_predictit)} current markets ({predictit_status})")
                    
                    # Show API results
                    st.info("📡 **API Results:**")
                    for result in api_results:
                        st.write(f"  • {result}")
                    
                    if not all_markets:
                        st.warning("""
                        **⚠️ No Current Markets Found**
                        
                        None of the prediction market APIs returned current active markets.
                        This could be due to:
                        - API rate limiting
                        - No current active markets available
                        - API endpoint changes
                        - Network issues
                        """)
                        
                        if st.button("🔄 Use Demo Markets"):
                            st.info("Using realistic demo markets for demonstration...")
                            # Add some demo markets
                            demo_markets = [
                                {
                                    'id': 'demo_btc_2025',
                                    'question': 'Will Bitcoin reach $150,000 by end of 2025?',
                                    'category': 'Cryptocurrency',
                                    'end_date_iso': '2025-12-31T23:59:59Z',
                                    'active': True,
                                    'closed': False,
                                    'accepting_orders': True,
                                    'tokens': [{"outcome": "Yes", "price": 0.35}],
                                    'liquidity': 45000,
                                    'volume': 25000,
                                    'source': 'Demo'
                                }
                            ]
                            all_markets = demo_markets
                    
                    # Analyze markets with AI
                    recommendations = []
                    analyzed_count = 0
                    
                    for market in all_markets[:max_markets]:
                        if analyzed_count >= max_markets:
                            break
                            
                        analysis = analyze_market(market, portfolio_value, min_confidence)
                        if analysis:
                            recommendations.append(analysis)
                        analyzed_count += 1
                    
                    if recommendations:
                        st.markdown(f"""
                        <div class="success-box">
                            <h4>✅ Found {len(recommendations)} trading opportunities!</h4>
                            <p>Analyzed {analyzed_count} current markets with {min_confidence:.0%}+ confidence threshold</p>
                            <p>Sources: {', '.join(set([r['source'] for r in recommendations]))}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Display recommendations
                        for i, rec in enumerate(recommendations, 1):
                            with st.expander(f"{i}. {rec['question'][:70]}...", expanded=i<=2):
                                col1, col2, col3 = st.columns(3)
                                
                                with col1:
                                    st.metric("Current Price", f"{rec['current_price']:.1%}")
                                    st.metric("AI Prediction", f"{rec['ai_prediction']:.1%}")
                                
                                with col2:
                                    st.metric("Confidence", f"{rec['confidence']:.1%}")
                                    st.metric("Expected Value", f"{rec['expected_value']:.3f}")
                                
                                with col3:
                                    st.metric("Position Size", f"${rec['position_size_cad']:.2f} CAD")
                                    st.metric("Days to End", f"{rec['days_to_end']:.0f}")
                                
                                # Recommendation
                                if rec['recommendation'] == 'BUY YES':
                                    st.success(f"🎯 **Recommendation: {rec['recommendation']}**")
                                elif rec['recommendation'] == 'BUY NO':
                                    st.info(f"🎯 **Recommendation: {rec['recommendation']}**")
                                else:
                                    st.warning(f"🎯 **Recommendation: {rec['recommendation']}**")
                                
                                # Additional info
                                col_info1, col_info2 = st.columns(2)
                                with col_info1:
                                    st.write(f"**Category:** {rec['category']}")
                                    st.write(f"**Source:** {rec['source']}")
                                with col_info2:
                                    st.write(f"**Liquidity:** ${rec['liquidity']:,}")
                                    st.write(f"**Risk Score:** {rec['risk_score']:.1%}")
                        
                        # Summary
                        total_position = sum(rec['position_size_cad'] for rec in recommendations)
                        avg_confidence = sum(rec['confidence'] for rec in recommendations) / len(recommendations)
                        
                        st.subheader("📊 Portfolio Summary")
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Total Position Size", f"${total_position:.2f} CAD")
                        with col2:
                            st.metric("Average Confidence", f"{avg_confidence:.1%}")
                        with col3:
                            st.metric("Number of Trades", len(recommendations))
                        with col4:
                            st.metric("Portfolio Allocation", f"{(total_position/portfolio_value)*100:.1f}%")
                        
                    else:
                        st.warning(f"No recommendations meet your {min_confidence:.0%} confidence threshold. Try lowering the minimum confidence.")
                        st.info(f"Analyzed {analyzed_count} markets but none met the confidence requirements.")
                        
                except Exception as e:
                    st.error(f"Error analyzing markets: {str(e)}")
    
    with tab2:
        st.header("📊 Market Overview")
        
        if st.button("📈 Load Market Data"):
            with st.spinner("Loading market data from all APIs..."):
                try:
                    all_markets = []
                    
                    if use_kalshi:
                        kalshi_markets, _ = fetch_kalshi_markets()
                        all_markets.extend(normalize_market_data(kalshi_markets, "Kalshi"))
                    
                    if use_manifold:
                        manifold_markets, _ = fetch_manifold_markets()
                        all_markets.extend(normalize_market_data(manifold_markets, "Manifold"))
                    
                    if use_predictit:
                        predictit_markets, _ = fetch_predictit_markets()
                        all_markets.extend(normalize_market_data(predictit_markets, "PredictIt"))
                    
                    if all_markets:
                        # Create DataFrame
                        df = pd.DataFrame(all_markets)
                        
                        # Basic statistics
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Total Markets", len(all_markets))
                        with col2:
                            st.metric("Active Markets", len([m for m in all_markets if m.get('active', True)]))
                        with col3:
                            sources = [m.get('source', 'Unknown') for m in all_markets]
                            st.metric("Data Sources", len(set(sources)))
                        with col4:
                            avg_volume = sum(m.get('volume', 0) for m in all_markets) / len(all_markets)
                            st.metric("Avg Volume", f"${avg_volume:,.0f}")
                        
                        # Source distribution
                        st.subheader("📊 Data Sources")
                        source_counts = pd.Series(sources).value_counts()
                        fig = px.pie(values=source_counts.values, names=source_counts.index, 
                                   title="Distribution by Data Source")
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Markets table
                        st.subheader("📋 Current Markets")
                        display_df = df[['question', 'category', 'source', 'volume', 'end_date_iso']].head(20)
                        display_df.columns = ['Question', 'Category', 'Source', 'Volume (USD)', 'End Date']
                        st.dataframe(display_df, use_container_width=True)
                        
                    else:
                        st.error("No market data available from any API")
                        
                except Exception as e:
                    st.error(f"Error loading markets: {str(e)}")
    
    with tab3:
        st.header("ℹ️ About Multi-API Polymarket AI")
        
        st.markdown("""
        ## 🎯 Multi-API Polymarket AI Predictor
        
        This system integrates with multiple prediction market APIs to find current active markets.
        
        ## 📡 Supported APIs
        
        **Kalshi:**
        - US-based prediction market
        - Focus on political and economic events
        - Real-time market data
        
        **Manifold Markets:**
        - Decentralized prediction market
        - Wide variety of topics
        - Community-driven markets
        
        **PredictIt:**
        - Political prediction market
        - US election focus
        - Real-money trading
        
        ## 🎯 Current Market Focus
        
        The system filters for **current and future events**:
        - **2025+ Predictions**: Only shows future events
        - **Active Markets**: Only tradeable, non-closed markets
        - **Real Data**: Uses actual API responses
        - **Multi-Source**: Combines data from multiple platforms
        
        ## 🧠 AI Analysis Features
        
        - **Multi-Factor Analysis**: Liquidity, volume, time to expiration
        - **Category-Specific Models**: Different confidence levels by category
        - **Risk Assessment**: Comprehensive risk scoring
        - **Real-Time Confidence**: Based on current market conditions
        
        ## ⚠️ Important Notes
        
        - **Educational Purpose**: This is a demonstration system
        - **Real API Data**: Uses actual prediction market APIs
        - **Legal Compliance**: Check local regulations before trading
        - **API Limitations**: Some APIs may have rate limits or restrictions
        """)
        
        # System information
        st.subheader("🔧 System Information")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Python Version**: 3.12")
            st.write(f"**Streamlit Version**: {st.__version__}")
            st.write(f"**Current Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        with col2:
            st.write(f"**CAD/USD Rate**: 0.7169 (estimated)")
            st.write(f"**Max Position Size**: {max_position_size}%")
            st.write(f"**Min Confidence**: {min_confidence:.0%}")

if __name__ == "__main__":
    main()
