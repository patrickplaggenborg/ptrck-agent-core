# Agent Instructions for ptrck-agent-core

This repository is the **source of truth** for global Claude Code configuration (skills, commands, and hooks).

## First-Time Setup

After cloning this repo, run:
```bash
.claude/skills/repo-deployment/scripts/setup-hooks.sh
```

This installs the git hooks needed for automatic deployment. See the `repo-deployment` skill for details.

## Deployment Workflow

When making changes to files in `.claude/` (skills, commands, or hooks):

1. **Automatic deployment**: After committing changes, the post-commit hook will automatically deploy to `~/.claude/`
2. **Manual deployment**: Run `.claude/skills/repo-deployment/scripts/deploy-to-user.sh` anytime to sync changes

## Important Notes

- Changes to `.claude/` in this repo are deployed globally to `~/.claude/`
- All other repositories will inherit these global configurations
- When creating or updating skills, commands, or hooks, remind the user that changes will be automatically deployed on the next commit
- If you clone this repo on a new machine, remember to run the setup script first

## Output Folder

The `/output/` folder is for storing artifacts from quick, ad-hoc tasks that don't have a defined project scope.

- **Organization**: Create subdirectories by task/project name (e.g., `output/api-research/`, `output/data-migration-script/`)
- **Committed to git**: This folder is tracked, not ignored
- **Cleanup**: Manual cleanup when instructed by the user
