import asyncio
import sys
import logging
from pathlib import Path
from datetime import datetime
from claude_agent_sdk import query, ClaudeAgentOptions

# Add paths for module imports
PROJECT_ROOT = Path("/home/admin/workspaces/datachat")
MONITOR_SYSTEM_ROOT = Path("/opt/task-monitor")
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(MONITOR_SYSTEM_ROOT))
from models import TaskResult, TaskStatus

# Configure logging to systemd journal (standard for Linux services)
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'  # Simple format for journald
)
logger = logging.getLogger(__name__)


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

        # Log task start to systemd journal
        logger.info(f"[{task_id}] Task started")

        # Configure SDK
        options = ClaudeAgentOptions(
            cwd=str(self.project_root),  # Set working directory
            permission_mode="acceptEdits",  # Auto-accept file edits
            setting_sources=["project"],  # Load project settings (including skills)
        )

        start_time = datetime.now()
        result = TaskResult(
            task_id=task_id,
            status=TaskStatus.RUNNING,
            created_at=start_time,
            started_at=start_time,
        )

        # Create query object explicitly for proper cleanup
        q = query(
            prompt=f"""/task-coordination

Execute the following task:

{task_content}
""",
            options=options
        )

        try:
            full_output = []
            # Iterate through messages
            async for message in q:
                if hasattr(message, 'subtype'):
                    if message.subtype == 'success':
                        result.status = TaskStatus.COMPLETED
                        result.completed_at = datetime.now()
                        # Calculate duration
                        result.duration_seconds = (result.completed_at - start_time).total_seconds()
                        # Capture stdout
                        result.stdout = "\n".join(full_output) if full_output else ""
                        result.worker_output = {
                            "summary": message.result or "Task completed",
                            "raw_output": result.stdout
                        }
                        if hasattr(message, 'usage'):
                            result.worker_output['usage'] = message.usage
                        if hasattr(message, 'total_cost_usd'):
                            result.worker_output['cost_usd'] = message.total_cost_usd
                        # Log completion to systemd journal
                        logger.info(f"[{task_id}] Task completed in {result.duration_seconds:.1f}s")
                        # Exit loop normally (no break needed when we close below)
                        break
                    elif message.subtype == 'error':
                        result.status = TaskStatus.FAILED
                        result.completed_at = datetime.now()
                        result.duration_seconds = (result.completed_at - start_time).total_seconds()
                        result.stdout = "\n".join(full_output) if full_output else ""
                        result.stderr = message.result or "Task failed"
                        result.error = result.stderr
                        # Log failure to systemd journal
                        logger.error(f"[{task_id}] Task failed: {result.error}")
                        break
                else:
                    if hasattr(message, 'content'):
                        for block in message.content:
                            if hasattr(block, 'text'):
                                full_output.append(block.text)

            self._save_result(result)

        except Exception as e:
            result.status = TaskStatus.FAILED
            result.completed_at = datetime.now()
            result.duration_seconds = (result.completed_at - start_time).total_seconds()
            result.error = f"{type(e).__name__}: {str(e)}"
            # Log exception to systemd journal
            logger.error(f"[{task_id}] Task exception: {result.error}")
            self._save_result(result)

        finally:
            # Explicitly close query in the same async context
            # This prevents the cancel scope error when cleanup runs
            try:
                await q.close()
            except Exception:
                # Ignore errors during cleanup (query may already be closed)
                pass

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

