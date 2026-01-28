---
name: agent-delegation-auditor
description: "Delegator skill implementing a two-agent workflow. Delegates tasks to a Worker Agent with clear instructions, then audits results with an Auditor Agent for quality assurance. Use when you need to: ensure high-quality outputs through independent review; implement separation of duties between execution and verification; get quality ratings and actionable feedback; apply consistency standards; audit code, analysis, writing, research, or any generated work."
---

# Agent Delegation Auditor

A two-agent workflow that separates task execution from quality verification.

## Overview

Delegates a task to a Worker Agent for execution, then routes the results to an Auditor Agent for independent review. The Auditor provides a quality rating (1-10), identifies issues, and delivers actionable feedback.

**Use Cases:**
- Code reviews with automated quality assessment
- Analysis verification and validation
- Writing quality checks
- Research accuracy auditing
- Any task requiring independent verification

## Task Document Generation

The **Main Agent (Development Agent)** is responsible for writing task documents.

### Key Principle: Two-Level Investigation

```
┌─────────────────────────────────────────────────────────────────┐
│                     Main Agent (Task Writer)                      │
│  Purpose: Holistic understanding, scope, direction               │
│  Output: Task document with requirements + guidance              │
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

### Main Agent: Holistic Investigation (Before Writing Task)

Investigate to understand the big picture, NOT every detail:

| What | How | Output |
|------|-----|--------|
| **Scope** | `find`, `ls` directories | Directories affected |
| **Patterns** | `grep`, `Read` samples | Current conventions |
| **Dependencies** | `grep -r "import"` | What depends on what |
| **Tests** | `find tests/` | Test coverage location |
| **Docs** | `find docs/` | Architecture decisions |

### Task Document: Direction, Not Micromanagement

**DO** - Provide scope and requirements:
```markdown
## Scope
- Directories: dflib/core/, dflib/computation/
- Affected: ~5-10 files importing from core/io

## Requirements
1. Create new module for SPSS file loading (pyreadstat wrapper only)
2. Create/update module for metadata enrichment
3. Update ALL imports across codebase
4. Maintain backward compatibility

## Worker Investigation Instructions
[CRITICAL] You MUST do your own deep investigation:
- Find ALL files with: grep -r "from dflib.core" --include="*.py"
- Understand current patterns before changing
- Identify ALL edge cases and dependencies
```

**DON'T** - Micromanage with line numbers:
```markdown
## Requirements
1. Update line 5 of pandas_analyzer.py
2. Update line 8 of pandas_analyzer.py
```
❌ Too brittle, Worker doesn't investigate, might miss files

### Task Document Quality

| Quality | Characteristics | Use Case |
|---------|----------------|----------|
| **Poor** | Too vague, no direction | ❌ Never use |
| **Fair** | Some direction, no investigation request | ⚠️ Worker may miss things |
| **Good** | Clear scope + Worker investigation requested | ✅ Use this |
| **Excellent** | Holistic context + explicit investigation | ✅ Ideal for complex tasks |

See [task-template.md](references/task-template.md) for:
- Two-level investigation process
- Main Agent investigation checklist
- Worker investigation template
- Good vs Bad examples
- Complete task document structure

### Quick Task Generation (Minimal Format)

For simple tasks, use this minimal structure:

```markdown
## Task
[Clear one-line description]

## Context
[Relevant background from conversation]

## Requirements
1. [Specific requirement 1]
2. [Specific requirement 2]
```

## Quick Start

### Basic Usage (Script)

```bash
# Run with default prompts
python scripts/delegate_and_audit.py --task "Write a Python function to sort a list"

# Use custom prompts from files
python scripts/delegate_and_audit.py \
  --task "Analyze the market trends for electric vehicles" \
  --worker-prompts references/worker-prompts.md \
  --auditor-prompts references/auditor-prompts.md

# Save results to JSON
python scripts/delegate_and_audit.py \
  --task "Create a marketing email for a product launch" \
  --output results.json
```

### Programmatic Usage

**Simple string task:**

```python
from scripts.delegate_and_audit import delegate_and_audit
import asyncio

result = asyncio.run(delegate_and_audit(
    task="Write a REST API endpoint for user authentication",
    worker_prompt="You are a backend developer specializing in FastAPI...",
    auditor_prompt="You are a code reviewer focusing on security and best practices..."
))

print(f"Rating: {result['rating']}/10")
print(f"Verdict: {result['verdict']}")
```

**Using helper function for structured task document:**

```python
from scripts.delegate_and_audit import delegate_and_audit, create_task_document
import asyncio

