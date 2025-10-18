# AJHL Data Collection API Documentation

## 🏒 Overview

The AJHL Data Collection API is a RESTful service that provides comprehensive hockey data collection and management for the Alberta Junior Hockey League (AJHL). It automatically scrapes data from Hudl Instat and provides it through a clean API interface.

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone <your-repo-url>
cd ajhl-api

# Create credentials file
cp hudl_credentials.py.example hudl_credentials.py
# Edit hudl_credentials.py with your Hudl credentials

# Start the API
docker-compose up -d

# Check status
curl http://localhost:8000/health
```

### Manual Installation

```bash
# Install dependencies
pip install -r ajhl_requirements.txt

# Set up credentials
cp hudl_credentials.py.example hudl_credentials.py
# Edit hudl_credentials.py

# Run the API
python ajhl_api_system.py
```

## 📚 API Endpoints

### Base URL
```
http://localhost:8000
```

### Authentication
All endpoints require an API key in the Authorization header:
```
Authorization: Bearer your-api-key-here
```

### Teams

#### Get All Teams
```http
GET /teams
```

**Response:**
```json
[
  {
    "team_id": "21479",
    "team_name": "Lloydminster Bobcats",
    "city": "Lloydminster",
    "division": "North",
    "hudl_team_id": "21479",
    "last_updated": "2024-01-15T10:30:00Z",
    "data_available": true
  }
]
```

#### Get Specific Team
```http
GET /teams/{team_id}
```

**Response:**
```json
{
  "team_id": "21479",
  "team_name": "Lloydminster Bobcats",
  "city": "Lloydminster",
  "division": "North",
  "hudl_team_id": "21479",
  "last_updated": "2024-01-15T10:30:00Z",
  "data_available": true
}
```

### Games

#### Get Games
```http
GET /games?team_id={team_id}&limit=100&offset=0
```

**Parameters:**
- `team_id` (optional): Filter by team ID
- `limit` (optional): Number of results (default: 100)
- `offset` (optional): Pagination offset (default: 0)

**Response:**
```json
[
  {
    "game_id": "game_123",
    "team_id": "21479",
    "opponent": "Brooks Bandits",
    "game_date": "2024-01-15T19:00:00Z",
    "home_away": "home",
    "result": "W 4-2",
    "data_files": ["game_123_stats.csv", "game_123_shots.csv"],
    "last_updated": "2024-01-15T22:30:00Z"
  }
]
```

#### Get Specific Game
```http
GET /games/{game_id}
```

### Players

#### Get Players
```http
GET /players?team_id={team_id}&position={position}&limit=100&offset=0
```

**Parameters:**
- `team_id` (optional): Filter by team ID
- `position` (optional): Filter by position (F, D, G)
- `limit` (optional): Number of results (default: 100)
- `offset` (optional): Pagination offset (default: 0)

**Response:**
```json
[
  {
    "player_id": "player_123",
    "team_id": "21479",
    "name": "John Smith",
    "position": "F",
    "stats": {
      "goals": 15,
      "assists": 20,
      "points": 35
    },
    "last_updated": "2024-01-15T10:30:00Z"
  }
]
```

### Data Collection

#### Trigger Data Collection
```http
POST /collect
```

**Request Body:**
```json
{
  "team_ids": ["21479", "21480"],
  "collection_type": "full",
  "force_refresh": false
}
```

**Response:**
```json
{
  "success": true,
  "message": "Data collection started for 2 teams",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### Get Collection Status
```http
GET /collect/status
```

**Response:**
```json
{
  "success": true,
  "message": "Collection status",
  "data": {
    "is_running": false,
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

#### Stop Collection
```http
POST /collect/stop
```

### Notifications

#### Get Notification Configuration
```http
GET /notifications/config
```

#### Update Notification Configuration
```http
POST /notifications/config
```

**Request Body:**
```json
{
  "email": {
    "enabled": true,
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "username": "your-email@gmail.com",
    "password": "your-app-password",
    "recipients": ["coach@team.com"]
  },
  "sms": {
    "enabled": true,
    "provider": "twilio",
    "account_sid": "your-twilio-sid",
    "auth_token": "your-twilio-token",
    "from_number": "+1234567890",
    "recipients": ["+1234567890"]
  }
}
```

#### Test Notifications
```http
POST /notifications/test
```

### System

#### Get System Status
```http
GET /status
```

**Response:**
```json
{
  "success": true,
  "message": "System status",
  "data": {
    "scraper_initialized": true,
    "notification_system_initialized": true,
    "collection_running": false,
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

#### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 🐍 Python Client Usage

### Basic Usage

```python
import asyncio
from ajhl_api_client import AJHLAPIClient, AJHLDataManager

async def main():
    async with AJHLAPIClient(
        base_url="http://localhost:8000",
        api_key="your-api-key-here"
    ) as client:
        
        # Get all teams
        teams = await client.get_teams()
        print(f"Found {len(teams)} teams")
        
        # Get Lloydminster Bobcats data
        manager = AJHLDataManager(client)
        lloydminster_data = await manager.get_lloydminster_data()
        print(f"Lloydminster has {len(lloydminster_data['recent_games'])} recent games")
        
        # Trigger data collection
        result = await client.collect_data(["21479"], collection_type="full")
        print(f"Collection result: {result}")

asyncio.run(main())
```

### Advanced Usage

```python
async def advanced_example():
    async with AJHLAPIClient(api_key="your-api-key") as client:
        # Get specific team
        team = await client.get_team("21479")
        print(f"Team: {team.team_name}")
        
        # Get recent games
        games = await client.get_recent_games("21479", days=30)
        print(f"Recent games: {len(games)}")
        
        # Get players by position
        forwards = await client.get_players_by_position("21479", "F")
        defensemen = await client.get_players_by_position("21479", "D")
        goalies = await client.get_players_by_position("21479", "G")
        
        print(f"Players: {len(forwards)}F, {len(defensemen)}D, {len(goalies)}G")
        
        # Test notifications
        await client.test_notifications()
```

## 🔧 Configuration

### Environment Variables

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_KEY=your-secure-api-key

# Database Configuration
DATABASE_URL=sqlite:///./ajhl_api.db
# or for PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost/ajhl

# Scraping Configuration
SCRAPING_HEADLESS=true
SCRAPING_TIMEOUT=30
SCRAPING_RETRIES=3

# Notification Configuration
NOTIFICATION_CHECK_INTERVAL=30
```

### Hudl Credentials

Create `hudl_credentials.py`:
```python
HUDL_USERNAME = "your-hudl-username"
HUDL_PASSWORD = "your-hudl-password"
```

### Notification Configuration

The API automatically loads notification configuration from `notification_config.json`. Use the setup script to configure:

```bash
python setup_notifications.py
```

## 📊 Data Schema

### Team Data
```json
{
  "team_id": "string",
  "team_name": "string",
  "city": "string",
  "division": "string",
  "hudl_team_id": "string",
  "last_updated": "datetime",
  "data_available": "boolean"
}
```

### Game Data
```json
{
  "game_id": "string",
  "team_id": "string",
  "opponent": "string",
  "game_date": "datetime",
  "home_away": "string",
  "result": "string",
  "data_files": ["string"],
  "last_updated": "datetime"
}
```

### Player Data
```json
{
  "player_id": "string",
  "team_id": "string",
  "name": "string",
  "position": "string",
  "stats": "object",
  "last_updated": "datetime"
}
```

## 🔄 Data Collection Process

1. **Authentication**: API authenticates with Hudl Instat
2. **Team Discovery**: Identifies teams and their Hudl team IDs
3. **Data Scraping**: Scrapes data from all 8 Hudl Instat tabs
4. **Data Processing**: Processes and normalizes the data
5. **Database Storage**: Stores data in SQLite/PostgreSQL
6. **Notification**: Sends notifications if configured
7. **API Access**: Data available through REST API

## 🚨 Error Handling

The API uses standard HTTP status codes:

- `200`: Success
- `400`: Bad Request
- `401`: Unauthorized
- `404`: Not Found
- `500`: Internal Server Error

Error responses include details:
```json
{
  "success": false,
  "message": "Error description",
  "error": "Detailed error information",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 📈 Monitoring and Logging

### Health Checks
- `GET /health` - Basic health check
- `GET /status` - Detailed system status

### Logging
- Application logs: `ajhl_data/logs/`
- Database logs: SQLite/PostgreSQL logs
- Scraping logs: Selenium/Requests logs

### Metrics
- Collection success rate
- API response times
- Data freshness
- System uptime

## 🔒 Security

### API Key Authentication
All endpoints require a valid API key in the Authorization header.

### Rate Limiting
Consider implementing rate limiting for production use.

### Data Privacy
- No sensitive data stored in logs
- Secure credential storage
- HTTPS recommended for production

## 🚀 Deployment

### Production Deployment

1. **Set up reverse proxy** (nginx)
2. **Configure SSL/TLS**
3. **Set up monitoring**
4. **Configure backups**
5. **Set up logging aggregation**

### Scaling

- **Horizontal scaling**: Multiple API instances behind load balancer
- **Database scaling**: PostgreSQL with read replicas
- **Caching**: Redis for frequently accessed data
- **CDN**: For static assets and documentation

## 📞 Support

### API Documentation
- Interactive docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Troubleshooting
1. Check health endpoint
2. Review logs
3. Verify credentials
4. Test individual components

### Common Issues
- **Authentication failures**: Check Hudl credentials
- **Scraping errors**: Check network connectivity
- **Database errors**: Check database connection
- **Notification failures**: Check notification configuration

## 🎯 Next Steps

1. **Deploy the API** using Docker
2. **Configure notifications** for your team
3. **Set up monitoring** and alerting
4. **Integrate with your analytics** tools
5. **Build custom dashboards** using the API data

The AJHL Data Collection API provides a robust, scalable solution for collecting and managing hockey data with real-time notifications and comprehensive API access.
