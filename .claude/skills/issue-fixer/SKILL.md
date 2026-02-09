---
name: issue-fixer
description: "Systematic issue resolution workflow for investigating and fixing bugs in the codebase. Use when: User explicitly requests to fix an issue from implementation/open_issue/, User asks to investigate a bug or error, User wants to systematically resolve open issues, User references open issue or closed issue directories. The skill follows a 6-step process: Safety Check, Issue Discovery, Solution Lookup, Deep Investigation, Fix Implementation, Documentation. Only complex issues are documented and moved to closed_issue; simple fixes are dropped without documentation."
---

# Issue Fixer

## Overview

Systematic workflow for resolving documented issues and bugs in the codebase. This skill guides the process of discovering issues, finding existing solutions, investigating root causes, implementing fixes, and documenting resolved issues.

**Key principle:** Always ensure git safety before making changes. Every issue resolution begins with a safety checkpoint.

## Workflow

### Step 1: Safety Check (REQUIRED)

Before any issue resolution work:

1. **Verify current branch**
   ```bash
   git branch --show-current
   ```
   - If NOT on `main`, notify user and switch back
   - Never proceed on feature/backup branches without explicit user request

2. **Check for uncommitted changes**
   ```bash
   git status
   ```

3. **If changes exist:**
   - Review the changes with the user
   - Commit with descriptive message if user approves
   - Push to remote: `git push`

4. **Only proceed to issue resolution when working directory is clean**

**Rationale:** This prevents losing work and ensures all changes are safely backed up before investigation begins.

### Step 2: Issue Discovery

Identify the issue to resolve:

**Option A: User-specified issue**
- User may provide a specific issue filename or description
- Example: "Fix the workflow state accumulation issue"

**Option B: Auto-scan open_issue directory**
- List all markdown files in `implementation/open_issue/`
- Use `Glob` or `Grep` to find issue files: `implementation/open_issue/*.md`
- Present available issues to user if multiple exist
- Example: "Found 1 open issue: workflow-state-accumulation-issue.md"

**Read the issue document:**
- Full issue description
- Root cause analysis (if present)
- Possible solutions (if documented)
- Affected files/tests

### Step 3: Solution Lookup

Check if a solution already exists:

1. **Search closed_issue directory**
   ```bash
   # Use Grep to search for related keywords in closed issues
   implementation/closed_issue/
   ```

2. **Compare issue characteristics**
   - Same error message?
   - Same affected files?
   - Similar symptoms?

3. **If solution found:**
   - Read the closed issue document
   - Apply the documented solution
   - Verify the fix works
   - Skip to Step 6

4. **If no solution exists:**
   - Proceed to Step 4 for deep investigation

### Step 4: Deep Investigation

When no existing solution exists, investigate the root cause:

**Investigation checklist:**

1. **Read affected files**
   - Identify all files mentioned in the issue
   - Read each file to understand current implementation

2. **Reproduce the issue (if applicable)**
   - Run failing tests: `pytest tests/core/test_graph.py::TestEndToEndWorkflow::test_end_to_end_workflow -v`
   - Check error messages and stack traces

3. **Analyze the root cause**
   - Trace through the code execution
   - Identify where expected behavior diverges from actual
   - Consider architectural patterns (e.g., LangGraph state management, TypedDict behavior)

4. **Research external dependencies**
   - Check documentation for affected libraries
   - Use `mcp__context7__query-docs` for library-specific questions
   - Search for known issues or version-specific behaviors

5. **Formulate solution approach**
   - Identify minimal fix needed
   - Consider trade-offs of different approaches
   - Plan verification strategy

**Example investigation pattern:**
```
Issue: current_step stuck at 4 instead of 22
→ Read agent/graph.py, agent/state.py
→ Run test and observe: all outputs present, step counter wrong
→ Hypothesis: LangGraph state merger without custom reducer
→ Verify: Each node sets current_step correctly
→ Conclusion: Need custom reducer for current_step field
```

