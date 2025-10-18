#!/bin/bash

# Goalie Analysis App - 24/7 Startup Script
# This script ensures the app runs continuously and restarts if it crashes

APP_NAME="Goalie Analysis App"
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$APP_DIR/app.log"
PID_FILE="$APP_DIR/app.pid"
PORT=8239

echo "🥅 Starting $APP_NAME on port $PORT..."
echo "   App directory: $APP_DIR"
echo "   Log file: $LOG_FILE"
echo "   PID file: $PID_FILE"

# Function to start the app
start_app() {
    echo "$(date): Starting $APP_NAME..." >> "$LOG_FILE"
    
    # Kill any existing process on the port
    lsof -ti:$PORT | xargs kill -9 2>/dev/null || true
    
    # Start the app in the background
    cd "$APP_DIR"
    python3 app.py >> "$LOG_FILE" 2>&1 &
    
    # Save the PID
    echo $! > "$PID_FILE"
    echo "$(date): $APP_NAME started with PID $(cat $PID_FILE)" >> "$LOG_FILE"
    echo "✅ $APP_NAME started successfully on port $PORT"
}

# Function to stop the app
stop_app() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        echo "🛑 Stopping $APP_NAME (PID: $PID)..."
        kill $PID 2>/dev/null || true
        rm -f "$PID_FILE"
        echo "$(date): $APP_NAME stopped" >> "$LOG_FILE"
    else
        echo "⚠️  No PID file found"
    fi
}

# Function to check if app is running
check_app() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            return 0
        else
            return 1
        fi
    else
        return 1
    fi
}

# Function to restart the app
restart_app() {
    echo "🔄 Restarting $APP_NAME..."
    stop_app
    sleep 2
    start_app
}

# Function to monitor and auto-restart
monitor_app() {
    echo "👀 Starting monitoring for $APP_NAME..."
    echo "$(date): Monitoring started" >> "$LOG_FILE"
    
    while true; do
        if ! check_app; then
            echo "$(date): App crashed, restarting..." >> "$LOG_FILE"
            echo "⚠️  App crashed, restarting..."
            start_app
        fi
        
        # Check every 30 seconds
        sleep 30
    done
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
        restart_app
        ;;
    status)
        if check_app; then
            echo "✅ $APP_NAME is running (PID: $(cat $PID_FILE))"
        else
            echo "❌ $APP_NAME is not running"
        fi
        ;;
    monitor)
        monitor_app
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|monitor}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the app"
        echo "  stop    - Stop the app"
        echo "  restart - Restart the app"
        echo "  status  - Check app status"
        echo "  monitor - Start monitoring (auto-restart on crash)"
        echo ""
        echo "For 24/7 operation, run:"
        echo "  $0 start"
        echo "  $0 monitor &"
        exit 1
        ;;
esac
