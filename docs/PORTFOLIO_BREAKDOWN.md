# Portfolio Project Breakdowns

## 🏒 NHL In-Game Predictions Application

### Overview
Real-time NHL game prediction system that provides live win probability updates during active games, combining pre-game analytics with dynamic in-game momentum factors.

### Core Features
- **Real-Time Game Monitoring**: Automatically detects and tracks all live NHL games using NHL API integration
- **Live In-Game Predictions**: Generates dynamic win probability predictions that update every 30 seconds during active games
- **Momentum-Based Adjustments**: Calculates live momentum factors including:
  - Score differential impact (weighted by period progression)
  - Time pressure adjustments (more impact in later periods)
  - Shot differential analysis
  - Power play performance impact
  - Faceoff dominance metrics
- **Pre-Game Prediction Dashboard**: Flask-based web dashboard displaying pre-game and live predictions side-by-side
- **Auto-Refresh Interface**: Live games automatically update every 10 seconds via AJAX polling
- **Comprehensive Game Metrics**: Tracks shots, hits, PIM, faceoffs, power plays, and blocked shots in real-time

### Technical Architecture
- **Backend**: Python with Flask framework for RESTful API endpoints
- **Data Integration**: Custom NHL API client for real-time game data retrieval
- **Prediction Engine**: 
  - Base predictions from self-learning ensemble model (70% correlation-weighted + 30% ensemble)
  - Live adjustments applied to base predictions using momentum calculations
  - Confidence scoring based on game state and period progression
- **Frontend**: Vanilla JavaScript with responsive CSS Grid layout (no framework dependencies)
- **Real-Time Updates**: Efficient polling system that only updates live games

### Advanced Features
- **Period-Aware Weighting**: Score differential impact increases as game progresses (0.1x in period 1, up to 0.2x in period 3)
- **Time Pressure Calculations**: Converts time remaining to pressure factor (0-1 scale) affecting prediction confidence
- **Multi-Factor Momentum Analysis**: Combines 5+ live metrics into unified momentum score
- **Normalized Probability Output**: Ensures predictions stay within valid bounds (1-99%) with proper normalization
- **Game State Detection**: Handles LIVE, CRITICAL, and PREVIEW game states appropriately

### Data Processing
- **Live Game Data Extraction**: Parses comprehensive game data including boxscores, play-by-play, and team statistics
- **Metric Aggregation**: Real-time calculation of team performance metrics from live API responses
- **Historical Context**: Integrates pre-game predictions with live adjustments for comprehensive analysis

---

## 🤖 Discord Self-Learning Model Application

### Overview
Automated NHL prediction system with self-improving machine learning model that sends daily predictions via Discord webhooks, continuously learning from game outcomes to improve accuracy.

### Core Features
- **Self-Learning Prediction Model**: Continuously updates model weights based on actual game outcomes using gradient descent principles
- **Automated Daily Predictions**: GitHub Actions workflow runs daily at 8:00 AM CT to generate and send predictions
- **Discord Integration**: Rich formatted messages with embeds, team predictions, and model performance metrics
- **Multi-Model Ensemble**: Combines correlation model (70%) with ensemble predictions (30%) for improved accuracy
- **Performance Tracking**: Tracks total games predicted, overall accuracy, and recent accuracy (last 30 games)
- **Missing Game Detection**: Automatically identifies and backfills missing games from previous days

### Technical Architecture
- **Machine Learning Model**: 
  - Improved Self-Learning Model V2 with 15+ weighted features
  - Features include: xG, HDC, Corsi%, power play%, faceoff%, shots, hits, blocked shots, takeaways, PIM
  - Advanced features: rest days advantage, goalie performance (GSAX), strength of schedule, venue-specific win rates
- **Learning Algorithm**:
  - Momentum-based weight updates (momentum = 0.8)
  - Learning rate: 0.03 with weight clipping (0.03-0.65 range)
  - Minimum 3 games required before weight updates
  - Automatic weight normalization to sum to 1.0
