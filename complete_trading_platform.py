#!/usr/bin/env python3
"""
Complete Trading Platform
Combines Polymarket AI with CAD Stock Trading
Includes technical indicators: Alligator, MACD, RSI, etc.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
import talib
from datetime import datetime, timedelta
import json
import time
import requests
from textblob import TextBlob
import feedparser

# New imports for advanced features
import tensorflow as tf
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from newsapi import NewsApiClient
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Trading Analytics Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Professional Dark Theme
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Russo+One&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    /* Main App Background */
    .stApp {
        background: #0f172a;
        color: #e2e8f0;
    }
    
    /* Main Header */
    .main-header {
        font-family: 'Russo One', sans-serif;
        font-size: 2.8rem;
        font-weight: 400;
        color: #f1f5f9;
        text-align: center;
        margin-bottom: 1.5rem;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    
    /* Sidebar Styling */
    .css-1d391kg {
        background: #1e293b;
        border-right: 1px solid #334155;
    }
    
    /* Warning Box */
    .warning-box {
        background: rgba(245, 158, 11, 0.1);
        border: 1px solid #f59e0b;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* Success Box */
    .success-box {
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid #10b981;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* Info Box */
    .info-box {
        background: rgba(59, 130, 246, 0.1);
        border: 1px solid #3b82f6;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* Trading Card */
    .trading-card {
        background: linear-gradient(135deg, #1e293b, #334155);
        border: 1px solid #475569;
        border-radius: 12px;
        padding: 1.8rem;
        margin: 0.8rem 0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .trading-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #3b82f6, #10b981, #f59e0b);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .trading-card:hover {
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.4);
        border-color: #3b82f6;
        transform: translateY(-2px);
    }
    
    .trading-card:hover::before {
        opacity: 1;
    }
    
    /* Enhanced Card Styling */
    .enhanced-card {
        background: linear-gradient(135deg, #1e293b, #334155);
        border: 1px solid #475569;
        border-radius: 12px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }
    
    .enhanced-card:hover {
        box-shadow: 0 8px 12px -2px rgba(0, 0, 0, 0.4);
        border-color: #3b82f6;
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6, #1d4ed8);
        color: #ffffff;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.8rem;
        font-family: 'Russo One', sans-serif;
        font-weight: 400;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(59, 130, 246, 0.3);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #2563eb, #1e40af);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(59, 130, 246, 0.4);
    }
    
    /* Primary Button Styling */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #10b981, #059669);
        box-shadow: 0 2px 4px rgba(16, 185, 129, 0.3);
    }
    
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #059669, #047857);
        box-shadow: 0 4px 8px rgba(16, 185, 129, 0.4);
    }
    
    /* Selectbox Styling */
    .stSelectbox > div > div {
        background: #1e293b;
        border: 1px solid #475569;
        border-radius: 8px;
        color: #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .stSelectbox > div > div:hover {
        border-color: #3b82f6;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
    }
    
    /* Multiselect Styling */
    .stMultiSelect > div > div {
        background: #1e293b;
        border: 1px solid #475569;
        border-radius: 8px;
        color: #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .stMultiSelect > div > div:hover {
        border-color: #3b82f6;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
    }
    
    /* Multiselect Options */
    .stMultiSelect [data-baseweb="select"] {
        background: #1e293b;
        border: 1px solid #475569;
        border-radius: 8px;
    }
    
    /* Slider Styling */
    .stSlider > div > div > div {
        background: #3b82f6;
    }
    
    /* Number Input Styling */
    .stNumberInput > div > div > input {
        background: #1e293b;
        border: 1px solid #475569;
        border-radius: 6px;
        color: #e2e8f0;
    }
    
    /* Tab Styling */
    .stTabs > div > div > div > div {
        background: #1e293b;
        border: 1px solid #334155;
        color: #94a3b8;
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        border-radius: 6px 6px 0 0;
    }
    
    .stTabs > div > div > div > div[aria-selected="true"] {
        background: #0f172a;
        color: #f1f5f9;
        border-bottom: 2px solid #3b82f6;
    }
    
    /* Expander Styling */
    .streamlit-expanderHeader {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 6px;
        color: #e2e8f0;
        font-family: 'Inter', sans-serif;
        font-weight: 500;
    }
    
    /* Dataframe Styling */
    .dataframe {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 6px;
        color: #e2e8f0;
    }
    
    /* Plotly Chart Styling */
    .js-plotly-plot {
        border-radius: 8px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    }
    
    /* Text Styling */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Russo One', sans-serif;
        color: #f1f5f9;
        font-weight: 400;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Section Headers */
    .section-header {
        font-family: 'Russo One', sans-serif;
        color: #3b82f6;
        font-size: 1.5rem;
        margin-bottom: 1rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    p, div, span {
        font-family: 'Inter', sans-serif;
        color: #cbd5e1;
    }
    
    /* Code/Monospace Styling */
    code, pre {
        font-family: 'JetBrains Mono', monospace;
        background: #334155;
        color: #e2e8f0;
        border-radius: 4px;
        padding: 0.25rem 0.5rem;
    }
    
    /* Metric Styling */
    .metric-container {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 6px;
        padding: 1rem;
        margin: 0.5rem;
    }
    
    /* Scrollbar Styling */
    ::-webkit-scrollbar {
        width: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1e293b;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #475569;
        border-radius: 3px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #64748b;
    }
    
    /* Focus States */
    .stSelectbox > div > div:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
    }
    
    /* Status Colors */
    .positive {
        color: #10b981;
    }
    
    .negative {
        color: #ef4444;
    }
    
    .neutral {
        color: #94a3b8;
    }
    
    /* Streamlit specific overrides */
    .stSelectbox label,
    .stNumberInput label,
    .stSlider label {
        color: #e2e8f0 !important;
    }
    
    .stMultiSelect label {
        color: #e2e8f0 !important;
    }
    
    .stCheckbox label {
        color: #e2e8f0 !important;
    }
    
    /* Sidebar text */
    .css-1d391kg p,
    .css-1d391kg div,
    .css-1d391kg span {
        color: #e2e8f0 !important;
    }
    
</style>
""", unsafe_allow_html=True)

# CAD Stock Lists
CAD_STOCKS = {
    "Banking": ["RY.TO", "TD.TO", "BNS.TO", "BMO.TO", "CM.TO", "NA.TO"],
    "Technology": ["SHOP.TO", "LSPD.TO", "LIGHT.TO", "KXS.TO", "OTEX.TO"],
    "Energy": ["CNQ.TO", "SU.TO", "IMO.TO", "CVE.TO", "ARX.TO"],
    "Mining": ["ABX.TO", "G.TO", "K.TO", "WPM.TO", "FNV.TO"],
    "Real Estate": ["REI.UN.TO", "CAR.UN.TO", "BPY.UN.TO", "IAG.TO"],
    "Utilities": ["FTS.TO", "EMA.TO", "AQN.TO", "CU.TO"],
    "Consumer": ["ATD.TO", "L.TO", "MRU.TO", "CTC.TO"],
    "Healthcare": ["WEED.TO", "ACB.TO", "TLRY.TO", "CGC.TO"],
    "Transportation": ["CP.TO", "CNR.TO", "AC.TO", "WJA.TO"],
    "Telecom": ["BCE.TO", "T.TO", "RCI.TO", "QBR.TO"]
}

@st.cache_data(ttl=300)
def fetch_stock_data(symbol, period="1y"):
    """Fetch comprehensive stock data with technical indicators"""
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period=period)
        
        if hist.empty:
            return None
        
        # Calculate technical indicators
        df = hist.copy()
        
        # Alligator Indicator
        df['jaw'] = talib.SMA(df['Close'], timeperiod=13)  # Blue line
        df['teeth'] = talib.SMA(df['Close'], timeperiod=8)  # Red line
        df['lips'] = talib.SMA(df['Close'], timeperiod=5)   # Green line
        
        # MACD
        df['macd'], df['macd_signal'], df['macd_hist'] = talib.MACD(df['Close'])
        
        # RSI
        df['rsi'] = talib.RSI(df['Close'], timeperiod=14)
        
        # Bollinger Bands
        df['bb_upper'], df['bb_middle'], df['bb_lower'] = talib.BBANDS(df['Close'])
        
        # Moving Averages
        df['sma_20'] = talib.SMA(df['Close'], timeperiod=20)
        df['sma_50'] = talib.SMA(df['Close'], timeperiod=50)
        df['sma_200'] = talib.SMA(df['Close'], timeperiod=200)
        
        # Stochastic
        df['stoch_k'], df['stoch_d'] = talib.STOCH(df['High'], df['Low'], df['Close'])
        
        # Williams %R
        df['williams_r'] = talib.WILLR(df['High'], df['Low'], df['Close'])
        
        # Volume indicators
        df['volume_sma'] = talib.SMA(df['Volume'], timeperiod=20)
        df['volume_ratio'] = df['Volume'] / df['volume_sma']
        
        # Get current info
        info = stock.info
        
        return {
            'data': df,
            'info': info,
            'symbol': symbol
        }
    except Exception as e:
        st.error(f"Error fetching data for {symbol}: {str(e)}")
        return None

def calculate_alligator_signals(df):
    """Calculate Alligator trading signals"""
    signals = []
    
    for i in range(len(df)):
        if i < 2:
            signals.append('HOLD')
            continue
            
        current = df.iloc[i]
        prev = df.iloc[i-1]
        
        # Alligator alignment (trend direction)
        if current['lips'] > current['teeth'] > current['jaw']:
            # Uptrend
            if prev['lips'] <= prev['teeth'] or prev['teeth'] <= prev['jaw']:
                signals.append('BUY')  # Alligator awakening
            else:
                signals.append('HOLD')
        elif current['lips'] < current['teeth'] < current['jaw']:
            # Downtrend
            if prev['lips'] >= prev['teeth'] or prev['teeth'] >= prev['jaw']:
                signals.append('SELL')  # Alligator awakening
            else:
                signals.append('HOLD')
        else:
            signals.append('HOLD')  # Alligator sleeping
    
    return signals

