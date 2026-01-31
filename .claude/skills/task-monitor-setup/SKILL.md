---
name: task-monitor-setup
description: "Create and configure the multi-project task monitoring system with watchdog file monitoring and Claude Agent SDK integration. Use when: setting up a new task monitor system; installing from scratch; understanding system architecture; configuring the monitor; registering new projects. For detailed architecture, see [architecture.md](references/architecture.md)."
---

# Multi-Project Task Monitor System

## Quick Overview

Single service that monitors multiple projects, watching each project's `/tasks/task-monitor/pending/` directory and executing tasks **sequentially within each project** (but **parallel across projects**).

## Execution Model

```
Project A (sequential) ──┐
                         ├─→ PARALLEL ──→ Tasks execute independently
Project B (sequential) ──┘
```

- **Within project**: Sequential FIFO queue (one task at a time)
- **Across projects**: Parallel execution (projects run independently)

---

## Creating the Task Monitor System

### Quick Install

The install script is included in this skill at [references/install-service.sh](references/install-service.sh).

```bash
# Run the install script
sudo bash /opt/task-monitor/install-service.sh
```

This will:
1. Create virtual environment at `/opt/task-monitor/.venv/`
2. Install dependencies (claude-agent-sdk, watchdog, pydantic)
3. Create `pyproject.toml` for CLI installation
4. Install CLI command via `pip install --user`
5. Create systemd user service
6. Start the service

### Manual Installation

If you prefer to install manually:

```bash
# 1. Create virtual environment
sudo python3 -m venv /opt/task-monitor/.venv

# 2. Install dependencies
sudo /opt/task-monitor/.venv/bin/pip install claude-agent-sdk watchdog pydantic

# 3. Create pyproject.toml (see references/install-service.sh for content)

# 4. Install CLI
pip install --user --break-system-packages /opt/task-monitor

# 5. Create systemd user service (see references/install-service.sh for content)

# 6. Start service
systemctl --user enable task-monitor
systemctl --user start task-monitor
```

### Verify Installation

```bash
# Check service status
systemctl --user status task-monitor

# Test CLI
task-monitor --help

# Check queue status
task-monitor queue
```

---

## Task Naming Convention

**Format:** `task-YYYYMMDD-HHMMSS-<description>.md`

**Example:** `task-20260130-143000-system-verification.md`

- `task-` - Fixed prefix
- `YYYYMMDD-HHMMSS` - Timestamp (for chronological sorting)
- `<description>` - Short, kebab-case description
- `.md` - Markdown document

**Pattern (glob):** `task-????????-??????-*.md`

## Key Paths

| Purpose | Path |
|---------|------|
| Skill directory | `.claude/skills/task-monitor-setup/` |
| Source code | `/home/admin/workspaces/task-monitor/` |
| System service | `~/.config/systemd/user/task-monitor.service` |
| Configuration | `~/.config/task-monitor/` |
| CLI command | `/home/admin/workspaces/task-monitor/.venv/bin/task-monitor` |
| CLI source | `/home/admin/workspaces/task-monitor/task_monitor/cli.py` |
| Package config | `/home/admin/workspaces/task-monitor/pyproject.toml` |

## Project Structure (Each Project)

```
{project-root}/
├── tasks/
│   ├── pending/       # Task documents (watched by monitor)
│   ├── results/       # Execution results (JSON)
│   ├── state/         # Queue state per project
│   └── logs/          # Monitor logs per project
└── .claude/
    └── skills/        # Project-specific skills
```

## Quick Commands

```bash
# Service management
systemctl --user status task-monitor       # Check status
systemctl --user restart task-monitor      # Restart service

# Query tasks (per project)
task-monitor queue                         # Show queue status (uses default project)
task-monitor -p /path/to/project queue     # Show queue for specific project
task-monitor task-id                       # Show task status
task-monitor --help                        # Show all options
```

## Systemd Service

**File:** `~/.config/systemd/user/task-monitor.service`

