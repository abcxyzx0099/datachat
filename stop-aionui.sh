#!/bin/bash
# =============================================================================
# DataChat AionUI Stop Script
# =============================================================================
# Stops LangGraph API server and AionUi WebUI.
#
# Usage:
#   ./stop-aionui.sh          # Stop both LangGraph API and AionUi
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
LANGGRAPH_PORT=8123
AIONUI_PORT=25808
PID_FILE="/tmp/datachat-aionui-pids"

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}  Stopping DataChat AionUI${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Function to kill process on port
kill_port() {
    local port=$1
    local name=$2
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${YELLOW}Killing $name on port $port...${NC}"
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
        sleep 1
    else
        echo -e "${GREEN}✓ No process on port $port${NC}"
    fi
}

# Kill by PID file if exists
if [ -f "$PID_FILE" ]; then
    echo -e "${YELLOW}Stopping services from PID file...${NC}"
    while read pid; do
        if kill -0 $pid 2>/dev/null; then
            echo -e "  Killing PID $pid..."
            kill $pid 2>/dev/null || true
        fi
    done < "$PID_FILE"
    rm -f "$PID_FILE"
    echo -e "${GREEN}✓ PID file cleaned${NC}"
    echo ""
fi

# Kill LangGraph API processes
echo -e "${YELLOW}Stopping LangGraph API...${NC}"
kill_port $LANGGRAPH_PORT "LangGraph API"
pkill -f "agent.server" 2>/dev/null || true
echo ""

# Kill AionUi processes
echo -e "${YELLOW}Stopping AionUi WebUI...${NC}"
kill_port $AIONUI_PORT "AionUi WebUI"
pkill -f "aionui" 2>/dev/null || true
pkill -f "electron-forge.*webui" 2>/dev/null || true
echo ""

echo -e "${BLUE}============================================${NC}"
echo -e "${GREEN}✓ DataChat AionUI Stopped${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""