# Create structured task document
task_doc = create_task_document(
    task_type="Code",
    objective="Create a REST API endpoint for user authentication with JWT tokens",
    context="Building a FastAPI backend for dataflow project at /home/admin/workspaces/dataflow",
    requirements=[
        "Implement POST /auth/login endpoint",
        "Validate username/password against database",
        "Return JWT token on successful authentication",
        "Handle error cases properly"
    ],
    deliverables=[
        "Python code for the endpoint",
        "Include proper error handling",
        "Add docstrings",
        "Follow existing code patterns"
    ],
    constraints=[
        "Use FastAPI framework",
        "Follow existing project patterns",
        "Include type hints",
        "Token expiry: 24 hours"
    ],
    success_criteria=[
        "Endpoint accepts POST requests",
        "Returns valid JWT on correct credentials",
        "Returns 401 on invalid credentials",
        "Code follows project conventions"
    ]
)

result = asyncio.run(delegate_and_audit(
    task=task_doc,
    worker_prompt="You are a backend developer...",
    auditor_prompt="You are a code reviewer..."
))
```

**Minimal task for simple cases:**

```python
from scripts.delegate_and_audit import delegate_and_audit, create_minimal_task
import asyncio

task = create_minimal_task(
    task="Write a Python function to calculate fibonacci numbers",
    context="Need efficient implementation for a coding tutorial",
    requirements=[
        "Handle edge cases (negative numbers, zero)",
        "Include docstring with examples",
        "Use recursive or iterative approach"
    ]
)

result = asyncio.run(delegate_and_audit(task=task))
```

## Workflow

```
┌─────────────────┐
│   Your Request  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  STEP 1: WORKER AGENT               │
│  - Receives task with instructions  │
│  - Executes the task                │
│  - Returns structured results       │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  STEP 2: AUDITOR AGENT              │
│  - Reviews worker's results         │
│  - Identifies issues                │
│  - Provides quality rating (1-10)   │
│  - Returns JSON with verdict        │
└────────┬────────────────────────────┘
         │
         ▼
    ┌────────────────┐
    │ Verdict Check  │
    └────┬─────┬─────┘
         │     │
    PASS │     │ FAIL/NEEDS_REVISION
         │     │
         │     ▼
         │  ┌──────────────────────────┐
         │  │  Worker Retries          │
         │  │  (up to max_iterations)  │
         │  │  - Receives audit feed-  │
         │  │    back from prev round  │
         │  └──────────┬───────────────┘
         │             │
         └─────────────┴──────────┐
                                   ▼
                        ┌─────────────────────────────┐
                        │  FINAL OUTPUT               │
                        │  - All iterations           │
                        │  - Quality rating            │
                        │  - Pass/Fail verdict        │
                        │  - Audit findings           │
                        └─────────────────────────────┘
```

### Iteration Loop with Feedback

The workflow supports automatic retry when the audit fails:

- **Default max_iterations: 3** (configurable with `--max-iterations`)
- If verdict is PASS/APPROVED: Stop early (quality achieved)
- If verdict is FAIL/NEEDS_REVISION: Worker retries with audit feedback
- Each iteration provides full audit feedback to the Worker Agent
- Final output includes all iterations for review

**Exit codes:**
- `0`: Final audit passed (PASS, APPROVED, etc.)
- `1`: Max iterations reached without passing

## JSON Response Format

### Why JSON?

The Auditor Agent is instructed to respond **only with valid JSON**. This provides:

1. **Reliable parsing**: Direct dictionary access instead of fragile regex
2. **Structured data**: Verdict, rating, findings in predictable fields
3. **Type safety**: Numbers are numbers, arrays are arrays
4. **Backward compatibility**: Falls back to regex if JSON parsing fails

### Auditor Response Structure

The Auditor's entire response is a JSON object:

```json
{
  "verdict": "PASS",
  "rating": 8,
  "summary": "Brief overall assessment",
  "strengths": ["Thing done well", "Another strength"],
  "issues_found": ["Issue 1", "Issue 2"],
  "recommendations": ["Fix 1", "Fix 2"],
  "findings": "Detailed analysis text"
}
```

### Parsing Logic

The script uses a two-tier approach:

1. **Primary**: Parse with `json.loads()` for direct field access
2. **Fallback**: Use regex parsing if JSON is malformed (backward compatibility)

This ensures reliability even if the model occasionally wraps JSON in markdown or adds extra text.

## Task Prompts

This skill uses **generic, universal prompts** that adapt to any task type:

- **Worker Prompt**: See [worker-prompts.md](references/worker-prompts.md) - Single prompt that works for any task
- **Auditor Prompt**: See [auditor-prompts.md](references/auditor-prompts.md) - Single prompt that evaluates any work

The prompts are designed to:
- Understand task requirements from the task document itself
- Adapt evaluation criteria based on the task's success criteria
- Work for code, analysis, writing, research, documentation, or any other task type

**Special Case**: For tasks involving "find all and update" operations (terminology renames, config updates), see the [Comprehensive Search Tasks](references/worker-prompts.md#for-comprehensive-search-tasks) section which includes specific methodology for exhaustive discovery.

## Git Backup Step

For tasks involving file changes, the Worker Agent creates a **Git backup commit** on the current branch before making any modifications.

### Commands

```bash
git status
git add -A
git commit -m "backup: snapshot before task execution