```ini
[Unit]
Description=Task Monitor Daemon (SDK)
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/task-monitor
Environment="PATH=/opt/task-monitor/.venv/bin:/usr/bin"
ExecStart=/opt/task-monitor/.venv/bin/python /opt/task-monitor/monitor_daemon.py
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
```

**Single service** monitoring all registered projects. Uses dedicated virtual environment at `/opt/task-monitor/.venv/`.

## Workflow

```
1. Register project(s) → ~/.config/task-monitor/registered.json
                          ↓
2. Start service → task-monitor.service
                          ↓
3. For each project:
   - Watchdog monitors {project}/tasks/task-monitor/pending/
   - Tasks queued in project-specific FIFO queue
   - Sequential execution within project
   - Results saved to {project}/task-monitor/results/
```

## Directory Structure

```
~/.config/systemd/user/
└── task-monitor.service            # User service for all projects

/opt/task-monitor/                  # System-level infrastructure
├── .venv/                         # Dedicated virtual environment
│   ├── bin/
│   │   ├── python → python3       # Python interpreter for service
│   │   └── ...
│   └── lib/
│       └── python3.13/
│           └── site-packages/
│               ├── claude_agent_sdk/
│               ├── watchdog/
│               └── pydantic/
├── monitor_daemon.py              # Multi-project monitor daemon
├── task_executor.py               # Task executor (with project cwd)
├── models.py                      # Data models
├── cli.py                         # Status CLI source (with main() entry point)
├── pyproject.toml                 # Package config (defines [project.scripts])
└── install-service.sh             # Installation script

~/.config/task-monitor/             # User configuration
└── registered.json                # Project registry

~/.local/
└── bin/
    └── task-monitor                # CLI wrapper (installed via pip install --user)

{project-root}/                    # Per-project (can be multiple)
└── tasks/
    ├── pending/                   # Task documents
    ├── results/                   # Execution results
    ├── state/                     # Queue state
    └── logs/                      # Log files
```

## Project Registry

**Location:** `~/.config/task-monitor/registered.json`

```json
{
  "projects": {
    "datachat": {
      "path": "/home/admin/workspaces/datachat",
      "enabled": true,
      "registered_at": "2026-01-30T12:43:00"
    },
    "project-b": {
      "path": "/home/admin/workspaces/project-b",
      "enabled": true,
      "registered_at": "2026-01-30T13:00:00"
    }
  }
}
```

## Registering a New Codebase/Project

### Manual Registration

```bash
# Create required directories manually
mkdir -p /path/to/project/task-monitor/{pending,results,state,logs}

# Add to registry (~/.config/task-monitor/registered.json)
# Then restart service
systemctl --user restart task-monitor
```

### What Happens During Registration

```
1. Verify project path exists
         ↓
2. Create required directories:
   - {project}/tasks/task-monitor/pending/ (task documents)
   - {project}/tasks/task-monitor/results/ (execution results)
   - {project}/tasks/task-monitor/state/   (queue state)
   - {project}/tasks/task-monitor/logs/    (monitor logs)
         ↓
3. Add to ~/.config/task-monitor/registered.json
         ↓
4. Restart task-monitor.service
         ↓
5. Service creates:
   - Watchdog observer for {project}/tasks/task-monitor/pending/
   - Project-specific queue
   - Project-specific executor (with correct cwd)
```

### Verify Registration

```bash
# Check service logs
journalctl --user -u task-monitor | grep "Observer started"

# Verify project structure
ls -la /home/admin/workspaces/myproject/tasks/task-monitor/pending/
ls -la /home/admin/workspaces/myproject/tasks/task-monitor/pending/
ls -la /home/admin/workspaces/myproject/tasks/task-monitor/results/
ls -la /home/admin/workspaces/myproject/tasks/task-monitor/state/
```

## Detailed Information

- **Full Architecture**: [architecture.md](references/architecture.md) - System layout, multi-project design, file descriptions
## Documentation

