#!/bin/bash
# =============================================================================
# DataChat SPSS Analyzer - Docker Start Script
# =============================================================================
# This script starts the DataChat Docker container
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}DataChat Docker Start${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo -e "${RED}Error: Docker daemon is not running${NC}"
    echo "Please start Docker and try again"
    exit 1
fi

# Check if image exists
if ! docker image ls datachat-app &> /dev/null; then
    echo -e "${YELLOW}Docker image not found. Building...${NC}"
    bash scripts/docker-build.sh
fi

# Create necessary directories if they don't exist
echo -e "${GREEN}Creating necessary directories...${NC}"
mkdir -p data output temp logs

# Start the container
echo -e "${GREEN}Starting DataChat container...${NC}"
docker-compose up -d

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}DataChat is starting...${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "LangGraph Studio will be available at:"
echo -e "  ${YELLOW}http://localhost:8123${NC}"
echo ""
echo "To view logs:"
echo -e "  ${YELLOW}docker-compose logs -f${NC}"
echo ""
echo "To stop:"
echo -e "  ${YELLOW}docker-compose down${NC}"
echo ""

# Wait for container to be healthy
echo -e "${GREEN}Waiting for container to be healthy...${NC}"
timeout=30
while [ $timeout -gt 0 ]; do
    if docker-compose ps | grep -q "healthy"; then
        echo -e "${GREEN}Container is healthy!${NC}"
        exit 0
    fi
    sleep 1
    ((timeout--))
done

echo -e "${YELLOW}Container is starting up...${NC}"
echo "Check logs with: docker-compose logs -f"
