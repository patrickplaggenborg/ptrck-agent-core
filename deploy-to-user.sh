#!/bin/bash

# Deploy .claude configuration to user directory
# This syncs skills, commands, and hooks from this repo to ~/.claude/

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="$SCRIPT_DIR/.claude"
TARGET_DIR="$HOME/.claude"

echo "🚀 Deploying .claude configuration to user directory..."

# Sync skills, commands, and hooks
rsync -av --delete "$SOURCE_DIR/skills/" "$TARGET_DIR/skills/"
rsync -av --delete "$SOURCE_DIR/commands/" "$TARGET_DIR/commands/"
rsync -av --delete "$SOURCE_DIR/hooks/" "$TARGET_DIR/hooks/"

echo "✅ Deployment complete!"
echo ""
echo "Deployed:"
echo "  - skills"
echo "  - commands"
echo "  - hooks"