- **Architecture**: [architecture.md](references/architecture.md) - System architecture and design
- **Install Script**: [scripts/install-service.sh](scripts/install-service.sh) - Complete installation script
- **Source Code**: All Python modules included in `scripts/`:
  - [scripts/monitor_daemon.py](scripts/monitor_daemon.py) - Multi-project watchdog daemon
  - [scripts/task_executor.py](scripts/task_executor.py) - Task executor with Claude Agent SDK
  - [scripts/models.py](scripts/models.py) - Pydantic data models
  - [scripts/cli.py](scripts/cli.py) - Command-line interface

## Recreating the System from Scratch

If the task monitor system is completely deleted, you can recreate it:

```bash
# 1. Clone or navigate to the task-monitor source
cd /home/admin/workspaces/task-monitor

# 2. Create virtual environment and install
python -m venv .venv
source .venv/bin/activate
pip install -e .

# 3. Create user systemd service
mkdir -p ~/.config/systemd/user
cat > ~/.config/systemd/user/task-monitor.service << 'EOF'
[Unit]
Description=Multi-Project Task Monitor Daemon
After=network.target

[Service]
Type=simple
WorkingDirectory=%h/workspaces/task-monitor
Environment="PATH=%h/workspaces/task-monitor/.venv/bin:/usr/bin"
Environment="PYTHONPATH=%h/workspaces/task-monitor"
EnvironmentFile=%h/.config/task-monitor/.env
ExecStart=%h/workspaces/task-monitor/.venv/bin/python -m task_monitor.monitor_daemon
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
EOF

# 4. Create configuration
mkdir -p ~/.config/task-monitor
cat > ~/.config/task-monitor/.env << 'EOF'
ANTHROPIC_BASE_URL=https://open.bigmodel.cn/api/anthropic
ANTHROPIC_MODEL=glm-4.7
ANTHROPIC_AUTH_TOKEN=your_token_here
EOF

# 5. Create project registry
cat > ~/.config/task-monitor/registered.json << 'EOF'
{
  "projects": {}
}
EOF

# 6. Enable and start service
systemctl --user daemon-reload
systemctl --user enable task-monitor.service
systemctl --user start task-monitor.service
```

## Dependencies

The task monitor uses the virtual environment at `/home/admin/workspaces/task-monitor/.venv/` for independence from project-specific environments.

**Installed dependencies (in venv):**
```
claude-agent-sdk    # Claude Agent SDK
watchdog>=5.0.0     # File system monitoring
pydantic>=2.0.0     # Data validation
```

**CLI Installation (pip install --user):**

The CLI is installed via `pyproject.toml` using setuptools entry points:

```toml
[project.scripts]
task-monitor = "cli:main"
```

**To install/reinstall the CLI:**
```bash
# Install to user site-packages (requires --break-system-packages on Debian)
pip install --user --break-system-packages /opt/task-monitor

# Or using a temp directory to avoid permission issues
TEMP_DIR=$(mktemp -d) && cp -r /opt/task-monitor/* "$TEMP_DIR/" && \
pip install --user --break-system-packages "$TEMP_DIR" && rm -rf "$TEMP_DIR"
```

This creates:
- `~/.local/bin/task-monitor` - Native wrapper script
- `~/.local/lib/python3.13/site-packages/cli.py` - CLI module (with main())
- `~/.local/lib/python3.13/site-packages/models.py` - Data models
- `~/.local/lib/python3.13/site-packages/monitor_daemon.py` - Monitor daemon
- `~/.local/lib/python3.13/site-packages/task_executor.py` - Task executor

## Key Design Principles

1. **Single Service**: One `task-monitor.service` for all projects
2. **Dedicated Virtual Environment**: Self-contained venv at `/opt/task-monitor/.venv/` for independence
3. **Per-Project Isolation**: Each project has its own queue, executor, and watchdog observer
4. **Sequential Within Project**: Tasks in same project execute one at a time (FIFO)
5. **Parallel Across Projects**: Different projects execute simultaneously
6. **Project-Specific CWD**: Each task executes with its project root as working directory
7. **Registration-Based**: Projects registered via config file, service reloads automatically

## Related Skills

- `task-document-writer`: Creates task documents with correct naming pattern
- `task-implementation`: Executes tasks with worker-auditor workflow
