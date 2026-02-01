#!/bin/bash
# =============================================================================
# DataChat SPSS Analyzer - Docker Clean Script
# =============================================================================
# This script removes Docker containers, images, and volumes
# =============================================================================
# Usage: docker-clean.sh [--all]
#   --all    Also removes the Docker image (forces rebuild on next start)
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

REMOVE_IMAGE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --all)
            REMOVE_IMAGE=true
            shift
            ;;
        -h|--help)
            echo "Usage: docker-clean.sh [options]"
            echo ""
            echo "Options:"
            echo "  --all       Also remove the Docker image"
            echo "  -h, --help  Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use -h for help"
            exit 1
            ;;
    esac
done

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}DataChat Docker Clean${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Stop and remove containers
echo -e "${GREEN}Stopping and removing containers...${NC}"
docker-compose down -v

# Remove image if requested
if [ "$REMOVE_IMAGE" = true ]; then
    echo -e "${GREEN}Removing Docker image...${NC}"
    docker rmi datachat-app 2>/dev/null || echo "Image not found or already removed"
fi

# Remove dangling images
echo -e "${GREEN}Removing dangling images...${NC}"
docker image prune -f

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Cleanup completed!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

if [ "$REMOVE_IMAGE" = true ]; then
    echo "Next time you start, the image will be rebuilt."
    echo "Use 'docker-compose up' to start again."
fi
