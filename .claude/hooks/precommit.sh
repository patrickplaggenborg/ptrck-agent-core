#!/usr/bin/env bash

# Pre-commit hook for Claude Code
# Auto-detects and runs lint/test commands before git commits
# Exits 0 (success) if no lint/test configured, so commits still work

echo "[precommit hook] triggered"

if [ -f "package.json" ]; then
  # Node.js project - check if scripts exist
  if grep -q '"lint"' package.json 2>/dev/null; then
    echo "Running npm run lint..."
    npm run lint || exit 1
  fi
  if grep -q '"test"' package.json 2>/dev/null; then
    echo "Running npm test..."
    npm test || exit 1
  fi
elif [ -f "pyproject.toml" ]; then
  # Python project with pyproject.toml
  if command -v ruff &>/dev/null; then
    echo "Running ruff..."
    ruff check . || exit 1
  fi
  if command -v pytest &>/dev/null && [ -d "tests" ]; then
    echo "Running pytest..."
    pytest || exit 1
  fi
fi

# Success - either checks passed or none were configured
exit 0
