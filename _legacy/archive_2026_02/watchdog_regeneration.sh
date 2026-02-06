#!/bin/bash
# Watchdog script to keep generate_real_team_stats.py running

LOG_FILE="regeneration.log"
SCRIPT="generate_real_team_stats.py"
CHECK_INTERVAL=30  # Check every 30 seconds

echo "=== Watchdog started at $(date) ===" >> "$LOG_FILE"
echo "Will monitor and restart $SCRIPT if it crashes" >> "$LOG_FILE"

while true; do
    # Check if the process is running
    if ! pgrep -f "python3 $SCRIPT" > /dev/null; then
        echo "" >> "$LOG_FILE"
        echo "[$( date '+%Y-%m-%d %H:%M:%S' )] Process died. Restarting..." >> "$LOG_FILE"
        echo "" >> "$LOG_FILE"
        
        # Restart the process
        nohup python3 "$SCRIPT" >> "$LOG_FILE" 2>&1 &
        
        echo "[$( date '+%Y-%m-%d %H:%M:%S' )] Restarted with PID $!" >> "$LOG_FILE"
    fi
    
    # Wait before checking again
    sleep $CHECK_INTERVAL
done
