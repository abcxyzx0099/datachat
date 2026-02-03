#!/bin/bash
# =============================================================================
# DataChat Survey Analyzer - Start Script
# =============================================================================
# This script starts the LangGraph servers and/or Agent Chat UI.
#
# Usage:
#   ./dev-start.sh          # Start all servers (2024 + 8123 + 3000) [DEFAULT]
#   ./dev-start.sh --studio # Start LangGraph Studio only (2024)
#   ./dev-start.sh --web    # Start web app only (8123 + 3000)
#   ./dev-start.sh --all     # Start all servers (2024 + 8123 + 3000)
#
# To stop the application, use: ./dev-stop.sh
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
STUDIO_PORT=2024
LANGGRAPH_PORT=8123
UI_PORT=3000

# PID files for tracking processes
STUDIO_PID_FILE="$PROJECT_ROOT/.studio_pid"
LANGGRAPH_PID_FILE="$PROJECT_ROOT/.langgraph_pid"
UI_PID_FILE="$PROJECT_ROOT/.ui_pid"

# Parse arguments
START_WEB=false
START_STUDIO=false

case "${1:-}" in
    --studio)
        START_STUDIO=true
        ;;
    --web)
        START_WEB=true
        ;;
    --all|"")
        START_WEB=true
        START_STUDIO=true
        ;;
    *)
        echo -e "${RED}Error: Unknown option '$1'${NC}"
        echo "Usage: $0 [--studio|--web|--all]"
        exit 1
        ;;
esac

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

    # Method 5: For Studio, kill langgraph dev processes
    if [ "$port" = "$STUDIO_PORT" ]; then
        local studio_pids=$(pgrep -f "langgraph dev" || true)
        if [ -n "$studio_pids" ]; then
            echo -e "${YELLOW}  Killing LangGraph Studio processes...${NC}"
            pkill -f "langgraph dev" 2>/dev/null || true
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

