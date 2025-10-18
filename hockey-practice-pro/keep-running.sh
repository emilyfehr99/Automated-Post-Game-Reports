#!/bin/bash

# Hockey Practice Planner - Keep Running Script
# This script ensures the app stays running even after terminal closes

echo "🏒 Hockey Practice Planner - Keep Running"
echo "=========================================="

# Function to start the app
start_app() {
    echo "🚀 Starting Hockey Practice Planner..."
    cd /Users/emilyfehr8/CascadeProjects/hockey-practice-planner
    nohup npm run dev > hockey-app.log 2>&1 &
    echo $! > hockey-app.pid
    echo "✅ App started with PID: $(cat hockey-app.pid)"
    echo "🌐 Access at: http://localhost:3000"
    echo "📝 Logs: tail -f hockey-app.log"
}

# Function to stop the app
stop_app() {
    if [ -f hockey-app.pid ]; then
        PID=$(cat hockey-app.pid)
        echo "🛑 Stopping app (PID: $PID)..."
        kill $PID 2>/dev/null
        rm hockey-app.pid
        echo "✅ App stopped"
    else
        echo "❌ No PID file found"
    fi
}

# Function to check status
check_status() {
    if [ -f hockey-app.pid ]; then
        PID=$(cat hockey-app.pid)
        if ps -p $PID > /dev/null 2>&1; then
            echo "✅ App is running (PID: $PID)"
            echo "🌐 Access at: http://localhost:3000"
        else
            echo "❌ App is not running (stale PID file)"
            rm hockey-app.pid
        fi
    else
        echo "❌ App is not running"
    fi
}

# Main script logic
case "$1" in
    start)
        start_app
        ;;
    stop)
        stop_app
        ;;
    restart)
        stop_app
        sleep 2
        start_app
        ;;
    status)
        check_status
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the app in background"
        echo "  stop    - Stop the running app"
        echo "  restart - Restart the app"
        echo "  status  - Check if app is running"
        exit 1
        ;;
esac
