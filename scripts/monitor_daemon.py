import asyncio
import json
import logging
import sys
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Add project root to Python path for module imports
# Note: This is separate from SDK's cwd parameter which is for Claude agent's working directory
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
            try:
                # Add to queue (non-blocking)
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

        # Get project root (parent of scripts directory)
        project_root = Path(__file__).parent.parent.resolve()

        self.executor = TaskExecutor(
            tasks_dir=str(self.tasks_dir),
            results_dir="./results",
            project_root=str(project_root)
        )
        # Event handler will be initialized with event loop in _run()
        self.event_handler = None
        self.observer = Observer()
        self.running = False

    def start(self):
        """Start the monitor daemon."""
        logger.info(f"Starting monitor on {self.tasks_dir}")
        logger.info("Execution model: SEQUENTIAL (one task at a time)")

        self.observer = Observer()
        # Event handler will be initialized in _run() after event loop is created

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
                # Wait for next task (blocks if queue is empty)
                # Use timeout to allow checking self.running flag
                logger.debug("Waiting for task...")
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
