#!/bin/bash
# =============================================================================
# DataChat Survey Analyzer - Stop Script
# =============================================================================
# This script stops the DataChat service.
#
# Usage:
#   ./scripts/stop.sh
#
# =============================================================================

SERVICE_NAME="datachat"

echo "============================================================================"
echo "Stopping DataChat Survey Analyzer"
echo "============================================================================"

# Check if systemd service is installed
if systemctl list-unit-files | grep -q "^${SERVICE_NAME}.service"; then
    # Service is installed
    if systemctl is-active --quiet $SERVICE_NAME; then
        echo "Stopping systemd service: $SERVICE_NAME"
        sudo systemctl stop $SERVICE_NAME

        # Wait for service to stop
        for i in {1..10}; do
            if ! systemctl is-active --quiet $SERVICE_NAME; then
                echo "✓ Service stopped successfully"
                exit 0
            fi
            sleep 1
        done

        echo "✓ Service stop command sent"
        echo ""
        echo "Check status with: sudo systemctl status $SERVICE_NAME"
    else
        echo "Service is not currently running."
    fi
else
    # Service not installed, try to find running process
    echo "Systemd service not found. Checking for running processes..."

    # Find LangGraph processes
    LANGGRAPH_PIDS=$(pgrep -f "langgraph dev" || true)

    if [ -n "$LANGGRAPH_PIDS" ]; then
        echo "Found running LangGraph process(es):"
        echo "$LANGGRAPH_PIDS"
        echo ""
        read -p "Do you want to kill these processes? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo $LANGGRAPH_PIDS | xargs kill
            echo "✓ Processes terminated"
        else
            echo "No action taken."
        fi
    else
        echo "No DataChat processes found running."
    fi
fi

echo ""
echo "============================================================================"
