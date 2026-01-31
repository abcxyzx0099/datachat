# Multi-Project Task Monitor Architecture

## System Layout

```
/home/admin/workspaces/task-monitor/    # Source code (editable install)
├── .venv/                             # Virtual environment
│   └── bin/
│       └── task-monitor               # CLI entry point
├── task_monitor/
│   ├── __init__.py
│   ├── monitor_daemon.py              # Multi-project daemon
│   ├── task_executor.py               # Task executor (project-aware cwd)
│   ├── models.py                      # Data models
│   └── cli.py                         # Status CLI
├── tests/                             # Unit tests
└── pyproject.toml                     # Package config

~/.config/systemd/user/                # User systemd services
└── task-monitor.service               # Monitor daemon service

~/.config/task-monitor/                # User configuration
├── .env                               # API credentials
└── registered.json                    # Project registry

{project-root}/                        # Per-project (multiple projects)
├── tasks/                            # Centralized task directory
│   ├── task-monitor/                 # Task monitoring system
│   │   ├── pending/                  # Input (watchdog monitors this)
│   │   ├── results/                  # Execution results (JSON)
│   │   ├── state/                    # Queue state (per project)
│   │   ├── logs/                     # Log files (per project)
│   │   └── archive/                  # Completed tasks
│   ├── task-planning/                # Task planning documents
│   └── task-implementation/          # Detailed workflow reports
└── .claude/
    └── skills/                        # Project-specific skills
```

## Installation

**Editable install** (development mode):
```bash
cd /home/admin/workspaces/task-monitor
pip install -e .
```

**PATH configuration** (in `~/.bashrc`):
```bash
export PATH="$HOME/workspaces/task-monitor/.venv/bin:$PATH"
```

**Service enablement**:
```bash
systemctl --user enable task-monitor.service
systemctl --user start task-monitor.service
```

## Task Naming Convention

**Format:** `task-<description>-YYYYMMDD-HHMMSS.md`

**Pattern (glob):** `task-*-????????-??????.md`

**Examples:**
- `task-system-verification-20250129-143000.md`
- `task-data-export-20250129-150000.md`
- `task-api-test-20250129-153000.md`

**Components:**
- `task-` - Fixed prefix
- `<description>` - Short, kebab-case description
- `<timestamp>` - ISO format with single dash (YYYYMMDD-HHMMSS)
- `.md` - Markdown document

## Multi-Project Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              task-monitor.service                           │
│                   (Single Service)                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                    Reads registry
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  datachat   │  │  project-b  │  │  project-c  │
├─────────────┤  ├─────────────┤  ├─────────────┤
│ Observer    │  │ Observer    │  │ Observer    │
│ tasks/      │  │ tasks/      │  │ tasks/      │
├─────────────┤  ├─────────────┤  ├─────────────┤
│ Queue       │  │ Queue       │  │ Queue       │
│ (FIFO)      │  │ (FIFO)      │  │ (FIFO)      │
├─────────────┤  ├─────────────┤  ├─────────────┤
│ Executor    │  │ Executor    │  │ Executor    │
│ cwd=datachat│  │ cwd=proj-b  │  │ cwd=proj-c  │
└─────────────┘  └─────────────┘  └─────────────┘
    │                 │                 │
    └─────────────────┴─────────────────┘
                         │
                   PARALLEL EXECUTION
           (projects run independently)
```

## Execution Model

### Within Project (Sequential)
```
Project A tasks/:
├── task-1.md ────→ [Queue] ────→ [Executing] ────→ Done
├── task-2.md ────→ [Waiting] ──→ [Next] ────────→ Done
└── task-3.md ────→ [Waiting] ──→ [Waiting] ──────→ ...
```

### Across Projects (Parallel)
```
Time:  0s    10s   20s   30s   40s   50s
       │     │     │     │     │     │

datachat:   [task-1───] [task-2──────] [task-3─]

project-b:  [task-1───────────] [task-2───] [task-3]

project-c:       [task-1───] [task-2─────] [task-3]
```

## How It Works

```
1. Register project(s) → ~/.config/task-monitor/registered.json
                           ↓
2. Start service → systemctl --user start task-monitor.service
                           ↓
3. Service loads registry → Creates per-project components:
                           - Observer (watchdog) for each tasks/
                           - Queue for each project
                           - Executor for each project (with correct cwd)
                           ↓
4. For each project independently:
   - Watchdog monitors {project}/tasks/task-monitor/
   - On file creation → Queued to project's queue
   - Sequential execution within project
   - Results saved to {project}/results/
