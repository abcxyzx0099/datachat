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


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "queue":
            show_queue()
        else:
            show_status(sys.argv[1])
    else:
        show_status()
