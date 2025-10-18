#!/bin/bash

echo "🏒 Hockey Practice Planner - Mobile Access 24/7"
echo "==============================================="

# Kill any existing Next.js processes
echo "🔄 Stopping any existing servers..."
pkill -f 'next dev' 2>/dev/null || true
sleep 2

# Get the local IP address
LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | head -1 | awk '{print $2}')
echo "📱 Your computer's IP address: $LOCAL_IP"

# Create a PID file
PID_FILE="hockey-mobile.pid"
LOG_FILE="hockey-mobile.log"

# Start the development server with network access in background
echo "🚀 Starting server with mobile access (running in background)..."
echo "📱 Mobile URL: http://$LOCAL_IP:3000"
echo "💻 Computer URL: http://localhost:3000"
echo "📝 Make sure your phone is on the same WiFi network!"
echo ""

# Start the server in background and save PID
nohup npm run dev -- --hostname 0.0.0.0 > $LOG_FILE 2>&1 &
SERVER_PID=$!

# Save PID to file
echo $SERVER_PID > $PID_FILE

echo "✅ Server started with PID: $SERVER_PID"
echo "📁 Log file: $LOG_FILE"
echo "📁 PID file: $PID_FILE"
echo ""
echo "🔄 Server will keep running even if you close this terminal!"
echo "🛑 To stop: ./stop-mobile.sh"
echo "📊 To check status: ./check-mobile-status.sh"
echo ""
echo "🌐 Your app is now accessible 24/7 at: http://$LOCAL_IP:3000"
