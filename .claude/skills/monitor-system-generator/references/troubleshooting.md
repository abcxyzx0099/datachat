# Multi-Project Task Monitor Troubleshooting Guide

## Service not starting or API authentication errors

### Check if .env file exists

```bash
# Verify .env file location
ls -la ~/.config/task-monitor/.env

# Check if service is configured to use it
grep EnvironmentFile /etc/systemd/system/task-monitor.service
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
sudo systemctl daemon-reload
sudo systemctl restart task-monitor
```

## Project registration issues

### Check registered projects

```bash
# List all registered projects
task-monitor-control list

# Check registry file directly
cat ~/.config/task-monitor/registered.json
```

### Re-register a project

```bash
# Unregister and re-register
task-monitor-control unregister project-name
task-monitor-control register /path/to/project --name project-name
```

### Project not being monitored

```bash
# Check if project is enabled
task-monitor-control list

# Enable the project
task-monitor-control enable project-name

# Restart service to apply changes
task-monitor-control restart
```

## Permission errors

```bash
# Ensure correct ownership of /opt/task-monitor/
sudo chown -R root:root /opt/task-monitor/

# Ensure correct ownership of project directories
sudo chown -R admin:admin /home/admin/workspaces/datachat/
sudo chown -R admin:admin /home/admin/workspaces/project-b/
```

## Tasks not being processed

### Check service status

```bash
# Check if service is running
sudo systemctl status task-monitor

# Check if watchdog is running for your project
sudo journalctl -u task-monitor | grep "Observer started"
```

### Check specific project

```bash
# Verify project directory structure
ls -la /home/admin/workspaces/datachat/tasks/
ls -la /home/admin/workspaces/datachat/results/
ls -la /home/admin/workspaces/datachat/state/
ls -la /home/admin/workspaces/datachat/logs/

# Check monitor logs for that project
tail -50 /home/admin/workspaces/datachat/logs/monitor.log

# Check queue state
cat /home/admin/workspaces/datachat/state/queue_state.json
```

### Test with a valid task file

```bash
# Task files must match pattern: task-*-????????-??????.md
touch /home/admin/workspaces/datachat/tasks/task-test-$(date +%Y%m%d-%H%M%S).md

# Check if detected
sudo journalctl -u task-monitor -f | grep "detected"
```

## Viewing logs

```bash
# View systemd service logs (primary source - recommended)
sudo journalctl -u task-monitor -f
sudo journalctl -u task-monitor -n 100
sudo journalctl -u task-monitor --since "1 hour ago"

# Filter logs by specific task
sudo journalctl -u task-monitor -f | grep "task-xxx"

# View task execution results (includes stdout/stderr/duration)
cat /home/admin/workspaces/datachat/results/task-xxx-xxx.json

# View task output only
cat /home/admin/workspaces/datachat/results/task-xxx-xxx.json | jq '.stdout'

# View task duration
cat /home/admin/workspaces/datachat/results/task-xxx-xxx.json | jq '.duration_seconds'

# View logs for specific project
tail -f /home/admin/workspaces/datachat/logs/monitor.log

# View queue state
cat /home/admin/workspaces/datachat/state/queue_state.json
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
| Service won't start | Check `.env` file exists, verify Python path in service file (`/opt/task-monitor/.venv/bin/python`) |
| API authentication errors | Create/update `~/.config/task-monitor/.env` |
| Permission denied | Fix file ownership (admin for projects, root for /opt/) |
| Tasks not processing | Check project is registered and enabled, verify tasks directory |
| Import errors | Verify dedicated venv at `/opt/task-monitor/.venv/` has required packages |
| Project not monitored | Use `task-monitor-control list` to verify registration |
| Wrong project context | Check executor has correct `cwd` for project |
| Tasks not detected | Verify task name matches pattern `task-*-????????-??????.md` |

## Multi-project specific issues

### Task executes in wrong project

```bash
# Verify project path in registry
cat ~/.config/task-monitor/registered.json | grep project-name

# Re-register with correct path
task-monitor-control unregister project-name
task-monitor-control register /correct/path --name project-name
```

### One project blocking others

**This should not happen** - projects execute in parallel. If you see this:

```bash
# Check service logs for each project
sudo journalctl -u task-monitor | grep -E "\[.*\] (Starting|completed)"

# Each project should have independent queue processors
```

### Service crashes after task execution

Known issue with SDK cleanup (non-fatal):

```bash
# Check if service auto-restarted
sudo systemctl status task-monitor

# The task should still complete successfully
ls -la /home/admin/workspaces/datachat/results/
```

## Query task status

```bash
# For a specific project (uses installed CLI)
task-monitor -p /home/admin/workspaces/{project}

# Show queue state
task-monitor -p /home/admin/workspaces/{project} queue
```

## Reinstallation

If you need to reinstall the service:

```bash
# Stop service
sudo systemctl stop task-monitor

# Reload systemd
sudo systemctl daemon-reload

# Start service
sudo systemctl start task-monitor

# Verify status
sudo systemctl status task-monitor
```

## Getting help

```bash
# Check service status
task-monitor-control status

# List monitored projects
task-monitor-control list

# View logs
sudo journalctl -u task-monitor -n 50
```
