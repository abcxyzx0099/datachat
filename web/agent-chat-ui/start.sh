#!/bin/bash
# Quick start script for Agent Chat UI development server
# Part of the DataChat SPSS Analyzer project

set -e

echo "=================================="
echo "Agent Chat UI - Development Server"
echo "=================================="
echo

# Check if we're in the correct directory
if [ ! -f "package.json" ]; then
    echo "Error: Must be run from web/agent-chat-ui directory"
    echo "Usage: cd web/agent-chat-ui && ./start.sh"
    exit 1
fi

# Check if pnpm is installed
if ! command -v pnpm &> /dev/null; then
    echo "Error: pnpm is not installed"
    echo "Install with: npm install -g pnpm"
    exit 1
fi

# Check if .env.local exists
if [ ! -f ".env.local" ]; then
    echo "Warning: .env.local not found"
    echo "Creating from .env.example..."
    cp .env.example .env.local
    echo "Please edit .env.local with your configuration"
fi

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Dependencies not found. Installing..."
    pnpm install
fi

echo "Starting development server..."
echo "UI will be available at: http://localhost:3000"
echo "Press Ctrl+C to stop"
echo

pnpm dev
