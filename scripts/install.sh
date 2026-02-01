#!/bin/bash
# =============================================================================
# DataChat Survey Analyzer - Installation Script
# =============================================================================
# This script installs the DataChat Survey Analyzer to /opt/survey-analyzer/
#
# Usage:
#   sudo ./scripts/install.sh
#
# Requirements:
#   - Run as root or with sudo
#   - Python 3.11 or later must be installed
#   - Internet connection for package installation
# =============================================================================

set -e  # Exit on error

echo "============================================================================"
echo "DataChat Survey Analyzer - Installation"
echo "============================================================================"

# =============================================================================
# Prerequisites Check
# =============================================================================

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Error: This script must be run as root or with sudo."
    exit 1
fi

# Check Python version
PYTHON_CMD=""
for python_cmd in python3.11 python3.12 python3.13 python3; do
    if command -v $python_cmd &> /dev/null; then
        PYTHON_VERSION=$($python_cmd --version | awk '{print $2}')
        PYTHON_MAJOR=$($python_cmd -c "import sys; print(sys.version_info.major)")
        PYTHON_MINOR=$($python_cmd -c "import sys; print(sys.version_info.minor)")

        if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 11 ]; then
            PYTHON_CMD=$python_cmd
            echo "✓ Found Python $PYTHON_VERSION ($python_cmd)"
            break
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo "Error: Python 3.11 or later is required but not found."
    echo "Please install Python 3.11+ before running this script."
    exit 1
fi

# =============================================================================
# Installation
# =============================================================================

INSTALL_DIR="/opt/survey-analyzer"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/.."

echo ""
echo "Installing DataChat Survey Analyzer to $INSTALL_DIR..."

# Create production directory structure
echo "Creating directory structure..."
mkdir -p $INSTALL_DIR
mkdir -p $INSTALL_DIR/{data,output,temp,logs,checkpoints}

# Copy application files
echo "Copying application files..."
cp -r $SCRIPT_DIR/agent $INSTALL_DIR/
cp -r $SCRIPT_DIR/config $INSTALL_DIR/
cp -r $SCRIPT_DIR/utils $INSTALL_DIR/
cp $SCRIPT_DIR/requirements.txt $INSTALL_DIR/
cp $SCRIPT_DIR/.env.example $INSTALL_DIR/

# Verify files were copied
if [ ! -d "$INSTALL_DIR/agent" ] || [ ! -d "$INSTALL_DIR/config" ]; then
    echo "Error: Failed to copy application files."
    exit 1
fi

echo "✓ Application files copied successfully"

# =============================================================================
# Install System Dependencies
# =============================================================================

echo ""
echo "Installing system dependencies..."

# Update package list
apt-get update -q

# Install PSPP
echo "Installing PSPP..."
apt-get install -y pspp pspp-dev

# Verify PSPP installation
if ! command -v pspp &> /dev/null; then
    echo "Warning: PSPP installation may have failed. Please verify manually."
else
    PSPP_VERSION=$(pspp --version | head -n1)
    echo "✓ $PSPP_VERSION"
fi

# =============================================================================
# Install Python Dependencies
# =============================================================================

echo ""
echo "Installing Python dependencies..."

cd $INSTALL_DIR

# Create virtual environment
echo "Creating virtual environment..."
$PYTHON_CMD -m venv venv

# Activate virtual environment and install packages
echo "Installing Python packages from requirements.txt..."
venv/bin/pip install --upgrade pip --quiet
venv/bin/pip install -r requirements.txt --quiet

echo "✓ Python dependencies installed"

# =============================================================================
# Create Service User
# =============================================================================

echo ""
echo "Creating service user..."

# Create service user if it doesn't exist
if ! id surveychat &> /dev/null; then
    useradd -r -s /bin/false -d $INSTALL_DIR surveychat
    echo "✓ Service user 'surveychat' created"
else
    echo "✓ Service user 'surveychat' already exists"
fi

# =============================================================================
# Set Permissions
# =============================================================================

echo ""
echo "Setting permissions..."

# Set ownership
chown -R surveychat:surveychat $INSTALL_DIR

# Set directory permissions
chmod 750 $INSTALL_DIR
chmod 750 $INSTALL_DIR/{agent,config,utils,venv}
chmod 770 $INSTALL_DIR/{data,output,temp,logs,checkpoints}

echo "✓ Permissions configured"

# =============================================================================
# Installation Complete
# =============================================================================

echo ""
echo "============================================================================"
echo "Installation Complete!"
echo "============================================================================"
echo ""
echo "Next steps:"
echo "  1. Configure the application:"
echo "     sudo ./scripts/configure.sh"
echo ""
echo "  2. Edit the environment file with your API keys:"
echo "     sudo nano $INSTALL_DIR/.env"
echo ""
echo "  3. Install the systemd service:"
echo "     sudo cp scripts/datachat.service /etc/systemd/system/"
echo "     sudo systemctl daemon-reload"
echo "     sudo systemctl enable datachat"
echo ""
echo "  4. Start the service:"
echo "     sudo systemctl start datachat"
echo ""
echo "  5. Check service status:"
echo "     sudo systemctl status datachat"
echo ""
echo "For manual testing, you can also run:"
echo "  cd $INSTALL_DIR"
echo "  source venv/bin/activate"
echo "  langgraph dev --port 8123 --host 0.0.0.0"
echo ""
