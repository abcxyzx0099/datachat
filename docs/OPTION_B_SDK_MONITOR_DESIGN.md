# Option B: SDK-Based Task Monitor Design (Sequential Execution)

## Overview

A Python-based monitoring service that uses `watchdog` for file monitoring and the Claude Agent SDK to programmatically execute tasks **sequentially** (one at a time), providing structured output, better error handling, and direct result retrieval.

## Execution Model: Sequential (One-by-One)

```
Task 1 arrives ──────────────────────────────────────
                    ████████████████████████████
                    Task 1 executes (5 min)

Task 2 arrives ─────────────────────────────────────────────────────────
                    (Waits in queue...)
                                          ██████████████
                                          Task 2 executes (3 min)

Task 3 arrives ──────────────────────────────────────────────────────────────────────────
                    (Waits in queue...)
                                                           ████████
                                                           Task 3 executes (2 min)
```

**Key Points:**
- Tasks are queued in arrival order (FIFO)
- Only ONE task runs at a time
- Task N+1 starts ONLY after Task N completes
- No concurrent/parallel execution

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         User Session                                 │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  You: /task-document-generator "Fix auth bug"                  │ │
│  │  ────────────────────────────────────────────────────────────  │ │
│  │  ✅ Task document created: /tasks/task-001.md                  │ │
│  │  ✅ Immediate return - you continue working                    │ │
│  └────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    Monitor Daemon (Python + watchdog)              │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  watchdog.Observer watching /tasks/                            │ │
│  │  ────────────────────────────────────────────────────────────  │ │
│  │  [DETECT] task-001.md → Add to Task Queue                      │ │
│  │  [DETECT] task-002.md → Add to Task Queue                      │ │
│  │  [DETECT] task-003.md → Add to Task Queue                      │ │
│  │                                                                  │ │
│  │  ┌────────────────────────────────────────────────────────┐    │ │
│  │  │  Task Queue (FIFO - Sequential Processing)             │    │ │
│  │  │  ┌────────┐  ┌────────┐  ┌────────┐                   │    │ │
│  │  │  │ Task 1 │→ │ Task 2 │→ │ Task 3 │→ ...              │    │ │
│  │  │  └────────┘  └────────┘  └────────┘                   │    │ │
│  │  │    (running)    (waiting)    (waiting)                 │    │ │
│  │  └────────────────────────────────────────────────────────┘    │ │
│  └────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                    ↓
                    Only ONE task at a time
                                    ↓
┌─────────────────────────────────────────────────────────────────────┐
│                  SDK Agent Execution (In-Process)                   │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  AgentDefinition: task-executor                                 │ │
│  │  ────────────────────────────────────────────────────────────  │ │
│  │  1. Reads task document (via Read tool)                        │
│  │  2. Invokes task-coordination skill (via Skill tool)            │
│  │     ├─ Spawns Implementation Agent (via Task tool)               │
│  │     └─ Spawns Auditor Agent (via Task tool)                     │
│  │  3. Automatic iteration until quality threshold met             │
│  │  4. Returns structured result                                   │
│  │  5. Mark as COMPLETE → Trigger NEXT task                       │
│  └────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────┐
│                      Result Storage                                 │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  {                                                              │ │
│  │    "task_id": "task-001",                                       │ │
│  │    "status": "completed",                                       │ │
│  │    "worker_result": {...},                                      │ │
│  │    "audit_score": 9,                                            │ │
│  │    "artifacts": [...]                                           │ │
│  │  }                                                              │ │
│  │  → Saved to /results/task-001.json                             │ │
│  └────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

## Components

### 1. Task Document Generator Skill
**Location**: `~/.claude/skills/task-document-generator/`

Triggered by user during conversation to create task documents.

**Input**: User conversation context
**Output**: Task document in `/tasks/` directory
**Returns**: Immediately

### 2. Python Monitor Service
**Location**: `/scripts/monitor_daemon.py`

A Python daemon using `watchdog` for file monitoring and a **sequential task queue** for execution.

**Features**:
- File monitoring via `watchdog`
- **Sequential task queue (FIFO)** - processes one task at a time
- Async file monitoring
- Structured result handling
- Error tracking and retry logic
- Status API endpoint
- Metrics collection

