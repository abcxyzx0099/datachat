# Task: Refactor Survey Analysis Workflow Design into Concise and Detailed Versions

**Status**: pending

---

## Task

Refactor the existing Survey Analysis Workflow Design document (3,238 lines) into two separate documents:
1. **Concise version** - Focused, scannable workflow design
2. **Detailed specifications** - Complete implementation details moved to appendix-style document

## Context

The current `docs/SURVEY_ANALYSIS_WORKFLOW_DESIGN.md` document is verbose and contains repetitive content. Key areas needing attention:

1. **State Management (Section 2.4)**: Contains significant repetition between the main `WorkflowState` definition and the "Task-Specific States" explanation

2. **Three-Node Pattern (Section 2.2.1)**: Currently a subsection, but is a key architectural pattern used in 3 different phases (Steps 4-6, 9-11, 12-14)

3. **Overall verbosity**: Extensive code examples, redundant explanations, and multiple similar diagrams

The goal is to create a main document that is easy to scan and reference, while preserving all detailed information in a separate specifications document for implementers.

## Scope

- **Files affected**:
  - `docs/SURVEY_ANALYSIS_WORKFLOW_DESIGN.md` (to be replaced with concise version)
  - `docs/SURVEY_ANALYSIS_WORKFLOW_DESIGN.md` (backup current to appendix)
  - `docs/SURVEY_ANALYSIS_DETAILED_SPECIFICATIONS.md` (new file with all verbose details)

- **Sections to restructure**:
  - Section 2 (Workflow Architecture) - create new Section 2.4 for "Key Architectural Patterns"
  - Section 2.2.1 (Three-Node Pattern) - promote to new Section 2.4 subsection
  - Section 2.4 (State Management) - move to new Section 2.4 subsection, streamline
  - Section 3 (Detailed Step Specifications) - keep logic/pseudocode, move full code to detailed specs
  - Section 11 (Appendix) - expand with all moved content

- **Content to keep intact**:
  - Section 2.3 (Data Flow Diagram) - keep content as-is, title may be updated

## Requirements

### Document Structure Requirements

**1. Concise Version (`docs/SURVEY_ANALYSIS_WORKFLOW_DESIGN.md`)**

- Target length: ~1,200-1,500 lines (down from 3,238 lines)
- Structure:
  ```
  1. Overview (brief)
  2. Workflow Architecture
     2.1 High-Level Pipeline (main flowchart)
     2.2 Phase Descriptions (table summary only)
     2.3 Data Flow Diagram (keep content intact, title may change)
     2.4 Key Architectural Patterns
         2.4.1 Three-Node Pattern (Generate -> Validate -> Review)
         2.4.2 State Management (streamlined)
  3. Step Specifications (concise - logic only, pseudocode)
  4. Configuration
  5. Technology Stack
  6. Project Structure
  7. Execution Example
  8. Error Handling & Recovery
  9. Future Enhancements
  10. Human-in-the-Loop Implementation
  11. Appendix (references to detailed specs, not full content)
  ```

**2. Detailed Specifications (`docs/SURVEY_ANALYSIS_DETAILED_SPECIFICATIONS.md`)**

- All verbose content moved here:
  - Complete `WorkflowState` and all sub-state definitions (full TypedDict classes)
  - Full code examples for each step (complete Python implementations)
  - Detailed prompts for AI nodes (initial, validation retry, human feedback variants)
  - Complete validation check specifications
  - Full statistical analysis implementation details
  - PSPP syntax examples for all scenarios
  - Error handling specifics

### Content Transformation Requirements

**1. Section 2.3 (Data Flow Diagram)**
- **MUST**: Keep all content intact - do not modify the diagram or explanations
- **MAY**: Update the section title if needed for clarity

**2. State Management (new Section 2.4.2)**
- Show structure skeleton only in concise version
- Move complete TypedDict definitions to detailed specs
- Eliminate repetition between "WorkflowState" and "Task-Specific States"
- Use precise terminology: "State fields", "State inheritance", "State evolution"

**3. Three-Node Pattern (new Section 2.4.1)**
- Promote from subsection 2.2.1 to standalone pattern section
- Keep concise explanation with one clear diagram
- Move detailed examples and prompts to detailed specs
- Use precise terminology: "Generate node", "Validate node", "Review node", "Feedback loop", "Iteration tracking"

**4. Step Specifications (Section 3)**
- Keep: Purpose, input/output descriptions, logic flow
- Replace full code with concise pseudocode or key logic snippets
- Move complete implementations to detailed specs
- Use consistent verb tense (imperative: "extract", "validate", "generate")

