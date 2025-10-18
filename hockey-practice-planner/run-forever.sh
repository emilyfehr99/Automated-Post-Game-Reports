#!/bin/bash

echo "🏒 Starting Hockey Practice Planner to run 24/7..."

# Function to restart the app if it crashes
restart_app() {
    echo "🔄 Restarting app..."
    sleep 2
    npm start &
    APP_PID=$!
    echo "✅ App restarted with PID: $APP_PID"
}

# Start the app
npm start &
APP_PID=$!
echo "✅ App started with PID: $APP_PID"
echo "🌐 Open: http://localhost:3000"
echo "📊 Monitor with: ps aux | grep node"
echo ""

# Monitor the app
while true; do
    if ! kill -0 $APP_PID 2>/dev/null; then
        echo "❌ App crashed, restarting..."
        restart_app
    fi
    sleep 10
done
