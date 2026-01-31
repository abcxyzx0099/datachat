#!/bin/bash
#
# rename_job.sh - Rename job temp file to final name with generated timestamp
#
# Usage: bash scripts/rename_job.sh /path/to/job-{description}.md.tmp
#
# This script:
# 1. Generates a timestamp using date command
# 2. Renames the .md.tmp file to final .md with timestamp-first format
# 3. Outputs the final file path for use by subsequent scripts
#

set -e

# Configuration
PROJECT_ROOT="${PROJECT_ROOT:-/home/admin/workspaces/datachat}"
JOBS_DIR="${JOBS_DIR:-${PROJECT_ROOT}/jobs/pending}"
JOB_PREFIX="job"

# Get temp file path from argument
TEMP_FILE="$1"

if [ -z "$TEMP_FILE" ]; then
    echo "❌ Error: No temp file specified"
    echo "Usage: bash scripts/rename_job.sh /path/to/${JOB_PREFIX}-{description}.md.tmp"
    exit 1
fi

if [ ! -f "$TEMP_FILE" ]; then
    echo "❌ Error: Temp file not found: $TEMP_FILE"
    exit 1
fi

# Generate current timestamp
# Format: YYYYMMDD-HHMMSS
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")

# Extract description from temp file name
# Format: job-{description}.md.tmp (no timestamp)
TEMP_FILENAME=$(basename "$TEMP_FILE")
DESCRIPTION="${TEMP_FILENAME#${JOB_PREFIX}-}"  # Remove "job-" prefix
DESCRIPTION="${DESCRIPTION%.md.tmp}"  # Remove ".md.tmp" extension

# Build final filename with generated timestamp
FINAL_FILE="${JOBS_DIR}/${JOB_PREFIX}-${TIMESTAMP}-${DESCRIPTION}.md"

# Move to final location
mv "$TEMP_FILE" "$FINAL_FILE"

# Output result (can be captured by caller)
echo "✅ Job created: $FINAL_FILE"
echo "$FINAL_FILE"