### Step 5: Fix Implementation

Apply the fix:

1. **Create test coverage (if missing)**
   - Write test that reproduces the issue
   - Verify test fails before fix

2. **Implement the fix**
   - Make minimal, targeted changes
   - Follow project conventions (TypedDict usage, file organization, etc.)
   - Document any non-obvious decisions in code comments

3. **Verify the fix**
   - Run affected tests
   - Run full test suite if changes are significant
   - Check for regressions

4. **Update related tests if needed**
   - Fix tests that relied on old behavior
   - Update assertions to match new behavior

**Quality gates:**
- No test failures introduced
- Fix addresses root cause, not symptoms
- Code follows project patterns

### Step 6: Documentation

Complete the issue resolution lifecycle:

**1. If issue was NOT fixed**

Keep in `implementation/open_issue/`:
- Update document with investigation findings so far
- Add next steps for future investigation
- Skip to commit (if any progress to save)

**2. If issue WAS fixed**

Evaluate complexity:

| Complex? | Criteria |
|----------|----------|
| **Yes** | Time-consuming, difficult, required deep research |
| **No** | Quick fix, straightforward, minimal effort |

- **If COMPLEX:** Document and keep
  - Add solution to issue document (root cause, fix, files changed)
  - Move to `implementation/closed_issue/`
  - Pattern: `ISSUE-YYYYMMDD-{description}.md`
  - Example: `ISSUE-20250203-workflow-state-accumulation.md`

- **If NOT complex:** Drop
  - Delete the issue file from `implementation/open_issue/`
  - No documentation needed

**3. Commit if anything was saved**

```bash
# Only if issue was moved to closed_issue
git add implementation/
git commit -m "fix: resolve workflow state accumulation issue

- Added custom state reducer for current_step field
- Updated 17 failing e2e tests
- Moved to closed_issue"
```

## Issue Document Template

When creating new issue documents in `implementation/open_issue/`, use this structure:

```markdown
# {Issue Title}

**Status:** Open
**Created:** YYYY-MM-DD
**Related:** {Affected tests, components, or features}

## Issue Description

{Clear description of the problem}

### Observed Behavior

{What actually happens - include error messages, test output}

### Expected Behavior

{What should happen}

## Root Cause Analysis

{Investigation findings - if known}

## Possible Solutions

{List potential approaches with pros/cons}

## Affected Tests

{List of failing tests or affected test files}

## Files to Investigate

{List of files relevant to this issue}

## Next Steps

{Plan for resolution}
```

## Common Patterns

### LangGraph State Issues

**Symptoms:** State values not updating as expected across workflow steps

**Investigation:**
1. Check `agent/state.py` - Verify TypedDict structure
2. Check `agent/graph.py` - Look for custom reducer
3. Verify nodes use correct state update patterns

**Common fixes:**
- Add custom state reducer for specific fields
- Use `Annotated` with reducer function in TypedDict
- Ensure state updates use correct merge patterns

### TypedDict Access Issues

**Symptoms:** AttributeError trying to access dict keys as attributes

**Fix:** Change from attribute access to dictionary access
```python
# Wrong:
result.is_valid
# Correct:
result['is_valid']
```

### Test Mock Issues

**Symptoms:** Tests fail with real values instead of mocks

**Investigation:**
1. Check fixture is `autouse=True`
2. Verify patch paths match actual import locations
3. Use `ExitStack` for multiple patches

**Common fix:**
```python
@pytest.fixture(autouse=True)
def mock_dependencies():
    with ExitStack() as stack:
        stack.enter_context(patch('module.function', return_value=mock))
        yield
```

## References

- **Project structure:** `docs/application-design/project-structure.md`
- **Testing conventions:** `docs/application-design/testing-structure.md`
- **Git workflow:** CLAUDE.md sections 3 (branch management), 5 (document creation)
