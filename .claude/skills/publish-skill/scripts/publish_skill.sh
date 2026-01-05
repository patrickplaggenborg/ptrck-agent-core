#!/bin/bash
set -e

# Configuration
REPO_URL="https://github.com/patrickplaggenborg/ptrck-agent-core.git"
USER_SKILLS_DIR="$HOME/.claude/skills"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check arguments
if [ -z "$1" ]; then
    echo -e "${RED}Error: No skill name provided${NC}"
    echo "Usage: $0 <skill-name>"
    exit 1
fi

SKILL_NAME="$1"
SKILL_SOURCE=".claude/skills/$SKILL_NAME"

# Validate skill exists
if [ ! -d "$SKILL_SOURCE" ]; then
    echo -e "${RED}Error: Skill not found at $SKILL_SOURCE${NC}"
    exit 1
fi

if [ ! -f "$SKILL_SOURCE/SKILL.md" ]; then
    echo -e "${RED}Error: SKILL.md not found in $SKILL_SOURCE${NC}"
    exit 1
fi

echo -e "${YELLOW}Publishing skill: $SKILL_NAME${NC}"

# Create temp directory
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

echo "Cloning ptrck-agent-core (shallow)..."
git clone --depth 1 "$REPO_URL" "$TEMP_DIR/repo" 2>/dev/null

# Ensure target directory exists
mkdir -p "$TEMP_DIR/repo/.claude/skills"

# Sync to git repo using rsync --delete
echo "Syncing skill to git repo..."
rsync -av --delete "$SKILL_SOURCE/" "$TEMP_DIR/repo/.claude/skills/$SKILL_NAME/"

# Commit and push
cd "$TEMP_DIR/repo"
git add .claude/skills/"$SKILL_NAME"

if git diff --cached --quiet; then
    echo -e "${YELLOW}No changes to commit to git repo${NC}"
    GIT_SUCCESS=true
else
    git commit -m "Add $SKILL_NAME skill"
    if git push; then
        echo -e "${GREEN}Successfully pushed to ptrck-agent-core${NC}"
        GIT_SUCCESS=true
    else
        echo -e "${RED}Failed to push to ptrck-agent-core${NC}"
        GIT_SUCCESS=false
    fi
fi

cd - > /dev/null

# Sync to user folder
echo "Syncing skill to user folder..."
mkdir -p "$USER_SKILLS_DIR"
rsync -av --delete "$SKILL_SOURCE/" "$USER_SKILLS_DIR/$SKILL_NAME/"

if [ -d "$USER_SKILLS_DIR/$SKILL_NAME" ]; then
    echo -e "${GREEN}Successfully synced to $USER_SKILLS_DIR/$SKILL_NAME${NC}"
    USER_SUCCESS=true
else
    echo -e "${RED}Failed to sync to user folder${NC}"
    USER_SUCCESS=false
fi

# Remove skill from current workspace
if [ "$GIT_SUCCESS" = true ] && [ "$USER_SUCCESS" = true ]; then
    echo "Removing skill from current workspace..."
    rm -rf "$SKILL_SOURCE"
    echo -e "${GREEN}Removed $SKILL_SOURCE${NC}"
    CLEANUP_SUCCESS=true
else
    echo -e "${YELLOW}Skipping cleanup due to previous failures${NC}"
    CLEANUP_SUCCESS=false
fi

# Summary
echo ""
echo "=== Summary ==="
if [ "$GIT_SUCCESS" = true ]; then
    echo -e "${GREEN}Git repo: Success${NC}"
else
    echo -e "${RED}Git repo: Failed${NC}"
fi

if [ "$USER_SUCCESS" = true ]; then
    echo -e "${GREEN}User folder: Success${NC}"
else
    echo -e "${RED}User folder: Failed${NC}"
fi

if [ "$CLEANUP_SUCCESS" = true ]; then
    echo -e "${GREEN}Workspace cleanup: Success${NC}"
else
    echo -e "${YELLOW}Workspace cleanup: Skipped${NC}"
fi

if [ "$GIT_SUCCESS" = true ] && [ "$USER_SUCCESS" = true ]; then
    echo -e "\n${GREEN}Skill '$SKILL_NAME' published successfully!${NC}"
    exit 0
else
    exit 1
fi
