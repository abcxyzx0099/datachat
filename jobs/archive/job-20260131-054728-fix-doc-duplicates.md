# Task: Fix Duplicate Code Blocks in Survey Analysis Documentation

**Status**: pending

---

## Task
Remove duplicate code blocks in SURVEY_ANALYSIS_DETAILED_SPECIFICATIONS.md and move JSON imports to top of functions where they are used inside function bodies.

## Context
During documentation review of two survey analysis workflow documents, duplicate code blocks were identified in the detailed specifications document. The `generate_html_dashboard_node` function appears twice (lines 1620-1871) with verbatim duplication, and there is overlap in the `execute_python_statistics_script_node` function. Additionally, some code blocks import `json` module inside function bodies rather than at the top, which is non-idiomatic Python.

## Scope
- Directories: `docs/`
- Files: `docs/SURVEY_ANALYSIS_DETAILED_SPECIFICATIONS.md`
- Dependencies: None - standalone documentation fix

## Requirements
1. **Remove duplicate `generate_html_dashboard_node` function**
   - The function is duplicated at lines 1620-1871 and 1767-1871
   - Keep the first complete implementation (lines 1620-1766)
   - Remove the second duplicate block entirely

2. **Fix duplicate `execute_python_statistics_script_node` entries**
   - The function appears twice in Section 6.2
   - Consolidate into a single implementation
   - Ensure no code is lost in the consolidation

3. **Move JSON imports to top of code blocks**
   - Find all code blocks that use `import json` inside function bodies
   - Move these imports to the top of the code block
   - Ensure code remains executable after refactoring

4. **Preserve document structure**
   - Keep all section headers, tables, and cross-references intact
   - Maintain table of contents accuracy
   - Ensure line numbers in cross-references remain valid or are updated

## Deliverables
1. Updated `docs/SURVEY_ANALYSIS_DETAILED_SPECIFICATIONS.md` with duplicates removed
2. Brief summary of changes made (which blocks were removed/consolidated)

## Constraints
1. Follow project documentation conventions:
   - No version numbers in documentation
   - No changelog entries (git is source of truth)
   - No date metadata
2. Do not modify code functionality - only reorganize existing code
3. Preserve all comments and docstrings
4. Use idiomatic Python style (imports at top)

## Success Criteria
1. `generate_html_dashboard_node` appears exactly once in the document
2. `execute_python_statistics_script_node` appears exactly once in the document
3. All `import json` statements appear at the top of their code blocks
4. Document renders correctly with no broken formatting
5. All code examples remain syntactically valid Python

## Worker Investigation Instructions
- You MUST do your own deep investigation before implementing
- Find ALL instances of duplicate code:
  - Search for function names: `generate_html_dashboard_node`, `execute_python_statistics_script_node`
  - Compare implementations to verify exact duplication vs overlap
  - Check for any other potential duplicates in the document
- Identify ALL code blocks with internal imports:
  - Search for `import json` patterns inside function definitions
  - Verify that moving imports to top won't break the code examples
- Read the full context around each duplicate to ensure safe removal:
  - Check if the duplicates are in different sections with different purposes
  - Verify that removing one won't break document flow or references
