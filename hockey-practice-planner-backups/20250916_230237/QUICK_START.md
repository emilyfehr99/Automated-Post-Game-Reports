# 🏒 Hockey Practice Planner - Quick Start Guide

## ✅ CURRENT STATUS: RUNNING & READY!

Your Hockey Practice Planner is currently **RUNNING** and accessible at:
**🌐 http://localhost:3000**

## 🚀 New Features Added

### 📋 Clipboard Paste for Images
- **Upload Images**: Click upload area to select files
- **Paste from Clipboard**: Copy any image and press **Ctrl+V** (or Cmd+V on Mac)
- **Multiple Images**: Upload or paste multiple images per drill

### 💾 Backup System
- **Automatic Backup**: Your current progress has been saved
- **Backup Location**: `/Users/emilyfehr8/CascadeProjects/hockey-practice-planner-backups/`
- **Run Backup**: `./backup.sh` to create new backup

## 🎯 How to Use

### Creating Drills
1. **Open App**: Go to http://localhost:3000
2. **Click "Create Drill"** from anywhere in the app
3. **Add Images**:
   - Click upload area to select files, OR
   - Copy image from anywhere and press Ctrl+V
4. **Fill Details**: Name, category, duration, description
5. **Add Instructions**: Setup steps, variations, coaching points
6. **Create Drill Plan**: Click the button to save

### Managing Your Drills
- **Drill Library**: View all your drills with images
- **Search**: Find drills by name or description
- **Filter**: Filter by category (Skills, Systems, etc.)
- **Practice Plans**: Add drills to practice sessions

## 🔧 Management Commands

### Check Status
```bash
./check-status.sh
```

### Start App (if stopped)
```bash
./start-production.sh
```

### Stop App
```bash
pkill -f 'next start'
```

### Create Backup
```bash
./backup.sh
```

### Start 24/7 (with auto-restart)
```bash
./run-forever.sh
```

## 📱 Access from Other Devices

Your app is accessible from other devices on your network:
1. Find your computer's IP address
2. Open: `http://[your-ip]:3000`
3. Use on phone, tablet, or other computers

## 🎨 Current Features

### ✅ Working Features
- **Simple Drill Creator** - Upload images or paste from clipboard
- **Drill Library** - Browse, search, and filter drills
- **Practice Plan Builder** - Create structured practice sessions
- **Image Management** - Multiple images per drill
- **Text Organization** - Setup, variations, coaching points
- **Professional UI** - IHS-style hockey theme
- **Responsive Design** - Works on all devices

### 🎯 Perfect for Your Workflow
- **Quick Image Import** - Just copy and paste images
- **No Drawing Required** - Focus on your drill images
- **Professional Output** - Creates IHS-style drill plans
- **Easy Organization** - Search and categorize drills

## 🆘 Troubleshooting

### App Not Loading
```bash
./check-status.sh
```
If not running:
```bash
./start-production.sh
```

### Images Not Uploading
- Try clipboard paste (Ctrl+V) instead of file upload
- Check browser console for errors
- Ensure images are valid formats (PNG, JPG, GIF)

### Need Help
- Check this guide first
- Look at PRODUCTION_README.md for detailed info
- Your data is automatically saved in browser storage

## 🎉 You're All Set!

Your Hockey Practice Planner is running 24/7 and ready for professional use. You can now:

1. **Create drills** by uploading images or pasting from clipboard
2. **Organize drills** in your library with search and filters
3. **Build practice plans** with your drills
4. **Access from anywhere** on your network

**Happy coaching!** 🏒
