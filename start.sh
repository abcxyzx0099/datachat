#!/bin/bash
# =============================================================================
# DataChat Survey Analyzer - Start Script
# =============================================================================
# This script starts both the LangGraph API server and the Agent Chat UI.
#
# Usage:
#   ./start.sh
#
# The script will:
#   1. Kill any existing processes on ports 8123 and 3000
#   2. Start the LangGraph server on port 8123
#   3. Start the Agent Chat UI on port 3000
#
# To stop the application, use: ./stop.sh
# =============================================================================

set -e

# =============================================================================
# Configuration
# =============================================================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
UI_DIR="$PROJECT_ROOT/web/agent-chat-ui"

# Ports
LANGGRAPH_PORT=8123
UI_PORT=3000

# PID files for tracking processes
LANGGRAPH_PID_FILE="$PROJECT_ROOT/.langgraph_pid"
UI_PID_FILE="$PROJECT_ROOT/.ui_pid"

# Log files
LOG_DIR="$PROJECT_ROOT/logs"
LANGGRAPH_LOG="$LOG_DIR/langgraph.log"
UI_LOG="$LOG_DIR/ui.log"

# =============================================================================
# Functions
# =============================================================================

# Function to kill process on a specific port
kill_port() {
    local port=$1
    local name=$2
    local killed=0

    echo -e "${YELLOW}Cleaning port $port ($name)...${NC}"

    # Method 1: Try lsof
    local pid=$(lsof -ti:$port 2>/dev/null || true)
    if [ -n "$pid" ]; then
        echo -e "${YELLOW}  Killing process $pid on port $port...${NC}"
        kill -9 $pid 2>/dev/null || true
        killed=1
    fi

    # Method 2: Try fuser
    local fuser_pids=$(fuser $port/tcp 2>/dev/null || true)
    if [ -n "$fuser_pids" ]; then
        echo -e "${YELLOW}  Killing processes on port $port (fuser)...${NC}"
        fuser -k $port/tcp 2>/dev/null || true
        killed=1
    fi

    # Method 3: For UI (Next.js), kill any next-dev/node processes
    if [ "$port" = "$UI_PORT" ]; then
        local next_pids=$(pgrep -f "next dev" || true)
        if [ -n "$next_pids" ]; then
            echo -e "${YELLOW}  Killing Next.js dev processes...${NC}"
            pkill -f "next dev" 2>/dev/null || true
            killed=1
        fi
    fi

    # Method 4: For LangGraph, kill any agent.server processes
    if [ "$port" = "$LANGGRAPH_PORT" ]; then
        local server_pids=$(pgrep -f "agent.server" || true)
        if [ -n "$server_pids" ]; then
            echo -e "${YELLOW}  Killing LangGraph server processes...${NC}"
            pkill -f "agent.server" 2>/dev/null || true
            killed=1
        fi
    fi

    if [ $killed -eq 1 ]; then
        sleep 1
        echo -e "${GREEN}✓ Port $port is now free${NC}"
    else
        echo -e "${GREEN}✓ Port $port was already free${NC}"
    fi
}

# Function to ensure port is free before starting
ensure_port_free() {
    local port=$1
    local max_attempts=5
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        local pid=$(lsof -ti:$port 2>/dev/null || true)
        if [ -z "$pid" ]; then
            return 0
        fi
        echo -e "${YELLOW}Port $port still in use (attempt $attempt/$max_attempts), killing...${NC}"
        kill -9 $pid 2>/dev/null || true
        sleep 1
        attempt=$((attempt + 1))
    done

    echo -e "${RED}Error: Could not free port $port${NC}"
    return 1
}

