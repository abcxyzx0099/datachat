# Survey Analysis Workflow - Task Tracking

> Task tracking document for the Survey Analysis & Visualization Workflow implementation using LangGraph.

**Project**: SPSS Survey Data Analyzer
**Reference Documents**:
- [Workflow Architecture](./workflow-architecture.md)
- [Implementation Specifications](./implementation-specifications.md)
- [Project Structure](./project-structure.md)
**Created**: 2026-01-31

---

## Task Overview

| ID | Task | Stage | Steps | Status |
|----|------|-------|-------|--------|
| 1 | Set up project structure and configuration | Setup | - | pending |
| 2 | Implement state management with TypedDict definitions | Setup | - | pending |
| 3 | Implement Stage 1 nodes - Data Preparation (Steps 1-3) | Stage 1 | Steps 1-3 | pending |
| 4 | Implement Stage 1 nodes - Recoding Three-Node Pattern (Steps 4-6) | Stage 1 | Steps 4-6 | pending |
| 5 | Implement Stage 1 nodes - PSPP Recoding Execution (Steps 7-8) | Stage 1 | Steps 7-8 | pending |
| 6 | Implement conditional edge routing functions for Stage 1 | Stage 1 | Edges | pending |
| 7 | Implement Stage 2 nodes - Indicator Generation (Steps 9-11) | Stage 2 | Steps 9-11 | pending |
| 8 | Implement Stage 2 nodes - Cross-Table Specification (Steps 12-14) | Stage 2 | Steps 12-14 | pending |
| 9 | Implement Stage 2 nodes - PSPP Table Execution (Steps 15-16) | Stage 2 | Steps 15-16 | pending |
| 10 | Implement Stage 2 nodes - Statistical Analysis (Steps 17-18) | Stage 2 | Steps 17-18 | pending |
| 11 | Implement Stage 2 nodes - Filtering (Steps 19-20) | Stage 2 | Steps 19-20 | pending |
| 12 | Implement Stage 3 nodes - Presentation Generation (Steps 21-22) | Stage 3 | Steps 21-22 | pending |
| 13 | Implement main LangGraph workflow graph | Graph | - | pending |
| 14 | Implement error handling and logging infrastructure | Infrastructure | - | pending |
| 15 | Create configuration and environment setup | Config | - | pending |
| 16 | Write end-to-end integration tests | Testing | - | pending |

---

## Detailed Tasks

### Task 1: Set up project structure and configuration

**Status**: pending

Create the project structure for the LangGraph-based survey analysis workflow.

**Directory Structure**:

See [project-structure.md](./project-structure.md) for the complete project directory structure and file organization.

**Key directories for this task**:
- `agent/` - Application code with nodes, utils, validation, llm modules
- `config/` - Configuration files (langgraph.json, default.py)
- `output/` - Generated outputs (logs, reviews, temp files)

**Requirements**:
- Create all directories with `__init__.py` where needed
- Set up `langgraph.json` with all 22 nodes mapped to `agent.nodes:*`
- Set up DEFAULT_CONFIG in `config/default.py` with LLM, PSPP, and validation settings

---

### Task 2: Implement state management with TypedDict definitions

**Status**: pending

Create `agent/state.py` with all TypedDict state classes as specified in implementation-specifications.md.

**Required Classes**:
- `InputState` - Initial input configuration (spss_file_path, config)
- `ExtractionState` - Steps 1-3 data extraction fields
- `RecodingState` - Steps 4-8 recoding with three-node pattern fields
- `IndicatorState` - Steps 9-11 indicator generation
- `CrossTableState` - Steps 12-16 cross-table specification
- `StatisticalAnalysisState` - Steps 17-18 statistics
- `FilteringState` - Steps 19-20 filtering
- `PresentationState` - Steps 21-22 outputs
- `ApprovalState` - Human-in-the-loop tracking
- `TrackingState` - Execution logs and errors

**Final Combined State**:
- `WorkflowState` - Inherits all sub-states with `total=False`

**Reference**: `docs/implementation-specifications.md` section 1.1

---

### Task 3: Implement Stage 1 nodes - Data Preparation (Steps 1-3)

**Status**: pending

Implement deterministic processing nodes for data extraction and preparation in `agent/nodes.py`.

**Step 1: extract_spss_node**
- Use `pyreadstat.read_sav()` to extract .sav file
- Store `raw_data` (DataFrame) and `original_metadata`

