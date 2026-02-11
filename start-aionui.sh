#!/bin/bash
# =============================================================================
# DataChat AionUI Startup Script (Production Mode)
# =============================================================================
# Starts LangGraph API server and AionUi WebUI for hybrid integration.
# This script uses the PRODUCTION build of AionUi (no compilation needed).
#
# Usage:
#   ./start-aionui.sh         # Start LangGraph API (8123) + AionUi (25808)
#
# To stop services, use: ./stop-aionui.sh
#
# PREREQUISITE: AionUi must be built and installed first:
#   cd /home/admin/workspaces/AionUi
#   npm run build-deb
#   sudo dpkg -i out/AionUi-*-linux-*.deb
#
# For development mode (with npm), use: ./start-aionui.sh.backup
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration (relative paths)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATACHAT_DIR="$SCRIPT_DIR"
AIONUI_PROD_BINARY="/opt/AionUi/AionUi"
LANGGRAPH_PORT=8123
AIONUI_PORT=25808

echo -e "${GREEN}======================================"
echo "DataChat AionUI Startup (Production)"
echo "  Using pre-built binary - fast startup!"
echo -e "======================================${NC}"
echo ""

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to kill process on port
kill_port() {
    local port=$1
    if check_port $port; then
        echo -e "${YELLOW}Killing process on port $port...${NC}"
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
        sleep 1
    fi
}

# Kill existing processes if they exist
echo -e "${YELLOW}Checking for existing services...${NC}"
kill_port $LANGGRAPH_PORT
kill_port $AIONUI_PORT

# Start LangGraph API
echo -e "${YELLOW}Step 1: Starting LangGraph API (port $LANGGRAPH_PORT)...${NC}"
cd "$DATACHAT_DIR"

# Activate virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
else
    echo -e "${RED}Error: No virtual environment found${NC}"
    exit 1
fi

# Start LangGraph server
nohup python -m agent.server > /tmp/langgraph.log 2>&1 &
LANGGRAPH_PID=$!
echo "  LangGraph PID: $LANGGRAPH_PID"
echo "  Logs: tail -f /tmp/langgraph.log"

# Wait for LangGraph to be ready
echo -n "  Waiting for API to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:$LANGGRAPH_PORT/health >/dev/null 2>&1; then
        echo -e " ${GREEN}OK${NC}"
        break
    fi
    echo -n "."
    sleep 1
done
echo ""

# Start AionUi WebUI (Production Mode)
echo -e "${YELLOW}Step 2: Starting AionUi WebUI - PRODUCTION MODE (port $AIONUI_PORT)...${NC}"

# Check if production binary exists
if [ ! -f "$AIONUI_PROD_BINARY" ]; then
    echo -e "${RED}Error: AionUi production binary not found at $AIONUI_PROD_BINARY${NC}"
    echo ""
    echo -e "${YELLOW}To build and install AionUi production version:${NC}"
    echo -e "  cd /home/admin/workspaces/AionUi"
    echo -e "  npm run build-deb"
    echo -e "  sudo dpkg -i out/AionUi-*-linux-*.deb"
    echo ""
    echo -e "${YELLOW}Or use development mode instead:${NC}"
    echo -e "  ./start-aionui.sh"
    exit 1
fi

echo -e "${GREEN}Using production binary: $AIONUI_PROD_BINARY${NC}"

# Start AionUi in WebUI remote mode (NO COMPILATION - fast startup!)
nohup "$AIONUI_PROD_BINARY" --webui --remote > /tmp/aionui.log 2>&1 &
AIONUI_PID=$!
echo "  AionUi PID: $AIONUI_PID"
echo "  Logs: tail -f /tmp/aionui.log"

# Wait for AionUi to be ready (shorter timeout - no compilation needed)
echo -n "  Waiting for WebUI to be ready..."
for i in {1..15}; do
    if curl -s http://localhost:$AIONUI_PORT >/dev/null 2>&1; then
        echo -e " ${GREEN}OK${NC}"
        break
    fi
    echo -n "."
    sleep 1
done
echo ""

# Save PIDs for cleanup
echo $LANGGRAPH_PID > /tmp/datachat-aionui-pids
echo $AIONUI_PID >> /tmp/datachat-aionui-pids

echo -e "${BLUE}============================================${NC}"
echo -e "${GREEN}✓ DataChat AionUI Started Successfully!${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""
echo -e "${GREEN}LangGraph API:${NC}  http://localhost:$LANGGRAPH_PORT"
echo -e "${GREEN}  - Health:       http://localhost:$LANGGRAPH_PORT/health${NC}"
echo -e "${GREEN}  - API Docs:     http://localhost:$LANGGRAPH_PORT/docs${NC}"
echo ""
echo -e "${GREEN}AionUi WebUI:${NC}   http://localhost:$AIONUI_PORT"
echo ""
echo -e "${YELLOW}To stop services:${NC}"
echo "  ./stop-aionui.sh"
echo ""
