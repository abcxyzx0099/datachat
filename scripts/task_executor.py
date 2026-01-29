import asyncio
import sys
from pathlib import Path
from datetime import datetime
from claude_agent_sdk import query, ClaudeAgentOptions

# Add project root to Python path for module imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.models import TaskResult, TaskStatus


class TaskExecutor:
    """Executes tasks using Claude Agent SDK - directly invokes skills."""

    def __init__(self, tasks_dir: str, results_dir: str, project_root: str = "."):
        self.tasks_dir = Path(tasks_dir)
        self.results_dir = Path(results_dir)
        self.project_root = Path(project_root).resolve()
        self.results_dir.mkdir(parents=True, exist_ok=True)

    async def execute_task(self, task_file: str) -> TaskResult:
        """Execute a task by directly invoking task-coordination skill."""
        task_id = Path(task_file).stem
        task_path = self.tasks_dir / task_file

        # Read task document content
        task_content = self._read_task_document(task_path)

        # Configure SDK
        options = ClaudeAgentOptions(
            cwd=str(self.project_root),  # Set working directory
            permission_mode="acceptEdits",  # Auto-accept file edits
            setting_sources=["project"],  # Load project settings (including skills)
        )

        result = TaskResult(
            task_id=task_id,
            status=TaskStatus.RUNNING,
            created_at=datetime.now(),
            started_at=datetime.now(),
        )

        try:
            # Use standalone query() function - simplest approach!
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
