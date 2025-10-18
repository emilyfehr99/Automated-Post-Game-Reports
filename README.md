# 🏒 NHL Post-Game Report Generator

A comprehensive Python application that generates beautiful, detailed PDF post-game reports for NHL games using the official NHL API and advanced data visualization.

## ✨ Features

- **Real-time NHL Data**: Fetches live game data from the official NHL API
- **Advanced Hockey Metrics**: Pre-shot movement analysis, pressure sequences, zone-originating shots
- **Beautiful Visualizations**: Shot location plots with team logos and color-coded data
- **Professional PDF Output**: Single-page reports with dynamic team colors and logos
- **Batch Processing**: Generate reports for all games on any date
- **Automatic Image Conversion**: PDFs automatically converted to PNG format
- **OT/SO Support**: Dynamic table rows and indicators for overtime and shootout games
- **🐦 Twitter Automation**: Automatically post reports to Twitter with team hashtags
- **🤖 Fully Automatic Monitoring**: Real-time game monitoring with automatic posting

## 📋 Requirements

- Python 3.8+
- Internet connection for NHL API access
- Required Python packages (see requirements.txt)

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Generate Reports for a Specific Date

```bash
# Generate reports for all games on a specific date
TARGET_DATE="2025-10-08" python3 batch_report_generator.py

# Or use yesterday's games by default
python3 batch_report_generator.py
```

The batch generator will:
1. Fetch all NHL games for the specified date
2. Generate comprehensive reports for each game
3. Convert PDFs to PNG images automatically
4. Save all files to a date-stamped folder on your Desktop

### 3. Fully Automatic (Cloud) - RECOMMENDED ☁️🤖

**Set it up once, never touch it again! Runs 24/7 even when your laptop is off.**

```bash
# One-time setup (5 minutes):
# 1. Add Twitter API secrets to GitHub repo settings
# 2. Push the code (already done!)
# 3. Done! It runs automatically in the cloud forever

# See GITHUB_ACTIONS_SETUP.md for step-by-step instructions
```

**Features:**
- ✅ Runs in GitHub's cloud (no laptop needed!)
- ✅ Checks every 15 minutes for completed games
- ✅ Completely FREE forever
- ✅ Generates and posts automatically
- ✅ Works even when you're offline

See [GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md) for setup instructions.

### 4. Automatic Monitoring (Local) 🤖

**Alternative: Run on your laptop when it's on**

```bash
# Start the automatic monitor
./start_monitor.sh

# The system will:
# - Monitor games in real-time (checks every 60 seconds)
# - Generate reports when games finish
# - Post to Twitter automatically
# - Keep running until you press Ctrl+C
```

**Note:** Laptop must stay on. For 24/7 automation without your laptop, use GitHub Actions (Option 3) instead.

See [AUTOMATIC_MONITORING.md](AUTOMATIC_MONITORING.md) for complete local monitoring documentation.

### 5. Manual Twitter Posting (Optional)

If you prefer manual control:

```bash
# Post today's completed game reports to Twitter
python3 twitter_poster.py

# Or post reports from a specific date
python3 twitter_poster.py --date 2025-10-11
```

The Twitter poster will:
1. Post each game as an individual tweet (no threading)
2. Use proper team hashtags for maximum reach
3. Maximize visibility across Hockey Twitter and team hashtag searches
4. Automatically handle all games from that date

**Why individual posts?** Higher algorithmic reach, better hashtag visibility, and independent engagement per game.

See [TWITTER_POSTING_GUIDE.md](TWITTER_POSTING_GUIDE.md) for detailed Twitter automation setup.

## 📊 Report Contents

Each generated report includes:

### Header Section
- **Team Logos**: Away and home team logos with NHL logo
- **Title**: Team matchup (e.g., "MTL vs TOR")
- **Subtitle**: "Post Game Report" with date, score, and winner
- **Grey Accent Line**: Visual separator (0.5 cm thick, matches subtitle width)
- **OT/SO Indicator**: Shows "(OT)" or "(SO)" in subtitle when applicable

