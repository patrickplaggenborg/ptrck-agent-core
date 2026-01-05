---
name: publish-skill
description: Publish a skill from the current repo to the ptrck-agent-core repository and user folder. Use when the user wants to move or copy a skill they've created to their central skills repo for distribution.
---

# Publish Skill

Publish skills from any repository to the central `ptrck-agent-core` repo and user folder for immediate availability.

## When to Use

- After creating or updating a skill in a project-specific repo
- When moving a skill to the central skills repository
- To make a skill available across all projects

## Usage

Run the publish script with the skill name:

```bash
.claude/skills/publish-skill/scripts/publish_skill.sh <skill-name>
```

Example:
```bash
.claude/skills/publish-skill/scripts/publish_skill.sh my-new-skill
```

## What It Does

1. Validates the skill exists in `.claude/skills/<skill-name>/`
2. Creates a temporary shallow clone of `ptrck-agent-core`
3. Syncs the skill folder using `rsync --delete` (removes stale files)
4. Commits and pushes to `ptrck-agent-core`
5. Syncs the skill to `~/.claude/skills/` for immediate use
6. Cleans up temporary files

## Destinations

The skill is published to two locations:

1. **Git repo**: `https://github.com/patrickplaggenborg/ptrck-agent-core` at `.claude/skills/<skill-name>/`
2. **User folder**: `~/.claude/skills/<skill-name>/` (immediately available)

## Notes

- Requires git push access to `ptrck-agent-core`
- Uses `rsync --delete` to ensure clean sync (removes files no longer in source)
- Overwrites existing skills with the same name
