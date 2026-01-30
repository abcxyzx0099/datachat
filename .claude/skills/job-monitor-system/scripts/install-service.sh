#!/bin/bash

# Task Monitor System Installation Script
# Location: /opt/task-monitor/

set -e

# Set paths
MONITOR_SYSTEM_ROOT="/opt/task-monitor"
CONFIG_DIR="/home/admin/.config/task-monitor"
VENV_DIR="$MONITOR_SYSTEM_ROOT/.venv"

echo "Task Monitor Installation Script"
echo "================================"
echo ""

# Create dedicated virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating dedicated virtual environment at $VENV_DIR..."
    sudo python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment and install dependencies
echo "Installing dependencies..."
sudo "$VENV_DIR/bin/pip" install claude-agent-sdk watchdog pydantic

# Create pyproject.toml for CLI installation
echo "Creating pyproject.toml..."
sudo tee "$MONITOR_SYSTEM_ROOT/pyproject.toml" > /dev/null <<'EOF_PYPROJECT'
[project]
name = "task-monitor"
version = "1.0.0"
description = "Multi-project task monitoring system with Claude Agent SDK integration"
requires-python = ">=3.10"
dependencies = [
    "watchdog>=5.0.0",
]

[project.scripts]
task-monitor = "cli:main"

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[tool.setuptools]
py-modules = ["cli", "models", "monitor_daemon", "task_executor"]
EOF_PYPROJECT

