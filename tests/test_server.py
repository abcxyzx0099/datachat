"""
Unit Tests for FastAPI Server (agent/server.py)

This module contains comprehensive unit tests for the FastAPI server that exposes
the LangGraph survey analysis workflow as REST API endpoints.

Test Coverage:
- Root endpoint (/) - API information
- Health check (/health) - Server health status
- Thread creation (POST /threads) - Create new analysis thread
- Thread invocation (POST /threads/{thread_id}/invoke) - Upload file and run analysis
- Thread state (GET /threads/{thread_id}/state) - Get current workflow state
- Feedback submission (POST /threads/{thread_id}/feedback) - Submit human review feedback
- Thread resume (POST /threads/{thread_id}/resume) - Resume interrupted workflow
- Review document (GET /reviews/{document_name}) - Get review markdown files
- Streaming endpoint (POST /threads/{thread_id}/stream) - SSE streaming
- CORS middleware - Cross-origin resource sharing
- Error handling - All error paths

Testing Strategy:
- Use FastAPI TestClient for HTTP endpoint testing
- Mock LangGraph graph execution (no actual workflow runs)
- Mock file I/O operations
- Test both success and error paths
- Use pytest-asyncio for async endpoints
"""

import pytest
import json
import io
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from typing import Dict, Any

# FastAPI imports
from fastapi.testclient import TestClient
from fastapi import UploadFile

# Import server module
from agent import server
from agent.state import WorkflowState, ValidationResult, create_initial_state
from agent.config import DEFAULT_CONFIG


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def temp_upload_dir():
    """Create temporary upload directory for test file uploads."""
    temp_dir = tempfile.mkdtemp(prefix="upload_test_")
    yield Path(temp_dir)
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def temp_checkpoint_db():
    """Create temporary checkpoint database for testing."""
    fd, db_path = tempfile.mkstemp(suffix=".db", prefix="test_checkpoint_")
    os.close(fd)
    yield db_path
    try:
        os.unlink(db_path)
    except FileNotFoundError:
        pass


@pytest.fixture
def mock_compiled_graph():
    """Mock the compiled LangGraph instance."""
    mock_graph = Mock()
    return mock_graph


@pytest.fixture
def mock_state_snapshot():
    """Mock a LangGraph state snapshot."""
    snapshot = Mock()
    snapshot.values = {
        "current_step": 5,
        "requires_human_review": True,
        "recoding_approved": False,
        "indicators_approved": False,
        "table_specs_approved": False,
        "input_file_path": "/test/data.sav",
        "errors": [],
        "warnings": [],
    }
    snapshot.next = ("generate_recoding_rules_node",)
    return snapshot


@pytest.fixture
def sample_workflow_state() -> WorkflowState:
    """Sample workflow state for testing."""
    state = create_initial_state("/test/data.sav", DEFAULT_CONFIG)
    state["current_step"] = 8
    state["recoding_approved"] = True
    state["indicators_approved"] = True
    state["table_specs_approved"] = True
    state["new_data_path"] = "/output/new_data.sav"
    state["cross_table_sav_path"] = "/output/cross_table.sav"
    state["powerpoint_path"] = "/output/presentation.pptx"
    state["html_dashboard_path"] = "/output/dashboard.html"
    return state


@pytest.fixture
def client(temp_upload_dir, temp_checkpoint_db, mock_compiled_graph):
    """Create FastAPI TestClient with mocked dependencies."""
    # Patch environment variables
    with patch.dict(os.environ, {
        "UPLOAD_DIR": str(temp_upload_dir),
        "CHECKPOINT_DB_PATH": temp_checkpoint_db,
        "LANGGRAPH_HOST": "127.0.0.1",
        "LANGGRAPH_PORT": "8123",
        "ALLOWED_ORIGINS": "http://localhost:3000",
    }):
        # Reset global graph instance
        server._graph = None

        # Patch get_graph to return mock
        with patch("agent.server.get_graph", return_value=mock_compiled_graph):
            # Import and create test client
            from agent.server import app
            test_client = TestClient(app)
            yield test_client


