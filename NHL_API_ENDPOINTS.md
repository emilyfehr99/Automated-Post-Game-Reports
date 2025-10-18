# 🏒 NHL API Complete Endpoint Guide

## 🚀 Base URL
```
https://api-web.nhle.com/v1
```

## 📊 Available Endpoints & Data

### 🏒 TEAM ENDPOINTS

#### 1. Team Information
```
GET /teams/{team_id}
```
**Example:** `https://api-web.nhle.com/v1/teams/13` (Florida Panthers)

**Data Provided:**
- `name`: Team full name
- `abbrev`: Team abbreviation (FLA, EDM, etc.)
- `conferenceName`: Conference (Eastern, Western)
- `divisionName`: Division (Atlantic, Central, etc.)
- `venue`: Arena information
- `franchiseId`: Franchise identifier
- `teamId`: Unique team ID
- `locationName`: City name
- `teamName`: Team nickname
- `officialSiteUrl`: Official website
- `timeZone`: Time zone information

#### 2. Team Roster
```
GET /teams/{team_id}/roster
```
**Example:** `https://api-web.nhle.com/v1/teams/13/roster`

**Data Provided:**
- `forwards[]`: Array of forward players
- `defensemen[]`: Array of defensemen
- `goalies[]`: Array of goalies

**Each Player Contains:**
- `id`: Unique player ID
- `name`: Player full name
- `position`: Position (C, LW, RW, D, G)
- `jerseyNumber`: Jersey number
- `height`: Height in feet/inches
- `weight`: Weight in pounds
- `birthDate`: Birth date
- `birthCity`: Birth city
- `birthCountry`: Birth country
- `shootsCatches`: Handedness
- `rookie`: Rookie status

#### 3. Team Statistics
```
GET /teams/{team_id}/stats
```
**Example:** `https://api-web.nhle.com/v1/teams/13/stats`

**Data Provided:**
- `stats`: Season statistics
- `standings`: Current standings position
- `team`: Team information
- `season`: Season details

---

### 🏃 PLAYER ENDPOINTS

#### 1. Player Profile
```
GET /players/{player_id}
```
**Example:** `https://api-web.nhle.com/v1/players/8478402` (Connor McDavid)

**Data Provided:**
- `id`: Player ID
- `name`: Full name
- `position`: Position
- `height`: Height
- `weight`: Weight
- `birthDate`: Birth date
- `birthCity`: Birth city
- `birthCountry`: Birth country
- `nationality`: Nationality
- `shootsCatches`: Handedness
- `rookie`: Rookie status
- `active`: Active status
- `alternateCaptain`: Alternate captain status
- `captain`: Captain status
- `assistantCaptain`: Assistant captain status

#### 2. Player Statistics
```
GET /players/{player_id}/stats
```
**Example:** `https://api-web.nhle.com/v1/players/8478402/stats`

**Data Provided:**
- `stats`: Statistics by type
  - `gameLog`: Game-by-game statistics
  - `season`: Season totals
  - `career`: Career totals
  - `playoffs`: Playoff statistics
  - `vsTeam`: Statistics vs specific teams
  - `homeAndAway`: Home/away splits
  - `winLoss`: Win/loss record
  - `monthly`: Monthly statistics
  - `weekly`: Weekly statistics

**Statistical Categories:**
- **Skater Stats**: Goals, assists, points, shots, hits, blocks, faceoffs
- **Goalie Stats**: Wins, losses, saves, goals against, save percentage, shutouts
- **Advanced Stats**: Time on ice, power play points, short-handed points

#### 3. Player Game Log
```
GET /players/{player_id}/game-log
```
**Example:** `https://api-web.nhle.com/v1/players/8478402/game-log`

**Data Provided:**
- `gameLog[]`: Array of individual games
- Each game contains:
  - `gameId`: Game identifier
  - `gameDate`: Game date
  - `opponent`: Opposing team
  - `homeAway`: Home or away game
  - `goals`: Goals scored
  - `assists`: Assists
  - `points`: Total points
  - `plusMinus`: Plus/minus rating
  - `timeOnIce`: Time on ice
  - `powerPlayGoals`: Power play goals
  - `powerPlayAssists`: Power play assists
  - `shortHandedGoals`: Short-handed goals
  - `shortHandedAssists`: Short-handed assists

---

### 🎮 GAME ENDPOINTS

#### 1. Game Center Feed (Live Data)
```
GET /gamecenter/{game_id}/feed/live
```
**Example:** `https://api-web.nhle.com/v1/gamecenter/2024030416/feed/live`

**Data Provided:**
- `game`: Game information
  - `id`: Game ID
  - `gameDate`: Game date
  - `gameState`: Game status (LIVE, FINAL, etc.)
  - `awayTeamScore`: Away team score
  - `homeTeamScore`: Home team score
  - `awayTeamScoreByPeriod[]`: Period-by-period away scoring
  - `homeTeamScoreByPeriod[]`: Period-by-period home scoring
  - `periodNumber`: Current period
  - `timeInPeriod`: Time remaining in period
- `awayTeam`: Away team information
- `homeTeam`: Home team information
- `venue`: Arena information
- `plays[]`: Play-by-play data
  - `typeDescKey`: Type of play (goal, penalty, etc.)
  - `periodNumber`: Period number
  - `timeInPeriod`: Time in period
  - `team`: Team involved
  - `scorer`: Goal scorer (for goals)
  - `players[]`: Players involved in play
  - `score`: Score at time of play

#### 2. Game Boxscore
```
GET /gamecenter/{game_id}/boxscore
```
**Example:** `https://api-web.nhle.com/v1/gamecenter/2024030416/boxscore`

