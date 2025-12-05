# 🚀 GitHub Actions Setup Guide

## Overview
Set up automatic NHL report posting that runs 24/7 in the cloud, completely free!

## What This Does

- ✅ Runs in GitHub's cloud (not on your laptop)
- ✅ Checks every 15 minutes for completed games
- ✅ Generates reports automatically
- ✅ Posts to Twitter automatically
- ✅ Completely free forever
- ✅ No laptop needed - close everything!

## Setup Steps (5 minutes)

### Step 1: Add Twitter API Credentials to GitHub

1. Go to your repository: https://github.com/emilyfehr99/Automated-Post-Game-Reports

2. Click **Settings** (top right of repo)

3. In left sidebar, click **Secrets and variables** → **Actions**

4. Click **New repository secret** button

5. Add these 4 secrets one at a time:

   **Secret 1:**
   - Name: `TWITTER_API_KEY`
   - Value: `rY7LNd3dr7Z9JJqKpdJiTWCHA`
   - Click "Add secret"

   **Secret 2:**
   - Name: `TWITTER_API_SECRET`
   - Value: `4kxhQTEBkJTfHUHFgIYMxQB11HQw8LdASJSlvIh32Y0Ats2nvE`
   - Click "Add secret"

   **Secret 3:**
   - Name: `TWITTER_ACCESS_TOKEN`
   - Value: `1011358647228686336-qxTAVsHIppqf5FZ8kwxMIKflc6cn4a`
   - Click "Add secret"

   **Secret 4:**
   - Name: `TWITTER_ACCESS_TOKEN_SECRET`
   - Value: `W8Uqz90Amk5NOysIsuXedqMbvQV3q6Db8RL8NhQZMqlw4`
   - Click "Add secret"

### Step 2: Push the GitHub Actions Workflow

The workflow file is already created. Just push it to GitHub:

```bash
cd /Users/emilyfehr8/CascadeProjects/nhl_postgame_reports
git add .github/workflows/auto_post_reports.yml github_actions_runner.py GITHUB_ACTIONS_SETUP.md
git commit -m "Add GitHub Actions for automatic posting"
git push origin main
```

### Step 3: Enable GitHub Actions (if needed)

1. Go to your repository
2. Click **Actions** tab
3. If prompted, click **"I understand my workflows, go ahead and enable them"**

### Step 4: That's It! ✅

The automation is now live! It will:
- Check every 15 minutes (starting at the next 15-minute mark)
- Find completed games
- Generate reports
- Post to Twitter
- All without your laptop on!

## How to Verify It's Working

### Check Workflow Runs:
1. Go to your repo: https://github.com/emilyfehr99/Automated-Post-Game-Reports
2. Click **Actions** tab
3. You'll see runs every 15 minutes
4. Click on any run to see logs

### Manual Trigger (Test Now):
1. Go to **Actions** tab
2. Click **Auto Post NHL Reports** on the left
3. Click **Run workflow** button (top right)
4. Click green **Run workflow** button
5. Watch it run in real-time!

## Schedule Details

The workflow runs:
- **Every 15 minutes** from 12:00 PM to 3:00 AM ET (Eastern Time)
- This covers all typical NHL game times
- Completely automatic, no action needed from you

Example schedule:
```
12:00 PM - Check
12:15 PM - Check
12:30 PM - Check
... (continues all day)
2:45 AM - Check
3:00 AM - Check
```

## What Happens Each Run

```
1. GitHub Actions starts the workflow
2. Checks NHL API for today's games
3. Finds games with FINAL/OFF status
4. Filters out already-posted games
5. For each new completed game:
   - Generates PDF report
   - Converts to PNG
   - Uploads to Twitter
   - Posts with team hashtags
6. Saves list of posted games
7. Waits 15 minutes, repeat
```

## Cost

**$0 - Completely Free!**

GitHub provides:
- 2,000 minutes/month free (more than enough)
- Each run takes ~2-3 minutes
- Running every 15 minutes = 96 runs/day
- 96 runs × 3 minutes = 288 minutes/day
- Even on full game days, well within free tier

