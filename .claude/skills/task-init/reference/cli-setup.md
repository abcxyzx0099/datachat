# Task Monitor CLI Setup

Complete guide for installing and configuring the task-monitor CLI command.

---

## Overview

The task-monitor CLI provides commands for task system initialization, queue management, and status monitoring.

---

## CLI Command Name

**Command:** `task-monitor`

**Module:** `task_monitor.cli`

**Package Name:** `task-monitor` (Python package)

---

## Installation Methods

### Method 1: Editable Install (Recommended for Development)

**Best for:** Development, testing, when code changes frequently

```bash
cd /home/admin/workspaces/task-monitor

# Install in editable mode
.venv/bin/pip install -e . --break-system-packages

# CLI becomes available
.venv/bin/task-monitor status
```

**Pros:** Changes to code are immediately reflected
**Cons:** Requires activation of venv

### Method 2: pipx Installation (Recommended for Production)

**Best for:** Production, system-wide availability

```bash
# Install pipx if not available
python3 -m pip install --user pipx
python3 -m pipx ensurepath

# Install task-monitor
pipx install /home/admin/workspaces/task-monitor
```

**Pros:** Available globally without venv activation
**Cons:** Need to reinstall after code changes

### Method 3: Wrapper Script (System-Wide)

**Best for:** Making CLI available without PATH modification

```bash
# Create wrapper script
cat > ~/.local/bin/task-monitor <<'EOF'
#!/bin/bash
exec /home/admin/workspaces/task-monitor/.venv/bin/python -m task_monitor.cli "$@"
EOF

# Make executable
chmod +x ~/.local/bin/task-monitor

# Ensure ~/.local/bin is in PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# CLI now available globally
task-monitor status
```

---

## Verification

### Check CLI is Available

```bash
# Check if command is found
which task-monitor

# Or check if it's in PATH
command -v task-monitor

# Test the command
task-monitor --help
```

### Test Core Commands

```bash
# Status check
task-monitor status

# List sources
task-monitor sources list

# Check version
task-monitor --version 2>/dev/null || echo "Version not implemented"
```

---

## CLI Commands Reference

### System Commands

| Command | Purpose |
|---------|---------|
| `init` | Initialize task system from current directory |
| `status` | Show system status (overview) |
| `status --detailed` | Show detailed status with running tasks |

### Sources Commands

| Command | Purpose |
|---------|---------|
| `sources list` | List registered Task Source Directories |
| `sources add <path> --id <id>` | Add a Task Source Directory |
| `sources rm --source-id <id>` | Remove a Task Source Directory |

### Tasks Commands

| Command | Purpose |
|---------|---------|
| `tasks show <task-id>` | Show task document path |
| `tasks result <task-id>` | Show result JSON path |
| `tasks cancel <task-id>` | Cancel a running task |

### Workers Commands

| Command | Purpose |
|---------|---------|
| `workers status` | Show detailed worker status |
| `workers list` | List workers summary |

### Logs Command

| Command | Purpose |
|---------|---------|
| `logs` | Show daemon logs (exit with Ctrl+C) |
| `logs --follow` | Follow logs live |
| `logs --lines <n>` | Show last N lines |

---

## Direct Python Module Usage

If CLI wrapper is not available, run as Python module:

```bash
# Instead of: task-monitor status
# Use:
python -m task_monitor.cli status

# With full path:
/home/admin/workspaces/task-monitor/.venv/bin/python -m task_monitor.cli status
```

---

## pyproject.toml Configuration

The CLI is registered in `pyproject.toml`:

```toml
[project.scripts]
task-monitor = "task_monitor.cli:main"
task-monitor-daemon = "task_monitor.daemon:main"
```

**After changing this, reinstall the package:**
```bash
.venv/bin/pip install -e . --break-system-packages --force-reinstall
```

---

## Shell Completion

### Bash Completion

Add to `~/.bashrc`:

```bash
# Task Monitor completion
eval "$(_TASK_MONITOR_COMPLETE=bash_source /home/admin/workspaces/task-monitor/.venv/bin/task-monitor)"
```

### Or register completion script

```bash
# Register completion for task-monitor
register-python-argcomplete --shell bash task-monitor
```

---

## Troubleshooting

### Command Not Found

**Symptom:** `task-monitor: command not found`

**Solutions:**

1. **Use full Python module path:**
   ```bash
   /home/admin/workspaces/task-monitor/.venv/bin/python -m task_monitor.cli status
   ```

2. **Install with pipx:**
   ```bash
   pipx install /home/admin/workspaces/task-monitor
   ```

3. **Create wrapper script:** (See Method 3 above)

### Module Not Found

**Symptom:** `ModuleNotFoundError: No module named 'task_monitor'`

**Solution:**
```bash
cd /home/admin/workspaces/task-monitor
.venv/bin/pip install -e . --break-system-packages
```

### Permission Denied

**Symptom:** `Permission denied` when running CLI

**Solution:**
```bash
# Fix venv permissions
chmod +x /home/admin/workspaces/task-monitor/.venv/bin/python

# Fix wrapper script permissions
chmod +x ~/.local/bin/task-monitor
```

---

## Environment Variables

The CLI reads configuration from:

| Variable | Description | Default |
|----------|-------------|---------|
| `TASK_MONITOR_CONFIG` | Path to config file | `~/.config/task-monitor/config.json` |
| `PYTHONPATH` | Path to task-monitor module | Auto-detected |

---

## Related Documents

- **[Service Setup](./service-setup.md)** - Task Monitor systemd service configuration
- **[../task-init/SKILL.md](../SKILL.md)** - Main task initialization skill