# =============================================================================
# Main Script
# =============================================================================

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}  DataChat Survey Analyzer${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Create logs directory
mkdir -p "$LOG_DIR"

# =============================================================================
# Step 1: Kill existing processes
# =============================================================================

echo -e "${YELLOW}Step 1: Cleaning up ports...${NC}"
kill_port $LANGGRAPH_PORT "LangGraph API"
kill_port $UI_PORT "Agent Chat UI"
echo ""

# =============================================================================
# Step 2: Ensure ports are free
# =============================================================================

echo -e "${YELLOW}Step 2: Ensuring ports are free...${NC}"
ensure_port_free $LANGGRAPH_PORT
ensure_port_free $UI_PORT
echo ""

# =============================================================================
# Step 3: Start LangGraph Server
# =============================================================================

echo -e "${YELLOW}Step 3: Starting LangGraph Server (port $LANGGRAPH_PORT)...${NC}"

cd "$PROJECT_ROOT"

# Check for virtual environment
if [ -d ".venv" ]; then
    echo -e "${GREEN}Activating virtual environment...${NC}"
    source ".venv/bin/activate"
elif [ -d "venv" ]; then
    echo -e "${GREEN}Activating virtual environment...${NC}"
    source "venv/bin/activate"
else
    echo -e "${YELLOW}Warning: No virtual environment found, using system Python${NC}"
fi

# Check if agent.server module exists
if ! python3 -c "import agent.server" 2>/dev/null; then
    echo -e "${RED}Error: agent.server module not found${NC}"
    echo -e "${YELLOW}Make sure you're in the project root directory${NC}"
    exit 1
fi

# Start LangGraph server in background
nohup python3 -m agent.server > "$LANGGRAPH_LOG" 2>&1 &
LANGGRAPH_PID=$!
echo $LANGGRAPH_PID > "$LANGGRAPH_PID_FILE"

# Wait for server to start
sleep 3

# Check if server is running
if ps -p $LANGGRAPH_PID > /dev/null; then
    # Check if server is responding
    if curl -s http://localhost:$LANGGRAPH_PORT/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ LangGraph Server started successfully (PID: $LANGGRAPH_PID)${NC}"
    else
        echo -e "${YELLOW}⚠ LangGraph Server started but not responding yet. Check logs: $LANGGRAPH_LOG${NC}"
    fi
else
    echo -e "${RED}✗ LangGraph Server failed to start${NC}"
    echo -e "${YELLOW}Check logs: $LANGGRAPH_LOG${NC}"
    tail -20 "$LANGGRAPH_LOG"
    exit 1
fi
echo ""

# =============================================================================
# Step 4: Start Agent Chat UI
# =============================================================================

echo -e "${YELLOW}Step 4: Starting Agent Chat UI (port $UI_PORT)...${NC}"

cd "$UI_DIR"

# Check if pnpm is available
if command -v pnpm &> /dev/null; then
    PKG_MANAGER="pnpm"
elif command -v npm &> /dev/null; then
    PKG_MANAGER="npm"
else
    echo -e "${RED}Error: Neither pnpm nor npm found${NC}"
    echo -e "${YELLOW}Please install Node.js and pnpm/npm${NC}"
    exit 1
fi

echo -e "${GREEN}Using package manager: $PKG_MANAGER${NC}"

# Check if .env.local exists
if [ ! -f ".env.local" ]; then
    echo -e "${RED}Error: .env.local not found in $UI_DIR${NC}"
    echo -e "${YELLOW}Create it from .env.example: cp .env.example .env.local${NC}"
    exit 1
fi

# Start UI in background
nohup $PKG_MANAGER run dev > "$UI_LOG" 2>&1 &
UI_PID=$!
echo $UI_PID > "$UI_PID_FILE"

# Wait for UI to start
sleep 5

# Check if UI is running
if ps -p $UI_PID > /dev/null; then
    echo -e "${GREEN}✓ Agent Chat UI started successfully (PID: $UI_PID)${NC}"
else
    echo -e "${RED}✗ Agent Chat UI failed to start${NC}"
    echo -e "${YELLOW}Check logs: $UI_LOG${NC}"
    tail -20 "$UI_LOG"
    exit 1
fi
echo ""

# =============================================================================
# Done
# =============================================================================

echo -e "${BLUE}============================================${NC}"
echo -e "${GREEN}✓ DataChat Application Started!${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""
echo -e "${GREEN}LangGraph API:${NC}  http://localhost:$LANGGRAPH_PORT"
echo -e "${GREEN}  - Health:       http://localhost:$LANGGRAPH_PORT/health"
echo -e "${GREEN}  - API Docs:     http://localhost:$LANGGRAPH_PORT/docs"
echo ""
echo -e "${GREEN}Agent Chat UI:${NC}   http://localhost:$UI_PORT"
echo ""
echo -e "${YELLOW}To view logs:${NC}"
echo -e "  LangGraph:  tail -f $LANGGRAPH_LOG"
echo -e "  UI:         tail -f $UI_LOG"
echo ""
echo -e "${YELLOW}To stop the application:${NC}"
echo -e "  ./stop.sh"
echo ""
echo -e "${YELLOW}Or kill by PID:${NC}"
echo -e "  kill $LANGGRAPH_PID  # LangGraph Server"
echo -e "  kill $UI_PID          # Agent Chat UI"
echo ""
