---
name: task-cleanup
description: "Cleans up the tasks directory by removing all files while preserving the directory structure. Cleans both ad-hoc and planned queues, plus legacy directories. Use when: you need a clean slate for new task planning."
---

# Task Cleanup

Removes all task files while preserving directory structure. Cleans ad-hoc queue, planned queue, and legacy directories.

---

## Quick Start

```bash
# 1. Safety checkpoint (commit & push changes first)
git add -A && git commit -m "safety: before task cleanup" && git push

# 2. Preview what will be removed
find task-monitor/ -mindepth 2 -type f

# 3. Clean all (single command)
find task-monitor/ -mindepth 2 -type f -delete

# 4. Verify
find task-monitor/ -mindepth 2 -type f  # Should return nothing
```

---

## Directory Structure

```
task-monitor/
├── ad-hoc/                    # Ad-hoc queue
│   ├── staging/              → Emptied
│   ├── pending/              → Emptied
│   ├── completed/            → Emptied
│   ├── failed/               → Emptied
│   ├── results/              → Emptied
│   ├── reports/              → Emptied
│   └── planning/             → Emptied
│
├── planned/                   # Planned queue
│   ├── staging/              → Emptied
│   ├── pending/              → Emptied
│   ├── completed/            → Emptied
│   ├── failed/               → Emptied
│   ├── results/              → Emptied
│   ├── reports/              → Emptied
│   └── planning/             → Emptied
│
└── [Legacy Directories]      # Old structure (also cleaned)
    ├── staging/              → Emptied
    ├── pending/              → Emptied
    ├── completed/            → Emptied
    ├── failed/               → Emptied
    ├── planning/             → Emptied
    ├── results/              → Emptied
    └── reports/              → Emptied
```

---

## Detailed Steps

### 1. Safety Checkpoint

```bash
# Verify on main branch
git branch --show-current
git switch main  # If not on main

# Commit and push all changes
git add -A
git commit -m "safety: checkpoint before task cleanup"
git push
```

### 2. Preview Files

```bash
# List all files to be removed
find task-monitor/ -mindepth 2 -type f

# Count files per directory
echo "=== Ad-hoc ==="
for dir in task-monitor/ad-hoc/*/; do echo "$dir: $(ls -1 "$dir" 2>/dev/null | wc -l) files"; done

echo "=== Planned ==="
for dir in task-monitor/planned/*/; do echo "$dir: $(ls -1 "$dir" 2>/dev/null | wc -l) files"; done
```

### 3. Clean All Files

**Single command (recommended):**
```bash
find task-monitor/ -mindepth 2 -type f -delete
```

**Or by queue (step-by-step):**
```bash
# Ad-hoc queue
rm -f task-monitor/ad-hoc/staging/task-*.md
rm -f task-monitor/ad-hoc/pending/task-*.md
rm -f task-monitor/ad-hoc/completed/task-*.md
rm -f task-monitor/ad-hoc/failed/task-*.md
rm -f task-monitor/ad-hoc/results/task-*.json
rm -rf task-monitor/ad-hoc/reports/task-*

# Planned queue
rm -f task-monitor/planned/staging/task-*.md
rm -f task-monitor/planned/pending/task-*.md
rm -f task-monitor/planned/completed/task-*.md
rm -f task-monitor/planned/failed/task-*.md
rm -f task-monitor/planned/planning/*.md
rm -f task-monitor/planned/results/task-*.json
rm -rf task-monitor/planned/reports/task-*

# Legacy directories
rm -f task-monitor/staging/task-*.md
rm -f task-monitor/pending/task-*.md
rm -f task-monitor/completed/task-*.md
rm -f task-monitor/failed/task-*.md
rm -f task-monitor/planning/*.md
rm -f task-monitor/results/task-*.json
rm -rf task-monitor/reports/task-*
```

### 4. Verify Cleanup

```bash
# Should return empty
find task-monitor/ -mindepth 2 -type f

# Or count files (all should show 0)
for dir in task-monitor/*/ task-monitor/*/*/; do
    [ -d "$dir" ] && echo "$dir: $(ls -1 "$dir" 2>/dev/null | wc -l) files"
done
```

---

## Safety Notes

| Rule | Description |
|------|-------------|
| **1. Branch** | Always verify on `main` branch first |
| **2. Checkpoint** | Commit and push all changes before cleanup |
| **3. Confirm** | Show user what will be removed before proceeding |
| **4. Preserve** | Never remove subdirectories themselves, only files |
| **5. Archive** | Consider archiving first if tasks might be needed later |

---

## What Gets Cleaned

| Directory | Files Removed |
|-----------|---------------|
| `task-monitor/ad-hoc/staging/` | `task-*.md` |
| `task-monitor/ad-hoc/pending/` | `task-*.md` |
| `task-monitor/ad-hoc/completed/` | `task-*.md` |
| `task-monitor/ad-hoc/failed/` | `task-*.md` |
| `task-monitor/ad-hoc/results/` | `task-*.json` |
| `task-monitor/ad-hoc/reports/` | `task-*/` (subdirectories) |
| `task-monitor/planned/staging/` | `task-*.md` |
| `task-monitor/planned/pending/` | `task-*.md` |
| `task-monitor/planned/completed/` | `task-*.md` |
| `task-monitor/planned/failed/` | `task-*.md` |
| `task-monitor/planned/planning/` | `*.md` |
| `task-monitor/planned/results/` | `task-*.json` |
| `task-monitor/planned/reports/` | `task-*/` (subdirectories) |
| `task-monitor/staging/` | `task-*.md` (legacy) |
| `task-monitor/pending/` | `task-*.md` (legacy) |
| `task-monitor/completed/` | `task-*.md` (legacy) |
| `task-monitor/failed/` | `task-*.md` (legacy) |
| `task-monitor/planning/` | `*.md` (legacy) |
| `task-monitor/results/` | `task-*.json` (legacy) |
| `task-monitor/reports/` | `task-*/` (legacy) |

---

## Related Skills

- **task-init**: Initialize task system
- **task-planning**: Generate planning documents
- **task-documents**: Create task specifications
- **task-monitor**: Execute tasks
- **material-archiver**: Archive before cleanup
