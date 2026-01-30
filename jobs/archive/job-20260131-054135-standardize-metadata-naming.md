# Standardize Metadata Naming Across Survey Analysis Documents

## Task

Standardize all references to the complete metadata extracted from `new_data.sav` to use `new_metadata` consistently across both survey analysis documentation files.

## Context

During document review, an inconsistency was found in how the complete metadata (extracted from `new_data.sav` after Step 8) is referenced:

- **Detailed Specifications** (line 60): Uses `new_metadata` in the TypedDict definition
- **Workflow Design** (line 289): Uses `updated_metadata` in the RecodingState example
- **Workflow Design** (diagram): Uses `updatedMeta` as a node label
- **Detailed Specifications** (lines 395, 452): Incorrectly references `updated_metadata` in prompt templates

This is the authoritative metadata source for all steps after Step 8 (Phase 2). Inconsistent naming will cause implementation errors when developers reference different field names.

## Scope

**Files to modify:**
- `docs/SURVEY_ANALYSIS_DETAILED_SPECIFICATIONS.md`
- `docs/SURVEY_ANALYSIS_WORKFLOW_DESIGN.md`

**Do NOT modify:**
- Code files (`agent/`, `dflib/`, etc.) - this is documentation-only
- Backup files (`*.backup`)
- Other documentation

## Requirements

### 1. Standardize Field Name to `new_metadata`

Replace all occurrences of `updated_metadata` and `updatedMeta` with `new_metadata` in both documents.

**Specific changes in SURVEY_ANALYSIS_DETAILED_SPECIFICATIONS.md:**
- Line 395: Change `{format_metadata_for_llm(updated_metadata)}` to `{format_metadata_for_llm(new_metadata)}`
- Line 452: Change `{format_metadata_for_llm(updated_metadata)}` to `{format_metadata_for_llm(new_metadata)}`

**Specific changes in SURVEY_ANALYSIS_WORKFLOW_DESIGN.md:**
- Line 289: Change `updated_metadata: Dict[str, Any]` to `new_metadata: Dict[str, Any]`
- Line 309: Change example from `updated_metadata` to `new_metadata`
- Line 320: Change table entry from `updated_metadata` to `new_metadata`
- Lines 376, 440, 443: Change diagram node label `updatedMeta` to `newMeta` or better yet, `new_metadata`
- Line 473: In legend table, change `updated_metadata` to `new_metadata`
- Line 477: In legend table, change `updated_metadata` to `new_metadata`
- Lines 492, 505, 509: In observations section, change `updated_metadata` to `new_metadata`
- Line 751: In Step 10 description, change `updated_metadata` to `new_metadata`

### 2. Remove Duplicate Code in Detailed Specifications

The `generate_powerpoint_node` function has duplicate code that must be removed:
- Lines 1616-1676: Delete this entire duplicate block
- The original complete function is at lines 1515-1614

### 3. Verify TypedDict Consistency

After making changes, verify that:
- All references to the complete metadata field use `new_metadata`
- The TypedDict definitions in both documents are consistent
- The field name matches between code examples and explanatory text

## Deliverables

1. **Modified SURVEY_ANALYSIS_DETAILED_SPECIFICATIONS.md**:
   - All `updated_metadata` references changed to `new_metadata`
   - Duplicate code block (lines 1616-1676) removed
   - Document remains well-formatted and internally consistent

2. **Modified SURVEY_ANALYSIS_WORKFLOW_DESIGN.md**:
   - All `updated_metadata` and `updatedMeta` references changed to `new_metadata`
   - Table entries, diagram labels, and explanatory text updated
   - Document remains well-formatted and internally consistent

3. **Verification summary**: Brief confirmation that:
   - No remaining references to `updated_metadata` or `updatedMeta`
   - Both documents use `new_metadata` consistently
   - Duplicate code has been removed

## Constraints

- **Documentation only**: Do not modify any Python code or implementation files
- **Preserve formatting**: Maintain markdown structure, table formatting, and code blocks
- **No semantic changes**: Only change variable names, not logic or descriptions
- **Cross-reference integrity**: Ensure links between documents still work

## Success Criteria

1. [ ] `grep -r "updated_metadata" docs/SURVEY_ANALYSIS_*.md` returns no results (excluding .backup files)
2. [ ] `grep -r "updatedMeta" docs/SURVEY_ANALYSIS_*.md` returns no results (excluding .backup files)
3. [ ] Both documents use `new_metadata` consistently for the complete metadata field
4. [ ] Duplicate code block (lines 1616-1676 in Detailed Specs) is removed
5. [ ] Documents remain well-formatted and readable
6. [ ] Mermaid diagrams render correctly after label changes

## Worker Investigation Instructions

Before making changes, the Worker Agent should:

1. **Read both documents completely** to understand the full context and ensure no other inconsistencies are missed
2. **Search for all occurrences** of the inconsistent names using grep to create a comprehensive checklist
3. **Verify the TypedDict definition** in Detailed Specs (around line 60) confirms `new_metadata` is the correct field name
4. **Check if any other documentation** references these field names that should also be updated
5. **Plan the edits** to ensure they're done efficiently and consistently

After making changes:
1. **Run verification grep commands** to confirm all instances are fixed
2. **Read the modified sections** to ensure formatting and clarity are preserved
3. **Verify the duplicate code removal** didn't break the document structure