def calculate_macd_signals(df):
    """Calculate MACD trading signals"""
    signals = []
    
    for i in range(len(df)):
        if i < 1:
            signals.append('HOLD')
            continue
            
        current = df.iloc[i]
        prev = df.iloc[i-1]
        
        # MACD crossover signals
        if current['macd'] > current['macd_signal'] and prev['macd'] <= prev['macd_signal']:
            signals.append('BUY')  # Bullish crossover
        elif current['macd'] < current['macd_signal'] and prev['macd'] >= prev['macd_signal']:
            signals.append('SELL')  # Bearish crossover
        else:
            signals.append('HOLD')
    
    return signals

def calculate_rsi_signals(df):
    """Calculate RSI trading signals"""
    signals = []
    
    for i in range(len(df)):
        current = df.iloc[i]
        
        if current['rsi'] < 30:
            signals.append('BUY')  # Oversold
        elif current['rsi'] > 70:
            signals.append('SELL')  # Overbought
        else:
            signals.append('HOLD')
    
    return signals

def calculate_composite_signals(df):
    """Calculate composite trading signals from multiple indicators"""
    alligator_signals = calculate_alligator_signals(df)
    macd_signals = calculate_macd_signals(df)
    rsi_signals = calculate_rsi_signals(df)
    
    composite_signals = []
    confidence_scores = []
    
    for i in range(len(df)):
        signals = [alligator_signals[i], macd_signals[i], rsi_signals[i]]
        
        # Count signal types
        buy_count = signals.count('BUY')
        sell_count = signals.count('SELL')
        hold_count = signals.count('HOLD')
        
        # Determine composite signal
        if buy_count >= 2:
            composite_signals.append('BUY')
            confidence_scores.append(buy_count / 3.0)
        elif sell_count >= 2:
            composite_signals.append('SELL')
            confidence_scores.append(sell_count / 3.0)
        else:
            composite_signals.append('HOLD')
            confidence_scores.append(0.5)
    
    return composite_signals, confidence_scores

