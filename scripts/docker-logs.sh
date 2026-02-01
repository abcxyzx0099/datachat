#!/bin/bash
# =============================================================================
# DataChat SPSS Analyzer - Docker Logs Script
# =============================================================================
# This script shows logs from the DataChat Docker container
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Follow logs by default
FOLLOW=true

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -f|--follow)
            FOLLOW=true
            shift
            ;;
        -n|--no-follow)
            FOLLOW=false
            shift
            ;;
        -h|--help)
            echo "Usage: docker-logs.sh [options]"
            echo ""
            echo "Options:"
            echo "  -f, --follow    Follow logs (default)"
            echo "  -n, --no-follow  Don't follow logs"
            echo "  -h, --help      Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use -h for help"
            exit 1
            ;;
    esac
done

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo -e "${RED}Error: Docker daemon is not running${NC}"
    exit 1
fi

# Show logs
if [ "$FOLLOW" = true ]; then
    docker-compose logs -f
else
    docker-compose logs
fi
