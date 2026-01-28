# Task Document Template

Use this template when creating task documents for delegation.

## Key Principle: Two-Level Investigation

```
┌─────────────────────────────────────────────────────────────────┐
│                     Main Agent (Task Writer)                      │
│  Purpose: Understand holistic context, scope, direction          │
│  Output: Task document with requirements, guidance              │
└──────────────────────────────┬──────────────────────────────────┘
                               │ Task Document (Requirements + Direction)
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Worker Agent (Implementer)                    │
│  Purpose: Deep investigation, cover all files, implement         │
│  Output: Complete implementation with all details               │
└─────────────────────────────────────────────────────────────────┘
```

**Balance**: Main Agent provides direction, Worker Agent investigates thoroughly.

---

## Phase 1: Main Agent Investigation (Holistic Understanding)

**Goal**: Understand the big picture, NOT every detail.

### Investigation Checklist

- [ ] **Understand the Problem**: What is being solved? Why?
- [ ] **Identify Scope**: Which directories/modules are affected?
- [ ] **Find Patterns**: What are the current conventions?
- [ ] **Note Dependencies**: What depends on what?
- [ ] **Check Documentation**: Are there relevant docs, architecture decisions?
- [ ] **Locate Tests**: What test coverage exists?

### Investigation Commands

```bash
# Find affected directories
find . -type d -name "core" -o -name "computation"

# Find relevant files
grep -r "from.*core import" --include="*.py" .

# Check for tests
find . -path "*/tests/*" -name "*.py"

# Look for documentation
find docs -name "*.md" | grep -E "(core|module|architecture)"
```

### What Main Agent Learns

| Category | Output | Example |
|----------|--------|---------|
| **Scope** | Directories affected | `dflib/core/`, `dflib/computation/` |
| **Patterns** | Current conventions | "Uses pyreadstat for SPSS files" |
| **Dependencies** | What depends on what | "computation modules depend on core/io" |
| **Tests** | Test location | `dflib/tests/test_io.py` |
| **Risks** | Potential issues | "Breaking change: imports need update" |

---

## Phase 2: Task Document Structure

### Balance: Direction, Not Micromanagement

```markdown
# Task Document

## Objective
[Clear statement of what needs to be accomplished]

## Context
[Background - why this task exists, what problem it solves]

## Current Understanding
[What Main Agent discovered during investigation]
- Scope: [Directories/modules affected]
- Current patterns: [Conventions in use]
- Dependencies: [What depends on what]
- Risks: [Potential issues to watch]

## Requirements
1. [High-level requirement - WHAT needs to be done]
2. [Another requirement]
3. [Continue for all requirements]

## Worker Investigation Instructions

[CRITICAL: Explicitly ask Worker to do their own deep investigation]

### Step 1: Git Backup (MANDATORY)
Before making ANY changes, you MUST create a Git backup:
```bash
# Check git status
git status

# Stage all current changes (if any)
git add -A

# Create backup commit on current branch
git commit -m "backup: snapshot before task execution

Task: [Brief task description from above]
Timestamp: $(date -Iseconds)
Revert with: git reset --hard HEAD~1"

# Verify backup
git log -1 --oneline
echo "✅ Backup commit created. Revert with: git reset --hard HEAD~1"
```

### Step 2: Deep Investigation
- Investigate ALL files in [directories]
- Find ALL imports/references to [modules]
- Understand current patterns before making changes
- Identify ALL edge cases and dependencies
- Run tests to verify baseline

## Constraints
- [Technical limitations - MUST follow]
- [Style guidelines - MUST follow]
- [Compatibility requirements - MUST maintain]

## Success Criteria
- [ ] [Measurable outcome 1]
- [ ] [Measurable outcome 2]
- [ ] [Measurable outcome 3]
```

---

## Phase 3: Good vs Bad Task Documents

### BAD: Too Specific (Micromanagement)

```markdown
## Requirements
1. Update line 5 of pandas_analyzer.py
2. Update line 8 of pandas_analyzer.py
3. Update line 12 of crosstab_analyzer.py
```

**Problems:**
- Brittle (line numbers change)
- Might miss files
- Worker doesn't investigate thoroughly
- Assumes Main Agent knows every detail

