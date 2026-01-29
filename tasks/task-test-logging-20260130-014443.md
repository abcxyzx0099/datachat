# Task: Test logging feature

**Status**: pending

---

## Task

Test the new logging feature to verify stdout/stderr capture and duration tracking.

## Context

The task monitor system has been updated with improved logging:
- stdout/stderr capture in result JSON
- duration_seconds tracking
- systemd journal logging with [task_id] prefix

## Scope

- Directories: tasks/, results/
- Files: Test task document only
- Dependencies: task-monitor service

## Requirements

1. Create a simple task that outputs some text
2. Verify that stdout is captured in the result JSON
3. Verify that duration_seconds is recorded
4. Verify that systemd journal contains [task_id] prefixed logs

## Deliverables

1. Task result JSON showing captured stdout
2. Logged duration
3. systemd journal entries with [test-logging-...] prefix

## Constraints

1. Task should complete quickly (simple test)
2. No complex operations needed

## Success Criteria

1. Result JSON contains `stdout` field with content
2. Result JSON contains `duration_seconds` > 0
3. systemd journal shows `[task-id]` prefixed log messages
4. Task status is "completed"

## Worker Investigation Instructions

- This is a test task - simply output some text to verify logging
- Use `print()` statements or return text in the output
- Complete the task successfully so we can examine the result
