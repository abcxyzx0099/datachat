---
name: task-cleanup
description: "Cleans up the tasks directory by removing all materials (files) while preserving the directory structure. Leaves all subdirectories empty. Cleans both ad-hoc and planned queues. Use when: you need to reset the tasks directory; you want to clear completed tasks and specifications; you need a clean slate for new task planning."
---

# Task Cleanup

Cleans up the `tasks/` directory by removing all files while preserving the directory structure.

**Note:** This cleans both ad-hoc and planned task queues.

---

## Directory Structure

```
tasks/
├── ad-hoc/                              # Ad-hoc task queue
│   ├── task-staging/                    # Will be emptied
│   ├── task-documents/                  # Will be emptied (Task Source Directory)
│   ├── task-archive/                    # Will be emptied
│   ├── task-failed/                    # Will be emptied
│   ├── task-queue/                     # Will be emptied (flat structure)
│   └── task-reports/                   # Will be emptied
│
├── planned/                             # Planned task queue
│   ├── task-staging/                    # Will be emptied
│   ├── task-documents/                  # Will be emptied (Task Source Directory)
│   ├── task-archive/                    # Will be emptied
│   ├── task-failed/                    # Will be emptied
│   ├── task-queue/                     # Will be emptied (flat structure)
│   └── task-reports/                   # Will be emptied
│
└── task-planning/                       # Will be emptied
    └── {descriptive-name}.md
```

**Note:** `docs/methodology/task-system-guide.md` is documentation and is NOT affected by cleanup.

---

## Official Directories Cleaned

| Directory | Purpose |
|-----------|---------|
| `tasks/ad-hoc/task-staging/` | Ad-hoc staging area |
| `tasks/ad-hoc/task-documents/` | Ad-hoc task specifications |
| `tasks/ad-hoc/task-archive/` | Ad-hoc archived tasks |
| `tasks/ad-hoc/task-failed/` | Ad-hoc failed tasks |
| `tasks/ad-hoc/task-queue/` | Ad-hoc result JSON files |
| `tasks/ad-hoc/task-reports/` | Ad-hoc worker reports |
| `tasks/planned/task-staging/` | Planned staging area |
| `tasks/planned/task-documents/` | Planned task specifications |
| `tasks/planned/task-archive/` | Planned archived tasks |
| `tasks/planned/task-failed/` | Planned failed tasks |
| `tasks/planned/task-queue/` | Planned result JSON files |
| `tasks/planned/task-reports/` | Planned worker reports |
| `tasks/task-planning/` | Planning documents |

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
for dir in tasks/ad-hoc/task-staging tasks/ad-hoc/task-documents tasks/ad-hoc/task-queue tasks/ad-hoc/task-archive tasks/ad-hoc/task-failed tasks/ad-hoc/task-reports; do
    echo "$dir: $(ls -1 "$dir" 2>/dev/null | wc -l) files"
done

echo "=== Planned Queue ==="
for dir in tasks/planned/task-staging tasks/planned/task-documents tasks/planned/task-queue tasks/planned/task-archive tasks/planned/task-failed tasks/planned/task-reports; do
    echo "$dir: $(ls -1 "$dir" 2>/dev/null | wc -l) files"
done

echo "=== Planning ==="
echo "tasks/task-planning/: $(ls -1 tasks/task-planning/ 2>/dev/null | wc -l) files"
```

**Confirm with user before proceeding.**

---

## Step 3: Clean Up Ad-hoc Queue

```bash
# Remove ad-hoc staging files
rm -f tasks/ad-hoc/task-staging/task-*.md 2>/dev/null

# Remove ad-hoc task specifications (Task Source Directory)
rm -f tasks/ad-hoc/task-documents/task-*.md 2>/dev/null

# Remove ad-hoc result JSON files (flat structure)
rm -f tasks/ad-hoc/task-queue/task-*.json 2>/dev/null

# Remove ad-hoc archived task specifications
rm -f tasks/ad-hoc/task-archive/task-*.md 2>/dev/null

# Remove ad-hoc failed task specifications
rm -f tasks/ad-hoc/task-failed/task-*.md 2>/dev/null

# Remove ad-hoc worker reports (detailed subdirectories)
rm -rf tasks/ad-hoc/task-reports/task-* 2>/dev/null
```

## Step 4: Clean Up Planned Queue

```bash
# Remove planned staging files
rm -f tasks/planned/task-staging/task-*.md 2>/dev/null

# Remove planned task specifications (Task Source Directory)
rm -f tasks/planned/task-documents/task-*.md 2>/dev/null

# Remove planned result JSON files (flat structure)
rm -f tasks/planned/task-queue/task-*.json 2>/dev/null

# Remove planned archived task specifications
rm -f tasks/planned/task-archive/task-*.md 2>/dev/null

# Remove planned failed task specifications
rm -f tasks/planned/task-failed/task-*.md 2>/dev/null

# Remove planned worker reports (detailed subdirectories)
rm -rf tasks/planned/task-reports/task-* 2>/dev/null
```

## Step 5: Clean Up Planning Documents

```bash
# Remove planning documents
rm -f tasks/task-planning/*.md 2>/dev/null
```

**Alternative (single command for all):**
```bash
find tasks/ -mindepth 2 -type f -delete
```

---

## Step 6: Verify Cleanup

```bash
echo "=== Ad-hoc Queue ==="
for dir in tasks/ad-hoc/task-staging tasks/ad-hoc/task-documents tasks/ad-hoc/task-queue tasks/ad-hoc/task-archive tasks/ad-hoc/task-failed tasks/ad-hoc/task-reports; do
    count=$(ls -1 "$dir" 2>/dev/null | wc -l)
    echo "$dir: $count files"
done

echo "=== Planned Queue ==="
for dir in tasks/planned/task-staging tasks/planned/task-documents tasks/planned/task-queue tasks/planned/task-archive tasks/planned/task-failed tasks/planned/task-reports; do
    count=$(ls -1 "$dir" 2>/dev/null | wc -l)
    echo "$dir: $count files"
done

echo "=== Planning ==="
echo "tasks/task-planning/: $(ls -1 tasks/task-planning/ 2>/dev/null | wc -l) files"
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
| `rm -f tasks/ad-hoc/task-staging/task-*.md` | Remove ad-hoc staged files |
| `rm -f tasks/ad-hoc/task-documents/task-*.md` | Remove ad-hoc task specs |
| `rm -f tasks/ad-hoc/task-queue/task-*.json` | Remove ad-hoc result files |
| `rm -f tasks/planned/task-staging/task-*.md` | Remove planned staged files |
| `rm -f tasks/planned/task-documents/task-*.md` | Remove planned task specs |
| `rm -f tasks/planned/task-queue/task-*.json` | Remove planned result files |
| `rm -f tasks/task-planning/*.md` | Remove planning documents |

---

## Completion Checklist

- [ ] Verified on `main` branch
- [ ] Safety checkpoint created (committed and pushed)
- [ ] Tasks directory exists with both ad-hoc and planned subdirectories
- [ ] User confirmed cleanup
- [ ] Ad-hoc queue files removed
- [ ] Planned queue files removed
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

---

## Related Skills

- **task-init**: Initialize task system with ad-hoc and planned queues
- **task-planning**: Generate new task planning documents
- **task-documents**: Create new task specifications
- **task-queue**: Execute task specifications
- **material-archiver**: Archive completed materials before cleanup