### BAD: Too Vague (No Direction)

```markdown
## Requirements
1. Update the modules
2. Fix the imports
3. Update tests
```

**Problems:**
- No scope (which modules?)
- No direction (what kind of updates?)
- Worker doesn't know where to start

### GOOD: Balanced (Direction + Worker Investigation)

```markdown
## Context
Need to separate SPSS file I/O from metadata enrichment.
Currently, core/io and core/metadata have overlapping responsibilities.

## Current Understanding
From investigation:
- Scope: dflib/core/, dflib/computation/, web/backend/
- 5 files import from core/io (frequency, descriptive, crosstab, spss_tools, services)
- Current pattern: Uses SharedDataLoader for loading + metadata
- Risk: Breaking change - all imports need update

## Requirements
1. Create new module for SPSS file loading (pyreadstat wrapper, no business logic)
2. Create/update module for metadata enrichment (derives info, doesn't load files)
3. Update ALL imports across the codebase to use new modules
4. Maintain backward compatibility

## Worker Investigation Instructions

[CRITICAL - You must do your own deep investigation]

### Step 1: Git Backup (MANDATORY)
Before making ANY changes, you MUST create a Git backup:
```bash
# Check git status
git status

# Stage all current changes (if any)
git add -A

# Create backup commit on current branch
git commit -m "backup: snapshot before task execution

Task: [Brief task description from above]
Timestamp: $(date -Iseconds)
Revert with: git reset --hard HEAD~1"

# Verify backup
git log -1 --oneline
echo "✅ Backup commit created. Revert with: git reset --hard HEAD~1"
```

### Step 2: Deep Investigation
Before implementing, THOROUGHLY investigate:
1. Find ALL files importing from dflib.core.io or dflib.core.metadata
   - Use: grep -r "from dflib.core" --include="*.py"
   - Use: grep -r "import.*core" --include="*.py"

2. For each file found, understand:
   - What functions/classes are used from core modules?
   - How will the API change affect this file?
   - Are there edge cases to handle?

3. Check test coverage:
   - What tests exist for core modules?
   - What tests need updating after changes?

4. Verify understanding:
   - Can you map out the dependency graph?
   - Do you know which files will break without backward compatibility?

## Constraints
- spss_loader: Only pyreadstat wrapper, NO processing logic
- variable_manager: Only metadata enrichment, NO file loading
- Maintain backward compatibility
- All tests must pass

## Success Criteria
- [ ] New modules created with correct responsibilities
- [ ] ALL imports updated (no old references remain)
- [ ] Backward compatibility maintained
- [ ] All tests pass
- [ ] No circular imports
```

**Why This Works:**
- Main Agent: Provides scope, direction, requirements
- Worker Agent: Does deep investigation, finds all files, handles details

---

## Phase 4: Worker Agent Responsibilities

The task document must explicitly state Worker's investigation duties:

### Worker Investigation Template

```markdown
## Worker Investigation Instructions

You MUST do your own deep investigation before implementing:

### Step 1: Git Backup (MANDATORY)
Before making ANY changes, you MUST create a Git backup:
```bash
# Check git status
git status

# Stage all current changes (if any)
git add -A

# Create backup commit on current branch
git commit -m "backup: snapshot before task execution

Task: [Brief task description from above]
Timestamp: $(date -Iseconds)
Revert with: git reset --hard HEAD~1"

# Verify backup
git log -1 --oneline
echo "✅ Backup commit created. Revert with: git reset --hard HEAD~1"
```

### Step 2: Deep Investigation
You MUST do your own deep investigation before implementing:

1. **Find ALL affected files**
   - Search for ALL imports/references to [modules]
   - Don't assume the list is complete
   - Use grep/find to comprehensively search

2. **Understand current implementation**
   - Read the code you'll be changing
   - Understand patterns and conventions
   - Identify edge cases

3. **Map dependencies**
   - What depends on what?
   - What breaks if you change X?
   - Are there circular dependencies?

4. **Check test coverage**
   - What tests exist?
   - What will break?
   - What new tests are needed?

5. **Verify understanding**
   - Can you explain the current architecture?
   - Do you know what needs to change?
   - Can you identify all risks?

ONLY after thorough investigation, implement the requirements.
```

