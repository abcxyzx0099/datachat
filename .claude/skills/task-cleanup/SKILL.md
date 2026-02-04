---
name: task-cleanup
description: "Cleans up the tasks directory by removing all materials (files) while preserving the directory structure. Leaves all subdirectories empty. Use when: you need to reset the tasks directory; you want to clear completed tasks and specifications; you need a clean slate for new task planning."
---

# Task Cleanup

Cleans up the `tasks/` directory by removing all files while preserving the directory structure.

---

## Directory Structure

```
tasks/
├── task-archive/                # Will be emptied
├── task-management/
│   ├── logs/                    # Will be emptied
│   ├── results/                 # Will be emptied
│   └── state/                   # Will be emptied
├── task-planning/               # Will be emptied
├── task-specifications/         # Will be emptied
├── task-worker-reports/         # Will be emptied
└── task-system-guide.md         # PRESERVED
```

---

## Step 1: Safety Checkpoint

**CRITICAL: Always create a safety checkpoint before cleanup.**

```bash
# Verify on main branch (switch if needed)
git branch --show-current
git switch main  # Only if not on main

# Commit and push all changes
git add -A
git commit -m "safety: checkpoint before task cleanup

Committing all changes before cleaning up tasks directory."
git push
```

---

## Step 2: Show Current Contents

```bash
# Show what will be removed
find tasks/ -type f ! -name "task-system-guide.md"

# Count files in each subdirectory
for dir in tasks/task-archive tasks/task-management/results tasks/task-management/state tasks/task-planning tasks/task-specifications tasks/task-worker-reports; do
    echo "$dir: $(ls -1 "$dir" 2>/dev/null | wc -l) files"
done
```

**Confirm with user before proceeding.**

---

## Step 3: Clean Up Subdirectories

```bash
rm -f tasks/task-archive/*.md 2>/dev/null
rm -f tasks/task-management/results/*.json 2>/dev/null
rm -f tasks/task-management/state/*.json 2>/dev/null
rm -f tasks/task-planning/*.md 2>/dev/null
rm -f tasks/task-specifications/task-*.md 2>/dev/null
rm -rf tasks/task-worker-reports/* 2>/dev/null
```

**Alternative (single command):**
```bash
find tasks/ -mindepth 2 -type f ! -name "task-system-guide.md" -delete
```

---

## Step 4: Verify Cleanup

```bash
for dir in tasks/task-archive tasks/task-management/results tasks/task-management/state tasks/task-planning tasks/task-specifications tasks/task-worker-reports; do
    count=$(ls -1 "$dir" 2>/dev/null | wc -l)
    echo "$dir: $count files"
done
```

**Expected:** All directories show 0 files.

---

## CLI Commands Reference

| Command | Purpose |
|---------|---------|
| `git branch --show-current` | Verify current branch |
| `git switch main` | Switch to main branch |
| `git add -A && git commit && git push` | Safety checkpoint |
| `find tasks/ -type f ! -name "task-system-guide.md"` | List files to remove |
| `rm -f tasks/task-archive/*.md` | Remove archived tasks |
| `rm -f tasks/task-management/results/*.json` | Remove result files |
| `rm -f tasks/task-management/state/*.json` | Remove state files |
| `rm -f tasks/task-planning/*.md` | Remove planning docs |
| `rm -f tasks/task-specifications/task-*.md` | Remove specifications |
| `rm -rf tasks/task-worker-reports/*` | Remove worker reports |

---

## Completion Checklist

- [ ] Verified on `main` branch
- [ ] Safety checkpoint created (committed and pushed)
- [ ] Tasks directory exists
- [ ] User confirmed cleanup
- [ ] All files removed from subdirectories
- [ ] All subdirectories still exist
- [ ] Verification shows 0 files in each subdirectory

---

## Safety Notes

1. **Always verify** on `main` branch before starting
2. **Create safety checkpoint** - commit and push before cleanup
3. **Confirm with user** before executing cleanup
4. **Never remove** subdirectories themselves
5. **Never remove** task-system-guide.md
6. **Consider archiving** first if tasks might be needed later

---

## Related Skills

- **task-planning**: Generate new task planning documents
- **task-specification-generation**: Create new task specifications
- **task-management**: Execute task specifications
- **material-archiver**: Archive completed materials before cleanup
