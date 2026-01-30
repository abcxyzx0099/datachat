---
name: job-monitor-system
description: "Create and configure the multi-project job monitoring system with watchdog file monitoring and Claude Agent SDK integration. Use when: setting up a new job monitor system; installing from scratch; understanding system architecture; troubleshooting service issues; configuring the monitor; registering new projects. For detailed architecture, see [architecture.md](references/architecture.md). For troubleshooting, see [troubleshooting.md](references/troubleshooting.md)."
---

# Multi-Project Job Monitor System

## Quick Overview

Single service that monitors multiple projects, watching each project's `/jobs/items/` directory and executing jobs **sequentially within each project** (but **parallel across projects**).

## Execution Model

```
Project A (sequential) ──┐
                         ├─→ PARALLEL ──→ Jobs execute independently
Project B (sequential) ──┘
```

- **Within project**: Sequential FIFO queue (one job at a time)
- **Across projects**: Parallel execution (projects run independently)

---

## Creating the Job Monitor System

### Quick Install

The install script is included in this skill at [references/install-service.sh](references/install-service.sh).

```bash
# Run the install script
sudo bash /opt/job-monitor/install-service.sh
```

This will:
1. Create virtual environment at `/opt/job-monitor/.venv/`
2. Install dependencies (claude-agent-sdk, watchdog, pydantic)
3. Create `pyproject.toml` for CLI installation
4. Install CLI command via `pip install --user`
5. Create systemd user service
6. Start the service

### Manual Installation

If you prefer to install manually:

```bash
# 1. Create virtual environment
sudo python3 -m venv /opt/job-monitor/.venv

# 2. Install dependencies
sudo /opt/job-monitor/.venv/bin/pip install claude-agent-sdk watchdog pydantic

# 3. Create pyproject.toml (see references/install-service.sh for content)

# 4. Install CLI
pip install --user --break-system-packages /opt/job-monitor

# 5. Create systemd user service (see references/install-service.sh for content)

# 6. Start service
systemctl --user enable job-monitor
systemctl --user start job-monitor
```

### Verify Installation

```bash
# Check service status
systemctl --user status job-monitor

# Test CLI
job-monitor --help

# Check queue status
job-monitor queue
```

---

## Job Naming Convention

**Format:** `job-YYYYMMDD-HHMMSS-<description>.md`

**Example:** `job-20260130-143000-system-verification.md`

- `job-` - Fixed prefix
- `YYYYMMDD-HHMMSS` - Timestamp (for chronological sorting)
- `<description>` - Short, kebab-case description
- `.md` - Markdown document

**Pattern (glob):** `job-????????-??????-*.md`

## Key Paths

| Purpose | Path |
|---------|------|
| Install script | `.claude/skills/job-monitor-system/references/install-service.sh` |
| System service | `~/.config/systemd/user/job-monitor.service` |
| Monitor daemon | `/opt/job-monitor/` (system-level) |
| Configuration | `~/.config/job-monitor/` |
| CLI command | `~/.local/bin/job-monitor` (installed via `pip install --user`) |
| CLI source | `/opt/job-monitor/cli.py` (with `main()` entry point) |
| Package config | `/opt/job-monitor/pyproject.toml` (defines `[project.scripts]`) |

## Project Structure (Each Project)

```
{project-root}/
├── jobs/
│   ├── items/         # Job documents (watched by monitor)
│   ├── results/       # Execution results (JSON)
│   ├── state/         # Queue state per project
│   └── logs/          # Monitor logs per project
└── .claude/
    └── skills/        # Project-specific skills
```

## Quick Commands

```bash
# Service management
systemctl --user status job-monitor       # Check status
systemctl --user restart job-monitor      # Restart service

# Query jobs (per project)
job-monitor queue                         # Show queue status (uses default project)
job-monitor -p /path/to/project queue     # Show queue for specific project
job-monitor job-id                        # Show job status
job-monitor --help                        # Show all options
```

## Systemd Service

**File:** `~/.config/systemd/user/job-monitor.service`

```ini
[Unit]
Description=Job Monitor Daemon (SDK)
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/job-monitor
Environment="PATH=/opt/job-monitor/.venv/bin:/usr/bin"
ExecStart=/opt/job-monitor/.venv/bin/python /opt/job-monitor/monitor_daemon.py
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
```

**Single service** monitoring all registered projects. Uses dedicated virtual environment at `/opt/job-monitor/.venv/`.

## Workflow

```
1. Register project(s) → ~/.config/job-monitor/registered.json
                          ↓
2. Start service → job-monitor.service
                          ↓
3. For each project:
   - Watchdog monitors {project}/jobs/items/
   - Jobs queued in project-specific FIFO queue
   - Sequential execution within project
   - Results saved to {project}/jobs/results/
```

## Directory Structure

