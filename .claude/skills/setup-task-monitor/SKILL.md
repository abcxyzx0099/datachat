---
name: setup-task-monitor
description: "Sets up the complete task monitoring system. Uses watchdog for file monitoring, Claude Agent SDK with direct skill invocation, user systemd service with environment inheritance. Use when: deploying automated task execution system; monitoring /tasks/ directory for task documents; implementing sequential task processing with quality assurance."
---

# Setup Task Monitor

Sets up the complete task monitoring system with file-based monitoring, Claude Agent SDK integration, and user systemd service.

## Overview

This skill creates the infrastructure for automated task execution:
- **File-based monitoring** using `watchdog` for task-*.md detection
- **Direct skill invocation** - Uses standalone `query()` function, no unnecessary layers
- **Sequential task queue** - FIFO processing (one task at a time)
- **User systemd service** - Runs as your user, inherits environment automatically
- **Structured result storage** - JSON output in /results/

## Architecture Overview

```
User → task-document-generator → /tasks/task-*.md
                                    ↓
                            Watchdog detects file
                                    ↓
                            Direct query() with /task-coordination
                                    ↓
                    Implementation → Audit → Iterate
                                    ↓
                            JSON Results (/results/)
```

## When to Use

Call this skill when:
- Setting up the task monitoring system for the first time
- Deploying automated background task processing
- Configuring file-based task monitoring
- Setting up the complete workflow from scratch

## Prerequisites

- Python 3.10+ installed
- pip available
- systemctl available (for user systemd service)
- `ANTHROPIC_AUTH_TOKEN` and `ANTHROPIC_BASE_URL` in your environment

## Setup Steps

### Phase 1: Project Structure Creation

```
datachat/
├── tasks/                          # Task document directory
├── results/                        # Structured results
├── scripts/
│   ├── monitor_daemon.py           # Watchdog-based monitor daemon
│   ├── task_executor.py            # Task execution with direct SDK query
│   ├── models.py                   # Pydantic data models
│   ├── cli.py                      # Status query CLI
├── logs/
│   └── monitor.log                 # Monitor daemon logs
├── state/
│   └── queue_state.json            # Queue state persistence
└── requirements.txt                # Python dependencies
```

### Phase 2: Create requirements.txt

```txt
# Claude Agent SDK - core library
claude-agent-sdk>=0.1.0

# File system monitoring
watchdog>=4.0.0

# Data validation and models
pydantic>=2.0.0
```

### Phase 3: Implement models.py

```python
from pydantic import BaseModel
from enum import Enum
from datetime import datetime
from typing import Optional, List

class TaskStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"

class TaskResult(BaseModel):
    task_id: str
    status: TaskStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    queue_position: Optional[int] = None
    worker_output: Optional[dict] = None
    audit_score: Optional[int] = None
    audit_notes: Optional[str] = None
    artifacts: List[str] = []
    error: Optional[str] = None
    retry_count: int = 0

class QueueState(BaseModel):
    """Current state of the task queue."""
    queue_size: int
    current_task: Optional[str]
    is_processing: bool
    queued_tasks: List[str]
```

### Phase 4: Implement task_executor.py (SIMPLIFIED - No AgentDefinition!)

