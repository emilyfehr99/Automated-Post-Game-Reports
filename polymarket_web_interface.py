#!/usr/bin/env python3
"""
Polymarket AI Predictor - Web Interface
A Streamlit web interface for the Polymarket AI prediction system
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import time
from polymarket_ai_predictor import PolymarketAIPredictor

# Page configuration
st.set_page_config(
    page_title="Polymarket AI Predictor",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
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
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">🎯 Polymarket AI Predictor</h1>', unsafe_allow_html=True)
    
    # Legal warning
    st.markdown("""
    <div class="warning-box">
        <h4>⚠️ Important Legal Notice</h4>
        <p><strong>Polymarket is currently restricted in Ontario, Canada.</strong> Manitoba residents should verify local regulations. 
        This tool is for educational and research purposes only. Please consult with legal and financial professionals 
        before engaging in any trading activities. Past performance does not guarantee future results.</p>
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
            max_value=20,
            value=10,
            help="Maximum percentage of portfolio to risk per trade"
        )
        
        min_confidence = st.slider(
            "Minimum Confidence (%)",
            min_value=10,
            max_value=90,
            value=30,
            help="Minimum AI confidence required for recommendations"
        )
        
        # Analysis settings
        st.subheader("📊 Analysis Settings")
        num_events = st.slider(
            "Number of Events to Analyze",
            min_value=5,
            max_value=50,
            value=20,
            help="Number of active events to analyze"
        )
        
        historical_days = st.slider(
            "Historical Data (Days)",
            min_value=1,
            max_value=90,
            value=7,
            help="Number of days of historical data to include"
        )
    
    # Main content
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 Recommendations", "📊 Market Analysis", "📈 Performance", "ℹ️ About"])
    
    with tab1:
        st.header("🎯 AI Trading Recommendations")
        
        if st.button("🚀 Generate Recommendations", type="primary"):
            with st.spinner("Analyzing markets and generating recommendations..."):
                try:
                    # Initialize predictor
                    predictor = PolymarketAIPredictor()
                    predictor.max_position_size = max_position_size / 100.0
                    
                    # Generate recommendations
                    recommendations = predictor.generate_trading_recommendations(portfolio_value)
                    
                    if recommendations:
                        # Filter by confidence
                        filtered_recommendations = [
                            rec for rec in recommendations 
                            if rec['confidence'] >= min_confidence / 100.0
                        ]
                        
                        if filtered_recommendations:
                            st.markdown(f"""
                            <div class="success-box">
                                <h4>✅ Found {len(filtered_recommendations)} high-confidence opportunities!</h4>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Display recommendations
                            for i, rec in enumerate(filtered_recommendations[:10], 1):
                                with st.expander(f"{i}. {rec['question'][:60]}...", expanded=i<=3):
                                    col1, col2, col3 = st.columns(3)
                                    
                                    with col1:
                                        st.metric("Current Price", f"{rec['current_price']:.1%}")
                                        st.metric("AI Prediction", f"{rec['prediction']:.1%}")
                                    
                                    with col2:
                                        st.metric("Confidence", f"{rec['confidence']:.1%}")
                                        st.metric("Expected Value", f"{rec['expected_value']:.3f}")
                                    
                                    with col3:
                                        st.metric("Position Size", f"${rec['position_size_cad']:.2f} CAD")
                                        st.metric("Risk Score", f"{rec['risk_score']:.1%}")
                                    
                                    # Recommendation
                                    if rec['recommendation'] == 'BUY YES':
                                        st.success(f"🎯 **Recommendation: {rec['recommendation']}**")
                                    elif rec['recommendation'] == 'BUY NO':
                                        st.info(f"🎯 **Recommendation: {rec['recommendation']}**")
                                    else:
                                        st.warning(f"🎯 **Recommendation: {rec['recommendation']}**")
                                    
                                    # Additional info
                                    st.write(f"**Category:** {rec['category']}")
                                    st.write(f"**End Date:** {rec['end_date']}")
                                    st.write(f"**Kelly Fraction:** {rec['kelly_fraction']:.1%}")
                        else:
                            st.warning("No recommendations meet your confidence threshold. Try lowering the minimum confidence or check back later.")
                    else:
                        st.error("No recommendations generated. Please check your connection and try again.")
                        
                except Exception as e:
                    st.error(f"Error generating recommendations: {str(e)}")
    
    with tab2:
        st.header("📊 Market Analysis")
        
        if st.button("📈 Analyze Current Markets"):
            with st.spinner("Fetching market data..."):
                try:
                    predictor = PolymarketAIPredictor()
                    events = predictor.fetch_polymarket_events(limit=num_events)
                    
                    if events:
                        # Create DataFrame for analysis
                        df = pd.DataFrame(events)
                        
                        # Basic statistics
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Total Events", len(events))
                        with col2:
                            st.metric("Active Markets", len([e for e in events if e.get('active', False)]))
                        with col3:
                            categories = [e.get('category', 'Other') for e in events]
                            st.metric("Categories", len(set(categories)))
                        with col4:
                            avg_volume = sum(e.get('volume', 0) for e in events) / len(events)
                            st.metric("Avg Volume", f"${avg_volume:,.0f}")
                        
                        # Category distribution
                        st.subheader("📊 Market Categories")
                        category_counts = pd.Series(categories).value_counts()
                        fig = px.pie(values=category_counts.values, names=category_counts.index, 
                                   title="Distribution of Market Categories")
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Volume analysis
                        st.subheader("💰 Volume Analysis")
                        volumes = [e.get('volume', 0) for e in events if e.get('volume', 0) > 0]
                        if volumes:
                            fig = px.histogram(x=volumes, title="Volume Distribution", 
                                             labels={'x': 'Volume (USD)', 'y': 'Count'})
                            st.plotly_chart(fig, use_container_width=True)
                        
                        # Recent events table
                        st.subheader("📋 Recent Events")
                        display_df = df[['question', 'category', 'volume', 'endDate']].head(20)
                        display_df.columns = ['Question', 'Category', 'Volume (USD)', 'End Date']
                        st.dataframe(display_df, use_container_width=True)
                        
                    else:
                        st.error("No market data available. Please check your connection.")
                        
                except Exception as e:
                    st.error(f"Error analyzing markets: {str(e)}")
    
    with tab3:
        st.header("📈 Performance Tracking")
        
        st.info("Performance tracking features will be available in future updates. This will include:")
        st.write("• Historical prediction accuracy")
        st.write("• Portfolio performance metrics")
        st.write("• Risk-adjusted returns")
        st.write("• Trade execution tracking")
        
        # Placeholder for future performance charts
        st.subheader("📊 Performance Metrics (Coming Soon)")
        
        # Sample data for demonstration
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
        sample_returns = np.random.normal(0.001, 0.02, len(dates)).cumsum()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dates, y=sample_returns, mode='lines', name='Portfolio Value'))
        fig.update_layout(title="Portfolio Performance (Sample Data)", 
                         xaxis_title="Date", yaxis_title="Cumulative Returns")
        st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.header("ℹ️ About Polymarket AI Predictor")
        
        st.markdown("""
        ## 🎯 What is Polymarket AI Predictor?
        
        The Polymarket AI Predictor is an advanced machine learning system designed to analyze prediction markets 
        and provide intelligent trading recommendations. It combines multiple AI models with real-time market data 
        to help users make informed decisions.
        
        ## 🧠 How It Works
        
        1. **Data Collection**: Fetches real-time data from Polymarket's API
        2. **Feature Engineering**: Extracts relevant features from market data
        3. **AI Analysis**: Uses multiple machine learning models for predictions
        4. **Risk Management**: Applies Kelly Criterion for position sizing
        5. **Recommendations**: Generates actionable trading suggestions
        
        ## 🔧 Key Features
        
        - **Multi-Model AI**: Combines Random Forest, Gradient Boosting, and Logistic Regression
        - **Real-Time Analysis**: Live market data and price updates
        - **Risk Management**: Kelly Criterion-based position sizing
        - **CAD Support**: Native Canadian Dollar integration
        - **Confidence Scoring**: AI confidence levels for each recommendation
        - **Regulatory Compliance**: Built-in warnings for Canadian users
        
        ## ⚠️ Important Disclaimers
        
        - **Legal**: Polymarket is restricted in Ontario and may be restricted in other provinces
        - **Financial**: Past performance does not guarantee future results
        - **Risk**: Only invest what you can afford to lose
        - **Compliance**: Consult legal/financial professionals before trading
        
        ## 🛠️ Technical Details
        
        - **Language**: Python 3.8+
        - **ML Libraries**: Scikit-learn, XGBoost, LightGBM
        - **Data Sources**: Polymarket API, Yahoo Finance
        - **Interface**: Streamlit web application
        
        ## 📞 Support
        
        For questions or issues, please refer to the documentation or contact support.
        """)
        
        # System information
        st.subheader("🔧 System Information")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Python Version**: {st.__version__}")
            st.write(f"**Streamlit Version**: {st.__version__}")
            st.write(f"**Current Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        with col2:
            st.write(f"**CAD/USD Rate**: {predictor.cad_to_usd_rate:.4f}")
            st.write(f"**Max Position Size**: {max_position_size}%")
            st.write(f"**Min Confidence**: {min_confidence}%")

if __name__ == "__main__":
    main()
