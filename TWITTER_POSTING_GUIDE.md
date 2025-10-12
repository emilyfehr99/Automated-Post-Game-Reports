# 🐦 Automated Twitter Posting Guide

## Overview
Automatically post NHL Post-Game Reports to Twitter with proper team hashtags and threading.

## Features
- ✅ Automatic thread creation ("Week X Day Y - NHL Post-Game Reports 🏒")
- ✅ Posts each game report as a reply in the thread
- ✅ Uses official team hashtags for each matchup
- ✅ Automatically calculates week/day based on NHL season schedule
- ✅ Handles multiple games per day

## Quick Start

### 1. Post Today's Games
```bash
python3 twitter_poster.py
```

### 2. Post Specific Date
```bash
python3 twitter_poster.py --date 2025-10-11
```

### 3. Post from Custom Folder
```bash
python3 twitter_poster.py --date 2025-10-11 --image-folder /path/to/images
```

## How It Works

### Thread Structure
1. **Parent Tweet**: "Week 1 Day 3 - NHL Post-Game Reports 🏒"
2. **Reply Tweets**: Each game report posted as a reply with team hashtags

Example:
```
Week 1 Day 3 - NHL Post-Game Reports 🏒
October 11, 2025
  ↳ #GoKingsGo vs #GoJetsGo [image]
  ↳ #STLBlues vs #Flames [image]
  ↳ #SabreHood vs #NHLBruins [image]
  ... (all games from that day)
```

### Tweet Format
Each game tweet contains:
- Away team hashtag
- "vs"
- Home team hashtag
- Report image attached

Example: `#GoKingsGo vs #GoJetsGo`

## Team Hashtags

All 32 NHL team hashtags are configured in `twitter_config.py`:

| Team | Hashtag |
|------|---------|
| ANA | #FlyTogether |
| BOS | #NHLBruins |
| BUF | #SabreHood |
| CGY | #Flames |
| CAR | #CarolinaCultre |
| CHI | #Blackhawks |
| COL | #GoAvsGo |
| CBJ | #CBJ |
| DAL | #TexasHockey |
| DET | #LGRW |
| EDM | #LetsGoOilers |
| FLA | #TimeToHunt |
| LAK | #GoKingsGo |
| MIN | #MNWild |
| MTL | #GoHabsGo |
| NSH | #Smashville |
| NJD | #NJDevils |
| NYI | #Isles |
| NYR | #NYR |
| OTT | #GoSensGo |
| PHI | #LetsGoFlyers |
| PIT | #LetsGoPens |
| SJS | #TheFutureIsTeal |
| SEA | #SeaKraken |
| STL | #STLBlues |
| TBL | #GoBolts |
| TOR | #LeafsForever |
| UTA | #TusksUp |
| VAN | #Canucks |
| VGK | #VegasBorn |
| WSH | #ALLCAPS |
| WPG | #GoJetsGo #NHLJets |

## Configuration

### Season Start Date
Update `NHL_SEASON_START` in `twitter_config.py` if needed:
```python
NHL_SEASON_START = '2025-10-08'
```

### API Credentials
Stored in `twitter_config.py`. For security, consider using environment variables:
```bash
export TWITTER_API_KEY="your_key"
export TWITTER_API_SECRET="your_secret"
export TWITTER_ACCESS_TOKEN="your_token"
export TWITTER_ACCESS_TOKEN_SECRET="your_token_secret"
```

## Typical Workflow

### After Games Complete
```bash
# 1. Generate reports for the day
cd /Users/emilyfehr8/CascadeProjects/nhl_postgame_reports
TARGET_DATE=2025-10-11 python3 batch_report_generator.py

# 2. Post to Twitter
python3 twitter_poster.py --date 2025-10-11

# Done! All reports posted in a threaded format
```

## Troubleshooting

### "Authentication failed"
- Check your API credentials in `twitter_config.py`
- Ensure your Twitter Developer App has read/write permissions

### "No report images found"
- Verify the image folder path is correct
- Check that report generation completed successfully
- Default folder: `/Users/emilyfehr8/Desktop/NHL_Images_YYYY_MM_DD`

### "Could not extract teams from filename"
- Ensure report filenames follow the pattern: `nhl_postgame_report_XXX_vs_YYY_*.png`
- Check that the batch generator completed successfully

### Rate Limits
- Twitter Free tier: 1,500 tweets/month
- If you hit rate limits, wait 15 minutes or upgrade your API plan

## Security Note

⚠️ **IMPORTANT**: Your API credentials are currently hardcoded. For production use:

1. **Regenerate your credentials** in the Twitter Developer Portal
2. Use environment variables instead:
   ```bash
   # Add to ~/.zshrc or ~/.bash_profile
   export TWITTER_API_KEY="your_new_key"
   export TWITTER_API_SECRET="your_new_secret"
   export TWITTER_ACCESS_TOKEN="your_new_token"
   export TWITTER_ACCESS_TOKEN_SECRET="your_new_token_secret"
   ```
3. Remove hardcoded credentials from `twitter_config.py`

## Support

For issues or questions:
- Check Twitter API status: https://api.twitterstat.us/
- Twitter Developer Portal: https://developer.twitter.com/

