# X Post Monitor Setup Guide

This guide will help you set up Discord notifications for your NHL report posts on X (Twitter).

## 🔧 Setup Steps

### 1. Get Twitter API Access

1. **Go to [developer.twitter.com](https://developer.twitter.com)**
2. **Apply for a developer account** (free)
3. **Create a new app** in the developer portal
4. **Get your Bearer Token** from the app settings

### 2. Add GitHub Secrets

Go to your GitHub repository → **Settings** → **Secrets and variables** → **Actions**

Add these secrets:

- **`DISCORD_WEBHOOK_URL`** - Your Discord webhook URL (already set)
- **`TWITTER_BEARER_TOKEN`** - Your Twitter API Bearer Token

### 3. Test the Setup

1. **Run the workflow manually** from the Actions tab
2. **Check Discord** for notifications
3. **Post a test NHL report** on X to verify it works

## 🎯 What It Does

### **Monitors Your X Posts:**
- ✅ Checks every 5 minutes for new posts
- ✅ Filters for NHL-related content
- ✅ Extracts game information (e.g., "FLA @ BUF")
- ✅ Tracks daily post count

### **Sends Discord Notifications:**
```
🏒 New NHL Report Posted! 🏒

FLA @ BUF

🏒 FLA @ BUF Post-Game Report 📊

Final: BUF 3-0 FLA

Key Stats:
• BUF: 60 shots, 3 goals
• FLA: 78 shots, 0 goals

Full analysis in the report! #NHL #PostGame

📊 Today's Progress: 3 report(s) posted today
🔗 View Post: [Click here](https://x.com/emilyfehr99/status/1234567890)

Posted by @emilyfehr99 • 2025-10-18 15:30 CT
```

## 🔍 How It Works

1. **Every 5 minutes**, the workflow runs
2. **Checks your X timeline** for new posts
3. **Filters for NHL content** using keywords
4. **Extracts game info** from post text
5. **Sends Discord notification** with game details
6. **Tracks daily progress** (e.g., "3/4 games posted today")

## 🎮 Keywords It Looks For

The monitor detects posts containing:
- `nhl`, `hockey`, `post-game`, `report`
- `game`, `final`, `shots`, `goals`
- `assists`, `save`, `period`, `overtime`

## 🚀 Features

- **Real-time monitoring** (5-minute intervals)
- **Game extraction** (e.g., "FLA @ BUF")
- **Daily progress tracking**
- **Beautiful Discord embeds**
- **Direct links to your posts**
- **Automatic filtering** (only NHL content)

## 🔧 Customization

You can modify:
- **Check frequency** (change cron schedule)
- **Keywords** (edit `filter_nhl_tweets` function)
- **Discord message format** (edit `send_discord_notification`)
- **Game extraction patterns** (edit `extract_game_info`)

## 📱 Example Notifications

When you post: "🏒 FLA @ BUF Post-Game Report 📊 Final: BUF 3-0 FLA..."

You'll get a Discord notification showing:
- Game: FLA @ BUF
- Today's count: 3/4 games posted
- Direct link to your post
- Full post content preview

## 🎯 Perfect for:
- **Tracking your daily NHL reports**
- **Getting instant notifications**
- **Monitoring your posting progress**
- **Sharing with your Discord community**