# Install CLI to user site-packages
echo "Installing CLI command..."
TEMP_DIR=$(mktemp -d)
sudo cp -r "$MONITOR_SYSTEM_ROOT"/* "$TEMP_DIR/"
chmod -R u+r "$TEMP_DIR"
pip install --user --break-system-packages "$TEMP_DIR" 2>/dev/null || true
rm -rf "$TEMP_DIR"

# Create config directory
echo "Creating config directory..."
mkdir -p "$CONFIG_DIR"

# Create .env file if it doesn't exist
if [ ! -f "$CONFIG_DIR/.env" ]; then
    echo "Creating .env file..."
    cat > "$CONFIG_DIR/.env" << ENVFILE
# Task Monitor Environment Configuration
# This file is sourced by the systemd service

# Claude API Configuration
ANTHROPIC_BASE_URL=https://open.bigmodel.cn/api/anthropic
ANTHROPIC_MODEL=glm-4.7
ANTHROPIC_AUTH_TOKEN=your_token_here
ENVFILE
    echo "Please edit $CONFIG_DIR/.env with your API credentials"
fi

# Install as systemd service (runs as admin user)
echo "Installing systemd service..."
sudo tee /etc/systemd/system/task-monitor.service > /dev/null <<EOF_SERVICE
[Unit]
Description=Multi-Project Task Monitor Daemon
After=network.target

[Service]
Type=simple
User=admin
Environment="PATH=$VENV_DIR/bin:/usr/bin"
Environment="PYTHONPATH=$MONITOR_SYSTEM_ROOT"
EnvironmentFile=$CONFIG_DIR/.env
ExecStart=$VENV_DIR/bin/python $MONITOR_SYSTEM_ROOT/monitor_daemon.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF_SERVICE

# Create management CLI
echo "Installing management CLI..."
sudo tee /usr/local/bin/task-monitor-control > /dev/null <<'EOF_CLI'
#!/bin/bash
# Task Monitor Control CLI

REGISTRY_FILE="$HOME/.config/task-monitor/registered.json"
MONITOR_ROOT="/opt/task-monitor"

case "$1" in
    register)
        PROJECT_PATH="$2"
        PROJECT_NAME="${3:-$(basename "$2")}"

        if [ -z "$PROJECT_PATH" ]; then
            echo "Usage: task-monitor-control register <project-path> [--name <project-name>]"
            exit 1
        fi

        # Create required directories
        mkdir -p "$PROJECT_PATH"/{tasks,results,logs,state}

        # Add to registry
        if [ ! -f "$REGISTRY_FILE" ]; then
            echo '{"projects": {}}' > "$REGISTRY_FILE"
        fi

        # Use python to update JSON
        python3 <<EOF_PY
import json
from datetime import datetime

registry_file = "$REGISTRY_FILE"
project_path = "$PROJECT_PATH"
project_name = "$PROJECT_NAME"

with open(registry_file, 'r') as f:
    registry = json.load(f)

registry['projects'][project_name] = {
    'path': project_path,
    'enabled': True,
    'registered_at': datetime.now().isoformat()
}

with open(registry_file, 'w') as f:
    json.dump(registry, f, indent=2)

print(f"Project '{project_name}' registered successfully")
EOF_PY

        # Auto-restart by default
        if [ "$4" != "--no-restart" ]; then
            echo "Restarting task-monitor service..."
            sudo systemctl restart task-monitor
        fi
        ;;

    unregister)
        PROJECT_NAME="$2"
        python3 <<EOF_PY
import json

registry_file = "$REGISTRY_FILE"
project_name = "$PROJECT_NAME"

with open(registry_file, 'r') as f:
    registry = json.load(f)

if project_name in registry['projects']:
    del registry['projects'][project_name]

    with open(registry_file, 'w') as f:
        json.dump(registry, f, indent=2)

    print(f"Project '{project_name}' unregistered")
else:
    print(f"Project '{project_name}' not found")
    exit(1)
EOF_PY
        sudo systemctl restart task-monitor
        ;;

    list)
        python3 <<EOF_PY
import json

registry_file = "$REGISTRY_FILE"

try:
    with open(registry_file, 'r') as f:
        registry = json.load(f)

    for name, info in registry['projects'].get('projects', {}).items():
        status = "✓ enabled" if info.get('enabled', True) else "✗ disabled"
        print(f"\n{name}")
        print(f"  Path: {info['path']}")
        print(f"  Status: {status}")
        print(f"  Registered: {info.get('registered_at', 'N/A')}")
except FileNotFoundError:
    print("No projects registered")
EOF_PY
        ;;

    enable|disable)
        PROJECT_NAME="$2"
        ENABLED="$([ "$1" = "enable" ] && echo "true" || echo "false")"

        python3 <<EOF_PY
import json

registry_file = "$REGISTRY_FILE"
project_name = "$PROJECT_NAME"
enabled = $ENABLED

with open(registry_file, 'r') as f:
    registry = json.load(f)

if project_name in registry['projects']:
    registry['projects'][project_name]['enabled'] = enabled

    with open(registry_file, 'w') as f:
        json.dump(registry, f, indent=2)

    print(f"Project '{project_name}' {'enabled' if enabled else 'disabled'}")
else:
    print(f"Project '{project_name}' not found")
    exit(1)
EOF_PY
        sudo systemctl restart task-monitor
        ;;

    restart)
        sudo systemctl restart task-monitor
        echo "Task monitor service restarted"
        ;;

    status)
        sudo systemctl status task-monitor
        ;;

    *)
        echo "Task Monitor Control CLI"
        echo ""
        echo "Usage: task-monitor-control <command> [args]"
        echo ""
        echo "Commands:"
        echo "  register <path> [--name <name>]  Register a new project"
        echo "  unregister <name>               Remove a project"
        echo "  list                             List all projects"
        echo "  enable <name>                   Enable a project"
        echo "  disable <name>                  Disable a project"
        echo "  restart                          Restart the service"
        echo "  status                           Show service status"
        exit 1
        ;;
esac
EOF_CLI

sudo chmod +x /usr/local/bin/task-monitor-control

# Reload and start service
echo "Reloading systemd daemon..."
sudo systemctl daemon-reload
sudo systemctl enable task-monitor
sudo systemctl restart task-monitor

echo ""
echo "Task monitor installed and started"
echo ""
echo "Status check:"
sudo systemctl status task-monitor --no-pager | head -10
echo ""
echo "Useful commands:"
echo "  task-monitor-control list                              - List all projects"
echo "  task-monitor-control register /path/to/project          - Register a project"
echo "  task-monitor queue                                      - Check queue status"
echo "  task-monitor -p /path/to/project queue                  - Check specific project"
echo "  sudo systemctl status task-monitor                      - Check service status"
echo "  sudo journalctl -u task-monitor -f                      - View logs"
echo ""
