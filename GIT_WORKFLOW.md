# Degenerate Labs Blender Fork - Git Workflow

## Repository Setup

### Remotes
```bash
origin        - https://github.com/blender/blender (official mirror)
degen         - https://github.com/BitHighlander/blender (your fork)
lfs-fallback  - https://projects.blender.org/blender/blender.git (LFS files)
```

### Branch Strategy
- **`main`**: Tracks upstream Blender (from `origin`)
- **`master-degen`**: Degenerate Labs modifications and customizations

---

## Daily Workflow

### Making Changes
```bash
# Make sure you're on your branch
git checkout master-degen

# Make your changes to code
# ... edit files ...

# Stage and commit
git add <files>
git commit -m "Your commit message"

# Push to your fork (skip LFS for GitHub)
git push degen master-degen --no-verify
```

### Syncing with Upstream Blender
```bash
# Fetch latest from official Blender
git fetch origin main

# Option 1: Rebase your changes on top of latest Blender
git checkout master-degen
git rebase origin/main

# Option 2: Merge latest Blender into your branch
git checkout master-degen  
git merge origin/main

# Push updated branch
git push degen master-degen --force-with-lease --no-verify
```

---

## Working with LFS Files

### Important Note
GitHub forks **cannot** upload new LFS objects. The original LFS files from Blender are fine, but you can't add new large files.

### For release datafiles (needed for building)
```bash
# Restore from git if missing
git checkout HEAD -- release/datafiles/

# Or pull specific LFS files
git lfs pull --include="release/datafiles/**"
```

### Bypass LFS for normal workflow
```bash
# Clone without LFS (faster)
GIT_LFS_SKIP_SMUDGE=1 git clone https://github.com/BitHighlander/blender.git

# Push without LFS (our normal workflow)
git push degen master-degen --no-verify
```

---

## Building Your Fork

```bash
# First time setup
git clone https://github.com/BitHighlander/blender.git
cd blender
git checkout master-degen

# Get dependencies
git clone --depth=1 https://projects.blender.org/blender/lib-macos_arm64.git lib/macos_arm64

# Restore release files if needed
git checkout HEAD -- release/datafiles/

# Build
make developer ninja

# Run
open ../build_darwin/bin/Blender.app
```

---

## Common Tasks

### Create a feature branch
```bash
git checkout -b feature/my-awesome-feature master-degen
# ... make changes ...
git push degen feature/my-awesome-feature --no-verify
```

### Cherry-pick a commit from upstream
```bash
git fetch origin
git cherry-pick <commit-hash>
git push degen master-degen --no-verify
```

### Stash local changes
```bash
git stash push -m "WIP: description"
# ... do something else ...
git stash pop
```

### View what changed
```bash
# Since last commit
git diff

# Between your branch and upstream
git diff origin/main...master-degen

# File history
git log --follow <file>
```

---

## Troubleshooting

### "Failed to push LFS objects"
**Solution:** Always use `--no-verify` flag when pushing:
```bash
git push degen master-degen --no-verify
```

### "Deleted files" showing in git status
**Cause:** Git LFS files not downloaded locally
**Solution:** These are test files, safe to ignore. If needed:
```bash
# Restore specific files
git checkout HEAD -- <path>

# Or ignore them in your workflow
git status --short | grep -v "^D "
```

### Merge conflicts with upstream
```bash
# Abort and start over
git rebase --abort
# or
git merge --abort

# Resolve conflicts manually
git status  # shows conflicted files
# Edit files to resolve
git add <resolved-files>
git rebase --continue  # or git merge --continue
```

---

## Best Practices

1. **Commit often** - Small, focused commits are easier to manage
2. **Write good commit messages** - Explain *why*, not just *what*
3. **Keep master-degen clean** - Use feature branches for experiments
4. **Sync regularly** - Don't let your fork drift too far from upstream
5. **Document your changes** - Update LEARNING_NOTES.md with discoveries

---

## Links

- **Your Fork**: https://github.com/BitHighlander/blender
- **Upstream**: https://github.com/blender/blender
- **Blender Dev Docs**: https://developer.blender.org/docs/
- **Build Guide**: BUILD_GUIDE.md
- **Learning Notes**: LEARNING_NOTES.md

---

## Quick Reference

```bash
# Daily commands
git status
git add <files>
git commit -m "message"
git push degen master-degen --no-verify

# Sync with upstream
git fetch origin
git rebase origin/main  # or git merge origin/main
git push degen master-degen --force-with-lease --no-verify

# Build
make developer ninja
```

