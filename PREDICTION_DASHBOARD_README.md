# NHL Predictions Dashboard

A fast mini web dashboard for viewing pre-game and in-game NHL predictions side-by-side.

## Features

- **Pre-Game Predictions**: See win probabilities before games start
- **Live In-Game Predictions**: Real-time predictions that update as games progress
- **Auto-Refresh**: Live games update every 10 seconds automatically
- **Beautiful UI**: Clean, modern interface with responsive design
- **Fast Performance**: Lightweight Flask backend with efficient updates

## Quick Start

1. **Install Flask** (if not already installed):
   ```bash
   pip install flask==3.0.0
   ```

2. **Start the dashboard**:
   ```bash
   python prediction_dashboard.py
   ```

3. **Open your browser**:
   ```
   http://localhost:8080
   ```

## Usage

- The dashboard automatically loads today's NHL games
- Games with pre-game predictions show them in the left box
- Live games (marked with 🔴 LIVE badge) show both pre-game and live predictions side-by-side
- Live predictions update automatically every 10 seconds
- Click the "🔄 Refresh" button to manually refresh all games
- All games refresh every 60 seconds

## API Endpoints

- `GET /` - Main dashboard page
- `GET /api/games` - Get all games for today with predictions
- `GET /api/game/<game_id>` - Get specific game prediction (for live updates)

## How It Works

1. **Pre-Game Predictions**: Uses the same 70/30 blend (correlation model + ensemble) as `run_predictions_for_date.py`
2. **Live Predictions**: Uses `LiveInGamePredictor` which incorporates:
   - Current score and period
   - Live momentum factors (shots, power plays, faceoffs)
   - Time pressure adjustments
   - Base predictions adjusted by in-game factors

## Technical Details

- Built with Flask (Python backend)
- Vanilla JavaScript (no frameworks, fast loading)
- Responsive CSS Grid layout
- Real-time updates via AJAX polling
- Efficient: Only live games poll for updates

