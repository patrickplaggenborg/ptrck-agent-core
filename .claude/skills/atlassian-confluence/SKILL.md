---
name: atlassian-confluence
description: Manage Confluence pages via API. Provides search, page CRUD operations, and space listing. This skill should be used when users need to interact with Confluence like "search Confluence pages", "create a new wiki page", "update documentation", or "list Confluence spaces".
---

# Confluence Integration

Manage Confluence pages using the Confluence REST API v2.

## When to Use This Skill

Use this skill when the user wants to:
- Search for pages
- View page content
- Create, update, or delete pages
- List available spaces

## Prerequisites

1. **Install dependencies**:
   ```bash
   pip install requests
   ```

2. **Configure authentication**:
   ```bash
   export CONFLUENCE_EMAIL="your.email@company.com"
   export CONFLUENCE_API_TOKEN="your-confluence-token"
   export CONFLUENCE_CLOUD_ID="your-cloud-id"
   ```

   - Get your API token from: https://id.atlassian.com/manage-profile/security/api-tokens
   - Get your Cloud ID from: `https://your-site.atlassian.net/_edge/tenant_info`

3. **Verify setup**:
   ```bash
   python3 .claude/skills/atlassian-confluence/scripts/confluence_api.py test
   ```

## Confluence Tool

The Confluence tool is located at `.claude/skills/atlassian-confluence/scripts/confluence_api.py`. Execute it using `python3` with appropriate commands.

### Available Commands

| Command | Description | Example |
|---------|-------------|---------|
| `test` | Test connection | `test` |
| `search` | Search pages | `search "meeting notes"` |
| `get` | View page content | `get 12345` |
| `create` | Create a new page | `create --space DEV --title "Title" --content "Content"` |
| `update` | Update a page | `update 12345 --content "New content"` |
| `delete` | Delete a page | `delete 12345` |
| `spaces` | List available spaces | `spaces` |

### Common Usage Patterns

#### Test Connection
```bash
python3 .claude/skills/atlassian-confluence/scripts/confluence_api.py test
```

#### Search Pages
```bash
python3 .claude/skills/atlassian-confluence/scripts/confluence_api.py search "project documentation"
python3 .claude/skills/atlassian-confluence/scripts/confluence_api.py search "meeting notes" --space DEV
```

#### View Page Content
```bash
python3 .claude/skills/atlassian-confluence/scripts/confluence_api.py get 12345
```

#### Create Page
```bash
python3 .claude/skills/atlassian-confluence/scripts/confluence_api.py create --space DEV --title "API Documentation" --content "<h1>Overview</h1><p>This page documents...</p>"
python3 .claude/skills/atlassian-confluence/scripts/confluence_api.py create --space DEV --title "Child Page" --parent 12345 --content "Content here"
```

#### Update Page
```bash
python3 .claude/skills/atlassian-confluence/scripts/confluence_api.py update 12345 --content "Updated content"
python3 .claude/skills/atlassian-confluence/scripts/confluence_api.py update 12345 --title "New Title"
```

#### Delete Page
```bash
python3 .claude/skills/atlassian-confluence/scripts/confluence_api.py delete 12345
```

#### List Spaces
```bash
python3 .claude/skills/atlassian-confluence/scripts/confluence_api.py spaces
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

## API Token Scopes

When creating your API token, you need specific scopes for different operations:

| Operation | Required Scopes |
|-----------|----------------|
| Read pages | `read:confluence-content.all` or `read:page:confluence` |
| Search | `search:confluence` |
| Create pages | `write:confluence-content` or `write:page:confluence` |
| Update pages | `write:confluence-content` or `write:page:confluence` |
| Delete pages | `delete:page:confluence` |
| List spaces | `read:confluence-space.summary` |

Create tokens at: https://id.atlassian.com/manage-profile/security/api-tokens

## Error Handling

When errors occur, check:
1. Dependencies installed: `pip install requests`
2. Environment variables are set correctly (`CONFLUENCE_EMAIL`, `CONFLUENCE_API_TOKEN`, `CONFLUENCE_CLOUD_ID`)
3. API token has required scopes for the operation
4. Network connectivity to your Atlassian instance

## API Documentation

- Confluence REST API v2: https://developer.atlassian.com/cloud/confluence/rest/v2/
