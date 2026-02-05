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
├── task-planning/               # Will be emptied
│   └── {descriptive-name}.md
├── task-documents/              # Will be emptied (Task Source Directory)
│   └── task-YYYYMMDD-HHMMSS-{description}.md
├── task-queue/                  # Will be emptied (flat structure)
│   └── task-YYYYMMDD-HHMMSS-{description}.json
├── task-archive/                # Will be emptied
│   └── task-YYYYMMDD-HHMMSS-{description}.md
└── task-reports/                # Will be emptied
    └── task-{timestamp}-{description}/
        ├── workflow-result.json
        ├── audit-report-iteration-*.md
        └── implementation-summary.md
```

**Note:** `docs/methodology/task-system-guide.md` is documentation and is NOT affected by cleanup.

---

## Official Directories Cleaned

| Directory | Purpose |
|-----------|---------|
| `tasks/task-archive/` | Archived task specifications |
| `tasks/task-queue/` | Result JSON files (flat structure) |
| `tasks/task-reports/` | Worker execution reports (detailed) |
| `tasks/task-planning/` | Planning documents |
| `tasks/task-documents/` | Task specifications (Task Source Directory) |

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
find tasks/ -type f

# Count files in each subdirectory
for dir in tasks/task-planning tasks/task-documents tasks/task-queue tasks/task-archive tasks/task-reports; do
    echo "$dir: $(ls -1 "$dir" 2>/dev/null | wc -l) files"
done
```

**Confirm with user before proceeding.**

---

## Step 3: Clean Up Subdirectories

```bash
# Remove planning documents
rm -f tasks/task-planning/*.md 2>/dev/null

# Remove task specifications (Task Source Directory)
rm -f tasks/task-documents/task-*.md 2>/dev/null

# Remove result JSON files (flat structure)
rm -f tasks/task-queue/task-*.json 2>/dev/null

# Remove archived task specifications
rm -f tasks/task-archive/task-*.md 2>/dev/null

# Remove worker reports (detailed subdirectories)
rm -rf tasks/task-reports/task-* 2>/dev/null
```

**Alternative (single command):**
```bash
find tasks/ -mindepth 2 -type f -delete
```

---

## Step 4: Verify Cleanup

```bash
for dir in tasks/task-planning tasks/task-documents tasks/task-queue tasks/task-archive tasks/task-reports; do
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
| `rm -f tasks/task-planning/*.md` | Remove planning documents |
| `rm -f tasks/task-documents/task-*.md` | Remove task specifications |
| `rm -f tasks/task-queue/task-*.json` | Remove result JSON files |
| `rm -f tasks/task-archive/task-*.md` | Remove archived tasks |
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
