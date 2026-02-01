#!/bin/bash
# =============================================================================
# DataChat SPSS Analyzer - Docker Exec Script
# =============================================================================
# This script executes commands inside the DataChat Docker container
# =============================================================================
# Usage: docker-exec.sh [command]
# If no command is specified, starts an interactive shell
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if container is running
if ! docker-compose ps | grep -q "datachat-app"; then
    echo -e "${RED}Error: DataChat container is not running${NC}"
    echo "Start it with: docker-compose up -d"
    exit 1
fi

# Execute command or start shell
if [ $# -eq 0 ]; then
    echo -e "${GREEN}Starting interactive shell in DataChat container...${NC}"
    docker-compose exec datachat bash
else
    echo -e "${GREEN}Executing command in DataChat container: $@${NC}"
    docker-compose exec datachat "$@"
fi