**5. Diagrams**
- Consolidate redundant diagrams
- Keep one primary pipeline diagram (Section 2.1)
- Keep data flow diagram (Section 2.3)
- Keep one three-node pattern diagram
- Remove duplicate/similar diagrams

### Terminology Improvements

Use precise, consistent terminology throughout:

| Current/Imprecise | Precise/Preferred |
|------------------|-------------------|
| "AI-driven steps" | "AI-orchestrated steps" or "LLM-mediated steps" |
| "Traditional programming" | "Deterministic processing" or "Procedural code" |
| "Generate (LLM)" | "Generation node (LLM)" |
| "Validate (Python)" | "Validation node (Python)" |
| "Review (Human)" | "Review node (Human)" |
| "new_metadata" | "updated_metadata" (use consistently) |
| "Task-specific states" | "Task-scoped state views" |
| "total=False" explanation | "Optional field specification" |
| "interrupt" | "LangGraph interrupt mechanism" |

### Formatting Requirements

- Use Markdown for all formatting
- Code blocks with language specification (```python, ```mermaid)
- Tables for structured data
- Consistent heading levels (## for main sections, ### for subsections)
- No version numbers, dates, or author attributions (Git is source of truth)

## Deliverables

1. **`docs/SURVEY_ANALYSIS_WORKFLOW_DESIGN.md`** (replaced with concise version)
   - ~1,200-1,500 lines
   - Scannable, focused on architecture and workflow
   - References detailed specs document

2. **`docs/SURVEY_ANALYSIS_DETAILED_SPECIFICATIONS.md`** (new file)
   - All verbose implementation details
   - Complete code examples
   - Full prompt templates
   - Detailed validation specifications

3. **`docs/SURVEY_ANALYSIS_WORKFLOW_DESIGN.md.backup`** (backup of original)
   - Original 3,238-line document preserved

## Constraints

1. **MUST preserve Section 2.3 content** - Data Flow Diagram must remain unchanged
2. **MUST use precise terminology** - Consistent, technical language throughout
3. **MUST maintain semantic equivalence** - No information loss, only reorganization
4. **MUST follow project conventions** - No version numbers, dates, or author attributions
5. **MUST ensure cross-references work** - Links between concise and detailed documents
6. **SHOULD maintain mermaid diagrams** - Keep all visual representations
7. **SHOULD keep table structures** - Phase descriptions, state evolution, etc.

## Success Criteria

1. [ ] Concise document is 50-60% of original length (~1,200-1,500 lines)
2. [ ] Section 2.3 (Data Flow Diagram) content is unchanged
3. [ ] All verbose content exists in detailed specifications document
4. [ ] Cross-references between documents work correctly
5. [ ] Terminology is precise and consistent throughout
6. [ ] No information loss - all original content preserved
7. [ ] Document structure matches requirements specification
8. [ ] Three-node pattern is prominent as architectural pattern
9. [ ] State management is streamlined without losing clarity
10. [ ] Code examples are pseudocode in concise, full implementations in detailed

## Worker Investigation Instructions

[CRITICAL] You MUST do your own deep investigation before implementing:

**1. Read the complete source document**:
   - `docs/SURVEY_ANALYSIS_WORKFLOW_DESIGN.md` (all 3,238 lines)
   - Identify ALL areas of repetition
   - Map ALL code examples that should move to detailed specs
   - Note ALL diagrams and their purposes

**2. Understand current terminology**:
   - Grep for inconsistent terminology: grep -n "AI-driven\|LLM\|traditional" docs/SURVEY_ANALYSIS_WORKFLOW_DESIGN.md
   - Identify all instances of imprecise language
   - Create terminology mapping before making changes

**3. Analyze document structure**:
   - Create outline of current sections with line counts
   - Identify which sections contribute most to verbosity
   - Map content flow between sections (dependencies, cross-references)

**4. Identify all diagrams**:
   - List all mermaid diagrams with their purposes
   - Identify redundant/similar diagrams that could be consolidated
   - Ensure section 2.3 diagram is marked as "keep intact"

**5. Plan content migration**:
   - Create mapping: current section -> concise section OR detailed specs section
   - Identify cross-references that will need updating
   - Plan how to handle "see detailed specs" references

**6. Verify backup strategy**:
   - Ensure original document is backed up before modification
   - Confirm backup location and naming convention

**7. Before writing**:
   - Review this job document completely
   - Ask clarifying questions if anything is unclear
   - Only begin writing when you have complete understanding
