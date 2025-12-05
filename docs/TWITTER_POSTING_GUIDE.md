# 🐦 Automated Twitter Posting Guide

## Overview
Automatically post NHL Post-Game Reports to Twitter with proper team hashtags as **individual posts** for maximum reach and engagement.

## Features
- ✅ Posts each game as an individual tweet (no threading)
- ✅ Uses official team hashtags for each matchup
- ✅ Maximizes reach across Hockey Twitter and team hashtag searches
- ✅ Each game gets independent engagement and visibility
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

### Individual Post Strategy
Each game is posted as a **standalone tweet** for maximum visibility and engagement.

Example Timeline:
```
Tweet 1: #GoKingsGo vs #GoJetsGo #NHLJets [image]
Tweet 2: #STLBlues vs #Flames [image]
Tweet 3: #SabreHood vs #NHLBruins [image]
... (each game as separate post)
```

### Tweet Format
Each game tweet contains:
- Away team hashtag
- "vs"
- Home team hashtag
- Report image attached

Example: `#GoKingsGo vs #GoJetsGo #NHLJets`

### Why Individual Posts?
- ✅ **Higher reach**: Each post appears in main feeds, not buried in replies
- ✅ **Hashtag visibility**: Games show up in both teams' hashtag searches
- ✅ **Algorithm boost**: Each post gets independent algorithmic distribution
- ✅ **Better engagement**: Fans of each team can find and interact with their game
- ✅ **Growth potential**: Appear in 2 team communities per post

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
- Twitter Free tier: 1,500 tweets/month (~50 tweets/day)
- With 12-16 games/day, you'll use ~360-480 tweets/month
- If you hit rate limits, wait 15 minutes or upgrade your API plan

### Timeline Management
- Individual posts will appear on your timeline (not replies)
- On big game days (12+ games), this will be 12+ consecutive posts
- Followers will see all posts in their feeds
- This is normal and accepted in Hockey Twitter culture

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