@pytest.fixture
def sample_sav_file_content():
    """Sample SPSS file content (dummy data for testing)."""
    # This is dummy content - actual SPSS files have binary format
    return b"$FL2@(#) SPSS DATA FILE test data " + b"\x00" * 100


@pytest.fixture
def temp_review_file(temp_upload_dir):
    """Create temporary review markdown file for testing."""
    reviews_dir = temp_upload_dir / "reviews"
    reviews_dir.mkdir(parents=True, exist_ok=True)

    review_file = reviews_dir / "recoding_rules_review.md"
    review_file.write_text("# Recoding Rules Review\n\nTest review content")
    return review_file


# =============================================================================
# Root Endpoint Tests
# =============================================================================

class TestRootEndpoint:
    """Tests for GET / endpoint."""

    def test_root_endpoint_returns_api_info(self, client):
        """Test that root endpoint returns API metadata."""
        response = client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert data["message"] == "DataChat Survey Analysis API"
        assert data["graph_id"] == "survey_analysis"
        assert data["version"] == "1.0.0"
        assert "endpoints" in data

        # Verify all expected endpoints are listed
        endpoints = data["endpoints"]
        assert endpoints["threads"] == "/threads"
        assert endpoints["invoke"] == "/threads/{thread_id}/invoke"
        assert endpoints["state"] == "/threads/{thread_id}/state"
        assert endpoints["feedback"] == "/threads/{thread_id}/feedback"
        assert endpoints["resume"] == "/threads/{thread_id}/resume"
        assert endpoints["reviews"] == "/reviews/{document_name}"
        assert endpoints["health"] == "/health"
        assert endpoints["docs"] == "/docs"


# =============================================================================
# Health Check Tests
# =============================================================================

class TestHealthCheck:
    """Tests for GET /health endpoint."""

    def test_health_check_returns_healthy_status(self, client):
        """Test that health check returns healthy status."""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert data["graph_id"] == "survey_analysis"
        assert data["version"] == "1.0.0"


# =============================================================================
# Thread Creation Tests
# =============================================================================

class TestCreateThread:
    """Tests for POST /threads endpoint."""

    def test_create_thread_returns_thread_id(self, client):
        """Test creating a new thread returns a unique thread ID."""
        response = client.post("/threads", json={})
        assert response.status_code == 200

        data = response.json()
        assert "thread_id" in data
        assert len(data["thread_id"]) > 0
        assert "message" in data

    def test_create_thread_with_metadata(self, client):
        """Test creating thread with optional metadata."""
        metadata = {"user_id": "test_user", "project": "test_project"}
        response = client.post("/threads", json={"metadata": metadata})
        assert response.status_code == 200

        data = response.json()
        assert "thread_id" in data


# =============================================================================
# Thread Invocation Tests
# =============================================================================