```python
import asyncio
import sys
from pathlib import Path
from datetime import datetime
from claude_agent_sdk import query, ClaudeAgentOptions

sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.models import TaskResult, TaskStatus


class TaskExecutor:
    """Executes tasks using standalone query() function - no unnecessary layers."""

    def __init__(self, tasks_dir: str, results_dir: str, project_root: str = "."):
        self.tasks_dir = Path(tasks_dir)
        self.results_dir = Path(results_dir)
        self.project_root = Path(project_root).resolve()
        self.results_dir.mkdir(parents=True, exist_ok=True)

    async def execute_task(self, task_file: str) -> TaskResult:
        """Execute task using standalone query() - direct skill invocation."""
        task_id = Path(task_file).stem
        task_path = self.tasks_dir / task_file
        task_content = self._read_task_document(task_path)

        # Configure SDK with cwd and project settings - NO AgentDefinition!
        options = ClaudeAgentOptions(
            cwd=str(self.project_root),  # Set working directory
            permission_mode="acceptEdits",  # Auto-accept file edits
            setting_sources=["project"],  # Load project settings (skills)
        )

        result = TaskResult(
            task_id=task_id,
            status=TaskStatus.RUNNING,
            created_at=datetime.now(),
            started_at=datetime.now(),
        )

        try:
            # Use standalone query() - SIMPLEST approach!
            prompt = f"""/task-coordination

Execute the following task:

{task_content}
"""

            full_output = []
            async for message in query(prompt=prompt, options=options):
                if hasattr(message, 'subtype'):
                    if message.subtype == 'success':
                        result.status = TaskStatus.COMPLETED
                        result.completed_at = datetime.now()
                        result.worker_output = {
                            "summary": message.result or "Task completed",
                            "raw_output": "\n".join(full_output)
                        }
                        if hasattr(message, 'usage'):
                            result.worker_output['usage'] = message.usage
                        if hasattr(message, 'total_cost_usd'):
                            result.worker_output['cost_usd'] = message.total_cost_usd
                        break
                    elif message.subtype == 'error':
                        result.status = TaskStatus.FAILED
                        result.completed_at = datetime.now()
                        result.error = message.result or "Task failed"
                        break
                else:
                    if hasattr(message, 'content'):
                        for block in message.content:
                            if hasattr(block, 'text'):
                                full_output.append(block.text)

            self._save_result(result)

        except Exception as e:
            result.status = TaskStatus.FAILED
            result.error = f"{type(e).__name__}: {str(e)}"
            result.completed_at = datetime.now()
            self._save_result(result)

        return result

    def _read_task_document(self, task_path: Path) -> str:
        """Read task document content."""
        try:
            with open(task_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Task document not found: {task_path}")

    def _save_result(self, result: TaskResult):
        """Save result to JSON file."""
        output_file = self.results_dir / f"{result.task_id}.json"
        with open(output_file, "w") as f:
            f.write(result.model_dump_json(indent=2))
```

### Phase 5: Implement monitor_daemon.py