**Execution Model:**
- Tasks added to queue as they are detected
- Queue processor runs tasks sequentially
- Task N+1 starts ONLY after Task N completes
- No parallel/concurrent execution

### 3. Task Executor
**Location**: `/scripts/task_executor.py`

Handles the actual task execution using SDK.

**Features**:
- Agent definition management
- Worker delegation
- Result auditing
- Structured output generation

### 4. Status API (Optional)
**Location**: `/scripts/status_api.py`

REST API for querying task status and results.

**Endpoints**:
- `GET /tasks` - List all tasks
- `GET /tasks/{id}` - Get task details
- `GET /tasks/{id}/status` - Get task status
- `POST /tasks/{id}/retry` - Retry failed task

## File Structure

```
datachat/
├── tasks/                          # Task document directory
│   └── task-001.md
│
├── results/                        # Structured results
│   └── task-001.json
│
├── scripts/
│   ├── monitor_daemon.py           # Main monitor daemon (with TaskQueue)
│   ├── task_executor.py            # Task execution logic
│   ├── status_api.py               # Optional status API
│   ├── models.py                   # Data models
│   ├── install-service.sh          # Setup systemd service
│   └── cli.py                      # CLI for status queries
│
├── logs/
│   ├── monitor.log                 # Monitor daemon logs
│   └── executor/                   # Per-task execution logs
│       └── task-001.log
│
├── state/                          # Runtime state (optional)
│   └── queue_state.json            # Queue state persistence
│
└── requirements.txt                # Python dependencies
```

## Implementation Details

### SDK Usage Notes

**IMPORTANT:** The Claude Agent SDK has specific patterns that differ from typical Python APIs:

#### Import Pattern
```python
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AgentDefinition
```

**DO NOT import these directly (they are NOT exported):**
- `AssistantMessage` ❌
- `ResultMessage` ❌
- `TextBlock` ❌
- `ToolUseBlock` ❌

#### Message Detection Pattern

Instead of `isinstance()` checks, use `hasattr()` to detect message types:

```python
async for message in client.receive_messages():
    # Check for final result (has 'subtype' attribute)
    if hasattr(message, 'subtype'):
        if message.subtype == 'success':
            # Task completed successfully
            result = message.result
            usage = message.usage
        elif message.subtype == 'error':
            # Task failed
            error = message.result
        break
    else:
        # Assistant messages have 'content' attribute
        if hasattr(message, 'content'):
            for block in message.content:
                if hasattr(block, 'text'):
                    # Text block
                    text = block.text
```

#### ClaudeSDKClient vs query()

| Aspect | `query()` | `ClaudeSDKClient` |
|--------|-----------|-------------------|
| Session | New each time | Maintained across calls |
| Context | No memory | Remembers conversation |
| For Task Monitor | ❌ Less control | ✅ **Recommended** |

**Use `ClaudeSDKClient` for this task monitor** because:
- Better session management across multi-turn conversations
- More control over message processing
- Cleaner async context management

### requirements.txt
```txt
# Claude Agent SDK - core library
# Note: Message types (AssistantMessage, ResultMessage, TextBlock) are NOT directly exported
# Use hasattr() checks instead of isinstance() for message type detection
claude-agent-sdk>=0.1.0

# File system monitoring
watchdog>=4.0.0

# Async HTTP server (for optional status API)
aiohttp>=3.9.0

# Data validation and models
pydantic>=2.0.0
```

### models.py
```python
from pydantic import BaseModel
from enum import Enum
from datetime import datetime
from typing import Optional, List

class TaskStatus(str, Enum):
    QUEUED = "queued"       # Waiting in queue
    RUNNING = "running"     # Currently executing
    COMPLETED = "completed" # Successfully completed
    FAILED = "failed"       # Failed with error
    RETRYING = "retrying"   # Being retried

class TaskResult(BaseModel):
    task_id: str
    status: TaskStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    queue_position: Optional[int] = None  # Position in queue (if queued)
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

class TaskInfo(BaseModel):
    """Basic task info for status queries."""
    task_id: str
    status: TaskStatus
    created_at: datetime
    queue_position: Optional[int] = None
```

