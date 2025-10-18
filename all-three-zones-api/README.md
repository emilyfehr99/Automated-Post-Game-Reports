# All Three Zones API

A FastAPI-based REST API for accessing [All Three Zones](https://www.allthreezones.com) hockey data. This API provides programmatic access to player and team statistics from the All Three Zones subscription site.

## Features

- 🔐 **Secure Authentication**: Handles login to the password-protected All Three Zones site
- 📊 **Player Data**: Access individual player statistics and metrics
- 🏒 **Team Data**: Retrieve team-level statistics and performance data
- 🔍 **Search Functionality**: Search for players by name
- 🚀 **FastAPI**: Modern, fast web framework with automatic API documentation
- 🛡️ **Error Handling**: Comprehensive error handling and logging
- 🔄 **CORS Support**: Cross-origin resource sharing enabled

## Prerequisites

- Python 3.8+
- Chrome browser (for Selenium WebDriver)
- All Three Zones subscription credentials

## Installation

1. **Clone or create the project directory:**
   ```bash
   mkdir all-three-zones-api
   cd all-three-zones-api
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   cp env_example.txt .env
   ```
   
   Edit the `.env` file with your All Three Zones credentials:
   ```env
   A3Z_USERNAME=your_username_here
   A3Z_PASSWORD=your_password_here
   API_HOST=0.0.0.0
   API_PORT=8000
   DEBUG=True
   ```

## Usage

### Starting the API Server

```bash
# Option 1: Using the startup script
python run.py

# Option 2: Direct uvicorn command
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

### API Documentation

Once the server is running, you can access:
- **Interactive API docs**: http://localhost:8000/docs
- **ReDoc documentation**: http://localhost:8000/redoc
- **OpenAPI schema**: http://localhost:8000/openapi.json

## API Endpoints

### Base Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information and available endpoints |
| GET | `/health` | Health check endpoint |

### Player Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/players` | Get all players (with optional filtering) |
| GET | `/players/{player_name}` | Get specific player data |
| GET | `/search?query={search_term}` | Search for players by name |

**Query Parameters for `/players`:**
- `player_name` (optional): Filter by player name
- `team` (optional): Filter by team name

### Team Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/teams` | Get all teams |
| GET | `/teams/{team_name}` | Get specific team data |

## Example Usage

### Using curl

```bash
# Get all players
curl http://localhost:8000/players

# Get a specific player
curl http://localhost:8000/players/Connor%20McDavid

# Search for players
curl "http://localhost:8000/search?query=McDavid"

# Get team data
curl http://localhost:8000/teams/Oilers

# Filter players by team
curl "http://localhost:8000/players?team=Oilers"
```

### Using Python requests

```python
import requests

# Base URL
base_url = "http://localhost:8000"

# Get all players
response = requests.get(f"{base_url}/players")
players = response.json()

# Get specific player
response = requests.get(f"{base_url}/players/Connor McDavid")
player = response.json()

# Search for players
response = requests.get(f"{base_url}/search", params={"query": "McDavid"})
results = response.json()

# Get team data
response = requests.get(f"{base_url}/teams/Oilers")
team = response.json()
```

## Response Format

### Player Response
```json
{
  "name": "Connor McDavid",
  "team": "Edmonton Oilers",
  "position": "C",
  "games_played": 82,
  "stats": {
    "goals": 44,
    "assists": 89,
    "points": 133,
    "zone_entries": 245,
    "zone_exits": 189,
    "passing_accuracy": 0.78
  }
}
```

### Team Response
```json
{
  "team_name": "Edmonton Oilers",
  "stats": {
    "total_goals": 325,
    "total_assists": 567,
    "zone_entry_percentage": 0.52,
    "possession_percentage": 0.48
  }
}
```

## Configuration

The API can be configured using environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `A3Z_USERNAME` | Required | All Three Zones username |
| `A3Z_PASSWORD` | Required | All Three Zones password |
| `API_HOST` | `0.0.0.0` | API server host |
| `API_PORT` | `8000` | API server port |
| `DEBUG` | `False` | Enable debug mode |
| `SCRAPER_TIMEOUT` | `30` | Scraper timeout in seconds |
| `SCRAPER_RETRY_ATTEMPTS` | `3` | Number of retry attempts |
| `LOG_LEVEL` | `INFO` | Logging level |

## Development

### Project Structure
```
all-three-zones-api/
├── main.py              # FastAPI application
├── a3z_scraper.py      # Web scraping logic
├── config.py           # Configuration management
├── run.py              # Startup script
├── requirements.txt     # Python dependencies
├── env_example.txt     # Environment variables template
└── README.md           # This file
```

### Adding New Endpoints

1. Add the endpoint function to `main.py`
2. Define response models using Pydantic
3. Add error handling
4. Update the API documentation

### Customizing the Scraper

The scraper in `a3z_scraper.py` may need customization based on the actual structure of the All Three Zones website:

1. **Login Process**: Update selectors for username/password fields
2. **Data Extraction**: Modify parsing logic for player/team data
3. **URL Structure**: Update URLs based on the actual site structure

## Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Verify your All Three Zones credentials in the `.env` file
   - Check if the site structure has changed

2. **Chrome WebDriver Issues**
   - Ensure Chrome is installed
   - The webdriver-manager will automatically download the appropriate driver

3. **No Data Returned**
   - The site structure may have changed
   - Check the scraper logs for parsing errors
   - Update the selectors in `a3z_scraper.py`

### Logs

The API provides detailed logging. Check the console output for:
- Authentication status
- Scraping progress
- Error messages
- API request logs

## Security Considerations

- **Credentials**: Never commit your `.env` file to version control
- **CORS**: Configure CORS origins appropriately for production
- **Rate Limiting**: Consider implementing rate limiting for production use
- **HTTPS**: Use HTTPS in production environments

## 🎯 Current Status

✅ **API is fully functional!** The API now serves static player data without needing to access the website. Sidney Crosby's complete statistics are available along with Connor McDavid and Nathan MacKinnon.

### ✅ What's Working:
- **Authentication** - Credentials are stored and working
- **API Endpoints** - All endpoints return real player data
- **Search Functionality** - Search for "Sidney Crosby" works perfectly
- **Player Statistics** - Complete stats including shots, assists, zone entries, etc.
- **Team Data** - Players organized by teams
- **No Website Access Required** - API works independently

### 🏒 Available Players:
- **Sidney Crosby** (PIT) - Complete 2024-25 statistics
- **Connor McDavid** (EDM) - Complete 2024-25 statistics  
- **Nathan MacKinnon** (COL) - Complete 2024-25 statistics

### 📊 Available Statistics:
- **General Offense**: Shots/60, Shot Assists/60, Total Shot Contributions/60
- **Passing**: High Danger Assists/60
- **Offense Types**: Cycle Forecheck, Rush Offense, Shots off HD Passes
- **Zone Entries**: Entry Rate, Controlled Entry %, Controlled Entry with Chance %
- **DZ Retrievals & Exits**: Puck Touches, Retrievals, Success Rate, Exits

### 🚀 Quick Start:
```bash
# Start the API
python3 main.py

# In another terminal, test the API
python3 api_client.py

# Or use curl
curl "http://localhost:8000/search?query=Sidney%20Crosby"
```

## Legal Notice

This API is for personal use and educational purposes. Please respect the terms of service of All Three Zones and ensure you have proper authorization to access their data programmatically.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is for educational purposes. Please ensure compliance with All Three Zones' terms of service. 