```python
import asyncio
import json
import logging
import sys
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.task_executor import TaskExecutor
from scripts.models import TaskStatus

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/monitor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TaskQueue:
    """Sequential FIFO task queue with state persistence."""

    STATE_FILE = Path("state/queue_state.json")

    def __init__(self):
        self.queue = asyncio.Queue()
        self.current_task = None
        self.is_processing = False
        self.STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

    async def put(self, task_file: str):
        """Add a task to the queue."""
        await self.queue.put(task_file)
        logger.info(f"Task queued: {task_file} (queue size: {self.queue.qsize()})")
        self._save_state()

    async def get_next(self) -> str:
        """Get the next task from the queue."""
        task = await self.queue.get()
        logger.info(f"Task retrieved from queue: {task}")
        self._save_state()
        return task

    @property
    def size(self) -> int:
        """Return current queue size."""
        return self.queue.qsize()

    def _save_state(self):
        """Save queue state to file."""
        state = {
            "queue_size": self.queue.qsize(),
            "current_task": self.current_task,
            "is_processing": self.is_processing,
            "queued_tasks": []
        }
        with open(self.STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)


class TaskFileHandler(FileSystemEventHandler):
    """Handles task file creation events."""

    def __init__(self, task_queue: TaskQueue, loop: asyncio.AbstractEventLoop):
        self.task_queue = task_queue
        self.loop = loop

    def on_created(self, event):
        """Called when a file is created."""
        if event.is_directory:
            return

        file_path = Path(event.src_path)
        if file_path.match("task-*.md"):
            logger.info(f"New task detected: {file_path.name}")
            try:
                future = asyncio.run_coroutine_threadsafe(
                    self.task_queue.put(file_path.name),
                    self.loop
                )
                logger.info(f"Task queued successfully: {file_path.name}")
            except Exception as e:
                logger.error(f"Failed to queue task {file_path.name}: {e}")


class MonitorDaemon:
    """Main monitor daemon with sequential task queue."""

    def __init__(self, tasks_dir: str = "./tasks"):
        self.tasks_dir = Path(tasks_dir)
        self.tasks_dir.mkdir(parents=True, exist_ok=True)

        # Sequential task queue
        self.task_queue = TaskQueue()

        # Get project root
        project_root = Path(__file__).parent.parent.resolve()

        self.executor = TaskExecutor(
            tasks_dir=str(self.tasks_dir),
            results_dir="./results",
            project_root=str(project_root)
        )
        self.event_handler = None
        self.observer = Observer()
        self.running = False

    def start(self):
        """Start the monitor daemon."""
        logger.info(f"Starting monitor on {self.tasks_dir}")
        logger.info("Execution model: SEQUENTIAL (one task at a time)")

        try:
            asyncio.run(self._run())
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            self.running = False
            self.observer.stop()
        self.observer.join()

    async def _run(self):
        """Main async loop - processes queue sequentially."""
        logger.info("Monitor running, waiting for tasks...")
        self.running = True

        # Get the current event loop (created by asyncio.run)
        loop = asyncio.get_event_loop()

        # Initialize event handler with the current loop
        self.event_handler = TaskFileHandler(self.task_queue, loop)

        self.observer.schedule(
            self.event_handler,
            str(self.tasks_dir),
            recursive=False
        )
        self.observer.start()

        # Start queue processor
        processor_task = asyncio.create_task(self._process_queue())

        # Keep running until shutdown
        while self.running:
            await asyncio.sleep(1)

        # Wait for processor to finish
        await processor_task

    async def _process_queue(self):
        """Process tasks from queue sequentially (one at a time)."""
        logger.info("Queue processor started")

        while self.running:
            try:
                task_file = await asyncio.wait_for(
                    self.task_queue.get_next(),
                    timeout=1.0
                )

                logger.info(f"Starting task: {task_file} (queue size: {self.task_queue.size})")
                self.task_queue.is_processing = True
                self.task_queue.current_task = task_file
                self.task_queue._save_state()

                # Execute task (blocking)
                try:
                    result = await self.executor.execute_task(task_file)
                    if result.completed_at:
                        duration = (result.completed_at - result.started_at).total_seconds()
                    else:
                        duration = 0
                    logger.info(
                        f"Task completed: {task_file} - "
                        f"status={result.status}, "
                        f"duration={duration:.1f}s"
                    )
                except Exception as e:
                    logger.error(f"Task failed: {task_file} - {e}")

                # Mark as ready for next task
                self.task_queue.current_task = None
                self.task_queue.is_processing = False
                self.task_queue._save_state()

                await asyncio.sleep(0.5)

            except asyncio.TimeoutError:
                # No task in queue, continue waiting
                continue
            except Exception as e:
                logger.error(f"Error processing task: {e}")
                self.task_queue.current_task = None
                self.task_queue.is_processing = False
                self.task_queue._save_state()


if __name__ == "__main__":
    daemon = MonitorDaemon()
    daemon.start()
```

### Phase 6: Implement cli.py

```python
import sys
import json
from pathlib import Path

def show_status(task_id: str = None):
    """Show task status."""
    results_dir = Path("results")

    if task_id:
        result_file = results_dir / f"{task_id}.json"
        if result_file.exists():
            with open(result_file) as f:
                data = json.load(f)
            print(json.dumps(data, indent=2))
        else:
            print(f"Task {task_id} not found")
    else:
        for result_file in results_dir.glob("*.json"):
            with open(result_file) as f:
                data = json.load(f)
            print(f"{data['task_id']}: {data['status']}")

def show_queue():
    """Show current queue state."""
    state_file = Path("state/queue_state.json")
    if state_file.exists():
        with open(state_file, 'r') as f:
            state = json.load(f)
        print(f"Queue size: {state['queue_size']}")
        print(f"Processing: {state.get('current_task', 'None')}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "queue":
            show_queue()
        else:
            show_status(sys.argv[1])
    else:
        show_status()
```

### Phase 7: Create User Systemd Service with Environment Inheritance

**IMPORTANT**: Uses user service (not system service) to automatically inherit your environment variables including `ANTHROPIC_AUTH_TOKEN` and `ANTHROPIC_BASE_URL`.

Create `~/.config/systemd/user/task-monitor.service`:

