"""
LangGraph Server for DataChat Survey Analysis

This module implements a FastAPI server that exposes the LangGraph survey analysis
workflow as REST API endpoints for the Agent Chat UI.

Features:
- Thread-based workflow execution with checkpointing
- File upload support for .sav SPSS files
- CORS configuration for Agent Chat UI
- Streaming support via Server-Sent Events (SSE)
- State management and resumption

Endpoints:
- POST /threads: Create a new analysis thread
- POST /threads/{thread_id}/invoke: Invoke analysis with file upload
- GET /threads/{thread_id}/state: Get current thread state
- POST /threads/{thread_id}/feedback: Submit human feedback for review steps
- GET /health: Health check endpoint
"""

import os
import logging
import asyncio
import json
from typing import Optional, Dict, Any, AsyncGenerator
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # .env loading is optional

from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel, Field
import uvicorn

# LangGraph imports
from agent.graph import get_graph, run_analysis, resume_analysis
from agent.state import WorkflowState, state_to_dict, get_state_summary


# =============================================================================
# Configuration
# =============================================================================

# Server configuration
# SECURITY NOTE: Default binding to localhost for security. Set LANGGRAPH_HOST to "0.0.0.0" for containerized deployments.
HOST = os.getenv("LANGGRAPH_HOST", "127.0.0.1")
PORT = int(os.getenv("LANGGRAPH_PORT", "8123"))
GRAPH_ID = "survey_analysis"

# CORS configuration
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000"
).split(",")

# File upload configuration
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "data"))
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "100")) * 1024 * 1024  # 100 MB default
ALLOWED_EXTENSIONS = {".sav"}

# Checkpoint configuration
CHECKPOINT_DB_PATH = os.getenv("CHECKPOINT_DB_PATH", "checkpoints.db")


# =============================================================================
# Pydantic Models
# =============================================================================

class ThreadCreate(BaseModel):
    """Request model for creating a new thread."""
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional metadata for the thread"
    )


class InvokeRequest(BaseModel):
    """Request model for invoking the workflow."""
    config: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional workflow configuration overrides"
    )
    stream: bool = Field(
        default=False,
        description="Enable streaming responses"
    )


class FeedbackRequest(BaseModel):
    """Request model for submitting human feedback."""
    approved: bool = Field(
        ...,
        description="Whether to approve or reject the current artifact"
    )
    feedback: Optional[str] = Field(
        default=None,
        description="Optional feedback message explaining the decision"
    )
    iteration_count: Optional[int] = Field(
        default=None,
        description="Current iteration count for the review node"
    )


class ThreadStateResponse(BaseModel):
    """Response model for thread state."""
    thread_id: str
    state: Dict[str, Any]
    summary: Dict[str, Any]
    current_step: int
    requires_human_review: bool


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    graph_id: str
    version: str = "1.0.0"


# =============================================================================
# FastAPI Application
# =============================================================================

