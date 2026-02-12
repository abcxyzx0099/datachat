# Task: Remove CROSSTABS-based alternative implementation

**Status**: pending

---

## Task
Remove all CROSSTABS-based alternative implementation code from Phase 4 (tables) nodes, keeping only the CTABLES-based primary implementation.

## Context
The codebase contains two alternative implementations for generating PSPP cross-tabulation syntax:
1. **CTABLES-based** (primary) - Currently used by the graph
2. **CROSSTABS-based** (alternative) - Not used, dead code

Since CTABLES is the working approach and CROSSTABS is unused legacy code, this task cleans up the alternative implementation to reduce code complexity and maintenance burden.

## Scope
- Directories: agent/nodes/, tests/
- Files affected:
  - `agent/nodes/phase4_tables.py` (main implementation file)
  - `agent/nodes/__init__.py` (exports)
- Dependencies: None (alternative code is not used by graph)

## Requirements
1. Remove `generate_pspp_crosstabs_syntax_node` function from phase4_tables.py
2. Remove `execute_pspp_crosstabs_node` function from phase4_tables.py
3. Remove helper function `_generate_crosstabs_command` from phase4_tables.py
4. Remove crosstabs-related exports from `agent/nodes/__init__.py`:
   - `generate_pspp_crosstabs_syntax_node`
   - `execute_pspp_crosstabs_node`
5. Update module docstring in phase4_tables.py to remove references to alternative implementation
6. Ensure CTABLES-based implementation (`generate_pspp_table_syntax_node`, `execute_pspp_tables_node`) remains intact

## Testing Requirements

### Test Type
- [ ] **Unit Tests** - Not required (removing dead code only)
- [ ] **Integration Tests** - Not required (no functional change)
- [ ] **E2E Tests** - Not required (no functional change)
- [x] **No Tests** - Code cleanup only, no behavior change

### Coverage Target
- **Minimum**: N/A (removing code only)
- **Test Files**: None

### Test Scenarios
1. Verify existing tests still pass (no functional regression)
2. Verify graph construction still works with only CTABLES nodes

### Verification Commands
```bash
# Verify imports still work
python3 -c "from agent.nodes import generate_pspp_table_syntax_node, execute_pspp_tables_node"

# Verify graph construction works
python3 -c "from agent.graph import build_graph; g = build_graph(checkpointer_path=False); print('Graph built successfully')"

# Run existing tests (should all still pass)
pytest tests/nodes/test_phase4_tables.py -v
```

## Deliverables
1. Cleaned `agent/nodes/phase4_tables.py` (no crosstabs functions)
2. Updated `agent/nodes/__init__.py` (no crosstabs exports)
3. Updated module docstrings

## Constraints
1. CTABLES-based implementation must remain fully functional
2. No changes to graph.py (graph already uses CTABLES nodes)
3. No changes to tests (tests verify CTABLES implementation)
4. Preserve all comments and documentation for CTABLES functions

## Success Criteria
1. CROSSTABS functions removed from phase4_tables.py:
   - `generate_pspp_crosstabs_syntax_node`
   - `execute_pspp_crosstabs_node`
   - `_generate_crosstabs_command`
2. CROSSTABS exports removed from __init__.py
3. Module docstrings updated
4. All existing tests pass (100% pass rate)
5. Graph construction works without errors
6. No references to crosstabs in phase4_tables.py (except in comments explaining CTABLES)

## Implementation Agent Investigation Instructions

- You MUST investigate the current structure of agent/nodes/phase4_tables.py
- Find ALL functions related to CROSSTABS: grep -n "crosstab" agent/nodes/phase4_tables.py
- Understand which functions are CTABLES vs CROSSTABS
- Identify all exports in agent/nodes/__init__.py related to crosstabs
- Review how graph.py uses these nodes (it should only use CTABLES)
- Identify any comments/docstrings that mention "alternative" implementation
- Review existing test patterns: check tests/nodes/test_phase4_tables.py to understand what is tested

**Key Files to Review:**
- agent/nodes/phase4_tables.py (main file to modify)
- agent/nodes/__init__.py (exports to modify)
- agent/graph.py (verify it doesn't use crosstabs nodes)
- tests/nodes/test_phase4_tables.py (understand test coverage)
