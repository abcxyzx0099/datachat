# Task: Fix data-schema.md raw_data field documentation

**Status**: pending

---

## Task
Update `docs/application-design/data-schema.md` to reflect that `raw_data` field is deprecated and not stored in state.

## Context
The `data-schema.md` documentation incorrectly shows `raw_data: DataFrame` as being populated in Step 1. However, the actual implementation in `agent/state.py` marks `raw_data` as DEPRECATED and does NOT populate it. This design choice avoids LangGraph serialization issues with pandas DataFrames. The documentation should reflect the actual implementation.

## Scope
- Directories: docs/application-design/
- Files: data-schema.md
- Dependencies: None (documentation only)

## Requirements
1. Remove `raw_data` from the ExtractionState field table (lines 129-135)
2. Update the ExtractionState code block (lines 119-127) to remove or mark `raw_data` as deprecated
3. Add a note explaining why `raw_data` is not stored:
   - LangGraph uses msgpack serialization which doesn't handle pandas DataFrames well
   - Storing DataFrames in state would cause large checkpoint files and performance issues
   - Data is reloaded from `input_file_path` when needed instead

## Testing Requirements

### Test Type
- [x] **No Tests** - Documentation-only change

### Coverage Target
- N/A (documentation change)

### Test Scenarios
1. N/A

### Verification Commands
```bash
# No tests - verify documentation manually
# Check that raw_data is removed from field table
# Check that explanation note is added
```

## Deliverables
1. Updated `docs/application-design/data-schema.md` with:
   - `raw_data` removed from field table
   - Explanation note about why DataFrames are not stored in state

## Constraints
1. Do not change the actual code in `agent/state.py` - only update documentation
2. Follow existing documentation style and format
3. Keep the explanation clear and concise

## Success Criteria
1. `raw_data` is removed from the ExtractionState field table
2. A clear note explains that DataFrames are not stored to avoid serialization issues
3. Documentation accurately reflects the implementation in `agent/state.py`
4. No changes to actual code files

## Implementation Agent Investigation Instructions
- You MUST read `agent/state.py` lines 95-117 to understand the actual ExtractionState definition
- You MUST read `docs/application-design/data-schema.md` lines 117-148 to see what needs updating
- Find the exact locations where `raw_data` appears in the documentation
- Understand the reasoning: check the comment on line 100 of state.py about serialization issues
- Review existing documentation patterns in data-schema.md for consistency
