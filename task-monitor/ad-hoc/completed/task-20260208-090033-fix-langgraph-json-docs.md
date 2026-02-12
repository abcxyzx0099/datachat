# Task: Fix langgraph.json documentation inconsistency

**Status**: completed ✅

---

## Task
Correct the `langgraph.json` format documentation in `system-configuration.md` to match the official LangGraph CLI specification and the actual implementation

## Context
The `docs/application-design/system-configuration.md` file (section 6.1) shows an incorrect `langgraph.json` structure with `nodes`, `edges`, and `conditional_edges` defined directly in JSON. According to official LangGraph CLI documentation, the correct format uses string references to graph factory functions. The actual `langgraph.json` in the project is correct and matches the official standard.

## Scope
- Directories: docs/application-design/
- Files: docs/application-design/system-configuration.md
- Dependencies: None (documentation-only change)

## Requirements
1. Update section 6.1 "langgraph.json Structure" in `system-configuration.md` to show the correct format
2. Remove incorrect `nodes`, `edges`, and `conditional_edges` JSON structure
3. Show correct string reference format: `"graph_name": "module/path:function_name"`
4. Preserve the `checkpoint` section which is a valid configuration option
5. Update the "Node Path Format" subsection to clarify the correct string reference format
6. Ensure the example matches the actual `langgraph.json` file in the project root

## Testing Requirements

### Test Type
- [ ] **Unit Tests** - Not required (documentation only)
- [ ] **Integration Tests** - Not required (documentation only)
- [ ] **E2E Tests** - Not required (documentation only)
- [x] **No Tests** - Documentation correction only

### Coverage Target
- N/A (documentation change)

### Test Scenarios
1. Verify updated documentation matches actual `langgraph.json` file
2. Verify updated documentation matches official LangGraph CLI specification

### Verification Commands
```bash
# Compare documentation example with actual file
cat langgraph.json

# Verify langgraph dev still works
langgraph dev --help
```

## Deliverables
1. Updated `docs/application-design/system-configuration.md` section 6.1 with correct format
2. Documentation should reflect that nodes/edges are defined in Python code, not JSON

## Constraints
1. Do NOT modify the actual `langgraph.json` file (it is already correct)
2. Only update the documentation to match reality
3. Follow existing documentation style and markdown formatting
4. Preserve all other sections of the document unchanged

## Success Criteria
1. Section 6.1 shows correct `langgraph.json` format with string references
2. Documentation example matches the actual `langgraph.json` in project root
3. Incorrect `nodes`, `edges`, `conditional_edges` JSON structure is removed
4. `checkpoint` section is preserved and correctly documented
5. Documentation clearly states that graph structure is defined in Python code
6. All other sections remain unchanged

## Implementation Agent Investigation Instructions
- You MUST read the actual `langgraph.json` file in project root before making changes
- You MUST read the current `docs/application-design/system-configuration.md` section 6.1
- Compare the official LangGraph CLI format with what needs to be corrected
- Verify that the `checkpoint` configuration is valid and should be preserved
- Ensure only section 6.1 is modified; no other sections are changed
