#!/bin/bash
#
# rename_task.sh - Rename task temp file(s) to final name with timestamp
#
# Usage (single file): bash scripts/rename_task.sh /path/to/task-{description}.md.tmp
# Usage (batch mode):  bash scripts/rename_task.sh
#
# This script:
# 1. Single file mode: Renames one .md.tmp file with current timestamp
# 2. Batch mode: Scans ALL .md.tmp files, sorts by creation time, renames in order
# 3. In batch mode: Uses file creation time for timestamp, sleeps 1s between files
#

set -e

# Configuration
PROJECT_ROOT="${PROJECT_ROOT:-/home/admin/workspaces/datachat}"
TASKS_DIR="${TASKS_DIR:-${PROJECT_ROOT}/tasks/task-monitor/pending}"
TASK_PREFIX="task"
SLEEP_SECONDS=5

# Get creation time (birth time) of a file
# Falls back to modification time if birth time not available
get_file_time() {
    local file="$1"
    # Try birth time (%W) first, fallback to modification time (%Y)
    local birth_time=$(stat -c %W "$file" 2>/dev/null || echo "0")
    if [ "$birth_time" = "0" ] || [ "$birth_time" = "-" ]; then
        stat -c %Y "$file"
    else
        echo "$birth_time"
    fi
}

# Convert epoch timestamp to YYYYMMDD-HHMMSS format
epoch_to_timestamp() {
    date -d "@$1" +"%Y%m%d-%H%M%S" 2>/dev/null || date -r "$1" +"%Y%m%d-%H%M%S" 2>/dev/null
}

# Process a single temp file
process_single_file() {
    local temp_file="$1"
    local use_file_time="${2:-false}"

    if [ ! -f "$temp_file" ]; then
        echo "❌ Error: Temp file not found: $temp_file"
        return 1
    fi

    local timestamp
    if [ "$use_file_time" = "true" ]; then
        # Use file's creation time for timestamp
        local file_epoch=$(get_file_time "$temp_file")
        timestamp=$(epoch_to_timestamp "$file_epoch")
    else
        # Use current time for timestamp
        timestamp=$(date +"%Y%m%d-%H%M%S")
    fi

    # Extract description from temp file name
    # Format: task-{description}.md.tmp (no timestamp)
    local temp_filename=$(basename "$temp_file")
    local description="${temp_filename#${TASK_PREFIX}-}"
    description="${description%.md.tmp}"

    # Build final filename with timestamp
    local final_file="${TASKS_DIR}/${TASK_PREFIX}-${timestamp}-${description}.md"

    # Move to final location
    mv "$temp_file" "$final_file"

    # Output result
    echo "✅ Task created: $final_file"
    echo "$final_file"
}

# Batch mode: Process all .md.tmp files sorted by creation time
batch_process() {
    local temp_files=()

    # Scan for all .md.tmp files
    while IFS= read -r -d '' file; do
        temp_files+=("$file")
    done < <(find "$TASKS_DIR" -maxdepth 1 -name "${TASK_PREFIX}-*.md.tmp" -print0 2>/dev/null)

    if [ ${#temp_files[@]} -eq 0 ]; then
        echo "ℹ️  No .md.tmp files found in $TASKS_DIR"
        return 0
    fi

    echo "🔍 Found ${#temp_files[@]} temp file(s) to process"

    # Sort files by creation time using a stable sort
    local sorted_files=()
    while IFS= read -r file; do
        sorted_files+=("$file")
    done < <(
        for file in "${temp_files[@]}"; do
            echo "$(get_file_time "$file")|$file"
        done | sort -n | cut -d'|' -f2-
    )

    # Process each file in order
    local count=0
    for file in "${sorted_files[@]}"; do
        count=$((count + 1))
        echo ""
        echo "[$count/${#temp_files[@]}] Processing: $(basename "$file")"
        process_single_file "$file" "true"

        # Sleep between files (but not after the last one)
        if [ $count -lt ${#temp_files[@]} ]; then
            sleep "$SLEEP_SECONDS"
        fi
    done

    echo ""
    echo "✅ Batch processing complete: $count file(s) renamed"
}

# Main entry point
main() {
    local temp_file="$1"

    if [ -z "$temp_file" ]; then
        # Batch mode: No argument = process all .md.tmp files
        batch_process
    else
        # Single file mode: Original behavior
        process_single_file "$temp_file" "false"
    fi
}

main "$@"
