---
name: atlassian-confluence
description: Manage Confluence pages via API. Provides search, page CRUD operations, and space listing. Supports both classic and scoped API tokens. This skill should be used when users need to interact with Confluence like "search Confluence pages", "create a new wiki page", "update documentation", or "list Confluence spaces".
---

# Confluence Integration

Manage Confluence pages using `atlassian-python-api` with support for scoped API tokens.

## When to Use This Skill

Use this skill when the user wants to:
- Search for pages
- View page content
- Create, update, or delete pages
- List available spaces

## Prerequisites

1. **Install dependencies**:
   ```bash
   pip install atlassian-python-api>=3.41.0
   ```

2. **Configure authentication** (choose one method):

   **Option A: Classic API Token** (uses site-specific URL)
   ```bash
   export ATLASSIAN_URL="https://your-site.atlassian.net"
   export ATLASSIAN_EMAIL="your.email@company.com"
   export ATLASSIAN_API_TOKEN="your-api-token"
   ```

   **Option B: Scoped API Token** (uses api.atlassian.com - more secure)
   ```bash
   export ATLASSIAN_EMAIL="your.email@company.com"
   export ATLASSIAN_API_TOKEN="your-scoped-api-token"
   export ATLASSIAN_CLOUD_ID="your-cloud-id"
   export ATLASSIAN_USE_SCOPED_TOKEN="true"
   ```

   Get your Cloud ID from: `https://your-site.atlassian.net/_edge/tenant_info`

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

## Scoped Token Configuration

When using scoped API tokens, you need specific scopes for different operations:

| Operation | Required Scopes |
|-----------|----------------|
| Read pages | `read:confluence-content.all` or `read:page:confluence` |
| Search | `search:confluence` |
| Create pages | `write:confluence-content` or `write:page:confluence` |
| Update pages | `write:confluence-content` or `write:page:confluence` |
| Delete pages | `delete:page:confluence` |
| List spaces | `read:confluence-space.summary` |

Create scoped tokens at: https://id.atlassian.com/manage-profile/security/api-tokens

## Error Handling

When errors occur, check:
1. Dependencies installed: `pip install atlassian-python-api`
2. Environment variables are set correctly
3. For scoped tokens: using correct Cloud ID and api.atlassian.com endpoint
4. Required permissions/scopes for the operation
5. Network connectivity to your Atlassian instance

## API Documentation

- atlassian-python-api: https://atlassian-python-api.readthedocs.io/
- Confluence REST API: https://developer.atlassian.com/cloud/confluence/rest/