## Benefits Over Local Monitoring

| Feature | Local (Laptop) | GitHub Actions |
|---------|----------------|----------------|
| **Laptop needed** | ✅ Yes, always on | ❌ No |
| **Cost** | Electricity | Free |
| **Reliability** | Can crash/sleep | Very reliable |
| **Check frequency** | 60 seconds | 15 minutes |
| **Setup** | Run manually | Set & forget |

## Monitoring & Logs

### View Logs:
1. Go to **Actions** tab in your repo
2. Click any workflow run
3. Click **check-and-post** job
4. See full output logs

### What You'll See in Logs:
```
🤖 NHL REPORT AUTOMATION - GITHUB ACTIONS
==========================================
📅 Date: 2025-10-11 10:15:32 PM
📋 Previously processed: 8 games
==========================================

🔍 Found 12 games today
   LAK @ WPG: OFF
   STL @ CGY: OFF
   ...
   DAL @ COL: FINAL
      ✅ NEW COMPLETED GAME!

🚀 Processing 1 new game(s)...

==========================================
🏒 PROCESSING: DAL @ COL
==========================================

📊 Generating report for DAL @ COL...
✅ Report generated

🐦 Posting DAL @ COL to Twitter...
✅ Posted to Twitter: #TexasHockey vs #GoAvsGo
   🔗 https://twitter.com/user/status/1234567890

✅ COMPLETED: DAL @ COL

==========================================
🎉 Run Complete!
✅ Successfully posted: 1/1
📊 Total processed games: 9
==========================================
```

## Troubleshooting

### "Workflow not running"
- Check that GitHub Actions is enabled in repo settings
- Verify the workflow file is in `.github/workflows/` folder
- Check that secrets are added correctly

### "Authentication failed"
- Verify all 4 Twitter secrets are added
- Check that secret names match exactly (case-sensitive)
- Try regenerating Twitter API credentials

### "No games found"
- This is normal when no games are scheduled
- Workflow still runs successfully
- Will auto-detect when games start

### "Report generation failed"
- Check workflow logs for specific error
- May be a temporary NHL API issue
- Will retry on next 15-minute check

## Customization

### Change Check Frequency:
Edit `.github/workflows/auto_post_reports.yml`:

```yaml
# Check every 10 minutes instead of 15
- cron: '*/10 12-23 * * *'

# Check every 30 minutes
- cron: '*/30 12-23 * * *'
```

### Change Time Window:
```yaml
# Only run during evening games (5 PM - 1 AM)
- cron: '*/15 17-23 * * *'
- cron: '*/15 0-1 * * *'
```

## Stopping/Pausing

### Temporarily Disable:
1. Go to repo → **Actions** tab
2. Click **Auto Post NHL Reports**
3. Click **⋯** menu (top right)
4. Click **Disable workflow**

### Re-enable:
Same steps, click **Enable workflow**

### Permanently Remove:
```bash
# Delete the workflow file
rm .github/workflows/auto_post_reports.yml
git commit -m "Remove auto posting"
git push
```

## Comparison

### Before (Manual):
```bash
# Every time a game ends, you had to:
TARGET_DATE=2025-10-11 python3 batch_report_generator.py
python3 twitter_poster.py --date 2025-10-11

# Required laptop on, manual monitoring
```

### After (GitHub Actions):
```bash
# One-time setup, then:
# (nothing - it's all automatic!)

# Games post themselves every 15 minutes
# Laptop can be off, closed, anywhere
# Completely hands-off
```

## Support

If you have issues:
1. Check **Actions** tab logs
2. Verify secrets are set correctly
3. Manually trigger workflow to test
4. Check Twitter API rate limits

---

**🎉 You're all set for fully automatic posting without your laptop!**

The system will run 24/7 in GitHub's cloud, catch every completed game, and post to Twitter automatically. You literally never need to think about it again! 🚀🏒

