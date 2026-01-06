#!/bin/bash

# Setup git hooks for this repository

REPO_ROOT="$(git rev-parse --show-toplevel)"
SKILL_DIR="$REPO_ROOT/.claude/skills/repo-deployment"

# Get the actual git directory (handles both regular repos and worktrees)
GIT_DIR="$(git rev-parse --git-dir)"

echo "Setting up git hooks..."

# Create hooks directory if it doesn't exist
mkdir -p "$GIT_DIR/hooks"

# Copy hooks from skill directory to git hooks directory
cp "$SKILL_DIR/hooks/post-commit" "$GIT_DIR/hooks/post-commit"
chmod +x "$GIT_DIR/hooks/post-commit"

echo "Git hooks installed successfully!"
echo ""
echo "The post-commit hook will now automatically deploy .claude/ changes to ~/.claude/"
