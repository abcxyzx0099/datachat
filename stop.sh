#!/bin/bash
# =============================================================================
# DataChat Survey Analyzer - Stop Script
# =============================================================================
# This script stops both the LangGraph API server and the Agent Chat UI.
#
# Usage:
#   ./stop.sh
#
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

# PID files
LANGGRAPH_PID_FILE="$PROJECT_ROOT/.langgraph_pid"
UI_PID_FILE="$PROJECT_ROOT/.ui_pid"

# =============================================================================
# Functions
# =============================================================================

# Function to stop a process by PID file
stop_process() {
    local pid_file=$1
    local name=$2

    if [ ! -f "$pid_file" ]; then
        echo -e "${YELLOW}No PID file found for $name${NC}"
        return 1
    fi

    local pid=$(cat "$pid_file")

    if [ -z "$pid" ]; then
        echo -e "${YELLOW}Empty PID in $pid_file${NC}"
        rm -f "$pid_file"
        return 1
    fi

    # Check if process is still running
    if ps -p $pid > /dev/null 2>&1; then
        echo -e "${YELLOW}Stopping $name (PID: $pid)...${NC}"
        kill $pid 2>/dev/null || true

        # Wait for process to stop gracefully
        local count=0
        while [ $count -lt 5 ]; do
            if ! ps -p $pid > /dev/null 2>&1; then
                echo -e "${GREEN}✓ $name stopped${NC}"
                rm -f "$pid_file"
                return 0
            fi
            sleep 1
            count=$((count + 1))
        done

        # Force kill if still running
        if ps -p $pid > /dev/null 2>&1; then
            echo -e "${YELLOW}Force killing $name...${NC}"
            kill -9 $pid 2>/dev/null || true
            echo -e "${GREEN}✓ $name force stopped${NC}"
        fi

        rm -f "$pid_file"
    else
        echo -e "${GREEN}✓ $name was not running${NC}"
        rm -f "$pid_file"
    fi

    return 0
}

# =============================================================================
# Main Script
# =============================================================================

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}  Stopping DataChat Application${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Stop LangGraph Server
echo -e "${YELLOW}Stopping LangGraph Server...${NC}"
stop_process "$LANGGRAPH_PID_FILE" "LangGraph Server"
echo ""

# Stop Agent Chat UI
echo -e "${YELLOW}Stopping Agent Chat UI...${NC}"
stop_process "$UI_PID_FILE" "Agent Chat UI"
echo ""

# Also kill any stray processes on ports
echo -e "${YELLOW}Cleaning up ports...${NC}"

# Kill any remaining processes on port 8123
local langgraph_pids=$(lsof -ti:8123 2>/dev/null || true)
if [ -n "$langgraph_pids" ]; then
    echo -e "${YELLOW}Killing stray processes on port 8123...${NC}"
    kill -9 $langgraph_pids 2>/dev/null || true
fi

# Kill any remaining processes on port 3000
local ui_pids=$(lsof -ti:3000 2>/dev/null || true)
if [ -n "$ui_pids" ]; then
    echo -e "${YELLOW}Killing stray processes on port 3000...${NC}"
    kill -9 $ui_pids 2>/dev/null || true
fi

# Kill any next-dev processes
local next_pids=$(pgrep -f "next dev" || true)
if [ -n "$next_pids" ]; then
    echo -e "${YELLOW}Killing stray Next.js processes...${NC}"
    pkill -f "next dev" 2>/dev/null || true
fi

# Kill any agent.server processes
local server_pids=$(pgrep -f "agent.server" || true)
if [ -n "$server_pids" ]; then
    echo -e "${YELLOW}Killing stray LangGraph server processes...${NC}"
    pkill -f "agent.server" 2>/dev/null || true
fi

echo -e "${GREEN}✓ Ports cleaned${NC}"
echo ""

echo -e "${BLUE}============================================${NC}"
echo -e "${GREEN}✓ DataChat Application Stopped${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""
