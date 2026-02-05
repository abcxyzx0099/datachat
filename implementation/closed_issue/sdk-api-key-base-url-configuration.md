# Issue: Claude Agent SDK - API Key and Base URL Configuration

**Status**: CLOSED ✅

**Created**: 2026-02-06
**Resolved**: 2026-02-06

---

## Problem

The task-queue daemon needed to authenticate with a custom API endpoint (bigmodel.cn) using a non-standard auth token format. Initial attempts to configure authentication failed with "invalid x-api-key" errors.

## Root Cause

1. **Token Format**: The token `cef62fd30a0e4ddf826ccba67b7a1e78.iSRcFQPBKBt4MQ52` does not match the standard Anthropic API key format (`sk-ant-xxx`)

2. **Custom Endpoint**: The token is for `https://open.bigmodel.cn/api/anthropic`, a proxy endpoint that requires both:
   - API key/token
   - Base URL

3. **Configuration Methods**:
   - `ANTHROPIC_AUTH_TOKEN` vs `ANTHROPIC_API_KEY` - Both work for this endpoint
   - `settings.json` apiKey + baseUrl - Works but may have issues when overridden by env vars

## Solution

### Method 1: Using SDK's `env` Parameter (Recommended)

Pass credentials through the SDK's `env` parameter to the bundled CLI subprocess:

**File**: `/home/admin/workspaces/task-queue/.env`
```bash
# Anthropic API Configuration for task-queue daemon
ANTHROPIC_AUTH_TOKEN=cef62fd30a0e4ddf826ccba67b7a1e78.iSRcFQPBKBt4MQ52
ANTHROPIC_BASE_URL=https://open.bigmodel.cn/api/anthropic
```

**File**: `/home/admin/workspaces/task-queue/task_queue/executor.py`
```python
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file at module import time
_ENV_PATH = Path("/home/admin/workspaces/task-queue/.env")
load_dotenv(_ENV_PATH, override=True)

_ANTHROPIC_AUTH_TOKEN = os.getenv("ANTHROPIC_AUTH_TOKEN", "")
_ANTHROPIC_BASE_URL = os.getenv("ANTHROPIC_BASE_URL", "")

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
```

### Method 2: Using settings.json

**File**: `~/.config/claude/settings.json`
```json
{
  "apiKey": "cef62fd30a0e4ddf826ccba67b7a1e78.iSRcFQPBKBt4MQ52",
  "baseUrl": "https://open.bigmodel.cn/api/anthropic"
}
```

## Key Findings

### Environment Variable Names

| Variable | Purpose | Works? |
|----------|---------|--------|
| `ANTHROPIC_API_KEY` | Standard API key | ✅ Yes |
| `ANTHROPIC_AUTH_TOKEN` | Auth token | ✅ Yes (for this endpoint) |
| `ANTHROPIC_BASE_URL` | Custom endpoint | ✅ Required for custom endpoints |

### Configuration Best Practices

1. **Use `env` parameter** - Cleaner than `os.environ` as it only affects the subprocess
2. **Store credentials in `.env`** - Keep tokens out of code
3. **Use `python-dotenv`** - Load env vars at module import time
4. **Never hardcode credentials** - Always use environment variables

### Setting Sources (Scope)

```python
SettingSource = Literal["user", "project", "local"]
```

- `user`: `~/.config/claude/settings.json`
- `project`: `<project_root>/.claude/settings.json`
- `local`: Current directory settings

Current configuration uses `setting_sources=["project"]`.

## Test Script

Created `/home/admin/workspaces/task-queue/test_sdk_call.py` to verify authentication:

```bash
cd /home/admin/workspaces/task-queue
python3 test_sdk_call.py
```

**Expected Output**:
```
✅ Environment variables loaded successfully
✅ SDK call successful!
Response: Hello from Claude SDK!
✅ Authentication is working correctly!
```

## Files Modified

- `/home/admin/workspaces/task-queue/.env` - Added ANTHROPIC_AUTH_TOKEN and ANTHROPIC_BASE_URL
- `/home/admin/workspaces/task-queue/.env.example` - Updated template
- `/home/admin/workspaces/task-queue/task_queue/executor.py` - Added python-dotenv and env parameter
- `/home/admin/workspaces/task-queue/.gitignore` - Added `.env` to prevent committing credentials
- `/home/admin/workspaces/task-queue/test_sdk_call.py` - Created test script

## Related Issues

- `daemon-task-authentication-failure.md` - Previous authentication issue (resolved)
- `task-worker-skill-subagent-enforcement-via-system-prompt.md` - System prompt configuration

## Verification Command

```bash
# Test authentication
python3 /home/admin/workspaces/task-queue/test_sdk_call.py

# Check daemon status
task-queue status
```
