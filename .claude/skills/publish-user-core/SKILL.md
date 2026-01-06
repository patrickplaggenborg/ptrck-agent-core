---
name: publish-user-core
description: Publish skills, commands, or hooks from the current repo to both ptrck-agent-core repository and user folder. Use when you want to distribute Claude configurations globally.
---

# Publish User Core

Publish Claude configurations (skills, commands, hooks) from any repository to:
- **User folder**: `~/.claude/` for immediate local availability
- **Core repo**: `ptrck-agent-core` for version control and sharing

## When to Use

- After creating or updating a skill, command, or hook in a project
- When moving configurations to the central repository
- To make configurations available across all projects

## Usage

Run the publish script with a name (auto-detects type) or explicit type:

```bash
# Auto-detect type
.claude/skills/publish-user-core/scripts/publish.sh <name>

# Explicit type
.claude/skills/publish-user-core/scripts/publish.sh <type> <name>
```

### Examples

```bash
# Publish a skill (auto-detected from .claude/skills/my-skill/)
./scripts/publish.sh my-skill

# Publish a command (auto-detected from .claude/commands/pull.md)
./scripts/publish.sh pull

# Publish a hook (auto-detected from .claude/hooks/my-hook.md)
./scripts/publish.sh my-hook

# Explicit type specification
./scripts/publish.sh skill my-skill
./scripts/publish.sh command pull
./scripts/publish.sh hook my-hook
```

## What It Does

1. Auto-detects the configuration type (skill, command, or hook)
2. Validates the source exists
3. Creates a temporary shallow clone of `ptrck-agent-core`
4. Syncs the configuration using `rsync --delete`
5. Commits and pushes to `ptrck-agent-core`
6. Syncs to `~/.claude/` for immediate use
7. Removes source from workspace after successful publish

## Type Detection

- **Skill**: `.claude/skills/<name>/` directory with `SKILL.md`
- **Command**: `.claude/commands/<name>.md` file
- **Hook**: `.claude/hooks/<name>.md` file

## Destinations

| Type | Git Repo | User Folder |
|------|----------|-------------|
| Skill | `.claude/skills/<name>/` | `~/.claude/skills/<name>/` |
| Command | `.claude/commands/<name>.md` | `~/.claude/commands/<name>.md` |
| Hook | `.claude/hooks/<name>.md` | `~/.claude/hooks/<name>.md` |

## Notes

- Requires git push access to `ptrck-agent-core`
- Uses `rsync --delete` to ensure clean sync
- Overwrites existing configurations with the same name
- Source is removed only after both destinations succeed
