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
    """Show current queue state."""
    state_file = project_root / "state" / "queue_state.json"
    if state_file.exists():
        with open(state_file, 'r') as f:
            state = json.load(f)
        print(f"Queue size: {state['queue_size']}")
        print(f"Processing: {state.get('current_task', 'None')}")
        if state.get('queued_tasks'):
            print("Queued tasks:")
            for i, task in enumerate(state['queued_tasks'], 1):
                print(f"  {i}. {task}")
    else:
        print("Queue state not available (monitor may not be running)")


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
