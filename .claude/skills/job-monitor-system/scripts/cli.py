import argparse
import json
from pathlib import Path


# Default project root - can be overridden by --project-path argument
DEFAULT_PROJECT_ROOT = Path("/home/admin/workspaces/datachat")


def show_status(job_id: str = None, project_root: Path = DEFAULT_PROJECT_ROOT):
    """Show job status."""
    results_dir = project_root / "jobs" / "results"

    if job_id:
        result_file = results_dir / f"{job_id}.json"
        if result_file.exists():
            with open(result_file) as f:
                data = json.load(f)
            print(json.dumps(data, indent=2))
        else:
            print(f"Job {job_id} not found")
    else:
        # List all jobs
        for result_file in results_dir.glob("*.json"):
            with open(result_file) as f:
                data = json.load(f)
            print(f"{data['job_id']}: {data['status']}")


def show_queue(project_root: Path = DEFAULT_PROJECT_ROOT):
    """Show current queue state."""
    state_file = project_root / "jobs" / "state" / "queue_state.json"
    if state_file.exists():
        with open(state_file, 'r') as f:
            state = json.load(f)
        print(f"Queue size: {state['queue_size']}")
        print(f"Processing: {state.get('current_task', 'None')}")
        if state.get('queued_tasks'):
            print("Queued jobs:")
            for i, job in enumerate(state['queued_tasks'], 1):
                print(f"  {i}. {job}")
    else:
        print("Queue state not available (monitor may not be running)")


def main():
    """CLI entry point - called by setuptools entry point."""
    parser = argparse.ArgumentParser(description="Job Monitor CLI")
    parser.add_argument("--project-path", "-p", type=str, help="Project root path")
    parser.add_argument("command", nargs="?", default="status", help="Command: status, queue, or job_id")
    args = parser.parse_args()

    # Project root - where jobs/items, jobs/results, jobs/state directories are located
    project_root = Path(args.project_path) if args.project_path else DEFAULT_PROJECT_ROOT

    if args.command == "queue":
        show_queue(project_root)
    else:
        show_status(args.command, project_root)


if __name__ == "__main__":
    main()
