#!/bin/bash
# =============================================================================
# DataChat LangGraph Server Startup Script
# =============================================================================
#
# This script starts the FastAPI server that exposes the LangGraph survey
# analysis workflow as REST API endpoints for the Agent Chat UI.
#
# Usage:
#   ./scripts/start_server.sh [--port PORT] [--host HOST]
#
# Examples:
#   ./scripts/start_server.sh              # Default: host=0.0.0.0, port=8123
#   ./scripts/start_server.sh --port 9000  # Custom port
#   ./scripts/start_server.sh --host 127.0.0.1 --port 8080
#
# =============================================================================

set -e  # Exit on error

# =============================================================================
# Configuration
# =============================================================================

# Default values
DEFAULT_HOST="0.0.0.0"
DEFAULT_PORT="8123"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Parse command line arguments
HOST="$DEFAULT_HOST"
PORT="$DEFAULT_PORT"

while [[ $# -gt 0 ]]; do
    case $1 in
        --host)
            HOST="$2"
            shift 2
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [--host HOST] [--port PORT]"
            echo ""
            echo "Start the DataChat LangGraph server."
            echo ""
            echo "Options:"
            echo "  --host HOST    Server host (default: 0.0.0.0)"
            echo "  --port PORT    Server port (default: 8123)"
            echo "  -h, --help     Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

# =============================================================================
# Environment Setup
# =============================================================================

export LANGGRAPH_HOST="$HOST"
export LANGGRAPH_PORT="$PORT"

# Set CORS origins (default: localhost:3000 for Agent Chat UI)
export ALLOWED_ORIGINS="${ALLOWED_ORIGINS:-http://localhost:3000,http://127.0.0.1:3000}"

# Set upload directory
export UPLOAD_DIR="${UPLOAD_DIR:-data}"

# Set checkpoint database path
export CHECKPOINT_DB_PATH="${CHECKPOINT_DB_PATH:-checkpoints.db}"

# =============================================================================
# Virtual Environment Activation
# =============================================================================

# Check for virtual environment
if [ -d "$PROJECT_ROOT/.venv" ]; then
    echo "Activating virtual environment at .venv..."
    source "$PROJECT_ROOT/.venv/bin/activate"
elif [ -d "$PROJECT_ROOT/venv" ]; then
    echo "Activating virtual environment at venv..."
    source "$PROJECT_ROOT/venv/bin/activate"
else
    echo "Warning: No virtual environment found"
    echo "Attempting to use system Python..."
fi

# =============================================================================
# Dependencies Check
# =============================================================================

# Check if required Python packages are installed
echo "Checking dependencies..."

if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "Error: fastapi is not installed"
    echo "Install with: pip install fastapi uvicorn"
    exit 1
fi

if ! python3 -c "import uvicorn" 2>/dev/null; then
    echo "Error: uvicorn is not installed"
    echo "Install with: pip install uvicorn"
    exit 1
fi

if ! python3 -c "import langgraph" 2>/dev/null; then
    echo "Error: langgraph is not installed"
    echo "Install with: pip install langgraph"
    exit 1
fi

echo "Dependencies check passed"

# =============================================================================
# Create Required Directories
# =============================================================================

echo "Creating required directories..."

# Create upload directory if it doesn't exist
if [ ! -d "$UPLOAD_DIR" ]; then
    mkdir -p "$UPLOAD_DIR"
    echo "Created upload directory: $UPLOAD_DIR"
fi

# Create output directory if it doesn't exist
if [ ! -d "output" ]; then
    mkdir -p "output"
    echo "Created output directory: output"
fi

# =============================================================================
# Start Server
# =============================================================================

echo ""
echo "============================================================================"
echo "Starting DataChat LangGraph Server"
echo "============================================================================"
echo "Host: $HOST"
echo "Port: $PORT"
echo "Graph ID: survey_analysis"
echo "CORS Origins: $ALLOWED_ORIGINS"
echo "Upload Directory: $UPLOAD_DIR"
echo "Checkpoint Database: $CHECKPOINT_DB_PATH"
echo "============================================================================"
echo ""
echo "API Documentation:"
echo "  - Swagger UI:  http://$HOST:$PORT/docs"
echo "  - ReDoc:       http://$HOST:$PORT/redoc"
echo ""
echo "API Endpoints:"
echo "  - POST /                    Root endpoint"
echo "  - GET  /health              Health check"
echo "  - POST /threads             Create new thread"
echo "  - POST /threads/{id}/invoke Upload file and invoke analysis"
echo "  - GET  /threads/{id}/state  Get thread state"
echo "  - POST /threads/{id}/feedback Submit review feedback"
echo "  - POST /threads/{id}/resume Resume paused workflow"
echo "  - POST /threads/{id}/stream Stream analysis (SSE)"
echo ""
echo "Press Ctrl+C to stop the server"
echo "============================================================================"
echo ""

# Change to project root directory
cd "$PROJECT_ROOT"

# Start the server
# Using uvicorn directly with auto-reload disabled for production
python3 -m uvicorn agent.server:app \
    --host "$HOST" \
    --port "$PORT" \
    --reload \
    --log-level info

# Note: --reload is enabled for development. For production, remove --reload
# and consider using:
#   --workers 4 \
#   --worker-class uvicorn.workers.UvicornWorker
