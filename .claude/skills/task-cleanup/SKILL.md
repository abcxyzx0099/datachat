---
name: task-cleanup
description: "Cleans up the tasks directory by removing all materials (files) while preserving the directory structure. Leaves all subdirectories empty. Cleans both ad-hoc and planned queues, plus the shared results directory. Use when: you need to reset the tasks directory; you want to clear completed tasks and specifications; you need a clean slate for new task planning."
---

# Task Cleanup

Cleans up the `tasks/` directory by removing all files while preserving the directory structure.

**Note:** This cleans both ad-hoc and planned task queues, plus the shared results directory.

---

## Directory Structure

```
tasks/
├── ad-hoc/                              # Ad-hoc task queue
│   ├── staging/                    # Will be emptied
│   ├── pending/                  # Will be emptied (Task Source Directory)
│   ├── completed/                    # Will be emptied
│   ├── failed/                    # Will be emptied
│   ├── results/                     # Will be emptied
│   └── reports/                   # Will be emptied
│
├── planned/                             # Planned task queue
│   ├── staging/                    # Will be emptied
│   ├── pending/                  # Will be emptied (Task Source Directory)
│   ├── completed/                    # Will be emptied
│   ├── failed/                    # Will be emptied
│   ├── planning/                   # Will be emptied
│   ├── results/                     # Will be emptied
│   └── reports/                   # Will be emptied
```

**Note:** `docs/methodology/task-system-guide.md` is documentation and is NOT affected by cleanup.

---

## Official Directories Cleaned

| Directory | Purpose |
|-----------|---------|
| `tasks/ad-hoc/staging/` | Ad-hoc staging area |
| `tasks/ad-hoc/pending/` | Ad-hoc task specifications |
| `tasks/ad-hoc/completed/` | Ad-hoc archived tasks |
| `tasks/ad-hoc/failed/` | Ad-hoc failed tasks |
| `tasks/ad-hoc/results/` | Ad-hoc result JSON files |
| `tasks/ad-hoc/reports/` | Ad-hoc worker reports |
| `tasks/planned/staging/` | Planned staging area |
| `tasks/planned/pending/` | Planned task specifications |
| `tasks/planned/completed/` | Planned archived tasks |
| `tasks/planned/failed/` | Planned failed tasks |
| `tasks/planned/planning/` | Planning documents |
| `tasks/planned/results/` | Planned result JSON files |
| `tasks/planned/reports/` | Planned worker reports |

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
echo "=== Ad-hoc Queue ==="
for dir in tasks/ad-hoc/staging tasks/ad-hoc/pending tasks/ad-hoc/completed tasks/ad-hoc/failed tasks/ad-hoc/results tasks/ad-hoc/reports; do
    echo "$dir: $(ls -1 "$dir" 2>/dev/null | wc -l) files"
done

echo "=== Planned Queue ==="
for dir in tasks/planned/staging tasks/planned/pending tasks/planned/completed tasks/planned/failed tasks/planned/planning tasks/planned/results tasks/planned/reports; do
    echo "$dir: $(ls -1 "$dir" 2>/dev/null | wc -l) files"
done
```

**Confirm with user before proceeding.**

---

## Step 3: Clean Up Ad-hoc Queue

```bash
# Remove ad-hoc staging files
rm -f tasks/ad-hoc/staging/task-*.md 2>/dev/null

# Remove ad-hoc task specifications (Task Source Directory)
rm -f tasks/ad-hoc/pending/task-*.md 2>/dev/null

# Remove ad-hoc archived task specifications
rm -f tasks/ad-hoc/completed/task-*.md 2>/dev/null

# Remove ad-hoc failed task specifications
rm -f tasks/ad-hoc/failed/task-*.md 2>/dev/null

# Remove ad-hoc result JSON files
rm -f tasks/ad-hoc/results/task-*.json 2>/dev/null

# Remove ad-hoc worker reports (detailed subdirectories)
rm -rf tasks/ad-hoc/reports/task-* 2>/dev/null
```

## Step 4: Clean Up Planned Queue

```bash
# Remove planned staging files
rm -f tasks/planned/staging/task-*.md 2>/dev/null

# Remove planned task specifications (Task Source Directory)
rm -f tasks/planned/pending/task-*.md 2>/dev/null

# Remove planned archived task specifications
rm -f tasks/planned/completed/task-*.md 2>/dev/null

# Remove planned failed task specifications
rm -f tasks/planned/failed/task-*.md 2>/dev/null

# Remove planning documents
rm -f tasks/planned/planning/*.md 2>/dev/null

# Remove planned result JSON files
rm -f tasks/planned/results/task-*.json 2>/dev/null

# Remove planned worker reports (detailed subdirectories)
rm -rf tasks/planned/reports/task-* 2>/dev/null
```

**Alternative (single command for all):**
```bash
find tasks/ -mindepth 2 -type f -delete
```

---

## Step 5: Verify Cleanup

```bash
echo "=== Ad-hoc Queue ==="
for dir in tasks/ad-hoc/staging tasks/ad-hoc/pending tasks/ad-hoc/completed tasks/ad-hoc/failed tasks/ad-hoc/results tasks/ad-hoc/reports; do
    count=$(ls -1 "$dir" 2>/dev/null | wc -l)
    echo "$dir: $count files"
done

echo "=== Planned Queue ==="
for dir in tasks/planned/staging tasks/planned/pending tasks/planned/completed tasks/planned/failed tasks/planned/planning tasks/planned/results tasks/planned/reports; do
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
| `rm -f tasks/ad-hoc/staging/task-*.md` | Remove ad-hoc staged files |
| `rm -f tasks/ad-hoc/pending/task-*.md` | Remove ad-hoc task specs |
| `rm -f tasks/ad-hoc/results/task-*.json` | Remove ad-hoc result JSON files |
| `rm -f tasks/planned/staging/task-*.md` | Remove planned staged files |
| `rm -f tasks/planned/pending/task-*.md` | Remove planned task specs |
| `rm -f tasks/planned/results/task-*.json` | Remove planned result JSON files |
| `rm -f tasks/planned/planning/*.md` | Remove planning documents |

---

## Completion Checklist

- [ ] Verified on `main` branch
- [ ] Safety checkpoint created (committed and pushed)
- [ ] Tasks directory exists with both ad-hoc and planned subdirectories
- [ ] User confirmed cleanup
- [ ] Ad-hoc queue files removed (including results)
- [ ] Planned queue files removed (including results)
- [ ] Planning documents removed
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
7. **Both queues are cleaned** - This cleans ad-hoc AND planned queues
8. **Results are per-queue** - Each queue has its own `results/` subdirectory

---

## Related Skills

- **task-init**: Initialize task system with ad-hoc and planned queues
- **task-planning**: Generate new task planning documents
- **task-documents**: Create new task specifications
- **task-monitor**: Execute task specifications
- **material-archiver**: Archive completed materials before cleanup