# Load environment variables from .env file
if [ -f "$PROJECT_ROOT/.env" ]; then
    echo -e "${GREEN}Loading environment variables from .env...${NC}"
    while IFS='=' read -r key value; do
        # Skip comments and empty lines
        [[ "$key" =~ ^#.*$ ]] && continue
        [[ -z "$key" ]] && continue
        # Remove leading/trailing whitespace and quotes
        key=$(echo "$key" | xargs)
        value=$(echo "$value" | xargs | sed 's/^["\x27]|["\x27]$//g')
        export "$key=$value"
    done < "$PROJECT_ROOT/.env"
    echo -e "${GREEN}✓ Environment loaded${NC}"
    echo ""
fi

# Build mode message
if [ "$START_WEB" = true ] && [ "$START_STUDIO" = true ]; then
    MODE_MSG="All servers (Studio + Web App)"
elif [ "$START_STUDIO" = true ]; then
    MODE_MSG="LangGraph Studio only"
else
    MODE_MSG="Web App only"
fi

echo -e "${GREEN}Starting mode: $MODE_MSG${NC}"
echo ""

# =============================================================================
# Step 1: Kill existing processes
# =============================================================================

echo -e "${YELLOW}Step 1: Cleaning up ports...${NC}"
if [ "$START_STUDIO" = true ]; then
    kill_port $STUDIO_PORT "LangGraph Studio"
fi
if [ "$START_WEB" = true ]; then
    kill_port $LANGGRAPH_PORT "LangGraph API"
    kill_port $UI_PORT "Agent Chat UI"
fi
echo ""

# =============================================================================
# Step 2: Ensure ports are free
# =============================================================================

echo -e "${YELLOW}Step 2: Ensuring ports are free...${NC}"
if [ "$START_STUDIO" = true ]; then
    ensure_port_free $STUDIO_PORT
fi
if [ "$START_WEB" = true ]; then
    ensure_port_free $LANGGRAPH_PORT
    ensure_port_free $UI_PORT
fi
echo ""

# Activate virtual environment once
cd "$PROJECT_ROOT"
PYTHON_CMD="python3"
if [ -d ".venv" ]; then
    echo -e "${GREEN}Activating virtual environment...${NC}"
    source ".venv/bin/activate"
    PYTHON_CMD=".venv/bin/python"
elif [ -d "venv" ]; then
    echo -e "${GREEN}Activating virtual environment...${NC}"
    source "venv/bin/activate"
    PYTHON_CMD="venv/bin/python"
else
    echo -e "${YELLOW}Warning: No virtual environment found, using system Python${NC}"
fi
echo ""

# =============================================================================
# Step 3: Start LangGraph Studio (if requested)
# =============================================================================

if [ "$START_STUDIO" = true ]; then
    echo -e "${YELLOW}Step 3: Starting LangGraph Studio (port $STUDIO_PORT)...${NC}"

    # Check if langgraph CLI is available
    if ! command -v langgraph &> /dev/null; then
        echo -e "${RED}Error: langgraph CLI not found${NC}"
        echo -e "${YELLOW}Install with: pip install 'langgraph-cli[inmem]'${NC}"
        exit 1
    fi

    # Start Studio in background with --allow-blocking flag
    nohup langgraph dev --allow-blocking > /dev/null 2>&1 &
    STUDIO_PID=$!
    echo $STUDIO_PID > "$STUDIO_PID_FILE"

    # Wait for Studio to start
    sleep 5

    # Check if Studio is running
    if ps -p $STUDIO_PID > /dev/null; then
        if curl -s http://127.0.0.1:$STUDIO_PORT/ok > /dev/null 2>&1; then
            echo -e "${GREEN}✓ LangGraph Studio started successfully (PID: $STUDIO_PID)${NC}"
        else
            echo -e "${YELLOW}⚠ LangGraph Studio started but not responding yet${NC}"
        fi
    else
        echo -e "${RED}✗ LangGraph Studio failed to start${NC}"
        exit 1
    fi
    echo ""
fi

# =============================================================================
# Step 4: Start Custom LangGraph Server (if requested)
# =============================================================================

if [ "$START_WEB" = true ]; then
    echo -e "${YELLOW}Step 4: Starting LangGraph Server (port $LANGGRAPH_PORT)...${NC}"

    # Check if agent.server module exists
    if ! $PYTHON_CMD -c "import agent.server" 2>/dev/null; then
        echo -e "${RED}Error: agent.server module not found${NC}"
        echo -e "${YELLOW}Make sure you're in the project root directory${NC}"
        exit 1
    fi

    # Start LangGraph server in background
    nohup $PYTHON_CMD -m agent.server > /dev/null 2>&1 &
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
            echo -e "${YELLOW}⚠ LangGraph Server started but not responding yet${NC}"
        fi
    else
        echo -e "${RED}✗ LangGraph Server failed to start${NC}"
        exit 1
    fi
    echo ""
fi

# =============================================================================
# Step 5: Start Agent Chat UI (if requested)
# =============================================================================

if [ "$START_WEB" = true ]; then
    echo -e "${YELLOW}Step 5: Starting Agent Chat UI (port $UI_PORT)...${NC}"

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
    nohup $PKG_MANAGER run dev > /dev/null 2>&1 &
    UI_PID=$!
    echo $UI_PID > "$UI_PID_FILE"

    # Wait for UI to start
    sleep 5

    # Check if UI is running
    if ps -p $UI_PID > /dev/null; then
        echo -e "${GREEN}✓ Agent Chat UI started successfully (PID: $UI_PID)${NC}"
    else
        echo -e "${RED}✗ Agent Chat UI failed to start${NC}"
        exit 1
    fi
    echo ""
fi

# =============================================================================
# Done
# =============================================================================

echo -e "${BLUE}============================================${NC}"
echo -e "${GREEN}✓ DataChat Application Started!${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Print URLs based on what was started
if [ "$START_STUDIO" = true ]; then
    echo -e "${GREEN}LangGraph Studio:${NC} http://127.0.0.1:$STUDIO_PORT"
    echo -e "${GREEN}  - Studio UI:    https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:$STUDIO_PORT${NC}"
    echo -e "${GREEN}  - API Docs:     http://127.0.0.1:$STUDIO_PORT/docs${NC}"
    echo ""
fi

if [ "$START_WEB" = true ]; then
    echo -e "${GREEN}LangGraph API:${NC}    http://localhost:$LANGGRAPH_PORT"
    echo -e "${GREEN}  - Health:       http://localhost:$LANGGRAPH_PORT/health${NC}"
    echo -e "${GREEN}  - API Docs:     http://localhost:$LANGGRAPH_PORT/docs${NC}"
    echo ""
    echo -e "${GREEN}Agent Chat UI:${NC}     http://localhost:$UI_PORT"
    echo ""
fi

echo -e "${YELLOW}To stop the application:${NC}"
echo -e "  ./dev-stop.sh"
echo ""

echo -e "${YELLOW}Or kill by PID:${NC}"
if [ "$START_STUDIO" = true ]; then
    echo -e "  kill $STUDIO_PID     # LangGraph Studio"
fi
if [ "$START_WEB" = true ]; then
    echo -e "  kill $LANGGRAPH_PID  # LangGraph Server"
    echo -e "  kill $UI_PID          # Agent Chat UI"
fi
echo ""
