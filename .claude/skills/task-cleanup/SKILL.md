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
find tasks/ -mindepth 2 -type f

# 3. Clean all (single command)
find tasks/ -mindepth 2 -type f -delete

# 4. Verify
find tasks/ -mindepth 2 -type f  # Should return nothing
```

---

## Directory Structure

```
tasks/
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
find tasks/ -mindepth 2 -type f

# Count files per directory
echo "=== Ad-hoc ==="
for dir in tasks/ad-hoc/*/; do echo "$dir: $(ls -1 "$dir" 2>/dev/null | wc -l) files"; done

echo "=== Planned ==="
for dir in tasks/planned/*/; do echo "$dir: $(ls -1 "$dir" 2>/dev/null | wc -l) files"; done
```

### 3. Clean All Files

**Single command (recommended):**
```bash
find tasks/ -mindepth 2 -type f -delete
```

**Or by queue (step-by-step):**
```bash
# Ad-hoc queue
rm -f tasks/ad-hoc/staging/task-*.md
rm -f tasks/ad-hoc/pending/task-*.md
rm -f tasks/ad-hoc/completed/task-*.md
rm -f tasks/ad-hoc/failed/task-*.md
rm -f tasks/ad-hoc/results/task-*.json
rm -rf tasks/ad-hoc/reports/task-*

# Planned queue
rm -f tasks/planned/staging/task-*.md
rm -f tasks/planned/pending/task-*.md
rm -f tasks/planned/completed/task-*.md
rm -f tasks/planned/failed/task-*.md
rm -f tasks/planned/planning/*.md
rm -f tasks/planned/results/task-*.json
rm -rf tasks/planned/reports/task-*

# Legacy directories
rm -f tasks/staging/task-*.md
rm -f tasks/pending/task-*.md
rm -f tasks/completed/task-*.md
rm -f tasks/failed/task-*.md
rm -f tasks/planning/*.md
rm -f tasks/results/task-*.json
rm -rf tasks/reports/task-*
```

### 4. Verify Cleanup

```bash
# Should return empty
find tasks/ -mindepth 2 -type f

# Or count files (all should show 0)
for dir in tasks/*/ tasks/*/*/; do
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
| `tasks/ad-hoc/staging/` | `task-*.md` |
| `tasks/ad-hoc/pending/` | `task-*.md` |
| `tasks/ad-hoc/completed/` | `task-*.md` |
| `tasks/ad-hoc/failed/` | `task-*.md` |
| `tasks/ad-hoc/results/` | `task-*.json` |
| `tasks/ad-hoc/reports/` | `task-*/` (subdirectories) |
| `tasks/planned/staging/` | `task-*.md` |
| `tasks/planned/pending/` | `task-*.md` |
| `tasks/planned/completed/` | `task-*.md` |
| `tasks/planned/failed/` | `task-*.md` |
| `tasks/planned/planning/` | `*.md` |
| `tasks/planned/results/` | `task-*.json` |
| `tasks/planned/reports/` | `task-*/` (subdirectories) |
| `tasks/staging/` | `task-*.md` (legacy) |
| `tasks/pending/` | `task-*.md` (legacy) |
| `tasks/completed/` | `task-*.md` (legacy) |
| `tasks/failed/` | `task-*.md` (legacy) |
| `tasks/planning/` | `*.md` (legacy) |
| `tasks/results/` | `task-*.json` (legacy) |
| `tasks/reports/` | `task-*/` (legacy) |

---

## Related Skills

- **task-init**: Initialize task system
- **task-planning**: Generate planning documents
- **task-documents**: Create task specifications
- **task-monitor**: Execute tasks
- **material-archiver**: Archive before cleanup
