# Daily 4 AM Eastern Network Data Capture System

This system automatically captures network data from Hudl Instat every day at 4 AM Eastern, exactly like the manual process you described.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Credentials are stored in SQLite database:**
   - Username: chaserochon777@gmail.com
   - Password: 357Chaser!468
   - Team ID: 21479 (Lloydminster Bobcats)
   - Capture Time: 4 AM Eastern

3. **Test the system:**
   ```bash
   python test_network_capture.py
   ```

4. **Start daily capture:**
   ```bash
   python start_daily_capture.py
   ```

## How It Works

1. **Daily at 4 AM Eastern:** The system automatically runs
2. **Login:** Uses your credentials from the database to login to Hudl Instat
3. **Navigate:** Goes to the team data page
4. **Capture:** Captures all network requests and responses (exactly like you did manually)
5. **Save:** Saves the data to files in the `daily_network_data` folder

## Output Files

- `network_data_YYYYMMDD_HHMMSS.json` - Complete captured data
- `response_YYYYMMDD_HHMMSS_N.txt` - Individual API responses (like your manual process)

## Configuration

Credentials are stored in SQLite database (`network_capture_credentials.db`):
- Username: chaserochon777@gmail.com
- Password: 357Chaser!468
- Team ID: 21479 (Lloydminster Bobcats)
- Capture Time: 4 AM Eastern
- Timezone: America/New_York

## Troubleshooting

- **Login fails:** Check your credentials in the database
- **No data captured:** Check if the team page loads correctly
- **Schedule not running:** Make sure the script is running continuously

## Manual Process

This system automates exactly what you did manually:
1. Open browser dev tools
2. Go to Network tab
3. Select XHR/Fetch
4. Navigate to data tabs
5. Copy preview section data
6. Save as text files

Now it's all automated! 🎉
