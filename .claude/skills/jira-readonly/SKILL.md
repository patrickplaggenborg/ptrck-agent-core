---
name: jira-readonly
description: Read-only Jira access via CLI. Provides search and view operations only - no modifications. This skill should be used when users need to query Jira like "search for open bugs", "show me issue PROJ-123", or "list active sprints".
---

# Jira Integration (Read-Only)

Query Jira issues using a CLI wrapper around `jira-cli`. This skill only provides read operations - no create, update, or delete.

## When to Use This Skill

Use this skill when the user wants to:
- Search for issues using JQL
- View issue details
- List sprints

For write operations (create, update, delete, comment, transition), use the full `jira` skill instead.

## Prerequisites

1. **Install jira-cli**:
   ```bash
   brew install ankitpokhrel/jira-cli/jira-cli
   ```

2. **Configure authentication**:
   ```bash
   export JIRA_API_TOKEN="your-token"
   jira init
   ```

3. **Verify setup**:
   ```bash
   jira me
   ```

## Jira Tool

The Jira tool is located at `.claude/skills/jira-readonly/scripts/jira_cli.py`. Execute it using `python3` with appropriate commands.

### Available Commands

| Command | Description | Example |
|---------|-------------|---------|
| `search` | Search issues using JQL | `search "project = PROJ AND status = Open"` |
| `get` | View issue details | `get PROJ-123` |
| `sprints` | List sprints | `sprints --board 123` |

### Common Usage Patterns

#### Search Issues
```bash
python3 .claude/skills/jira-readonly/scripts/jira_cli.py search "project = MYPROJ AND status = 'In Progress'"
python3 .claude/skills/jira-readonly/scripts/jira_cli.py search "assignee = currentUser() AND sprint in openSprints()"
python3 .claude/skills/jira-readonly/scripts/jira_cli.py search "created >= -7d" --limit 20
```

#### View Issue Details
```bash
python3 .claude/skills/jira-readonly/scripts/jira_cli.py get PROJ-123
```

#### List Sprints
```bash
python3 .claude/skills/jira-readonly/scripts/jira_cli.py sprints --board 123
python3 .claude/skills/jira-readonly/scripts/jira_cli.py sprints --board 123 --state active
```

## Output Format

All commands return JSON output for easy parsing.

## Error Handling

When errors occur, check:
1. CLI is installed: `which jira`
2. Authentication is configured: `jira me`
3. Network connectivity to your Atlassian instance

## CLI Documentation

For additional CLI features: https://github.com/ankitpokhrel/jira-cli
