# Automated Post-Game Reports 🏒

An automated system for processing NHL game data, generating advanced analytics reports, and posting predictions/insights to social media (Twitter/Discord).

## 🚀 Overview
This repository contains the complete pipeline for:
- **Scraping** high-fidelity NHL edge data and game stats.
- **Training** XGBoost machine learning models for win probability and player performance.
- **Generating** comprehensive PDF post-game reports.
- **Notifying** users of predictions and outcomes via Discord and Twitter.

## 📂 Key Components

### Core Automation
- **`github_actions_runner.py`**: The main entry point for CI/CD workflows. Orchestrates the entire scraping -> prediction -> reporting pipeline.
- **`daily_prediction_notifier.py`**: Generates daily game predictions using the ensemble model and sends notifications.
- **`daily_edge_data_scraper.py`**: specialized scraper for collecting NHL EDGE tracking data (speed, distance, etc.).

### Models & Analysis
- **`train_xgboost_model.py`**: Trains the core win probability model using historical data.
- **`improved_self_learning_model_v2.py`**: The primary predictive engine.
- **`meta_ensemble_predictor.py`**: Combines multiple model outputs (XGBoost, specialized models) for final predictions.
- **`context_detector.py`**: Identifies game context (e.g., "Rivalry", "High Fatigue") to adjust model weights dynamically.

### Reporting
- **`pdf_report_generator.py`**: Creates detailed PDF reports for completed games.
- **`twitter_poster.py`**: Handles automated social media posting.

## 🛠️ Setup & Usage

### Prerequisites
- Python 3.9+
- See `requirements.txt` for dependencies.

### Installation
```bash
git clone https://github.com/your-username/automated-post-game-reports.git
cd automated-post-game-reports
pip install -r requirements.txt
```

### Running Manually
To run the daily automation locally:
```bash
python3 github_actions_runner.py
```

To run just the prediction notifier:
```bash
python3 daily_prediction_notifier.py
```

## 🗄️ Legacy Archive
As of **February 2026**, a major cleanup was performed. 
- **Active Code**: Located in the root directory (verified for production).
- **Archived Code**: Old scripts, manual tools, and previous model iterations have been moved to `_legacy/archive_2026_02`.
- **docs/README.md**: The previous StrideSync documentation has been archived as it does not apply to this repository.

## 📊 Data Sources
- NHL Official API
- Puckalytics (Edge Data)
- Rotowire (Lineups & Injuries)
