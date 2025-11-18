# Automated Post-Game Report Posting - Complete Code Overview

This document lists all code files involved in the automated posting of NHL post-game reports.

## 📋 Table of Contents
1. [Core Workflow Files](#core-workflow-files)
2. [Report Generation](#report-generation)
3. [Twitter Posting](#twitter-posting)
4. [API Clients](#api-clients)
5. [Automation & Orchestration](#automation--orchestration)
6. [Configuration Files](#configuration-files)
7. [Data Tracking](#data-tracking)
8. [Supporting Files](#supporting-files)

---

## 🔄 Core Workflow Files

### 1. **`.github/workflows/auto_post_reports.yml`**
   - **Purpose**: GitHub Actions workflow that runs the automation
   - **Frequency**: Runs every 10 minutes (cron: `*/10 * * * *`)
   - **What it does**:
     - Sets up Python environment
     - Installs dependencies (including poppler-utils for PDF conversion)
     - Runs `github_actions_runner.py`
     - Commits `processed_games.json` and model data back to repo
   - **Key Steps**:
     - Checkout repository
     - Set up Python 3.10
     - Install system dependencies (poppler-utils)
     - Install Python packages from `requirements.txt`
     - Run main runner with Twitter credentials from GitHub Secrets
     - Commit and push processed games tracking

### 2. **`github_actions_runner.py`** (Main Entry Point for GitHub Actions)
   - **Purpose**: Main orchestrator for GitHub Actions automation
   - **Key Methods**:
     - `get_todays_games()`: Fetches games from yesterday and today (Central Time)
     - `generate_and_post_game()`: Complete workflow for a single game:
       1. Fetches comprehensive game data
       2. Updates team stats
       3. Generates PDF report
       4. Converts PDF to PNG
       5. Posts to Twitter
       6. Cleans up files
     - `learn_from_game()`: Updates machine learning models after each game
     - `run()`: Main execution loop that:
       - Checks for completed games (FINAL or OFF status)
       - Processes each new game
       - Updates models
       - Tracks processed games
   - **Dependencies**: Uses `nhl_api_client.py`, `twitter_poster.py`, `pdf_report_generator.py`

---

## 📊 Report Generation

### 3. **`pdf_report_generator.py`**
   - **Purpose**: Generates the PDF post-game reports with analytics
   - **Key Class**: `PostGameReportGenerator`
   - **Main Method**: `generate_report(game_data, output_filename, game_id)`
   - **Features**:
     - Custom header with team logos
     - Period-by-period statistics
     - Advanced metrics (xG, high danger chances, game scores)
     - Shot plots with rink overlay
     - Team color coding
   - **Metrics Calculated**:
     - Expected Goals (xG) from play-by-play
     - High Danger Chances (xG ≥ 0.15)
     - Game Scores
     - Period-by-period stats
     - Zone-originating shots

### 4. **`batch_report_generator.py`** (Local Batch Processing)
   - **Purpose**: Generates reports for all games from a specific date
   - **Usage**: Can be run locally with `TARGET_DATE` environment variable
   - **What it does**:
     - Fetches schedule for target date
     - Generates PDF reports for all FINAL/OFF games
     - Converts PDFs to PNG images
     - Saves to Desktop folders (`NHL_Reports_*` and `NHL_Images_*`)
     - Cleans up PDF files after conversion
   - **Output**: Creates image files ready for Twitter posting

---

## 🐦 Twitter Posting

### 5. **`twitter_poster.py`**
   - **Purpose**: Handles all Twitter posting functionality
   - **Key Class**: `TwitterPoster`
   - **Key Methods**:
     - `__init__()`: Authenticates with Twitter API (v1.1 and v2)
     - `upload_media()`: Uploads images to Twitter
     - `post_individual_games()`: Posts each game report as individual tweet
     - `extract_teams_from_filename()`: Parses team names from filenames
     - `get_team_hashtags()`: Gets hashtags for teams from config
   - **Authentication**: Uses OAuth 1.0a (v1.1 for media) and OAuth 2.0 (v2 for posting)
   - **Format**: Individual posts (not threaded) for maximum reach
   - **Tweet Format**: `{away_hashtag} vs {home_hashtag}` + image

### 6. **`twitter_config.py`**
   - **Purpose**: Twitter API credentials and team hashtag configuration
   - **Contains**:
     - Twitter API credentials (from environment variables)
     - `TEAM_HASHTAGS` dictionary mapping team abbreviations to hashtags
     - NHL season start date
   - **Teams Covered**: All 32 NHL teams with official hashtags

### 7. **`twitter_api_client.py`**
   - **Purpose**: Alternative Twitter API client (appears to be for monitoring/reading tweets)
   - **Note**: This is different from `twitter_poster.py` - used for reading tweets, not posting
   - **Methods**: Get user tweets, filter NHL-related content

---

## 🌐 API Clients

### 8. **`nhl_api_client.py`**
   - **Purpose**: NHL API integration for fetching game data
   - **Key Class**: `NHLAPIClient`
   - **Base URL**: `https://api-web.nhle.com/v1`
   - **Key Methods**:
     - `get_game_schedule(date)`: Gets games for a date
     - `get_comprehensive_game_data(game_id)`: Gets full game data (boxscore + play-by-play)
     - `get_game_boxscore(game_id)`: Gets boxscore only
     - `get_game_center(game_id)`: Combines boxscore and play-by-play
   - **Used by**: All report generation and game monitoring code

---

## 🤖 Automation & Orchestration

### 9. **`game_monitor.py`** (Local Continuous Monitoring)
   - **Purpose**: Monitors games continuously in real-time (local alternative to GitHub Actions)
   - **Key Class**: `GameMonitor`
   - **Usage**: Run locally for continuous monitoring (not currently used for production)
   - **Features**:
     - Checks for completed games every N seconds (default 60)
     - Generates reports for completed games
     - Posts to Twitter immediately
     - Tracks processed games in `processed_games.json`
   - **Methods**:
     - `check_for_completed_games()`: Scans today's games for FINAL/OFF status
     - `process_game()`: Complete workflow (generate + post)
     - `generate_report()`: Calls report generator
     - `post_to_twitter()`: Handles Twitter posting

### 10. **`automated_workflow.sh`** (Shell Script for Manual/Local Runs)
   - **Purpose**: Bash script for running the complete workflow locally
   - **Usage**: `./automated_workflow.sh [DATE]`
   - **What it does**:
     1. Runs `batch_report_generator.py` to generate all reports for a date
     2. Runs `twitter_poster.py` to post all generated reports
   - **Steps**:
     - Step 1: Generate reports (batch_report_generator.py)
     - Step 2: Post to Twitter (twitter_poster.py)

---

## ⚙️ Configuration Files

### 11. **`twitter_config.py`** (Already covered above)
   - Twitter credentials and team hashtags

### 12. **`requirements.txt`**
   - Python package dependencies (not shown, but referenced in workflow)

---

## 📁 Data Tracking

### 13. **`processed_games.json`**
   - **Purpose**: Tracks which games have already been processed and posted
   - **Format**: JSON with `{"games": ["game_id1", "game_id2", ...]}`
   - **Usage**: Prevents duplicate postings
   - **Location**: Committed to git after each GitHub Actions run
   - **Logic**: Only games that successfully post are added to this list

### 14. **`season_2025_2026_team_stats.json`**
   - **Purpose**: Tracks cumulative team statistics throughout the season
   - **Updated by**: `github_actions_runner.py` after each game
   - **Contains**: Team averages for xG, HDC, Game Scores, etc.

### 15. **`win_probability_predictions_v2.json`**
   - **Purpose**: Stores machine learning model predictions and training data
   - **Updated by**: Model learning system in `github_actions_runner.py`

---

## 🔧 Supporting Files

### 16. **`SYSTEM_STATUS.md`**
   - Documentation of system status and setup

### 17. **`GITHUB_ACTIONS_SETUP.md`**
   - Setup instructions for GitHub Actions automation

### 18. **Supporting Python Files** (Used by report generator):
   - `advanced_metrics_analyzer.py`: xG model and analytics calculations
   - `advanced_prediction_model.py`: Prediction models
   - `improved_self_learning_model_v2.py`: Self-learning model for predictions
   - `correlation_model.py`: Correlation-based model

---

## 🔄 Complete Workflow

### GitHub Actions Flow (Production):
```
1. GitHub Actions triggers (.github/workflows/auto_post_reports.yml)
   ↓
2. Sets up environment (Python, dependencies, poppler-utils)
   ↓
3. Runs github_actions_runner.py
   ↓
4. github_actions_runner.py:
   a. Gets games from yesterday + today (nhl_api_client.py)
   b. Filters for FINAL/OFF games not in processed_games.json
   c. For each new game:
      - Fetches comprehensive game data (nhl_api_client.py)
      - Updates team stats
      - Generates PDF report (pdf_report_generator.py)
      - Converts PDF to PNG (pdf2image)
      - Posts to Twitter (twitter_poster.py)
      - Cleans up files
      - Updates models (learn_from_game)
      - Adds to processed_games.json
   d. Updates model learning data
   ↓
5. Commits processed_games.json and model data back to repo
```

### Local Batch Flow (Alternative):
```
1. Run batch_report_generator.py
   ↓
2. Generates PDFs for all games on target date
   ↓
3. Converts PDFs to PNGs
   ↓
4. Run twitter_poster.py
   ↓
5. Posts all generated images to Twitter
```

---

## 🔑 Key Dependencies

### External Libraries:
- `tweepy`: Twitter API client
- `reportlab`: PDF generation
- `pdf2image`: PDF to PNG conversion
- `Pillow`: Image processing
- `requests`: HTTP requests to NHL API
- `poppler-utils`: System dependency for PDF conversion

### Internal Dependencies:
- `nhl_api_client.py`: NHL data fetching
- `pdf_report_generator.py`: Report generation
- `twitter_poster.py`: Twitter posting
- `twitter_config.py`: Configuration

---

## 📝 Summary

**Main Entry Points:**
1. **Production (Automated)**: `.github/workflows/auto_post_reports.yml` → `github_actions_runner.py`
2. **Local Batch**: `batch_report_generator.py` → `twitter_poster.py`
3. **Local Continuous**: `game_monitor.py`

**Core Components:**
1. **Report Generation**: `pdf_report_generator.py`
2. **Twitter Posting**: `twitter_poster.py`
3. **Game Data**: `nhl_api_client.py`
4. **Tracking**: `processed_games.json`

**All files work together to automatically detect completed NHL games, generate beautiful PDF reports, convert them to images, and post them to Twitter with proper hashtags.**

