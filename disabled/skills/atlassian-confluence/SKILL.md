---
name: atlassian-confluence
description: Manage Confluence pages via CLI. Provides search, page CRUD operations, and space listing. This skill should be used when users need to interact with Confluence like "search Confluence pages", "create a new wiki page", "update documentation", or "list Confluence spaces".
---

# Confluence Integration

Manage Confluence pages using a CLI wrapper around `confluence-cli`.

## When to Use This Skill

Use this skill when the user wants to:
- Search for pages
- View page content
- Create, update, or delete pages
- List available spaces

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

The Confluence tool is located at `.claude/skills/atlassian-confluence/scripts/confluence_cli.py`. Execute it using `python3` with appropriate commands.

### Available Commands

| Command | Description | Example |
|---------|-------------|---------|
| `search` | Search pages | `search "meeting notes"` |
| `get` | View page content | `get 12345` |
| `create` | Create a new page | `create --space DEV --title "Title" --content "Content"` |
| `update` | Update a page | `update 12345 --content "New content"` |
| `delete` | Delete a page | `delete 12345` |
| `spaces` | List available spaces | `spaces` |

### Common Usage Patterns

#### Search Pages
```bash
python3 .claude/skills/atlassian-confluence/scripts/confluence_cli.py search "project documentation"
python3 .claude/skills/atlassian-confluence/scripts/confluence_cli.py search "meeting notes" --space DEV
```

#### View Page Content
```bash
python3 .claude/skills/atlassian-confluence/scripts/confluence_cli.py get 12345
```

#### Create Page
```bash
python3 .claude/skills/atlassian-confluence/scripts/confluence_cli.py create --space DEV --title "API Documentation" --content "# Overview\n\nThis page documents..."
python3 .claude/skills/atlassian-confluence/scripts/confluence_cli.py create --space DEV --title "Child Page" --parent 12345 --content "Content here"
```

#### Update Page
```bash
python3 .claude/skills/atlassian-confluence/scripts/confluence_cli.py update 12345 --content "Updated content"
python3 .claude/skills/atlassian-confluence/scripts/confluence_cli.py update 12345 --title "New Title"
```

#### Delete Page
```bash
python3 .claude/skills/atlassian-confluence/scripts/confluence_cli.py delete 12345
```

#### List Spaces
```bash
python3 .claude/skills/atlassian-confluence/scripts/confluence_cli.py spaces
```

## Output Format

All commands return JSON output for easy parsing. Example:

```json
{
  "id": "12345",
  "title": "Page Title",
  "space": "DEV",
  "version": 5
}
```

## Error Handling

When errors occur, check:
1. CLI is installed: `which confluence-cli`
2. Authentication is configured: `confluence-cli spaces`
3. Network connectivity to your Atlassian instance
4. Required permissions for the operation

## CLI Documentation

For additional CLI features: https://github.com/pchuri/confluence-cli
