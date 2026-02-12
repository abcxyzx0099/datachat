# Task: Fix node count inconsistency in langgraph-studio-setup.md

**Status**: completed

---

## Task
Update `docs/application-design/langgraph-studio-setup.md` to correct the graph node count from 24 to 22 nodes to match the actual implementation.

## Context
The `langgraph-studio-setup.md` document incorrectly states that the survey_analysis graph contains **24 nodes**, but the actual implementation in `agent/graph.py` only adds **22 nodes** to the graph. Investigation revealed:

- 24 node functions are defined in the codebase
- Only 22 nodes are added to the graph with `builder.add_node()`
- The comment on line 162 of `agent/graph.py` explicitly states "Add 22 Nodes"
- The extra 2 nodes (`generate_pspp_crosstabs_syntax_node` and `execute_pspp_crosstabs_node`) are alternative implementations using the older CROSSTABS command instead of CTABLES, and are NOT connected to the workflow

## Scope
- Directories: docs/application-design/
- Files:
  - `docs/application-design/langgraph-studio-setup.md` (primary)
  - Verify `agent/graph.py` for node count (reference)
- Dependencies: None

## Requirements
1. Update line 100 in `docs/application-design/langgraph-studio-setup.md` to state **22 nodes** instead of 24 nodes
2. Verify the phase breakdown in the document correctly sums to 22:
   - Phase 1 (Extraction): 3 nodes
   - Phase 2 (Recoding): 5 nodes
   - Phase 3 (Indicators): 3 nodes
   - Phase 4 (Tables): 5 nodes
   - Phase 5 (Statistics): 2 nodes
   - Phase 6 (Filtering): 2 nodes
   - Phase 7 (PowerPoint): 1 node
   - Phase 8 (Dashboard): 1 node
   - Total: 3 + 5 + 3 + 5 + 2 + 2 + 1 + 1 = 22
3. Ensure no other references to "24 nodes" exist in the document

## Testing Requirements

### Test Type
- [ ] **Unit Tests** - Not required for documentation change
- [ ] **Integration Tests** - Not required for documentation change
- [ ] **E2E Tests** - Not required for documentation change
- [x] **No Tests** - Documentation-only change

### Coverage Target
N/A - Documentation change

### Verification Steps
1. Read the updated document and verify it states "22 nodes"
2. Search for any remaining references to "24 nodes" in the file
3. Verify the phase breakdown counts sum to 22

### Verification Commands
```bash
# Verify no references to "24 nodes" remain
grep -n "24 node" docs/application-design/langgraph-studio-setup.md

# Verify correct node count is documented
grep -n "22 node" docs/application-design/langgraph-studio-setup.md
```

## Deliverables
1. Updated `docs/application-design/langgraph-studio-setup.md` with corrected node count (22 instead of 24)

## Constraints
1. Do NOT modify the actual implementation code
2. Only update the documentation to reflect reality
3. Preserve the document structure and format
4. No version metadata or dates should be added (per CLAUDE.md guidelines)

## Success Criteria
1. `langgraph-studio-setup.md` states **22 nodes** (not 24)
2. No references to "24 nodes" remain in the document
3. Phase breakdown counts sum to 22
4. Document formatting and structure preserved

## Implementation Agent Investigation Instructions
- You MUST read the current `docs/application-design/langgraph-studio-setup.md` to understand the context
- Verify the actual node count in `agent/graph.py` by counting `builder.add_node()` calls (lines 164-201)
- Understand that the extra 2 nodes are alternative CROSSTABS implementations NOT added to the graph
- Only make the minimal necessary change to correct the node count
- Do NOT add version numbers, dates, or change logs (per project documentation guidelines)
