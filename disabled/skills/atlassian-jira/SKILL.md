---
name: atlassian-jira
description: Manage Jira issues via CLI. Provides search, CRUD operations, comments, transitions, worklogs, links, epics, and sprints. This skill should be used when users need to interact with Jira like "create a Jira issue", "search for open bugs", "transition issue to Done", or "add a comment to PROJ-123".
---

# Jira Integration

Manage Jira issues using a CLI wrapper around `jira-cli`.

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

1. **Install jira-cli**:
   ```bash
   brew install ankitpokhrel/jira-cli/jira-cli
   ```

2. **Configure authentication**:
   ```bash
   # Set your API token (get from https://id.atlassian.com/manage-profile/security/api-tokens)
   export JIRA_API_TOKEN="your-token"

   # Initialize jira-cli
   jira init
   ```

3. **Verify setup**:
   ```bash
   jira me
   ```

## Jira Tool

The Jira tool is located at `.claude/skills/atlassian-jira/scripts/jira_cli.py`. Execute it using `python3` with appropriate commands.

### Available Commands

| Command | Description | Example |
|---------|-------------|---------|
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

#### Search Issues
```bash
python3 .claude/skills/atlassian-jira/scripts/jira_cli.py search "project = MYPROJ AND status = 'In Progress'"
python3 .claude/skills/atlassian-jira/scripts/jira_cli.py search "assignee = currentUser() AND sprint in openSprints()"
python3 .claude/skills/atlassian-jira/scripts/jira_cli.py search "created >= -7d" --limit 20
```

#### View Issue Details
```bash
python3 .claude/skills/atlassian-jira/scripts/jira_cli.py get PROJ-123
```

#### Create Issue
```bash
python3 .claude/skills/atlassian-jira/scripts/jira_cli.py create --project PROJ --type Task --summary "Implement feature X" --description "Details here"
python3 .claude/skills/atlassian-jira/scripts/jira_cli.py create --project PROJ --type Bug --summary "Fix login error" --priority High
```

#### Update Issue
```bash
python3 .claude/skills/atlassian-jira/scripts/jira_cli.py update PROJ-123 --summary "Updated title"
python3 .claude/skills/atlassian-jira/scripts/jira_cli.py update PROJ-123 --assignee "john.doe"
python3 .claude/skills/atlassian-jira/scripts/jira_cli.py update PROJ-123 --priority Critical
```

#### Transition Issue
```bash
python3 .claude/skills/atlassian-jira/scripts/jira_cli.py transition PROJ-123 "In Progress"
python3 .claude/skills/atlassian-jira/scripts/jira_cli.py transition PROJ-123 "Done"
```

#### Add Comment
```bash
python3 .claude/skills/atlassian-jira/scripts/jira_cli.py comment PROJ-123 "Investigation complete. Root cause identified."
```

#### Log Work
```bash
python3 .claude/skills/atlassian-jira/scripts/jira_cli.py worklog PROJ-123 --time 2h --comment "Code review"
python3 .claude/skills/atlassian-jira/scripts/jira_cli.py worklog PROJ-123 --time 30m
```

#### Link Issues
```bash
python3 .claude/skills/atlassian-jira/scripts/jira_cli.py link PROJ-123 PROJ-456 --type "blocks"
python3 .claude/skills/atlassian-jira/scripts/jira_cli.py link PROJ-123 PROJ-456 --type "is blocked by"
python3 .claude/skills/atlassian-jira/scripts/jira_cli.py link PROJ-123 PROJ-456 --type "relates to"
```

#### Manage Epics
```bash
python3 .claude/skills/atlassian-jira/scripts/jira_cli.py epic-add EPIC-1 PROJ-123 PROJ-124 PROJ-125
```

#### List Sprints
```bash
python3 .claude/skills/atlassian-jira/scripts/jira_cli.py sprints --board 123
python3 .claude/skills/atlassian-jira/scripts/jira_cli.py sprints --board 123 --state active
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

## Error Handling

When errors occur, check:
1. CLI is installed: `which jira`
2. Authentication is configured: `jira me`
3. Network connectivity to your Atlassian instance
4. Required permissions for the operation

## CLI Documentation

For additional CLI features: https://github.com/ankitpokhrel/jira-cli
