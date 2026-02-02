# LangGraph Server for DataChat

This document describes the LangGraph server implementation for the DataChat Survey Analysis application.

## Overview

The LangGraph server exposes the 22-step survey analysis workflow as REST API endpoints, enabling the Agent Chat UI to interact with the workflow graph programmatically.

**Server Type**: Custom FastAPI server (Option B from task requirements)
**Port**: 8123 (default)
**Graph ID**: `survey_analysis`

## Quick Start

### Starting the Server

```bash
# Default: host=0.0.0.0, port=8123
bash scripts/start_server.sh

# Custom port
bash scripts/start_server.sh --port 9000

# Custom host and port
bash scripts/start_server.sh --host 127.0.0.1 --port 8080
```

### Stopping the Server

Press `Ctrl+C` in the terminal where the server is running.

## API Endpoints

### Root Endpoint
```
GET /
```
Returns API information and available endpoints.

### Health Check
```
GET /health
```
Returns server health status.

**Response:**
```json
{
  "status": "healthy",
  "graph_id": "survey_analysis",
  "version": "1.0.0"
}
```

### Create Thread
```
POST /threads
```
Create a new analysis thread with a unique thread ID.

**Request:**
```json
{
  "metadata": {
    "description": "Optional metadata"
  }
}
```

**Response:**
```json
{
  "thread_id": "uuid-string",
  "message": "Thread created successfully. Upload a file to invoke analysis."
}
```

### Invoke Analysis
```
POST /threads/{thread_id}/invoke
```
Upload a SPSS .sav file and invoke the survey analysis workflow.

**Parameters:**
- `thread_id`: Thread ID (path parameter)
- `file`: SPSS .sav file (form-data)
- `config`: Optional JSON string of workflow configuration overrides (query parameter)
- `stream`: Enable streaming (query parameter, default: false)

**Example using curl:**
```bash
curl -X POST "http://localhost:8123/threads/{thread_id}/invoke" \
  -F "file=@survey_data.sav" \
  -F 'config={"llm_provider": "DEEPSEEK"}'
```

**Response:**
```json
{
  "thread_id": "uuid-string",
  "status": "completed",
  "result": {
    "current_step": 22,
    "powerpoint_file": "output/20240201_153045/presentation.pptx",
    "html_dashboard_file": "output/20240201_153045/dashboard.html",
    ...
  },
  "summary": {
    "current_step": 22,
    "requires_human_review": false,
    ...
  }
}
```

### Get Thread State
```
GET /threads/{thread_id}/state
```
Get the current state of a thread.

**Response:**
```json
{
  "thread_id": "uuid-string",
  "state": { ... },
  "summary": { ... },
  "current_step": 6,
  "requires_human_review": true
}
```

### Submit Feedback
```
POST /threads/{thread_id}/feedback
```
Submit human feedback for review steps (Steps 6, 11, 14).

**Request:**
```json
{
  "approved": true,
  "feedback": "Looks good, proceed",
  "iteration_count": 1
}
```

**Response:**
```json
{
  "thread_id": "uuid-string",
  "current_step": 6,
  "approved": true,
  "feedback": "Looks good, proceed",
  "message": "Feedback submitted. Use resume to continue workflow."
}
```

### Resume Thread
```
POST /threads/{thread_id}/resume
```
Resume a paused or interrupted thread after human review.

**Response:**
```json
{
  "thread_id": "uuid-string",
  "status": "completed",
  "result": { ... },
  "summary": { ... }
}
```

### Stream Analysis (SSE)
```
POST /threads/{thread_id}/stream
```
Invoke workflow with Server-Sent Events streaming for real-time progress updates.

**Response:** SSE stream with events

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LANGGRAPH_HOST` | `0.0.0.0` | Server host |
| `LANGGRAPH_PORT` | `8123` | Server port |
| `ALLOWED_ORIGINS` | `http://localhost:3000,http://127.0.0.1:3000` | CORS allowed origins |
| `UPLOAD_DIR` | `data` | Directory for uploaded files |
| `MAX_FILE_SIZE` | `100` | Maximum file size in MB |
| `CHECKPOINT_DB_PATH` | `checkpoints.db` | SQLite checkpoint database path |

### CORS Configuration

The server is configured to allow CORS for the Agent Chat UI:

```python
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]
```

To add additional origins, set the `ALLOWED_ORIGINS` environment variable:

```bash
export ALLOWED_ORIGINS="http://localhost:3000,https://example.com"
bash scripts/start_server.sh
```

## File Upload

### Supported File Types

- `.sav` - SPSS data files

### File Size Limits

Default: 100 MB

To change the limit:

```bash
export MAX_FILE_SIZE=200  # 200 MB
bash scripts/start_server.sh
```

### Upload Directory

Uploaded files are saved to the `data/` directory by default.

## Three-Node Pattern Integration

The server supports the three-node pattern for human-in-the-loop review:

### Review Steps

1. **Step 6**: Recoding Rules Review
2. **Step 11**: Indicators Review
3. **Step 14**: Table Specifications Review

