# Multi-Project Task Monitor Troubleshooting Guide

## Service not starting or API authentication errors

### Check if .env file exists

```bash
# Verify .env file location
ls -la ~/.config/task-monitor/.env

# Check if service is configured to use it
grep EnvironmentFile ~/.config/systemd/user/task-monitor.service
```

### Create or update .env file

```bash
# Ensure directory exists
mkdir -p ~/.config/task-monitor

# Create .env file with your credentials
cat > ~/.config/task-monitor/.env << EOF
# Task Monitor Environment Configuration
# This file is sourced by the systemd service

# Claude API Configuration
ANTHROPIC_BASE_URL=https://open.bigmodel.cn/api/anthropic
ANTHROPIC_MODEL=glm-4.7
ANTHROPIC_AUTH_TOKEN=your_actual_token_here
EOF

# Reload and restart service
systemctl --user daemon-reload
systemctl --user restart task-monitor.service
```

## Project registration issues

### Check registered projects

```bash
# Check registry file directly
cat ~/.config/task-monitor/registered.json
```

### Manually register a project

```bash
# Edit registry file
nano ~/.config/task-monitor/registered.json

# Format:
{
  "projects": {
    "project-name": {
      "path": "/full/path/to/project",
      "enabled": true,
      "registered_at": "2026-01-29T12:00:00"
    }
  }
}

# Restart service to apply changes
systemctl --user restart task-monitor.service
```

### Project not being monitored

```bash
# Check if project is enabled
cat ~/.config/task-monitor/registered.json

# Verify project directory structure exists
ls -la /path/to/project/tasks/
```

## Tasks not being processed

### Check service status

```bash
# Check if service is running
systemctl --user status task-monitor.service

# Check if watchdog is running for your project
journalctl --user -u task-monitor.service | grep "Observer started"
```

### Check specific project

```bash
# Verify project directory structure
ls -la /home/admin/workspaces/datachat/tasks/
ls -la /home/admin/workspaces/datachat/tasks/results/
ls -la /home/admin/workspaces/datachat/tasks/state/
ls -la /home/admin/workspaces/datachat/tasks/logs/

# Check monitor logs for that project
tail -50 /home/admin/workspaces/datachat/tasks/logs/monitor.log

# Check queue state
cat /home/admin/workspaces/datachat/tasks/state/queue_state.json
```

### Test with a valid task file

```bash
# Task files must match pattern: task-????????-??????-*.md
touch /home/admin/workspaces/datachat/tasks/pending/task-test-$(date +%Y%m%d-%H%M%S).md

# Check if detected
journalctl --user -u task-monitor.service -f | grep "detected"
```

## Viewing logs

```bash
# View systemd service logs (primary source - recommended)
journalctl --user -u task-monitor.service -f
journalctl --user -u task-monitor.service -n 100
journalctl --user -u task-monitor.service --since "1 hour ago"

# Filter logs by specific task
journalctl --user -u task-monitor.service -f | grep "task-xxx"

# View task execution results (includes stdout/stderr/duration)
cat /home/admin/workspaces/datachat/tasks/results/task-xxx-xxx.json

# View task output only
cat /home/admin/workspaces/datachat/tasks/results/task-xxx-xxx.json | jq '.stdout'

# View task duration
cat /home/admin/workspaces/datachat/tasks/results/task-xxx-xxx.json | jq '.duration_seconds'

# View logs for specific project
tail -f /home/admin/workspaces/datachat/tasks/logs/monitor.log

# View queue state
cat /home/admin/workspaces/datachat/tasks/state/queue_state.json
```

**Task Result JSON includes:**
- `stdout` - Full task output
- `stderr` - Error output (if any)
- `duration_seconds` - Execution time
- `started_at`, `completed_at` - Timestamps
- `status` - Task completion status

## Common issues and solutions

