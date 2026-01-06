# repo-deployment

Deploy `.claude/` configurations from this repository to the user's global `~/.claude/` directory.

## What this does

This skill manages automatic deployment of skills, commands, and hooks from this repo to your user directory. Changes committed to `.claude/` are automatically synced to `~/.claude/`, making them available globally.

## Setup (one-time)

After cloning this repo, run the setup script to install the git hook:

```bash
.claude/skills/repo-deployment/scripts/setup-hooks.sh
```

This copies the post-commit hook to `.git/hooks/`, enabling automatic deployment.

## How it works

1. You commit changes to `.claude/` files
2. The post-commit hook detects the changes
3. `deploy-to-user.sh` syncs to `~/.claude/` using rsync

## Manual deployment

To deploy without committing:

```bash
.claude/skills/repo-deployment/scripts/deploy-to-user.sh
```

## What gets synced

- `.claude/skills/` → `~/.claude/skills/`
- `.claude/commands/` → `~/.claude/commands/`
- `.claude/hooks/` → `~/.claude/hooks/`

Uses `rsync --delete`, so removed files are also removed from the target.