---

## Quick Reference: Task Document Quality

| Quality | Characteristics | Result |
|---------|----------------|--------|
| **Poor** | Too vague, no direction | Worker confused, incomplete |
| **Fair** | Some direction, no investigation request | Worker may miss things |
| **Good** | Clear direction + worker investigation request | Worker covers all bases |
| **Excellent** | Holistic context + clear scope + explicit investigation | Thorough, reliable results |

**Target**: **Good to Excellent** - Provide direction, trust Worker to investigate thoroughly.

---

## Example: Balanced Task Document

```markdown
# Task: Reorganize dflib Core Modules

## Objective
Separate SPSS file I/O from metadata enrichment for clearer module responsibilities.

## Context
Current issue: core/io and core/metadata have overlapping responsibilities.
- Function names confusing (get_all_variables_info in both)
- Unclear separation of concerns
- Difficult to maintain

## Current Understanding (from Main Agent investigation)

**Scope:**
- Directories: dflib/core/, dflib/computation/, web/backend/
- Approximately 5-10 files import from core/io

**Current Pattern:**
- Uses pyreadstat for SPSS file loading
- SharedDataLoader provides both file I/O and metadata extraction
- computation modules import from core/io

**Risks:**
- Breaking change: imports need update
- Backward compatibility needed
- Tests may need updating

## Requirements

1. Create SPSS file loading module (pyreadstat wrapper only)
   - Responsibility: Load SPSS files, return raw (df, metadata)
   - NO business logic, NO data processing

2. Create/update metadata enrichment module
   - Responsibility: Derive information from raw metadata
   - NO file loading directly

3. Update ALL imports across codebase
   - Replace old imports with new module imports
   - Ensure no old references remain

4. Maintain backward compatibility
   - Old API should still work (with deprecation warnings)

## Worker Investigation Instructions

[CRITICAL - Do your own thorough investigation]

### Step 1: Git Backup (MANDATORY)
Before making ANY changes, you MUST create a Git backup:
```bash
# Check git status
git status

# Stage all current changes (if any)
git add -A

# Create backup commit on current branch
git commit -m "backup: snapshot before task execution

Task: [Brief task description from above]
Timestamp: $(date -Iseconds)
Revert with: git reset --hard HEAD~1"

# Verify backup
git log -1 --oneline
echo "✅ Backup commit created. Revert with: git reset --hard HEAD~1"
```

### Step 2: Deep Investigation
Before implementing, you MUST:

1. **Find ALL files importing from core modules**
   ```bash
   grep -r "from dflib.core" --include="*.py" -l
   grep -r "from.*core.io import" --include="*.py" -l
   grep -r "from.*core.metadata import" --include="*.py" -l
   ```
   - Don't assume the provided list is complete
   - Verify ALL files are found

2. **For each file, understand:**
   - What specific functions/classes are imported?
   - How are they used?
   - Will the API change break this file?

3. **Check test coverage:**
   ```bash
   find dflib/tests -name "*.py" | xargs grep -l "core"
   ```
   - What tests exist?
   - What will need updating?

4. **Understand current implementation:**
   - Read core/io/__init__.py - what does SharedDataLoader do?
   - Read core/metadata - what functions exist?
   - What are the API contracts?

5. **Plan your approach:**
   - What files will you create?
   - What files will you modify?
   - In what order?
   - How will you ensure backward compatibility?

ONLY after completing this investigation, implement the requirements.

## Constraints
- New modules must follow pyreadstat API patterns
- Maintain backward compatibility (deprecation warnings OK)
- All existing tests must pass
- No circular imports

## Success Criteria
- [ ] ALL files importing from old modules found and updated
- [ ] New modules have clear, single responsibilities
- [ ] Backward compatibility maintained (old imports still work)
- [ ] All tests pass
- [ ] No circular dependencies
```

---

## Key Principle: Trust Worker Agent

The Worker Agent is capable of:
- Finding ALL files with grep/find
- Reading code to understand patterns
- Identifying edge cases
- Planning implementation

Main Agent's job:
- Provide scope and direction
- Give requirements and constraints
- Set success criteria
- Ask Worker to investigate thoroughly

Result: **Thorough implementation without micromanagement**
