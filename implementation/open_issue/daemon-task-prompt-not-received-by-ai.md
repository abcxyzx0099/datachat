# Issue: Daemon Task Execution - Prompt Not Received by AI

**Status:** 🔴 OPEN - NOT SOLVED (SDK upgrade fixed timeout but skill still not invoked)
**Created:** 2026-02-06
**Updated:** 2026-02-06 (Double-check revealed issue persists)
**Related:** task-queue module, bundled CLI, Claude Agent SDK, MCP servers

---

## Issue Description

The task-queue daemon authenticated successfully with the custom API endpoint (bigmodel.cn), but tasks executed by the daemon did not create the expected files. The AI responded with "I don't see a specific task or question in my message" instead of executing the `/task-worker` skill.

### Observed Behavior (Before Fix)

When a task was queued and executed by the daemon:
- ✅ Authentication succeeded (no auth errors)
- ✅ Prompt was sent from Python code (confirmed by logging)
- ✅ Bundled CLI started and connected to API
- ❌ AI responded with generic message: "I don't see a specific task or question in my message"
- ❌ `/task-worker` skill command was not recognized
- ❌ No files were created

---

## Root Cause Analysis (Updated)

### Initial Hypothesis (INCORRECT)

Initially believed that the `system_prompt` parameter was required for the `/task-worker` skill to work.

### NEW FINDING: The Issue Is Environment-Specific!

After creating a standalone test script (`/home/admin/workspaces/datachat/temp/test_no_system_prompt.py`), we discovered:

| Environment | Without system_prompt | Result |
|-------------|----------------------|--------|
| **Simple Python script** | ✅ | **WORKS!** |
| **Task-queue daemon** | ❌ | FAILS |

### Test Results

**Standalone Test Script (NO system_prompt):**
```python
options = ClaudeAgentOptions(
    cwd="/home/admin/workspaces/datachat",
    permission_mode="bypassPermissions",
    setting_sources=["project"],
    tools={"type": "preset", "preset": "claude_code"},
    env={
        "ANTHROPIC_API_KEY": _ANTHROPIC_AUTH_TOKEN,
        "ANTHROPIC_BASE_URL": _ANTHROPIC_BASE_URL
    },
    # NO system_prompt
)
```

**Result:** ✅ **WORKS!** The `/task-worker` skill was invoked and task executed successfully.

```
Message 2: AssistantMessage
  Text: I'll read and execute the task document....
Message 20: ResultMessage
  Subtype: success
  ✅ Success!
```

### Conclusion

The `system_prompt` parameter is **NOT inherently required** for the `/task-worker` skill to work. The issue is **specific to the daemon environment** (systemd service).

### Possible Environmental Differences

| Factor | Script | Daemon |
|--------|--------|--------|
| **TTY/Stdin** | Has terminal | No terminal (systemd) |
| **Environment** | User shell | systemd service |
| **Process context** | Interactive | Background service |
| **Session type** | Login session | Service session |

---

## Current Workaround

While the root cause (environment difference) remains uninvestigated, adding `system_prompt` provides a working solution:

```python
system_prompt="""You are a TASK COORDINATOR. Your ONLY job is to coordinate work through sub-agents using the Task tool.

CRITICAL RULES:
1. You are FORBIDDEN from doing any implementation work yourself
2. You MUST ALWAYS use the Task tool to spawn sub-agents for ALL implementation work
3. NEVER use Write, Edit, NotebookEdit, or any implementation tool directly
4. DO NOT think "this is simple, I'll do it yourself" - ALWAYS use Task tool

Your workflow for the task-worker skill:
1. Read the task document
2. Spawn Implementation Agent: Use Task tool with subagent_type="general-purpose"
3. Spawn Auditor Agent: Use Task tool with subagent_type="general-purpose"
4. Check audit verdict
5. If audit fails (FAIL, NEEDS_REVISION), iterate: spawn agents again with feedback
6. Return final result

You MUST use the Task tool for ALL implementation. DO NOT take shortcuts.
"""
```

**File Modified:** `/home/admin/workspaces/task-queue/task_queue/executor.py`

---

## Verification

With `system_prompt` added, tasks execute successfully:

