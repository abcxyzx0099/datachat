# Issue: Task Implementation Daemon Not Automatically Processing Queued Tasks

## Status
CLOSED

## Problem Description
When a task is loaded using `task-impl load`, the task is added to the queue but the daemon does not automatically process it. The queue state shows `is_processing: false` and `current_task: null` even when tasks are queued.

## Observed Behavior
1. Task is loaded successfully: `task-impl load task-xxx.md`
2. Task appears in queue_state.json under `queued_tasks`
3. Daemon shows `is_processing: false` and `current_task: null`
4. Task is not processed until daemon is manually restarted

## Expected Behavior
When a task is loaded into the queue, the running daemon should automatically detect and process it without requiring a restart.

## Solution Implemented: Two-Command Approach

Instead of implementing complex polling or file watching, we simplified the workflow with two explicit commands:

### Commands

1. **`task-impl load`** - Load tasks from specifications directory into queue
2. **`task-impl run`** - Execute all queued tasks

### Usage

```bash
# Load tasks into queue
task-impl load

# Execute queued tasks
task-impl run
```

### Implementation

**File**: `/home/admin/workspaces/task-implementation/task_implementation/cli.py`

**Changes**:
1. Added `run_tasks_async()` - async function to execute queued tasks
2. Added `run_tasks()` - synchronous wrapper
3. Added `run` subparser to CLI
4. Added command handler for `run` command

### Code Snippet

```python
async def run_tasks_async(project_root: Path):
    """Execute all queued tasks (async version)."""
    state_file = project_root / task_implementation_path / "state" / "queue_state.json"

    if not state_file.exists():
        print("No queued tasks found.")
        return

    with open(state_file, 'r') as f:
        state = json.load(f)

    queued_tasks = state.get('queued_tasks', [])

    if not queued_tasks:
        print("No queued tasks found.")
        return

    print(f"Found {len(queued_tasks)} task(s) in queue.")
    print()

    # Create executor
    executor = TaskExecutor(project_root)

    # Process each task
    for task_file in queued_tasks:
        print(f"Executing: {task_file}")
        try:
            result = await executor.execute_task(task_file)
            print(f"  Status: {result.status}")
            if result.duration_seconds:
                print(f"  Duration: {result.duration_seconds:.1f}s")
            if result.error:
                print(f"  Error: {result.error}")
        except Exception as e:
            print(f"  Failed: {e}")
        print()

    print("All queued tasks processed.")


def run_tasks(project_root: Path):
    """Execute all queued tasks synchronously."""
    asyncio.run(run_tasks_async(project_root))
```

### Advantages of This Approach

1. **Simple** - No complex polling or file watching needed
2. **Explicit** - User has full control over when tasks execute
3. **Reliable** - No race conditions or timing issues
4. **Clear feedback** - User sees exactly what's being executed
5. **Easy to debug** - Execution happens in foreground, not background

### Workflow

```bash
# Step 1: Create task specification (manually or via task-specification-generation)
vim tasks/task-specifications/task-20260203-120000-my-task.md

# Step 2: Load task into queue
task-impl load
# Output: Added 1 task(s) to queue.

# Step 3: Execute queued tasks
task-impl run
# Output:
# Found 1 task(s) in queue.
# Executing: task-20260203-120000-my-task.md
#   Status: completed
#   Duration: 45.2s
# All queued tasks processed.

# Step 4: Check result
task-impl result task-20260203-120000-my-task
```

### Notes

- The **daemon** (`task-impl daemon`) is still available for background processing
- The **run command** provides immediate execution without daemon
- Users can choose whichever approach fits their workflow
- For automatic processing, users can still run the daemon (which requires restart to pick up new tasks)

## Files Modified

1. `/home/admin/workspaces/task-implementation/task_implementation/cli.py`
   - Added `run_tasks_async()` function
   - Added `run_tasks()` function
   - Added `run` subparser
   - Added command handler

## Original Alternatives Considered

1. ~~Polling mechanism~~ - Rejected in favor of simpler explicit command
2. ~~Inotify/file watcher~~ - Overly complex for this use case
3. ~~IPC/signals~~ - Adds unnecessary complexity
