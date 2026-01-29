# Task: Implement LangGraph Three-Node Pattern for AI Processing

**Status**: pending

---

## Task

Implement the explicit LangGraph three-node pattern (Generate → Validate → Review) for the three AI processing steps in the survey analysis workflow.

## Context

The design document (`SURVEY_ANALYSIS_WORKFLOW_DESIGN.md`) was updated to use LangGraph's explicit pattern instead of a factory function approach. The three AI processing steps (Steps 4, 8, and 9) each use a three-node pattern:

1. **Step 4**: Generate Recoding Rules
2. **Step 8**: Generate Indicators
3. **Step 9**: Generate Table Specifications

Each step follows the same pattern:
- **Node 1**: Generate (LLM creates output)
- **Node 2**: Validate (Python validates output)
- **Node 3**: Review (Human optional review via `interrupt()`)
- **Edge 1**: After validation - route to review or retry based on validation result
- **Edge 2**: After review - route to END or retry based on human decision

The existing `survey_analysis/` directory has partial implementations (validators, models, recoding_agent) that used a combined agent approach. These need to be refactored into separate nodes.

## Scope

- **Directories**:
  - `survey_analysis/` - Existing implementation to refactor
  - `workflow/` - New directory for LangGraph workflow implementation (create if needed)

- **Files to Create**:
  - `workflow/__init__.py`
  - `workflow/state.py` - State definitions
  - `workflow/nodes/recoding.py` - Step 4 nodes (generate, validate, review)
  - `workflow/nodes/indicators.py` - Step 8 nodes (generate, validate, review)
  - `workflow/nodes/table_specs.py` - Step 9 nodes (generate, validate, review)
  - `workflow/graph.py` - Main workflow graph construction
  - `workflow/validators/` - Validators (recoding, indicators, table_specs)

- **Files to Refactor**:
  - `survey_analysis/validators.py` - Extract to `workflow/validators/recoding.py`
  - `survey_analysis/models.py` - Extract relevant models to `workflow/state.py`
  - `survey_analysis/recoding_agent.py` - Refactor logic into separate nodes

- **Dependencies**:
  - LangGraph for workflow orchestration
  - Pydantic for data validation
  - Existing models in `survey_analysis/models.py`

## Requirements

### 1. State Management
Define a unified state class that includes task-specific fields for all three AI processing tasks:

```python
from typing import TypedDict, Literal, Annotated
from langgraph.graph.message import add_messages

class State(TypedDict):
    # Core workflow state
    messages: Annotated[list, add_messages]
    config: dict

    # Shared data
    filtered_metadata: list
    variable_centered_metadata: list
    raw_data: object

    # Step 4: Recoding Rules
    recoding_rules: dict | None
    recoding_validation: dict | None
    recoding_feedback: dict | None
    recoding_iteration: int
    recoding_feedback_source: Literal["validation", "human"] | None

    # Step 8: Indicators
    indicators: dict | None
    indicators_validation: dict | None
    indicators_feedback: dict | None
    indicators_iteration: int
    indicators_feedback_source: Literal["validation", "human"] | None

    # Step 9: Table Specifications
    table_specifications: dict | None
    table_specs_validation: dict | None
    table_specs_feedback: dict | None
    table_specs_iteration: int
    table_specs_feedback_source: Literal["validation", "human"] | None
```

### 2. Node Implementation Pattern

For each of the three tasks (recoding, indicators, table_specs), implement:

**Node 1: Generate**
- Takes state, extracts iteration count and feedback
- Builds prompt based on feedback source (validation or human)
- Calls LLM and parses response
- Returns updated state with output and incremented iteration

**Node 2: Validate**
- Runs Python validator on generated output
- Returns validation result with errors/warnings

**Node 3: Review**
- Uses LangGraph `interrupt()` to pause for human input
- Returns human decision

**Edge Functions**:
- `after_[task]_validation`: Route to review or retry
- `after_[task]_review`: Route to END or retry

### 3. Validators

