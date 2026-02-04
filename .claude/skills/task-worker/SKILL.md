---
name: task-worker
description: "Two-agent workflow coordinator with automatic iteration. Reads a task specification, spawns Implementation Agent to execute it, spawns Auditor Agent to review quality, iterates based on feedback (max 3), commits approved work. Called by task-queue module."
---

# Task Worker

Execute a task specification using Implementation and Auditor agents with automatic iteration.

## Workflow Overview

```mermaid
flowchart TD
    START([Start]) --> CHECKPOINT{Safety Checkpoint}
    CHECKPOINT -->|git commit + push| CREATE[Create Working Document]

    CREATE --> IMPLEMENT[Implementation Agent]
    IMPLEMENT -->|writes to doc| AUDIT[Auditor Agent]

    AUDIT -->|reads reqs + code<br/>writes to doc| DECISION{Audit Verdict}

    DECISION -->|PASS| COMMIT[Commit Approved Work]
    DECISION -->|FAIL| COUNT{Iteration < 3?}

    COUNT -->|Yes| IMPLEMENT
    COUNT -->|No| RETURN([Return Failed])

    COMMIT --> PUSH([Push to Remote])
    PUSH --> DONE([Return Success])

    style CHECKPOINT fill:#ffcdd2,stroke:#c62828,stroke-width:2px
    style CREATE fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    style IMPLEMENT fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    style AUDIT fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
    style DECISION fill:#fff9c4,stroke:#f57f17,stroke-width:2px
    style COMMIT fill:#c8e6c9,stroke:#2e7d32,stroke-width:3px
    style DONE fill:#c8e6c9,stroke:#2e7d32,stroke-width:3px
    style RETURN fill:#ffcdd2,stroke:#c62828,stroke-width:2px
```

## How It Works

1. **Safety Checkpoint** - Commit and push current state (git)
2. **Create Working Document** - Create shared document in `tasks/task-worker-reports/`
3. **Implement** - Implementation Agent works and updates the document
4. **Audit** - Auditor Agent independently verifies and updates the document
5. **Iterate** - If audit fails, repeat steps 3-4 (max 3 times)
6. **Commit** - If audit passes, commit and push approved work

## Input

You will receive:
- **Task specification** - File path or markdown content
- **Max iterations** - Optional (default: 3)

## Execution Steps

### Step 1: Safety Checkpoint

**Before reading the task, create a restore point:**

```bash
# Verify on main branch
git branch --show-current
# If not main, switch back: git checkout main

# Stage and commit current state
git add -A
git commit -m "safety-checkpoint: pre-task-implementation backup

This commit creates a restore point before task implementation begins.
If implementation fails, can revert to this checkpoint.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"

# Push to remote
git push
```

**Error handling:**
- If no changes to commit: Continue without checkpoint
- If push fails: Resolve merge conflicts before proceeding

### Step 2: Read Task & Create Working Document

**Read the task specification** and extract task ID.

**Create working document** at `tasks/task-worker-reports/{task-id}.md`:

```markdown
# Task Working Document: {task-id}

**Status**: In Progress
**Iteration**: 1
**Started**: {timestamp}

---

## Original Requirements
{Copy from task specification}

## Implementation Log
{Implementation Agent will write here}

## Audit Report
{Auditor Agent will write here}

## Iteration History
{Appended after each iteration}
```

### Step 3: Spawn Implementation Agent

**Use the Task tool to spawn a general-purpose agent:**

```
Task(
    subagent_type="general-purpose",
    description="Execute the following task",
    prompt="Read the task specification and implement it thoroughly.

IMPORTANT: Update the Implementation Log in the working document at:
tasks/task-worker-reports/{task-id}.md

In your Implementation Log, document:
- What you investigated
- What files you modified
- What changes you made
- Any issues encountered
- Your honest assessment of completeness"
)
```

**Implementation Agent must:**
- **Do deep investigation first** - Find ALL affected files, understand patterns, identify edge cases
- Execute task completely
- **Update the working document** with Implementation Log

### Step 4: Spawn Auditor Agent

**Use the Task tool to spawn a general-purpose agent:**

