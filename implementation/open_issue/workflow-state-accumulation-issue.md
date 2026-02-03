# Workflow State Accumulation Issue

**Status:** Open
**Created:** 2025-02-03
**Related:** Graph/E2E workflow tests

## Issue Description

The LangGraph workflow completes successfully (all 22 steps execute, all output files are generated), but the final `current_step` value remains at 4 instead of 22.

### Observed Behavior

When running end-to-end workflow tests:
- All 22 steps execute correctly
- All final output files are generated (`powerpoint_file`, `html_dashboard_file`, etc.)
- Final state contains all expected fields from all 22 phases
- BUT: `current_step = 4` (from step 4) instead of `current_step = 22` (from final step)

### Debug Output

```
DEBUG: result keys = dict_keys([...all 40+ state keys...])
DEBUG: result['current_step'] = 4
DEBUG: result['errors'] = []
DEBUG: result['recoding_rules'] = {'recoding_rules': [], 'indicators': [], 'table_specifications': []}
```

All final outputs present:
- `powerpoint_file`: Set (step 21 output)
- `html_dashboard_file`: Set (step 22 output)
- `statistical_summary`: Populated (step 18 output)
- `filtered_tables`: Populated (step 20 output)
- etc.

## Root Cause Analysis

The issue is in **LangGraph state accumulation behavior**. When nodes return state updates using the `**state` pattern:

```python
new_state = {
    **state,  # Preserves all existing fields
    "current_step": 4,
    "recoding_rules": recoding_rules,
}
```

LangGraph's default state merger may not be properly updating the `current_step` field when:
1. Multiple nodes update the same field (`current_step`)
2. The state schema uses `total=False` TypedDict inheritance
3. No custom reducer is defined for `current_step`

### Key Findings

1. **No custom state reducer**: The graph is built with `StateGraph(WorkflowState)` without any custom reducer function
2. **TypedDict structure**: `WorkflowState` inherits from multiple sub-states, with `current_step` defined in `ApprovalState`
3. **State updates are correct**: Each node correctly sets its `current_step` value (e.g., step 22 sets `"current_step": 22`)
4. **Workflow execution is complete**: All outputs are generated, meaning all nodes executed successfully

## Affected Tests

All workflow/e2e tests that check `current_step` at the end:

- `tests/core/test_graph.py::TestEndToEndWorkflow::test_end_to_end_workflow`
- `tests/core/test_graph.py::TestEndToEndWorkflow::test_end_to_end_workflow_steps_execution`
- `tests/core/test_graph.py::TestStateEvolution::test_state_evolution`
- `tests/e2e/test_e2e_complete_workflow.py::TestCompleteWorkflowE2E::test_complete_22_step_workflow`
- And ~12 more e2e workflow tests

## Possible Solutions

### Option 1: Add Custom State Reducer

Define a reducer function that explicitly handles `current_step` updates:

```python
def state_reducer(current: WorkflowState, update: dict) -> WorkflowState:
    """Custom state reducer to ensure current_step always updates."""
    result = {**current, **update}
    # Always take the latest current_step value
    return result
```

Then compile the graph with:
```python
graph = builder.compile(checkpointer=checkpointer, reducer=state_reducer)
```

### Option 2: Use Mutable State Pattern

Instead of treating `current_step` as an immutable field that gets overwritten, use a pattern where each node explicitly increments or checks the step.

### Option 3: Check LangGraph Version Behavior

The issue might be specific to a LangGraph version. Verify if upgrading to the latest version resolves the state accumulation behavior.

### Option 4: Accept Current Behavior

If the workflow is functionally correct (all outputs generated), consider that `current_step` is just metadata and the actual workflow completion is what matters. Tests could be adjusted to check for output file presence instead of `current_step` value.

## Test Status Summary

**Total Tests:** 1,352 (including skipped)
**Passing:** 1,335
**Failing:** 17
**Skipped:** 18

### Breakdown of 17 Failures

1. **State accumulation issue (primary):** 3 core graph tests
   - test_end_to_end_workflow
   - test_end_to_end_workflow_steps_execution
   - test_state_evolution

2. **Missing function attributes:** 3 tests
   - Tests expect `run_pspp`, `create_powerpoint`, `create_html_dashboard` functions
   - These appear to be internal functions that may have been renamed

3. **E2E workflow tests:** 11 tests
   - Most depend on the `current_step` issue
   - Some have related issues (recursion limit, file not found)

### Files to Investigate

1. `/home/admin/workspaces/datachat/agent/graph.py` - Graph building and compilation
2. `/home/admin/workspaces/datachat/agent/state.py` - WorkflowState TypedDict definition
3. `/home/admin/workspaces/datachat/tests/core/test_graph.py` - Failing workflow tests

## Next Steps

1. Try adding a custom state reducer (Option 1)
2. Verify LangGraph version and check for known issues
3. If reducer doesn't work, investigate LangGraph's internal state merging logic
4. Consider alternative: change tests to verify workflow completion via output files instead of `current_step`

## Related Files

- `agent/graph.py` - Graph building code
- `agent/state.py` - State definitions
- `tests/core/test_graph.py` - Failing workflow tests
- `tests/e2e/` - E2E test directory