### Workflow

1. Invoke analysis with a file
2. Workflow pauses at review step
3. Get thread state to see review prompt
4. Submit feedback (approve/reject)
5. Resume workflow

**Example:**

```bash
# 1. Create thread and upload file
THREAD_ID=$(curl -X POST "http://localhost:8123/threads" | jq -r '.thread_id')
curl -X POST "http://localhost:8123/threads/$THREAD_ID/invoke" \
  -F "file=@survey_data.sav"

# 2. Check state (workflow paused at Step 6)
curl "http://localhost:8123/threads/$THREAD_ID/state"

# 3. Submit feedback
curl -X POST "http://localhost:8123/threads/$THREAD_ID/feedback" \
  -H "Content-Type: application/json" \
  -d '{"approved": true, "feedback": "Approved"}'

# 4. Resume workflow
curl -X POST "http://localhost:8123/threads/$THREAD_ID/resume"
```

## Streaming Support

The server supports Server-Sent Events (SSE) for real-time workflow progress:

```bash
curl -X POST "http://localhost:8123/threads/$THREAD_ID/stream" \
  -F "file=@survey_data.sav"
```

SSE events include:
- State updates at each node
- Custom data from nodes
- Completion status

## API Documentation

Interactive API documentation is available when the server is running:

- **Swagger UI**: http://localhost:8123/docs
- **ReDoc**: http://localhost:8123/redoc

## Architecture

### Server Components

```
agent/server.py
├── FastAPI Application
│   ├── CORS Middleware
│   ├── Global Graph Instance
│   └── Endpoints
├── Pydantic Models
│   ├── ThreadCreate
│   ├── InvokeRequest
│   ├── FeedbackRequest
│   └── Response Models
└── Workflow Integration
    ├── Graph Compilation
    ├── Thread Management
    └── Checkpointing
```

### Graph Integration

The server uses the `get_graph()` function from `agent/graph.py`:

```python
from agent.graph import get_graph, run_analysis, resume_analysis

graph = get_graph(checkpointer_path=CHECKPOINT_DB_PATH)
result = run_analysis(input_file_path, thread_id, checkpointer_path)
```

## Error Handling

The server returns appropriate HTTP status codes:

| Status | Description |
|--------|-------------|
| 200 | Success |
| 400 | Bad request (invalid file, validation error) |
| 404 | Thread not found |
| 500 | Internal server error |

**Error Response:**
```json
{
  "detail": "Error message describing the issue"
}
```

## Security Considerations

### File Upload Validation

- File extension validation (`.sav` only)
- File size limits
- Safe file handling

### CORS

- Configurable allowed origins
- Credentials support

### Checkpoint Security

- Thread ID isolation
- State persistence in SQLite

## Troubleshooting

### Server Won't Start

**Problem**: Port already in use

```bash
# Check what's using the port
lsof -i :8123

# Use a different port
bash scripts/start_server.sh --port 9000
```

### File Upload Fails

**Problem**: File too large

```bash
# Increase max file size
export MAX_FILE_SIZE=200
bash scripts/start_server.sh
```

### CORS Errors

**Problem**: Agent Chat UI can't access server

```bash
# Add your UI origin to allowed origins
export ALLOWED_ORIGINS="http://localhost:3000,http://your-ui-origin"
bash scripts/start_server.sh
```

## Development

### Running with Auto-Reload

The startup script uses `--reload` for development. For production, remove this flag:

```bash
# In scripts/start_server.sh, change:
python3 -m uvicorn agent.server:app --host "$HOST" --port "$PORT" --reload

# To:
python3 -m uvicorn agent.server:app --host "$HOST" --port "$PORT"
```

### Testing Endpoints

```bash
# Test health endpoint
curl http://localhost:8123/health

# Test thread creation
curl -X POST http://localhost:8123/threads

# Test with Python
import requests

# Create thread
response = requests.post("http://localhost:8123/threads")
thread_id = response.json()["thread_id"]

# Upload file
with open("survey_data.sav", "rb") as f:
    response = requests.post(
        f"http://localhost:8123/threads/{thread_id}/invoke",
        files={"file": f}
    )
```

## Production Deployment

### Using Gunicorn

For production, use Gunicorn with Uvicorn workers:

```bash
pip install gunicorn

gunicorn agent.server:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8123 \
  --access-logfile - \
  --error-logfile -
```

### Using Systemd

Create a systemd service file at `/etc/systemd/system/datachat-langgraph.service`:

```ini
[Unit]
Description=DataChat LangGraph Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/datachat
Environment="PATH=/path/to/datachat/.venv/bin"
ExecStart=/path/to/datachat/.venv/bin/gunicorn agent.server:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8123
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable datachat-langgraph
sudo systemctl start datachat-langgraph
sudo systemctl status datachat-langgraph
```

## References

- LangGraph Documentation: https://langchain-ai.github.io/langgraph/
- FastAPI Documentation: https://fastapi.tiangolo.com/
- Task Requirements: Task B-3 - Configure LangGraph Server Endpoint