```
Task(
    subagent_type="general-purpose",
    description="Audit implementation quality",
    prompt="You are the Auditor Agent. Your job is to INDEPENDENTLY verify the implementation.

CRITICAL: Do NOT rely on the Implementation Agent's claims.
Verify by examining the ACTUAL code, tests, and behavior against the ORIGINAL requirements.

Read:
1. Original Requirements from the working document
2. The actual code/files that were modified

DO NOT just read the Implementation Log and trust it.

Check:
- Accuracy - Is the code correct and functional?
- Completeness - Were ALL requirements met? (check against original requirements)
- Quality - Is it well-structured and follows best practices?
- Edge cases - Are edge cases handled?

Update the Audit Report in the working document at:
tasks/task-worker-reports/{task-id}.md

Return JSON with your verdict."
)
```

**Auditor Agent evaluates:**
- **Accuracy** - Correct, functional, no logical errors
- **Completeness** - All requirements met, edge cases handled
- **Quality** - Well-structured, follows best practices
- **Requirements adherence** - Followed original task document

**CRITICAL: Auditor Agent must independently verify against ORIGINAL REQUIREMENTS, not the Implementation Log.**

**Auditor Agent must return JSON and update the working document:**
```json
{
  "verdict": "PASS or FAIL",
  "rating": 1-10,
  "summary": "Brief assessment",
  "strengths": ["Thing done well"],
  "issues_found": ["Issue 1", "Issue 2"],
  "recommendations": ["Fix 1", "Fix 2"],
  "findings": "Detailed analysis"
}
```

### Step 5: Iterate if Needed

**If verdict is FAIL and under max iterations:**
- Increment iteration counter in working document
- Append current iteration to Iteration History
- Include audit feedback
- Go back to Step 3

**If verdict is PASS:**
- Proceed to Step 6

**If max iterations reached:**
- Return with "max_iterations_reached" status

### Step 6: Commit Approved Work

**Only executes when audit passes:**

```bash
# Review changes
git status
git diff

# Stage and commit
git add -A
git commit -m "feat: {task summary} - completed

Task: {task file}
Iterations: {N}
Final verdict: PASS ({rating}/10)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"

# Push to remote
git push
```

**Update working document final status:**
```markdown
**Status**: Completed
**Final Verdict**: PASS ({rating}/10)
**Completed**: {timestamp}
```

## Working Document Structure

The shared working document serves as the **information center** for all agents:

```markdown
# Task Working Document: task-20260204-120000-fix-auth-timeout

**Status**: In Progress
**Iteration**: 2
**Started**: 2026-02-04 12:00:00

---

## Original Requirements
[Immutable - copied from task specification]

## Implementation Log
[Implementation Agent writes what they did]
- Files investigated: ...
- Files modified: ...
- Changes made: ...
- Self-assessment: "I think it's complete" (but Auditor verifies)

## Audit Report
[Auditor Agent writes independent verification]
- Verification: Checked code against ORIGINAL REQUIREMENTS
- Found: These issues that Implementation missed
- Verdict: FAIL - Missing X and Y

## Iteration History
### Iteration 1
- Status: FAILED
- Rating: 6/10
- Issues: [...]
- Feedback: [...]

### Iteration 2
- Status: IN PROGRESS
```

## Output Format

**Return JSON result:**
```json
{
  "status": "completed or max_iterations_reached",
  "task_document": "[file path]",
  "working_document": "tasks/task-worker-reports/{task-id}.md",
  "iterations": [N],
  "final_verdict": "PASS or FAIL",
  "final_rating": [1-10],
  "final_commit_hash": "[hash if completed]"
}
```

## Progress Updates

**Inform user at each phase:**
```
🔒 Creating safety checkpoint...
📋 Task: [summary]
📄 Created working document: tasks/task-worker-reports/{task-id}.md
🔄 Iteration 1/3
👷 Implementation complete
🔍 Auditing (independent verification)...
✅ Audit PASSED (8/10)
💾 Committing approved work...
```

## Key Principles

- **Always checkpoint first** - Create restore point before any work
- **Shared working document** - Single source of truth in `tasks/task-worker-reports/`
- **Independent auditor** - Auditor verifies against ORIGINAL REQUIREMENTS, not Implementation Log
- **Let subagents work autonomously** - Don't micromanage
- **Respect the audit verdict** - PASS commits, FAIL iterates
- **Max 3 iterations** - Prevent infinite loops
- **Commit only on success** - Failed work should not be committed
