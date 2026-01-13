#!/usr/bin/env bash

# Setup script for the precommit hook
# This adds the PreToolUse hook configuration to ~/.claude/settings.json

SETTINGS_FILE="$HOME/.claude/settings.json"

# Check if jq is available
if ! command -v jq &>/dev/null; then
  echo "Error: jq is required but not installed."
  echo "Install with: brew install jq"
  exit 1
fi

# Check if settings file exists
if [ ! -f "$SETTINGS_FILE" ]; then
  echo "Creating new settings.json..."
  echo '{}' > "$SETTINGS_FILE"
fi

# Define the hook configuration
HOOK_CONFIG='{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "if echo \"$CLAUDE_TOOL_INPUT\" | jq -r '\''.command'\'' | grep -qE '\''^git commit'\''; then ~/.claude/hooks/precommit.sh; fi",
            "timeout": 300
          }
        ]
      }
    ]
  }
}'

# Merge the hook config into existing settings
echo "Adding PreToolUse hook to $SETTINGS_FILE..."
MERGED=$(jq -s '.[0] * .[1]' "$SETTINGS_FILE" <(echo "$HOOK_CONFIG"))
echo "$MERGED" > "$SETTINGS_FILE"

echo "Done! PreToolUse hook configured."
echo ""
echo "The hook will now run lint and tests before any 'git commit' command."