- **Automation**: GitHub Actions workflow with scheduled cron jobs
- **API Integration**: NHL API client for game schedules, lineups, and historical data
- **Data Persistence**: JSON-based storage for predictions, model weights, and team statistics

### Advanced ML Features
- **Goalie Performance Prediction**: Predicts starting goalie using rotation patterns and B2B heuristics, calculates GSAX (Goals Saved Above Expected)
- **Rest Days Analysis**: Calculates rest advantage/disadvantage with B2B detection and travel penalty adjustments
- **Venue-Aware Predictions**: Separate home/away performance tracking with venue-specific win percentages
- **Recent Form Analysis**: Windowed recent form calculation (last 10 games) filtered by venue
- **Strength of Schedule**: Opponent strength index based on xG and game score averages
- **Historical Data Integration**: Supports multiple seasons of historical team statistics for better predictions

### Model Performance Features
- **Accuracy Tracking**: Real-time accuracy calculation from all completed predictions
- **Recent Accuracy Window**: Last 30 games accuracy for trend analysis
- **Team-Specific Analysis**: Per-team accuracy tracking to identify model strengths/weaknesses
- **Performance Recalculation**: Ability to recalculate performance from scratch for accuracy validation
- **Backtesting**: Built-in backtesting functionality with Brier score and log loss metrics

### Automation & Integration
- **GitHub Actions Workflow**: 
  - Scheduled daily execution (cron: 0 13 * * *)
  - Manual trigger support (workflow_dispatch)
  - Python environment setup and dependency installation
  - Error handling and logging
- **Discord Webhook System**:
  - Rich embed formatting with team colors and emojis
  - Model performance metrics in footer
  - Structured message format with game-by-game breakdowns
  - Environment variable-based webhook URL (secure secret management)
- **Data Pipeline**:
  - Automatic game schedule retrieval
  - Prediction generation for all scheduled games
  - Model learning update after predictions
  - Missing game backfill from previous 7 days

### Data Management
- **Team Statistics Tracking**: 
  - Per-team, per-venue (home/away) statistics
  - Rolling window of last 20 games to prevent memory bloat
  - Comprehensive metrics: xG, HDC, shots, goals, Corsi%, PP%, faceoff%, hits, blocked shots, takeaways, giveaways, PIM
- **Goalie Statistics**: Per-goalie GSAX tracking with minimum game thresholds
- **Prediction History**: Complete prediction log with actual outcomes for learning
- **Model State Persistence**: Saves model weights, momentum values, and performance metrics

### Prediction Methodology
- **Pre-Game Analysis**:
  - Team performance metrics from historical data
  - Situational factors (rest, goalie, venue)
  - Correlation model using re-fitted weights from completed games
  - Ensemble prediction combining multiple methods
- **70/30 Blend**: Correlation-weighted model (70%) + Ensemble model (30%)
- **Confidence Scoring**: Based on sample size, data quality, and prediction certainty
- **Lineup Integration**: Optional confirmed goalie data from lineup service for improved accuracy

### Output & Reporting
- **Discord Message Format**:
  - Game-by-game predictions with win probabilities
  - Favorite team identification with spread percentage
  - Model performance summary (total games, accuracy, recent accuracy)
  - Timestamp and model attribution
- **Console Output**: Detailed prediction breakdowns with confidence scores
- **Performance Analytics**: Team accuracy rankings and model analysis

---

## 🛠️ Shared Technical Components

### NHL API Client
- RESTful API integration with NHL's official web API
- Session management with proper headers
- Comprehensive game data retrieval (schedules, boxscores, play-by-play)
- Team roster and player statistics access
- Error handling and retry logic

### Data Processing
- Timezone-aware date handling (Central Time for NHL games)
- JSON data parsing and validation
- Historical data aggregation and analysis
- Real-time data extraction from API responses

### Code Quality
- Modular architecture with separation of concerns
- Comprehensive error handling and logging
- Type hints and documentation
- JSON-based configuration and data persistence
- Environment variable management for secrets




