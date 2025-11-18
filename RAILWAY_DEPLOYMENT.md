# Railway Deployment Guide

Railway is typically much faster than Render's free tier. Here's how to deploy:

## Quick Setup

1. **Sign up for Railway**
   - Go to https://railway.app
   - Sign up with GitHub (free tier includes $5 credit/month)

2. **Deploy from GitHub**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your `Automated-Post-Game-Reports` repository
   - Railway will auto-detect it's a Python app

3. **Configure Environment**
   - Railway will automatically:
     - Detect Python from `runtime.txt`
     - Install dependencies from `requirements.txt`
     - Run the app using the `Procfile`

4. **Set Port (if needed)**
   - Railway automatically sets the `PORT` environment variable
   - The app already uses `os.environ.get('PORT', 8080)` so it should work automatically

5. **Get Your URL**
   - Railway will provide a URL like `your-app.railway.app`
   - You can also add a custom domain if you want

## Why Railway is Faster

- Better free tier performance
- Faster cold starts
- More reliable uptime
- $5 free credit per month (usually enough for a small Flask app)

## Alternative: Fly.io (Also Fast)

If Railway doesn't work, Fly.io is another great option:

1. Install Fly CLI: `curl -L https://fly.io/install.sh | sh`
2. Run: `fly launch` in your project directory
3. Follow the prompts

Both Railway and Fly.io are typically much faster than Render's free tier!

