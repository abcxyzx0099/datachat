#!/bin/bash

# Set project root
PROJECT_ROOT="$(pwd)"
VENV_DIR="$PROJECT_ROOT/.venv"

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment and install dependencies
echo "Installing dependencies..."
source "$VENV_DIR/bin/activate"
pip install -r requirements.txt

# Create directories
mkdir -p tasks results logs/executor state prompts

# Install as systemd service (runs as current user)
CURRENT_USER=$(whoami)
sudo cat > /etc/systemd/system/task-monitor.service <<EOF
[Unit]
Description=Task Monitor Daemon (SDK)
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$PROJECT_ROOT
Environment="PATH=$VENV_DIR/bin:\$PATH"
ExecStart=$VENV_DIR/bin/python scripts/monitor_daemon.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable task-monitor
sudo systemctl start task-monitor

echo ""
echo "Monitor installed and started"
echo "Check status: sudo systemctl status task-monitor"
echo "View logs: tail -f logs/monitor.log"
echo ""
echo "Useful commands:"
echo "  source .venv/bin/activate          - Activate virtual environment"
echo "  python scripts/cli.py              - Show all tasks"
echo "  python scripts/cli.py task-001      - Show specific task"
echo "  python scripts/cli.py queue         - Show queue state"
