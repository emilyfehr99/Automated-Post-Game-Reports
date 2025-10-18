# Hockey Practice Planner - Production Setup

## 🚀 Quick Start (24/7 Running)

### First Time Setup
```bash
# 1. Create backup of current state
./backup.sh

# 2. Setup for production (installs PM2, builds app, starts 24/7)
./setup-production.sh
```

### Daily Use
```bash
# Start the app (if stopped)
./start.sh

# Check if running
pm2 status

# View logs
pm2 logs
```

## 📋 Features

### ✅ Current Working Features
- **Simple Drill Creator** - Upload images or paste from clipboard (Ctrl+V)
- **Drill Library** - Browse, search, and filter drills
- **Practice Plan Builder** - Create structured practice sessions
- **Image Management** - Upload multiple images per drill
- **Text Organization** - Setup steps, variations, coaching points
- **Professional UI** - IHS-style interface with hockey theme

### 🎯 How to Use

#### Creating Drills
1. Click "Create Drill" from anywhere in the app
2. **Upload Images**: 
   - Click upload area to select files, OR
   - Copy image to clipboard and press Ctrl+V
3. Fill in drill details (name, category, duration, description)
4. Add setup steps, variations, and coaching points
5. Click "Create Drill Plan"

#### Managing Drills
- **Drill Library**: Browse all your drills with images
- **Search**: Find drills by name or description
- **Filter**: Filter by category (Skills, Systems, etc.)
- **Add to Practice**: Click + button to add drills to practice plans

## 🔧 Production Commands

### PM2 Management
```bash
pm2 status                    # Check app status
pm2 logs                      # View real-time logs
pm2 logs --lines 100          # View last 100 log lines
pm2 restart hockey-practice-planner  # Restart app
pm2 stop hockey-practice-planner     # Stop app
pm2 delete hockey-practice-planner   # Remove app completely
pm2 save                      # Save current PM2 configuration
```

### Backup & Restore
```bash
./backup.sh                   # Create timestamped backup
pm2 save                      # Save PM2 configuration
```

### Development
```bash
npm run dev                   # Development mode
npm run build                 # Build for production
npm start                     # Start production build
```

## 📁 File Structure

```
hockey-practice-planner/
├── app/                      # Next.js app directory
├── components/               # React components
├── utils/                    # Utility functions
├── sample-drills/           # Sample drill data
├── logs/                    # PM2 log files
├── ecosystem.config.js      # PM2 configuration
├── setup-production.sh      # Production setup script
├── start.sh                 # Quick start script
├── backup.sh                # Backup script
└── PRODUCTION_README.md     # This file
```

## 🌐 Access

- **Local**: http://localhost:3000
- **Network**: http://[your-ip]:3000 (accessible from other devices)

## 🔒 Data Storage

- **Drills**: Stored in browser localStorage (persists between sessions)
- **Images**: Base64 encoded and stored with drill data
- **Practice Plans**: Stored in browser localStorage

## 🛠️ Troubleshooting

### App Won't Start
```bash
pm2 logs                      # Check for errors
pm2 restart hockey-practice-planner
```

### Images Not Uploading
- Check browser console for errors
- Ensure images are valid formats (PNG, JPG, GIF)
- Try clipboard paste (Ctrl+V) instead of file upload

### Performance Issues
```bash
pm2 restart hockey-practice-planner  # Restart app
pm2 logs --lines 50           # Check recent logs
```

## 📊 Monitoring

### Check App Health
```bash
pm2 status                    # Should show "online"
pm2 logs --lines 20          # Check recent activity
```

### View Resource Usage
```bash
pm2 monit                     # Real-time monitoring
```

## 🔄 Updates

### Update Application
1. Stop the app: `pm2 stop hockey-practice-planner`
2. Pull latest changes
3. Run: `npm run build`
4. Start: `pm2 start hockey-practice-planner`

### Rollback
1. Restore from backup: `./backup.sh` (if you have a backup)
2. Or restore from specific backup directory

## 📱 Mobile Access

The app is responsive and works on mobile devices. Access it from any device on your network using your computer's IP address.

## 🎯 Tips

1. **Clipboard Paste**: Copy images from anywhere and paste with Ctrl+V
2. **Multiple Images**: Upload several images per drill for different angles
3. **Categories**: Use consistent categories for better organization
4. **Descriptions**: Add detailed descriptions for better search results
5. **Backup Regularly**: Run `./backup.sh` before major changes

## 🆘 Support

If you encounter issues:
1. Check PM2 status: `pm2 status`
2. View logs: `pm2 logs`
3. Restart app: `pm2 restart hockey-practice-planner`
4. Check this README for troubleshooting steps

---

**Your Hockey Practice Planner is now running 24/7 and ready for professional use!** 🏒
