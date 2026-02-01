#!/bin/bash
# =============================================================================
# DataChat SPSS Analyzer - Docker Build Script
# =============================================================================
# This script builds the DataChat Docker image
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}DataChat Docker Build${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    echo -e "${RED}Error: Docker daemon is not running${NC}"
    echo "Please start Docker and try again"
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Warning: .env file not found${NC}"
    echo "Creating .env from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${YELLOW}Please edit .env and configure your API keys${NC}"
    else
        echo -e "${RED}Error: .env.example not found${NC}"
        exit 1
    fi
fi

# Build the Docker image
echo -e "${GREEN}Building Docker image...${NC}"
docker-compose build

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Build completed successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "To start the application:"
echo -e "  ${YELLOW}docker-compose up${NC}"
echo ""
echo "To start in detached mode:"
echo -e "  ${YELLOW}docker-compose up -d${NC}"
echo ""
echo "To view logs:"
echo -e "  ${YELLOW}docker-compose logs -f${NC}"
echo ""
echo "To stop the application:"
echo -e "  ${YELLOW}docker-compose down${NC}"
echo ""
