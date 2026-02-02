# LangGraph Survey Analysis Workflow

Implementation of the LangGraph three-node pattern for AI-powered survey data processing.

## Overview

This workflow implements LangGraph's explicit node pattern (no factory functions) for three AI processing steps in the survey analysis pipeline:

1. **Step 4**: Generate Recoding Rules
2. **Step 8**: Generate Indicators
3. **Step 9**: Generate Table Specifications

Each step follows the same three-node pattern:

```
Generate (LLM) → Validate (Python) → Review (Human, optional)
     ↑                                           │
     └─────────────── Retry on failure ──────────┘
```

## Directory Structure

```
workflow/
├── __init__.py           # Package exports
├── state.py              # Unified state definition
├── graph.py              # Main LangGraph workflow construction
├── prompts.py            # Prompt builders for all tasks
├── nodes/                # Node implementations
│   ├── __init__.py
│   ├── recoding.py       # Step 4 nodes
│   ├── indicators.py     # Step 8 nodes
│   └── table_specs.py    # Step 9 nodes
├── validators/           # Python validation logic
│   ├── __init__.py
│   ├── recoding.py       # Recoding rules validator (7 checks)
│   ├── indicators.py     # Indicators validator (5 checks)
│   └── table_specs.py    # Table specs validator (6 checks)
├── tests/                # Unit tests
│   ├── __init__.py
│   └── test_validators.py
└── example.py            # Usage examples
```

## Key Features

### 1. Three-Node Pattern

Each AI task uses three explicit nodes:

- **Generate Node**: LLM creates output based on metadata and feedback
- **Validate Node**: Python validator checks for structural correctness
- **Review Node**: Human review via LangGraph's `interrupt()` (optional)

### 2. Conditional Routing

Conditional edges control flow between nodes:

- After validation: Route to review (if valid) or retry generation
- After review: Route to END (if approved) or retry generation
- Max iterations = 3 to prevent infinite loops

### 3. Feedback Tracking

State tracks feedback source to build appropriate retry prompts:

- `validation`: Validation errors → technical retry
- `human`: Human rejection → semantic refinement

### 4. Validators

Python-based validation for each task:

**RecodingValidator** (7 checks):
1. Source variables exist
2. Target variable conflicts
3. Range validity
4. No duplicate targets
5. Transformation completeness
6. Target value uniqueness
7. Source value overlap

**IndicatorValidator** (5 checks):
1. Variables exist
2. Metric valid (average, percentage, distribution)
3. No duplicate IDs
4. Variables not empty
5. Variable type matches metric

**TableSpecsValidator** (6 checks):
1. Indicator IDs exist
2. No overlap between rows and columns
3. Weighting variable exists
4. Sorting valid
5. Cramer's V in range [0, 1]
6. Count min > 0

### 5. Prompt Builders

Context-aware prompt generation:

- Initial prompts: First generation
- Validation retry prompts: Include validation errors
- Human feedback prompts: Include human rejection comments

## Usage

### Basic Example

```python
from workflow import create_initial_state, create_workflow

# Create initial state
state = create_initial_state(
    spss_file_path="data/survey.sav",
    config={
        "auto_approve_recoding": True,  # Skip human review
        "max_iterations": 3
    }
)

# Add metadata (normally from Steps 1-3)
state["filtered_metadata"] = [...]

# Create and run workflow
app = create_workflow()
result = app.invoke(state)
```

### With Human Review

```python
# Disable auto-approval for human-in-the-loop
state = create_initial_state(
    spss_file_path="data/survey.sav",
    config={
        "auto_approve_recoding": False,
        "auto_approve_indicators": False,
        "auto_approve_table_specs": False
    }
)

app = create_workflow()

# Stream workflow and handle interrupts
for event in app.stream(state):
    if "__interrupt__" in event:
        # Get human decision
        decision = get_human_input(event["__interrupt__"])
        # Resume with decision
        state = app.resume(state, decision)
```

### Run Examples

```bash
# Auto-approval mode
python workflow/example.py auto

# Human review mode
python workflow/example.py human

# Show validation retry logic
python workflow/example.py retry
```

### Run Tests

```bash
# Run all validator tests
pytest workflow/tests/test_validators.py -v

# Run specific test class
pytest workflow/tests/test_validators.py::TestRecodingValidator -v
```

## State Fields

The unified state includes:

```python
class State(TypedDict):
    # Core workflow state
    messages: Annotated[list, add_messages]
    config: Dict[str, Any]

    # Step 4: Recoding Rules
    recoding_rules: Optional[Dict[str, Any]]
    recoding_validation: Optional[Dict[str, Any]]
    recoding_feedback: Optional[Dict[str, Any]]
    recoding_iteration: int
    recoding_feedback_source: Optional[Literal["validation", "human"]]
    recoding_rules_approved: bool

    # Step 8: Indicators
    indicators: Optional[Dict[str, Any]]
    indicators_validation: Optional[Dict[str, Any]]
    indicators_feedback: Optional[Dict[str, Any]]
    indicators_iteration: int
    indicators_feedback_source: Optional[Literal["validation", "human"]]
    indicators_approved: bool

    # Step 9: Table Specifications
    table_specifications: Optional[Dict[str, Any]]
    table_specs_validation: Optional[Dict[str, Any]]
    table_specs_feedback: Optional[Dict[str, Any]]
    table_specs_iteration: int
    table_specs_feedback_source: Optional[Literal["validation", "human"]]
    table_specs_approved: bool

    # ... (other fields for full workflow)
```

## Implementation Notes

### Explicit Node Pattern

The workflow uses LangGraph's explicit pattern (no factory functions):

```python
workflow = StateGraph(State)

# Add nodes explicitly
workflow.add_node("generate_recoding", generate_recoding)
workflow.add_node("validate_recoding", validate_recoding)
workflow.add_node("review_recoding", review_recoding)

# Add edges explicitly
workflow.add_edge("generate_recoding", "validate_recoding")
workflow.add_conditional_edges(
    "validate_recoding",
    after_recoding_validation,
    {"review_recoding": "review_recoding", "generate_recoding": "generate_recoding"}
)
```

### Mock LLM Responses

Current implementation uses mock LLM responses for testing. Replace `_mock_llm_response()` functions with actual LLM calls:

```python
# In nodes/recoding.py, nodes/indicators.py, nodes/table_specs.py
# Replace:
response = _mock_llm_response(prompt)

# With:
response = llm_client.invoke(prompt)
```

### Connecting to Full Workflow

These three-node patterns are designed to integrate with the full survey analysis workflow. In the complete implementation:

- Step 4 (recoding) connects after Step 3 (preliminary filtering)
- Step 8 (indicators) connects after Step 7 (PSPP recoding execution)
- Step 9 (table specs) connects after Step 8 (indicators approval)

## Dependencies

- LangGraph for workflow orchestration
- Pydantic for data validation (used by validators)
- pytest for testing

Install with:

```bash
pip install langgraph pydantic pytest
```

## Design Documents

See the main design document:
- `SURVEY_ANALYSIS_WORKFLOW_DESIGN.md` - Full workflow specification

## Success Criteria

✅ All three AI tasks use the three-node pattern
✅ Each node is a separate, testable function
✅ Conditional edges route correctly based on state
✅ Human review via `interrupt()` works
✅ Validation catches all specified error conditions
✅ Retry logic respects max_iterations = 3
✅ Prompts include appropriate feedback based on source
✅ Workflow can be compiled and invoked end-to-end