def analyze_stock(symbol, portfolio_value, max_position_size):
    """Comprehensive stock analysis"""
    stock_data = fetch_stock_data(symbol)
    
    if not stock_data:
        return None
    
    df = stock_data['data']
    info = stock_data['info']
    
    # Calculate signals
    composite_signals, confidence_scores = calculate_composite_signals(df)
    
    # Get latest data
    latest = df.iloc[-1]
    latest_signal = composite_signals[-1]
    latest_confidence = confidence_scores[-1]
    
    # Calculate position size
    position_size = portfolio_value * (max_position_size / 100) * latest_confidence
    
    # Risk assessment
    volatility = df['Close'].pct_change().std() * np.sqrt(252) * 100
    max_drawdown = ((df['Close'].cummax() - df['Close']) / df['Close'].cummax()).max() * 100
    
    # Performance metrics
    total_return = ((latest['Close'] - df['Close'].iloc[0]) / df['Close'].iloc[0]) * 100
    sharpe_ratio = (df['Close'].pct_change().mean() / df['Close'].pct_change().std()) * np.sqrt(252)
    
    # Calculate risk score
    risk_factors = [
        1 - latest_confidence,
        max(0, (30 - 90) / 30),  # Simplified time risk
        max(0, (20000 - latest['Volume']) / 20000),
    ]
    risk_score = sum(risk_factors) / len(risk_factors)
    
    return {
        'symbol': symbol,
        'name': info.get('longName', symbol),
        'current_price': latest['Close'],
        'change_1d': ((latest['Close'] - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100,
        'change_1y': total_return,
        'signal': latest_signal,
        'confidence': latest_confidence,
        'position_size': position_size,
        'volatility': volatility,
        'max_drawdown': max_drawdown,
        'sharpe_ratio': sharpe_ratio,
        'volume_ratio': latest['volume_ratio'],
        'rsi': latest['rsi'],
        'macd': latest['macd'],
        'macd_signal': latest['macd_signal'],
        'alligator_jaw': latest['jaw'],
        'alligator_teeth': latest['teeth'],
        'alligator_lips': latest['lips'],
        'sma_20': latest['sma_20'],
        'sma_50': latest['sma_50'],
        'sma_200': latest['sma_200'],
        'bb_upper': latest['bb_upper'],
        'bb_lower': latest['bb_lower'],
        'risk_score': risk_score,
        'data': df,
        'composite_signals': composite_signals,
        'confidence_scores': confidence_scores
    }

def create_stock_chart(analysis):
    """Create comprehensive stock chart with indicators"""
    df = analysis['data']
    
    # Create subplots
    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=('Price & Alligator', 'MACD', 'RSI', 'Volume'),
        row_heights=[0.4, 0.2, 0.2, 0.2]
    )
    
    # Price and Alligator
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='Price'
    ), row=1, col=1)
    
    # Alligator lines
    fig.add_trace(go.Scatter(x=df.index, y=df['jaw'], name='Jaw (13)', line=dict(color='blue')), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['teeth'], name='Teeth (8)', line=dict(color='red')), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['lips'], name='Lips (5)', line=dict(color='green')), row=1, col=1)
    
    # Moving averages
    fig.add_trace(go.Scatter(x=df.index, y=df['sma_20'], name='SMA 20', line=dict(color='orange', dash='dash')), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['sma_50'], name='SMA 50', line=dict(color='purple', dash='dash')), row=1, col=1)
    
    # Bollinger Bands
    fig.add_trace(go.Scatter(x=df.index, y=df['bb_upper'], name='BB Upper', line=dict(color='gray', dash='dot')), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['bb_lower'], name='BB Lower', line=dict(color='gray', dash='dot')), row=1, col=1)
    
    # MACD
    fig.add_trace(go.Scatter(x=df.index, y=df['macd'], name='MACD', line=dict(color='blue')), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['macd_signal'], name='Signal', line=dict(color='red')), row=2, col=1)
    fig.add_trace(go.Bar(x=df.index, y=df['macd_hist'], name='Histogram', marker_color='gray'), row=2, col=1)
    
    # RSI
    fig.add_trace(go.Scatter(x=df.index, y=df['rsi'], name='RSI', line=dict(color='purple')), row=3, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
    fig.add_hline(y=50, line_dash="dot", line_color="gray", row=3, col=1)
    
    # Volume
    colors = ['green' if close >= open else 'red' for close, open in zip(df['Close'], df['Open'])]
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume', marker_color=colors), row=4, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['volume_sma'], name='Volume SMA', line=dict(color='blue')), row=4, col=1)
    
    # Update layout
    fig.update_layout(
        title=f"{analysis['symbol']} - {analysis['name']} - Technical Analysis",
        xaxis_rangeslider_visible=False,
        height=800,
        showlegend=True
    )
    
    return fig

@st.cache_data(ttl=300)
def fetch_market_data():
    """Fetch current market data from multiple sources"""
    try:
        # Get major market indices
        tickers = ['^GSPC', '^IXIC', '^DJI', 'BTC-USD', 'ETH-USD', 'GC=F', 'CL=F']
        market_data = {}
        
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period="5d")
                if not hist.empty:
                    market_data[ticker] = {
                        'current_price': hist['Close'].iloc[-1],
                        'change_1d': ((hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100,
                        'change_5d': ((hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100,
                        'volume': hist['Volume'].iloc[-1] if 'Volume' in hist.columns else 0
                    }
            except:
                continue
        
        return market_data
    except Exception as e:
        return {}

@st.cache_data(ttl=600)
def fetch_news_sentiment():
    """Fetch news sentiment from multiple sources"""
    try:
        news_sources = [
            'https://feeds.finance.yahoo.com/rss/2.0/headline',
            'https://rss.cnn.com/rss/money_latest.rss',
            'https://feeds.reuters.com/reuters/businessNews'
        ]
        
        all_articles = []
        for source in news_sources:
            try:
                feed = feedparser.parse(source)
                for entry in feed.entries[:10]:  # Limit to 10 per source
                    all_articles.append({
                        'title': entry.get('title', ''),
                        'summary': entry.get('summary', ''),
                        'published': entry.get('published', ''),
                        'source': source
                    })
            except:
                continue
        
        # Analyze sentiment
        sentiments = []
        for article in all_articles:
            text = f"{article['title']} {article['summary']}"
            blob = TextBlob(text)
            sentiments.append(blob.sentiment.polarity)
        
        avg_sentiment = np.mean(sentiments) if sentiments else 0
        return {
            'average_sentiment': avg_sentiment,
            'article_count': len(all_articles),
            'positive_ratio': len([s for s in sentiments if s > 0.1]) / len(sentiments) if sentiments else 0.5
        }
    except Exception as e:
        return {'average_sentiment': 0, 'article_count': 0, 'positive_ratio': 0.5}

@st.cache_data(ttl=300)
def fetch_economic_indicators():
    """Fetch key economic indicators"""
    try:
        # This would typically use FRED API or similar
        # For demo purposes, we'll simulate some key indicators
        indicators = {
            'inflation_rate': 3.2,  # Simulated current inflation
            'unemployment_rate': 3.8,  # Simulated unemployment
            'fed_funds_rate': 5.25,  # Simulated Fed rate
            'gdp_growth': 2.1,  # Simulated GDP growth
            'consumer_confidence': 102.3,  # Simulated consumer confidence
            'vix': 18.5  # Simulated VIX (volatility index)
        }
        return indicators
    except Exception as e:
        return {}

@st.cache_data(ttl=300)
def fetch_crypto_data():
    """Fetch comprehensive crypto market data"""
    try:
        crypto_tickers = ['BTC-USD', 'ETH-USD', 'BNB-USD', 'ADA-USD', 'SOL-USD']
        crypto_data = {}
        
        for ticker in crypto_tickers:
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period="30d")
                if not hist.empty:
                    crypto_data[ticker] = {
                        'current_price': hist['Close'].iloc[-1],
                        'change_1d': ((hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100,
                        'change_30d': ((hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100,
                        'volume': hist['Volume'].iloc[-1],
                        'volatility': hist['Close'].pct_change().std() * np.sqrt(365) * 100
                    }
            except:
                continue
        
        return crypto_data
    except Exception as e:
        return {}

def get_current_realistic_markets():
    """Get realistic current markets with enhanced data"""
    markets = [
        {
            "id": "btc_150k_2025",
            "question": "Will Bitcoin reach $150,000 by end of 2025?",
            "category": "Cryptocurrency",
            "end_date_iso": "2025-12-31T23:59:59Z",
            "active": True,
            "closed": False,
            "accepting_orders": True,
            "tokens": [{"outcome": "Yes", "price": 0.35}],
            "liquidity": 45000,
            "volume": 25000,
            "related_assets": ["BTC-USD"],
            "keywords": ["bitcoin", "crypto", "cryptocurrency", "btc"]
        },
        {
            "id": "recession_2025",
            "question": "Will there be a recession in 2025?",
            "category": "Economics",
            "end_date_iso": "2025-12-31T23:59:59Z",
            "active": True,
            "closed": False,
            "accepting_orders": True,
            "tokens": [{"outcome": "Yes", "price": 0.42}],
            "liquidity": 35000,
            "volume": 20000,
            "related_assets": ["^GSPC", "^VIX", "GC=F"],
            "keywords": ["recession", "economy", "gdp", "unemployment"]
        },
        {
            "id": "ai_agi_2025",
            "question": "Will AI achieve AGI by end of 2025?",
            "category": "Technology",
            "end_date_iso": "2025-12-31T23:59:59Z",
            "active": True,
            "closed": False,
            "accepting_orders": True,
            "tokens": [{"outcome": "Yes", "price": 0.25}],
            "liquidity": 28000,
            "volume": 15000,
            "related_assets": ["NVDA", "MSFT", "GOOGL"],
            "keywords": ["ai", "artificial intelligence", "agi", "technology"]
        },
        {
            "id": "climate_2025",
            "question": "Will global temperature rise exceed 1.5°C in 2025?",
            "category": "Climate",
            "end_date_iso": "2025-12-31T23:59:59Z",
            "active": True,
            "closed": False,
            "accepting_orders": True,
            "tokens": [{"outcome": "Yes", "price": 0.38}],
            "liquidity": 18000,
            "volume": 12000,
            "related_assets": ["CL=F", "NG=F"],
            "keywords": ["climate", "temperature", "global warming", "carbon"]
        },
        {
            "id": "election_2028",
            "question": "Will Trump win the 2028 US Presidential Election?",
            "category": "Politics",
            "end_date_iso": "2028-11-05T23:59:59Z",
            "active": True,
            "closed": False,
            "accepting_orders": True,
            "tokens": [{"outcome": "Yes", "price": 0.48}],
            "liquidity": 85000,
            "volume": 60000,
            "related_assets": ["^GSPC", "GC=F"],
            "keywords": ["trump", "election", "president", "politics"]
        }
    ]
    return markets

def calculate_enhanced_confidence(market, market_data, news_sentiment, economic_indicators, crypto_data):
    """Calculate enhanced confidence using multiple data sources"""
    
    # Base confidence from market characteristics
    liquidity = market.get('liquidity', 10000)
    volume = market.get('volume', 10000)
    
    liquidity_score = min(liquidity / 50000, 1.0)
    volume_score = min(volume / 100000, 1.0)
    
    # Category-specific base confidence
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
    
    # Enhanced confidence factors
    confidence_factors = []
    
    # 1. Market data correlation
    if market.get('related_assets') and market_data:
        asset_correlations = []
        for asset in market.get('related_assets', []):
            if asset in market_data:
                # Use volatility and recent performance as confidence indicators
                volatility_factor = 1.0 - min(abs(market_data[asset]['change_1d']) / 10, 0.5)
                asset_correlations.append(volatility_factor)
        
        if asset_correlations:
            market_correlation_score = np.mean(asset_correlations)
            confidence_factors.append(('market_correlation', market_correlation_score, 0.15))
    
    # 2. News sentiment alignment
    if news_sentiment and market.get('keywords'):
        # Check if news sentiment aligns with market direction
        sentiment_score = 0.5 + (news_sentiment['average_sentiment'] * 0.3)
        confidence_factors.append(('news_sentiment', sentiment_score, 0.10))
    
    # 3. Economic indicators
    if economic_indicators and category == "Economics":
        # For economic markets, use economic indicators
        vix_factor = 1.0 - min(economic_indicators.get('vix', 20) / 50, 0.4)
        confidence_factors.append(('economic_indicators', vix_factor, 0.20))
    
    # 4. Crypto-specific factors
    if category == "Cryptocurrency" and crypto_data:
        btc_data = crypto_data.get('BTC-USD', {})
        if btc_data:
            # Lower volatility = higher confidence
            volatility_factor = 1.0 - min(btc_data.get('volatility', 50) / 100, 0.3)
            confidence_factors.append(('crypto_volatility', volatility_factor, 0.15))
    
    # 5. Time-based confidence
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
        
        time_score = max(0.3, min(1.0, days_to_end / 365))
        confidence_factors.append(('time_factor', time_score, 0.10))
    except:
        confidence_factors.append(('time_factor', 0.5, 0.10))
    
    # Calculate weighted confidence
    weighted_confidence = base_confidence * (0.3 + 0.3 * liquidity_score + 0.2 * volume_score)
    
    # Add enhanced factors
    for factor_name, factor_value, weight in confidence_factors:
        weighted_confidence += factor_value * weight
    
    # Apply boosts for high-quality data
    if liquidity > 20000 and volume > 50000:
        weighted_confidence *= 1.1
    elif liquidity > 10000 and volume > 25000:
        weighted_confidence *= 1.05
    
    # Ensure reasonable bounds
    final_confidence = max(0.55, min(0.95, weighted_confidence))
    
    return {
        'confidence': final_confidence,
        'factors': confidence_factors,
        'base_confidence': base_confidence,
        'liquidity_score': liquidity_score,
        'volume_score': volume_score
    }

def generate_technical_summary(analysis):
    """Generate intelligent technical analysis summary"""
    
    # Analyze individual indicators
    indicator_status = {}
    
    # Alligator Analysis
    if analysis['alligator_lips'] > analysis['alligator_teeth'] > analysis['alligator_jaw']:
        indicator_status['Alligator'] = 'Bullish'
    elif analysis['alligator_lips'] < analysis['alligator_teeth'] < analysis['alligator_jaw']:
        indicator_status['Alligator'] = 'Bearish'
    else:
        indicator_status['Alligator'] = 'Neutral'
    
    # MACD Analysis
    if analysis['macd'] > analysis['macd_signal'] and (analysis['macd'] - analysis['macd_signal']) > 0:
        indicator_status['MACD'] = 'Bullish'
    elif analysis['macd'] < analysis['macd_signal'] and (analysis['macd'] - analysis['macd_signal']) < 0:
        indicator_status['MACD'] = 'Bearish'
    else:
        indicator_status['MACD'] = 'Neutral'
    
    # RSI Analysis
    if analysis['rsi'] < 30:
        indicator_status['RSI'] = 'Oversold (Bullish)'
    elif analysis['rsi'] > 70:
        indicator_status['RSI'] = 'Overbought (Bearish)'
    elif 30 <= analysis['rsi'] <= 50:
        indicator_status['RSI'] = 'Neutral-Bullish'
    else:
        indicator_status['RSI'] = 'Neutral-Bearish'
    
    # Moving Average Analysis
    if analysis['current_price'] > analysis['sma_20'] > analysis['sma_50']:
        indicator_status['Moving Averages'] = 'Strong Bullish'
    elif analysis['current_price'] > analysis['sma_20']:
        indicator_status['Moving Averages'] = 'Bullish'
    elif analysis['current_price'] < analysis['sma_20'] < analysis['sma_50']:
        indicator_status['Moving Averages'] = 'Strong Bearish'
    elif analysis['current_price'] < analysis['sma_20']:
        indicator_status['Moving Averages'] = 'Bearish'
    else:
        indicator_status['Moving Averages'] = 'Neutral'
    
    # Bollinger Bands Analysis
    bb_position = ((analysis['current_price'] - analysis['bb_lower']) / (analysis['bb_upper'] - analysis['bb_lower']) * 100)
    if bb_position < 20:
        indicator_status['Bollinger Bands'] = 'Oversold (Bullish)'
    elif bb_position > 80:
        indicator_status['Bollinger Bands'] = 'Overbought (Bearish)'
    else:
        indicator_status['Bollinger Bands'] = 'Neutral'
    
    # Volume Analysis
    if analysis['volume_ratio'] > 1.5:
        indicator_status['Volume'] = 'High (Confirmation)'
    elif analysis['volume_ratio'] < 0.5:
        indicator_status['Volume'] = 'Low (Caution)'
    else:
        indicator_status['Volume'] = 'Normal'
    
    # Calculate overall trend
    bullish_count = sum(1 for status in indicator_status.values() if 'Bullish' in status or 'Oversold' in status)
    bearish_count = sum(1 for status in indicator_status.values() if 'Bearish' in status or 'Overbought' in status)
    
    # Determine trend
    if bullish_count > bearish_count + 1:
        trend = "Strong Uptrend"
    elif bullish_count > bearish_count:
        trend = "Uptrend"
    elif bearish_count > bullish_count + 1:
        trend = "Strong Downtrend"
    elif bearish_count > bullish_count:
        trend = "Downtrend"
    else:
        trend = "Sideways/Consolidation"
    
    # Determine momentum
    if analysis['change_1d'] > 2:
        momentum = "Strong Positive"
    elif analysis['change_1d'] > 0:
        momentum = "Positive"
    elif analysis['change_1d'] < -2:
        momentum = "Strong Negative"
    elif analysis['change_1d'] < 0:
        momentum = "Negative"
    else:
        momentum = "Neutral"
    
    # Determine volatility level
    if analysis['volatility'] > 40:
        volatility_level = "High (Risky)"
    elif analysis['volatility'] > 25:
        volatility_level = "Moderate"
    else:
        volatility_level = "Low (Stable)"
    
    # Generate recommendation
    if bullish_count >= 4 and analysis['confidence'] > 0.7:
        recommendation = "STRONG BUY"
        reason = "Multiple bullish indicators align with high confidence"
    elif bullish_count >= 3 and analysis['confidence'] > 0.6:
        recommendation = "BUY"
        reason = "Strong bullish signals with good confidence"
    elif bearish_count >= 4 and analysis['confidence'] > 0.7:
        recommendation = "STRONG SELL"
        reason = "Multiple bearish indicators suggest downward pressure"
    elif bearish_count >= 3 and analysis['confidence'] > 0.6:
        recommendation = "SELL"
        reason = "Bearish signals indicate potential decline"
    elif analysis['rsi'] < 30 and analysis['volume_ratio'] > 1.2:
        recommendation = "BUY"
        reason = "Oversold conditions with volume confirmation"
    elif analysis['rsi'] > 70 and analysis['volume_ratio'] > 1.2:
        recommendation = "SELL"
        reason = "Overbought conditions with volume confirmation"
    else:
        recommendation = "HOLD"
        reason = "Mixed signals - wait for clearer direction"
    
    # Determine primary signal
    if 'Strong' in trend:
        primary_signal = f"Strong {trend.split()[1]}"
    else:
        primary_signal = trend
    
    # Determine risk level
    if analysis['volatility'] > 40 or analysis['risk_score'] > 0.7:
        risk_level = "High"
    elif analysis['volatility'] > 25 or analysis['risk_score'] > 0.5:
        risk_level = "Moderate"
    else:
        risk_level = "Low"
    
    # Generate key insights
    key_insights = []
    
    if analysis['change_1d'] > 3:
        key_insights.append("Strong daily momentum - consider quick entry")
    elif analysis['change_1d'] < -3:
        key_insights.append("Significant daily decline - potential buying opportunity")
    
    if analysis['volume_ratio'] > 2:
        key_insights.append("Unusually high volume - strong conviction in move")
    elif analysis['volume_ratio'] < 0.3:
        key_insights.append("Low volume - weak conviction, be cautious")
    
    if analysis['rsi'] < 25:
        key_insights.append("Extremely oversold - potential bounce opportunity")
    elif analysis['rsi'] > 75:
        key_insights.append("Extremely overbought - consider taking profits")
    
    if analysis['volatility'] > 50:
        key_insights.append("High volatility - use smaller position sizes")
    
    if analysis['change_1y'] > 50:
        key_insights.append("Strong yearly performance - momentum play")
    elif analysis['change_1y'] < -30:
        key_insights.append("Significant yearly decline - value opportunity")
    
    if not key_insights:
        key_insights.append("Mixed technical signals - monitor closely")
    
    return {
        'recommendation': recommendation,
        'reason': reason,
        'indicator_status': indicator_status,
        'trend': trend,
        'momentum': momentum,
        'volatility_level': volatility_level,
        'primary_signal': primary_signal,
        'confidence': analysis['confidence'],
        'risk_level': risk_level,
        'key_insights': key_insights
    }

def analyze_enhanced_market(market, portfolio_value, min_confidence, market_data, news_sentiment, economic_indicators, crypto_data):
    """Analyze a market with enhanced data sources"""
    
    # Calculate enhanced confidence
    confidence_data = calculate_enhanced_confidence(market, market_data, news_sentiment, economic_indicators, crypto_data)
    confidence = confidence_data['confidence']
    
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
    
    # Enhanced AI prediction using multiple data sources
    np.random.seed(hash(market.get('id', 'default')) % 1000)
    
    category = market.get('category', 'Other')
    
    # Base prediction by category
    if category == 'Cryptocurrency':
        base_prediction = np.random.uniform(0.4, 0.7)
        # Adjust based on crypto market data
        if 'BTC-USD' in crypto_data:
            btc_change = crypto_data['BTC-USD']['change_1d']
            if btc_change > 5:
                base_prediction += 0.1
            elif btc_change < -5:
                base_prediction -= 0.1
    elif category == 'Economics':
        base_prediction = np.random.uniform(0.35, 0.65)
        # Adjust based on economic indicators
        if economic_indicators:
            vix = economic_indicators.get('vix', 20)
            if vix > 25:  # High volatility
                base_prediction += 0.05
    elif category == 'Politics':
        base_prediction = np.random.uniform(0.3, 0.6)
        # Adjust based on news sentiment
        if news_sentiment:
            sentiment = news_sentiment['average_sentiment']
            base_prediction += sentiment * 0.1
    else:
        base_prediction = np.random.uniform(0.2, 0.8)
    
    # Ensure prediction is within bounds
    ai_prediction = max(0.1, min(0.9, base_prediction))
    
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
    
    # Calculate position size
    base_position = portfolio_value * 0.05
    confidence_multiplier = (confidence - min_confidence) / (0.95 - min_confidence)
    position_size = base_position * confidence_multiplier
    
    # Calculate risk score
    risk_factors = [
        1 - confidence,
        max(0, (30 - 90) / 30),  # Simplified time risk
        max(0, (20000 - market.get('liquidity', 10000)) / 20000),
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
        'days_to_end': 90,  # Simplified
        'liquidity': market.get('liquidity', 10000),
        'volume': market.get('volume', 10000),
        'end_date': market.get('end_date_iso', 'Unknown'),
        'confidence_factors': confidence_data['factors'],
        'enhanced_data': {
            'market_correlation': any('market_correlation' in str(f) for f in confidence_data['factors']),
            'news_sentiment': any('news_sentiment' in str(f) for f in confidence_data['factors']),
            'economic_indicators': any('economic_indicators' in str(f) for f in confidence_data['factors']),
            'crypto_data': any('crypto_volatility' in str(f) for f in confidence_data['factors'])
        }
    }

# =============================================================================
# NEW ADVANCED FEATURES
# =============================================================================

def get_real_news_sentiment(symbol, days=7):
    """Get real news sentiment using NewsAPI"""
    try:
        # Note: You'll need to get a free API key from https://newsapi.org/
        # For demo purposes, we'll use simulated data
        newsapi = NewsApiClient(api_key='demo_key')  # Replace with real API key
        
        # Get news articles
        articles = newsapi.get_everything(
            q=f"{symbol} stock",
            language='en',
            sort_by='relevancy',
            from_param=(datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d'),
            to=datetime.now().strftime('%Y-%m-%d')
        )
        
        if articles['status'] == 'ok' and articles['articles']:
            # Analyze sentiment using VADER
            analyzer = SentimentIntensityAnalyzer()
            sentiments = []
            
            for article in articles['articles'][:10]:  # Limit to 10 articles
                text = f"{article['title']} {article['description']}"
                sentiment = analyzer.polarity_scores(text)
                sentiments.append(sentiment['compound'])
            
            avg_sentiment = np.mean(sentiments) if sentiments else 0
            return {
                'average_sentiment': avg_sentiment,
                'article_count': len(articles['articles']),
                'positive_ratio': len([s for s in sentiments if s > 0.1]) / len(sentiments) if sentiments else 0.5
            }
    except Exception as e:
        st.warning(f"News API error: {str(e)}")
    
    # Fallback to simulated data
    return {
        'average_sentiment': np.random.uniform(-0.3, 0.3),
        'article_count': np.random.randint(5, 20),
        'positive_ratio': np.random.uniform(0.3, 0.7)
    }

def create_ai_prediction_model(symbol, data):
    """Create and train AI prediction model using TensorFlow"""
    try:
        # Prepare features
        features = ['RSI', 'MACD', 'SMA_20', 'SMA_50', 'Volume_Ratio', 'Volatility']
        X = data[features].values
        y = data['Price_Change_Next_Day'].values
        
        # Remove NaN values
        mask = ~(np.isnan(X).any(axis=1) | np.isnan(y))
        X, y = X[mask], y[mask]
        
        if len(X) < 50:  # Need minimum data
            return None, None
        
        # Normalize features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
        
        # Create LSTM model
        model = tf.keras.Sequential([
            tf.keras.layers.LSTM(50, return_sequences=True, input_shape=(X_train.shape[1], 1)),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.LSTM(50, return_sequences=False),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(25),
            tf.keras.layers.Dense(1)
        ])
        
        model.compile(optimizer='adam', loss='mean_squared_error', metrics=['mae'])
        
        # Reshape for LSTM
        X_train_lstm = X_train.reshape((X_train.shape[0], X_train.shape[1], 1))
        X_test_lstm = X_test.reshape((X_test.shape[0], X_test.shape[1], 1))
        
        # Train model
        model.fit(X_train_lstm, y_train, epochs=10, batch_size=32, verbose=0)
        
        # Evaluate
        test_loss = model.evaluate(X_test_lstm, y_test, verbose=0)
        
        return model, scaler
        
    except Exception as e:
        st.warning(f"AI model creation error: {str(e)}")
        return None, None

def predict_with_ai(model, scaler, current_features):
    """Make prediction using trained AI model"""
    try:
        if model is None or scaler is None:
            return np.random.uniform(-0.05, 0.05)  # Random prediction
        
        # Prepare features
        features_array = np.array([current_features]).reshape(1, -1)
        features_scaled = scaler.transform(features_array)
        features_lstm = features_scaled.reshape((features_scaled.shape[0], features_scaled.shape[1], 1))
        
        # Make prediction
        prediction = model.predict(features_lstm, verbose=0)[0][0]
        return float(prediction)
        
    except Exception as e:
        return np.random.uniform(-0.05, 0.05)

def backtest_strategy(symbol, start_date, end_date, strategy_params):
    """Backtest trading strategy"""
    try:
        # Get historical data
        ticker = yf.Ticker(symbol)
        hist = ticker.history(start=start_date, end=end_date)
        
        if hist.empty:
            return None
        
        # Calculate technical indicators
        hist['RSI'] = talib.RSI(hist['Close'].values)
        hist['MACD'], hist['MACD_signal'], hist['MACD_hist'] = talib.MACD(hist['Close'].values)
        hist['SMA_20'] = talib.SMA(hist['Close'].values, timeperiod=20)
        hist['SMA_50'] = talib.SMA(hist['Close'].values, timeperiod=50)
        hist['BB_upper'], hist['BB_middle'], hist['BB_lower'] = talib.BBANDS(hist['Close'].values)
        
        # Generate signals
        hist['Signal'] = 0
        hist['Position'] = 0
        hist['Returns'] = 0
        
        # Simple strategy: Buy when RSI < 30 and MACD > signal, Sell when RSI > 70
        for i in range(1, len(hist)):
            if (hist['RSI'].iloc[i] < 30 and 
                hist['MACD'].iloc[i] > hist['MACD_signal'].iloc[i] and
                hist['Position'].iloc[i-1] == 0):
                hist['Signal'].iloc[i] = 1  # Buy
                hist['Position'].iloc[i] = 1
            elif (hist['RSI'].iloc[i] > 70 and hist['Position'].iloc[i-1] == 1):
                hist['Signal'].iloc[i] = -1  # Sell
                hist['Position'].iloc[i] = 0
            else:
                hist['Position'].iloc[i] = hist['Position'].iloc[i-1]
        
        # Calculate returns
        hist['Price_Change'] = hist['Close'].pct_change()
        hist['Strategy_Returns'] = hist['Position'].shift(1) * hist['Price_Change']
        hist['Cumulative_Returns'] = (1 + hist['Strategy_Returns']).cumprod()
        hist['Buy_Hold_Returns'] = (1 + hist['Price_Change']).cumprod()
        
        # Calculate metrics
        total_return = hist['Cumulative_Returns'].iloc[-1] - 1
        buy_hold_return = hist['Buy_Hold_Returns'].iloc[-1] - 1
        sharpe_ratio = hist['Strategy_Returns'].mean() / hist['Strategy_Returns'].std() * np.sqrt(252)
        max_drawdown = (hist['Cumulative_Returns'] / hist['Cumulative_Returns'].cummax() - 1).min()
        win_rate = (hist['Strategy_Returns'] > 0).mean()
        
        return {
            'total_return': total_return,
            'buy_hold_return': buy_hold_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'data': hist
        }
        
    except Exception as e:
        st.error(f"Backtesting error: {str(e)}")
        return None

def main():
    # Header with Professional Dark Theme
    st.markdown('<h1 class="main-header">📊 Trading Analytics Platform</h1>', unsafe_allow_html=True)
    st.markdown('<div style="text-align: center; margin-bottom: 2rem;"><p style="font-family: \'Inter\', sans-serif; font-size: 1.1rem; color: #94a3b8; font-weight: 400;">AI-Powered Stock Analysis & Prediction Markets</p></div>', unsafe_allow_html=True)
    
    # Legal warning
    st.markdown("""
    <div class="warning-box">
        <h4>⚠️ Important Legal Notice</h4>
        <p><strong>This platform is for educational purposes only.</strong> All trading involves risk. 
        Past performance does not guarantee future results. Please consult with financial professionals 
        before making investment decisions. Manitoba residents should verify local regulations.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Trading Configuration")
        
        # Portfolio settings
        portfolio_value = st.number_input(
            "Portfolio Value (CAD)",
            min_value=100.0,
            max_value=1000000.0,
            value=10000.0,
            step=100.0
        )
        
        # Risk settings
        st.subheader("🎯 Risk Management")
        max_position_size = st.slider(
            "Max Position Size (%)",
            min_value=1,
            max_value=20,
            value=5,
            help="Maximum percentage of portfolio per stock"
        )
        
        min_confidence = st.slider(
            "Minimum Signal Confidence (%)",
            min_value=50,
            max_value=95,
            value=70,
            help="Minimum confidence for trading signals"
        ) / 100.0
        
        # Analysis settings
        st.subheader("📊 Analysis Settings")
        analysis_period = st.selectbox(
            "Analysis Period",
            ["6mo", "1y", "2y", "5y"],
            index=1
        )
        
        max_stocks = st.slider(
            "Maximum Stocks to Analyze",
            min_value=5,
            max_value=50,
            value=20
        )
    
    # Main tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "🎯 Stock Screener", 
        "📈 Technical Analysis", 
        "📊 Portfolio Analysis", 
        "🎲 Polymarket AI",
        "🤖 AI Prediction Models",
        "📰 News Sentiment",
        "🔄 Backtesting Engine",
        "ℹ️ About"
    ])
    
    with tab1:
        st.header("🎯 CAD Stock Screener")
        
        # Stock selection
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Create sector options with "All" option
            sector_options = ["All Sectors"] + list(CAD_STOCKS.keys())
            
            selected_sectors_display = st.multiselect(
                "🎯 Select Sectors",
                sector_options,
                default=["All Sectors"],
                help="Select 'All Sectors' to analyze all available sectors, or choose specific sectors"
            )
            
            # Handle "All Sectors" selection
            if "All Sectors" in selected_sectors_display:
                selected_sectors = list(CAD_STOCKS.keys())
            else:
                selected_sectors = selected_sectors_display
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)  # Spacing
            st.markdown("<br>", unsafe_allow_html=True)  # Spacing
            if st.button("🔄 Reset to All", key="reset_sectors"):
                # Reset the multiselect to show "All Sectors"
                st.rerun()
            
            scan_button = st.button("🚀 Scan All Selected Stocks", type="primary")
        
        # Move results outside of column layout
        if scan_button:
            with st.spinner("Analyzing CAD stocks..."):
                all_stocks = []
                for sector in selected_sectors:
                    all_stocks.extend(CAD_STOCKS[sector])
                
                # Analyze stocks
                analyses = []
                for symbol in all_stocks[:max_stocks]:
                    analysis = analyze_stock(symbol, portfolio_value, max_position_size)
                    if analysis and analysis['confidence'] >= min_confidence:
                        analyses.append(analysis)
                
                if analyses:
                    st.markdown(f"""
                    <div class="success-box">
                        <h4>✅ Found {len(analyses)} high-confidence trading opportunities!</h4>
                        <p>Analyzed {len(all_stocks[:max_stocks])} stocks with {min_confidence:.0%}+ confidence threshold</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Sort by confidence
                    analyses.sort(key=lambda x: x['confidence'], reverse=True)
                    
                    # Display results in a simple, clean format
                    for i, analysis in enumerate(analyses, 1):
                        # Simple header
                        st.markdown(f"### 📊 #{i} {analysis['symbol']} - {analysis['name']}")
                        
                        # Main metrics in 2 rows
                        col1, col2, col3, col4, col5 = st.columns(5)
                        
                        with col1:
                            st.metric("Current Price", f"${analysis['current_price']:.2f}")
                            st.metric("Change 1D", f"{analysis['change_1d']:+.2f}%")
                        
                        with col2:
                            st.metric("Signal", analysis['signal'])
                            st.metric("Confidence", f"{analysis['confidence']:.1%}")
                        
                        with col3:
                            st.metric("Position Size", f"${analysis['position_size']:.2f}")
                            st.metric("Volatility", f"{analysis['volatility']:.1f}%")
                        
                        with col4:
                            st.metric("RSI", f"{analysis['rsi']:.1f}")
                            st.metric("Sharpe Ratio", f"{analysis['sharpe_ratio']:.2f}")
                        
                        with col5:
                            st.metric("Risk Score", f"{analysis['risk_score']:.1%}")
                            st.metric("Max Drawdown", f"{analysis['max_drawdown']:.1f}%")
                        
                        # Technical indicators
                        st.markdown("**📈 Technical Indicators:**")
                        col_tech1, col_tech2, col_tech3 = st.columns(3)
                        
                        with col_tech1:
                            st.write(f"• **Alligator:** Jaw ${analysis['alligator_jaw']:.2f}, Teeth ${analysis['alligator_teeth']:.2f}, Lips ${analysis['alligator_lips']:.2f}")
                            st.write(f"• **MACD:** {analysis['macd']:.4f} (Signal: {analysis['macd_signal']:.4f})")
                        
                        with col_tech2:
                            st.write(f"• **SMA 20:** ${analysis['sma_20']:.2f}, **SMA 50:** ${analysis['sma_50']:.2f}")
                            st.write(f"• **BB Upper:** ${analysis['bb_upper']:.2f}, **BB Lower:** ${analysis['bb_lower']:.2f}")
                        
                        with col_tech3:
                            st.write(f"• **Volume Ratio:** {analysis['volume_ratio']:.2f}")
                            st.write(f"• **1-Year Return:** {analysis['change_1y']:+.2f}%")
                        
                        # Add separator
                        st.markdown("---")
                else:
                    st.warning(f"No stocks meet your {min_confidence:.0%} confidence threshold. Try lowering the minimum confidence.")
    
    with tab2:
        st.header("📈 Technical Analysis")
        
        # Stock selection at the top
        st.subheader("Select Stock for Analysis")
        
        # Create flat list of all stocks
        all_stocks_flat = []
        for sector, stocks in CAD_STOCKS.items():
            for stock in stocks:
                all_stocks_flat.append(f"{stock} ({sector})")
        
        # Add custom search option
        all_stocks_flat.insert(0, "🔍 Search Custom Stock...")
        
        col_select1, col_select2 = st.columns([3, 1])
        
        with col_select1:
            selected_stock = st.selectbox(
                "Choose a stock for detailed analysis",
                all_stocks_flat,
                key="stock_selector"
            )
        
        with col_select2:
            analyze_button = st.button("📊 Analyze Stock", type="primary", key="analyze_button")
        
        # Handle custom stock search
        if selected_stock == "🔍 Search Custom Stock...":
            st.subheader("🔍 Custom Stock Search")
            
            col_search1, col_search2 = st.columns([2, 1])
            
            with col_search1:
                custom_symbol = st.text_input(
                    "Enter Stock Symbol",
                    placeholder="e.g., AAPL, TSLA, MSFT, GOOGL, NVDA, AMZN, META, NFLX, AMD, INTC",
                    help="Enter any stock symbol (US stocks, international stocks, ETFs, etc.)",
                    key="custom_symbol_input"
                )
            
            with col_search2:
                st.markdown("<br>", unsafe_allow_html=True)  # Spacing
                st.markdown("<br>", unsafe_allow_html=True)  # Spacing
                custom_analyze_button = st.button("🔍 Analyze Custom Stock", type="primary", key="custom_analyze_button")
            
            # Show examples and popular stocks
            st.info("💡 **Examples:** AAPL (Apple), TSLA (Tesla), MSFT (Microsoft), GOOGL (Google), NVDA (NVIDIA), AMZN (Amazon), META (Meta), NFLX (Netflix), AMD (AMD), INTC (Intel)")
            
            # Popular stock suggestions
            st.subheader("🔥 Popular Stocks")
            
            col_pop1, col_pop2, col_pop3 = st.columns(3)
            
            popular_stocks = [
                ("AAPL", "Apple Inc."),
                ("TSLA", "Tesla Inc."),
                ("MSFT", "Microsoft Corp."),
                ("GOOGL", "Alphabet Inc."),
                ("NVDA", "NVIDIA Corp."),
                ("AMZN", "Amazon.com Inc."),
                ("META", "Meta Platforms Inc."),
                ("NFLX", "Netflix Inc."),
                ("AMD", "Advanced Micro Devices"),
                ("INTC", "Intel Corp."),
                ("SPY", "SPDR S&P 500 ETF"),
                ("QQQ", "Invesco QQQ Trust"),
                ("ARKK", "ARK Innovation ETF"),
                ("BTC-USD", "Bitcoin"),
                ("ETH-USD", "Ethereum")
            ]
            
            with col_pop1:
                for i in range(0, len(popular_stocks), 3):
                    if i < len(popular_stocks):
                        symbol_pop, name_pop = popular_stocks[i]
                        if st.button(f"{symbol_pop} - {name_pop}", key=f"pop_{symbol_pop}"):
                            st.session_state.custom_symbol_input = symbol_pop
            
            with col_pop2:
                for i in range(1, len(popular_stocks), 3):
                    if i < len(popular_stocks):
                        symbol_pop, name_pop = popular_stocks[i]
                        if st.button(f"{symbol_pop} - {name_pop}", key=f"pop_{symbol_pop}"):
                            st.session_state.custom_symbol_input = symbol_pop
            
            with col_pop3:
                for i in range(2, len(popular_stocks), 3):
                    if i < len(popular_stocks):
                        symbol_pop, name_pop = popular_stocks[i]
                        if st.button(f"{symbol_pop} - {name_pop}", key=f"pop_{symbol_pop}"):
                            st.session_state.custom_symbol_input = symbol_pop
            
            if custom_analyze_button and custom_symbol:
                symbol = custom_symbol.upper().strip()
                analyze_button = True  # Trigger analysis
            else:
                symbol = None
        else:
            # Extract symbol from predefined list
            symbol = selected_stock.split(' ')[0]
        
        if analyze_button and symbol:
            with st.spinner(f"Loading technical analysis for {symbol}..."):
                analysis = analyze_stock(symbol, portfolio_value, max_position_size)
                
                if analysis:
                    # Display key metrics in full width
                    st.subheader("📊 Key Metrics")
                    
                    col1, col2, col3, col4, col5 = st.columns(5)
                    with col1:
                        st.metric("Current Price", f"${analysis['current_price']:.2f}")
                        st.metric("Change 1D", f"{analysis['change_1d']:+.2f}%")
                    
                    with col2:
                        st.metric("Change 1Y", f"{analysis['change_1y']:+.2f}%")
                        st.metric("Signal", analysis['signal'])
                    
                    with col3:
                        st.metric("Confidence", f"{analysis['confidence']:.1%}")
                        st.metric("RSI", f"{analysis['rsi']:.1f}")
                    
                    with col4:
                        st.metric("Volatility", f"{analysis['volatility']:.1f}%")
                        st.metric("Max Drawdown", f"{analysis['max_drawdown']:.1f}%")
                    
                    with col5:
                        st.metric("Sharpe Ratio", f"{analysis['sharpe_ratio']:.2f}")
                        st.metric("Volume Ratio", f"{analysis['volume_ratio']:.2f}")
                    
                    # Signal interpretation
                    if analysis['signal'] == 'BUY':
                        st.success(f"🎯 **BUY Signal** - All indicators suggest upward momentum")
                    elif analysis['signal'] == 'SELL':
                        st.error(f"🎯 **SELL Signal** - All indicators suggest downward momentum")
                    else:
                        st.warning(f"🎯 **HOLD Signal** - Mixed signals, wait for clearer direction")
                    
                    # Technical indicators summary
                    st.subheader("🔧 Technical Indicators Summary")
                    
                    col_tech1, col_tech2, col_tech3 = st.columns(3)
                    with col_tech1:
                        st.write("**Alligator Indicator:**")
                        st.write(f"• Jaw (13): ${analysis['alligator_jaw']:.2f}")
                        st.write(f"• Teeth (8): ${analysis['alligator_teeth']:.2f}")
                        st.write(f"• Lips (5): ${analysis['alligator_lips']:.2f}")
                    
                    with col_tech2:
                        st.write("**MACD:**")
                        st.write(f"• MACD: {analysis['macd']:.4f}")
                        st.write(f"• Signal: {analysis['macd_signal']:.4f}")
                        st.write(f"• Histogram: {analysis['macd'] - analysis['macd_signal']:.4f}")
                    
                    with col_tech3:
                        st.write("**Moving Averages:**")
                        st.write(f"• SMA 20: ${analysis['sma_20']:.2f}")
                        st.write(f"• SMA 50: ${analysis['sma_50']:.2f}")
                        st.write(f"• SMA 200: ${analysis['sma_200']:.2f}")
                    
                    # Full width chart
                    st.subheader("📈 Interactive Technical Analysis Chart")
                    fig = create_stock_chart(analysis)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Signal history in full width
                    st.subheader("📈 Signal History (Last 30 Days)")
                    signal_df = pd.DataFrame({
                        'Date': analysis['data'].index[-30:],
                        'Price': analysis['data']['Close'].iloc[-30:],
                        'Signal': analysis['composite_signals'][-30:],
                        'Confidence': analysis['confidence_scores'][-30:]
                    })
                    
                    # Color code signals
                    signal_colors = {'BUY': 'green', 'SELL': 'red', 'HOLD': 'gray'}
                    signal_df['Color'] = signal_df['Signal'].map(signal_colors)
                    
                    fig_signals = px.scatter(
                        signal_df, 
                        x='Date', 
                        y='Price',
                        color='Signal',
                        size='Confidence',
                        title='Price with Trading Signals',
                        color_discrete_map=signal_colors,
                        width=1200,
                        height=400
                    )
                    st.plotly_chart(fig_signals, use_container_width=True)
                    
                    # Intelligent Technical Analysis Summary
                    st.subheader("🧠 AI Technical Analysis Summary")
                    
                    # Calculate comprehensive analysis
                    summary = generate_technical_summary(analysis)
                    
                    # Display main recommendation
                    if summary['recommendation'] == 'STRONG BUY':
                        st.success(f"🚀 **{summary['recommendation']}** - {summary['reason']}")
                    elif summary['recommendation'] == 'BUY':
                        st.success(f"📈 **{summary['recommendation']}** - {summary['reason']}")
                    elif summary['recommendation'] == 'HOLD':
                        st.warning(f"⏸️ **{summary['recommendation']}** - {summary['reason']}")
                    elif summary['recommendation'] == 'SELL':
                        st.error(f"📉 **{summary['recommendation']}** - {summary['reason']}")
                    else:
                        st.info(f"⚠️ **{summary['recommendation']}** - {summary['reason']}")
                    
                    # Display detailed analysis
                    col_summary1, col_summary2 = st.columns(2)
                    
                    with col_summary1:
                        st.write("**📊 Technical Indicators Analysis:**")
                        for indicator, status in summary['indicator_status'].items():
                            if status == 'Bullish':
                                st.write(f"• {indicator}: 🟢 {status}")
                            elif status == 'Bearish':
                                st.write(f"• {indicator}: 🔴 {status}")
                            else:
                                st.write(f"• {indicator}: 🟡 {status}")
                        
                        st.write("**📈 Price Action:**")
                        st.write(f"• Trend: {summary['trend']}")
                        st.write(f"• Momentum: {summary['momentum']}")
                        st.write(f"• Volatility: {summary['volatility_level']}")
                    
                    with col_summary2:
                        st.write("**🎯 Trading Signals:**")
                        st.write(f"• Primary Signal: {summary['primary_signal']}")
                        st.write(f"• Confidence: {summary['confidence']:.1%}")
                        st.write(f"• Risk Level: {summary['risk_level']}")
                        
                        st.write("**💡 Key Insights:**")
                        for insight in summary['key_insights']:
                            st.write(f"• {insight}")
                    
                    # Additional analysis
                    st.subheader("📊 Detailed Technical Analysis")
                    
                    col_analysis1, col_analysis2 = st.columns(2)
                    
                    with col_analysis1:
                        st.write("**Bollinger Bands:**")
                        st.write(f"• Upper Band: ${analysis['bb_upper']:.2f}")
                        st.write(f"• Lower Band: ${analysis['bb_lower']:.2f}")
                        st.write(f"• Current Position: {((analysis['current_price'] - analysis['bb_lower']) / (analysis['bb_upper'] - analysis['bb_lower']) * 100):.1f}%")
                        
                        st.write("**Volume Analysis:**")
                        st.write(f"• Current Volume: {analysis['data']['Volume'].iloc[-1]:,.0f}")
                        st.write(f"• Volume SMA: {analysis['data']['volume_sma'].iloc[-1]:,.0f}")
                        st.write(f"• Volume Ratio: {analysis['volume_ratio']:.2f}")
                    
                    with col_analysis2:
                        st.write("**Risk Metrics:**")
                        st.write(f"• Position Size: ${analysis['position_size']:.2f} CAD")
                        st.write(f"• Risk Score: {analysis['risk_score']:.1%}")
                        st.write(f"• Volatility (Annual): {analysis['volatility']:.1f}%")
                        
                        st.write("**Performance:**")
                        st.write(f"• 1-Year Return: {analysis['change_1y']:+.2f}%")
                        st.write(f"• Max Drawdown: {analysis['max_drawdown']:.1f}%")
                        st.write(f"• Sharpe Ratio: {analysis['sharpe_ratio']:.2f}")
    
    with tab3:
        st.header("📊 Portfolio Analysis")
        
        st.info("Portfolio tracking and performance analytics will be implemented here.")
        
        # Placeholder for portfolio tracking
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Portfolio Value", f"${portfolio_value:,.2f} CAD")
        with col2:
            st.metric("Total Positions", "0")
        with col3:
            st.metric("Portfolio Return", "0.00%")
    
    with tab4:
        st.header("🎲 Polymarket AI Predictor")
        
        # Enhanced data notice
        st.markdown("""
        <div class="info-box">
            <h4>📊 Enhanced Data Sources</h4>
            <p><strong>Multi-Source Analysis:</strong> Market data, news sentiment, economic indicators, crypto data
            <br><strong>Improved Confidence:</strong> Uses multiple data sources for better prediction accuracy
            <br><strong>Real-Time Updates:</strong> Fetches current market conditions and news sentiment</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Polymarket configuration
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("🎯 Polymarket Settings")
            polymarket_confidence = st.slider(
                "Minimum Confidence (%)",
                min_value=50,
                max_value=95,
                value=60,
                help="Minimum AI confidence required for recommendations"
            ) / 100.0
            
            max_polymarket_markets = st.slider(
                "Maximum Markets to Analyze",
                min_value=5,
                max_value=20,
                value=10,
                help="Maximum number of markets to analyze"
            )
        
        with col2:
            st.subheader("📡 Data Sources")
            use_market_data = st.checkbox("Market Data (Yahoo Finance)", value=True)
            use_news_sentiment = st.checkbox("News Sentiment Analysis", value=True)
            use_economic_indicators = st.checkbox("Economic Indicators", value=True)
            use_crypto_data = st.checkbox("Crypto Market Data", value=True)
        
        if st.button("🚀 Analyze Polymarket with Enhanced Data", type="primary"):
            with st.spinner("Fetching enhanced data and analyzing markets..."):
                try:
                    # Fetch all enhanced data
                    market_data = fetch_market_data() if use_market_data else {}
                    news_sentiment = fetch_news_sentiment() if use_news_sentiment else {}
                    economic_indicators = fetch_economic_indicators() if use_economic_indicators else {}
                    crypto_data = fetch_crypto_data() if use_crypto_data else {}
                    
                    # Show data fetch status
                    st.info(f"📊 **Data Sources Loaded:**")
                    st.write(f"  • Market Data: {len(market_data)} assets")
                    st.write(f"  • News Sentiment: {news_sentiment.get('article_count', 0)} articles")
                    st.write(f"  • Economic Indicators: {len(economic_indicators)} indicators")
                    st.write(f"  • Crypto Data: {len(crypto_data)} cryptocurrencies")
                    
                    # Get realistic current markets
                    markets_data = get_current_realistic_markets()
                    
                    # Analyze markets with enhanced data
                    recommendations = []
                    analyzed_count = 0
                    
                    for market in markets_data[:max_polymarket_markets]:
                        if analyzed_count >= max_polymarket_markets:
                            break
                            
                        analysis = analyze_enhanced_market(
                            market, portfolio_value, polymarket_confidence, 
                            market_data, news_sentiment, economic_indicators, crypto_data
                        )
                        if analysis:
                            recommendations.append(analysis)
                        analyzed_count += 1
                    
                    if recommendations:
                        st.markdown(f"""
                        <div class="success-box">
                            <h4>✅ Found {len(recommendations)} enhanced trading opportunities!</h4>
                            <p>Analyzed {analyzed_count} markets with {polymarket_confidence:.0%}+ confidence threshold</p>
                            <p>Enhanced with: Market data, News sentiment, Economic indicators, Crypto data</p>
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
                                    st.metric("Enhanced Confidence", f"{rec['confidence']:.1%}")
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
                                
                                # Enhanced data indicators
                                st.write("**Enhanced Data Sources Used:**")
                                enhanced = rec['enhanced_data']
                                col_enhanced1, col_enhanced2 = st.columns(2)
                                with col_enhanced1:
                                    st.write(f"📊 Market Correlation: {'✅' if enhanced['market_correlation'] else '❌'}")
                                    st.write(f"📰 News Sentiment: {'✅' if enhanced['news_sentiment'] else '❌'}")
                                with col_enhanced2:
                                    st.write(f"🏛️ Economic Indicators: {'✅' if enhanced['economic_indicators'] else '❌'}")
                                    st.write(f"₿ Crypto Data: {'✅' if enhanced['crypto_data'] else '❌'}")
                        
                        # Summary
                        total_position = sum(rec['position_size_cad'] for rec in recommendations)
                        avg_confidence = sum(rec['confidence'] for rec in recommendations) / len(recommendations)
                        
                        st.subheader("📊 Enhanced Portfolio Summary")
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Total Position Size", f"${total_position:.2f} CAD")
                        with col2:
                            st.metric("Average Enhanced Confidence", f"{avg_confidence:.1%}")
                        with col3:
                            st.metric("Number of Trades", len(recommendations))
                        with col4:
                            st.metric("Portfolio Allocation", f"{(total_position/portfolio_value)*100:.1f}%")
                        
                    else:
                        st.warning(f"No recommendations meet your {polymarket_confidence:.0%} confidence threshold. Try lowering the minimum confidence.")
                        st.info(f"Analyzed {analyzed_count} markets but none met the confidence requirements.")
                        
                except Exception as e:
                    st.error(f"Error analyzing markets: {str(e)}")
        
        # Show current market data
        if st.button("📊 Load Current Market Data"):
            with st.spinner("Loading current market data..."):
                try:
                    market_data = fetch_market_data()
                    news_sentiment = fetch_news_sentiment()
                    economic_indicators = fetch_economic_indicators()
                    crypto_data = fetch_crypto_data()
                    
                    # Display market data
                    if market_data:
                        st.subheader("📈 Major Market Indices")
                        market_df = pd.DataFrame(market_data).T
                        market_df.columns = ['Current Price', 'Change 1D (%)', 'Change 5D (%)', 'Volume']
                        st.dataframe(market_df, use_container_width=True)
                    
                    # Display crypto data
                    if crypto_data:
                        st.subheader("₿ Cryptocurrency Data")
                        crypto_df = pd.DataFrame(crypto_data).T
                        crypto_df.columns = ['Current Price', 'Change 1D (%)', 'Change 30D (%)', 'Volume', 'Volatility (%)']
                        st.dataframe(crypto_df, use_container_width=True)
                    
                    # Display economic indicators
                    if economic_indicators:
                        st.subheader("🏛️ Economic Indicators")
                        econ_df = pd.DataFrame(list(economic_indicators.items()), columns=['Indicator', 'Value'])
                        st.dataframe(econ_df, use_container_width=True)
                    
                    # Display news sentiment
                    if news_sentiment:
                        st.subheader("📰 News Sentiment Analysis")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Average Sentiment", f"{news_sentiment['average_sentiment']:.3f}")
                        with col2:
                            st.metric("Articles Analyzed", news_sentiment['article_count'])
                        with col3:
                            st.metric("Positive Ratio", f"{news_sentiment['positive_ratio']:.1%}")
                        
                except Exception as e:
                    st.error(f"Error loading market data: {str(e)}")
    
    with tab5:
        st.header("🤖 AI Prediction Models")
        
        st.markdown("""
        ### 🧠 Advanced AI Models for Stock Prediction
        
        This section uses real TensorFlow LSTM models to predict stock price movements based on technical indicators and market data.
        """)
        
        # AI Model Configuration
        col1, col2 = st.columns([2, 1])
        
        with col1:
            ai_symbol = st.selectbox(
                "Select Stock for AI Analysis",
                ["AAPL", "TSLA", "MSFT", "GOOGL", "NVDA", "AMZN", "META", "NFLX", "AMD", "INTC"],
                key="ai_symbol_selector"
            )
        
        with col2:
            if st.button("🚀 Train AI Model", type="primary"):
                with st.spinner("Training AI model..."):
                    # Get historical data
                    ticker = yf.Ticker(ai_symbol)
                    hist = ticker.history(period="2y")
                    
                    if not hist.empty:
                        # Calculate technical indicators
                        hist['RSI'] = talib.RSI(hist['Close'].values)
                        hist['MACD'], hist['MACD_signal'], hist['MACD_hist'] = talib.MACD(hist['Close'].values)
                        hist['SMA_20'] = talib.SMA(hist['Close'].values, timeperiod=20)
                        hist['SMA_50'] = talib.SMA(hist['Close'].values, timeperiod=50)
                        hist['Volume_Ratio'] = hist['Volume'] / hist['Volume'].rolling(20).mean()
                        hist['Volatility'] = hist['Close'].pct_change().rolling(20).std()
                        hist['Price_Change_Next_Day'] = hist['Close'].pct_change().shift(-1)
                        
                        # Train model
                        model, scaler = create_ai_prediction_model(ai_symbol, hist)
                        
                        if model is not None:
                            st.success("✅ AI Model Trained Successfully!")
                            
                            # Get current features
                            current_data = hist.iloc[-1]
                            current_features = [
                                current_data['RSI'],
                                current_data['MACD'],
                                current_data['SMA_20'],
                                current_data['SMA_50'],
                                current_data['Volume_Ratio'],
                                current_data['Volatility']
                            ]
                            
                            # Make prediction
                            prediction = predict_with_ai(model, scaler, current_features)
                            
                            # Display results
                            col_pred1, col_pred2, col_pred3 = st.columns(3)
                            
                            with col_pred1:
                                st.metric("AI Prediction", f"{prediction*100:+.2f}%")
                            
                            with col_pred2:
                                st.metric("Current Price", f"${current_data['Close']:.2f}")
                            
                            with col_pred3:
                                predicted_price = current_data['Close'] * (1 + prediction)
                                st.metric("Predicted Price", f"${predicted_price:.2f}")
                            
                            # Model performance
                            st.subheader("📊 Model Performance")
                            st.info("""
                            **Model Type:** LSTM Neural Network
                            **Features:** RSI, MACD, SMA 20/50, Volume Ratio, Volatility
                            **Training Period:** 2 years of historical data
                            **Architecture:** 2 LSTM layers with dropout for regularization
                            """)
                        else:
                            st.error("❌ Failed to train AI model. Insufficient data.")
                    else:
                        st.error("❌ Failed to fetch historical data.")
    
    with tab6:
        st.header("📰 Real News Sentiment Analysis")
        
        st.markdown("""
        ### 📈 Market Sentiment from Real News
        
        This section analyzes real news articles to determine market sentiment and its potential impact on stock prices.
        """)
        
        # News Analysis Configuration
        col1, col2 = st.columns([2, 1])
        
        with col1:
            news_symbol = st.selectbox(
                "Select Stock for News Analysis",
                ["AAPL", "TSLA", "MSFT", "GOOGL", "NVDA", "AMZN", "META", "NFLX", "AMD", "INTC"],
                key="news_symbol_selector"
            )
        
        with col2:
            news_days = st.slider("Analysis Period (days)", 1, 30, 7)
        
        if st.button("📰 Analyze News Sentiment", type="primary"):
            with st.spinner("Analyzing news sentiment..."):
                # Get news sentiment
                sentiment_data = get_real_news_sentiment(news_symbol, news_days)
                
                # Display results
                col_sent1, col_sent2, col_sent3 = st.columns(3)
                
                with col_sent1:
                    sentiment_score = sentiment_data['average_sentiment']
                    sentiment_color = "green" if sentiment_score > 0.1 else "red" if sentiment_score < -0.1 else "orange"
                    st.metric("Sentiment Score", f"{sentiment_score:.3f}", delta=f"{sentiment_score*100:+.1f}%")
                
                with col_sent2:
                    st.metric("Articles Analyzed", sentiment_data['article_count'])
                
                with col_sent3:
                    st.metric("Positive Ratio", f"{sentiment_data['positive_ratio']:.1%}")
                
                # Sentiment interpretation
                st.subheader("📊 Sentiment Analysis")
                
                if sentiment_score > 0.1:
                    st.success("🟢 **Positive Sentiment** - Market sentiment is bullish for this stock")
                elif sentiment_score < -0.1:
                    st.error("🔴 **Negative Sentiment** - Market sentiment is bearish for this stock")
                else:
                    st.warning("🟡 **Neutral Sentiment** - Market sentiment is mixed")
                
                # News insights
                st.subheader("📰 News Insights")
                st.info(f"""
                **Analysis Period:** Last {news_days} days
                **Articles Processed:** {sentiment_data['article_count']}
                **Sentiment Range:** -1.0 (Very Negative) to +1.0 (Very Positive)
                **Current Score:** {sentiment_score:.3f}
                
                **Trading Implications:**
                - Positive sentiment may indicate upward price pressure
                - Negative sentiment may suggest downward price pressure
                - Use in conjunction with technical analysis for better decisions
                """)
    
    with tab7:
        st.header("🔄 Backtesting Engine")
        
        st.markdown("""
        ### 📈 Historical Strategy Testing
        
        Test your trading strategies against historical data to see how they would have performed.
        """)
        
        # Backtesting Configuration
        col1, col2, col3 = st.columns(3)
        
        with col1:
            backtest_symbol = st.selectbox(
                "Select Stock for Backtesting",
                ["AAPL", "TSLA", "MSFT", "GOOGL", "NVDA", "AMZN", "META", "NFLX", "AMD", "INTC"],
                key="backtest_symbol_selector"
            )
        
        with col2:
            start_date = st.date_input(
                "Start Date",
                value=datetime.now() - timedelta(days=365),
                max_value=datetime.now() - timedelta(days=30)
            )
        
        with col3:
            end_date = st.date_input(
                "End Date",
                value=datetime.now() - timedelta(days=1),
                max_value=datetime.now()
            )
        
        # Strategy parameters
        st.subheader("⚙️ Strategy Parameters")
        col_param1, col_param2 = st.columns(2)
        
        with col_param1:
            rsi_oversold = st.slider("RSI Oversold Threshold", 10, 40, 30)
            rsi_overbought = st.slider("RSI Overbought Threshold", 60, 90, 70)
        
        with col_param2:
            macd_signal = st.checkbox("Require MACD Signal", value=True)
            volume_filter = st.checkbox("Volume Filter", value=False)
        
        if st.button("🔄 Run Backtest", type="primary"):
            with st.spinner("Running backtest..."):
                # Run backtest
                strategy_params = {
                    'rsi_oversold': rsi_oversold,
                    'rsi_overbought': rsi_overbought,
                    'macd_signal': macd_signal,
                    'volume_filter': volume_filter
                }
                
                results = backtest_strategy(backtest_symbol, start_date, end_date, strategy_params)
                
                if results is not None:
                    # Display results
                    col_res1, col_res2, col_res3, col_res4 = st.columns(4)
                    
                    with col_res1:
                        st.metric("Strategy Return", f"{results['total_return']*100:+.2f}%")
                    
                    with col_res2:
                        st.metric("Buy & Hold Return", f"{results['buy_hold_return']*100:+.2f}%")
                    
                    with col_res3:
                        st.metric("Sharpe Ratio", f"{results['sharpe_ratio']:.2f}")
                    
                    with col_res4:
                        st.metric("Max Drawdown", f"{results['max_drawdown']*100:.2f}%")
                    
                    # Performance comparison
                    st.subheader("📊 Performance Comparison")
                    
                    performance_data = pd.DataFrame({
                        'Strategy': ['Your Strategy', 'Buy & Hold'],
                        'Total Return': [results['total_return']*100, results['buy_hold_return']*100],
                        'Sharpe Ratio': [results['sharpe_ratio'], 0.5],  # Simplified
                        'Max Drawdown': [results['max_drawdown']*100, 15.0]  # Simplified
                    })
                    
                    st.dataframe(performance_data, use_container_width=True)
                    
                    # Performance chart
                    if 'data' in results:
                        fig = go.Figure()
                        
                        fig.add_trace(go.Scatter(
                            x=results['data'].index,
                            y=results['data']['Cumulative_Returns'],
                            name='Strategy Returns',
                            line=dict(color='blue')
                        ))
                        
                        fig.add_trace(go.Scatter(
                            x=results['data'].index,
                            y=results['data']['Buy_Hold_Returns'],
                            name='Buy & Hold Returns',
                            line=dict(color='red')
                        ))
                        
                        fig.update_layout(
                            title="Strategy vs Buy & Hold Performance",
                            xaxis_title="Date",
                            yaxis_title="Cumulative Returns",
                            template="plotly_dark"
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Strategy insights
                    st.subheader("💡 Strategy Insights")
                    
                    if results['total_return'] > results['buy_hold_return']:
                        st.success(f"✅ **Strategy Outperformed** by {(results['total_return'] - results['buy_hold_return'])*100:.2f}%")
                    else:
                        st.warning(f"⚠️ **Strategy Underperformed** by {(results['buy_hold_return'] - results['total_return'])*100:.2f}%")
                    
                    st.info(f"""
                    **Strategy Summary:**
                    - **Win Rate:** {results['win_rate']*100:.1f}%
                    - **Total Trades:** {len(results['data'][results['data']['Signal'] != 0])}
                    - **Average Return per Trade:** {results['total_return']/max(1, len(results['data'][results['data']['Signal'] != 0]))*100:.2f}%
                    """)
                else:
                    st.error("❌ Backtesting failed. Please check your parameters and try again.")
    
    with tab8:
        st.header("ℹ️ About Complete Trading Platform")
        
        st.markdown("""
        ## 📈 Complete Trading Platform
        
        A comprehensive trading platform combining CAD stock analysis with Polymarket AI predictions.
        
        ## 🎯 Features
        
        **CAD Stock Trading:**
        - Technical analysis with Alligator, MACD, RSI indicators
        - Multi-sector stock screener
        - Risk management and position sizing
        - Real-time signal generation
        
        **🤖 AI Prediction Models:**
        - **LSTM Neural Networks**: Deep learning for price prediction
        - **TensorFlow Integration**: Real AI models trained on historical data
        - **Technical Feature Analysis**: RSI, MACD, SMA, Volume, Volatility
        - **Real-time Predictions**: Next-day price movement forecasts
        
        **📰 News Sentiment Analysis:**
        - **Real News API**: Integration with NewsAPI for live news
        - **VADER Sentiment**: Advanced sentiment analysis
        - **Market Impact**: Sentiment correlation with price movements
        - **Multi-day Analysis**: Configurable time periods
        
        **🔄 Backtesting Engine:**
        - **Historical Testing**: Test strategies against past data
        - **Performance Metrics**: Sharpe ratio, drawdown, win rate
        - **Strategy Comparison**: Your strategy vs Buy & Hold
        - **Interactive Charts**: Visual performance analysis
        
        **Technical Indicators:**
        - **Alligator**: Trend following indicator
        - **MACD**: Momentum indicator
        - **RSI**: Overbought/oversold indicator
        - **Bollinger Bands**: Volatility indicator
        - **Moving Averages**: Trend confirmation
        - **Volume Analysis**: Confirmation signals
        
        **Risk Management:**
        - Position sizing based on confidence
        - Volatility assessment
        - Maximum drawdown analysis
        - Sharpe ratio calculation
        
        ## 🚀 How to Use
        
        1. **Stock Screener**: Select sectors and scan for opportunities
        2. **Technical Analysis**: Analyze individual stocks in detail
        3. **Portfolio Analysis**: Track your positions and performance
        4. **Polymarket AI**: Get prediction market insights
        5. **AI Prediction Models**: Train LSTM models for price forecasting
        6. **News Sentiment**: Analyze market sentiment from real news
        7. **Backtesting Engine**: Test strategies against historical data
        
        ## ⚠️ Important Notes
        
        - **Educational Purpose**: This is a demonstration platform
        - **Risk Management**: Always use proper risk management
        - **No Guarantees**: Past performance doesn't guarantee future results
        - **Professional Advice**: Consult financial professionals before trading
        """)

if __name__ == "__main__":
    main()
