# Task: Update Step 3 Filtering Criteria in Survey Analysis Documents

**Status**: pending

---

## Task

Update the Step 3 (Preliminary Filtering) section in both survey analysis workflow documents with specific filtering criteria from the backup file, replacing vague descriptions with precise, configurable rules.

## Context

During document review, it was discovered that the current Step 3 filtering criteria are vague ("variables starting with $, record, time") while the backup file (`docs/SURVEY_ANALYSIS_WORKFLOW_DESIGN.md.backup`) contains well-defined filtering rules. The current documents need to be updated to include:

1. Specific filtering rules with conditions and rationales
2. Configurable parameters (cardinality_threshold, filter_binary, filter_other_text)
3. Default values for each parameter

This update ensures implementers have clear, actionable specifications for the filtering logic.

## Scope

- **Directories**: `docs/`
- **Files**:
  - `docs/SURVEY_ANALYSIS_WORKFLOW_DESIGN.md`
  - `docs/SURVEY_ANALYSIS_DETAILED_SPECIFICATIONS.md`
  - Reference: `docs/SURVEY_ANALYSIS_WORKFLOW_DESIGN.md.backup` (read-only)
- **Dependencies**: None (documentation-only change)

## Requirements

1. **Update SURVEY_ANALYSIS_WORKFLOW_DESIGN.md**:
   - Change node name from `filter_metadata_node` to `preliminary_filter_node` (or keep `filter_metadata_node` if preferred - be consistent)
   - Add configuration parameters to the `DEFAULT_CONFIG` section:
     - `cardinality_threshold`: 30 (default)
     - `filter_binary`: true (default)
     - `filter_other_text`: true (default)
   - Replace vague filtering description with the following rules table:

   | Rule | Condition | Reason |
   |------|-----------|--------|
   | Binary variables | Exactly 2 distinct values | No room for recoding |
   | High cardinality | Distinct values > threshold | Typically IDs, open-ended |
   | Other text fields | Name contains "other" AND type is character | Open-ended feedback |

   - Update the Step 3 description to: "Filter out variables that don't need recoding to reduce AI context"
   - Update Input section to include config parameters
   - Add the filtering rules table to the Step 3 section

2. **Update SURVEY_ANALYSIS_DETAILED_SPECIFICATIONS.md**:
   - Add the same filtering rules table to the Step 3 implementation section
   - Update any code examples that reference filtering logic to use the new criteria

3. **Consistency Check**:
   - Ensure node names are consistent across both documents
   - Ensure config parameter names match
   - Ensure the rationale for each filtering rule is included

## Deliverables

1. Updated `docs/SURVEY_ANALYSIS_WORKFLOW_DESIGN.md` with detailed Step 3 filtering criteria
2. Updated `docs/SURVEY_ANALYSIS_DETAILED_SPECIFICATIONS.md` with detailed Step 3 filtering criteria
3. Both documents should have consistent node names, parameter names, and rule descriptions

## Constraints

1. **No functional code changes** - This is a documentation-only update
2. **Preserve existing structure** - Keep document formatting, headings, and overall structure intact
3. **Maintain consistency** - Both documents must have matching information
4. **Don't modify the backup file** - It's the reference source only
5. **Follow existing style** - Match the markdown formatting and table style used in other sections

## Success Criteria

1. Both documents contain the filtering rules table with all three rules (Binary, High cardinality, Other text)
2. Both documents list the three configuration parameters with default values
3. Step 3 section in both documents has the updated description: "Filter out variables that don't need recoding to reduce AI context"
4. Node name is consistent across both documents (either `filter_metadata_node` or `preliminary_filter_node`)
5. References to Step 3 in other parts of the documents (e.g., State Evolution tables, Mermaid diagrams) remain consistent

## Worker Investigation Instructions

**CRITICAL**: Before implementing, you MUST:

1. **Read both target documents completely**:
   - `docs/SURVEY_ANALYSIS_WORKFLOW_DESIGN.md`
   - `docs/SURVEY_ANALYSIS_DETAILED_SPECIFICATIONS.md`

2. **Read the backup reference**:
   - `docs/SURVEY_ANALYSIS_WORKFLOW_DESIGN.md.backup` - lines 844-868 contain the complete Step 3 specification

3. **Find ALL references to Step 3 filtering**:
   ```bash
   grep -n "Step 3\|filter_metadata_node\|Preliminary Filtering\|filtered_metadata" docs/SURVEY_ANALYSIS_*.md
   ```

4. **Identify all sections that reference Step 3**:
   - Mermaid diagrams (node labels)
   - Step specifications section
   - State evolution tables
   - Configuration section (DEFAULT_CONFIG)
   - LangGraph configuration (node mappings)

5. **Decide on node name**:
   - Current document uses `filter_metadata_node`
   - Backup uses `preliminary_filter_node`
   - Choose one and apply consistently throughout both documents

6. **Plan your edits**:
   - List exact line numbers for each change
   - Verify no other content conflicts with new information
   - Ensure formatting matches existing tables/sections