| Issue | Solution |
|-------|----------|
| Service won't start | Check `.env` file exists, verify Python path in service file (`/home/admin/workspaces/task-monitor/.venv/bin/python`) |
| API authentication errors | Create/update `~/.config/task-monitor/.env` |
| Tasks not processing | Check project is registered in `registered.json`, verify tasks directory |
| Import errors | Verify venv at `/home/admin/workspaces/task-monitor/.venv/` has required packages |
| Project not monitored | Edit `~/.config/task-monitor/registered.json` to add project |
| Wrong project context | Check executor has correct `cwd` for project |
| Tasks not detected | Verify task name matches pattern `task-????????-??????-*.md` |

## Multi-project specific issues

### Task executes in wrong project

```bash
# Verify project path in registry
cat ~/.config/task-monitor/registered.json | grep project-name

# Edit registry to fix path
nano ~/.config/task-monitor/registered.json
```

### One project blocking others

**This should not happen** - projects execute in parallel. If you see this:

```bash
# Check service logs for each project
journalctl --user -u task-monitor.service | grep -E "\[.*\] (Starting|completed)"

# Each project should have independent queue processors
```

### Service crashes after task execution (trio cancel scope error)

**Symptoms:**
- Service exits with `RuntimeError: Attempted to exit cancel scope in a different task than it was entered in`
- Service auto-restarts by systemd
- Tasks complete successfully but service crashes during cleanup

**Root Cause:**
The Claude Agent SDK documentation explicitly states: *"avoid using `break` to exit early from the iteration. Exiting prematurely with `break` can cause asyncio cleanup issues."*

The original task executor code used `break` to exit the async for loop when receiving success/error messages, causing trio (SDK's internal async library) cancel scope errors during cleanup.

**Solution:**

Update `/home/admin/workspaces/task-monitor/task_monitor/task_executor.py` to consume all messages naturally instead of using `break`:

```python
# ❌ WRONG - Causes cancel scope error
async for message in q:
    if message.subtype == 'success':
        # ... process result ...
        break  # ❌ Don't do this!

# ✅ CORRECT - Consume all messages naturally
task_complete = False
async for message in q:
    if task_complete:
        continue  # Skip but don't break
    if message.subtype == 'success':
        # ... process result ...
        task_complete = True  # Mark complete, let loop finish naturally
```

**Apply the fix:**

```bash
# Edit the file directly
nano /home/admin/workspaces/task-monitor/task_monitor/task_executor.py

# Then restart the service
systemctl --user restart task-monitor.service

# Verify it's working
systemctl --user status task-monitor.service
```

**Verify the fix:**

```bash
# Check for cancel scope errors
journalctl --user -u task-monitor.service --since "5 minutes ago" | grep "cancel scope"
# Should return nothing if fix is working

# Check service uptime (should be continuous, no restarts)
systemctl --user status task-monitor.service | grep "Active:"
```

**References:**
- [Claude Agent SDK Python Documentation](https://platform.claude.com/docs/en/agent-sdk/en/api/agent-sdk/python)
- Search for: "avoid using break to exit early from the iteration"

## Query task status

```bash
# For default project (datachat)
task-monitor

# For a specific project
task-monitor -p /home/admin/workspaces/{project}

# Show specific task
task-monitor task-20260131-204500-fix-auth-timeout

# Show queue state
task-monitor queue

# Show queue for specific project
task-monitor -p /home/admin/workspaces/{project} queue
```

## Reinstallation

If you need to reinstall the service:

```bash
# Stop service
systemctl --user stop task-monitor.service

# Navigate to project directory
cd /home/admin/workspaces/task-monitor

# Reinstall (editable mode)
pip install -e .

# Reload systemd
systemctl --user daemon-reload

# Start service
systemctl --user start task-monitor.service

# Verify status
systemctl --user status task-monitor.service
```

## Getting help

```bash
# Check service status
systemctl --user status task-monitor.service

# View logs
journalctl --user -u task-monitor.service -n 50

# Check registered projects
cat ~/.config/task-monitor/registered.json
```
