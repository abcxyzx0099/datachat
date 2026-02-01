#!/bin/bash
# =============================================================================
# DataChat Survey Analyzer - Start Script
# =============================================================================
# This script starts the LangGraph development server for DataChat.
#
# Usage:
#   ./scripts/start.sh
#
# For production, use the systemd service instead:
#   sudo systemctl start datachat
#
# =============================================================================

INSTALL_DIR="/opt/survey-analyzer"

# Change to installation directory
cd $INSTALL_DIR 2>/dev/null || {
    echo "Error: Installation directory not found: $INSTALL_DIR"
    echo "Please run ./scripts/install.sh first."
    exit 1
}

# =============================================================================
# Verify Prerequisites
# =============================================================================

# Check if virtual environment exists
if [ ! -d venv ]; then
    echo "Error: Virtual environment not found."
    echo "Please run ./scripts/install.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env exists
if [ ! -f .env ]; then
    echo "Error: .env file not found."
    echo "Please run ./scripts/configure.sh first."
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Verify API key is set
if [ -z "$ZHIPU_API_KEY" ] && [ "$LLM_PROVIDER" == "ZHIPU" ]; then
    echo "Error: ZHIPU_API_KEY is not set in .env file."
    echo "Please edit $INSTALL_DIR/.env and add your API key."
    exit 1
fi

if [ -z "$DEEPSEEK_API_KEY" ] && [ "$LLM_PROVIDER" == "DEEPSEEK" ]; then
    echo "Error: DEEPSEEK_API_KEY is not set in .env file."
    echo "Please edit $INSTALL_DIR/.env and add your API key."
    exit 1
fi

if [ -z "$KIMI_API_KEY" ] && [ "$LLM_PROVIDER" == "KIMI" ]; then
    echo "Error: KIMI_API_KEY is not set in .env file."
    echo "Please edit $INSTALL_DIR/.env and add your API key."
    exit 1
fi

# Check PSPP
if ! command -v pspp &> /dev/null; then
    echo "Warning: PSPP not found in PATH. Statistical analysis may fail."
    echo "Install PSPP with: sudo apt-get install pspp"
fi

# =============================================================================
# Start LangGraph Server
# =============================================================================

echo "============================================================================"
echo "Starting DataChat Survey Analyzer"
echo "============================================================================"
echo ""
echo "Configuration:"
echo "  LLM Provider: ${LLM_PROVIDER:-ZHIPU}"
echo "  PSPP Path: ${PSPP_PATH:-/usr/bin/pspp}"
echo "  Output Dir: ${OUTPUT_DIR:-output}"
echo "  Log Level: ${LOG_LEVEL:-INFO}"
echo ""
echo "Server will start on:"
echo "  http://localhost:8123"
echo "  http://0.0.0.0:8123"
echo ""
echo "Press Ctrl+C to stop the server."
echo ""
echo "============================================================================"
echo ""

# Start the server (exec replaces the shell)
exec langgraph dev --port 8123 --host 0.0.0.0
