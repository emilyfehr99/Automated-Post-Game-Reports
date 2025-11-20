# 🤖 Automatic Game Monitoring System

## Overview
Fully automatic system that monitors NHL games in real-time and posts reports to Twitter the moment they finish.

## How It Works

### The System:
1. **Monitors NHL API** every 60 seconds for game status changes
2. **Detects completed games** (FINAL or OFF status)
3. **Generates report** automatically using the report generator
4. **Posts to Twitter** immediately with proper team hashtags
5. **Tracks processed games** to avoid duplicates

### Features:
- ✅ **Fully automatic** - No manual intervention needed
- ✅ **Real-time monitoring** - Catches games as they finish
- ✅ **Duplicate prevention** - Never posts the same game twice
- ✅ **Error recovery** - Continues monitoring even if one game fails
- ✅ **Session persistence** - Remembers processed games across restarts

## Quick Start

### Start Monitoring (Simple):
```bash
cd /Users/emilyfehr8/CascadeProjects/nhl_postgame_reports
./start_monitor.sh
```

That's it! The system will now:
- Check every 60 seconds for completed games
- Generate reports and post to Twitter automatically
- Keep running until you press `Ctrl+C`

### What You'll See:
```
🤖 NHL GAME MONITOR - AUTOMATIC MODE
====================================
📅 Date: 2025-10-11
⏱️  Check interval: 60 seconds
📋 Previously processed: 0 games
====================================

🔄 Starting monitoring loop...
   Press Ctrl+C to stop

🔍 Checking for completed games... (10:15:32 PM)
   No new completed games (monitoring 4 games)

🔍 Checking for completed games... (10:16:32 PM)
✅ NEW COMPLETED GAME: DAL @ COL (ID: 2025020034)

====================================
🏒 PROCESSING: DAL @ COL
====================================

📊 Generating report for DAL @ COL...
✅ Report generated successfully for DAL @ COL

🐦 Posting DAL @ COL to Twitter...
✅ Posted to Twitter: #TexasHockey vs #GoAvsGo
   🔗 https://twitter.com/user/status/1234567890
✅ COMPLETED: DAL @ COL

⏳ Waiting 60 seconds before next check...
```

## Advanced Usage

### Custom Check Interval:
```bash
# Check every 30 seconds (faster)
python3 game_monitor.py --interval 30

# Check every 120 seconds (slower, less API calls)
python3 game_monitor.py --interval 120
```

### Reset Processed Games:
```bash
# Start fresh (useful at the start of a new day)
python3 game_monitor.py --reset
```

### Run in Background:
```bash
# Start monitoring in background
nohup ./start_monitor.sh > monitor.log 2>&1 &

# View the log in real-time
tail -f monitor.log

# Stop background monitor
pkill -f game_monitor.py
```

## Typical Workflow

### Option 1: Run During Game Days
```bash
# Start monitor when games begin
./start_monitor.sh

# Let it run all day
# Reports post automatically as games finish

# Stop when all games are done (Ctrl+C)
```

### Option 2: Leave Running Continuously
```bash
# Start in background (runs 24/7)
nohup ./start_monitor.sh > monitor.log 2>&1 &

# It will automatically detect and post new games every day
# Just let it run!
```

### Option 3: Schedule with Cron
```bash
# Edit crontab
crontab -e

# Add this line to start monitoring at 4 PM daily
0 16 * * * cd /Users/emilyfehr8/CascadeProjects/nhl_postgame_reports && ./start_monitor.sh > monitor.log 2>&1 &

# Add this line to stop monitoring at 2 AM daily
0 2 * * * pkill -f game_monitor.py
```

## How It Prevents Duplicates

The monitor maintains a `processed_games.json` file that tracks:
- All game IDs that have been processed
- Persists across restarts
- Automatically cleaned up daily (optional)

**Example:**
```json
{
  "games": [
    "2025020022",
    "2025020023",
    "2025020024"
  ]
}
```

If the monitor crashes or you restart it, it will:
- ✅ Skip games already processed
- ✅ Only process new completed games
- ✅ Never duplicate posts

## Manual Override

If you need to manually post a specific game:
```bash
# The monitor won't interfere with manual posts
python3 twitter_poster.py --date 2025-10-11
```

## Monitoring Multiple Days

The monitor always works on "today's date". To monitor:
- **Today**: Just run `./start_monitor.sh`
- **Past dates**: Use manual batch posting instead
- **Future dates**: Not supported (API doesn't have future game data)

## System Resources

### CPU Usage:
- **Idle**: ~0% (sleeping between checks)
- **Active**: ~5% (when generating reports)

### Network:
- API call every 60 seconds (~1-2 KB)
- Image upload when posting (~1-2 MB per game)

### Disk Space:
- Temporary report files (~1 MB per game)
- Automatically cleaned up after posting

## Troubleshooting

### "No games detected"
- Verify games are actually scheduled for today
- Check your internet connection
- Confirm NHL API is accessible

### "Report generation failed"
- Check that `pdf_report_generator.py` exists
- Verify all dependencies are installed
- Check error logs for details

### "Twitter posting failed"
- Verify Twitter API credentials in `twitter_config.py`
- Check if you hit rate limits (50 tweets/day on free tier)
- Ensure images are being generated correctly

### Monitor stops unexpectedly
- Check system logs: `tail -f monitor.log`
- Verify Python process is running: `ps aux | grep game_monitor`
- Restart: `./start_monitor.sh`

### Duplicate posts appearing
- Stop the monitor: `Ctrl+C`
- Reset processed games: `python3 game_monitor.py --reset`
- Restart: `./start_monitor.sh`

## Best Practices

1. **Start monitoring before games begin** (~1 hour before puck drop)
2. **Leave running all day** during heavy game days
3. **Check logs occasionally** to ensure everything is working
4. **Reset daily** if you restart the monitor each day
5. **Monitor your Twitter rate limits** (1,500 tweets/month on free tier)

## Comparison: Manual vs Automatic

### Manual Posting:
```bash
# You need to run this after every game finishes
TARGET_DATE=2025-10-11 python3 batch_report_generator.py
python3 twitter_poster.py --date 2025-10-11
```

### Automatic Monitoring:
```bash
# Run once, forget about it
./start_monitor.sh

# That's it! Everything else is automatic
```

## Safety Features

- ✅ **Duplicate prevention** - Never posts same game twice
- ✅ **Error isolation** - One failed game doesn't stop monitoring
- ✅ **Graceful shutdown** - Ctrl+C stops cleanly
- ✅ **State persistence** - Remembers what's been posted
- ✅ **API rate limiting** - Respects Twitter limits

## Future Enhancements

Potential additions (not yet implemented):
- Email notifications when games are posted
- Slack/Discord webhook integration
- Web dashboard for monitoring status
- Auto-cleanup of old reports
- Multi-day scheduling

## Support

For issues:
1. Check `monitor.log` for errors
2. Verify internet connection
3. Confirm API credentials are valid
4. Restart the monitor

---

**You're all set for fully automatic posting!** 🚀🏒

