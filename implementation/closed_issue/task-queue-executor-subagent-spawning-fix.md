# Task-Queue Executor Sub-Agent Spawning Fix

**Status**: Closed
**Date**: 2025-02-06
**Component**: task-queue executor

---

## Issue

The task-queue executor was not spawning sub-agents (Implementation Agent, Auditor Agent) as specified in the task-worker skill workflow. Tasks were being executed directly by a single agent instead.

## Investigation

Created multiple test scripts to isolate the root cause:

| Test | Prompt | Result |
|------|--------|--------|
| Test 1 | Explicit "You MUST spawn sub-agents" | ✅ Sub-agents spawned (but events not captured) |
| Test 2 | `/task-worker\n\nExecute task...` | ❌ Direct execution |
| Test 3 | "You are task worker..." | ❌ Direct execution |
| Test 4 | "READ skill doc, then execute" | ✅ **Sub-agents spawned, workflow followed** |

## Root Cause

The original executor prompt:
```python
prompt_text = f"""/task-worker

Execute task at: {relative_task_path}
"""
```

This simple invocation was not sufficient to force the agent to spawn sub-agents. The agent would see the simple task and choose direct execution for efficiency.

## Solution

Updated the executor prompt to explicitly require reading the skill documentation:

```python
prompt_text = f"""Read the task-worker skill documentation at: .claude/skills/task-worker/SKILL.md

Follow the skill's workflow EXACTLY to execute the task at: {relative_task_path}

IMPORTANT:
- Read the skill document carefully first
- Follow ALL steps in the workflow (Safety Checkpoint, Task Report, Implementation Agent, Auditor Agent, Commit)
- Do NOT skip any steps
- Do NOT execute the task directly - spawn sub-agents as specified in the skill documentation"""
```

## Changes Made

**File**: `/home/admin/workspaces/task-queue/task_queue/executor.py`

1. Updated prompt (lines 164-175) to require reading skill documentation
2. Added `allowed_tools` parameter including `"Task"` tool (lines 148-157)

## Verification

Test task `task-20260206-verify-new-executor` confirmed:
- ✅ Implementation Agent spawned
- ✅ Auditor Agent spawned
- ✅ Task report created with Implementation and Audit sections
- ✅ Audit verdict: PASS (10/10)
- ✅ Task completed successfully

## Files Modified

- `/home/admin/workspaces/task-queue/task_queue/executor.py` - Updated prompt and added `allowed_tools`

## Test Scripts Created

- `/home/admin/workspaces/datachat/temp/test_subagent_spawning.py`
- `/home/admin/workspaces/datachat/temp/test_original_prompt.py`
- `/home/admin/workspaces/datachat/temp/test_description_only.py`
- `/home/admin/workspaces/datachat/temp/test_read_skill_doc.py`