app = FastAPI(
    title="DataChat Survey Analysis API",
    description="LangGraph-based SPSS survey data analysis workflow",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# Global Graph Instance
# =============================================================================

# Global graph instance (compiled at startup)
_graph = None


def get_compiled_graph():
    """Get or create the compiled graph instance."""
    global _graph
    if _graph is None:
        logging.info("Compiling LangGraph...")
        _graph = get_graph(checkpointer_path=CHECKPOINT_DB_PATH)
        logging.info("LangGraph compiled successfully")
    return _graph


# =============================================================================
# Startup Event
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize server on startup."""
    # Ensure upload directory exists
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    # Pre-compile graph
    get_compiled_graph()

    logging.info(f"DataChat LangGraph Server starting on {HOST}:{PORT}")
    logging.info(f"Graph ID: {GRAPH_ID}")
    logging.info(f"CORS origins: {ALLOWED_ORIGINS}")
    logging.info(f"Upload directory: {UPLOAD_DIR}")
    logging.info(f"Checkpoint database: {CHECKPOINT_DB_PATH}")


# =============================================================================
# Endpoints
# =============================================================================

@app.get("/", tags=["Root"])
async def root() -> Dict[str, Any]:
    """
    Root endpoint providing API information.

    Returns:
        API metadata and available endpoints
    """
    return {
        "message": "DataChat Survey Analysis API",
        "graph_id": GRAPH_ID,
        "version": "1.0.0",
        "endpoints": {
            "threads": "/threads",
            "invoke": "/threads/{thread_id}/invoke",
            "state": "/threads/{thread_id}/state",
            "feedback": "/threads/{thread_id}/feedback",
            "resume": "/threads/{thread_id}/resume",
            "reviews": "/reviews/{document_name}",
            "health": "/health",
            "docs": "/docs"
        }
    }


from fastapi.responses import FileResponse


@app.get("/reviews/{document_name}", tags=["Reviews"])
async def get_review_document(document_name: str) -> FileResponse:
    """
    Get a review document markdown file.

    This endpoint serves the markdown review documents generated
    during human-in-the-loop workflow steps.

    Args:
        document_name: Name of the review document (e.g., "recoding_rules_review.md")

    Returns:
        The markdown file as a FileResponse

    Raises:
        HTTPException: If the document is not found
    """
    # Security check - only allow specific filenames
    allowed_documents = {
        "recoding_rules_review.md",
        "indicators_review.md",
        "table_specs_review.md",
    }

    if document_name not in allowed_documents:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid document name. Allowed: {', '.join(allowed_documents)}"
        )

    # Construct the file path
    # Reviews are saved to output/reviews/ by the review nodes
    output_dir = Path(os.getenv("OUTPUT_DIR", "output"))
    reviews_dir = output_dir / "reviews"
    file_path = reviews_dir / document_name

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Review document '{document_name}' not found at {file_path}"
        )

    return FileResponse(
        path=file_path,
        media_type="text/markdown",
        filename=document_name,
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
        }
    )


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    """
    Health check endpoint.

    Returns:
        Server health status
    """
    return HealthResponse(
        status="healthy",
        graph_id=GRAPH_ID
    )


@app.post("/threads", tags=["Threads"])
async def create_thread(request: ThreadCreate) -> Dict[str, str]:
    """
    Create a new analysis thread.

    Args:
        request: Thread creation request with optional metadata

    Returns:
        Created thread ID
    """
    import uuid
    thread_id = str(uuid.uuid4())

    logging.info(f"Created new thread: {thread_id}")

    return {
        "thread_id": thread_id,
        "message": "Thread created successfully. Upload a file to invoke analysis."
    }


@app.post("/threads/{thread_id}/invoke", tags=["Threads"])
async def invoke_thread(
    thread_id: str,
    file: UploadFile = File(...),
    config: Optional[str] = Query(None, description="JSON string of config overrides"),
    stream: bool = Query(False, description="Enable streaming")
) -> Dict[str, Any]:
    """
    Invoke the survey analysis workflow for a thread.

    Args:
        thread_id: Thread ID for state persistence
        file: Uploaded SPSS .sav file
        config: Optional JSON string of workflow configuration overrides
        stream: Enable streaming responses (not yet implemented)

    Returns:
        Workflow execution result

    Raises:
        HTTPException: If file validation fails or workflow execution errors
    """
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file extension. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Validate file size
    file_content = await file.read()
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024} MB"
        )

    try:
        # Parse config if provided
        config_dict = None
        if config:
            config_dict = json.loads(config)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON in config parameter"
        )

    # Save uploaded file
    file_path = UPLOAD_DIR / file.filename
    try:
        with open(file_path, "wb") as f:
            f.write(file_content)
        logging.info(f"Saved uploaded file: {file_path}")
    except Exception as e:
        logging.error(f"Failed to save uploaded file: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save uploaded file: {str(e)}"
        )

    # Run analysis
    try:
        logging.info(f"Invoking analysis for thread {thread_id} with file {file.filename}")

        result = run_analysis(
            input_file_path=str(file_path),
            thread_id=thread_id,
            checkpointer_path=CHECKPOINT_DB_PATH,
            config=config_dict
        )

        # Convert ValidationResult objects to dicts for JSON serialization
        result_dict = state_to_dict(result)

        logging.info(f"Analysis completed for thread {thread_id}")

        return {
            "thread_id": thread_id,
            "status": "completed",
            "result": result_dict,
            "summary": get_state_summary(result)
        }

    except Exception as e:
        logging.error(f"Analysis failed for thread {thread_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@app.get("/threads/{thread_id}/state", response_model=ThreadStateResponse, tags=["Threads"])
async def get_thread_state(thread_id: str) -> ThreadStateResponse:
    """
    Get the current state of a thread.

    Args:
        thread_id: Thread ID to query

    Returns:
        Current thread state and summary

    Raises:
        HTTPException: If thread not found
    """
    graph = get_compiled_graph()
    config = {"configurable": {"thread_id": thread_id}}

    try:
        state_snapshot = graph.get_state(config)
        if state_snapshot is None:
            raise HTTPException(
                status_code=404,
                detail=f"Thread '{thread_id}' not found"
            )

        # Convert state to dict
        state_dict = state_to_dict(state_snapshot.values)

        return ThreadStateResponse(
            thread_id=thread_id,
            state=state_dict,
            summary=get_state_summary(state_snapshot.values),
            current_step=state_snapshot.values.get("current_step", 0),
            requires_human_review=state_snapshot.values.get("requires_human_review", False)
        )

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Failed to get state for thread {thread_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get thread state: {str(e)}"
        )


@app.post("/threads/{thread_id}/feedback", tags=["Threads"])
async def submit_feedback(thread_id: str, request: FeedbackRequest) -> Dict[str, Any]:
    """
    Submit human feedback for a review step.

    This endpoint allows the Agent Chat UI to approve/reject artifacts
    during the three-node pattern review steps (Steps 6, 11, 14).

    Args:
        thread_id: Thread ID
        request: Feedback request with approval status and optional feedback

    Returns:
        Updated state after feedback submission

    Raises:
        HTTPException: If thread not found or not in review state
    """
    graph = get_compiled_graph()
    config = {"configurable": {"thread_id": thread_id}}

    try:
        # Get current state
        state_snapshot = graph.get_state(config)
        if state_snapshot is None:
            raise HTTPException(
                status_code=404,
                detail=f"Thread '{thread_id}' not found"
            )

        current_state = state_snapshot.values

        # Check if thread is in review state
        if not current_state.get("requires_human_review", False):
            raise HTTPException(
                status_code=400,
                detail="Thread is not in a review state"
            )

        # Update state based on current step
        current_step = current_state.get("current_step", 0)

        # Map review steps to their state fields
        review_field_mapping = {
            6: ("recoding_approved", "recoding_feedback"),
            11: ("indicators_approved", "indicator_feedback"),
            14: ("table_specs_approved", "table_specs_feedback"),
        }

        if current_step not in review_field_mapping:
            raise HTTPException(
                status_code=400,
                detail=f"Current step {current_step} is not a review step"
            )

        approved_field, feedback_field = review_field_mapping[current_step]

        # Update state with feedback
        current_state[approved_field] = request.approved
        if request.feedback:
            current_state[feedback_field] = request.feedback

        logging.info(
            f"Submitted feedback for thread {thread_id}, "
            f"step {current_step}: approved={request.approved}"
        )

        return {
            "thread_id": thread_id,
            "current_step": current_step,
            "approved": request.approved,
            "feedback": request.feedback,
            "message": "Feedback submitted. Use resume to continue workflow."
        }

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Failed to submit feedback for thread {thread_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit feedback: {str(e)}"
        )


@app.post("/threads/{thread_id}/resume", tags=["Threads"])
async def resume_thread(thread_id: str) -> Dict[str, Any]:
    """
    Resume a paused or interrupted thread.

    This endpoint continues workflow execution after human review
    or after an interruption.

    Args:
        thread_id: Thread ID to resume

    Returns:
        Workflow execution result after resumption

    Raises:
        HTTPException: If thread not found or cannot be resumed
    """
    try:
        logging.info(f"Resuming analysis for thread {thread_id}")

        result = resume_analysis(
            thread_id=thread_id,
            checkpointer_path=CHECKPOINT_DB_PATH
        )

        # Convert ValidationResult objects to dicts
        result_dict = state_to_dict(result)

        logging.info(f"Analysis resumed and completed for thread {thread_id}")

        return {
            "thread_id": thread_id,
            "status": "completed",
            "result": result_dict,
            "summary": get_state_summary(result)
        }

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        logging.error(f"Failed to resume thread {thread_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to resume thread: {str(e)}"
        )


# =============================================================================
# Streaming Support (Future Enhancement)
# =============================================================================

async def stream_workflow(
    graph,
    initial_state: WorkflowState,
    config: Dict[str, Any]
) -> AsyncGenerator[str, None]:
    """
    Stream workflow execution progress via SSE.

    Args:
        graph: Compiled LangGraph instance
        initial_state: Initial workflow state
        config: Run configuration with thread_id

    Yields:
        SSE-formatted events
    """
    try:
        # Stream mode: updates for state changes
        async for chunk in graph.astream(initial_state, config, stream_mode="updates"):
            # Format as SSE event
            event = f"data: {json.dumps(chunk)}\n\n"
            yield event

        # Send completion event
        yield f"data: {json.dumps({'status': 'completed'})}\n\n"

    except Exception as e:
        # Send error event
        error_event = {"status": "error", "error": str(e)}
        yield f"data: {json.dumps(error_event)}\n\n"


@app.post("/threads/{thread_id}/stream", tags=["Threads"])
async def invoke_thread_stream(
    thread_id: str,
    file: UploadFile = File(...),
    config: Optional[str] = Query(None, description="JSON string of config overrides")
) -> StreamingResponse:
    """
    Invoke workflow with streaming support (SSE).

    This endpoint streams real-time updates during workflow execution.
    Useful for long-running analyses with progress updates.

    Args:
        thread_id: Thread ID for state persistence
        file: Uploaded SPSS .sav file
        config: Optional JSON string of workflow configuration overrides

    Returns:
        Server-Sent Events stream

    Raises:
        HTTPException: If file validation fails
    """
    # Validate file
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file extension. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Save file
    file_content = await file.read()
    file_path = UPLOAD_DIR / file.filename
    with open(file_path, "wb") as f:
        f.write(file_content)

    # Parse config
    config_dict = None
    if config:
        try:
            config_dict = json.loads(config)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=400,
                detail="Invalid JSON in config parameter"
            )

    # Create initial state
    from agent.state import create_initial_state
    from agent.config import get_config_with_env_overrides, DEFAULT_CONFIG

    workflow_config = get_config_with_env_overrides(DEFAULT_CONFIG.copy())
    if config_dict:
        workflow_config.update(config_dict)

    initial_state = create_initial_state(str(file_path), workflow_config)

    # Get graph
    graph = get_compiled_graph()
    run_config = {"configurable": {"thread_id": thread_id}}

    # Return streaming response
    return StreamingResponse(
        stream_workflow(graph, initial_state, run_config),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


# =============================================================================
# Main Entry Point
# =============================================================================

def main():
    """
    Run the LangGraph server.

    Usage:
        python -m agent.server
        or
        python agent/server.py
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    uvicorn.run(
        "agent.server:app",
        host=HOST,
        port=PORT,
        reload=False,
        log_level="info"
    )


if __name__ == "__main__":
    main()