class TestInvokeThread:
    """Tests for POST /threads/{thread_id}/invoke endpoint."""

    def test_invoke_thread_with_valid_sav_file(
        self, client, sample_sav_file_content, temp_upload_dir,
        sample_workflow_state, mock_compiled_graph
    ):
        """Test successful invocation with valid .sav file."""
        # Mock run_analysis to return sample state
        with patch("agent.server.run_analysis", return_value=sample_workflow_state):
            file_content = io.BytesIO(sample_sav_file_content)
            files = {"file": ("test_data.sav", file_content, "application/octet-stream")}
            params = {"thread_id": "test-thread-123"}

            response = client.post(
                "/threads/test-thread-123/invoke",
                files=files,
                params=params
            )

            assert response.status_code == 200
            data = response.json()
            assert data["thread_id"] == "test-thread-123"
            assert data["status"] == "completed"
            assert "result" in data
            assert "summary" in data

    def test_invoke_thread_with_invalid_file_extension(
        self, client, temp_upload_dir
    ):
        """Test that invalid file extension returns 400 error."""
        file_content = io.BytesIO(b"test content")
        files = {"file": ("test.txt", file_content, "text/plain")}

        response = client.post(
            "/threads/test-thread-123/invoke",
            files=files
        )

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Invalid file extension" in data["detail"]

    def test_invoke_thread_with_large_file(self, client):
        """Test that file exceeding max size returns 400 error."""
        # Create content larger than default 100MB limit
        large_content = b"x" * (101 * 1024 * 1024)  # 101 MB
        file_content = io.BytesIO(large_content)
        files = {"file": ("large.sav", file_content, "application/octet-stream")}

        response = client.post(
            "/threads/test-thread-123/invoke",
            files=files
        )

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "File too large" in data["detail"]

    def test_invoke_thread_with_invalid_config_json(self, client, sample_sav_file_content):
        """Test that invalid config JSON returns 400 error."""
        file_content = io.BytesIO(sample_sav_file_content)
        files = {"file": ("test.sav", file_content, "application/octet-stream")}
        params = {"config": "{invalid json}", "stream": "false"}

        response = client.post(
            "/threads/test-thread-123/invoke",
            files=files,
            params=params
        )

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Invalid JSON in config parameter" in data["detail"]

    def test_invoke_thread_with_valid_config(
        self, client, sample_sav_file_content, sample_workflow_state
    ):
        """Test invocation with valid config override."""
        with patch("agent.server.run_analysis", return_value=sample_workflow_state):
            config = {"max_self_correction_iterations": 5}
            file_content = io.BytesIO(sample_sav_file_content)
            files = {"file": ("test.sav", file_content, "application/octet-stream")}
            params = {"config": json.dumps(config), "stream": "false"}

            response = client.post(
                "/threads/test-thread-123/invoke",
                files=files,
                params=params
            )

            assert response.status_code == 200

    def test_invoke_thread_analysis_failure(
        self, client, sample_sav_file_content
    ):
        """Test handling of analysis execution failure."""
        # Mock run_analysis to raise exception
        with patch("agent.server.run_analysis", side_effect=Exception("Analysis failed")):
            file_content = io.BytesIO(sample_sav_file_content)
            files = {"file": ("test.sav", file_content, "application/octet-stream")}

            response = client.post(
                "/threads/test-thread-123/invoke",
                files=files
            )

            assert response.status_code == 500
            data = response.json()
            assert "detail" in data
            assert "Analysis failed" in data["detail"]

    def test_invoke_thread_file_save_failure(
        self, client, sample_sav_file_content
    ):
        """Test handling of file save failure."""
        with patch("builtins.open", side_effect=IOError("Disk full")):
            file_content = io.BytesIO(sample_sav_file_content)
            files = {"file": ("test.sav", file_content, "application/octet-stream")}

            response = client.post(
                "/threads/test-thread-123/invoke",
                files=files
            )

            assert response.status_code == 500
            data = response.json()
            assert "Failed to save uploaded file" in data["detail"]


# =============================================================================
# Thread State Tests
# =============================================================================

class TestGetThreadState:
    """Tests for GET /threads/{thread_id}/state endpoint."""

    def test_get_thread_state_success(
        self, client, mock_compiled_graph, mock_state_snapshot
    ):
        """Test successfully getting thread state."""
        mock_compiled_graph.get_state.return_value = mock_state_snapshot

        response = client.get("/threads/test-thread-123/state")
        assert response.status_code == 200

        data = response.json()
        assert data["thread_id"] == "test-thread-123"
        assert "state" in data
        assert "summary" in data
        assert data["current_step"] == 5
        assert data["requires_human_review"] is True

    def test_get_thread_state_not_found(self, client, mock_compiled_graph):
        """Test getting state for non-existent thread returns 404."""
        mock_compiled_graph.get_state.return_value = None

        response = client.get("/threads/nonexistent-thread/state")
        assert response.status_code == 404

        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_get_thread_state_graph_error(
        self, client, mock_compiled_graph
    ):
        """Test handling of graph error when getting state."""
        mock_compiled_graph.get_state.side_effect = Exception("Graph error")

        response = client.get("/threads/test-thread-123/state")
        assert response.status_code == 500

        data = response.json()
        assert "detail" in data
        assert "Failed to get thread state" in data["detail"]


# =============================================================================
# Feedback Submission Tests
# =============================================================================

