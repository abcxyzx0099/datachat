# Issue: Task Executor Skill Not Using Sub-Agents When Invoked Via SDK

## Status
CLOSED

## Problem Description

When the `task-executor` skill was invoked via the Claude Agent SDK's `query()` function, the coordinator agent would **not spawn sub-agents** (Implementation Agent and Auditor Agent) as defined in the skill. Instead, it would choose to do the implementation work directly using Write/Edit tools, bypassing the two-agent workflow.

### Expected Behavior
The task-executor skill should:
1. Read the task specification document
2. Spawn an **Implementation Agent** via `Task(subagent_type="general-purpose")`
3. Spawn an **Auditor Agent** via `Task(subagent_type="general-purpose")`
4. Iterate based on audit feedback

### Actual Behavior
When invoked via SDK:
- The agent would read the task document
- Then directly implement using Write/Edit tools
- No sub-agents were spawned
- The two-agent workflow was bypassed

### Verification
Direct invocation of the skill via the **Skill tool** worked correctly and spawned sub-agents. The issue only occurred when invoked programmatically via the SDK.

## Investigation

### Attempted Solutions That Did NOT Work

1. **Adding enforcement language to the skill document**
   - Added "CRITICAL EXECUTION REQUIREMENT: MANDATORY TWO-AGENT WORKFLOW" section
   - Added explicit prohibitions and warnings
   - Result: Agent still ignored and did direct implementation

2. **Using `allowed_tools` parameter**
   - Tried restricting tools to only allow `Task` tool
   - Result: Parameter appears to be non-functional in SDK

3. **Using `ClaudeSDKClient` instead of `query()`**
   - Tried different SDK invocation methods
   - Result: Same behavior - agent optimized for efficiency

### Root Cause
When invoked via SDK, the agent optimizes for efficiency. Since it has access to implementation tools (Write, Edit), it determines that:
- "This task is simple, I'll just do it myself"
- Spawning sub-agents adds overhead
- Direct implementation is faster

The skill instructions alone are not strong enough to override this efficiency optimization behavior.

## Solution

### Working Solution: `system_prompt` Parameter

The `system_prompt` parameter in `ClaudeAgentOptions` **successfully forces** the coordinator-only behavior.

### Implementation

**File**: `/home/admin/workspaces/task-queue/task_queue/executor.py`

**Lines 61-89**:
```python
# Configure SDK with system_prompt to enforce coordinator behavior
options = ClaudeAgentOptions(
    cwd=str(self.project_root),
    permission_mode="bypassPermissions",
    setting_sources=["project"],
    tools={"type": "preset", "preset": "claude_code"},
    # CRITICAL: Force coordinator-only behavior - no direct implementation
    system_prompt="""You are a TASK COORDINATOR. Your ONLY job is to coordinate work through sub-agents using the Task tool.

CRITICAL RULES:
1. You are FORBIDDEN from doing any implementation work yourself
2. You MUST ALWAYS use the Task tool to spawn sub-agents for ALL implementation work
3. NEVER use Write, Edit, NotebookEdit, or any implementation tool directly
4. DO NOT think "this is simple, I'll do it myself" - ALWAYS use Task tool

Your workflow for the task-executor skill:
1. Read the task specification document
2. Spawn Implementation Agent: Use Task tool with subagent_type="general-purpose"
   - description: "Execute the task"
   - prompt: [full task document content]
3. Spawn Auditor Agent: Use Task tool with subagent_type="general-purpose"
   - description: "Audit implementation quality"
   - prompt: [task document + implementation result]
4. Check audit verdict
5. If audit fails (FAIL, NEEDS_REVISION), iterate: spawn agents again with feedback
6. Return final result

You MUST use the Task tool for ALL implementation. DO NOT take shortcuts.
""",
)
```

### Verification

**Test Task**: `task-20260203-221600-systemprompt-test.md`

**Result** from `/tasks/task-queue/results/task-20260203-221600-systemprompt-test.json`:

```json
{
  "status": "completed",
  "stdout": "Now I'll execute this task using the two-agent workflow as specified.
I'll spawn an Implementation Agent to create the file, and an Auditor Agent to verify the work.
You are the Implementation Agent. Execute the following task:
...
Now I'll spawn an Auditor Agent to verify the implementation quality:
You are the Auditor Agent. Your job is to audit the implementation quality...
...
## ✅ Task Execution Complete

The two-agent workflow (Implementation Agent + Auditor Agent) has been successfully executed:
- Implementation Agent: ✅ Complete
- Auditor Agent: ✅ PASS
The test confirms that the system_prompt successfully enforces the two-agent workflow."
}
```

### Evidence of Success

The coordinator output clearly shows:
1. Acknowledgment: "I'll spawn an Implementation Agent..."
2. Implementation Agent spawned with full task delegation
3. Auditor Agent spawned with verification request
4. Both agents completed successfully
5. Final result confirmed the two-agent workflow was used

## Related Changes

### Skill Document Cleanup
Since the `system_prompt` now enforces the behavior, redundant enforcement language was removed from:

**File**: `.claude/skills/task-executor/SKILL.md`

**Removed**:
- "CRITICAL EXECUTION REQUIREMENT: MANDATORY TWO-AGENT WORKFLOW" section
- Redundant "MANDATORY" headers and warnings
- Detailed prohibitions lists
- Common mistakes table

**Kept**:
- Clear workflow descriptions
- Phase 2 (Implementation) - concise Task tool usage
- Phase 3 (Audit) - concise Task tool usage

## Key Takeaways

1. **Skill instructions alone are not enough** when invoking via SDK
2. **`system_prompt` parameter can override** the agent's efficiency optimization
3. **Explicit prohibitions work** - "You are FORBIDDEN from..." is effective
4. **The solution is clean** - enforcement is in code, not in skill documentation
5. **Test with real tasks** - verification confirmed the two-agent workflow works

## Files Modified

1. `/home/admin/workspaces/task-queue/task_queue/executor.py` - Added `system_prompt` to `ClaudeAgentOptions`
2. `/home/admin/workspaces/datachat/.claude/skills/task-executor/SKILL.md` - Removed redundant enforcement language

## References

- **Test Result**: `/tasks/task-queue/results/task-20260203-221600-systemprompt-test.json`
- **Test Task**: `/tasks/task-archive/task-20260203-221600-systemprompt-test.md`
- **Related Issue**: `implementation/issues/daemon-not-processing-queued-tasks.md` (separate issue about daemon not auto-processing)