### Period-by-Period Statistics Table
Complete breakdown by period including:
- **GF**: Goals For (goals scored per period, including OT/SO when applicable)
- **S**: Total shots on goal
- **H**: Physical plays (hits)
- **BLK**: Blocked shots
- **FO%**: Faceoff win percentage
- **PP**: Power play opportunities and goals
- **GA**: Giveaways (turnovers)
- **TA**: Takeaways
- **xG**: Expected Goals (advanced metric for scoring chances)
- **CF%**: Corsi For Percentage (shot attempt differential)
- **OZS**: Offensive zone originating shots
- **NZS**: Neutral zone originating shots
- **DZS**: Defensive zone originating shots

### Advanced Metrics Table
Four key categories with team comparisons (team logos in headers):

**SHOT QUALITY**
- **Expected Goals (xG)**: Probability-based scoring metric using distance, angle, shot type, and zone to predict likelihood of scoring
- **High Danger Shots**: Shots on goal with xG ≥ 0.15 (15%+ scoring probability). Considers distance from goal, shot angle, shot type (wrist, slap, tip-in, etc.), and zone. All goals automatically count as high danger shots.
- **Total Shots**: All shot attempts (includes shots on goal, missed shots, and blocked shots)
- **Shots on Goal**: Shots that reached the goalie or resulted in a goal
- **Shooting %**: Goals divided by shots on goal

**DEFENSIVE**
- **Blocked Shots**: Shots blocked by defending team before reaching the goalie
- **Takeaways**: Successful puck takeaways from opponent
- **Hits**: Physical hits delivered
- **Shot Attempts Against**: Total shots faced (includes shots on goal, missed shots, blocked shots, and goals)
- **High Danger Chances Against**: Opponent shot attempts with xG ≥ 0.15 (15%+ scoring probability). Uses the same xG model as High Danger Shots but includes ALL shot types (not just shots on goal) - measures total dangerous pressure faced, including shots that were blocked or missed the net.

**PRE-SHOT MOVEMENT** *(New metrics)*

- **Royal Road Proxy**: Shots taken after the puck crosses the "Royal Road" (the center vertical line of the ice) within 4 seconds. These cross-seam passes create high-quality scoring chances by forcing the goalie to move laterally across the crease.

- **OZ Retrieval to Shot**: Shots generated within 5 seconds of winning the puck back in the offensive zone through a hit or takeaway. Measures a team's ability to quickly capitalize on puck recoveries and maintain offensive pressure.

- **Lateral Movement (E-W)**: Pre-shot east-west (side-to-side) puck movement within 4 seconds before a shot. Categories: Minor side-to-side (0-10 ft), Cross-ice movement (10-20 ft), Wide cross-ice (20+ ft). Greater lateral movement typically creates better shooting angles.

- **Longitudinal Movement (N-S)**: Pre-shot north-south (toward/away from goal) puck movement within 4 seconds before a shot. Categories: Point-blank range (0-10 ft), Close-range shot (10-20 ft), Zone entry shots (20-40 ft), Long-range rush (40+ ft). Measures shot generation from different ice depths.

**PRESSURE & TRANSITION**

- **Sustained Pressure Sequences**: Extended offensive possessions where a team generates multiple shot attempts in succession without the opponent clearing the zone. Indicates cycle game effectiveness and ability to maintain offensive zone time.

- **Quick Strike Opportunities**: Rapid transition chances where a team generates a shot attempt within seconds of gaining possession. Measures effectiveness of rush attacks and fast-break opportunities before the defense can set up.

### Shot Location Visualization
- **Shot Plot**: Visual representation of all shots on ice surface
- **Home Team Logo**: Displayed at center ice on shot plot
- Color-coded by team

### Top Players Table
- **Top 3 Performers**: Based on points (goals + assists)
- Player names and point totals
- Team color-coded backgrounds

### Report Styling
- **Team Colors**: Dynamic colors based on teams playing
- **Professional Layout**: Clean typography with consistent spacing
- **Single Page Format**: All content fits on one page (even with OT/SO rows)
- **PNG Export**: Automatically converted to image format

## 🔧 Configuration

### NHL API Endpoints

The application uses the official NHL API:
- Base URL: `https://api-web.nhle.com/v1`
- No API key required
- Rate limiting may apply

### Customization

