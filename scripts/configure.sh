#!/bin/bash
# =============================================================================
# DataChat Survey Analyzer - Configuration Script
# =============================================================================
# This script creates the .env configuration file and initializes the
# application for first use.
#
# Usage:
#   sudo ./scripts/configure.sh
#
# =============================================================================

set -e  # Exit on error

echo "============================================================================"
echo "DataChat Survey Analyzer - Configuration"
echo "============================================================================"

INSTALL_DIR="/opt/survey-analyzer"

# Check if installation exists
if [ ! -d "$INSTALL_DIR" ]; then
    echo "Error: Installation directory not found: $INSTALL_DIR"
    echo "Please run ./scripts/install.sh first."
    exit 1
fi

cd $INSTALL_DIR

# =============================================================================
# Create .env File
# =============================================================================

echo ""
echo "Creating environment configuration..."

if [ -f .env ]; then
    echo "Warning: .env file already exists."
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Keeping existing .env file."
    else
        rm .env
        echo "Existing .env file removed."
    fi
fi

if [ ! -f .env ]; then
    cat > .env << 'EOF'
# =============================================================================
# DataChat Survey Analyzer - Production Configuration
# =============================================================================
# This file contains environment variables for the production deployment.
# Configure your LLM provider API keys below.
# =============================================================================

# -----------------------------------------------------------------------------
# LLM Provider Selection
# -----------------------------------------------------------------------------
# Required: Select which LLM provider to use
# Options: KIMI, DEEPSEEK, ZHIPU
LLM_PROVIDER=ZHIPU

# -----------------------------------------------------------------------------
# API Keys (Configure at least one based on your LLM_PROVIDER selection)
# -----------------------------------------------------------------------------

# Kimi (Moonshot AI) - https://platform.moonshot.cn/
KIMI_API_KEY=

# DeepSeek - https://platform.deepseek.com/
DEEPSEEK_API_KEY=

# Zhipu GLM (BigModel) - https://open.bigmodel.cn/
ZHIPU_API_KEY=

# -----------------------------------------------------------------------------
# LLM API Settings (Optional)
# -----------------------------------------------------------------------------
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=4000
LLM_MAX_SELF_CORRECTION_ITERATIONS=3

# -----------------------------------------------------------------------------
# Paths
# -----------------------------------------------------------------------------
PSPP_PATH=/usr/bin/pspp
OUTPUT_DIR=/opt/survey-analyzer/output
TEMP_DIR=/opt/survey-analyzer/temp

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------
LOG_LEVEL=INFO

# -----------------------------------------------------------------------------
# Human Review
# -----------------------------------------------------------------------------
ENABLE_HUMAN_REVIEW=true

# -----------------------------------------------------------------------------
# Statistical Thresholds (Optional)
# -----------------------------------------------------------------------------
SIGNIFICANCE_LEVEL=0.05
MIN_CRAMERS_V=0.1
MIN_CELL_COUNT=10
HIGH_CARDINALITY_THRESHOLD=30
EOF

    echo "✓ .env file created at $INSTALL_DIR/.env"
fi

# =============================================================================
# Create Directories
# =============================================================================

echo ""
echo "Ensuring directories exist..."

mkdir -p logs
mkdir -p data/input
mkdir -p output/{logs,reviews,temp}

# Set ownership
chown -R surveychat:surveychat logs data output

echo "✓ Directories ready"

# =============================================================================
# Initialize Checkpoint Database
# =============================================================================

echo ""
echo "Initializing checkpoint database..."

touch checkpoints.db
chown surveychat:surveychat checkpoints.db
chmod 640 checkpoints.db

echo "✓ Checkpoint database initialized"

# =============================================================================
# Configuration Complete
# =============================================================================

echo ""
echo "============================================================================"
echo "Configuration Complete!"
echo "============================================================================"
echo ""
echo "IMPORTANT: Configure your API keys before starting the service:"
echo ""
echo "  sudo nano $INSTALL_DIR/.env"
echo ""
echo "Set at least one of the following API keys:"
echo "  - ZHIPU_API_KEY (if LLM_PROVIDER=ZHIPU)"
echo "  - DEEPSEEK_API_KEY (if LLM_PROVIDER=DEEPSEEK)"
echo "  - KIMI_API_KEY (if LLM_PROVIDER=KIMI)"
echo ""
echo "After configuring your API keys:"
echo ""
echo "  1. Install the systemd service:"
echo "     sudo cp $INSTALL_DIR/../scripts/datachat.service /etc/systemd/system/"
echo "     sudo systemctl daemon-reload"
echo "     sudo systemctl enable datachat"
echo ""
echo "  2. Start the service:"
echo "     sudo systemctl start datachat"
echo ""
echo "  3. Check service status:"
echo "     sudo systemctl status datachat"
echo ""
echo "  4. View logs:"
echo "     sudo journalctl -u datachat -f"
echo ""