```

## File Descriptions

### monitor_daemon.py
**Purpose:** Multi-project watchdog daemon.

**Location:** `/home/admin/workspaces/task-monitor/task_monitor/monitor_daemon.py`

**Key Components:**
- `MultiProjectMonitor`: Main orchestrator
- `ProjectTaskQueue`: Per-project FIFO queue
- `TaskFileHandler`: Handles file events per project

**Each Project Gets:**
- Observer (watchdog) monitoring `{project}/tasks/task-monitor/`
- Queue for sequential task processing
- Executor with correct `cwd={project_root}`

### task_executor.py
**Purpose:** Executes tasks using Claude Agent SDK with project-specific working directory.

**Location:** `/home/admin/workspaces/task-monitor/task_monitor/task_executor.py`

**Key Features:**
- Uses `query()` function from Claude Agent SDK
- Invokes `/task-implementation` skill
- Saves results to project's results directory
- **Critical**: `cwd=str(project_root)` for correct context

**SDK Configuration:**
```python
options = ClaudeAgentOptions(
    cwd=str(project_root),              # Project-specific working directory
    permission_mode="bypassPermissions", # Full autonomous execution
    setting_sources=["project"],         # Load project settings
)
```

### task-monitor CLI
**Purpose:** CLI tool for querying task status.

**Location:** `/home/admin/workspaces/task-monitor/.venv/bin/task-monitor`

**Access:** Added to PATH via `~/.bashrc`:
```bash
export PATH="$HOME/workspaces/task-monitor/.venv/bin:$PATH"
```

**Entry Point:** Defined in `pyproject.toml`:
```toml
[project.scripts]
task-monitor = "task_monitor.cli:main"
```

**Commands:**
```bash
task-monitor -p /path/to/project              # List all tasks
task-monitor -p /path/to/project task-001     # Show specific task
task-monitor queue                            # Show queue state
```

### registered.json
**Purpose:** Project registry for multi-project monitoring.

**Location:** `~/.config/task-monitor/registered.json`

**Format:**
```json
{
  "projects": {
    "project-name": {
      "path": "/full/path/to/project",
      "enabled": true,
      "registered_at": "2026-01-29T12:00:00"
    }
  }
}
```

### models.py
**Purpose:** Pydantic data models for task management.

**Location:** `/home/admin/workspaces/task-monitor/task_monitor/models.py`

**Models:**
- `TaskStatus`: Enum (QUEUED, RUNNING, COMPLETED, FAILED, RETRYING)
- `TaskResult`: Task execution result with metadata including stdout/stderr/duration
- `QueueState`: Current queue state (per project)

**TaskResult fields:**
```python
task_id: str                          # Task identifier
status: TaskStatus                     # Current status
stdout: Optional[str]                   # Captured stdout from task execution
stderr: Optional[str]                   # Captured stderr from task execution
duration_seconds: Optional[float]       # Execution duration in seconds
worker_output: Optional[dict]          # Worker agent output (summary, usage, cost)
error: Optional[str]                    # Error message if failed
started_at, completed_at: datetime     # Timestamps
```

### cli.py
**Purpose:** Command-line interface for querying task status.

**Location:** `/home/admin/workspaces/task-monitor/task_monitor/cli.py`

**Default Project:** `/home/admin/workspaces/datachat` (hardcoded in CLI)

**Usage:**
```bash
task-monitor                              # List all tasks (default project)
task-monitor -p /path/to/project          # List all tasks (specific project)
task-monitor task-001                     # Show specific task status
task-monitor queue                        # Show queue state
task-monitor -p /path/to/project queue    # Show queue for specific project
```

### task-monitor.service
**Purpose:** User systemd service for running the monitor daemon.

**Location:** `~/.config/systemd/user/task-monitor.service`

**Service File Content:**
```ini
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
```

**Service Management:**
```bash
# Enable service (start on login)
systemctl --user enable task-monitor.service

# Start service immediately
systemctl --user start task-monitor.service

# Stop service
systemctl --user stop task-monitor.service

# Restart service
systemctl --user restart task-monitor.service

# Check status
systemctl --user status task-monitor.service