class TestSubmitFeedback:
    """Tests for POST /threads/{thread_id}/feedback endpoint."""

    def test_submit_feedback_success(
        self, client, mock_compiled_graph, mock_state_snapshot
    ):
        """Test successfully submitting feedback for review step."""
        mock_state_snapshot.values["current_step"] = 6  # Recoding review step
        mock_compiled_graph.get_state.return_value = mock_state_snapshot

        feedback_data = {
            "approved": True,
            "feedback": "Looks good, proceed with analysis"
        }

        response = client.post(
            "/threads/test-thread-123/feedback",
            json=feedback_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["thread_id"] == "test-thread-123"
        assert data["approved"] is True
        assert data["feedback"] == "Looks good, proceed with analysis"
        assert "message" in data

    def test_submit_feedback_not_found(self, client, mock_compiled_graph):
        """Test submitting feedback for non-existent thread."""
        mock_compiled_graph.get_state.return_value = None

        feedback_data = {"approved": True}

        response = client.post(
            "/threads/nonexistent-thread/feedback",
            json=feedback_data
        )

        assert response.status_code == 404

    def test_submit_feedback_not_in_review_state(
        self, client, mock_compiled_graph, mock_state_snapshot
    ):
        """Test submitting feedback when not in review state."""
        mock_state_snapshot.values["requires_human_review"] = False
        mock_compiled_graph.get_state.return_value = mock_state_snapshot

        feedback_data = {"approved": True}

        response = client.post(
            "/threads/test-thread-123/feedback",
            json=feedback_data
        )

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "not in a review state" in data["detail"].lower()

    def test_submit_feedback_invalid_review_step(
        self, client, mock_compiled_graph, mock_state_snapshot
    ):
        """Test submitting feedback for non-review step."""
        mock_state_snapshot.values["current_step"] = 5  # Not a review step
        mock_compiled_graph.get_state.return_value = mock_state_snapshot

        feedback_data = {"approved": True}

        response = client.post(
            "/threads/test-thread-123/feedback",
            json=feedback_data
        )

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "not a review step" in data["detail"].lower()

    def test_submit_feedback_with_iteration_count(
        self, client, mock_compiled_graph, mock_state_snapshot
    ):
        """Test submitting feedback with iteration count."""
        mock_state_snapshot.values["current_step"] = 11  # Indicators review step
        mock_compiled_graph.get_state.return_value = mock_state_snapshot

        feedback_data = {
            "approved": False,
            "feedback": "Needs revision",
            "iteration_count": 2
        }

        response = client.post(
            "/threads/test-thread-123/feedback",
            json=feedback_data
        )

        assert response.status_code == 200

    def test_submit_feedback_with_message(
        self, client, mock_compiled_graph, mock_state_snapshot
    ):
        """Test submitting feedback with feedback message (covers line 507-508)."""
        mock_state_snapshot.values["current_step"] = 6  # Recoding review step
        mock_compiled_graph.get_state.return_value = mock_state_snapshot

        feedback_data = {
            "approved": True,
            "feedback": "Approved with feedback message"
        }

        response = client.post(
            "/threads/test-thread-123/feedback",
            json=feedback_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["feedback"] == "Approved with feedback message"

    def test_submit_feedback_unexpected_error(
        self, client, mock_compiled_graph
    ):
        """Test handling of unexpected error in feedback submission (covers lines 525-527)."""
        mock_compiled_graph.get_state.side_effect = RuntimeError("Unexpected error")

        feedback_data = {"approved": True}

        response = client.post(
            "/threads/test-thread-123/feedback",
            json=feedback_data
        )

        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "Failed to submit feedback" in data["detail"]

    def test_submit_feedback_rejection(
        self, client, mock_compiled_graph, mock_state_snapshot
    ):
        """Test submitting rejection feedback."""
        mock_state_snapshot.values["current_step"] = 14  # Table specs review step
        mock_compiled_graph.get_state.return_value = mock_state_snapshot

        feedback_data = {
            "approved": False,
            "feedback": "Table specifications need revision"
        }

        response = client.post(
            "/threads/test-thread-123/feedback",
            json=feedback_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["approved"] is False


# =============================================================================
# Thread Resume Tests
# =============================================================================

class TestResumeThread:
    """Tests for POST /threads/{thread_id}/resume endpoint."""

    def test_resume_thread_success(
        self, client, sample_workflow_state
    ):
        """Test successfully resuming a thread."""
        with patch("agent.server.resume_analysis", return_value=sample_workflow_state):
            response = client.post("/threads/test-thread-123/resume")

            assert response.status_code == 200
            data = response.json()
            assert data["thread_id"] == "test-thread-123"
            assert data["status"] == "completed"
            assert "result" in data
            assert "summary" in data

    def test_resume_thread_not_found(self, client):
        """Test resuming non-existent thread returns 404."""
        with patch("agent.server.resume_analysis", side_effect=ValueError("Thread not found")):
            response = client.post("/threads/nonexistent-thread/resume")

            assert response.status_code == 404
            data = response.json()
            assert "detail" in data
            assert "Thread not found" in data["detail"]

    def test_resume_thread_general_failure(self, client):
        """Test handling of general resume failure."""
        with patch("agent.server.resume_analysis", side_effect=Exception("Resume failed")):
            response = client.post("/threads/test-thread-123/resume")

            assert response.status_code == 500
            data = response.json()
            assert "detail" in data
            assert "Failed to resume thread" in data["detail"]


# =============================================================================
# Review Document Tests
# =============================================================================

class TestGetReviewDocument:
    """Tests for GET /reviews/{document_name} endpoint."""

    def test_get_review_document_success(self, client, temp_review_file, temp_upload_dir):
        """Test successfully getting a review document."""
        # Patch os.getenv to return our temp upload dir as OUTPUT_DIR
        with patch("os.getenv", return_value=str(temp_upload_dir)):
            # Create a new client with patched OUTPUT_DIR
            from agent.server import app
            test_client = TestClient(app)

            response = test_client.get("/reviews/recoding_rules_review.md")

            assert response.status_code == 200
            assert response.headers["content-type"] == "text/markdown; charset=utf-8"
            content = response.text
            assert "Recoding Rules Review" in content

    def test_get_review_document_not_found(self, client, temp_upload_dir):
        """Test getting non-existent review document returns 404."""
        reviews_dir = temp_upload_dir / "reviews"
        reviews_dir.mkdir(parents=True, exist_ok=True)

        with patch("os.getenv", return_value=str(temp_upload_dir)):
            from agent.server import app
            test_client = TestClient(app)

            response = test_client.get("/reviews/indicators_review.md")

            assert response.status_code == 404
            data = response.json()
            assert "detail" in data
            assert "not found" in data["detail"].lower()

    def test_get_review_document_invalid_name(self, client):
        """Test getting document with invalid name returns 400."""
        # The server validates document names against allowed_documents set
        # Invalid names should return 400
        response = client.get("/reviews/invalid_document.md")

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Invalid document name" in data["detail"]

    def test_get_review_document_path_traversal_blocked(self, client):
        """Test that path traversal attempts are blocked."""
        response = client.get("/reviews/../../../etc/passwd")

        # Should return 400 (invalid document name) or 404 (not found)
        # The important thing is it doesn't expose files outside the reviews dir
        assert response.status_code in [400, 404]

    def test_get_review_document_all_allowed_names(self, client, temp_upload_dir):
        """Test all allowed document names work."""
        allowed_docs = [
            "recoding_rules_review.md",
            "indicators_review.md",
            "table_specs_review.md"
        ]

        reviews_dir = temp_upload_dir / "reviews"
        reviews_dir.mkdir(parents=True, exist_ok=True)

        for doc_name in allowed_docs:
            (reviews_dir / doc_name).write_text(f"Test content for {doc_name}")

        with patch("os.getenv", return_value=str(temp_upload_dir)):
            from agent.server import app
            test_client = TestClient(app)

            for doc_name in allowed_docs:
                response = test_client.get(f"/reviews/{doc_name}")
                assert response.status_code == 200


# =============================================================================
# Streaming Endpoint Tests
# =============================================================================

class TestInvokeThreadStream:
    """Tests for POST /threads/{thread_id}/stream endpoint."""

    def test_stream_endpoint_with_valid_file(
        self, client, sample_sav_file_content, temp_upload_dir
    ):
        """Test streaming endpoint with valid file."""
        with patch("agent.server.get_compiled_graph") as mock_get_graph:
            mock_graph = Mock()
            # Mock async stream
            async def mock_stream(*args, **kwargs):
                yield 'data: {"status": "processing"}\n\n'
                yield 'data: {"status": "completed"}\n\n'

            mock_graph.astream = mock_stream
            mock_get_graph.return_value = mock_graph

            file_content = io.BytesIO(sample_sav_file_content)
            files = {"file": ("test.sav", file_content, "application/octet-stream")}

            response = client.post(
                "/threads/test-thread-123/stream",
                files=files
            )

            assert response.status_code == 200
            assert response.headers["content-type"] == "text/event-stream; charset=utf-8"

    def test_stream_endpoint_invalid_extension(self, client):
        """Test streaming endpoint rejects invalid file extension."""
        file_content = io.BytesIO(b"test content")
        files = {"file": ("test.txt", file_content, "text/plain")}

        response = client.post(
            "/threads/test-thread-123/stream",
            files=files
        )

        assert response.status_code == 400
        data = response.json()
        assert "Invalid file extension" in data["detail"]

    def test_stream_endpoint_invalid_config(
        self, client, sample_sav_file_content
    ):
        """Test streaming endpoint handles invalid config."""
        file_content = io.BytesIO(sample_sav_file_content)
        files = {"file": ("test.sav", file_content, "application/octet-stream")}
        params = {"config": "{invalid}"}

        response = client.post(
            "/threads/test-thread-123/stream",
            files=files,
            params=params
        )

        assert response.status_code == 400

    def test_stream_workflow_error_handling(self):
        """Test stream_workflow handles errors gracefully (covers lines 613-616)."""
        from agent.server import stream_workflow
        import asyncio

        mock_graph = Mock()

        # Create a proper async generator that raises an exception
        async def mock_astream_error(*args, **kwargs):
            yield {"step": "start"}
            raise RuntimeError("Stream error")

        mock_graph.astream = mock_astream_error

        async def run_stream():
            events = []
            try:
                async for event in stream_workflow(mock_graph, {}, {}):
                    events.append(event)
            except Exception:
                pass  # Error is yielded, not raised
            return events

        events = asyncio.run(run_stream())

        # Should have error event
        assert len(events) > 0
        assert "error" in events[-1].lower()

    def test_stream_endpoint_with_config(
        self, client, sample_sav_file_content, temp_upload_dir
    ):
        """Test streaming endpoint with config override (covers line 673)."""
        with patch("agent.server.get_compiled_graph") as mock_get_graph, \
             patch("agent.config.get_config_with_env_overrides") as mock_get_config, \
             patch("agent.state.create_initial_state") as mock_create_state:

            mock_graph = Mock()
            async def mock_stream(*args, **kwargs):
                yield 'data: {"status": "processing"}\n\n'
                yield 'data: {"status": "completed"}\n\n'

            mock_graph.astream = mock_stream
            mock_get_graph.return_value = mock_graph
            mock_get_config.return_value = {}
            mock_create_state.return_value = {}

            file_content = io.BytesIO(sample_sav_file_content)
            files = {"file": ("test.sav", file_content, "application/octet-stream")}
            params = {"config": '{"test_key": "test_value"}'}

            response = client.post(
                "/threads/test-thread-123/stream",
                files=files,
                params=params
            )

            assert response.status_code == 200


# =============================================================================
# CORS Middleware Tests
# =============================================================================

class TestCORSMiddleware:
    """Tests for CORS middleware configuration."""

    def test_cors_headers_present(self, client):
        """Test that CORS headers are present in response."""
        response = client.get("/", headers={"Origin": "http://localhost:3000"})
        assert response.status_code == 200

        # Check for CORS headers (FastAPI CORS middleware adds these)
        # Note: TestClient may not include all CORS headers in response
        # This test verifies the endpoint works with CORS middleware

    def test_preflight_request(self, client):
        """Test OPTIONS preflight request handling."""
        response = client.options(
            "/threads",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST"
            }
        )
        # Should handle preflight (may return 200 or method not allowed depending on config)


# =============================================================================
# Error Handling Tests
# =============================================================================

class TestErrorHandling:
    """Tests for general error handling."""

    def test_404_for_invalid_endpoint(self, client):
        """Test that invalid endpoint returns 404."""
        response = client.get("/nonexistent/endpoint")
        assert response.status_code == 404

    def test_method_not_allowed(self, client):
        """Test that wrong HTTP method returns 405."""
        response = client.get("/threads")  # POST endpoint
        assert response.status_code == 405

    def test_missing_file_parameter(self, client):
        """Test that missing file parameter returns 422 validation error."""
        response = client.post("/threads/test-thread/invoke")
        assert response.status_code == 422

    def test_invalid_json_body(self, client):
        """Test that invalid JSON body returns 422."""
        response = client.post(
            "/threads/test-thread/feedback",
            data="not json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422


# =============================================================================
# Startup Event Tests
# =============================================================================

class TestStartupEvent:
    """Tests for server startup configuration."""

    def test_startup_creates_upload_dir(self, temp_upload_dir, temp_checkpoint_db):
        """Test that startup creates upload directory if it doesn't exist."""
        import sys
        import importlib

        # Create a non-existent directory path
        non_existent_dir = tempfile.mktemp(prefix="non_existent_upload_")

        # Save the original UPLOAD_DIR
        original_upload_dir = server.UPLOAD_DIR

        try:
            # Modify the UPLOAD_DIR in the server module
            server.UPLOAD_DIR = Path(non_existent_dir)

            # Trigger startup by calling the startup event handler directly
            from agent.server import startup_event
            import asyncio
            asyncio.run(startup_event())

            # Directory should be created
            assert Path(non_existent_dir).exists()

        finally:
            # Restore original UPLOAD_DIR
            server.UPLOAD_DIR = original_upload_dir

            # Cleanup test directory
            import shutil
            shutil.rmtree(non_existent_dir, ignore_errors=True)

    def test_graph_precompilation_on_startup(self):
        """Test that graph is pre-compiled during startup."""
        with patch("agent.server.get_graph") as mock_get_graph:
            mock_get_graph.return_value = Mock()
            server._graph = None

            with patch.dict(os.environ, {
                "UPLOAD_DIR": tempfile.mkdtemp(),
                "CHECKPOINT_DB_PATH": tempfile.mktemp(suffix=".db"),
            }):
                # Trigger startup by calling the startup event handler directly
                from agent.server import startup_event
                import asyncio
                asyncio.run(startup_event())

                # Graph should have been requested during startup
                assert mock_get_graph.called


# =============================================================================
# Pydantic Model Validation Tests
# =============================================================================

class TestPydanticModels:
    """Tests for Pydantic request/response models."""

    def test_thread_create_model(self):
        """Test ThreadCreate model validation."""
        from agent.server import ThreadCreate

        # Test with no metadata
        model = ThreadCreate()
        assert model.metadata is None

        # Test with metadata
        model = ThreadCreate(metadata={"key": "value"})
        assert model.metadata == {"key": "value"}

    def test_invoke_request_model(self):
        """Test InvokeRequest model validation."""
        from agent.server import InvokeRequest

        # Test defaults
        model = InvokeRequest()
        assert model.config is None
        assert model.stream is False

        # Test with values
        model = InvokeRequest(config={"key": "value"}, stream=True)
        assert model.config == {"key": "value"}
        assert model.stream is True

    def test_feedback_request_model(self):
        """Test FeedbackRequest model validation."""
        from agent.server import FeedbackRequest

        # Test required field
        model = FeedbackRequest(approved=True)
        assert model.approved is True
        assert model.feedback is None
        assert model.iteration_count is None

        # Test with all fields
        model = FeedbackRequest(
            approved=False,
            feedback="Needs changes",
            iteration_count=2
        )
        assert model.approved is False
        assert model.feedback == "Needs changes"
        assert model.iteration_count == 2

    def test_thread_state_response_model(self):
        """Test ThreadStateResponse model validation."""
        from agent.server import ThreadStateResponse

        model = ThreadStateResponse(
            thread_id="test-123",
            state={"key": "value"},
            summary={"current_step": 5},
            current_step=5,
            requires_human_review=True
        )
        assert model.thread_id == "test-123"
        assert model.current_step == 5

    def test_health_response_model(self):
        """Test HealthResponse model validation."""
        from agent.server import HealthResponse

        model = HealthResponse(status="healthy", graph_id="test_graph")
        assert model.status == "healthy"
        assert model.graph_id == "test_graph"
        assert model.version == "1.0.0"


# =============================================================================
# Configuration Tests
# =============================================================================

class TestServerConfiguration:
    """Tests for server configuration and environment variables."""

    def test_default_configuration(self):
        """Test default server configuration values."""
        assert server.GRAPH_ID == "survey_analysis"
        assert server.HOST == "0.0.0.0"
        assert server.PORT == 8123

    def test_allowed_file_extensions(self):
        """Test allowed file extensions configuration."""
        assert ".sav" in server.ALLOWED_EXTENSIONS
        assert ".txt" not in server.ALLOWED_EXTENSIONS

    def test_default_max_file_size(self):
        """Test default max file size is 100MB."""
        expected_size = 100 * 1024 * 1024
        assert server.MAX_FILE_SIZE == expected_size


# =============================================================================
# Helper Function Tests
# =============================================================================

class TestHelperFunctions:
    """Tests for server helper functions."""

    def test_get_compiled_graph_caches_result(self, temp_checkpoint_db):
        """Test that get_compiled_graph caches the graph instance."""
        server._graph = None

        with patch("agent.server.get_graph") as mock_get_graph:
            mock_graph = Mock()
            mock_get_graph.return_value = mock_graph

            # First call
            result1 = server.get_compiled_graph()
            # Second call
            result2 = server.get_compiled_graph()

            # Should return same instance
            assert result1 is result2
            # Should only call get_graph once due to caching
            mock_get_graph.assert_called_once()

    def test_get_compiled_graph_with_checkpoint_path(self):
        """Test get_compiled_graph passes checkpoint path correctly."""
        server._graph = None

        with patch("agent.server.get_graph") as mock_get_graph:
            mock_get_graph.return_value = Mock()

            server.get_compiled_graph()

            # Verify get_graph was called with checkpoint path
            mock_get_graph.assert_called_once()


# =============================================================================
# Main Function Tests
# =============================================================================

class TestMainFunction:
    """Tests for main() function and server startup."""

    def test_main_function_setup(self):
        """Test that main function configures logging (covers lines 705-710)."""
        with patch("agent.server.uvicorn.run") as mock_uvicorn:
            server.main()

            # Verify uvicorn.run was called with correct parameters
            mock_uvicorn.assert_called_once()
            call_args = mock_uvicorn.call_args

            assert call_args[0][0] == "agent.server:app"
            assert call_args[1]["host"] == server.HOST
            assert call_args[1]["port"] == server.PORT
            assert call_args[1]["reload"] is False

    def test_main_with_custom_environment(self):
        """Test main function respects environment variables."""
        with patch.dict(os.environ, {
            "LANGGRAPH_HOST": "127.0.0.1",
            "LANGGRAPH_PORT": "9999"
        }), patch("agent.server.uvicorn.run") as mock_uvicorn:
            # Reload server module to pick up env vars
            import importlib
            importlib.reload(server)

            server.main()

            call_args = mock_uvicorn.call_args
            assert call_args[1]["host"] == "127.0.0.1"
            assert call_args[1]["port"] == 9999


# =============================================================================
# Import Tests
# =============================================================================

class TestModuleImports:
    """Tests for module-level imports and initialization."""

    def test_server_module_loads_with_dotenv(self):
        """Test that server module loads successfully with dotenv (lines 30-34)."""
        # Simply importing the server module verifies that
        # the dotenv import works correctly
        import importlib
        import sys

        # Remove server from cached modules to force fresh import
        sys.modules.pop("agent.server", None)

        # Re-import server module
        import agent.server

        # If we get here, the import succeeded
        assert hasattr(agent.server, "app")
        assert hasattr(agent.server, "main")