### task_executor.py
```python
import asyncio
from pathlib import Path
from datetime import datetime
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AgentDefinition
from models import TaskResult, TaskStatus
# Note: AgentDefinition is imported from claude_agent_sdk, NOT from models


class TaskExecutor:
    """Executes tasks using Claude Agent SDK with proper session management."""

    def __init__(self, tasks_dir: str, results_dir: str, prompts_dir: str = "./prompts"):
        self.tasks_dir = Path(tasks_dir)
        self.results_dir = Path(results_dir)
        self.prompts_dir = Path(prompts_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)

    async def execute_task(self, task_file: str) -> TaskResult:
        """Execute a task using the SDK and return structured results."""
        task_id = Path(task_file).stem
        task_path = self.tasks_dir / task_file

        # Read task document content
        task_content = self._read_task_document(task_path)

        # Load executor agent prompt
        executor_prompt = self._load_executor_prompt()

        # Define the task executor agent
        options = ClaudeAgentOptions(
            agents={
                "task-executor": AgentDefinition(
                    description="Executes tasks from task documents with worker and auditor",
                    prompt=executor_prompt,
                    tools=["Read", "Write", "Edit", "Bash", "Task"],
                    model="sonnet",
                )
            },
            permission_mode="acceptEdits",
            allowed_tools=["Read", "Write", "Edit", "Bash", "Task"],
            setting_sources=["project"],  # Load project settings for skills
        )

        result = TaskResult(
            task_id=task_id,
            status=TaskStatus.RUNNING,
            created_at=datetime.now(),
            started_at=datetime.now(),
        )

        try:
            # Use ClaudeSDKClient for proper session management
            async with ClaudeSDKClient(options=options) as client:
                await client.query(task_content)

                full_output = []

                # Process all messages until we get the final result
                async for message in client.receive_messages():
                    # Check for final result message (has 'subtype' attribute)
                    if hasattr(message, 'subtype'):
                        if message.subtype == 'success':
                            result.status = TaskStatus.COMPLETED
                            result.completed_at = datetime.now()
                            result.worker_output = {
                                "summary": message.result or "Task completed",
                                "raw_output": "\n".join(full_output)
                            }
                            # Extract usage information if available
                            if hasattr(message, 'usage'):
                                result.worker_output['usage'] = message.usage
                            if hasattr(message, 'total_cost_usd'):
                                result.worker_output['cost_usd'] = message.total_cost_usd
                        elif message.subtype == 'error':
                            result.status = TaskStatus.FAILED
                            result.completed_at = datetime.now()
                            result.error = message.result or "Task failed"
                        break
                    else:
                        # Accumulate assistant messages (text output)
                        if hasattr(message, 'content'):
                            for block in message.content:
                                if hasattr(block, 'text'):
                                    full_output.append(block.text)

            # Save structured result
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

    def _load_executor_prompt(self) -> str:
        """Load the executor agent prompt."""
        prompt_path = self.prompts_dir / "task_executor.txt"
        try:
            with open(prompt_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            # Fallback to default prompt if file doesn't exist
            return """
You are a task executor for the task monitoring system. When given a task document path:

1. Read the task document to understand requirements
2. Use the Skill tool to invoke the task-coordination skill
3. Pass the task document path to the skill
4. The skill will handle:
   - Implementation Agent execution
   - Auditor Agent review
   - Automatic iteration based on audit feedback
5. Return the final structured result from the coordination workflow

Important: Do NOT implement the task yourself. Always delegate to task-coordination skill.
"""

    def _save_result(self, result: TaskResult):
        """Save result to JSON file."""
        output_file = self.results_dir / f"{result.task_id}.json"
        with open(output_file, "w") as f:
            f.write(result.model_dump_json(indent=2))
```

