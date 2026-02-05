# Issue: Daemon Task Authentication Failure

**Status**: CLOSED ✅

**Created**: 2026-02-06
**Resolved**: 2026-02-06

---

## Problem

Tasks executed by the task-queue daemon failed with authentication errors after ~19-20 seconds. The bundled CLI could not authenticate when run via systemd daemon.

**Error**: `Could not resolve authentication method. Expected either apiKey or authToken to be set.`

## Root Cause

The bundled CLI requires API credentials, but:
- OAuth tokens are only available in interactive terminal sessions
- Systemd environment variables are NOT passed to the CLI subprocess
- Settings.json was not being read by the bundled CLI

## Solution

Pass the API key through the SDK's `env` parameter in `ClaudeAgentOptions`:

**File**: `/home/admin/workspaces/task-queue/task_queue/executor.py`

```python
options = ClaudeAgentOptions(
    cwd=str(self.project_root),
    permission_mode="bypassPermissions",
    setting_sources=["project"],
    tools={"type": "preset", "preset": "claude_code"},
    # Pass API credentials through SDK env parameter
    env={
        "ANTHROPIC_API_KEY": "YOUR_API_KEY_HERE",
        "ANTHROPIC_BASE_URL": "YOUR_BASE_URL_HERE",
    },
    # ... rest of configuration
)
```

## Test Results

| Before Fix | After Fix |
|------------|-----------|
| ~19-20s → Failed (no file) | 55s → ✅ Success (file created) |
| Auth errors | No errors |

## Files Modified

- `/home/admin/workspaces/task-queue/task_queue/executor.py` - Added `env` parameter

## Related Files

- `/home/admin/workspaces/task-queue/task_queue/daemon.py` - Background daemon
- `/home/admin/workspaces/task-queue/task_queue/task_runner.py` - Task runner
- `/home/admin/.config/systemd/user/task-queue.service` - Systemd service
