---
name: task-cleanup
description: "Cleans up the tasks directory by removing all materials (files) while preserving the directory structure. Leaves all subdirectories empty. Use when: you need to reset the tasks directory; you want to clear completed tasks and specifications; you need a clean slate for new task planning."
---

# Task Cleanup

Clean up the tasks directory by removing all materials (files) while preserving the directory structure.

## Overview

This skill cleans up the `tasks/` directory at the project root by:
1. **Preserving** the directory structure (all subdirectories remain)
2. **Removing** all files from subdirectories
3. **Keeping** the `task-system-guide.md` documentation file

After cleanup, the tasks directory will have empty subdirectories ready for new work.

---

## Directory Structure

```
tasks/
├── task-archive/                # Will be emptied
├── task-implementation/
│   ├── logs/                    # Will be emptied
│   ├── results/                 # Will be emptied
│   └── state/                   # Will be emptied
├── task-planning/               # Will be emptied
├── task-specifications/         # Will be emptied
├── task-worker-reports/         # Will be emptied
└── task-system-guide.md         # PRESERVED (documentation)
```

---

## Step 1: Safety Checkpoint (Commit & Push)

**CRITICAL: Before any cleanup, create a safety checkpoint.**

**1.1 Verify current branch:**

```bash
# Check current branch
git branch --show-current
```

**Expected output:**
```
main
```

**If NOT on main branch:**
- Notify user: "Currently on `{branch_name}`, switching back to `main`"
- Switch to main: `git checkout main` or `git switch main`
- Re-verify with `git branch --show-current`

**1.2 Commit and push all changes:**

```bash
# Stage all changes
git add -A

# Create safety commit
git commit -m "safety: checkpoint before task cleanup

Committing all changes before cleaning up tasks directory."

# Push to remote
git push
```

**Expected output:**
```
[main <hash>] safety: checkpoint before task cleanup
 N files changed, M insertions(+), D deletions(-)
To https://github.com/<repo>.git
   <old-hash>..<new-hash>  main -> main
```

**Rationale:** This ensures all work is safely backed up before any files are deleted. If anything goes wrong during cleanup, the committed state can be restored.

---

## Step 2: Verify Tasks Directory

**Verify the tasks directory exists at project root:**

```bash
# Check tasks directory
ls -la tasks/
```

**Expected output:**
```
drwxrwxr-x  7 admin admin  4096 Feb  2 05:04 .
drwxrwxr-x 24 admin admin  4096 Feb  2 13:47 ..
drwxrwxr-x  2 admin admin  4096 Feb  2 04:51 task-archive
drwxrwxr-x  5 admin admin  4096 Feb  2 04:30 task-implementation
drwxrwxr-x  2 admin admin  4096 Feb  2 13:41 task-planning
drwxrwxr-x  2 admin admin  4096 Feb  2 13:54 task-specifications
-rw-rw-r--  1 admin admin 22143 Feb  2 04:39 task-system-guide.md
drwxrwxr-x  2 admin admin  4096 Feb  2 04:30 task-worker-reports
```

**If tasks directory doesn't exist:**
- Inform user: "No tasks directory found at project root."
- Ask if they want to create the empty directory structure

---

## Step 3: Show Current Contents

**Before cleaning, show what will be removed:**

```bash
# List all files in tasks subdirectories (excluding .gitkeep files)
find tasks/ -type f -name "*.md" -o -name "*.json" | grep -v "task-system-guide.md"
```

**Count files to be removed:**

```bash
# Count files in each subdirectory
echo "Files to be removed:"
echo "  task-archive/: $(ls -1 tasks/task-archive/ 2>/dev/null | wc -l)"
echo "  task-implementation/results/: $(ls -1 tasks/task-implementation/results/ 2>/dev/null | wc -l)"
echo "  task-implementation/state/: $(ls -1 tasks/task-implementation/state/ 2>/dev/null | wc -l)"
echo "  task-planning/: $(ls -1 tasks/task-planning/ 2>/dev/null | wc -l)"
echo "  task-specifications/: $(ls -1 tasks/task-specifications/ 2>/dev/null | wc -l)"
echo "  task-worker-reports/: $(ls -1 tasks/task-worker-reports/ 2>/dev/null | wc -l)"
```

**Confirm with user before proceeding:**
```
This will remove N files from the tasks directory while preserving:
- All subdirectories (empty)
- task-system-guide.md (documentation)

Proceed with cleanup?
```

---

## Step 4: Clean Up Subdirectories

**Execute cleanup using CLI commands:**

```bash
# Remove all files from task-archive/
rm -f tasks/task-archive/*.md 2>/dev/null

# Remove all files from task-implementation/results/
rm -f tasks/task-implementation/results/*.json 2>/dev/null

# Remove all files from task-implementation/state/
rm -f tasks/task-implementation/state/*.json 2>/dev/null

# Remove all files from task-planning/
rm -f tasks/task-planning/*.md 2>/dev/null

# Remove all files from task-specifications/
rm -f tasks/task-specifications/task-*.md 2>/dev/null

# Remove all directories and files from task-worker-reports/
rm -rf tasks/task-worker-reports/* 2>/dev/null
```

**Alternative single-command cleanup:**

```bash
# Clean all subdirectories in one command
find tasks/ -mindepth 2 -type f ! -name "task-system-guide.md" -delete
find tasks/ -mindepth 2 -type d ! -name "task-implementation" -delete 2>/dev/null
```

---

