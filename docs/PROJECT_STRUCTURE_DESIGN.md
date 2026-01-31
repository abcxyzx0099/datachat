# Project Structure Design

**Your Request**: "Create a comprehensive project structure design document for the dataflow SPSS Analyzer web application."

This document defines the directory structure, file organization, and module boundaries for the Survey Analysis Workflow Agent project.

---

## Table of Contents

1. [Design Principles](#1-design-principles)
2. [Directory Structure](#2-directory-structure)
3. [Phase-to-File Mapping](#3-phase-to-file-mapping)
4. [File-by-File Specification](#4-file-by-file-specification)
5. [Naming Conventions](#5-naming-conventions)
6. [Implementation Roadmap](#6-implementation-roadmap)
7. [Architectural Decisions](#7-architectural-decisions)
8. [Phase-Step-State Mapping](#8-phase-step-state-mapping)
9. [Design Rationale](#9-design-rationale)

---

## 1. Design Principles

| Principle | Description | Example |
|-----------|-------------|---------|
| **Phase-Based Organization** | Group nodes by workflow phase, not one file per node | Steps 1-3 (Extraction) → `phase1_extraction.py` |
| **State Evolution Alignment** | Files map to state TypedDict evolution | `RecodingState` → `phase2_recoding.py` |
| **Separation of Concerns** | State, nodes, edges, validation, prompts in separate modules | `state.py`, `nodes/`, `edges.py`, `validation/`, `llm/prompts.py` |
| **Single Responsibility** | Each file/module has one clear purpose | `pspp_wrapper.py` only handles PSPP execution |
| **Testability** | Test structure mirrors source structure | `tests/unit/agent/nodes/phase1_*.py` |
| **Scalability** | Structure supports adding new phases/nodes | New phase = new file in `nodes/` |

---

## 2. Directory Structure

```
agent/
├── __init__.py                   # Package exports
├── state.py                      # All TypedDict state definitions
├── config.py                     # Configuration constants, paths, defaults
├── edges.py                      # Conditional routing logic
├── graph.py                      # LangGraph StateGraph construction
│
├── utils/                        # Shared utilities
│   ├── __init__.py
│   ├── pspp_wrapper.py           # PSPP command execution & output parsing
│   ├── file_io.py                # Safe file I/O utilities
│   └── statistics.py             # Statistical computations (Chi-square, Cramer's V)
│
├── validation/                   # Validation functions
│   ├── __init__.py
│   ├── recoding.py               # Recoding rule validation
│   ├── indicators.py             # Indicator definition validation
│   └── tables.py                 # Table specification validation
│
├── llm/                          # LLM-related modules
│   ├── __init__.py
│   ├── prompts.py                # All prompt templates
│   └── clients.py                # LLM client initialization
│
└── nodes/                        # LangGraph node implementations
    ├── __init__.py               # Export all nodes
    ├── phase1_extraction.py      # Steps 1-3: Extract, Transform, Filter
    ├── phase2_recoding.py        # Steps 4-8: Recoding (3-node + PSPP)
    ├── phase3_indicators.py      # Steps 9-11: Indicators (3-node)
    ├── phase4_tables.py          # Steps 12-16: Tables (3-node + PSPP)
    ├── phase5_statistics.py      # Steps 17-18: Chi-square stats
    ├── phase6_filtering.py       # Steps 19-20: Significant tables filter
    ├── phase7_powerpoint.py      # Step 21: PowerPoint generation
    └── phase8_html_dashboard.py  # Step 22: HTML dashboard generation

tests/
├── unit/
│   └── agent/
│       ├── test_state.py
│       ├── test_edges.py
│       ├── test_graph.py
│       ├── nodes/
│       │   ├── test_phase1_extraction.py
│       │   ├── test_phase2_recoding.py
│       │   └── ...
│       └── utils/
│           ├── test_pspp_wrapper.py
│           └── test_statistics.py
│
└── integration/                  # Integration tests
    ├── test_phase1_to_phase2.py
    ├── test_full_workflow.py

temp/                             # Temporary files (one-time scripts, experiments)
├── migration_*.py                # One-time migration scripts (delete after use)
└── test_*.py                     # Experimental test scripts

output/                           # Generated outputs (gitignored)
├── pspp/                         # PSPP output files
├── tables/                       # Generated tables
├── presentations/                # PPTX and HTML files
└── logs/                         # Execution logs

docs/                             # Documentation
├── PROJECT_STRUCTURE_DESIGN.md   # This document
├── WORKFLOW_ARCHITECTURE.md      # Detailed workflow design
└── API_REFERENCE.md              # API documentation
```

---

## 3. Phase-to-File Mapping

Each implementation phase corresponds to one file:

| File | Steps | State Modified | Description |
|------|-------|----------------|-------------|
| `phase1_extraction.py` | 1-3 | `ExtractionState` | Extract .sav, transform metadata, filter variables |
| `phase2_recoding.py` | 4-8 | `RecodingState` | Generate/validate/review recoding rules, PSPP execution |
| `phase3_indicators.py` | 9-11 | `IndicatorState` | Generate/validate/review indicators |
| `phase4_tables.py` | 12-16 | `CrossTableState` | Generate/validate/review table specs, PSPP tables |
| `phase5_statistics.py` | 17-18 | `StatisticalAnalysisState` | Generate/execute Python statistics script |
| `phase6_filtering.py` | 19-20 | `FilteringState` | Generate filter list, apply to tables |
| `phase7_powerpoint.py` | 21 | `PresentationState` | Generate PowerPoint presentation |
| `phase8_html_dashboard.py` | 22 | `PresentationState` | Generate HTML dashboard |

**Benefits**:
- Easy to locate code by workflow step number
- Phase 7 and Phase 8 are separate because they produce different output formats (PPT vs HTML)
- Related operations grouped together (e.g., Generate → Validate → Review)

---

## 4. File-by-File Specification

### 4.1 `agent/__init__.py`

```python
"""
Survey Analysis Workflow Agent Package

This package implements a 22-step LangGraph workflow for automated
survey data analysis and visualization.
"""

# Public API exports
from .state import WorkflowState
from .graph import create_graph, compiled_graph
from .config import DEFAULT_CONFIG, get_output_path

__version__ = "1.0.0"
__all__ = [
    "WorkflowState",
    "create_graph",
    "compiled_graph",
    "DEFAULT_CONFIG",
    "get_output_path",
]
```

### 4.2 `agent/state.py`

**Purpose**: Define all TypedDict state classes.

**Structure**:
```python
"""
WorkflowState Definitions

This module defines all TypedDict classes that comprise the WorkflowState.
Each sub-state represents a functional area of the workflow.
"""

from typing import TypedDict, List, Dict, Any, Optional
from pandas import DataFrame

# Sub-state classes (one per functional area)
class InputState(TypedDict):
    """Initial input parameters (Step 0)"""
    spss_file_path: str
    metadata_file_path: str

class ExtractionState(TypedDict):
    """Phase 1: Steps 1-3 outputs"""
    raw_data: DataFrame
    filtered_metadata: Dict[str, Any]

class RecodingState(TypedDict):
    """Phase 2: Steps 4-8 outputs"""
    recoding_rules: List[Dict[str, Any]]
    new_data_path: str
    new_metadata_path: str

class IndicatorState(TypedDict):
    """Phase 3: Steps 9-11 outputs"""
    indicator_definitions: List[Dict[str, Any]]

class CrossTableState(TypedDict):
    """Phase 4: Steps 12-16 outputs"""
    table_specifications: List[Dict[str, Any]]
    generated_tables: List[Dict[str, Any]]

class StatisticalAnalysisState(TypedDict):
    """Phase 5: Steps 17-18 outputs"""
    statistics_script_path: str
    statistics_results: Dict[str, Any]

class FilteringState(TypedDict):
    """Phase 6: Steps 19-20 outputs"""
    filter_list: List[str]
    significant_tables: List[Dict[str, Any]]

class PresentationState(TypedDict):
    """Phase 7-8: Steps 21-22 outputs"""
    powerpoint_path: Optional[str]
    html_dashboard_path: Optional[str]

# Main workflow state (union of all sub-states)
class WorkflowState(InputState,
                    ExtractionState,
                    RecodingState,
                    IndicatorState,
                    CrossTableState,
                    StatisticalAnalysisState,
                    FilteringState,
                    PresentationState):
    """Complete workflow state for LangGraph"""
    # Control fields
    current_step: int
    iteration_count: int
    validation_errors: List[str]
```

### 4.3 `agent/config.py`

**Purpose**: Centralized configuration management.

```python
"""Configuration constants and settings."""

from pathlib import Path
from typing import Dict

# Directory paths
BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / "output"
PSPP_OUTPUT_DIR = OUTPUT_DIR / "pspp"
TABLES_DIR = OUTPUT_DIR / "tables"
PRESENTATIONS_DIR = OUTPUT_DIR / "presentations"
LOGS_DIR = OUTPUT_DIR / "logs"

# PSPP configuration
PSPP_PATH = "/usr/bin/pspp"
PSPP_OUTPUT_FORMAT = "csv"

# LLM configuration
DEFAULT_MODEL = "claude-3-5-sonnet-20241022"
MAX_TOKENS = 4096
TEMPERATURE = 0.0

# Validation thresholds
CHI_SQUARED_ALPHA = 0.05
CRAMERS_V_THRESHOLD = 0.1

DEFAULT_CONFIG: Dict[str, Any] = {
    "pspp_path": PSPP_PATH,
    "model": DEFAULT_MODEL,
    "max_tokens": MAX_TOKENS,
    "temperature": TEMPERATURE,
    "chi_squared_alpha": CHI_SQUARED_ALPHA,
    "cramers_v_threshold": CRAMERS_V_THRESHOLD,
}

def get_output_path(filename: str, subdir: Path = OUTPUT_DIR) -> Path:
    """Get full output path for a file."""
    return subdir / filename
```

### 4.4 `agent/edges.py`

**Purpose**: Conditional routing between workflow phases.

```python
"""Conditional routing logic for workflow transitions."""

from typing import Literal
from .state import WorkflowState

def should_continue_validation(state: WorkflowState) -> Literal["validate", "proceed"]:
    """Determine if validation should iterate or proceed."""
    if state.get("validation_errors"):
        return "validate"
    return "proceed"

def route_after_recoding(state: WorkflowState) -> Literal["phase3_indicators", "phase2_recoding"]:
    """Route after recoding phase based on validation results."""
    if state.get("iteration_count", 0) > 3:
        # Max iterations reached, proceed anyway
        return "phase3_indicators"
    if state.get("validation_errors"):
        return "phase2_recoding"
    return "phase3_indicators"
```

### 4.5 `agent/graph.py`

**Purpose**: LangGraph StateGraph construction and compilation.

```python
"""LangGraph workflow construction."""

from langgraph.graph import StateGraph, END
from .state import WorkflowState
from .edges import route_after_recoding, should_continue_validation
from .nodes import (
    # Phase 1
    extract_spss_node,
    transform_metadata_node,
    filter_metadata_node,
    # Phase 2
    generate_recoding_rules_node,
    validate_recoding_rules_node,
    review_recoding_rules_node,
    execute_recoding_node,
    # ... all other nodes
)

def create_graph() -> StateGraph:
    """Construct the workflow graph."""
    graph = StateGraph(WorkflowState)

    # Add all nodes
    graph.add_node("extract_spss", extract_spss_node)
    graph.add_node("transform_metadata", transform_metadata_node)
    # ... add all nodes

    # Define edges
    graph.set_entry_point("extract_spss")
    graph.add_edge("extract_spss", "transform_metadata")
    # ... add all edges

    return graph.compile()

# Compiled graph for execution
compiled_graph = create_graph().compile()
```

### 4.6 `agent/nodes/phase1_extraction.py`

```python
"""
Phase 1: Extraction & Preparation (Steps 1-3)

Implements the first three workflow steps:
- Step 1: Extract .sav file
- Step 2: Transform metadata
- Step 3: Filter metadata
"""

from typing import Dict, Any
from pandas import DataFrame
from ..state import WorkflowState
from ..utils.pspp_wrapper import PSPPWrapper

# Step 1: Extract .sav file
def extract_spss_node(state: WorkflowState) -> WorkflowState:
    """Extract SPSS .sav file to CSV format."""
    pspp = PSPPWrapper()
    output_path = pspp.convert_to_csv(state["spss_file_path"])
    state["raw_data_path"] = str(output_path)
    state["current_step"] = 1
    return state

# Step 2: Transform metadata
def transform_metadata_node(state: WorkflowState) -> WorkflowState:
    """Transform metadata to internal format."""
    # Implementation...
    state["current_step"] = 2
    return state

# Step 3: Filter metadata
def filter_metadata_node(state: WorkflowState) -> WorkflowState:
    """Filter metadata based on criteria."""
    # Implementation...
    state["current_step"] = 3
    return state
```

### 4.7 `agent/validation/recoding.py`

**Purpose**: Recoding rule validation logic.

```python
"""Recoding rule validation functions."""

from typing import List, Dict, Any

def validate_recoding_rules(rules: List[Dict[str, Any]]) -> List[str]:
    """
    Validate recoding rules for common errors.

    Returns list of error messages (empty if valid).
    """
    errors = []

    for rule in rules:
        # Check required fields
        if "variable" not in rule:
            errors.append(f"Rule missing 'variable' field: {rule}")
        if "mappings" not in rule:
            errors.append(f"Rule missing 'mappings' field: {rule}")

        # Check for overlapping value ranges
        # ... additional validation logic

    return errors

def check_recoding_syntax(rule: Dict[str, Any]) -> List[str]:
    """Check PSPP recoding syntax."""
    # Implementation...
    return []
```

### 4.8 `agent/llm/prompts.py`

**Purpose**: All LLM prompt templates.

```python
"""LLM prompt templates for workflow nodes."""

from typing import Dict, Any

# Phase 2: Recoding
RECODING_GENERATION_PROMPT = """
You are a statistical analysis expert. Generate recoding rules for the following variables:

Variables: {variables}
Metadata: {metadata}

Generate recoding rules that:
1. Combine appropriate categories
2. Handle missing values
3. Create meaningful derived variables

Output format: JSON list of recoding rules.
"""

RECODING_VALIDATION_PROMPT = """
Review the following recoding rules for statistical validity:

Rules: {rules}

Check for:
1. Logical consistency
2. Category overlap
3. Statistical appropriateness

Return validation report with any issues found.
"""

# Phase 3: Indicators
INDICATOR_GENERATION_PROMPT = """
Generate indicator definitions based on:
Variables: {variables}
Research context: {context}

Output format: JSON list of indicator definitions.
"""

# ... additional prompts for other phases
```

---

## 5. Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Phase files | `phase{N}_{purpose}.py` | `phase2_recoding.py` |
| Node functions | `{operation}_{entity}_node` | `extract_spss_node` |
| Test files | `test_{module}.py` | `test_phase1_extraction.py` |
| State classes | `{Purpose}State` | `ExtractionState`, `RecodingState` |
| Utility modules | `lowercase_with_underscores` | `pspp_wrapper.py` |
| Directories | `lowercase_with_underscores` | `agent/`, `utils/`, `llm/` |
| Constants | `UPPERCASE_WITH_UNDERSCORES` | `PSPP_PATH`, `MAX_TOKENS` |

---

## 6. Implementation Roadmap

**Milestone 1: Foundation**
- [ ] Set up project structure
- [ ] Implement `agent/state.py` with all TypedDict definitions
- [ ] Implement `agent/config.py` with configuration

**Milestone 2: Core Infrastructure**
- [ ] Implement `agent/utils/` module with utilities
- [ ] Implement `agent/nodes/phase1_extraction.py` (Steps 1-3)
- [ ] Implement `agent/edges.py` with conditional routing
- [ ] Implement `agent/graph.py` with basic graph construction

**Milestone 3: Phase 2-3 (Recoding & Indicators)**
- [ ] Implement `agent/nodes/phase2_recoding.py` (Steps 4-8)
- [ ] Implement `agent/nodes/phase3_indicators.py` (Steps 9-11)
- [ ] Implement `agent/validation/recoding.py`
- [ ] Implement `agent/llm/prompts.py`

**Milestone 4: Phase 4-6 (Tables & Statistics)**
- [ ] Implement `agent/nodes/phase4_tables.py` (Steps 12-16)
- [ ] Implement `agent/nodes/phase5_statistics.py` (Steps 17-18)
- [ ] Implement `agent/nodes/phase6_filtering.py` (Steps 19-20)
- [ ] Implement `agent/validation/indicators.py` and `tables.py`

**Milestone 5: Phase 7-8 (Presentation)**
- [ ] Implement `agent/nodes/phase7_powerpoint.py` (Step 21)
- [ ] Implement `agent/nodes/phase8_html_dashboard.py` (Step 22)

**Milestone 6: Testing**
- [ ] Unit tests for each phase
- [ ] Integration tests for full workflow
- [ ] End-to-end tests with sample data

---

## 7. Architectural Decisions

### 7.1 Why Phase-Based Files Instead of One File Per Node?

**Decision**: Group nodes by phase (3-5 nodes per file) rather than one file per node.

**Rationale**:
1. **Coherence**: Nodes in a phase work on the same state and share context
2. **Maintainability**: Related code stays together
3. **File Size**: 8 files of ~350-400 lines each vs 22 files of ~100 lines each
4. **Navigation**: Phase files align with workflow documentation

**Trade-offs**:
- Pro: Easier to understand complete phase logic
- Pro: Reduces file clutter
- Con: Larger files (but still manageable at ~350-400 lines)

### 7.2 Why Separate Phase 7 and Phase 8?

**Decision**: Keep PowerPoint generation (Phase 7) and HTML dashboard (Phase 8) in separate files.

**Rationale**:
1. **Different Output Formats**: PPTX vs HTML require different libraries
2. **Independent Testing**: Can test presentation generation separately
3. **Future Flexibility**: Easy to add new output formats (Phase 9, 10, etc.)
4. **Clear Separation**: Each file has single, well-defined purpose

### 7.3 Why TypedDict State Classes?

**Decision**: Use TypedDict for state definitions.

**Rationale**:
1. **Type Safety**: Static type checking with mypy
2. **IDE Support**: Autocomplete and inline documentation
3. **Documentation**: State structure is self-documenting
4. **LangGraph Compatible**: Works seamlessly with LangGraph

### 7.4 Why Separate `validation/` and `llm/` Modules?

**Decision**: Validation logic and LLM prompts in separate directories.

**Rationale**:
1. **Separation of Concerns**: Validation is deterministic; LLM is probabilistic
2. **Testability**: Validation functions can be unit tested without LLM mocking
3. **Reusability**: Validation functions may be used outside of LLM context
4. **Maintainability**: Different update patterns (validation rules vs prompt engineering)

---

## 8. Phase-Step-State Mapping

```
Phase → Steps → State Modified
─────┼────────┼────────────────────────
  1  │  1-3   │ ExtractionState
  2  │  4-8   │ RecodingState
  3  │  9-11  │ IndicatorState
  4  │ 12-16  │ CrossTableState
  5  │ 17-18  │ StatisticalAnalysisState
  6  │ 19-20  │ FilteringState
  7  │  21    │ PresentationState
  8  │  22    │ PresentationState
```

Nodes within a phase modify the same state TypedDict → natural grouping.

**Note**: Phases 7 and 8 both modify `PresentationState` but produce different outputs (PPT vs HTML), so they are kept as separate files for better modularity.

---

## 9. Design Rationale

### 9.1 Comparison: One File Per Node vs Phase-Based

| Aspect | One File Per Node | Phase-Based (Chosen) |
|--------|-------------------|----------------------|
| Number of files | 22 node files | 8 phase files |
| File size | ~100 lines each | ~350-400 lines each |
| Navigation | Find by step number | Find by phase |
| Cohesion | Low (related nodes scattered) | High (related nodes grouped) |
| Testing | Granular but fragmented | Organized by phase |

**Decision**: Phase-based organization chosen for better cohesion and maintainability.

### 9.2 Three-Node Pattern Localization

Each three-node pattern (Generate → Validate → Review) is contained within a single file:

| File | Three-Node Pattern |
|------|-------------------|
| `phase2_recoding.py` | Steps 4 (Generate), 5 (Validate), 6 (Review) |
| `phase3_indicators.py` | Steps 9 (Generate), 10 (Validate), 11 (Review) |
| `phase4_tables.py` | Steps 12 (Generate), 13 (Validate), 14 (Review) |

Easy to understand the complete cycle within one file.

### 9.3 Utility Module Organization

Shared utilities grouped by functionality:

| Module | Purpose |
|--------|---------|
| `pspp_wrapper.py` | PSPP execution (external tool interface) |
| `file_io.py` | File operations (cross-cutting concern) |
| `statistics.py` | Statistical functions (domain logic) |

Each utility has a single, well-defined purpose and can be tested independently.

---

*This document should be updated as the project evolves. Use git history to track changes.*