# View logs
journalctl --user -u task-monitor.service -f
```

### .env (Configuration)
**Purpose:** Environment variables for API authentication.

**Location:** `~/.config/task-monitor/.env`

**Contents:**
```bash
ANTHROPIC_BASE_URL=https://open.bigmodel.cn/api/anthropic
ANTHROPIC_MODEL=glm-4.7
ANTHROPIC_AUTH_TOKEN=your_token_here
```

## Logging

**Standard Design (Implemented):**

| Location | Type | Content | Access |
|----------|------|---------|--------|
| **user systemd journal** | Service logs | All service output with task events | `journalctl --user -u task-monitor.service -f` |
| **{project}/tasks/task-monitor/results/** | Task results | JSON with stdout/stderr/duration | `cat {project}/tasks/task-monitor/results/{task_id}.json` |
| **{project}/tasks/task-monitor/logs/** | Project logs | Monitor daemon logs | `tail -f {project}/tasks/task-monitor/logs/monitor.log` |

**Task Result JSON Structure:**
```json
{
  "task_id": "task-example-20260130-120000",
  "status": "completed",
  "stdout": "Full task output captured here...",
  "stderr": null,
  "duration_seconds": 123.4,
  "started_at": "2026-01-30T12:00:00",
  "completed_at": "2026-01-30T12:02:03",
  "worker_output": {
    "summary": "Task completed",
    "raw_output": "Full task output..."
  }
}
```

**Viewing Logs:**
```bash
# Service logs (user systemd journal - primary source)
journalctl --user -u task-monitor.service -f           # Follow logs
journalctl --user -u task-monitor.service -n 100       # Last 100 lines
journalctl --user -u task-monitor.service --since "1 hour ago"  # Since 1 hour ago
journalctl --user -u task-monitor.service -f | grep "task-xxx"  # Filter by task

# Task execution results with full output
cat /home/admin/workspaces/datachat/tasks/task-monitor/results/task-xxx-xxx.json | jq '.stdout'

# Project logs (optional - for convenience)
tail -f /home/admin/workspaces/datachat/tasks/task-monitor/logs/monitor.log
```

**Logging Design:**
1. **user systemd journal** - Primary log destination (auto-rotated, searchable, persistent)
2. **Task stdout/stderr** - Captured in result JSON for complete audit trail
3. **Duration tracking** - Each task logs execution time
4. **Structured logging** - Task events logged with `[task_id]` prefix for filtering

**Improvements Made:**
- ✅ Task stdout/stderr captured in result JSON
- ✅ Execution duration tracked
- ✅ Task events logged to systemd journal with task_id prefix
- ✅ Standard Python logging configured for systemd integration

## Architecture Decisions

### Why Single Service for All Projects?

| Question | Answer |
|----------|--------|
| **One vs Multiple services?** | Single service is simpler to manage |
| **Per-project isolation?** | Achieved via separate queues/executors within service |
| **Add new project?** | Just register - no service file changes |
| **Restart impact?** | All projects restart together (acceptable trade-off) |

### Why Sequential Within Project?

| Reason | Explanation |
|--------|-------------|
| **Resource safety** | Tasks may modify same files |
| **Dependency safety** | Tasks may depend on previous results |
| **Predictable** | Easy to track progress |
| **Debuggable** | Clear execution order |

### Why Parallel Across Projects?

| Reason | Explanation |
|--------|-------------|
| **Independence** | Different codebases don't interfere |
| **Efficiency** | No waiting for unrelated projects |
| **Isolation** | Each has own queue, executor, state |

### Why Registration Mechanism?

| Reason | Explanation |
|--------|-------------|
| **User-friendly** | Simple commands instead of editing files |
| **Central registry** | Easy to see all monitored projects |
| **Service reload** | Auto-applies changes |
| **Names** | Friendly project names vs full paths |

### Why User-Space Installation?

| Reason | Explanation |
|--------|-------------|
| **No sudo required** | User can install and update without root privileges |
| **Development friendly** | Source code in user workspace for easy editing |
| **Infrastructure code** | Monitor serves multiple projects |
| **Clear separation** | Separate from project code |
| **Reusable** | Works with any project |
| **pip install --user** | Standard Python user-space installation |

## Key Design Principles

1. **User-Space Installation**: No root required, uses `pip install --user`
2. **Development Workflow**: Source code in workspace, installed to ~/.local/
3. **Per-Project Isolation**: Separate queue, executor, observer per project
4. **Sequential Within Project**: FIFO queue, one task at a time
5. **Parallel Across Projects**: Projects execute independently
6. **Project-Specific CWD**: Each task runs with correct working directory
7. **Configuration-Based**: Project registry in ~/.config/task-monitor/
8. **State Persistence**: Queue state saved per project
9. **Standard Python Locations**: Follows Python packaging conventions
