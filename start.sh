#!/bin/bash
# DataChat - Agno Agent + CopilotKit Start Script
# This script starts the DataChat agent server on port 8000

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENT_DIR="$SCRIPT_DIR/agent"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

# PID files for tracking processes
AGENT_PID_FILE="$SCRIPT_DIR/.agent_pid"
FRONTEND_PID_FILE="$SCRIPT_DIR/.frontend_pid"

# Log files
LOG_DIR="$SCRIPT_DIR/logs"
AGENT_LOG="$LOG_DIR/agent.log"
FRONTEND_LOG="$LOG_DIR/frontend.log"

# Ports
AGENT_PORT=8000
FRONTEND_PORT=3000

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  DataChat - Agent + Frontend${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Create logs directory
mkdir -p "$LOG_DIR"

# Function to kill process on a specific port
kill_port() {
    local port=$1
    local name=$2
    local killed=0

    # Method 1: Try lsof
    local pid=$(lsof -ti:$port 2>/dev/null || true)
    if [ -n "$pid" ]; then
        echo -e "${YELLOW}Killing $name (PID: $pid) on port $port (lsof)...${NC}"
        kill -9 $pid 2>/dev/null || true
        killed=1
    fi

    # Method 2: Try fuser
    local fuser_pids=$(fuser $port/tcp 2>/dev/null || true)
    if [ -n "$fuser_pids" ]; then
        echo -e "${YELLOW}Killing $name on port $port (fuser)...${NC}"
        fuser -k $port/tcp 2>/dev/null || true
        killed=1
    fi

    # Method 3: For port 3000, also kill any next-dev processes
    if [ "$port" = "3000" ]; then
        local next_pids=$(pgrep -f "next-dev" || true)
        if [ -n "$next_pids" ]; then
            echo -e "${YELLOW}Killing stray 'next-dev' processes...${NC}"
            pkill -f "next-dev" 2>/dev/null || true
            killed=1
        fi
    fi

    # Method 4: For agent processes
    if [ "$port" = "$AGENT_PORT" ]; then
        local agent_pids=$(pgrep -f "agent.py" || true)
        if [ -n "$agent_pids" ]; then
            echo -e "${YELLOW}Killing stray 'agent.py' processes...${NC}"
            pkill -f "agent.py" 2>/dev/null || true
            killed=1
        fi
    fi

    if [ $killed -eq 1 ]; then
        sleep 1
        # Double check the port is free
        local check_pid=$(lsof -ti:$port 2>/dev/null || true)
        if [ -n "$check_pid" ]; then
            echo -e "${RED}Warning: Port $port still in use, forcing kill...${NC}"
            kill -9 $check_pid 2>/dev/null || true
            sleep 1
        fi
        echo -e "${GREEN}✓ Killed $name on port $port${NC}"
    else
        echo -e "${GREEN}✓ No process found on port $port${NC}"
    fi
}

# Function to ensure port is free
ensure_port_free() {
    local port=$1
    local name=$2

    # Keep checking and killing until port is free
    while true; do
        local pid=$(lsof -ti:$port 2>/dev/null || true)
        if [ -z "$pid" ]; then
            break
        fi
        echo -e "${YELLOW}Port $port is in use (PID: $pid), killing...${NC}"
        kill -9 $pid 2>/dev/null || true
        sleep 1
    done
    echo -e "${GREEN}✓ Port $port is free${NC}"
}

# Kill existing processes
echo -e "${YELLOW}Step 1: Cleaning up ports...${NC}"
kill_port $AGENT_PORT "Agent"
kill_port $FRONTEND_PORT "Frontend"
echo ""

# Ensure ports are actually free
echo -e "${YELLOW}Step 2: Ensuring ports are free...${NC}"
ensure_port_free $AGENT_PORT "Agent"
ensure_port_free $FRONTEND_PORT "Frontend"
echo ""

# Function to install Python dependencies
install_agent_deps() {
    echo -e "${YELLOW}Checking agent dependencies...${NC}"

    cd "$AGENT_DIR"

    # Use system Python directly
    if ! python3 -c "import agno" 2>/dev/null; then
        echo -e "${YELLOW}Installing agent dependencies...${NC}"
        pip install --break-system-packages -q -r "$AGENT_DIR/requirements.txt" 2>/dev/null || pip3 install --user -q -r "$AGENT_DIR/requirements.txt"
        echo -e "${GREEN}✓ Agent dependencies installed${NC}"
    else
        echo -e "${GREEN}✓ Agent dependencies already installed${NC}"
    fi
}

# Function to install Node dependencies
install_frontend_deps() {
    echo -e "${YELLOW}Checking frontend dependencies...${NC}"
    cd "$FRONTEND_DIR"

    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}Installing frontend dependencies...${NC}"
        npm install --silent
        echo -e "${GREEN}✓ Frontend dependencies installed${NC}"
    else
        echo -e "${GREEN}✓ Frontend dependencies already installed${NC}"
    fi
}

# Start agent
echo -e "${YELLOW}Step 3: Starting Agent (port $AGENT_PORT)...${NC}"
install_agent_deps

cd "$AGENT_DIR"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${RED}Error: .env file not found in agent directory!${NC}"
    echo -e "${YELLOW}Please create .env from .env.example${NC}"
    exit 1
fi

# Load environment variables from .env
set -a
source .env
set +a

# Start agent in background
PORT=$AGENT_PORT nohup python3 agent.py > "$AGENT_LOG" 2>&1 &
AGENT_PID=$!
echo $AGENT_PID > "$AGENT_PID_FILE"

# Wait a moment for agent to start
sleep 3

# Check if agent is running
if ps -p $AGENT_PID > /dev/null; then
    echo -e "${GREEN}✓ Agent started successfully (PID: $AGENT_PID)${NC}"
else
    echo -e "${RED}✗ Agent failed to start. Check logs: $AGENT_LOG${NC}"
    cat "$AGENT_LOG" | tail -20
    exit 1
fi
echo ""

# Start frontend
echo -e "${YELLOW}Step 4: Starting Frontend (port $FRONTEND_PORT)...${NC}"
install_frontend_deps

cd "$FRONTEND_DIR"

# Check if .env.local exists
if [ ! -f ".env.local" ]; then
    echo -e "${RED}Error: .env.local file not found in frontend directory!${NC}"
    echo -e "${YELLOW}Please create .env.local from .env.example${NC}"
    exit 1
fi

# Start frontend in background
nohup npm run dev > "$FRONTEND_LOG" 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > "$FRONTEND_PID_FILE"

# Wait a moment for frontend to start
sleep 3

# Check if frontend is running
if ps -p $FRONTEND_PID > /dev/null; then
    echo -e "${GREEN}✓ Frontend started successfully (PID: $FRONTEND_PID)${NC}"
else
    echo -e "${RED}✗ Frontend failed to start. Check logs: $FRONTEND_LOG${NC}"
    cat "$FRONTEND_LOG" | tail -20
    exit 1
fi
echo ""

# Done
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✓ DataChat Application Started!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${GREEN}Frontend:${NC}  http://localhost:$FRONTEND_PORT"
echo -e "${GREEN}Agent (AGUI):${NC} http://localhost:$AGENT_PORT"
echo -e "${GREEN}API Docs:${NC}    http://localhost:$AGENT_PORT/docs"
echo ""
echo -e "${YELLOW}To view logs:${NC}"
echo -e "  Agent:    tail -f $AGENT_LOG"
echo -e "  Frontend: tail -f $FRONTEND_LOG"
echo ""
echo -e "${YELLOW}To stop the application:${NC}"
echo -e "  ./stop.sh"
echo ""
