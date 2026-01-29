# Task: Renumber non-integer step numbers to integers in workflow design

**Created**: 2025-01-29 15:55:00
**Status**: pending

---

## Task
Convert all non-integer step numbers in `SURVEY_ANALYSIS_WORKFLOW_DESIGN.md` to integer numbers. The document currently uses decimal step numbers (Step 4.5, Step 10.5) which causes confusion. These must be renumbered to integers, shifting all subsequent steps accordingly.

## Context
During review of `SURVEY_ANALYSIS_WORKFLOW_DESIGN.md`, the non-integer step numbering was identified as a source of potential confusion:
- **Step 4.5**: Deprecated validation step (now integrated into Step 4)
- **Step 10.5**: Chi-square statistics computation (Python-based, separate from PSPP)

The workflow has 6 phases with steps 1-13. The decimal numbering breaks the integer sequence and makes references unclear.

## Scope
- **File**: `SURVEY_ANALYSIS_WORKFLOW_DESIGN.md` (project root, 2,892 lines)
- **Affected step numbers**:
  - Step 4.5 (deprecated) - should be removed or renumbered
  - Step 10.5 (Chi-square statistics) - should become Step 11
  - Steps 11-13 must shift to 12-14

## Requirements
1. **Identify all occurrences** of non-integer step numbers:
   - `Step 4.5` (deprecated validation step)
   - `Step 10.5` (Chi-square statistics)
   - `Step 4.6` (human review - may need renumbering)

2. **Determine new numbering scheme**:
   - Option A: Remove Step 4.5 entirely (deprecated), rename 10.5 → 11, shift 11-13 → 12-14
   - Option B: Renumber ALL steps sequentially 1-14
   - Choose the option that maintains clarity and minimal disruption

3. **Update ALL references** throughout the document:
   - Section headers (### Step X: Title)
   - Mermaid diagrams (flowchart labels)
   - Tables (phase descriptions, state evolution tables)
   - Code examples (comments, docstrings)
   - Inline text references
   - Cross-references between steps
   - File paths in project structure section

4. **Update phase descriptions** if step counts change

5. **Verify consistency** - no decimal step numbers should remain

## Deliverables
1. Updated `SURVEY_ANALYSIS_WORKFLOW_DESIGN.md` with integer-only step numbering
2. Summary of changes made (before/after step mapping)
3. Confirmation that all references were updated

## Constraints
1. **Must not change step functionality** - only renumber, not modify logic
2. **Must preserve all content** - no information loss during renumbering
3. **Must maintain document structure** - phases, sections, formatting intact
4. **Follow Git best practices** - single atomic change for renumbering

## Success Criteria
1. No decimal step numbers (X.5) remain in the document
2. All step references are consistent and use integer numbers
3. Mermaid diagrams show correct step numbers
4. All tables reference correct step numbers
5. Code examples reflect updated step numbers
6. Document renders correctly with no broken references

## Worker Investigation Instructions
[CRITICAL] You MUST do your own deep investigation before implementing:

1. **Find ALL step number occurrences**:
   ```bash
   grep -n "Step [0-9]" SURVEY_ANALYSIS_WORKFLOW_DESIGN.md
   grep -n "step.*[0-9]" SURVEY_ANALYSIS_WORKFLOW_DESIGN.md
   ```

2. **Identify the complete step list** - understand current numbering:
   - Steps 1-10 (integer)
   - Step 10.5 (decimal)
   - Steps 11-13 (integer)

3. **Check for Step 4.5 and 4.6** - understand the deprecated step relationship

4. **Map old to new step numbers** before making any changes

5. **Use Edit tool strategically** - make targeted replacements rather than rewriting the entire file

6. **Verify all diagrams** - mermaid flowcharts contain step references

7. **Check the project structure section** - file names like `10_5_compute_chi_square_statistics.py` may need updating
