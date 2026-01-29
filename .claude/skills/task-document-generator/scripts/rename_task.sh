#!/bin/bash
#
# rename_task.sh - Rename task temp file to final name with timestamp
#
# Usage: bash scripts/rename_task.sh /path/to/task-xxx.md.tmp
#
# This script:
# 1. Renames the .md.tmp file to final .md with timestamp
# 2. Outputs the final file path for use by subsequent scripts
#

set -e

# Configuration
PROJECT_ROOT="${PROJECT_ROOT:-/home/admin/workspaces/datachat}"
TASKS_DIR="${TASKS_DIR:-${PROJECT_ROOT}/tasks}"

# Get temp file path from argument
TEMP_FILE="$1"

if [ -z "$TEMP_FILE" ]; then
    echo "❌ Error: No temp file specified"
    echo "Usage: bash scripts/rename_task.sh /path/to/task-xxx.md.tmp"
    exit 1
fi

if [ ! -f "$TEMP_FILE" ]; then
    echo "❌ Error: Temp file not found: $TEMP_FILE"
    exit 1
fi

# Extract description from temp file name (remove task- prefix and .md.tmp extension)
TEMP_FILENAME=$(basename "$TEMP_FILE")
DESCRIPTION="${TEMP_FILENAME#task-}"
DESCRIPTION="${DESCRIPTION%.md.tmp}"

# Get timestamp and rename atomically
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
FINAL_FILE="${TASKS_DIR}/task-${DESCRIPTION}-${TIMESTAMP}.md"
mv "$TEMP_FILE" "$FINAL_FILE"

# Output result (can be captured by caller)
echo "✅ Task created: $FINAL_FILE"
echo "$FINAL_FILE"
