Pull the latest changes from the main branch into the current branch.

Steps:
1. Run `git fetch origin` to get the latest remote refs
2. Run `git merge origin/main` to merge main branch changes into the current branch
3. If there are merge conflicts, list the conflicting files and offer to help resolve them
4. After merging, show a brief summary of what changed (new commits pulled in)
