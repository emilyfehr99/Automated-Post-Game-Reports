# 🏒 NHL Post-Game Report Generator

A comprehensive Python application that generates beautiful, detailed PDF post-game reports for NHL games using the official NHL API and advanced data visualization.

## ✨ Features

- **Real-time NHL Data**: Fetches live game data from the official NHL API
- **Comprehensive Reports**: Includes scores, player stats, team comparisons, and more
- **Beautiful Visualizations**: Charts and graphs for shots, scoring by period, and team performance
- **Professional PDF Output**: Clean, organized reports using ReportLab
- **Stanley Cup Finals Focus**: Specifically designed for high-stakes playoff games
- **Fallback Support**: Includes sample data for demonstration purposes

## 📋 Requirements

- Python 3.8+
- Internet connection for NHL API access
- Required Python packages (see requirements.txt)

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Generator

```bash
python main.py
```

The application will:
1. Search for recent Florida Panthers vs Edmonton Oilers games
2. Fetch comprehensive game data from the NHL API
3. Generate a detailed PDF report
4. Save the report with a timestamp

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
- Expected Goals (xG): Probability-based scoring chances
- Rush Shots: Shots from rush opportunities
- Pressure %: Shots taken under defensive pressure

**DEFENSIVE ZONE**
- Exits: Successful zone exits
- Retrievals: Puck recoveries
- DZ Time: Time spent in defensive zone

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
├── main.py                    # Main execution script
├── nhl_api_client.py         # NHL API client
├── pdf_report_generator.py   # PDF report generator
├── requirements.txt          # Python dependencies
├── README.md                # This file
└── outputs/                 # Generated PDF reports
```

## 🎯 Example Usage

### Generate Report for Specific Teams

```python
from nhl_api_client import NHLAPIClient
from pdf_report_generator import PostGameReportGenerator

# Initialize clients
nhl_client = NHLAPIClient()
generator = PostGameReportGenerator()

# Find recent game
game_id = nhl_client.find_recent_game('FLA', 'EDM', days_back=30)

if game_id:
    # Get game data
    game_data = nhl_client.get_comprehensive_game_data(game_id)
    
    # Generate report
    generator.generate_report(game_data, 'panthers_oilers_report.pdf')
```

### Custom Team Search

```python
# Search for any team matchup
game_id = nhl_client.find_recent_game('BOS', 'TOR', days_back=60)

# Get team information
team_info = nhl_client.get_team_info(13)  # Florida Panthers
roster = nhl_client.get_team_roster(13)
```

## 🎨 Report Styling

The PDF reports feature:
- Professional color scheme (NHL team colors)
- Clean typography with Helvetica fonts
- Organized tables with alternating row colors
- Consistent spacing and layout
- High-quality charts and graphs

## 🔍 Troubleshooting

### Common Issues

1. **No games found**: The NHL API may not have recent data for specific matchups
2. **API errors**: Check internet connection and NHL API status
3. **Chart generation errors**: Ensure matplotlib and seaborn are properly installed

### Fallback Mode

If the NHL API is unavailable, the application will:
1. Generate a sample report with realistic mock data
2. Demonstrate all report features
3. Provide a template for future customization

## 📈 Future Enhancements

- **Historical Reports**: Generate reports for past games
- **Player Comparison**: Side-by-side player statistics
- **Advanced Analytics**: Expected goals, possession metrics
- **Custom Templates**: User-defined report layouts
- **Batch Processing**: Generate multiple reports at once

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