### monitor_daemon.py
```python
import asyncio
import json
import logging
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from task_executor import TaskExecutor
from models import TaskStatus

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
        self._save_state()
        return task

    @property
    def size(self) -> int:
        """Return current queue size."""
        return self.queue.qsize()

    def get_queued_tasks(self) -> list[str]:
        """Get list of currently queued tasks (without dequeuing)."""
        # Note: asyncio.Queue doesn't expose peek, so we track via state
        return self._load_state().get("queued_tasks", [])

    def _load_state(self) -> dict:
        """Load queue state from file."""
        if self.STATE_FILE.exists():
            with open(self.STATE_FILE, 'r') as f:
                return json.load(f)
        return {
            "queue_size": 0,
            "current_task": None,
            "is_processing": False,
            "queued_tasks": []
        }

    def _save_state(self):
        """Save queue state to file."""
        state = {
            "queue_size": self.queue.qsize(),
            "current_task": self.current_task,
            "is_processing": self.is_processing,
            "queued_tasks": []  # asyncio.Queue doesn't expose contents
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
            # Add to queue (non-blocking)
            asyncio.run_coroutine_threadsafe(
                self.task_queue.put(file_path.name),
                self.loop
            )


class MonitorDaemon:
    """Main monitor daemon with sequential task queue."""

    def __init__(self, tasks_dir: str = "./tasks"):
        self.tasks_dir = Path(tasks_dir)
        self.tasks_dir.mkdir(parents=True, exist_ok=True)

        # Sequential task queue
        self.task_queue = TaskQueue()

        self.executor = TaskExecutor(
            tasks_dir=str(self.tasks_dir),
            results_dir="./results"
        )
        # Event handler will be initialized with event loop in _run()
        self.event_handler = None
        self.observer = Observer()
        self.running = False

    def start(self):
        """Start the monitor daemon."""
        logger.info(f"Starting monitor on {self.tasks_dir}")
        logger.info("Execution model: SEQUENTIAL (one task at a time)")

        # Get the event loop before starting observer
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Initialize event handler with the loop
        self.event_handler = TaskFileHandler(self.task_queue, loop)

        self.observer.schedule(
            self.event_handler,
            str(self.tasks_dir),
            recursive=False
        )
        self.observer.start()

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
                # Wait for next task (blocks if queue is empty)
                # Use timeout to allow checking self.running flag
                task_file = await asyncio.wait_for(
                    self.task_queue.get_next(),
                    timeout=1.0
                )

                logger.info(f"Starting task: {task_file} (queue size: {self.task_queue.size})")
                self.task_queue.is_processing = True
                self.task_queue.current_task = task_file
                self.task_queue._save_state()

                # Execute task (blocking - ensures sequential execution)
                try:
                    result = await self.executor.execute_task(task_file)
                    duration = (result.completed_at - result.started_at).total_seconds()
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

                # Small delay before next task
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

### cli.py (Optional - for querying status)
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
        # List all tasks
        for result_file in results_dir.glob("*.json"):
            with open(result_file) as f:
                data = json.load(f)
            print(f"{data['task_id']}: {data['status']}")

def show_queue():
    """Show current queue state."""
    state_file = Path("state/queue_state.json")
    if state_file.exists():
        with open(state_file) as f:
            state = json.load(f)
        print(f"Queue size: {state['queue_size']}")
        print(f"Processing: {state.get('current_task', 'None')}")
        if state.get('queued_tasks'):
            print("Queued tasks:")
            for i, task in enumerate(state['queued_tasks'], 1):
                print(f"  {i}. {task}")
    else:
        print("Queue state not available (monitor may not be running)")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "queue":
            show_queue()
        else:
            show_status(sys.argv[1])
    else:
        show_status()
```

### install-service.sh
```bash
#!/bin/bash

# Install as systemd service
sudo cat > /etc/systemd/system/task-monitor.service <<EOF
[Unit]
Description=Task Monitor Daemon (SDK)
After=network.target

[Service]
Type=simple
User=admin
WorkingDirectory=/home/admin/workspaces/datachat
Environment="PATH=/home/admin/.local/bin:/usr/bin"
ExecStart=/usr/bin/python3 scripts/monitor_daemon.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Install dependencies
pip3 install -r requirements.txt

sudo systemctl daemon-reload
sudo systemctl enable task-monitor
sudo systemctl start task-monitor

echo "Monitor installed and started"
echo "Check status: sudo systemctl status task-monitor"
echo "View logs: tail -f logs/monitor.log"
```

## Task Document Format

Same as Option A, but with potential for additional metadata:

```markdown
# Task Document

## Meta
- **ID**: task-20250129-143052-001
- **Created**: 2025-01-29 14:30:52
- **Status**: pending
- **Priority**: high
- **Max Retries**: 3
- **Timeout**: 3600  # seconds

## Description
Fix the authentication bug...

## Requirements
...

## Acceptance Criteria
...
```

## Result Format

