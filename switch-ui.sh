#!/bin/bash
# =============================================================================
# DataChat UI Switcher
# =============================================================================
# Switches between Agent Chat UI and AionUi WebUI reverse proxy configs.
#
# Usage:
#   ./switch-ui.sh langgraph    # Switch to Agent Chat UI (port 3000)
#   ./switch-ui.sh aionui       # Switch to AionUi WebUI (port 25808)
#   ./switch-ui.sh status       # Show current UI
# =============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

LANGGRAPH_CONF="/etc/nginx/sites-available/sysy-langgraph.conf"
AIONUI_CONF="/etc/nginx/sites-available/sysy-aionui.conf"
SYMLINK="/etc/nginx/sites-enabled/sysy.site"

# Show current status
show_status() {
    if [ -L "$SYMLINK" ]; then
        current=$(readlink -f "$SYMLINK")
        if [[ "$current" == *"langgraph"* ]]; then
            echo -e "${GREEN}Current UI: Agent Chat UI (LangGraph)${NC}"
            echo -e "  Config: $current"
        elif [[ "$current" == *"aionui"* ]]; then
            echo -e "${GREEN}Current UI: AionUi WebUI${NC}"
            echo -e "  Config: $current"
        else
            echo -e "${YELLOW}Current UI: Unknown${NC}"
            echo -e "  Config: $current"
        fi
    else
        echo -e "${RED}No UI configured (symlink not found)${NC}"
    fi
    echo ""
}

# Switch UI
switch_ui() {
    local target=$1

    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE}  Switching DataChat UI${NC}"
    echo -e "${BLUE}============================================${NC}"
    echo ""

    show_status

    case "$target" in
        langgraph)
            echo -e "${YELLOW}Switching to Agent Chat UI...${NC}"
            sudo ln -sf "$LANGGRAPH_CONF" "$SYMLINK"
            ;;
        aionui)
            echo -e "${YELLOW}Switching to AionUi WebUI...${NC}"
            sudo ln -sf "$AIONUI_CONF" "$SYMLINK"
            ;;
        *)
            echo -e "${RED}Error: Unknown UI '$target'${NC}"
            echo "Usage: $0 {langgraph|aionui|status}"
            exit 1
            ;;
    esac

    echo -e "${YELLOW}Reloading Nginx...${NC}"
    sudo systemctl reload nginx

    echo -e "${GREEN}✓ UI switched successfully${NC}"
    echo ""

    echo -e "${BLUE}============================================${NC}"
    show_status
}

# Main
case "${1:-}" in
    status|"")
        show_status
        ;;
    langgraph|aionui)
        switch_ui "$1"
        ;;
    *)
        echo "Usage: $0 {langgraph|aionui|status}"
        exit 1
        ;;
esac
