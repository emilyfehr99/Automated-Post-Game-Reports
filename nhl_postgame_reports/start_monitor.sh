#!/bin/bash

###############################################################################
# Start the automatic NHL game monitor
# 
# This script starts the monitoring system that will:
# 1. Watch for games to finish in real-time
# 2. Generate reports automatically
# 3. Post to Twitter automatically
#
# Usage:
#   ./start_monitor.sh
#
# To stop: Press Ctrl+C
###############################################################################

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}🤖 Starting NHL Game Monitor${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${GREEN}✅ Monitor will check every 60 seconds${NC}"
echo -e "${GREEN}✅ Reports generated automatically${NC}"
echo -e "${GREEN}✅ Posted to Twitter automatically${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop monitoring${NC}"
echo ""

# Navigate to script directory
cd "$(dirname "$0")"

# Start the monitor
python3 game_monitor.py --interval 60

