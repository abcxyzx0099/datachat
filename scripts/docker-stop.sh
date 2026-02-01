#!/bin/bash
# =============================================================================
# DataChat SPSS Analyzer - Docker Stop Script
# =============================================================================
# This script stops the DataChat Docker container
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}DataChat Docker Stop${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo -e "${RED}Error: Docker daemon is not running${NC}"
    exit 1
fi

# Check if container is running
if ! docker-compose ps | grep -q "datachat-app"; then
    echo -e "${YELLOW}DataChat container is not running${NC}"
    exit 0
fi

# Stop the container
echo -e "${GREEN}Stopping DataChat container...${NC}"
docker-compose down

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}DataChat stopped successfully${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
