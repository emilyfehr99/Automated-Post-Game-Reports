#!/bin/bash

###############################################################################
# Automated NHL Post-Game Report Generation and Twitter Posting
# 
# This script automates the complete workflow:
# 1. Generate reports for completed games
# 2. Automatically post to Twitter with proper threading
#
# Usage:
#   ./automated_workflow.sh 2025-10-11
#   or
#   ./automated_workflow.sh  (uses today's date)
###############################################################################

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get date parameter or use today
if [ -z "$1" ]; then
    TARGET_DATE=$(date +%Y-%m-%d)
else
    TARGET_DATE=$1
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}🏒 NHL Post-Game Report Automation${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "📅 Target Date: ${GREEN}${TARGET_DATE}${NC}"
echo ""

# Step 1: Generate reports
echo -e "${YELLOW}Step 1: Generating reports...${NC}"
TARGET_DATE=$TARGET_DATE python3 batch_report_generator.py

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Report generation failed!${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ Reports generated successfully!${NC}"
echo ""

# Step 2: Post to Twitter
echo -e "${YELLOW}Step 2: Posting to Twitter...${NC}"
python3 twitter_poster.py --date $TARGET_DATE

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Twitter posting failed!${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}🎉 Automation Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "Reports generated and posted to Twitter for ${TARGET_DATE}"
echo ""

