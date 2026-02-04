---
name: task-worker
description: "Two-agent workflow coordinator with automatic iteration. Reads a task specification, spawns Implementation Agent to execute it, spawns Auditor Agent to review quality, iterates based on feedback (max 3), commits approved work. Called by task-queue module."
---

# Task Worker

Execute a task specification using Implementation and Auditor agents with automatic iteration.

## How It Works

1. **Safety Checkpoint** - Commit and push current state (git)
2. **Read Task** - Parse the task specification document
3. **Implement** - Spawn Implementation Agent via Task tool
4. **Audit** - Spawn Auditor Agent via Task tool
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

### Step 2: Read Task Specification

**Read and extract:**
- If given file path: Read the file
- If given content: Use provided content

**Extract from document:**
- Task summary, Context, Scope
- Requirements, Deliverables, Constraints
- Success criteria, Investigation instructions

### Step 3: Spawn Implementation Agent

**Use the Task tool to spawn a general-purpose agent:**

```
Task(
    subagent_type="general-purpose",
    description="Execute the following task",
    prompt="[Full task specification + instruction to investigate thoroughly]"
)
```

**Implementation Agent must:**
- **Do deep investigation first** - Find ALL affected files, understand patterns, identify edge cases
- Execute task completely
- Return structured results (summary, results, steps taken)

### Step 4: Spawn Auditor Agent

**Use the Task tool to spawn a general-purpose agent:**

```
Task(
    subagent_type="general-purpose",
    description="Audit implementation quality",
    prompt="[Original task + implementation results + request for quality review]"
)
```

**Auditor Agent evaluates:**
- **Accuracy** - Correct, functional, no logical errors
- **Completeness** - All requirements met, edge cases handled
- **Quality** - Well-structured, follows best practices
- **Requirements adherence** - Followed task document, respected constraints

**Auditor Agent must return JSON:**
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
- Increment iteration counter
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
git commit -m "feat: [task summary] - completed

Task: [task file]
Iterations: [N]
Final verdict: PASS ([rating]/10)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"

# Push to remote
git push
```

## Output Format

**Return JSON result:**
```json
{
  "status": "completed or max_iterations_reached",
  "task_document": "[file path]",
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
🔄 Iteration 1/3
✅ Implementation complete
🔍 Auditing...
✅ Audit PASSED (8/10)
💾 Committing approved work...
```

## Key Principles

- **Always checkpoint first** - Create restore point before any work
- **Let subagents work autonomously** - Don't micromanage
- **Respect the audit verdict** - PASS commits, FAIL iterates
- **Max 3 iterations** - Prevent infinite loops
- **Commit only on success** - Failed work should not be committed