```
~/.config/systemd/user/
└── job-monitor.service            # User service for all projects

/opt/job-monitor/                  # System-level infrastructure
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
├── job_executor.py                # Job executor (with project cwd)
├── models.py                      # Data models
├── cli.py                         # Status CLI source (with main() entry point)
├── pyproject.toml                 # Package config (defines [project.scripts])
└── install-service.sh             # Installation script

~/.config/job-monitor/             # User configuration
└── registered.json                # Project registry

~/.local/
└── bin/
    └── job-monitor                # CLI wrapper (installed via pip install --user)

{project-root}/                    # Per-project (can be multiple)
└── jobs/
    ├── items/                     # Job documents
    ├── results/                   # Execution results
    ├── state/                     # Queue state
    └── logs/                      # Log files
```

## Project Registry

**Location:** `~/.config/job-monitor/registered.json`

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
mkdir -p /path/to/project/jobs/{items,results,state,logs}

# Add to registry (~/.config/job-monitor/registered.json)
# Then restart service
systemctl --user restart job-monitor
```

### What Happens During Registration

```
1. Verify project path exists
         ↓
2. Create required directories:
   - {project}/jobs/items/   (job documents)
   - {project}/jobs/results/ (execution results)
   - {project}/jobs/state/   (queue state)
   - {project}/jobs/logs/    (monitor logs)
         ↓
3. Add to ~/.config/job-monitor/registered.json
         ↓
4. Restart job-monitor.service
         ↓
5. Service creates:
   - Watchdog observer for {project}/jobs/items/
   - Project-specific queue
   - Project-specific executor (with correct cwd)
```

### Verify Registration

```bash
# Check service logs
journalctl --user -u job-monitor | grep "Observer started"

# Verify project structure
ls -la /home/admin/workspaces/myproject/jobs/items/
ls -la /home/admin/workspaces/myproject/jobs/results/
ls -la /home/admin/workspaces/myproject/jobs/state/
```

## Detailed Information

- **Full Architecture**: [architecture.md](references/architecture.md) - System layout, multi-project design, file descriptions
- **Troubleshooting**: [troubleshooting.md](references/troubleshooting.md) - Common issues and solutions
- **Install Script**: [scripts/install-service.sh](scripts/install-service.sh) - Complete installation script
- **Source Code**: All Python modules included in `scripts/`:
  - [scripts/monitor_daemon.py](scripts/monitor_daemon.py) - Multi-project watchdog daemon
  - [scripts/job_executor.py](scripts/job_executor.py) - Job executor with Claude Agent SDK
  - [scripts/models.py](scripts/models.py) - Pydantic data models
  - [scripts/cli.py](scripts/cli.py) - Command-line interface

## Recreating the System from Scratch

If the job monitor system is completely deleted, you can recreate it using only this skill:

```bash
# 1. Create the system directory
sudo mkdir -p /opt/job-monitor

# 2. Copy source files from this skill's scripts/
sudo cp .claude/skills/job-monitor-system/scripts/*.py /opt/job-monitor/
sudo cp .claude/skills/job-monitor-system/scripts/install-service.sh /opt/job-monitor/

# 3. Run the install script
sudo bash /opt/job-monitor/install-service.sh

# 4. Register your project
# (Manually edit ~/.config/job-monitor/registered.json)
```

## Dependencies

The job monitor uses a **dedicated virtual environment** at `/opt/job-monitor/.venv/` for independence from project-specific environments.

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
job-monitor = "cli:main"
```

**To install/reinstall the CLI:**
```bash
# Install to user site-packages (requires --break-system-packages on Debian)
pip install --user --break-system-packages /opt/job-monitor

# Or using a temp directory to avoid permission issues
TEMP_DIR=$(mktemp -d) && cp -r /opt/job-monitor/* "$TEMP_DIR/" && \
pip install --user --break-system-packages "$TEMP_DIR" && rm -rf "$TEMP_DIR"
```

This creates:
- `~/.local/bin/job-monitor` - Native wrapper script
- `~/.local/lib/python3.13/site-packages/cli.py` - CLI module (with main())
- `~/.local/lib/python3.13/site-packages/models.py` - Data models
- `~/.local/lib/python3.13/site-packages/monitor_daemon.py` - Monitor daemon
- `~/.local/lib/python3.13/site-packages/job_executor.py` - Job executor

## Key Design Principles

1. **Single Service**: One `job-monitor.service` for all projects
2. **Dedicated Virtual Environment**: Self-contained venv at `/opt/job-monitor/.venv/` for independence
3. **Per-Project Isolation**: Each project has its own queue, executor, and watchdog observer
4. **Sequential Within Project**: Jobs in same project execute one at a time (FIFO)
5. **Parallel Across Projects**: Different projects execute simultaneously
6. **Project-Specific CWD**: Each job executes with its project root as working directory
7. **Registration-Based**: Projects registered via config file, service reloads automatically

## Related Skills

- `job-document-writer`: Creates job documents with correct naming pattern
- `task-coordination`: Executes jobs with worker-auditor workflow
