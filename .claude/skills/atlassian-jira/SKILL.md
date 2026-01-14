---
name: atlassian-jira
description: Manage Jira issues via API. Provides search, CRUD operations, comments, transitions, worklogs, links, epics, and sprints. This skill should be used when users need to interact with Jira like "create a Jira issue", "search for open bugs", "transition issue to Done", or "add a comment to PROJ-123".
---

# Jira Integration

Manage Jira issues using `atlassian-python-api`.

## When to Use This Skill

Use this skill when the user wants to:
- Search for issues using JQL
- View issue details
- Create, update, or delete issues
- Add comments to issues
- Transition issues (move between statuses)
- Log work on issues
- Link issues together
- Manage epics and sprints

## Prerequisites

1. **Install dependencies**:
   ```bash
   pip install atlassian-python-api>=3.41.0
   ```

2. **Configure authentication**:
   ```bash
   export JIRA_EMAIL="your.email@company.com"
   export JIRA_API_TOKEN="your-jira-token"
   export JIRA_CLOUD_ID="your-cloud-id"
   ```

   - Get your API token from: https://id.atlassian.com/manage-profile/security/api-tokens
   - Get your Cloud ID from: `https://your-site.atlassian.net/_edge/tenant_info`

3. **Verify setup**:
   ```bash
   python3 .claude/skills/atlassian-jira/scripts/jira_api.py test
   ```

## Jira Tool

The Jira tool is located at `.claude/skills/atlassian-jira/scripts/jira_api.py`. Execute it using `python3` with appropriate commands.

### Available Commands

| Command | Description | Example |
|---------|-------------|---------|
| `test` | Test connection | `test` |
| `search` | Search issues using JQL | `search "project = PROJ AND status = Open"` |
| `get` | View issue details | `get PROJ-123` |
| `create` | Create a new issue | `create --project PROJ --type Task --summary "Title"` |
| `update` | Update an issue | `update PROJ-123 --summary "New Title"` |
| `delete` | Delete an issue | `delete PROJ-123` |
| `comment` | Add a comment | `comment PROJ-123 "Comment text"` |
| `transition` | Move issue to new status | `transition PROJ-123 "In Progress"` |
| `worklog` | Log work on an issue | `worklog PROJ-123 --time 2h --comment "Work done"` |
| `link` | Link two issues | `link PROJ-123 PROJ-456 --type "blocks"` |
| `epic-add` | Add issue to epic | `epic-add EPIC-1 PROJ-123` |
| `sprints` | List sprints | `sprints --board 123` |

### Common Usage Patterns

#### Test Connection
```bash
python3 .claude/skills/atlassian-jira/scripts/jira_api.py test
```

#### Search Issues
```bash
python3 .claude/skills/atlassian-jira/scripts/jira_api.py search "project = MYPROJ AND status = 'In Progress'"
python3 .claude/skills/atlassian-jira/scripts/jira_api.py search "assignee = currentUser() AND sprint in openSprints()"
python3 .claude/skills/atlassian-jira/scripts/jira_api.py search "created >= -7d" --limit 20
```

#### View Issue Details
```bash
python3 .claude/skills/atlassian-jira/scripts/jira_api.py get PROJ-123
```

#### Create Issue
```bash
python3 .claude/skills/atlassian-jira/scripts/jira_api.py create --project PROJ --type Task --summary "Implement feature X" --description "Details here"
python3 .claude/skills/atlassian-jira/scripts/jira_api.py create --project PROJ --type Bug --summary "Fix login error" --priority High
```

#### Update Issue
```bash
python3 .claude/skills/atlassian-jira/scripts/jira_api.py update PROJ-123 --summary "Updated title"
python3 .claude/skills/atlassian-jira/scripts/jira_api.py update PROJ-123 --assignee "john.doe"
python3 .claude/skills/atlassian-jira/scripts/jira_api.py update PROJ-123 --priority Critical
```

#### Transition Issue
```bash
python3 .claude/skills/atlassian-jira/scripts/jira_api.py transition PROJ-123 "In Progress"
python3 .claude/skills/atlassian-jira/scripts/jira_api.py transition PROJ-123 "Done"
```

#### Add Comment
```bash
python3 .claude/skills/atlassian-jira/scripts/jira_api.py comment PROJ-123 "Investigation complete. Root cause identified."
```

#### Log Work
```bash
python3 .claude/skills/atlassian-jira/scripts/jira_api.py worklog PROJ-123 --time 2h --comment "Code review"
python3 .claude/skills/atlassian-jira/scripts/jira_api.py worklog PROJ-123 --time 30m
```

#### Link Issues
```bash
python3 .claude/skills/atlassian-jira/scripts/jira_api.py link PROJ-123 PROJ-456 --type "blocks"
python3 .claude/skills/atlassian-jira/scripts/jira_api.py link PROJ-123 PROJ-456 --type "is blocked by"
python3 .claude/skills/atlassian-jira/scripts/jira_api.py link PROJ-123 PROJ-456 --type "relates to"
```

#### Manage Epics
```bash
python3 .claude/skills/atlassian-jira/scripts/jira_api.py epic-add EPIC-1 PROJ-123 PROJ-124 PROJ-125
```

#### List Sprints
```bash
python3 .claude/skills/atlassian-jira/scripts/jira_api.py sprints --board 123
python3 .claude/skills/atlassian-jira/scripts/jira_api.py sprints --board 123 --state active
```

## Output Format

All commands return JSON output for easy parsing. Example:

```json
{
  "key": "PROJ-123",
  "summary": "Issue title",
  "status": "In Progress",
  "assignee": "john.doe",
  "priority": "High"
}
```

## Scoped Token Configuration

When using scoped API tokens, you need specific scopes for different operations:

| Operation | Required Scopes |
|-----------|----------------|
| Read issues | `read:jira-work` |
| Create/update issues | `write:jira-work` |
| Delete issues | `delete:jira-work` (if available) |
| Manage sprints | `read:sprint:jira-software`, `write:sprint:jira-software` |

Create scoped tokens at: https://id.atlassian.com/manage-profile/security/api-tokens

## Error Handling

When errors occur, check:
1. Dependencies installed: `pip install atlassian-python-api`
2. Environment variables are set correctly (`JIRA_EMAIL`, `JIRA_API_TOKEN`, `JIRA_CLOUD_ID`)
3. API token has required scopes for the operation
4. Network connectivity to your Atlassian instance

## API Documentation

- atlassian-python-api: https://atlassian-python-api.readthedocs.io/
- Jira REST API: https://developer.atlassian.com/cloud/jira/platform/rest/v3/
