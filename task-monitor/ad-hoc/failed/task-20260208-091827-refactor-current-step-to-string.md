# Task: Refactor current_step from numeric to string identifiers

**Status**: pending

---

## Task
Refactor the `current_step` field in `ApprovalState` from integer (0-22) to string step identifiers for better readability and maintainability

## Context
The current implementation uses numeric step identifiers (0-22) for `current_step`, which are not self-descriptive and make debugging difficult. Refactoring to string identifiers (e.g., "recoding_review", "indicators_review") will improve code readability, debugging, and align with LangGraph's string-based node naming convention.

## Scope
- Directories: agent/, docs/application-design/, tests/
- Files:
  - `agent/state.py` - Core state definitions
  - `agent/nodes/__init__.py` - Step setting logic
  - `agent/edges.py` - Conditional routing based on step
  - `agent/server.py` - API endpoints that use current_step
  - All phase node files that set current_step
  - `tests/` - All tests that reference current_step
  - `docs/application-design/data-schema.md` - Update documentation

## Requirements
1. Define step name constants in `agent/state.py` for all 22 workflow steps
2. Change `current_step` type from `int` to `str` in `ApprovalState`
3. Update all node files to use string step identifiers instead of numbers
4. Update `agent/edges.py` conditional routing to work with string identifiers
5. Update `agent/server.py` API endpoint mappings (step 6→11→14 to step names)
6. Update all affected tests to use string identifiers
7. Update documentation in `docs/application-design/data-schema.md` to reflect new design
8. Maintain backward compatibility where possible (add helpers if needed)
9. Ensure all 22 steps have well-defined string names

## Testing Requirements

### Test Type
- [x] **Unit Tests** - Required for state changes and step constants
- [x] **Integration Tests** - Required for workflow execution
- [x] **E2E Tests** - Required for complete workflow verification

### Coverage Target
- **Minimum**: 80% code coverage for modified files
- **Test Files**:
  - `tests/core/test_state.py` - State definition tests
  - `tests/integration/test_graph_integration.py` - Workflow routing tests
  - `tests/e2e/test_e2e_workflow.py` - End-to-end workflow tests

### Test Scenarios
1. Step constants are correctly defined for all 22 steps
2. State initialization uses string step identifiers
3. Node execution sets correct string step identifier
4. Edge routing works with string step identifiers
5. API feedback endpoints map correctly to step names
6. Three-node pattern review steps trigger correctly with step names
7. All 22 steps can be traversed in order
8. Step comparisons and ordering work correctly

### Verification Commands
```bash
# Run core state tests
pytest tests/core/test_state.py -v

# Run integration tests
pytest tests/integration/test_graph_integration.py -v

# Run E2E tests
pytest tests/e2e/test_e2e_workflow.py -v

# Check coverage
coverage run -m pytest tests/ -v
coverage report --include='agent/state.py,agent/nodes/,agent/edges.py'
```

## Deliverables
1. Step name constants in `agent/state.py` (all 22 steps)
2. Updated `ApprovalState` with `current_step: str`
3. All node files updated to use string identifiers
4. Updated `edges.py` routing logic
5. Updated `server.py` feedback endpoint mappings
6. All tests updated and passing
7. Updated documentation

## Constraints
1. Do NOT break existing functionality - all tests must pass
2. Maintain the three-node pattern behavior for review steps
3. Step names should follow snake_case convention
4. Step names should be descriptive and consistent
5. Preserve step ordering semantics (step 1 comes before step 2)
6. Add helper functions if needed for step ordering/comparison

## Success Criteria
1. `current_step` type changed from `int` to `str`
2. All 22 steps have defined string constants
3. All nodes use string step identifiers
4. Edge routing works with string identifiers
5. API feedback endpoints work correctly
6. All tests pass (100% pass rate)
7. Coverage >= 80% for modified files
8. Documentation updated to reflect new design
9. No regressions in existing workflow execution

## Implementation Agent Investigation Instructions
- You MUST do your own deep investigation before implementing
- Find ALL files that set or read `current_step`: grep -r "current_step" agent/
- Find ALL files that compare step numbers: grep -r "current_step.*==" agent/
- Understand the three-node pattern: review `agent/edges.py` and `agent/nodes/phase*.py`
- Identify all 22 workflow steps and their purposes
- Review how the API uses current_step for feedback: check `agent/server.py` submit_feedback
- Check all tests that reference current_step or step numbers
- Review existing step naming patterns in node files
- Plan the step naming convention before implementing
- Consider adding a STEP_ORDER constant for ordering if needed
