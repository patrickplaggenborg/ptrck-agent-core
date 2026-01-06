#!/bin/bash
set -e

# Configuration
REPO_URL="https://github.com/patrickplaggenborg/ptrck-agent-core.git"
USER_DIR="$HOME/.claude"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Help message
show_help() {
    echo "Usage: $0 [type] <name>"
    echo ""
    echo "Publish skills, commands, or hooks to ptrck-agent-core and user folder."
    echo ""
    echo "Arguments:"
    echo "  type    Optional. One of: skill, command, hook"
    echo "  name    Name of the item to publish (without .md extension for commands/hooks)"
    echo ""
    echo "Examples:"
    echo "  $0 my-skill              # Auto-detect type"
    echo "  $0 skill my-skill        # Explicit skill"
    echo "  $0 command pull          # Explicit command"
    echo "  $0 hook user-prompt      # Explicit hook"
}

# Parse arguments
if [ -z "$1" ]; then
    show_help
    exit 1
fi

if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    show_help
    exit 0
fi

# Determine if first arg is type or name
TYPE=""
NAME=""

if [ "$1" = "skill" ] || [ "$1" = "command" ] || [ "$1" = "hook" ]; then
    TYPE="$1"
    NAME="$2"
    if [ -z "$NAME" ]; then
        echo -e "${RED}Error: No name provided${NC}"
        show_help
        exit 1
    fi
else
    NAME="$1"
fi

# Auto-detect type if not specified
if [ -z "$TYPE" ]; then
    if [ -d ".claude/skills/$NAME" ]; then
        TYPE="skill"
    elif [ -f ".claude/commands/$NAME.md" ]; then
        TYPE="command"
    elif [ -f ".claude/hooks/$NAME.md" ]; then
        TYPE="hook"
    else
        echo -e "${RED}Error: Could not find '$NAME' in skills, commands, or hooks${NC}"
        echo "Searched:"
        echo "  .claude/skills/$NAME/"
        echo "  .claude/commands/$NAME.md"
        echo "  .claude/hooks/$NAME.md"
        exit 1
    fi
    echo -e "${YELLOW}Auto-detected type: $TYPE${NC}"
fi

# Set source and destination paths based on type
case "$TYPE" in
    skill)
        SOURCE=".claude/skills/$NAME"
        DEST_SUBDIR="skills/$NAME"
        IS_DIR=true
        REQUIRED_FILE="$SOURCE/SKILL.md"
        ;;
    command)
        SOURCE=".claude/commands/$NAME.md"
        DEST_SUBDIR="commands"
        IS_DIR=false
        REQUIRED_FILE="$SOURCE"
        ;;
    hook)
        SOURCE=".claude/hooks/$NAME.md"
        DEST_SUBDIR="hooks"
        IS_DIR=false
        REQUIRED_FILE="$SOURCE"
        ;;
    *)
        echo -e "${RED}Error: Unknown type '$TYPE'${NC}"
        exit 1
        ;;
esac

# Validate source exists
if [ "$IS_DIR" = true ]; then
    if [ ! -d "$SOURCE" ]; then
        echo -e "${RED}Error: Directory not found at $SOURCE${NC}"
        exit 1
    fi
    if [ ! -f "$REQUIRED_FILE" ]; then
        echo -e "${RED}Error: SKILL.md not found in $SOURCE${NC}"
        exit 1
    fi
else
    if [ ! -f "$SOURCE" ]; then
        echo -e "${RED}Error: File not found at $SOURCE${NC}"
        exit 1
    fi
fi

echo -e "${YELLOW}Publishing $TYPE: $NAME${NC}"

# Create temp directory
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

echo "Cloning ptrck-agent-core (shallow)..."
git clone --depth 1 "$REPO_URL" "$TEMP_DIR/repo" 2>/dev/null

# Sync to git repo
if [ "$IS_DIR" = true ]; then
    # For skills (directories)
    mkdir -p "$TEMP_DIR/repo/.claude/skills"
    echo "Syncing skill directory to git repo..."
    rsync -av --delete "$SOURCE/" "$TEMP_DIR/repo/.claude/$DEST_SUBDIR/"
else
    # For commands/hooks (single files)
    mkdir -p "$TEMP_DIR/repo/.claude/$DEST_SUBDIR"
    echo "Syncing file to git repo..."
    cp "$SOURCE" "$TEMP_DIR/repo/.claude/$DEST_SUBDIR/"
fi

# Commit and push
cd "$TEMP_DIR/repo"
git add ".claude/$DEST_SUBDIR"

if git diff --cached --quiet; then
    echo -e "${YELLOW}No changes to commit to git repo${NC}"
    GIT_SUCCESS=true
else
    git commit -m "Add $NAME $TYPE"
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
echo "Syncing to user folder..."
if [ "$IS_DIR" = true ]; then
    mkdir -p "$USER_DIR/skills"
    rsync -av --delete "$SOURCE/" "$USER_DIR/$DEST_SUBDIR/"
    if [ -d "$USER_DIR/$DEST_SUBDIR" ]; then
        echo -e "${GREEN}Successfully synced to $USER_DIR/$DEST_SUBDIR${NC}"
        USER_SUCCESS=true
    else
        echo -e "${RED}Failed to sync to user folder${NC}"
        USER_SUCCESS=false
    fi
else
    mkdir -p "$USER_DIR/$DEST_SUBDIR"
    cp "$SOURCE" "$USER_DIR/$DEST_SUBDIR/"
    if [ -f "$USER_DIR/$DEST_SUBDIR/$NAME.md" ]; then
        echo -e "${GREEN}Successfully synced to $USER_DIR/$DEST_SUBDIR/$NAME.md${NC}"
        USER_SUCCESS=true
    else
        echo -e "${RED}Failed to sync to user folder${NC}"
        USER_SUCCESS=false
    fi
fi

# Remove source from current workspace
if [ "$GIT_SUCCESS" = true ] && [ "$USER_SUCCESS" = true ]; then
    echo "Removing from current workspace..."
    rm -rf "$SOURCE"
    echo -e "${GREEN}Removed $SOURCE${NC}"
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
    echo -e "\n${GREEN}$TYPE '$NAME' published successfully!${NC}"
    exit 0
else
    exit 1
fi