| Test | Result |
|------|--------|
| Task executed by daemon | ✅ Completed in 43.9 seconds |
| Output file created | ✅ `/home/admin/workspaces/datachat/test-prompt-fix-success.txt` |
| File content correct | ✅ "Prompt fix verified!" |

---

## Investigation Results Summary

### Tests Performed

| Test Configuration | Result |
|-------------------|--------|
| `tools` + `system_prompt` (daemon) | ✅ Works |
| `tools` only (daemon) | ❌ Fails |
| No `tools` (daemon) | ❌ Fails |
| `tools` only (standalone script) | ✅ Works |
| SDK 0.1.23 vs 0.1.30 | No difference |
| `allowed_tools` instead of `system_prompt` | ❌ Fails |

### Key Insight

The `system_prompt` works around the issue by explicitly instructing the AI on how to behave. This suggests the daemon environment may be missing some context or configuration that the standalone script has naturally.

---

## Open Questions

1. **Why does the daemon behave differently from a standalone script?**
   - Is it a systemd service environment issue?
   - Is it related to TTY/stdin handling?
   - Are there missing environment variables?

2. **Can we fix the root cause instead of using `system_prompt` as a workaround?**
   - Investigate daemon environment differences
   - Check for missing CLI flags when run as service
   - Compare process contexts

---

## Lessons Learned

1. **Environment matters** - The same code can behave differently in daemon vs interactive environments
2. **Test in isolation** - Creating standalone test scripts helped identify the real issue
3. **`system_prompt` is a workaround** - Not the root cause, but provides a working solution
4. **Further investigation needed** - The daemon environment issue remains unresolved

---

## Related Files

- `/home/admin/workspaces/task-queue/task_queue/executor.py` - Task executor (with system_prompt workaround)
- `/home/admin/workspaces/datachat/temp/test_no_system_prompt.py` - Standalone test script
- `/home/admin/.config/systemd/user/task-queue.service` - Daemon service configuration

---

## CRITICAL NEW FINDING (2026-02-06 07:00)

### Root Cause Identified: 10-Second Execution Timeout!

The daemon tasks are being killed by an **execution timeout of 10,000ms (10 seconds)**.

**Evidence from daemon logs:**
```
Feb 06 07:03:49 task-queue[1442902]: [task-XXX] STDERR: MCP server connections starting...
Feb 06 07:04:49 task-queue[1442902]: [task-XXX] STDERR: Execution timeout: 10000ms
Feb 06 07:05:03 task-queue[1442902]: [task-XXX] Task exception: Exception: Command failed with exit code -15 (SIGTERM)
```

**What's happening:**
1. Task is picked up by daemon ✅
2. Bundled CLI starts ✅
3. MCP servers connect ✅
4. After ~60 seconds, "Execution timeout: 10000ms" is logged ❌
5. CLI process receives SIGTERM (killed) ❌
6. Task is archived (marked as "success" but was actually killed) ❌

### Additional Discovery: Wrong Bundled CLI Path

The daemon is using the **system** bundled CLI instead of the **venv** bundled CLI:

| Context | Bundled CLI Path |
|---------|------------------|
| Direct script (works) | `/home/admin/workspaces/datachat/.venv/lib/python3.13/site-packages/...` |
| Daemon (fails) | `/home/admin/.local/lib/python3.13/site-packages/...` |

Both CLIs have identical MD5 checksums, so the binary itself is not the issue. The problem is likely:
1. The system bundled CLI may have different MCP server configurations
2. Or there's a 10-second timeout configured somewhere that's killing the process

### Investigation Needed

- Find where the 10-second execution timeout is configured
- Check if MCP server timeout settings differ between system and venv bundled CLIs
- Verify if `CLAUDE_CODE_STREAM_CLOSE_TIMEOUT` or similar env vars are involved

---

## ROOT CAUSE FOUND: SDK Version Mismatch (2026-02-06 15:18)

### The Real Issue: Old SDK Version with Timeout Bug

After investigating the bundled CLI paths and SDK versions, the root cause was found:

