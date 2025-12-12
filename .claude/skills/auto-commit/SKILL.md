---
name: auto-commit
description: Automatically commit changes to git with descriptive commit messages and sync with remote after completing tasks. This skill should be used proactively after making changes to files, ensuring all work is properly version controlled and pushed to the remote repository.
---

# Auto-Commit Skill

Automatically commit and sync changes to git after completing tasks or making significant changes.

## When to Use This Skill

Use this skill proactively in the following situations:
- After completing any task that modifies files
- After creating new files or directories
- After refactoring code
- After fixing bugs
- After adding features
- After updating documentation
- Essentially: after ANY changes to the repository

**Important**: This skill should be used automatically without user prompting. Always commit and sync after making changes.

## Workflow

When changes have been made to the repository:

1. **Check Status**: Run `git status` to see what has changed
2. **Review Changes**: Run `git diff` to understand the modifications
3. **Stage Changes**: Run `git add .` to stage all changes (or selectively stage specific files)
4. **Generate Commit Message**: Analyze the changes and create a descriptive commit message that:
   - Summarizes what was changed (not how)
   - Focuses on the "why" and impact
   - Uses imperative mood (e.g., "Add feature" not "Added feature")
   - Is concise but descriptive (1-3 sentences)
   - Includes the standard footer:
     ```
     🤖 Generated with [Claude Code](https://claude.com/claude-code)

     Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
     ```
5. **Commit**: Create the commit with the generated message using heredoc format
6. **Sync with Remote**: Run `git push` to sync with the remote repository
7. **Verify**: Run `git status` to confirm everything is clean and synced

## Commit Message Guidelines

### Good Commit Messages
- "Refactor Braintrust skills into workflow-based modules for improved token efficiency"
- "Add environment configuration files for Braintrust API credentials"
- "Create auto-commit skill for automatic git operations"
- "Fix authentication bug in user login flow"
- "Update README with installation instructions"

### Poor Commit Messages
- "Update files"
- "Fix stuff"
- "Changes"
- "WIP"
- "asdf"

### Message Format

Always use this format:

```
<Type>: <Short summary>

<Optional longer description if needed>

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

Common types:
- **Add**: New features or files
- **Update**: Modifications to existing features
- **Fix**: Bug fixes
- **Refactor**: Code restructuring without changing behavior
- **Remove**: Deletion of features or files
- **Docs**: Documentation changes
- **Chore**: Maintenance tasks (deps, config, etc.)

## Example Execution

```bash
# 1. Check what changed
git status

# 2. Review the changes
git diff

# 3. Stage changes
git add .

# 4. Commit with descriptive message
git commit -m "$(cat <<'EOF'
Refactor Braintrust skills into 4 workflow-based modules

Split monolithic braintrust skill into focused skills: braintrust-core (projects),
braintrust-experimentation (prompts/datasets/experiments), braintrust-evaluation
(eval runner), and braintrust-logs (production monitoring). This improves token
efficiency by ~30% for typical workflows.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"

# 5. Push to remote
git push

# 6. Verify
git status
```

## Important Notes

- **Always use heredoc format** for commit messages to ensure proper formatting
- **Never skip committing** after making changes - this skill should be used proactively
- **Always push to remote** after committing to keep the remote in sync
- **Check git status before and after** to ensure clean state
- **Don't commit secrets** - ensure `.env` and other sensitive files are in `.gitignore`
- **Handle merge conflicts** if push fails due to remote changes:
  1. Run `git pull --rebase`
  2. Resolve any conflicts
  3. Continue rebase: `git rebase --continue`
  4. Push again: `git push`

## Error Handling

If push fails:
1. Check if remote has changes: `git fetch && git status`
2. Pull with rebase: `git pull --rebase`
3. Resolve conflicts if any
4. Push again: `git push`

If commit fails due to pre-commit hooks:
1. Review the hook error message
2. Fix the issues identified
3. Stage the fixes: `git add .`
4. Retry commit

## When NOT to Use This Skill

- When the user explicitly asks NOT to commit
- When working with a detached HEAD
- When in the middle of a rebase or merge operation
- When there are no changes to commit (`git status` shows clean)

## Integration

This skill works automatically as part of the normal workflow. After completing any task that modifies files, this skill should trigger to ensure changes are committed and synced.
