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

**Copy and rename the template** using CLI command:

```bash
# Copy template from skill directory and rename with task ID
cp .claude/skills/task-worker/working-document-template.md tasks/task-worker-reports/{task-id}.md
```

**Populate the template with task requirements:**
- Replace `{task-id}` with actual task ID
- Replace `{timestamp}` with current timestamp
- Replace `{task-spec-file}` with task specification path
- Copy Original Requirements section from task specification

**The template provides the structure - each agent updates their designated section.**

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

Update the Audit Report section in the working document at:
tasks/task-worker-reports/{task-id}.md

Your report MUST include:
- Verdict: PASS or FAIL (clear statement at the top)
- Rating: 1-10
- Summary: Brief overall assessment
- Issues found: List of problems (if any)
- Recommendations: How to fix issues (if any)

IMPORTANT: Write clearly so the Coordinator can read your verdict and decide next steps."
)
```

**Auditor Agent evaluates:**
- **Accuracy** - Correct, functional, no logical errors
- **Completeness** - All requirements met, edge cases handled
- **Quality** - Well-structured, follows best practices
- **Requirements adherence** - Followed original task document

**CRITICAL: Auditor Agent must independently verify against ORIGINAL REQUIREMENTS, not the Implementation Log.**

**Auditor Agent writes to the shared document (no JSON return needed).**

### Step 5: Check Verdict and Decide

**Read the working document** to check the Auditor's verdict.

**Look for the verdict in the Audit Report section:**
- If verdict is **PASS** → Proceed to Step 6 (Commit)
- If verdict is **FAIL** and iteration < 3 → Append to history, increment counter, go to Step 3
- If verdict is **FAIL** and iteration = 3 → Return with "max_iterations_reached" status

**Coordinator reads from the shared document - no JSON passing needed.**

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

## Working Document Template

The working document structure is defined in the template file:
```
.claude/skills/task-worker/working-document-template.md
```

**Template sections:**

| Section | Updated By | Purpose |
|---------|------------|---------|
| **Header (Status, Iteration, etc.)** | Coordinator | Track progress |
| **Original Requirements** | Coordinator | Copied from task spec (immutable) |
| **Implementation Log** | Implementation Agent | What they did (reference only) |
| **Audit Report** | Auditor Agent | Independent verification |
| **Iteration History** | Coordinator | Complete record |

**Example workflow:**
1. Coordinator copies template → `{task-id}.md`
2. Coordinator fills in Original Requirements
3. Implementation Agent updates Implementation Log
4. Auditor Agent updates Audit Report (with PASS/FAIL verdict)
5. Coordinator reads Audit Report to decide next step
6. If iterating, append to Iteration History and repeat from step 3

## Output Format

**Return JSON result:**
```json
{
  "status": "completed or max_iterations_reached",
  "task_document": "[file path]",
  "working_document": "tasks/task-worker-reports/{task-id}.md",
  "iterations": [N],
  "final_verdict": "[read from Audit Report section]",
  "final_rating": "[read from Audit Report section]",
  "final_commit_hash": "[hash if completed]"
}
```

**Note:** Final verdict and rating are read from the working document's Audit Report section, not passed as JSON.

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
