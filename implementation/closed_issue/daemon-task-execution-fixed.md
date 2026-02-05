# Issue: Daemon Task Execution - Fixed

**Status:** ✅ CLOSED - Fixed with worker script workaround
**Created:** 2026-02-06
**Resolved:** 2026-02-06

---

## Summary

The task-queue daemon was not executing tasks properly. Tasks were archived without execution (status remained "Pending", output files not created).

## Root Cause

The `SyncTaskExecutor` in `executor.py` was calling the SDK with a custom `system_prompt` that interfered with `/task-worker` skill invocation. The AI treated `/task-worker` as text to understand rather than as a command to execute.

## Solution

**Created workaround worker script** (`test4_worker.py`):
- Uses direct SDK `query()` approach from Test 4 (known working)
- Removes custom `system_prompt` (lets skill define its own behavior)
- Called via `subprocess.run()` from TaskRunner

**Files modified:**
1. `/home/admin/workspaces/task-queue/test4_worker.py` - New worker script
2. `/home/admin/workspaces/task-queue/task_queue/task_runner.py` - Updated to use worker script
3. `/home/admin/workspaces/task-queue/.venv/` - Upgraded SDK to v0.1.30 (fixes 10s timeout)

## Verification

```bash
# Test task created
cat > tasks/task-documents/task-20260206-073400-verify-fix.md

# Task executed successfully
cat /tmp/verify-fix-output.txt
# Output: TaskRunner fix works!

# Task archived properly
ls tasks/task-archive/task-20260206-073400-verify-fix.md
```

✅ Tasks now execute via watchdog detection → worker script → `/task-worker` skill → output created → archived
