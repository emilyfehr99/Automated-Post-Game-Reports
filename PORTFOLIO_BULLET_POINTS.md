# Portfolio Project Bullet Points

## 🏒 NHL In-Game Predictions Application

### Project Overview
Real-time NHL game prediction system providing live win probability updates during active games, combining pre-game analytics with dynamic in-game momentum factors.

### Key Achievements & Features
• Built real-time prediction engine that monitors all live NHL games and updates win probabilities every 30 seconds during active play
• Developed momentum-based adjustment algorithm combining 5+ live metrics (score differential, time pressure, shots, power plays, faceoffs) with period-weighted impact
• Created Flask-based web dashboard with auto-refresh functionality (10-second polling) displaying pre-game and live predictions side-by-side
• Implemented period-aware weighting system where score differential impact increases as game progresses (0.1x in period 1, up to 0.2x in period 3)
• Designed efficient real-time data pipeline using NHL API integration for live game state, boxscores, and play-by-play data
• Built vanilla JavaScript frontend with responsive CSS Grid layout (no framework dependencies) for fast loading and real-time updates
• Implemented confidence scoring system based on game state, period progression, and prediction certainty with normalized probability bounds (1-99%)

### Technical Implementation
• **Backend**: Python/Flask RESTful API with custom NHL API client for real-time data retrieval
• **Prediction Model**: 70% correlation-weighted model + 30% ensemble predictions with live momentum adjustments
• **Real-Time Processing**: Efficient polling system that only updates live games, reducing API calls and improving performance
• **Data Processing**: Real-time extraction and aggregation of team statistics, game metrics, and momentum factors from live API responses

---

## 🤖 Discord Self-Learning Model Application

### Project Overview
Automated NHL prediction system with self-improving machine learning model that sends daily predictions via Discord webhooks, continuously learning from game outcomes to improve accuracy.

### Key Achievements & Features
• Developed self-learning ML model with 15+ weighted features (xG, HDC, Corsi%, power play%, faceoff%, shots, hits, etc.) that automatically adjusts weights based on prediction accuracy
• Implemented momentum-based gradient descent learning algorithm (learning rate: 0.03, momentum: 0.8) with weight clipping and normalization
• Built automated GitHub Actions workflow running daily at 8:00 AM CT to generate predictions and send formatted Discord notifications
• Created multi-model ensemble system combining correlation model (70%) with ensemble predictions (30%) for improved accuracy
• Designed goalie performance prediction system using rotation patterns, B2B heuristics, and GSAX (Goals Saved Above Expected) calculations
• Implemented advanced situational analysis including rest days advantage/disadvantage, venue-specific win rates, and strength of schedule calculations
• Built comprehensive performance tracking system monitoring total games, overall accuracy, recent accuracy (last 30 games), and per-team accuracy metrics
• Developed automatic missing game detection and backfill system that identifies and processes games from previous 7 days

### Technical Implementation
• **Machine Learning**: Improved Self-Learning Model V2 with momentum-based weight updates, minimum game thresholds (3 games), and automatic recalculation
• **Automation**: GitHub Actions workflow with scheduled cron jobs, Python environment setup, and error handling
• **Discord Integration**: Rich embed formatting with team predictions, model performance metrics, and structured message formatting
• **Data Management**: JSON-based persistence for predictions, model weights, team statistics, and goalie performance with rolling windows (last 20 games)
• **API Integration**: NHL API client for game schedules, lineups, historical data, and real-time game information
• **Advanced Features**: Venue-aware predictions (home/away), recent form analysis (windowed last 10 games), and historical multi-season data integration

### Model Performance & Analytics
• Tracks prediction accuracy across all completed games with real-time recalculation capability
• Provides recent accuracy window (last 30 games) for trend analysis and model improvement tracking
• Includes backtesting functionality with Brier score and log loss metrics for model validation
• Generates team-specific accuracy rankings to identify model strengths and weaknesses

---

## 🛠️ Shared Technical Components

• **NHL API Client**: RESTful integration with session management, comprehensive game data retrieval, and error handling
• **Data Processing**: Timezone-aware date handling, JSON parsing/validation, and historical data aggregation
• **Code Quality**: Modular architecture, comprehensive error handling, type hints, documentation, and environment variable management




