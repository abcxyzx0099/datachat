#!/bin/bash
#
# rename_job.sh - Rename job temp file to final name with timestamp-first format
#
# Usage: bash scripts/rename_job.sh /path/to/job-xxx.md.tmp
#
# This script:
# 1. Renames the .md.tmp file to final .md with timestamp-first format
# 2. Outputs the final file path for use by subsequent scripts
#

set -e

# Configuration
PROJECT_ROOT="${PROJECT_ROOT:-/home/admin/workspaces/datachat}"
JOBS_DIR="${JOBS_DIR:-${PROJECT_ROOT}/jobs/items}"

# Get temp file path from argument
TEMP_FILE="$1"

if [ -z "$TEMP_FILE" ]; then
    echo "❌ Error: No temp file specified"
    echo "Usage: bash scripts/rename_job.sh /path/to/job-xxx.md.tmp"
    exit 1
fi

if [ ! -f "$TEMP_FILE" ]; then
    echo "❌ Error: Temp file not found: $TEMP_FILE"
    exit 1
fi

# Extract timestamp and description from temp file name
# Format: job-{timestamp}-{description}.md.tmp
TEMP_FILENAME=$(basename "$TEMP_FILE")
DESCRIPTION="${TEMP_FILENAME#job-}"  # Remove "job-" prefix
DESCRIPTION="${DESCRIPTION%.md.tmp}"  # Remove ".md.tmp" extension

# The temp filename should already contain the timestamp
# So we just need to remove the .tmp extension and move to final location
TIMESTAMP="${DESCRIPTION%%-*}"  # Extract timestamp (everything before first dash)
DESCRIPTION="${DESCRIPTION#*-}"    # Extract description (everything after first dash)

# Move to final location
FINAL_FILE="${JOBS_DIR}/job-${TIMESTAMP}-${DESCRIPTION}.md"
mv "$TEMP_FILE" "$FINAL_FILE"

# Output result (can be captured by caller)
echo "✅ Job created: $FINAL_FILE"
echo "$FINAL_FILE"
