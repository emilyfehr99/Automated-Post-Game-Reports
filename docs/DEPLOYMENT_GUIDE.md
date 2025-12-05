# 🚀 Deploying NHL Predictions Dashboard

## Option 1: Render (Recommended - Free & Fast)

Render offers a free tier with automatic deployments from GitHub.

### Steps:

1. **Push your code to GitHub** (if not already):
   ```bash
   git add .
   git commit -m "Add prediction dashboard"
   git push origin main
   ```

2. **Sign up for Render**:
   - Go to https://render.com
   - Sign up with your GitHub account (free)

3. **Create a new Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the repository with your dashboard

4. **Configure the service**:
   - **Name**: `nhl-predictions-dashboard` (or any name)
   - **Region**: Choose closest to you (US/EU)
   - **Branch**: `main`
   - **Root Directory**: Leave empty (or `/` if it's not the root)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python3 prediction_dashboard.py`
   - **Plan**: Free

5. **Environment Variables** (optional):
   - `FLASK_DEBUG`: `false` (for production)
   - `PORT`: Render sets this automatically, don't override

6. **Click "Create Web Service"**
h
7. **Wait for deployment** (~2-3 minutes for first build)

8. **Your dashboard will be live at**: `https://your-app-name.onrender.com`

### Notes:
- Free tier spins down after 15 minutes of inactivity
- First request after spin-down takes ~30 seconds to wake up
- Unlimited requests once awake
- Automatic HTTPS
- Can upgrade to paid ($7/month) for always-on

---

## Option 2: Railway (Free Tier)

Railway also offers free deployment with a $5 monthly credit.

### Steps:

1. **Push to GitHub** (same as above)

2. **Sign up**: https://railway.app (use GitHub)

3. **Create New Project**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

4. **Configure**:
   - Railway auto-detects Python
   - It will run `requirements.txt` automatically
   - Sets PORT automatically

5. **Add start command** (if needed):
   - Go to Settings → Deploy
   - Start Command: `python3 prediction_dashboard.py`

6. **Deploy**: Railway auto-deploys on git push

### Notes:
- $5/month free credit (usually enough for free tier usage)
- Faster cold starts than Render
- Auto-deploys on push

---

## Option 3: Fly.io (Free Tier)

Fly.io offers free tier with good performance.

### Steps:

1. **Install flyctl**:
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login**:
   ```bash
   flyctl auth login
   ```

3. **Create app** (in your project directory):
   ```bash
   flyctl launch
   ```
   - Answer prompts (choose a name, region, etc.)

4. **It will create a `fly.toml`** - that's fine, it will auto-detect Python

5. **Deploy**:
   ```bash
   flyctl deploy
   ```

### Notes:
- Fast cold starts
- Good free tier
- More setup required but very reliable

---

## Option 4: PythonAnywhere (Simple but Slower)

Good for learning, but free tier is slower.

### Steps:

1. Sign up at https://www.pythonanywhere.com (free account)

2. Go to Files tab and upload your code

3. Go to Web tab → Add a new web app

4. Choose Flask and Python 3.10

5. Set working directory and source code path

6. Update WSGI file to point to your app

7. Reload web app

### Notes:
- Free tier is slower
- Only allows 3 apps
- Good for testing/development

---

## Recommended: Render

**Render is recommended because:**
- ✅ Easiest setup
- ✅ Free tier
- ✅ Automatic HTTPS
- ✅ Auto-deploys from GitHub
- ✅ Good documentation
- ✅ Reliable

**Quick Render Checklist:**
- [ ] Code pushed to GitHub
- [ ] Signed up at render.com
- [ ] Created new Web Service
- [ ] Connected GitHub repo
- [ ] Set build command: `pip install -r requirements.txt`
- [ ] Set start command: `python3 prediction_dashboard.py`
- [ ] Deployed!

Your dashboard will be live in ~3 minutes! 🎉

---

## Troubleshooting

### Port Issues:
- Render/Railway set PORT automatically - don't hardcode it
- The code uses `os.environ.get('PORT', 8080)` - this works everywhere

### Template Not Found:
- Make sure `templates/` folder is in your repo
- Check that it's not in `.gitignore`

### Import Errors:
- Check `requirements.txt` has all dependencies
- Make sure all your Python files are committed

### Cold Starts:
- Free tier apps "sleep" after inactivity
- First request after sleep takes ~30 seconds
- Subsequent requests are fast until next sleep

---

## Custom Domain (Optional)

All platforms allow custom domains:
- **Render**: Settings → Custom Domain
- **Railway**: Settings → Generate Domain
- **Fly.io**: `flyctl domains add yourdomain.com`

HTTPS is automatic! 🔒

