---
name: consistency-audit
description: Comprehensive audit comparing documentation (application design and configuration reference) against actual implementation code. Evaluates code structure, implemented features, behaviors, and configuration values for consistency with documented specifications. Use when Claude needs to verify that implementation matches design docs, check if configuration reference matches actual code settings, validate that documented features are actually implemented, or perform any doc-to-implementation consistency check.
---

# Consistency Audit

## Overview

This skill performs a THOROUGH, systematic audit comparing documentation against actual implementation. It does NOT rely on assumptions - every claim MUST be verified through code inspection.

**CRITICAL**: This skill requires reading implementation files and using Grep to verify specific patterns. Do NOT report something as missing without verification.

## Audit Workflow

### Step 1: Document Discovery

Use `Glob` tool to discover all documentation files:

```
docs/application-design/**/*.md
```

List all discovered documents at the start of the report.

### Step 2: Implementation Discovery

Use `Glob` tool to discover all implementation code:

```
agent/**/*.py
utils/**/*.py
tests/**/*.py
```

**Note**: Adjust patterns based on actual project structure discovered.

List the main directories and file counts.

### Step 3: Read Documentation Thoroughly

Read ALL documentation files. For each document, extract:

**Structural Information:**
- Directory structures and file layouts
- Module names and organizations
- File paths referenced

**Features and Behaviors:**
- Named features (e.g., "22-step workflow", "three-node pattern")
- Workflow steps and their sequence
- Data flow between components

**Configuration Values:**
- Environment variable names and defaults
- Configuration keys and their values
- Port numbers, URLs, paths

**API Interfaces:**
- Endpoints and their methods
- Function signatures
- Request/response formats

**Data Structures:**
- State fields and their types
- Class names and their purposes
- Schema definitions

### Step 4: Verify Implementation - REQUIRED CHECKS

**CRITICAL**: Each documented claim MUST be verified before reporting any inconsistency.

#### 4.1 Code Structure Verification

For each documented directory structure:

**Action**: Use `Bash` with `ls -la` to verify existence:
```bash
ls -la agent/
ls -la utils/
ls -la tasks/
ls -la scripts/
```

**For each documented module/file**:
- Use `Grep` to find references: `Grep pattern="from agent\.|import agent\."`
- Use `Glob` to find files: `Glob pattern="agent/nodes/*.py"`

#### 4.2 Feature/Behavior Verification

**For each documented feature** (e.g., "22-step workflow"):

**Action**: Count actual implementation:
```bash
# Count node files
ls -1 agent/nodes/*.py | wc -l

# Search for specific node names mentioned in docs
Grep pattern="extract_spss|transform_metadata|filter_metadata" path=agent/
```

**For the three-node pattern**:
- Verify recoding nodes exist: `Grep pattern="recoding" agent/nodes/*.py`
- Verify indicator nodes exist: `Grep pattern="indicator" agent/nodes/*.py`
- Verify table specs nodes exist: `Grep pattern="table" agent/nodes/*.py`

#### 4.3 Configuration Verification

**For each documented config value**:

**Action**: Compare documentation with `agent/config.py`:
```bash
# Read the actual DEFAULT_CONFIG
Read agent/config.py

# Search for specific config keys in code
Grep pattern="llm_provider|LLM_PROVIDER|temperature" path=agent/
```

**Check for environment variable usage**:
```bash
Grep pattern="os\.getenv|os\.environ" path=agent/
```

#### 4.4 API/Interface Verification

**For each documented endpoint**:

**Action**: Search in `agent/server.py`:
```bash
Grep pattern='@app\.(get|post|put|delete)' path=agent/server.py
Grep pattern='async def ' path=agent/server.py
```

#### 4.5 State/Schema Verification

**For each documented state field**:

**Action**: Search in `agent/state.py`:
```bash
Grep pattern='class.*State|InputState|ExtractionState' path=agent/state.py
```

**Compare documented field names with actual code**:
- Read `agent/state.py` to find all TypedDict fields
- Compare against documented state fields

### Step 5: Cross-Reference Verification

**MUST verify these relationships:**

1. **Graph Structure**: Documented nodes → Actual nodes in `agent/nodes/`
   ```bash
   # Get all node function names from documentation
   # Then verify each exists in agent/nodes/
   Grep pattern="def .*_node" path=agent/nodes/
   ```

