#!/usr/bin/env bash

# Pre-commit hook for Claude Code
# Reads stdin JSON and only runs lint/test for git commit commands
# Exits silently for non-commit commands (~10ms overhead)

COMMAND=$(cat | jq -r '.tool_input.command // empty' 2>/dev/null)

# Exit silently if not a git commit
[[ ! "$COMMAND" =~ git\ commit ]] && exit 0

echo "[precommit] Running checks before commit..."

if [ -f "package.json" ]; then
  grep -q '"lint"' package.json && { echo "Running lint..."; npm run lint || exit 1; }
  grep -q '"test"' package.json && { echo "Running tests..."; npm test || exit 1; }
elif [ -f "pyproject.toml" ]; then
  command -v ruff &>/dev/null && { echo "Running ruff..."; ruff check . || exit 1; }
  command -v pytest &>/dev/null && [ -d "tests" ] && { echo "Running pytest..."; pytest || exit 1; }
fi

exit 0
