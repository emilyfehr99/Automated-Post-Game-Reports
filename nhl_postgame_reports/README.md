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

### Game Summary
- Final score with period-by-period breakdown
- Game date, venue, and type
- Team information

### Team Statistics
- Goals, shots, power play conversion
- Penalty minutes, hits, faceoffs
- Blocked shots, giveaways, takeaways

### Scoring Summary
- Complete play-by-play scoring
- Goal scorers and assists
- Period and time information

### Player Performance
- Top goal scorers
- Leading assist providers
- Individual player statistics

### Goalie Analysis
- Shots against and saves
- Save percentage
- Time on ice

### Game Analysis
- Game flow analysis
- Key moments breakdown
- Special teams performance

### Visualizations
- Shots on goal comparison
- Scoring by period charts
- Team performance graphs

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
