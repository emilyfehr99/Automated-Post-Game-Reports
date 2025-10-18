# AJHL Real Team & League API Documentation

## Overview

The AJHL Real Team & League API is a comprehensive FastAPI application that processes **real data** from Hudl Instat to provide team and league metrics for the Alberta Junior Hockey League (AJHL). This API uses actual CSV data downloaded from Hudl Instat's various tabs to calculate authentic statistics and rankings.

## Key Features

- **Real Data Source**: Uses actual CSV data from Hudl Instat platform
- **Comprehensive Metrics**: Processes data from multiple Hudl tabs (SKATERS, GOALIES, GAMES, etc.)
- **Team Analysis**: Detailed team statistics and performance metrics
- **League Rankings**: League-wide statistics and team rankings
- **Live Data**: Can refresh data directly from Hudl Instat
- **RESTful API**: Clean, documented endpoints with proper error handling

## Data Sources

The API processes data from the following Hudl Instat tabs:

1. **OVERVIEW** - Team overview and general statistics
2. **GAMES** - Game results and team performance
3. **SKATERS** - Individual skater statistics
4. **GOALIES** - Goaltender statistics
5. **LINES** - Line combinations and performance
6. **SHOT_MAP** - Shot location and analysis data
7. **FACEOFFS** - Faceoff statistics and performance
8. **EPISODES_SEARCH** - Video analysis data

## API Endpoints

### Base URL
```
http://localhost:8004
```

### Authentication
All endpoints require API key authentication via Bearer token:
```
Authorization: Bearer your_api_key_here
```

### Endpoints

