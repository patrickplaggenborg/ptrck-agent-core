#!/bin/bash

# Setup git hooks for this repository

REPO_ROOT="$(git rev-parse --show-toplevel)"

echo "Setting up git hooks..."

# Copy hooks from hooks/ directory to .git/hooks/
cp "$REPO_ROOT/hooks/post-commit" "$REPO_ROOT/.git/hooks/post-commit"
chmod +x "$REPO_ROOT/.git/hooks/post-commit"

echo "✅ Git hooks installed successfully!"
echo ""
echo "The post-commit hook will now automatically deploy .claude/ changes to ~/.claude/"