Implement or extract validators:
- **RecodingValidator**: 7 checks (existing in `survey_analysis/validators.py`)
- **IndicatorValidator**: 5 checks (new)
  - Variables exist
  - Metric valid (average, percentage, distribution)
  - No duplicate IDs
  - Variables not empty
  - Variable type matches metric
- **TableSpecsValidator**: 6 checks (new)
  - Indicator IDs exist
  - No overlap between rows and columns
  - Weighting variable exists
  - Sorting valid
  - Cramer's V in range [0, 1]
  - Count min > 0

### 4. Prompt Builders

Implement prompt builder functions for each task:
- `build_initial_prompt()` - First generation
- `build_validation_retry_prompt()` - After validation failure
- `build_human_feedback_prompt()` - After human rejection

### 5. Graph Construction

Build the LangGraph workflow using explicit pattern:

```python
from langgraph.graph import StateGraph, START, END

workflow = StateGraph(State)

# Add all nodes explicitly
workflow.add_node("generate_recoding", generate_recoding)
workflow.add_node("validate_recoding", validate_recoding)
workflow.add_node("review_recoding", review_recoding)
# ... (all other nodes)

# Add edges explicitly
workflow.add_edge(START, "first_step")
workflow.add_edge("generate_recoding", "validate_recoding")
workflow.add_conditional_edges("validate_recoding", after_recoding_validation)
# ... (all other edges)

app = workflow.compile()
```

## Deliverables

1. **State definition** (`workflow/state.py`) - Unified state class with all task-specific fields
2. **Node implementations** (`workflow/nodes/`) - Separate modules for each task
3. **Validators** (`workflow/validators/`) - Python validation logic
4. **Prompt builders** (`workflow/prompts.py`) - Prompt generation functions
5. **Main graph** (`workflow/graph.py`) - LangGraph workflow construction
6. **Example usage** (`workflow/example.py`) - Demonstrate how to run the workflow
7. **Tests** (`workflow/tests/`) - Unit tests for validators and nodes

## Constraints

1. **Use explicit LangGraph pattern** - No factory functions, define each node explicitly
2. **Follow naming convention** - Nodes: `{task}_{action}` (e.g., `generate_recoding`)
3. **Max iterations = 3** - Prevent infinite loops in retry logic
4. **Use `interrupt()` for human review** - LangGraph's interrupt mechanism
5. **Track feedback source** - Distinguish between validation errors and human feedback
6. **Preserve existing logic** - Refactor from `survey_analysis/` where applicable

## Success Criteria

1. ✅ All three AI tasks use the three-node pattern
2. ✅ Each node is a separate, testable function
3. ✅ Conditional edges route correctly based on state
4. ✅ Human review via `interrupt()` works
5. ✅ Validation catches all specified error conditions
6. ✅ Retry logic respects max_iterations = 3
7. ✅ Prompts include appropriate feedback based on source
8. ✅ Workflow can be compiled and invoked end-to-end

## Worker Investigation Instructions

**CRITICAL**: Before implementing, you MUST:

1. **Read the design document** - `SURVEY_ANALYSIS_WORKFLOW_DESIGN.md` sections for Steps 4, 8, and 9
2. **Examine existing implementations**:
   - `survey_analysis/validators.py` - Understand existing validation logic
   - `survey_analysis/models.py` - Understand data models
   - `survey_analysis/recoding_agent.py` - Understand current approach
3. **Research LangGraph patterns**:
   - Use `mcp__context7__query-docs` with library `/langchain-ai/langgraph`
   - Search for "conditional edges", "interrupt", "explicit node pattern"
4. **Identify ALL edge cases**:
   - What happens when validation fails on iteration 3?
   - What happens when LLM returns invalid JSON?
   - What happens when human provides "modify" feedback?
5. **Plan the directory structure** - Ensure clean separation between tasks
6. **Define the complete state schema** - Include ALL fields before coding

**Investigation commands to run**:
```bash
# Find all relevant files
find survey_analysis -name "*.py" -type f

# Search for LangGraph patterns
# Use context7 MCP as described above
```