**Step 2: transform_metadata_node**
- Convert section-based metadata to variable-centered format
- Create variable objects with name, label, type, values

**Step 3: filter_metadata_node**
- Apply filtering rules (binary, high cardinality, other text)
- Use config: `cardinality_threshold`, `filter_binary`, `filter_other_text`
- Store `filtered_metadata` and `filtered_out_variables`

**Acceptance Criteria**:
- All nodes accept `WorkflowState` and return `WorkflowState`
- Execution logging to `state["execution_log"]`

---

### Task 4: Implement Stage 1 nodes - Recoding with Three-Node Pattern (Steps 4-6)

**Status**: pending

Implement the Generate → Validate → Review pattern for recoding rules.

**Step 4: generate_recoding_rules_node (LLM)**
- Build prompt based on feedback source (initial/validation retry/human)
- Invoke LLM with `filtered_metadata`
- Generate `recoding_rules` JSON structure
- Increment `recoding_iteration`

**Step 5: validate_recoding_rules_node (Python)**
- Syntax validation: JSON structure, required fields
- Reference validation: variable names exist in metadata
- Type validation: recoded types match sources
- Constraint validation: value ranges, logical consistency
- Store `recoding_validation` with errors/warnings

**Step 6: review_recoding_rules_node (Human)**
- Format review document (artifact + validation + context)
- Trigger LangGraph interrupt mechanism
- Wait for human approval/rejection
- Store `recoding_approved` and `recoding_feedback`

**Reference**: `docs/implementation-specifications.md` sections for prompts and validation specs

---

### Task 5: Implement Stage 1 nodes - PSPP Recoding Execution (Steps 7-8)

**Status**: pending

Implement PSPP syntax generation and execution for dataset creation.

**Step 7: generate_pspp_recoding_syntax_node**
- Parse validated `recoding_rules` JSON
- Generate PSPP RECODE commands for each variable
- Add variable labels and value labels
- Write to .sps file
- Store `pspp_recoding_syntax` and `pspp_recoding_syntax_path`

**Step 8: execute_pspp_recoding_node**
- Construct PSPP commands:
  - GET FILE original .sav
  - INSERT FILE recoding syntax
  - SAVE OUTFILE new_data.sav
- Execute via subprocess
- Extract metadata from new_data.sav using pyreadstat
- Store `new_data_path` and `new_metadata` (ALL variables - authoritative source)

**Acceptance Criteria**:
- `new_metadata` contains complete variable list (original + recoded)
- Error handling for PSPP failures

---

### Task 6: Implement conditional edge routing functions for Stage 1

**Status**: pending

Create conditional routing functions in `agent/edges.py` for the three-node patterns.

**Functions Required**:

1. `should_retry_recoding(state)` - Routes after `validate_recoding_rules`
   - If invalid AND iteration < max: return `"generate_recoding_rules"`
   - If invalid AND iteration >= max: return `"continue_with_warning"`
   - If valid: return `"review_recoding_rules"`

2. `should_approve_recoding(state)` - Routes after `review_recoding_rules`
   - If approved: return `"generate_pspp_recoding_syntax"`
   - If rejected: return `"generate_recoding_rules"` (with feedback)

3. Same pattern for:
   - `should_retry_indicators` / `should_approve_indicators`
   - `should_retry_table_specs` / `should_approve_table_specs`

**Configuration**:
- Respect `state["config"]["max_self_correction_iterations"]`
- Track `state["recoding_feedback_source"]` as `"validation"` or `"human"`

---

### Task 7: Implement Stage 2 nodes - Indicator Generation (Steps 9-11)

**Status**: pending

Implement three-node pattern for indicator generation.

**Step 9: generate_indicators_node (LLM)**
- Build prompt with `new_metadata` (complete variable list)
- Generate semantic groupings of variables into indicators
- Parse response into indicator structure: `[{name, variables, description}]`
- Increment `indicators_iteration`

**Step 10: validate_indicators_node (Python)**
- Structure validation: required fields (name, variables, description)
- Reference validation: all variables exist in `new_metadata`
- Uniqueness validation: indicator names are unique
- Non-empty validation: each indicator has >= 2 variables
- Store `indicators_validation`

**Step 11: review_indicators_node (Human)**
- Format review document with indicators, validation, variable context
- Trigger LangGraph interrupt
- Store `indicators_approved` and `indicators_feedback`