#### 1. Health Check
```
GET /health
```
Returns API health status and data availability information.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00",
  "data_source": "Hudl Instat Real CSV Data",
  "csv_data_available": true,
  "teams_with_data": 12,
  "cache_age_seconds": 0
}
```

#### 2. Root Information
```
GET /
```
Returns API information, features, and available endpoints.

#### 3. Get All Teams
```
GET /teams
```
Returns all AJHL teams with data availability status.

**Response:**
```json
{
  "success": true,
  "teams": [
    {
      "team_id": "21479",
      "team_name": "Lloydminster Bobcats",
      "city": "Lloydminster",
      "province": "AB",
      "league": "AJHL",
      "hudl_team_id": "21479",
      "is_active": true,
      "has_csv_data": true,
      "data_source": "Hudl Instat CSV"
    }
  ],
  "total_teams": 12,
  "teams_with_csv_data": 8,
  "league": "AJHL",
  "data_source": "Hudl Instat Real CSV Data"
}
```

#### 4. Get Team Details
```
GET /teams/{team_id}
```
Returns detailed information about a specific team and its available data.

**Response:**
```json
{
  "success": true,
  "team": {
    "team_id": "21479",
    "team_name": "Lloydminster Bobcats",
    "city": "Lloydminster",
    "province": "AB",
    "league": "AJHL",
    "hudl_team_id": "21479",
    "is_active": true
  },
  "csv_data_summary": {
    "tabs_available": ["SKATERS", "GOALIES", "GAMES"],
    "last_updated": "2024-01-15T09:45:00",
    "total_tabs_with_data": 3
  },
  "data_source": "Hudl Instat Real CSV Data"
}
```

#### 5. Get Team Metrics
```
GET /teams/{team_id}/metrics
```
Returns comprehensive team metrics calculated from real CSV data.

**Response:**
```json
{
  "success": true,
  "team": {
    "team_id": "21479",
    "team_name": "Lloydminster Bobcats",
    "hudl_team_id": "21479"
  },
  "metrics": {
    "total_skaters": 25,
    "forwards": 15,
    "defensemen": 8,
    "total_goals": 125,
    "total_assists": 200,
    "total_points": 325,
    "avg_plus_minus": 2.5,
    "total_shots": 980,
    "shot_percentage": 12.8,
    "faceoff_percentage": 52.3,
    "total_hits": 450,
    "total_blocks": 180,
    "total_takeaways": 95,
    "total_giveaways": 78,
    "total_penalty_minutes": 320
  },
  "goalies_metrics": {
    "total_goalies": 2,
    "total_goals_against": 85,
    "total_saves": 450,
    "total_shots_against": 535,
    "save_percentage": 84.1,
    "goals_against_average": 2.8,
    "total_wins": 18,
    "total_losses": 5,
    "total_ot_losses": 2,
    "total_shutouts": 3
  },
  "games_metrics": {
    "total_games": 25,
    "wins": 18,
    "losses": 5,
    "ot_losses": 2,
    "win_percentage": 72.0,
    "points": 38,
    "total_goals_for": 125,
    "total_goals_against": 85,
    "goal_differential": 40
  },
  "faceoffs_metrics": {
    "total_faceoffs": 850,
    "faceoffs_won": 445,
    "faceoffs_lost": 405,
    "faceoff_percentage": 52.4
  },
  "data_source": "Hudl Instat Real CSV Data",
  "last_updated": "2024-01-15T09:45:00"
}
```

#### 6. Get League Statistics
```
GET /league/stats
```
Returns comprehensive league-wide statistics.

**Response:**
```json
{
  "success": true,
  "league_data": {
    "league": "AJHL",
    "data_source": "Hudl Instat Real CSV Data",
    "last_updated": "2024-01-15T10:30:00",
    "rankings": {
      "by_points": [
        {
          "team": "Brooks Bandits",
          "points": 45,
          "wins": 22,
          "losses": 3
        }
      ],
      "by_goals_for": [
        {
          "team": "Brooks Bandits",
          "goals": 145
        }
      ],
      "by_goals_against": [
        {
          "team": "Brooks Bandits",
          "goals_against": 65
        }
      ],
      "by_win_percentage": [
        {
          "team": "Brooks Bandits",
          "win_percentage": 88.0
        }
      ]
    },
    "league_totals": {
      "total_goals": 1200,
      "total_games": 300,
      "total_teams": 12,
      "avg_goals_per_team": 100.0,
      "avg_games_per_team": 25.0
    }
  },
  "data_source": "Hudl Instat Real CSV Data"
}
```

#### 7. Get League Rankings
```
GET /league/rankings
```
Returns detailed league rankings in various categories.

#### 8. Refresh Data
```
POST /refresh
```
Forces a refresh of data from Hudl Instat (downloads fresh CSV files).

**Response:**
```json
{
  "success": true,
  "message": "Data refresh completed from Hudl Instat",
  "timestamp": "2024-01-15T10:30:00",
  "data_source": "Hudl Instat Real CSV Data",
  "teams_processed": 12,
  "successful_teams": 10,
  "csv_files_downloaded": 45
}
```

## Data Processing

### CSV Data Structure

The API processes CSV files from Hudl Instat with the following structure:

#### Skaters CSV
- **G** - Goals
- **A** - Assists
- **P** - Points
- **+/-** - Plus/Minus
- **S** - Shots
- **H** - Hits
- **B** - Blocks
- **TkA** - Takeaways
- **GvA** - Giveaways
- **PIM** - Penalty Minutes
- **FO_W** - Faceoffs Won
- **FO_L** - Faceoffs Lost
- **Pos** - Position

#### Goalies CSV
- **GA** - Goals Against
- **SV** - Saves
- **SA** - Shots Against
- **W** - Wins
- **L** - Losses
- **OTL** - Overtime Losses
- **SO** - Shutouts

#### Games CSV
- **Result** - Game Result (W/L/OTL)
- **GF** - Goals For
- **GA** - Goals Against

### Metric Calculations

The API calculates various metrics from the raw CSV data:

1. **Team Totals**: Sums individual player statistics
2. **Percentages**: Calculates shooting percentage, save percentage, faceoff percentage
3. **Averages**: Computes average plus/minus, goals against average
4. **Rankings**: Sorts teams by various metrics
5. **League Totals**: Aggregates data across all teams

## Installation and Setup

### Prerequisites

1. Python 3.8+
2. Required packages (see requirements.txt)
3. Hudl Instat credentials
4. Chrome browser for web scraping

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up Hudl credentials in `hudl_credentials.py`:
   ```python
   HUDL_USERNAME = "your_username"
   HUDL_PASSWORD = "your_password"
   ```

4. Run the API:
   ```bash
   python ajhl_real_team_league_api.py
   ```

### Testing

Run the test suite:
```bash
python test_real_ajhl_api.py
```

## Data Directory Structure

```
ajhl_data/
├── daily_downloads/
│   ├── 21479/  # Lloydminster Bobcats
│   │   ├── skaters/
│   │   ├── goalies/
│   │   ├── games/
│   │   └── overview/
│   ├── 21480/  # Brooks Bandits
│   └── ...
├── logs/
└── reports/
```

## Error Handling

The API includes comprehensive error handling:

- **404 Not Found**: Team not found or no data available
- **500 Internal Server Error**: Data processing errors
- **Authentication Errors**: Invalid API key
- **Data Errors**: Missing or corrupted CSV files

## Performance Considerations

- **Caching**: Team and player data is cached for 5 minutes
- **CSV Parsing**: Efficient CSV parsing with error handling
- **Memory Usage**: Optimized for large datasets
- **Response Time**: Typically < 1 second for most endpoints

## Security

- **API Key Authentication**: All endpoints require valid API key
- **CORS**: Configured for cross-origin requests
- **Input Validation**: All inputs are validated and sanitized
- **Error Messages**: Sensitive information is not exposed in error messages

## Monitoring and Logging

- **Structured Logging**: Comprehensive logging with timestamps
- **Health Checks**: Built-in health monitoring
- **Error Tracking**: Detailed error logging and reporting
- **Performance Metrics**: Response time and data processing metrics

## Future Enhancements

1. **Real-time Updates**: WebSocket support for live data updates
2. **Advanced Analytics**: More sophisticated statistical analysis
3. **Data Visualization**: Built-in charts and graphs
4. **Export Functionality**: Export data in various formats
5. **Mobile API**: Optimized endpoints for mobile applications

## Support

For issues or questions:
1. Check the logs in `ajhl_data/logs/`
2. Verify Hudl Instat credentials
3. Ensure CSV data is available
4. Check API key authentication

## License

This project is licensed under the MIT License - see the LICENSE file for details.