| Environment | SDK Version | Bundled CLI MD5 | Status |
|-------------|-------------|-----------------|--------|
| **task-queue venv** | v0.1.29 | `69e1be0b...` (Feb 4) | ❌ Has 10s timeout bug |
| **datachat venv** | v0.1.30 | `ec325bb1...` (Feb 6) | ✅ Fixed |

### What Happened

The task-queue venv had an **older SDK version (v0.1.29)** with a bundled CLI that had a 10-second execution timeout bug. When the daemon executed tasks:
1. It imported SDK from task-queue venv (v0.1.29)
2. The old bundled CLI had the timeout bug
3. Tasks were killed after 10 seconds with SIGTERM

### The Fix

Updated the task-queue venv SDK to v0.1.30:

```bash
/home/admin/workspaces/task-queue/.venv/bin/pip install --upgrade claude-agent-sdk
```

**Result:**
- ✅ SDK updated from v0.1.29 to v0.1.30
- ✅ Bundled CLI now matches datachat venv (MD5: `ec325bb1...`)
- ✅ 10-second timeout bug is fixed
- ✅ Tasks execute successfully without timeout

### Verification Test

```bash
# Test execution with SDK v0.1.30
executor = SyncTaskExecutor(project_root=Path('/home/admin/workspaces/datachat'))
result = executor.execute(Path('tasks/task-documents/task-test-sdk-update.md'))
# Result: Success: True, no timeout errors
```

### Why the Direct Tests Worked

The incremental tests (`/home/admin/workspaces/datachat/temp/incremental_test_*.py`) worked because they were using the datachat venv's SDK (v0.1.30), which has the newer bundled CLI without the timeout bug.

---

## RESOLUTION: Issue Fixed (2026-02-06 15:20)

**Status:** ✅ FIXED - SDK v0.1.30 resolves the 10-second timeout issue

### Action Taken

Updated `claude-agent-sdk` in task-queue venv from v0.1.29 to v0.1.30.

### Files Modified

- `/home/admin/workspaces/task-queue/.venv/` - Python venv with upgraded SDK

### Next Steps

1. Move this issue to `implementation/closed_issue/`
2. Test the daemon with real tasks to verify the fix
3. Add SDK version pinning to requirements to prevent regression

---

## DOUBLE-CHECK RESULTS (2026-02-06 15:30)

After upgrading SDK to v0.1.30, the 10-second timeout was fixed. However, the core issue persists:

### Test Results

| Test | Expected | Actual | Status |
|------|----------|--------|--------|
| Task execution | Output file created | File NOT created | ❌ FAIL |
| Task status | Completed | Still "Pending" in archive | ❌ FAIL |
| `/task-worker` invoked | Skill executes | AI responds with generic message | ❌ FAIL |

### Root Cause Identified: `system_prompt` Not Being Applied

The CLI logs show:
```
[SystemPrompt] path=simple proactive=false
```

This means the CLI is using a **"simple" preset system prompt** instead of the custom TASK COORDINATOR prompt passed via `--system-prompt`.

### Investigation Findings

1. **SDK passes `--system-prompt` correctly** - Verified by inspecting the built command
2. **CLI ignores it when `--setting-sources=project` is set** - The project settings override the command-line prompt
3. **Without `--setting-sources`**: Skills are NOT loaded (0 skills), so `/task-worker` doesn't exist
4. **With `--setting-sources`**: Skills ARE loaded, but `system_prompt` is overridden

### Catch-22

| Setting | Skills Loaded | Custom System Prompt |
|---------|---------------|---------------------|
| `setting_sources=['project']` | ✅ Yes (9 skills) | ❌ No (uses "simple") |
| No `setting_sources` | ❌ No (0 skills) | ✅ Yes (custom prompt) |

### Attempts to Fix

1. ❌ **Local settings file** - Created `.claude/local/settings.json` with `systemPrompt` - CLI ignored it
2. ❌ **Command-line `--system-prompt`** - Ignored when `--setting-sources=project` is set
3. ⏳ **Need to investigate** - How to make CLI respect custom system_prompt while loading project skills

### Current Status

**NOT SOLVED** - The issue requires further investigation into:
- How the CLI processes system_prompt when setting_sources is set
- Whether there's a different way to configure system_prompt for project skills
- Alternative approaches to invoke `/task-worker` without relying on system_prompt