---

### Task 8: Implement Stage 2 nodes - Cross-Table Specification (Steps 12-14)

**Status**: pending

Implement three-node pattern for cross-table specifications.

**Step 12: generate_table_specifications_node (LLM)**
- Build prompt with `new_metadata`, indicators, and table requirements
- Generate table definitions: `[{name, rows, columns, weight, statistics}]`
- Increment `table_specs_iteration`

**Step 13: validate_table_specifications_node (Python)**
- Structure validation: required fields
- Reference validation: row/column variables exist in `new_metadata`
- Statistics validation: requested statistics are valid
- Type validation: row/column are categorical
- Store `table_specs_validation`

**Step 14: review_table_specifications_node (Human)**
- Format review document
- Trigger LangGraph interrupt
- Store `table_specs_approved` and `table_specs_feedback`

---

### Task 9: Implement Stage 2 nodes - PSPP Table Execution (Steps 15-16)

**Status**: pending

Implement PSPP cross-table generation.

**Step 15: generate_pspp_table_syntax_node**
- Parse validated `table_specifications`
- Generate PSPP CTABLES syntax for each table
- Handle nested variables, weighting, statistics
- Write to .sps file
- Store `pspp_table_syntax` and `pspp_table_syntax_path`

**Step 16: execute_pspp_tables_node**
- Construct PSPP commands with CTABLES and EXPORT
- Execute via subprocess
- Verify output files created
- Store `cross_table_csv_path` and `cross_table_json_path`

**Output Files**:
- CSV with cross-tabulation data
- JSON with table metadata

---

### Task 10: Implement Stage 2 nodes - Statistical Analysis (Steps 17-18)

**Status**: pending

Implement Chi-square statistics computation.

**Step 17: generate_python_statistics_script_node**
- Parse `table_specifications` to identify contingency tables
- Generate Python script that:
  - Loads cross_table data from JSON
  - Iterates through each table
  - Computes `scipy.stats.chi2_contingency`
  - Computes Cramer's V effect size
  - Exports to `statistical_analysis_summary.json`
- Write to .py file
- Store `python_stats_script_path`

**Step 18: execute_python_statistics_script_node**
- Execute `python_stats_script.py` via subprocess
- Load generated `statistical_analysis_summary.json`
- Store in `state["statistical_summary"]`

**Output Structure**:
```python
[{table_name, chi_square, p_value, degrees_of_freedom, cramers_v, interpretation}]
```

---

### Task 11: Implement Stage 2 nodes - Filtering (Steps 19-20)

**Status**: pending

Implement significant table filtering.

**Step 19: generate_filter_list_node**
- Parse `statistical_summary`
- Apply significance criteria:
  - p-value < 0.05
  - Cramer's V >= 0.1
  - Cell count >= 10
- Generate `filter_list`: `[{table_name, pass, criteria}]`
- Save to JSON
- Store `filter_list_json_path`

**Step 20: apply_filter_to_tables_node**
- Load `filter_list` and `cross_table` data
- Filter tables where `pass = True`
- Retain both CSV data and JSON metadata for passing tables
- Save filtered results
- Store `significant_tables` and `significant_tables_json_path`

**Purpose**:
- `significant_tables` used for PowerPoint (Step 21)
- All `cross_tables` used for HTML dashboard (Step 22)

---

### Task 12: Implement Stage 3 nodes - Presentation Generation (Steps 21-22)

**Status**: pending

Implement final output generation.

**Step 21: generate_powerpoint_node**
- Load `significant_tables` and `statistical_summary`
- Create PowerPoint presentation using python-pptx:
  - Title slide with analysis summary
  - For each table: slide with chart, table, statistics
- Store `powerpoint_path` and `charts_generated`

**Step 22: generate_html_dashboard_node**
- Load ALL cross_table data (not just significant)
- Generate HTML with:
  - Navigation sidebar with table list
  - Interactive tables with sorting/filtering
  - Charts using Chart.js
  - Statistical annotations
- Embed CSS for styling
- Store `html_dashboard_path`

**Acceptance Criteria**:
- PowerPoint contains only significant tables
- HTML dashboard contains all tables

---

### Task 13: Implement main LangGraph workflow graph

**Status**: pending

Create `agent/graph.py` with the complete workflow graph.

**Graph Structure**:
- Define all 22 nodes
- Define linear edges for deterministic flow
- Define conditional edges for three-node patterns
- Configure checkpointing for resumable execution

