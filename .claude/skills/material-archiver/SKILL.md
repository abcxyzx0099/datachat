---
name: material-archiver
description: Generic archiver for completed materials. Works with development waves, documentation, design docs, or any directory that needs archiving. Moves entire directories to timestamped archive locations in history/.
---

# Generic Archiver

Archive any completed materials to `history/Archive-{description}-{timestamp}/`.

---

## Overview

Archive completed directories to organized timestamped locations. This keeps your workspace clean while preserving complete history.

**Archive Path:** `history/Archive-{description}-{timestamp}/`

**Source:** Any directory (development waves, docs, designs, etc.)

**Note:** The `history/` directory at the repository root serves as a central archive location for all historical materials.

---

## Step 1: Identify What to Archive

**First, understand the source location:**

Ask the user what they want to archive. Common patterns:
- Development wave: `development/{wave-name}/`
- Documentation directory: `docs/{directory-name}/`
- Single documentation file: `docs/{category}/{file}.md`
- Any other directory or file

**If archiving a development wave**, verify completion:

```bash
cat "development/{wave-name}/development-progress.md"
```

**Check:**
- All phases show **Overall: ✅ Complete**
- No 🔄 In Progress tasks
- No ⚠️ Blocked tasks

**If NOT complete (development waves only):**
- Ask user: "Wave is not complete. Phase X shows status Y. Archive anyway?"
- Only proceed if user confirms

**For non-development items** (docs, designs, etc.), skip completion check - just confirm with user before proceeding.

---

## Step 2: List Contents to Archive

**For directories:**
```bash
ls -la "{source-path}/"
```

**For single files:**
```bash
ls -la "{source-file}"
```

**Identify what will be archived:**

| Content Type | Patterns |
|--------------|----------|
| Development waves | Phase documents (`phase-*.md`), conventions, progress files |
| Documentation | Design docs, specifications, guides |
| Single files | Individual `.md` files or other documents |

**Confirm contents with user before proceeding.**

---

## Step 3: Determine Archive Name

The archive name consists of two parts: `Archive-{description}-{timestamp}`

### 3.1 Determine Description (Intelligent)

The skill intelligently determines a descriptive name. Try these methods in order:

**Method 1: Read document metadata (for .md files)**
```bash
# Read file for title
head -20 "{source-file}"
# Look for: # Title, # {Name}, or similar headings
```

**Method 2: Read progress file (for development waves)**
```bash
cat "development/{wave-name}/development-progress.md"
# Look for wave title or heading
```

**Method 3: Convert name to readable format**
```bash
# Convert kebab-case to Title Case
{wave-name}              → {Wave-Name}
```

**Description examples:**
| Source | Description |
|--------|-------------|
| `development/{wave-name}/` | `{Wave-Name}` |
| `docs/{directory}/` | `{Directory-Name}` |
| `docs/{category}/{file}.md` | `{File-Name}` |

**Ask user** to confirm or modify the description before proceeding.

### 3.2 Generate Timestamp

**Format:** `YYYYMMDD-HHMMSS`

**Example:**
```bash
# Get current timestamp
date +"%Y%m%d-%H%M%S"
# Output: 20260121-143052
```

### 3.3 Final Archive Name

**Format:** `history/Archive-{description}-{timestamp}/`

**Examples:**
```bash
history/Archive-{Wave-Name}-{timestamp}/
history/Archive-{Directory-Name}-{timestamp}/
history/Archive-{File-Name}-{timestamp}/
```

---

## Step 4: Create Archive Directory

**Ensure history directory exists:**
```bash
mkdir -p history
```

**Create the archive directory:**
```bash
mkdir -p "history/Archive-{description}-{timestamp}"
```

---

## Step 5: Move Source to Archive

**For directories (move entire directory):**
```bash
mv "{source-path}" "history/Archive-{description}-{timestamp}/"
```

**For single files (move into archive directory):**
```bash
mv "{source-file}" "history/Archive-{description}-{timestamp}/"
```

**Important:**
- For directories: The entire subdirectory is moved, keeping all files together
- For single files: First create the archive directory, then move the file into it