```ini
[Unit]
Description=Task Monitor Daemon (SDK)
After=network.target

[Service]
Type=simple
WorkingDirectory=/home/admin/workspaces/datachat
Environment="PATH=/home/admin/workspaces/datachat/.venv/bin:/usr/bin"
EnvironmentFile=-%h/.config/systemd/user/environment.conf
ExecStart=/home/admin/workspaces/datachat/.venv/bin/python /home/admin/workspaces/datachat/scripts/monitor_daemon.py
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
```

Create `~/.config/systemd/user/environment.conf` with your API credentials:

```bash
# Copy your existing environment variables
cat > ~/.config/systemd/user/environment.conf << 'ENV'
ANTHROPIC_AUTH_TOKEN=your_token_here
ANTHROPIC_BASE_URL=https://open.bigmodel.cn/api/anthropic
ANTHROPIC_MODEL=glm-4.7
ENV

# Install and start
systemctl --user daemon-reload
systemctl --user enable task-monitor
systemctl --user start task-monitor
```

### Phase 8: Install Dependencies

```bash
# Create virtual environment and install dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Create directories
mkdir -p tasks results logs state
```

### Phase 9: Verify Setup

Check that everything works:

```bash
# Check service status
systemctl --user status task-monitor

# View logs
tail -f logs/monitor.log

# Check queue state
python scripts/cli.py queue

# List all tasks
python scripts/cli.py
```

## Key Implementation Details

### What This DOES (Simplified Architecture)

| Component | Implementation Detail |
|-----------|----------------------|
| **Task Execution** | Uses standalone `query()` function - NO AgentDefinition layer |
| **Skill Invocation** | Direct `/task-coordination` in prompt - no intermediate agent |
| **SDK Configuration** | `cwd` for working directory, `setting_sources=["project"]` for skills |
| **Permission Mode** | `acceptEdits` - auto-accepts file edits |
| **Service Type** | User systemd service (not system) - inherits your environment |
| **Environment Loading** | `environment.conf` - automatic inheritance, no explicit passing needed |

### What This DOES NOT DO (Removed Unnecessary Layers)

| ❌ Removed | Why |
|----------|-----|
| AgentDefinition | Unnecessary intermediate layer - skills can be invoked directly |
| prompts/ directory | No longer needed - direct skill invocation |
| System service (root) | User service is safer and inherits environment automatically |
| Explicit env passing | environment.conf handles this automatically |
| ClaudeSDKClient class | Standalone `query()` is simpler for one-shot queries |

## Troubleshooting

### Service won't start
```bash
# Check user service logs
journalctl --user -u task-monitor -n 50

# Check environment file
cat ~/.config/systemd/user/environment.conf
```

### API Key errors
```bash
# Verify your environment has the required variables
env | grep ANTHROPIC

# Ensure environment.conf contains the same values
cat ~/.config/systemd/user/environment.conf
```

### Permission errors
```bash
# Ensure proper ownership (should be your user, not root)
ls -la tasks/ results/ logs/ state/
```

## Output

```json
{
  "setup_complete": true,
  "components_created": [
    "scripts/monitor_daemon.py",
    "scripts/task_executor.py",
    "scripts/models.py",
    "scripts/cli.py",
    "requirements.txt",
    "tasks/", "results/", "logs/", "state/"
  ],
  "service_type": "user systemd service",
  "status": "running",
  "architecture": "Simplified - no unnecessary layers",
  "key_features": [
    "Direct skill invocation (no AgentDefinition)",
    "User service (inherits environment automatically)",
    "Standalone query() function",
    "cwd parameter for working directory",
    "setting_sources for project settings/skills"
  ]
}
```

## How It Works

1. **File Detection**: Watchdog monitors `/tasks/` for `task-*.md` files
2. **Queue Processing**: Tasks are queued in FIFO order
3. **Direct Execution**: Standalone `query()` with `/task-coordination` prompt
4. **Skill Coordination**: skill handles Implementation → Audit → Iterate
5. **Result Storage**: JSON results saved to `/results/`

## Comparison: Before vs After

| Before | After |
|--------|-------|
| `ClaudeSDKClient` class | Standalone `query()` function |
| AgentDefinition layer | Direct skill invocation |
| System service (root) | User service (your user) |
| Explicit env passing | Automatic inheritance via environment.conf |
| prompts/ directory | No longer needed |