**Required Functions**:

1. `create_survey_analysis_graph()` - Returns StateGraph
   - Add all 22 nodes
   - Add edges: `extract_spss` → `transform_metadata` → `filter_metadata`
   - Add conditional edges for validation/review loops
   - Compile with checkpointer

2. Node implementations imported from `agent.nodes`
3. Edge functions imported from `agent.edges`

**Checkpointing**:
- Support SqliteSaver for persistence
- Enable resume after human interrupt

**Reference**: `docs/workflow-architecture.md` section 6 (LangGraph Configuration)

---

### Task 14: Implement error handling and logging infrastructure

**Status**: pending

Add comprehensive error handling and logging across all nodes.

**Error Categories**:
- LLM Errors: Rate limits, API failures - retry with exponential backoff
- Validation Errors: Automatic retry up to max_iterations
- PSPP Errors: Parse output logs, provide specific error messages
- File I/O Errors: Validate paths, fail gracefully
- Statistical Errors: Warn and continue

**Logging Implementation**:
- All nodes log to `state["execution_log"]`
- Store errors in `state["errors"]`
- Store warnings in `state["warnings"]`
- Write logs to `output/logs/` with timestamps

**Helper Functions**:
- `log_step(state, step_name, message, level="info")`
- `handle_error(state, error, context)`
- `parse_pspp_errors(pspp_output)`

**Acceptance Criteria**:
- No silent failures
- All errors logged with context
- Graceful degradation where possible

---

### Task 15: Create configuration and environment setup

**Status**: pending

Set up project configuration and dependencies.

**config/default.py**:
```python
DEFAULT_CONFIG = {
    # LLM Configuration
    "model": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 2000,

    # Three-Node Pattern Configuration
    "max_self_correction_iterations": 3,
    "enable_human_review": True,

    # Step 3: Preliminary Filtering Configuration
    "cardinality_threshold": 30,
    "filter_binary": True,
    "filter_other_text": True,

    # PSPP Configuration
    "pspp_path": "/usr/bin/pspp",
    "pspp_output_path": "output/pspp_logs.txt",

    # File Paths
    "output_dir": "output",
    "temp_dir": "temp",

    # Statistical Analysis
    "significance_level": 0.05,
    "min_cramers_v": 0.1,
    "min_cell_count": 10,

    # Presentation
    "powerpoint_template": None,
    "html_theme": "default"
}
```

**requirements.txt**:
```
langgraph
langchain-openai
pyreadstat
pandas
scipy
python-pptx
```

**config/langgraph.json**:
- Graph configuration with all 22 nodes
- Edges and conditional_edges mappings
- Reference `agent.nodes:` and `agent.edges:`

---

### Task 16: Write end-to-end integration tests

**Status**: pending

Create comprehensive tests for the workflow.

**Test Structure**:
```
tests/
├── __init__.py
├── test_state.py           # TypedDict validation
├── test_nodes.py           # Individual node tests
├── test_edges.py           # Conditional routing tests
├── test_graph.py           # End-to-end workflow test
└── fixtures/
    └── sample_data.sav     # Sample SPSS file for testing
```

**Test Coverage**:
- State evolution through all 22 steps
- Three-node pattern iteration logic
- Validation with various error scenarios
- Human interrupt/resume mechanism
- PSPP syntax generation accuracy
- Statistical calculation correctness

**Acceptance Criteria**:
- All nodes have unit tests
- Full workflow runs with sample data
- Human review flow tested
- Error recovery tested

---

## Progress Summary

| Stage | Tasks | Completed | Pending |
|-------|-------|-----------|---------|
| Setup | 3 | 0 | 3 |
| Stage 1 (Data Preparation) | 4 | 0 | 4 |
| Stage 2 (Analysis) | 5 | 0 | 5 |
| Stage 3 (Reporting) | 1 | 0 | 1 |
| Graph | 1 | 0 | 1 |
| Infrastructure | 1 | 0 | 1 |
| Config | 1 | 0 | 1 |
| Testing | 1 | 0 | 1 |
| **Total** | **16** | **0** | **16** |

---

## Notes

- Update task status by changing `**Status**: pending` to `**Status**: in_progress` or `**Status**: completed`
- Update the Progress Summary table as tasks are completed
- Add implementation notes or blockers to task descriptions as needed
- Reference the implementation specifications document for detailed code examples