You can modify the report generation by editing:
- `pdf_report_generator.py` - Report layout and styling
- `nhl_api_client.py` - API endpoints and data fetching
- `main.py` - Main execution logic

## 📁 File Structure

```
nhl_postgame_reports/
├── batch_report_generator.py    # Batch report generation for all games
├── pdf_report_generator.py      # PDF report generator
├── advanced_metrics_analyzer.py # Advanced hockey metrics calculator
├── nhl_api_client.py            # NHL API client
├── pdf_to_image_converter.py    # PDF to PNG converter
├── requirements.txt             # Python dependencies
├── README.md                    # This file
└── RussoOne-Regular.ttf         # Custom font for headers
```

## 🎯 Example Usage

### Generate Reports for All Games on a Date

```bash
# Generate for specific date
TARGET_DATE="2025-10-08" python3 batch_report_generator.py

# Generate for yesterday's games
python3 batch_report_generator.py
```

### Generate Single Game Report

```python
from nhl_api_client import NHLAPIClient
from pdf_report_generator import PostGameReportGenerator

# Initialize
api = NHLAPIClient()
generator = PostGameReportGenerator()

# Get specific game
game_data = api.get_game_data(2025020001)  # Game ID
boxscore = api.get_boxscore(2025020001)

# Generate report
generator.generate_report(game_data, boxscore, 'game_report.pdf')
```

### Access Advanced Metrics

```python
from advanced_metrics_analyzer import AdvancedMetricsAnalyzer

# Analyze game
analyzer = AdvancedMetricsAnalyzer(game_data)

# Get pre-shot movement metrics
pre_shot = analyzer.calculate_pre_shot_movement_metrics(team_id)
# Returns: royal_road_proxy, oz_retrieval_to_shot, lateral_movement, longitudinal_movement

# Get pressure metrics
pressure = analyzer.calculate_pressure_metrics(team_id)
# Returns: sustained_pressure_sequences, quick_strike_opportunities
```

## 🎨 Report Styling

The PDF reports feature:
- **Dynamic Team Colors**: Automatically uses official NHL team colors
- **Team Logos**: ESPN logos in advanced metrics headers, team logos on shot plots
- **Custom Typography**: Russo One font for headers, Helvetica for body text
- **Grey Accent Line**: Professional separator below subtitle
- **Single-Page Layout**: All content compressed to fit on one page
- **Automatic PNG Export**: Reports converted to images for easy sharing

## 🔍 Troubleshooting

### Common Issues

1. **No games found**: Check the date format (YYYY-MM-DD) and ensure games were played
2. **API errors**: NHL API occasionally has delays; try again in a few minutes
3. **Logo loading failures**: Team logos are fetched from ESPN CDN; requires internet connection
4. **Font missing**: Ensure `RussoOne-Regular.ttf` is in the project directory

### Output Location

Reports are saved to:
- **Desktop folder**: `NHL_Reports_YYYY_MM_DD/`
- **PNG files**: `nhl_postgame_report_TEAM_vs_TEAM_timestamp.png`
- **Original PDFs**: Automatically deleted after PNG conversion

## 📈 Implemented Features

✅ **Advanced Pre-Shot Movement Metrics**
- Royal Road Proxy (cross-seam passes)
- OZ Retrieval to Shot (puck recovery conversions)
- Lateral Movement (E-W) with descriptive categories
- Longitudinal Movement (N-S) with descriptive categories

✅ **Pressure & Transition Analytics**
- Sustained Pressure Sequences
- Quick Strike Opportunities

✅ **Dynamic Game Support**
- OT/SO automatic detection and row insertion
- Accurate goals-by-period calculation from play-by-play
- Indicator in subtitle for OT/SO games

✅ **Professional Presentation**
- Team logos in table headers
- Zone-originating shot metrics (OZS, NZS, DZS)
- Renamed columns for clarity (GF, BLK, CF%, S)

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Additional statistical categories
- Enhanced visualizations
- More team-specific customization
- Performance optimizations

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- NHL for providing the official API
- ReportLab for PDF generation capabilities
- Matplotlib and Seaborn for data visualization
- The hockey analytics community for inspiration

---

**Note**: This application is for educational and personal use. Please respect the NHL's terms of service and API usage guidelines.