## Step 5: Verify Cleanup

**Verify all subdirectories are now empty (except preserved files):**

```bash
# Verify cleanup
echo "Verification:"
for dir in tasks/task-archive tasks/task-implementation/results tasks/task-implementation/state tasks/task-planning tasks/task-specifications tasks/task-worker-reports; do
    count=$(ls -1 "$dir" 2>/dev/null | wc -l)
    echo "  $dir: $count files"
done

# Verify preserved file exists
ls -la tasks/task-system-guide.md
```

**Expected output:**
```
Verification:
  tasks/task-archive: 0 files
  tasks/task-implementation/results: 0 files
  tasks/task-implementation/state: 0 files
  tasks/task-planning: 0 files
  tasks/task-specifications: 0 files
  tasks/task-worker-reports: 0 files

-rw-rw-r-- 1 admin admin 22143 Feb  2 04:39 tasks/task-system-guide.md
```

---

## CLI Commands Reference

| Command | Purpose |
|---------|---------|
| `git branch --show-current` | Verify current branch |
| `git checkout main` or `git switch main` | Switch to main branch |
| `git add -A && git commit -m "..." && git push` | Safety checkpoint before cleanup |
| `ls -la tasks/` | Verify tasks directory structure |
| `find tasks/ -type f ! -name "task-system-guide.md"` | List files to be removed |
| `rm -f tasks/task-archive/*.md` | Remove files from task-archive/ |
| `rm -f tasks/task-implementation/results/*.json` | Remove result JSON files |
| `rm -f tasks/task-implementation/state/*.json` | Remove state files |
| `rm -f tasks/task-planning/*.md` | Remove planning documents |
| `rm -f tasks/task-specifications/task-*.md` | Remove task specifications |
| `rm -rf tasks/task-worker-reports/*` | Remove worker reports |
| `find tasks/ -mindepth 2 -type f ! -name "task-system-guide.md" -delete` | Clean all (alternative) |

---

## Complete Cleanup Script

**For convenience, here's the complete cleanup sequence:**

```bash
#!/bin/bash
# Task Cleanup Script

echo "Starting task cleanup..."

# Step 1: Safety checkpoint
echo "Step 1: Creating safety checkpoint..."
current_branch=$(git branch --show-current)
if [ "$current_branch" != "main" ]; then
    echo "Currently on '$current_branch', switching to main..."
    git switch main
fi
git add -A
git commit -m "safety: checkpoint before task cleanup

Committing all changes before cleaning up tasks directory."
git push
echo "Safety checkpoint created."

# Show current state
echo "Current files in tasks/:"
find tasks/ -type f ! -name "task-system-guide.md"

# Clean up
rm -f tasks/task-archive/*.md 2>/dev/null
rm -f tasks/task-implementation/results/*.json 2>/dev/null
rm -f tasks/task-implementation/state/*.json 2>/dev/null
rm -f tasks/task-planning/*.md 2>/dev/null
rm -f tasks/task-specifications/task-*.md 2>/dev/null
rm -rf tasks/task-worker-reports/* 2>/dev/null

# Verify
echo "Cleanup complete. Remaining files:"
find tasks/ -type f
```

---

## Completion Checklist

Before finishing, verify:
- [ ] Verified on `main` branch
- [ ] Safety checkpoint created (committed and pushed)
- [ ] Tasks directory exists at project root
- [ ] User confirmed cleanup
- [ ] All files removed from subdirectories
- [ ] All subdirectories still exist
- [ ] task-system-guide.md preserved
- [ ] Verification shows 0 files in each subdirectory

---

## Example Usage

### Scenario: Clean up after task completion

**User says:** "Clean up the tasks directory"

**Workflow:**

```bash
# 1. Safety checkpoint - verify branch and commit
git branch --show-current
# Output: main

git add -A
git commit -m "safety: checkpoint before task cleanup

Committing all changes before cleaning up tasks directory."
git push
# Output: [main <hash>] safety: checkpoint before task cleanup

# 2. Show current state
ls -la tasks/
find tasks/ -type f ! -name "task-system-guide.md"

# Output: Shows 42 task specifications, 2 archived tasks, 1 planning doc, etc.

# 3. Confirm with user
# "This will remove 45 files. Proceed?"

# 4. Execute cleanup
rm -f tasks/task-archive/*.md
rm -f tasks/task-implementation/results/*.json
rm -f tasks/task-implementation/state/*.json
rm -f tasks/task-planning/*.md
rm -f tasks/task-specifications/task-*.md
rm -rf tasks/task-worker-reports/*

# 5. Verify
find tasks/ -type f
# Output: tasks/task-system-guide.md
```

**Inform user:**
```
Task cleanup complete.

Removed 45 files from:
- tasks/task-archive/
- tasks/task-implementation/results/
- tasks/task-implementation/state/
- tasks/task-planning/
- tasks/task-specifications/
- tasks/task-worker-reports/

Preserved:
- task-system-guide.md (documentation)
- All subdirectories (empty, ready for new tasks)
```

---

## Related Skills

- **task-planning**: Generate new task planning documents
- **task-specification-generation**: Create new task specifications
- **task-implementation**: Execute task specifications
- **material-archiver**: Archive completed materials before cleanup

---

## Safety Notes

1. **Always verify** before removing files
2. **Confirm with user** before executing cleanup
3. **Never remove** task-system-guide.md (documentation)
4. **Never remove** the subdirectories themselves
5. **Consider archiving** first if tasks might be needed later