```json
{
  "task_id": "task-20250129-143052-001",
  "status": "completed",
  "created_at": "2025-01-29T14:30:52",
  "started_at": "2025-01-29T14:30:55",
  "completed_at": "2025-01-29T14:44:30",
  "queue_position": null,
  "worker_output": {
    "summary": "Fixed password special character handling",
    "changes": ["src/auth/login.py", "tests/test_auth.py"],
    "test_results": {
      "total": 42,
      "passed": 42,
      "failed": 0
    }
  },
  "audit_score": 9,
  "audit_notes": "High quality implementation. Minor suggestions for documentation.",
  "artifacts": [
    "src/auth/login.py",
    "tests/test_auth.py",
    "logs/test-run.log"
  ],
  "error": null,
  "retry_count": 0
}
```

## Queue State Format

```json
{
  "queue_size": 2,
  "current_task": "task-001.md",
  "is_processing": true,
  "queued_tasks": ["task-002.md", "task-003.md"]
}
```

## Pros & Cons

### Pros
| ✅ | Description |
|----|-------------|
| **Structured Output** | JSON results, easy to parse and query |
| **Error Handling** | Full exception handling and tracking |
| **Status API** | Programmatic status queries available |
| **Extensible** | Easy to add features (retry, metrics, webhooks) |
| **Better Logging** | Structured logging with levels |
| **In-Process** | No CLI overhead per task |
| **Type Safety** | Pydantic models ensure data integrity |

### Cons
| ❌ | Description |
|----|-------------|
| **Complexity** | More code to write and maintain |
| **Dependencies** | Requires Python packages |
| **Learning Curve** | Need to understand SDK |
| **Process Management** | Python daemon needs careful setup |
| **Memory** | Python process always running |

## Additional Features Possible

With SDK approach, these features are easier to add:

| Feature | Description |
|---------|-------------|
| **Task Queue** | Limit concurrent tasks |
| **Retry Logic** | Auto-retry failed tasks |
| **Priority** | Execute high-priority tasks first |
| **Timeouts** | Kill long-running tasks |
| **Webhooks** | Notify on completion |
| **Metrics** | Track execution times, success rates |
| **Web Dashboard** | Visual task status |
| **Task Dependencies** | Chain tasks together |
| **Scheduled Tasks** | Run tasks at specific times |

## Implementation Checklist

- [ ] Set up Python project structure
- [ ] Create `requirements.txt`
- [ ] Implement data models (`models.py`)
- [ ] Implement task executor (`task_executor.py`)
- [ ] Implement monitor daemon (`monitor_daemon.py`)
- [ ] Create systemd service configuration
- [ ] Implement optional status API (`status_api.py`)
- [ ] Implement CLI for status queries (`cli.py`)
- [ ] Create `task-document-generator` skill
- [ ] Create/update `task-coordination` skill
- [ ] Set up logging directory structure
- [ ] Test with sample tasks
- [ ] Create documentation

## Dependencies

| Package | Purpose |
|---------|---------|
| `claude-agent-sdk` | Claude Agent SDK |
| `watchdog` | File system monitoring |
| `pydantic` | Data validation |
| `aiohttp` | Async HTTP (for API) |

## Estimated Complexity

| Aspect | Level |
|--------|-------|
| Implementation | Medium - Python async code |
| Maintenance | Medium - More moving parts |
| Debugging | Easy - Structured logging |
| Extensibility | High - Modular design |

## When to Choose This Option

Choose Option B if:
- ✅ You need structured output/results
- ✅ You want better error handling
- ✅ You need a status query API
- ✅ You plan to add advanced features (retry, queue, etc.)
- ✅ You're comfortable with Python
- ✅ You want better observability
- ✅ You need programmatic integration
- ✅ **You prefer sequential task execution (one at a time)**

## Execution Model Summary

| Property | Value |
|----------|-------|
| **Monitoring** | `watchdog` library (Python) |
| **Detection** | New file creation events only |
| **Processing** | **Sequential (FIFO queue)** |
| **Concurrency** | **One task at a time** |
| **User Blocking** | **Non-blocking** (background process) |
| **Execution** | SDK (in-process, no CLI overhead) |
| **Output** | Structured JSON results |

## Key Behaviors

1. **New files only**: Monitor ignores existing files on startup
2. **Sequential processing**: Tasks execute one-by-one in arrival order
3. **Non-blocking**: User's Claude Code session continues while tasks run
4. **Background execution**: Separate Python daemon handles all task execution
5. **Structured results**: JSON output for easy querying and integration
