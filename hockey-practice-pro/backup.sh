#!/bin/bash

echo "💾 Creating backup of Hockey Practice Planner..."

# Create backup directory with timestamp
BACKUP_DIR="/Users/emilyfehr8/CascadeProjects/hockey-practice-planner-backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Copy all files except node_modules and .next
rsync -av --exclude 'node_modules' --exclude '.next' --exclude 'logs' \
  /Users/emilyfehr8/CascadeProjects/hockey-practice-planner/ \
  "$BACKUP_DIR/"

echo "✅ Backup created at: $BACKUP_DIR"
echo "📁 Backup includes:"
echo "  - All source code"
echo "  - Configuration files"
echo "  - Sample drills"
echo "  - Documentation"
echo ""
echo "🔄 To restore from backup:"
echo "  rsync -av $BACKUP_DIR/ /Users/emilyfehr8/CascadeProjects/hockey-practice-planner/"
