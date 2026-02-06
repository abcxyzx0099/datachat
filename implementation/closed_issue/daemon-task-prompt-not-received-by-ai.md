# Issue: Daemon Task Execution - Prompt Not Received by AI

**Status:** ✅ RESOLVED - Fixed by removing extras from SyncTaskExecutor
**Created:** 2026-02-06
**Resolved:** 2026-02-06
**Related:** task-queue module, Claude Agent SDK

---

## Issue Description

The task-queue daemon was not executing tasks properly. Tasks were being archived without execution (status remained "Pending", output files not created).

### Observed Behavior (Before Fix)

When a task was queued and executed by the daemon:
- ✅ Authentication succeeded
- ✅ Daemon picked up the task
- ✅ Executor was called
- ❌ `/task-worker` skill was not invoked
- ❌ AI responded with generic message instead of executing
- ❌ No files were created
- ❌ Task archived with "Status: Pending"

---

## Root Cause Analysis

### INCORRECT Hypotheses (Previously Tested)

1. ❌ **Missing `system_prompt`** - Adding custom system_prompt didn't help
2. ❌ **SDK version (v0.1.29 timeout bug)** - Upgraded to v0.1.30 but issue persisted
3. ❌ **Wrong bundled CLI path** - Path wasn't the issue
4. ❌ **Environment differences (daemon vs script)** - Not related to systemd

### CORRECT Root Cause: Extras in SyncTaskExecutor

Through **incremental testing** (Steps 1-7), the breaking point was identified:

| Test | Configuration | Result |
|------|---------------|--------|
| Step 1-5 | Basic features (watchdog, classes, etc.) | ✅ Works |
| Step 6 | SyncTaskExecutor **WITH extras** | ❌ **FAILS** |
| Step 7 | SDK call **WITHOUT extras** | ✅ Works |

### The Extras That Broke It

```python
# BROKEN CODE (Original)
options = ClaudeAgentOptions(
    cwd=str(self.project_root),
    permission_mode="bypassPermissions",
    setting_sources=["project"],
    tools={"type": "preset", "preset": "claude_code"},
    stderr=stderr_callback,              # ← EXTRA
    extra_args={"debug-to-stderr": True}, # ← EXTRA
    system_prompt="""...""",              # ← EXTRA
)

# Custom event loop - EXTRA
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(consume_messages())
finally:
    loop.close()  # ← Caused "cancel scope" error
```

### Why These Extras Broke /task-worker

The extras (`stderr`, `extra_args`, `system_prompt`, custom loop) interfered with the `/task-worker` skill invocation. The exact mechanism is unclear, but removing all extras restored normal skill execution.

---

## The Fix

### File Modified

**`/home/admin/workspaces/task-queue/task_queue/executor.py`**

### What Was Removed

1. `stderr=stderr_callback` - stderr capture callback
2. `extra_args={"debug-to-stderr": True}` - debug mode
3. `system_prompt="""..."""` - custom system prompt
4. Custom asyncio event loop with `loop.close()`
5. `cli_path=` forcing (was using wrong path)

### What Was Kept (Working Code)

```python
options = ClaudeAgentOptions(
    cwd=str(self.project_root),
    permission_mode="bypassPermissions",
    setting_sources=["project"],
    tools={"type": "preset", "preset": "claude_code"},
    env={
        "ANTHROPIC_API_KEY": _ANTHROPIC_AUTH_TOKEN,
        "ANTHROPIC_BASE_URL": _ANTHROPIC_BASE_URL
    },
)

# Standard asyncio.run()
asyncio.run(consume_messages())
```

### Additional Fix

**`/home/admin/workspaces/task-queue/task_queue/task_runner.py`**
- Removed subprocess workaround
- Now uses fixed SyncTaskExecutor directly

---

## Verification

### Test Results (After Fix)

| Test | Result |
|------|--------|
| Direct SDK call | ✅ Works |
| SyncTaskExecutor (fixed) | ✅ Works |
| Full module (2500 lines) | ✅ Works |
| Daemon with watchdog | ✅ Works |

### Full Module Test

```
==============================================================
DAEMON + WATCHDOG TEST
==============================================================

Created: task-20260206-102457-daemon-test.md
Watchdog: Auto-detected file creation
Worker:   Picked up task
SDK:      Invoked /task-worker skill
Result:   ✅ SUCCESS

Output:   /tmp/daemon-watchdog-works.txt
Content:  "DAEMON WATCHDOG AUTO-DETECTED AND EXECUTED THIS TASK!"
Execution Time: 30.3 seconds
```

### Key Features Verified

- ✅ Auto-detection of new task files (watchdog)
- ✅ Parallel worker threads (per source)
- ✅ Running marker creation (.task-*.running)
- ✅ Task execution via fixed executor
- ✅ /task-worker skill invocation
- ✅ Output file creation
- ✅ Task archiving (moved to task-archive/)
- ✅ Running marker cleanup

---

## Lessons Learned

1. **Incremental testing is powerful** - Adding elements one-by-one found the exact breaking point
2. **Simpler is often better** - The extras added complexity but broke functionality
3. **Standard patterns work best** - Using `asyncio.run()` instead of custom loops
4. **Environment variables for auth** - Use `env=` parameter instead of `os.environ`

---

## Related Files

- `/home/admin/workspaces/task-queue/task_queue/executor.py` - Fixed executor (removed extras)
- `/home/admin/workspaces/task-queue/task_queue/task_runner.py` - Uses fixed executor
- `/home/admin/.config/task-queue/config.json` - Daemon configuration

---

## Incremental Test Steps (Reference)

For future debugging, the incremental tests that identified the issue:

1. `step01_simple_watchdog.py` - Simple watchdog + worker ✅
2. `step02_add_running_marker.py` - Add running marker ✅
3. `step03_add_archive.py` - Add archive management ✅
4. `step04_add_failed_directory.py` - Add failed directory ✅
5. `step05_class_based.py` - Convert to class-based ✅
6. `step06_use_executor.py` - Use SyncTaskExecutor **WITH extras** ❌
7. `step07_clean_executor.py` - Use SDK **WITHOUT extras** ✅

**Breaking point identified at Step 6.**
