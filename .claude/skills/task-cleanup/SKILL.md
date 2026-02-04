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
├── task-queue/                  # Will be emptied (flat structure)
│   ├── task-*.json              # Result JSON files
│   └── state/                   # Queue state files
├── task-planning/               # Will be emptied
├── task-documents/              # Will be emptied
└── task-reports/                # Will be emptied
    └── task-*/
```

**Note:** `docs/methodology/task-system-guide.md` is documentation and is NOT affected by cleanup.

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
for dir in tasks/task-archive tasks/task-queue/results tasks/task-queue/state tasks/task-planning tasks/task-documents tasks/task-reports; do
    echo "$dir: $(ls -1 "$dir" 2>/dev/null | wc -l) files"
done
```

**Confirm with user before proceeding.**

---

## Step 3: Clean Up Subdirectories

```bash
rm -f tasks/task-archive/*.md 2>/dev/null
rm -f tasks/task-queue/results/*.json 2>/dev/null
rm -f tasks/task-queue/state/*.json 2>/dev/null
rm -f tasks/task-planning/*.md 2>/dev/null
rm -f tasks/task-documents/task-*.md 2>/dev/null
rm -rf tasks/task-reports/* 2>/dev/null
```

**Alternative (single command):**
```bash
find tasks/ -mindepth 2 -type f ! -name "task-system-guide.md" -delete
```

---

## Step 4: Verify Cleanup

```bash
for dir in tasks/task-archive tasks/task-queue/results tasks/task-queue/state tasks/task-planning tasks/task-documents tasks/task-reports; do
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
| `find tasks/ -mindepth 2 -type f` | List files to remove |
| `rm -f tasks/task-archive/*.md` | Remove archived tasks |
| `rm -f tasks/task-queue/task-*.json` | Remove result files |
| `rm -f tasks/task-queue/state/*.json` | Remove state files |
| `rm -f tasks/task-planning/*.md` | Remove planning docs |
| `rm -f tasks/task-documents/task-*.md` | Remove specifications |
| `rm -rf tasks/task-reports/task-*` | Remove worker reports |

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
5. **Documentation is preserved** - `docs/methodology/task-system-guide.md` is NOT affected
6. **Consider archiving** first if tasks might be needed later

---

## Related Skills

- **task-planning**: Generate new task planning documents
- **task-documents**: Create new task specifications
- **task-queue**: Execute task specifications
- **material-archiver**: Archive completed materials before cleanup
