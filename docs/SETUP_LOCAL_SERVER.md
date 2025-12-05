# 🏠 Running Dashboard on Local Mac (Always On)

## Option A: Manual Start (Current)
Just run:
```bash
cd /Users/emilyfehr8/CascadeProjects
python3 prediction_dashboard.py
```

Keep terminal open and Mac awake.

---

## Option B: Background Process with LaunchAgent (Auto-start on boot)

This will start the dashboard automatically when your Mac boots.

### Steps:

1. **Create the LaunchAgent plist file:**

```bash
cat > ~/Library/LaunchAgents/com.nhl.dashboard.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.nhl.dashboard</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/emilyfehr8/CascadeProjects/prediction_dashboard.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/Users/emilyfehr8/CascadeProjects/dashboard.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/emilyfehr8/CascadeProjects/dashboard.error.log</string>
    <key>WorkingDirectory</key>
    <string>/Users/emilyfehr8/CascadeProjects</string>
</dict>
</plist>
EOF
```

2. **Load the service:**
```bash
launchctl load ~/Library/LaunchAgents/com.nhl.dashboard.plist
```

3. **Start it immediately:**
```bash
launchctl start com.nhl.dashboard
```

4. **Check if it's running:**
```bash
launchctl list | grep nhl
```

5. **To stop:**
```bash
launchctl unload ~/Library/LaunchAgents/com.nhl.dashboard.plist
```

**Access:** http://localhost:8080 (only accessible from your Mac)

---

## Option C: Prevent Mac from Sleeping

**System Settings → Battery → Options:**
- Turn off "Put hard disks to sleep when possible"
- Set "Prevent automatic sleeping when display is off" to ON (if available)

**Or use caffeinate:**
```bash
caffeinate -d
```
(Keeps display awake - keeps Mac from sleeping)

---

## ⚠️ Limitations of Localhost:

- ❌ Only accessible from your Mac (not from phone/other devices)
- ❌ Requires Mac to stay on 24/7
- ❌ Uses electricity
- ❌ If Mac restarts, need to restart server
- ✅ Free
- ✅ Full control
- ✅ No sleep delays

---

## 💡 Recommendation:

**Best solution for "always available everywhere":**
- Use **Render paid tier ($7/month)** OR
- Use **Railway** (usually free with $5 credit/month)

Both give you:
- ✅ Accessible from anywhere (phone, laptop, etc.)
- ✅ Always on (no sleep delays)
- ✅ Automatic HTTPS
- ✅ Automatic restarts
- ✅ Professional hosting

**Best for "free and local only":**
- Use LaunchAgent (Option B above)
- Keep Mac plugged in
- Disable sleep

---

## Quick Comparison:

| Solution | Cost | Always On | Access Anywhere | Setup |
|----------|------|-----------|-----------------|-------|
| Render Free | Free | ❌ (sleeps) | ✅ | Easy |
| Render Paid | $7/mo | ✅ | ✅ | Easy |
| Local Mac | Free | ⚠️ (if awake) | ❌ | Medium |
| Railway | $5 credit/mo | ✅ | ✅ | Easy |