---

## Step 6: Verify Archive

**Check archive contents:**
```bash
ls -la "history/Archive-{description}-{timestamp}/"
```

**Expected contents:**
- All files from the original directory or the archived single file

**Verify source was removed:**
```bash
ls -la "{source-path}"
```
The archived path should no longer exist (file not found error confirms successful move).

---

## Step 7: Create Archive Summary (Optional)

Create a summary file in the archive directory:

**File:** `history/Archive-{description}-{timestamp}/README.md`

**Contents (for development waves):**
```markdown
# {Wave Name} - Development Archive

**Archived:** {YYYY-MM-DD}
**Status:** Complete

## Phases

| Phase | Name | Status |
|-------|------|--------|
| ... | ... | ... |

## Contents

- Phase documents: {count}
- Conventions: {file names}
- Progress: {file names}
```

**Contents (for documents/designs/plans):**
```markdown
# {Document Name} - Archive

**Archived:** {YYYY-MM-DD}

## Original Location

`{original-source-path}`

## Contents

- Files: {list of archived files}
```

---

## Step 8: Commit Archive Changes

```bash
git add -A
git commit -m "docs: archive {source-name} to {archive-dir}"
git push
```

---

## Completion Checklist

Before finishing, verify:
- [ ] Source identified correctly (directory or file)
- [ ] For development waves: Project is complete (all phases ✅)
- [ ] All related files moved
- [ ] Archive directory created with correct name
- [ ] No unrelated files moved
- [ ] Archive verified with `ls`
- [ ] Git commit created (optional)

---

## Example Usage

### Example 1: Archive Development Wave

**Input:** User says "Archive the {wave-name} wave"

**Steps:**
1. Identify source: `development/{wave-name}/`
2. Read progress file → verify all ✅
3. Determine description: "{Wave-Name}" (from subdirectory name)
4. Get timestamp: `date +"%Y%m%d-%H%M%S"`
5. Create archive: `mv "development/{wave-name}" "history/Archive-{Wave-Name}-{timestamp}/"`
6. Verify with `ls`
7. Commit changes

### Example 2: Archive Documentation Directory

**Input:** User says "Archive the {directory} docs"

**Steps:**
1. Identify source: `docs/{directory}/`
2. Determine description: "{Directory-Name}" (from directory name)
3. Get timestamp: `date +"%Y%m%d-%H%M%S"`
4. Create archive: `mv "docs/{directory}" "history/Archive-{Directory-Name}-{timestamp}/"`
5. Verify with `ls`
6. Commit changes

### Incomplete Project Archive

**Input:** User says "Archive current wave"

**Steps:**
1. Read progress → Phase shows 🔄 In Progress
2. Ask: "Phase is In Progress. Archive anyway?"
3. If yes → proceed with archive
4. If no → cancel, suggest completing work first

---

## Archive Structure

```
# Active work areas
{workspace-root}/
├── development/                          (active waves)
│   └── {wave-name}/                      (active wave)
│       ├── phase-*.md
│       ├── development-conventions.md
│       └── development-progress.md
└── docs/                                 (active documentation)
    └── {directory-name}/
        └── *.md

# Archived materials (flat structure)
history/
├── Archive-{Description-1}-{timestamp-1}/
├── Archive-{Description-2}-{timestamp-2}/
└── ...
```

---

## Quick Reference

### Common Files by Type

| Type | Files |
|------|-------|
| Development waves | `development-progress.md`, `phase-*.md`, `*-conventions.md` |
| Documentation | `*.md` files in various `docs/` subdirectories |

### Commands

| Command | Purpose |
|---------|---------|
| `ls -la {source}` | List contents before archive |
| `date +"%Y%m%d-%H%M%S"` | Generate timestamp |
| `mkdir -p "history/Archive-{desc}-{timestamp}"` | Create archive directory |
| `mv "{source}" "history/Archive-{desc}-{timestamp}/"` | Move to archive |
| `ls -la "history/Archive-{desc}-{timestamp}/"` | Verify archive contents |