2. **Edge Routing**: Documented edges → Actual edges in `agent/edges.py`
   ```bash
   Grep pattern="def should_" path=agent/edges.py
   ```

3. **Imports**: Documented modules → Actual imports
   ```bash
   Grep pattern="from agent\.|from agent_nodes" path=agent/
   ```

### Step 6: Read Implementation Files

**REQUIRED FILES TO READ** (before concluding anything is missing):

**Core Files:**
- `agent/graph.py` - Graph construction
- `agent/state.py` - State definitions
- `agent/config.py` - Configuration
- `agent/server.py` - API server
- `agent/edges.py` - Routing logic

**Node Files** (read in parallel):
- `agent/nodes/phase1_extraction.py`
- `agent/nodes/phase2_recoding.py`
- `agent/nodes/phase3_indicators.py`
- `agent/nodes/phase4_tables.py`
- `agent/nodes/phase5_statistics.py`
- `agent/nodes/phase6_filtering.py`
- `agent/nodes/phase7_powerpoint.py`
- `agent/nodes/phase8_html_dashboard.py`

**Validation Files**:
- `agent/validation/indicators.py`
- `agent/validation/tables.py`
- `agent/validation/recoding.py`

**LLM Files**:
- `agent/llm/clients.py`
- `agent/llm/prompts.py`

### Step 7: Generate Report

Only after completing verification, generate the report. Use this structure:

```markdown
# Consistency Audit Report

## Audit Methodology

This audit performed thorough verification by:
- Reading all documentation files
- Reading all core implementation files
- Using Grep to search for specific patterns
- Using Bash to verify file/directory existence
- Comparing documented values against actual code

## Documentation Reviewed
[List all files]

## Implementation Audited
[List directories, file counts]

## Verification Results

### Files Read: N files
[List key files read]

### Patterns Searched: M searches
[List key grep patterns used]

---

## Executive Summary
[Total issues by severity - ONLY report verified issues]

---

## Findings by Category

### 1. Code Structure Consistency
#### Verified to Exist
[List structures that were VERIFIED to exist]

#### Verified to NOT Exist
[List structures that were VERIFIED to NOT exist]

#### Not Verified
[List items that could not be verified]

### 2. Feature/Behavior Consistency
#### Verified Implemented
[List features VERIFIED as implemented]

#### Verification Pending
[List features that need more investigation]

### 3. Configuration Consistency
#### Verified Matches
[List config values VERIFIED to match]

#### Verified Mismatches
[List config values VERIFIED to differ]

### 4. API/Interface Consistency
#### Verified Endpoints
[List endpoints VERIFIED to exist]

---

## What's Consistent
[Positive observations - VERIFIED as consistent]

---

## Recommendations (Prioritized)
### Critical (Fix Immediately)
[VERIFIED blocking issues only]

### High Priority
[VERIFIED significant inconsistencies]

### Medium Priority
[VERIFIED minor inconsistencies]

### Low Priority
[Documentation improvements]

---

## Items Requiring Further Investigation
[List items that could not be conclusively verified]
```

---

## Verification Checklist

Before reporting any issue, you MUST:

- [ ] Read the documentation file that mentions the item
- [ ] Use `Glob` to search for the file/pattern
- [ ] Use `Grep` to search for the function/class name in code
- [ ] Use `Read` to examine the actual implementation file
- [ ] Compare the documented behavior with actual code
- [ ] Only report as "missing" if ALL verification steps fail

---

## Common Patterns to Search

**For finding functions:**
```
Grep pattern="def <function_name>" path=agent/
```

**For finding classes:**
```
Grep pattern="class <ClassName>" path=agent/
```

**For finding config keys:**
```
Grep pattern='"config_key"' path=agent/
```

**For finding endpoints:**
```
Grep pattern='@app\.<method>("/<path>"' path=agent/server.py
```

**For finding state fields:**
```
Grep pattern='<field_name>.*:' path=agent/state.py
```

---

## Notes

- **NEVER report something as missing without verification**
- Code comments are NOT documentation - only docs/ directory counts
- Use `Read` tool liberally - reading files is how you verify implementation
- When unsure, mark as "Requires Further Investigation" rather than making assumptions
- Focus on meaningful inconsistencies, not cosmetic differences
- Test files can provide clues but are not the primary implementation
