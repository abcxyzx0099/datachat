# Job: Verify Survey Analysis Documents are Correctly Fixed

## Task

Verify that all fixes were correctly applied to the two survey analysis workflow documents and ensure consistency.

## Context

During a review of the survey analysis workflow documents, several issues were identified:
1. Field naming inconsistency: `updated_metadata` vs `new_metadata`
2. Missing state fields in TypedDict definitions
3. Incomplete code implementations with placeholder functions
4. Missing docstrings and function signatures

The decision was made to standardize on `new_metadata` as the field name throughout both documents.

## Scope

**Directories:**
- `docs/`

**Files:**
- `docs/SURVEY_ANALYSIS_WORKFLOW_DESIGN.md`
- `docs/SURVEY_ANALYSIS_DETAILED_SPECIFICATIONS.md`

**Dependencies:**
- None external
- Documents reference each other via links

## Requirements

### 1. Field Naming Consistency

Verify that `new_metadata` is used consistently throughout BOTH documents:
- In all TypedDict definitions
- In all step specifications (Input/Output sections)
- In all code examples
- In data flow diagrams
- In state evolution tables
- In terminology/glossary sections

The field `updated_metadata` should NOT appear anywhere in either document.

### 2. State Field Completeness

Verify the following state fields are properly defined and referenced:

**In `SURVEY_ANALYSIS_DETAILED_SPECIFICATIONS.md`:**

| State Class | Field | Type |
|-------------|-------|------|
| `StatisticalAnalysisState` | `statistical_summary` | `List[Dict]` (not `Dict`) |
| `StatisticalAnalysisState` | `statistical_summary_path` | `str` |
| `FilteringState` | `filter_list_json_path` | `str` |
| `FilteringState` | `significant_tables_json_path` | `str` |
| `PresentationState` | `charts_generated` | `List[Dict]` |

### 3. Implementation Completeness

Verify that all placeholder functions have been replaced with complete implementations:

- `extract_contingency_table_from_csv()` - Helper for Step 18
- `execute_python_statistics_script_node()` - Complete implementation
- `add_contingency_table_to_slide()` - Helper for PowerPoint generation
- All edge routing functions (`should_retry_*`, `should_approve_*`)

### 4. Docstring Quality

Verify all functions have proper docstrings with:
- Function description
- Args section (for parameters)
- Returns or Output section (for return values/state fields)
- Type hints where applicable

### 5. Documentation References

- Verify document footer references are clean (no redundant version info)
- Verify cross-references between documents are correct

## Deliverables

1. **Verification Report** - A summary of findings:
   - Any remaining inconsistencies found
   - Confirmation that `new_metadata` is used consistently
   - List of any missing or incomplete implementations

2. **Fix Any Remaining Issues** - If issues are found during verification, fix them

## Constraints

- Do NOT change the field naming convention back to `updated_metadata`
- Do NOT modify the overall architecture or workflow design
- Maintain the existing document structure and formatting

## Success Criteria

1. Searching for `updated_metadata` in both files returns NO results (except in comments explaining the change)
2. `new_metadata` appears consistently in all appropriate locations
3. All TypedDict definitions include the required state fields
4. All placeholder functions have complete implementations
5. All functions have proper docstrings with Args/Returns
6. Both documents are internally consistent and cross-reference correctly

## Worker Investigation Instructions

1. **Search for inconsistencies**: Use `grep` to search for `updated_metadata` in both files
2. **Read both documents completely**: Verify that fixes were applied correctly
3. **Check TypedDict definitions**: Ensure all required fields are present with correct types
4. **Verify code implementations**: Check that no placeholder comments remain (e.g., `// ... add table rows`)
5. **Cross-reference validation**: Ensure references between documents are accurate
6. **Report findings**: Create a concise summary of verification results

## Priority

Normal - Documentation verification and cleanup task.

## Notes

- The user explicitly requested `new_metadata` as the standard field name
- The task was essentially completed during the conversation; this job is for verification only