Task: [description]
Timestamp: $(date -Iseconds)
Revert: git reset --hard HEAD~1"
git log -1 --oneline
```

### Revert

If something goes wrong:
```bash
git reset --hard HEAD~1
```

### Applied To

- Code refactoring
- Terminology renames
- Configuration updates
- Any file modifications

### If Git Fails

The Worker reports the issue, Auditor notes the risk, and decision to proceed is documented.

## Customizing System Prompts

### Option 1: File-Based

Create custom prompt files and reference them:

```bash
python scripts/delegate_and_audit.py \
  --task "Your task here" \
  --worker-prompts path/to/worker.txt \
  --auditor-prompts path/to/auditor.txt
```

### Option 2: Inline

Pass prompts directly as arguments:

```bash
python scripts/delegate_and_audit.py \
  --task "Your task here" \
  --worker-text "You are a specialist in X..." \
  --auditor-text "You are a reviewer focusing on Y..."
```

### Option 3: Programmatic

```python
custom_worker = """
You are a specialized agent for [domain].
[Your custom instructions]
"""

custom_auditor = """
You are a specialized auditor for [domain].
[Audit criteria specific to this domain]
"""

result = asyncio.run(delegate_and_audit(
    task="Your task",
    worker_prompt=custom_worker,
    auditor_prompt=custom_auditor
))
```

## Output Format

The Auditor Agent responds with structured JSON for reliable parsing:

### Output Directory

All outputs (audit reports and delegation results) are automatically saved to:

```
temp/tasks/agent-delegation-auditor/YYYYMMDD/
```

**Structure:**
```
temp/tasks/agent-delegation-auditor/
└── 20250115_ui-pages-renaming/
    ├── audit_report_iteration_1_task_8f160a39.md
    ├── audit_report_iteration_2_task_8f160a39.md
    ├── audit_report_iteration_3_task_8f160a39.md
    └── delegation_result_20250115_123456.json
```

- **Date-based subdirectories**: Each day gets its own folder (YYYYMMDD format)
- **Audit reports**: One markdown file per iteration
- **Delegation result**: JSON file with all iterations and final verdict
- **Custom output**: Use `--output` to specify a different location

### Auditor Response Format

```json
{
  "verdict": "PASS",
  "rating": 8,
  "summary": "Brief overall assessment of the work",
  "strengths": [
    "Specific thing that was done well",
    "Another strength"
  ],
  "issues_found": [
    "Specific issue identified",
    "Another issue"
  ],
  "recommendations": [
    "How to fix issue 1",
    "How to fix issue 2"
  ],
  "findings": "Detailed findings and analysis"
}
```

**Final output JSON includes:**

```json
{
  "task": "The original task description",
  "iterations": [
    {
      "iteration": 1,
      "worker_result": {
        "task": "...",
        "content": "Worker's full response...",
        "summary": "...",
        "steps": "...",
        "notes": "..."
      },
      "audit_result": {
        "content": "Raw auditor response...",
        "verdict": "PASS",
        "rating": 8,
        "summary": "...",
        "strengths": [...],
        "issues_found": [...],
        "recommendations": [...],
        "findings": "...",
        "json_parsed": true,
        "report_file": "temp/tasks/agent-delegation-auditor/20250115/audit_report_iteration_1_task_8f160a39.md"
      },
      "verdict": "PASS",
      "rating": 8
    }
  ],
  "total_iterations": 1,
  "final_verdict": "PASS",
  "final_rating": 8,
  "passed": true,
  "timestamp": "2025-01-10T12:34:56",
  "max_iterations": 3,
  "output_dir": "temp/tasks/agent-delegation-auditor/20250115"
}
```

## Verdict Meanings

| Verdict | Meaning |
|---------|---------|
| PASS | Work meets quality standards |
| FAIL | Work has critical issues |
| NEEDS_REVISION | Work has issues that should be addressed |
| APPROVED | Code/task approved for use |
| REJECTED | Code/task must be redone |
| PUBLISHED_READY | Writing ready for publication |
| MOSTLY_RELIABLE | Research generally credible with minor issues |

## Environment Variables

Required for Claude Agent SDK:

```bash
export ANTHROPIC_API_KEY="your-api-key"
export ANTHROPIC_MODEL="claude-sonnet-4-5-20250514"  # Optional
```

## Script Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Error (missing SDK, API key issues, etc.) |
