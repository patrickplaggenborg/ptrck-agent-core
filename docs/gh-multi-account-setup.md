# gh CLI Multi-Account Auto-Switch Setup

## The Problem

The `gh` CLI uses a global "active account" that doesn't respect which GitHub user owns the current repository. When working across multiple repos owned by different GitHub accounts, `gh` commands fail with authentication errors like:

```
error: must be a collaborator to comment on this issue
```

This happens because `gh` uses whichever account was last switched to, regardless of which account actually has access to the current repo.

## The Solution

A shell wrapper function that:
1. Tries the `gh` command normally
2. If it fails, detects the GitHub username from the git remote
3. Switches to that account and retries the command

## One-Liner Installation

Run this command to add the wrapper to your shell config:

```bash
echo 'gh() { command gh "$@" 2>&1 || { user=$(git remote get-url origin 2>/dev/null | sed -E '"'"'s#.*[:/]([^/]+)/.*#\1#'"'"'); [[ -n "$user" ]] && command gh auth switch --user "$user" 2>/dev/null; command gh "$@"; }; }' >> ~/.zshrc && source ~/.zshrc
```

## Manual Installation

If you prefer to add it manually, add this function to your `~/.zshrc` or `~/.bashrc`:

```bash
gh() {
  command gh "$@" 2>&1 || {
    user=$(git remote get-url origin 2>/dev/null | sed -E 's#.*[:/]([^/]+)/.*#\1#')
    [[ -n "$user" ]] && command gh auth switch --user "$user" 2>/dev/null
    command gh "$@"
  }
}
```

## How It Works

1. `command gh "$@"` - Runs the original `gh` command with all arguments
2. If it fails (`||`), the wrapper:
   - Extracts the username from the git remote URL (works for both HTTPS and SSH)
   - Switches `gh` to that user account
   - Retries the original command

## Prerequisites

- Multiple GitHub accounts must already be authenticated with `gh auth login`
- The repo's remote URL must contain the owner's username (standard for GitHub URLs)

## Verification

After installation:

1. Open a new terminal or run `source ~/.zshrc`
2. `cd` to a repo owned by a different account than your current active one
3. Run any `gh` command (e.g., `gh repo view`)
4. The wrapper should auto-switch accounts and succeed on retry
