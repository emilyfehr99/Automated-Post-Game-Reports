# Hudl Instat Hockey Data Scraper

A comprehensive Python-based web scraping system for extracting play-by-play data from Hudl Instat hockey platform.

## 🏒 Features

- **Multi-User Session Management** - Prevents session conflicts when multiple users access the same account
- **Advanced CSV Extraction** - Downloads play-by-play data with customizable data selections
- **Data Analysis** - Built-in analysis tools for downloaded CSV data
- **Comprehensive Reporting** - Export detailed analysis reports
- **Predefined Data Profiles** - Quick selection of common data combinations

## 📁 Files

- `hudl_instat_analyzer.py` - Core analyzer with session management
- `hudl_csv_extractor.py` - CSV extraction with data selection interface
- `hudl_advanced_csv_extractor.py` - Advanced features and data profiles
- `test_hudl_analyzer.py` - Test script for the analyzer
- `test_hudl_csv_extraction.py` - Test script for CSV extraction

## 🚀 Quick Start

1. **Install Dependencies**
   ```bash
   pip install selenium beautifulsoup4 requests pandas webdriver-manager
   ```

2. **Set Up Credentials**
   Create `hudl_credentials.py`:
   ```python
   HUDL_USERNAME = "your_username"
   HUDL_PASSWORD = "your_password"
   ```

3. **Run Basic Test**
   ```bash
   python test_hudl_analyzer.py
   ```

4. **Extract CSV Data**
   ```bash
   python test_hudl_csv_extraction.py
   ```

## 📊 Data Selection Profiles

### Comprehensive Profile
- All shifts (even strength, power play, penalty kill)
- Main statistics (goals, assists, penalties, hits)
- Shots (shots, shots on goal, blocked shots, missed shots)
- Passes (passes, accurate passes, inaccurate passes)
- Puck battles (won/lost battles)
- Entries/Breakouts (zone entries, breakouts, faceoffs)
- Goalie statistics

### Play-by-Play Profile
- Essential play-by-play data
- Goals, assists, penalties
- Shots and shots on goal
- Passes and accuracy
- Faceoffs and zone entries

### Analytics Profile
- Advanced analytics data
- Detailed shot statistics
- Comprehensive passing data
- Puck battle analysis
- Zone-specific statistics

### Goalie-Focused Profile
- Goalie-specific statistics
- Goals against, shots against, saves
- Shootout data
- Penalty-related statistics

## 🎯 Usage Examples

### Basic CSV Extraction
```python
from hudl_csv_extractor import HudlCSVExtractor

extractor = HudlCSVExtractor()
extractor.authenticate("username", "password")
games = extractor.get_games_list()
extractor.download_game_csv(games[0])
```

### Advanced CSV Extraction with Profiles
```python
from hudl_advanced_csv_extractor import HudlAdvancedCSVExtractor

extractor = HudlAdvancedCSVExtractor()
extractor.authenticate("username", "password")
games = extractor.get_games_list()

# Download with predefined profile
extractor.download_game_with_profile(games[0], 'comprehensive')

# Download with custom selection
custom_data = {
    'main_stats': ['Goals', 'Assists'],
    'shots': ['Shots', 'Shots on goal'],
    'passes': ['Passes', 'Accurate passes']
}
extractor.download_custom_selection(games[0], custom_data)
```

### Data Analysis
```python
# Analyze downloaded CSV data
analysis = extractor.analyze_csv_data(game)
print(f"Total rows: {analysis['data_overview']['total_rows']}")
print(f"Columns: {analysis['data_overview']['columns']}")

# Export comprehensive report
extractor.export_analysis_report(games, "bobcats_analysis.json")
```

## 🔧 Configuration

### Session Management
The system uses unique user identifiers to prevent session conflicts:
```python
extractor = HudlCSVExtractor(user_identifier="user1")
```

### Data Selection
Customize exactly what data to include in your CSV:
```python
selections = {
    'shifts': ['All shifts', 'Even strength shifts'],
    'main_stats': ['Goals', 'Assists', 'Penalties'],
    'shots': ['Shots', 'Shots on goal'],
    'passes': ['Passes', 'Accurate passes']
}
```

## 📈 Team Support

Currently configured for:
- **Lloydminster Bobcats** (Team ID: 21479)
- **Bonnyville Pontiacs** (Opponent team)

## 🛠️ Technical Details

- **Browser Automation**: Selenium WebDriver with Chrome
- **Data Processing**: Pandas for CSV analysis
- **Session Management**: Unique browser profiles per user
- **Error Handling**: Comprehensive logging and error recovery
- **Rate Limiting**: Built-in delays to prevent overloading

## 📝 Requirements

- Python 3.7+
- Chrome browser
- ChromeDriver (automatically managed)
- Valid Hudl Instat account

## ⚠️ Important Notes

- This tool requires valid Hudl Instat credentials
- Respect Hudl's terms of service and rate limits
- Use responsibly and don't overload their servers
- Session conflicts are prevented through unique user identifiers

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📄 License

This project is for educational and research purposes. Please respect Hudl's terms of service.
