import argparse
import json
from pathlib import Path


# Default project root - can be overridden by --project-path argument
DEFAULT_PROJECT_ROOT = Path("/home/admin/workspaces/datachat")


def show_status(task_id: str = None, project_root: Path = DEFAULT_PROJECT_ROOT):
    """Show task status."""
    results_dir = project_root / "results"

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


def show_queue(project_root: Path = DEFAULT_PROJECT_ROOT):
    """Show current queue state with enhanced output showing both processing and waiting tasks."""
    state_file = project_root / "state" / "queue_state.json"
    tasks_dir = project_root / "tasks"

    if not state_file.exists():
        print("┌─────────────────────────────────────────────┐")
        print("│  Task Monitor Status                         │")
        print("├─────────────────────────────────────────────┤")
        print("│  Service: ❌ Not running                     │")
        print("│                                              │")
        print("│  Queue state not available.                  │")
        print("│  Start the task monitor service to enable    │")
        print("│  automatic task processing.                  │")
        print("└─────────────────────────────────────────────┘")
        return

    with open(state_file, 'r') as f:
        state = json.load(f)

    # Build visual output
    print("┌─────────────────────────────────────────────┐")
    print("│  Task Monitor Status                         │")
    print("├─────────────────────────────────────────────┤")

    # Service status
    is_processing = state.get('is_processing', False)
    if is_processing:
        print("│  Service: ✅ Running                         │")
    else:
        print("│  Service: ⏸️ Idle                            │")
    print("│                                              │")

    # Currently processing
    current_task = state.get('current_task')
    if current_task:
        print("│  Currently Processing:                       │")
        print(f"│  → {current_task[:44]:<44}│")
    else:
        print("│  Currently Processing: None                 │")

    # Waiting in queue - read from tasks directory for actual files
    print("│                                              │")
    print("│  Waiting in Queue:                           │")

    # Get actual task files from tasks directory
    waiting_tasks = []
    if tasks_dir.exists():
        # Get all .md task files, excluding temp files
        task_files = sorted(tasks_dir.glob("task-*.md"), key=lambda p: p.stat().st_mtime)
        for task_file in task_files:
            task_name = task_file.name
            # Skip if this is the currently processing task
            if current_task and task_name == current_task:
                continue
            waiting_tasks.append(task_name)

    # Also check queued_tasks from state if available
    if state.get('queued_tasks'):
        for task_name in state['queued_tasks']:
            if task_name not in waiting_tasks:
                waiting_tasks.append(task_name)

    if waiting_tasks:
        for task in waiting_tasks[:10]:  # Show max 10 tasks
            print(f"│  → {task[:44]:<44}│")
        if len(waiting_tasks) > 10:
            print(f"│  ... and {len(waiting_tasks) - 10} more                          │")
    else:
        print("│  → No tasks waiting                          │")

    print("│                                              │")
    print(f"│  Queue Size: {len(waiting_tasks):<31}│")
    print("└─────────────────────────────────────────────┘")


def main():
    """CLI entry point - called by setuptools entry point."""
    parser = argparse.ArgumentParser(description="Task Monitor CLI")
    parser.add_argument("--project-path", "-p", type=str, help="Project root path")
    parser.add_argument("command", nargs="?", default="status", help="Command: status, queue, or task_id")
    args = parser.parse_args()

    # Project root - where tasks, results, state directories are located
    project_root = Path(args.project_path) if args.project_path else DEFAULT_PROJECT_ROOT

    if args.command == "queue":
        show_queue(project_root)
    else:
        show_status(args.command, project_root)


if __name__ == "__main__":
    main()