**Data Provided:**
- `awayTeam`: Away team statistics
  - `score`: Final score
  - `sog`: Shots on goal
  - `powerPlayConversion`: Power play success
  - `penaltyMinutes`: Penalty minutes
  - `hits`: Hits
  - `faceoffWins`: Faceoff wins
  - `blockedShots`: Blocked shots
  - `giveaways`: Giveaways
  - `takeaways`: Takeaways
  - `players[]`: Individual player statistics
- `homeTeam`: Home team statistics (same structure)
- `officials`: Game officials
- `teamStats`: Team statistical comparison

**Individual Player Stats:**
- `goals`: Goals scored
- `assists`: Assists
- `points`: Total points
- `shots`: Shots on goal
- `hits`: Hits delivered
- `blocks`: Shots blocked
- `timeOnIce`: Time on ice
- `plusMinus`: Plus/minus rating
- `powerPlayGoals`: Power play goals
- `powerPlayAssists`: Power play assists
- `shortHandedGoals`: Short-handed goals
- `shortHandedAssists`: Short-handed assists
- `penaltyMinutes`: Penalty minutes

#### 3. Game Summary
```
GET /gamecenter/{game_id}/summary
```
**Example:** `https://api-web.nhle.com/v1/gamecenter/2024030416/summary`

**Data Provided:**
- Game overview information
- Key statistics summary
- Period summaries
- Team performance highlights

---

### 📅 SCHEDULE ENDPOINTS

#### 1. Daily Schedule
```
GET /schedule/{date}
```
**Example:** `https://api-web.nhle.com/v1/schedule/2024-08-18`

**Data Provided:**
- `gameWeek[]`: Array of days
  - `date`: Date
  - `games[]`: Games on that date
    - `id`: Game ID
    - `gameDate`: Game date
    - `awayTeam`: Away team info
    - `homeTeam`: Home team info
    - `venue`: Arena
    - `gameState`: Game status
    - `startTimeUTC`: Start time

#### 2. Weekly Schedule
```
GET /schedule/week/{period}
```
**Example:** `https://api-web.nhle.com/v1/schedule/week/now`

**Data Provided:**
- Weekly game schedule
- Team matchups
- Game times and venues

---

### 🏆 LEAGUE ENDPOINTS

#### 1. Current Standings
```
GET /standings/now
```
**Example:** `https://api-web.nhle.com/v1/standings/now`

**Data Provided:**
- `standings[]`: Array of team standings
  - `team`: Team information
  - `stats`: Team statistics
  - `conferenceRank`: Conference ranking
  - `divisionRank`: Division ranking
  - `leagueRank`: League ranking
  - `points`: Total points
  - `gamesPlayed`: Games played
  - `wins`: Wins
  - `losses`: Losses
  - `overtimeLosses`: Overtime losses
  - `pointsPercentage`: Points percentage

#### 2. Player Search
```
GET /players/search
```
**Example:** `https://api-web.nhle.com/v1/players/search`

**Data Provided:**
- Player search functionality
- Player suggestions
- Search results

#### 3. Draft Information
```
GET /draft/{year}
```
**Example:** `https://api-web.nhle.com/v1/draft/2024`

**Data Provided:**
- Draft year information
- Draft picks
- Player selections
- Team draft results

---

## 🎯 Data Categories by Position

### 🏃 **SKATERS (Forwards & Defensemen)**
- **Basic Stats**: Goals, assists, points, plus/minus
- **Shooting**: Shots on goal, shooting percentage
- **Physical**: Hits, blocked shots, penalty minutes
- **Special Teams**: Power play goals/assists, short-handed goals/assists
- **Time**: Time on ice, average time on ice
- **Faceoffs**: Faceoff wins, faceoff percentage (centers)
- **Advanced**: Giveaways, takeaways, game-winning goals

### 🥅 **GOALIES**
- **Record**: Wins, losses, overtime losses
- **Saves**: Saves, save percentage, goals against average
- **Games**: Games played, games started, complete games
- **Shutouts**: Shutouts, shutout percentage
- **Time**: Time on ice, average time on ice
- **Special Situations**: Power play saves, short-handed saves
- **Quality**: Quality starts, really bad starts

### 🏒 **TEAMS**
- **Scoring**: Goals for, goals against, goal differential
- **Shooting**: Shots for, shots against, shooting percentage
- **Special Teams**: Power play percentage, penalty kill percentage
- **Physical**: Hits, blocked shots, penalty minutes
- **Faceoffs**: Faceoff wins, faceoff percentage
- **Advanced**: Giveaways, takeaways, team save percentage

---

## 🔧 Usage Examples

### Get Florida Panthers Roster
```python
import requests
url = "https://api-web.nhle.com/v1/teams/13/roster"
response = requests.get(url)
roster = response.json()
forwards = roster['forwards']
goalies = roster['goalies']
```

### Get Player Statistics
```python
url = "https://api-web.nhle.com/v1/players/8478402/stats"
response = requests.get(url)
stats = response.json()
season_stats = stats['stats']['season']
```

### Get Live Game Data
```python
url = "https://api-web.nhle.com/v1/gamecenter/2024030416/feed/live"
response = requests.get(url)
game_data = response.json()
score = f"{game_data['game']['awayTeamScore']} - {game_data['game']['homeTeamScore']}"
```

---

## 📈 Data Availability

- **Real-time**: Live game data, scores, play-by-play
- **Daily**: Game schedules, standings updates
- **Seasonal**: Player statistics, team performance
- **Historical**: Career stats, past seasons
- **Archival**: Draft information, franchise history

This comprehensive API provides everything needed to build advanced hockey analytics, real-time game tracking, and detailed player/team analysis systems.
