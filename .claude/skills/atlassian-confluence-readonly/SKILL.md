---
name: atlassian-confluence-readonly
description: Read-only Confluence access via CLI. Provides search and view operations only - no modifications. This skill should be used when users need to query Confluence like "search for documentation", "show me page 12345", or "list Confluence spaces".
---

# Confluence Integration (Read-Only)

Query Confluence pages using a CLI wrapper around `confluence-cli`. This skill only provides read operations - no create, update, or delete.

## When to Use This Skill

Use this skill when the user wants to:
- Search for pages
- View page content
- List available spaces

For write operations (create, update, delete), use the full `atlassian-confluence` skill instead.

## Prerequisites

1. **Install confluence-cli**:
   ```bash
   npm install -g @pchuri/confluence-cli
   ```

2. **Configure authentication**:
   ```bash
   confluence-cli config
   ```

3. **Verify setup**:
   ```bash
   confluence-cli spaces
   ```

## Confluence Tool

The Confluence tool is located at `.claude/skills/atlassian-confluence-readonly/scripts/confluence_cli.py`. Execute it using `python3` with appropriate commands.

### Available Commands

| Command | Description | Example |
|---------|-------------|---------|
| `search` | Search pages | `search "meeting notes"` |
| `get` | View page content | `get 12345` |
| `spaces` | List available spaces | `spaces` |

### Common Usage Patterns

#### Search Pages
```bash
python3 .claude/skills/atlassian-confluence-readonly/scripts/confluence_cli.py search "project documentation"
python3 .claude/skills/atlassian-confluence-readonly/scripts/confluence_cli.py search "meeting notes" --space DEV
```

#### View Page Content
```bash
python3 .claude/skills/atlassian-confluence-readonly/scripts/confluence_cli.py get 12345
```

#### List Spaces
```bash
python3 .claude/skills/atlassian-confluence-readonly/scripts/confluence_cli.py spaces
```

## Output Format

All commands return JSON output for easy parsing.

## Error Handling

When errors occur, check:
1. CLI is installed: `which confluence-cli`
2. Authentication is configured: `confluence-cli spaces`
3. Network connectivity to your Atlassian instance

## CLI Documentation

For additional CLI features: https://github.com/pchuri/confluence-cli
