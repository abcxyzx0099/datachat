# Task: Update Data Flow Architecture and Ensure Document Consistency

**Created**: 2025-01-29 15:45:00
**Status**: pending

---

## Task

Update the entire SURVEY_ANALYSIS_WORKFLOW_DESIGN.md document to reflect the corrected data flow architecture where Phase 2 produces a NEW dataset + NEW metadata that becomes the foundation for all subsequent phases. Ensure all sections are consistent with this architecture.

## Context

The current document has an architectural inconsistency:
- Section 2.3 shows `variable_centered_metadata` (from Phase 1) flowing to Phases 3-8
- But after Phase 2 completes, we have:
  - A NEW dataset (`recoded_data.sav`) with original + recoded variables
  - NEW metadata that describes ALL variables (original + new)

This creates a clean architectural boundary:
- **Stage 1 (Preparation)**: Phases 1-2 - Extract and enrich the dataset
- **Stage 2 (Analysis)**: Phases 3-6 - Analyze the complete dataset

The document needs consistency updates across ALL sections, not just the diagram.

## Scope

- Directories: `/home/admin/workspaces/datachat/`
- Files: `SURVEY_ANALYSIS_WORKFLOW_DESIGN.md` (entire document)
- Dependencies: The overall workflow design document structure

## Requirements

### Part 1: Section 2.3 - Data Flow Diagram (PRIMARY)

1. **Rename section 2.3** from "Data Evolution Through Phases" to "Data Flow Diagram"

2. **Rename Phase 2** from "New Variable Generation" to "New Dataset Generation"

3. **Add `updated_metadata` node**:
   - Represents metadata after Phase 2 (original variables + new recoded variables)
   - Produced by Phase 2 alongside `recoded_data.sav`

4. **Update data flow edges**:
   - Remove direct edges from `variable_centered_metadata` (Phase 1) to Phases 3-8
   - Add edges showing `recoded_data.sav` + `updated_metadata` flowing to Phases 3, 4, 5, 6, 7, 8

5. **Group phases into 2 Stages**:
   - Stage 1: Data Preparation (Phases 1-2)
   - Stage 2: Analysis & Reporting (Phases 3-6)

6. **Update the legend** to reflect the architectural change

7. **Update "Key Observations"** section to explain the two-stage architecture

### Part 2: Section 2.1 - High-Level Pipeline

8. **Update the pipeline diagram** to reflect:
   - Phase 2 name change to "New Dataset Generation"
   - Two-stage architecture if visible in the diagram

### Part 3: Section 2.2 - Step-by-Step Overview Table

9. **Update the table** to:
   - Change Phase 2 name from "New Variable Generation" to "New Dataset Generation"
   - Update Phase 2 description to mention producing both recoded data AND updated metadata
   - Review inputs/outputs for accuracy with new architecture

### Part 4: Section 2.4 - LangGraph State Management

10. **Review and update state definitions**:
    - Check if `RecodingState` or `ExtractionState` needs to include `updated_metadata`
    - Ensure state evolution description mentions the metadata update after Phase 2
    - Update "State Evolution by Step" table if needed

### Part 5: Detailed Step Specifications (Step 3, 4, 7, 8)

11. **Update Step 3 (Preliminary Filtering)**:
    - Input should reference `variable_centered_metadata` (this is correct - happens before Phase 2)

12. **Update Step 4 (Generate Recoding Rules)**:
    - Input should reference `filtered_metadata` (this is correct)
    - Output description should mention this contributes to `updated_metadata`

13. **Update Step 7 (Generate Indicators)**:
    - Input currently says `variable_centered_metadata` - CHANGE to `updated_metadata`
    - Rationale: Indicators should be generated from the COMPLETE metadata (original + recoded variables)

14. **Update Step 8 (Generate Table Specifications)**:
    - Input currently references `variable_centered_metadata` for identifying weighting variable
    - Should reference `updated_metadata` instead (complete metadata)
    - Update AI prompt template to use `updated_metadata`

### Part 6: Overview Section (1.2 Scope, 1.3 Key Objectives)

15. **Review for consistency**:
    - Check if any references to "recoding" vs "dataset generation" need updating
    - Ensure objectives align with two-stage architecture

### Part 7: State Evolution Summary (if exists)

16. **Update any summary tables** that show data flow between steps
17. **Ensure `updated_metadata` appears** as a state field after Phase 2 completion

## Deliverables

1. **Section 2.3**: Updated mermaid diagram with:
   - Two clear stages with visual separation
   - `updated_metadata` node after Phase 2
   - Correct data flow showing Stage 2 depends on Stage 1 outputs only
   - Updated legend and observations

2. **Section 2.1**: Updated high-level pipeline (if needed)

3. **Section 2.2**: Updated table with Phase 2 name change

4. **Section 2.4**: Updated state management description including `updated_metadata`

5. **Steps 7 & 8**: Updated input specifications to use `updated_metadata`

6. **Consistency check**: All sections reference correct metadata sources

## Constraints

1. Maintain existing color coding (AI vs Traditional programming)
2. Keep the diagram left-to-right flow
3. Preserve all 18 nodes (add 1 new: `updated_metadata`)
4. Keep the subgraph structure for phases
5. Maintain mermaid syntax validity
6. Do NOT change the actual workflow logic - only correct the documentation
7. Preserve all existing content that doesn't need changing

## Success Criteria

1. The diagram clearly shows Phase 2 produces both `recoded_data.sav` AND `updated_metadata`
2. Phases 3-6 clearly show dependencies on Phase 2 outputs (not Phase 1)
3. The two-stage architecture (Preparation vs Analysis) is visually distinct
4. Legend and observations accurately explain the updated architecture
5. Mermaid diagram renders correctly in GitHub/Markdown viewers
6. Steps 7 and 8 reference `updated_metadata` as input (not `variable_centered_metadata`)
7. Section 2.4 mentions `updated_metadata` in state definitions
8. NO inconsistencies remain between sections
9. A reviewer can trace any data object from its creation through all its uses

## Worker Investigation Instructions

[CRITICAL] You MUST do your own deep investigation before implementing:

1. **Read the ENTIRE document** - `SURVEY_ANALYSIS_WORKFLOW_DESIGN.md`
   - Understand all sections and how they relate
   - Note every place where metadata is referenced

2. **Search for all metadata references**:
   ```bash
   grep -n "metadata" SURVEY_ANALYSIS_WORKFLOW_DESIGN.md
   grep -n "variable_centered" SURVEY_ANALYSIS_WORKFLOW_DESIGN.md
   ```

3. **Identify ALL sections that need updates** - create a checklist before editing

4. **Plan the mermaid diagram structure**:
   - Sketch how nested subgraphs will work for 2 stages
   - Ensure edges don't cross confusingly
   - Count total nodes: should be 19 (18 existing + `updated_metadata`)

5. **Validate state management changes**:
   - Should `updated_metadata` be a new state class?
   - Or part of existing `RecodingState`?
   - Check how state flows to Steps 7-8

Find the file at: `/home/admin/workspaces/datachat/SURVEY_ANALYSIS_WORKFLOW_DESIGN.md`

Search for: `### 2.` to find all sections in Chapter 2
