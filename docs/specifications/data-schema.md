# Data Schema

This document describes all data structures, file formats, and schemas used in the Survey Analysis & Visualization Workflow.

---

## Table of Contents

1. [Overview](#1-overview)
2. [State Schema](#2-state-schema)
3. [File Format Schemas](#3-file-format-schemas)
4. [Data Transformation Flow](#4-data-transformation-flow)
5. [Validation Schemas](#5-validation-schemas)
6. [Configuration Schema](#6-configuration-schema)

---

## 1. Overview

### 1.1 Data Architecture

```mermaid
graph TB
    subgraph INPUT["Input Layer"]
        SAV[".sav File<br/>SPSS Survey Data"]
    end

    subgraph STATE["State Layer (WorkflowState)"]
        INPUT_STATE["InputState"]
        EXTRACTION["ExtractionState"]
        RECODING["RecodingState"]
        INDICATOR["IndicatorState"]
        CROSSTABLE["CrossTableState"]
        STATS["StatisticalAnalysisState"]
        FILTERING["FilteringState"]
        PRESENTATION["PresentationState"]
        APPROVAL["ApprovalState"]
        TRACKING["TrackingState"]
    end

    subgraph OUTPUT["Output Layer"]
        JSON["JSON Files<br/>significant_tables.json<br/>statistical_analysis_summary.json"]
        PPTX["PowerPoint<br/>presentation.pptx"]
        HTML["HTML Dashboard<br/>dashboard.html"]
        SPS["PSPP Syntax<br/>*.sps files"]
    end

    SAV --> STATE
    STATE --> JSON
    STATE --> PPTX
    STATE --> HTML
    STATE --> SPS

    style INPUT fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    style STATE fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    style OUTPUT fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
```

### 1.2 Schema Categories

| Category | Description | Examples |
|----------|-------------|----------|
| **State Schema** | TypedDict definitions for workflow state | `WorkflowState`, sub-states |
| **File Input** | External input data formats | `.sav` (SPSS) files |
| **File Output** | Generated output file schemas | `.json`, `.csv`, `.pptx`, `.html` |
| **Validation** | Data validation result structures | `ValidationResult`, feedback schemas |
| **Configuration** | Runtime configuration parameters | `DEFAULT_CONFIG` |

---

## 2. State Schema

The workflow uses a single evolving `WorkflowState` TypedDict that combines multiple function-specific sub-states.

### 2.1 State Hierarchy

```mermaid
graph TD
    WORKFLOW["WorkflowState<br/>(total=False)"]

    WORKFLOW --> INPUT["InputState"]
    WORKFLOW --> EXTRACTION["ExtractionState"]
    WORKFLOW --> RECODING["RecodingState"]
    WORKFLOW --> INDICATOR["IndicatorState"]
    WORKFLOW --> CROSSTABLE["CrossTableState"]
    WORKFLOW --> STATS["StatisticalAnalysisState"]
    WORKFLOW --> FILTERING["FilteringState"]
    WORKFLOW --> PRESENTATION["PresentationState"]
    WORKFLOW --> APPROVAL["ApprovalState"]
    WORKFLOW --> TRACKING["TrackingState"]

    style WORKFLOW fill:#f3e5f5,stroke:#7b1fa2,stroke-width:3px
    style INPUT fill:#e3f2fd
    style EXTRACTION fill:#e3f2fd
    style RECODING fill:#e3f2fd
    style INDICATOR fill:#e3f2fd
    style CROSSTABLE fill:#e3f2fd
    style STATS fill:#e3f2fd
    style FILTERING fill:#e3f2fd
    style PRESENTATION fill:#e3f2fd
    style APPROVAL fill:#fff3e0
    style TRACKING fill:#fff3e0
```

### 2.2 InputState

```python
class InputState(TypedDict):
    """Initial input configuration - populated at workflow start"""
    input_file_path: str         # Path to input .sav file
```

| Field | Type | Description |
|-------|------|-------------|
| `input_file_path` | `str` | Absolute path to SPSS survey data file |

### 2.3 ExtractionState

```python
class ExtractionState(TypedDict):
    """Data extraction and preparation - Steps 1-3"""
    original_metadata: Optional[Dict[str, Any]]   # Raw metadata from pyreadstat
    variable_centered_metadata: Optional[Dict[str, Any]]         # Metadata grouped by variable
    filtered_metadata: Optional[List[Dict[str, Any]]]          # Metadata after filtering
    filtered_out_variables: Optional[List[Dict[str, Any]]]     # Variables removed + reasons
```

**Note**: The `raw_data` field is deprecated and not stored in state. LangGraph uses msgpack serialization which doesn't handle pandas DataFrames efficiently. Storing DataFrames would cause large checkpoint files and performance issues. Instead, the data is reloaded from `input_file_path` when needed by subsequent processing steps.

| Field | Type | Populated | Description |
|-------|------|-----------|-------------|
| `original_metadata` | `Dict` | Step 1 | Raw SPSS variable metadata |
| `variable_centered_metadata` | `Dict` | Step 2 | Metadata restructured by variable |
| `filtered_metadata` | `List[Dict]` | Step 3 | Variables requiring recoding |
| `filtered_out_variables` | `List[Dict]` | Step 3 | Excluded variables with reasons |

#### Variable Metadata Dictionary

```python
{
    "name": str,              # Variable name (e.g., "q1_satisfaction")
    "label": str,             # Variable label/description
    "variable_type": str,     # "numeric" | "string" | "date"
    "min_value": Optional[int],     # Minimum value (numeric variables)
    "max_value": Optional[int],     # Maximum value (numeric variables)
    "value_labels": Optional[Dict[int, str]]  # Category labels (e.g., {1: "Strongly Disagree"})
}
```

### 2.4 RecodingState

```python
class RecodingState(TypedDict):
    """New dataset generation through LLM-orchestrated recoding - Steps 4-8"""

    recoding_rules: Optional[Dict[str, Any]]
    recoding_validation_result: Optional[Dict[str, Any]]
    recoding_approved: bool
    recoding_feedback: Optional[str]
    new_metadata: Optional[Dict[str, Any]]
    new_data_file: Optional[str]
```

| Field | Type | Populated | Description |
|-------|------|-----------|-------------|
| `recoding_rules` | `Dict` | Step 4 | AI-generated recoding rules |
| `recoding_validation_result` | `Dict` | Step 5 | Automated validation results |
| `recoding_approved` | `bool` | Step 6 | Human approval status |
| `recoding_feedback` | `str` | Step 5/6 | Feedback from validation or human |
| `new_metadata` | `Dict` | Step 8 | Complete metadata from new_data.sav |
| `new_data_file` | `str` | Step 8 | Path to new dataset .sav file |

### 2.5 IndicatorState

```python
class IndicatorState(TypedDict):
    """Indicator generation and semantic grouping - Steps 9-11"""

    indicators: Optional[Dict[str, Any]]
    indicator_validation_result: Optional[Dict[str, Any]]
    indicators_approved: bool
    indicator_feedback: Optional[str]
```

| Field | Type | Populated | Description |
|-------|------|-----------|-------------|
| `indicators` | `Dict` | Step 9 | Generated indicator definitions |
| `indicator_validation_result` | `Dict` | Step 10 | Validation results |
| `indicators_approved` | `bool` | Step 11 | Human approval status |
| `indicator_feedback` | `str` | Step 10/11 | Feedback from validation or human |

### 2.6 CrossTableState

```python
class CrossTableState(TypedDict):
    """Cross-table specification and generation - Steps 12-16"""

    table_specifications: Optional[Dict[str, Any]]
    table_validation_result: Optional[Dict[str, Any]]
    table_specs_approved: bool
    table_specs_feedback: Optional[str]
    table_syntax_file: Optional[str]
    cross_table_file: Optional[str]
```

| Field | Type | Populated | Description |
|-------|------|-----------|-------------|
| `table_specifications` | `Dict` | Step 12 | Table structure definitions |
| `table_validation_result` | `Dict` | Step 13 | Validation results |
| `table_specs_approved` | `bool` | Step 14 | Human approval status |
| `table_specs_feedback` | `str` | Step 13/14 | Feedback from validation or human |
| `table_syntax_file` | `str` | Step 15 | Path to PSPP CTABLES syntax file |
| `cross_table_file` | `str` | Step 16 | Path to cross-table output file |

### 2.7 StatisticalAnalysisState

```python
class StatisticalAnalysisState(TypedDict):
    """Python script generation and Chi-square statistics computation - Steps 17-18"""

    statistics_script: Optional[str]
    statistical_summary: Optional[Dict[str, Any]]
```

| Field | Type | Populated | Description |
|-------|------|-----------|-------------|
| `statistics_script` | `str` | Step 17 | Path to generated statistics script |
| `statistical_summary` | `Dict` | Step 18 | Statistical test results (chi-square, Cramer's V) |

### 2.8 FilteringState

```python
class FilteringState(TypedDict):
    """Filter list generation and significant tables selection - Steps 19-20"""

    filter_list: Optional[Dict[str, Any]]
    filtered_tables: Optional[Dict[str, Any]]
    total_tables_evaluated: int
    significant_tables_count: int
    filtering_valid: bool
```

| Field | Type | Populated | Description |
|-------|------|-----------|-------------|
| `filter_list` | `Dict` | Step 19 | Pass/fail status for all tables |
| `filtered_tables` | `Dict` | Step 20 | Tables filtered by significance |
| `total_tables_evaluated` | `int` | Step 20 | Total number of tables evaluated |
| `significant_tables_count` | `int` | Step 20 | Number of significant tables after filtering |
| `filtering_valid` | `bool` | Step 20 | Whether filtering validation passed |

### 2.9 PresentationState

```python
class PresentationState(TypedDict):
    """Final output generation - Steps 21-22"""

    powerpoint_file: Optional[str]
    html_dashboard_file: Optional[str]
```

| Field | Type | Populated | Description |
|-------|------|-----------|-------------|
| `powerpoint_file` | `str` | Step 21 | Generated PowerPoint file |
| `html_dashboard_file` | `str` | Step 22 | Generated HTML dashboard |

### 2.10 ApprovalState

```python
class ApprovalState(TypedDict):
    """Human-in-the-loop approval tracking (crosses all steps)"""

    current_step: str                      # Current step identifier (e.g., "step_4_generate_recoding_rules")
    requires_human_review: bool            # Whether current step needs human input
    iteration_count: int                   # Number of iterations for current step (for retry logic)
```

| Field | Type | Description |
|-------|------|-------------|
| `current_step` | `str` | Current step identifier from STEP_* constants (e.g., "step_6_review_recoding_rules") |
| `requires_human_review` | `bool` | Whether current step needs human input |
| `iteration_count` | `int` | Number of iterations for current step (for retry logic) |

#### Step Identifiers

The workflow uses string constants for step identifiers instead of numeric values:

| Step | Identifier Constant | Description |
|------|---------------------|-------------|
| 0 | `STEP_0_INITIAL` | Initial state |
| 1 | `STEP_1_EXTRACT_SPSS` | Extract SPSS data |
| 2 | `STEP_2_TRANSFORM_METADATA` | Transform metadata |
| 3 | `STEP_3_FILTER_METADATA` | Filter metadata |
| 4 | `STEP_4_GENERATE_RECODING_RULES` | Generate recoding rules |
| 5 | `STEP_5_VALIDATE_RECODING_RULES` | Validate recoding rules |
| 6 | `STEP_6_REVIEW_RECODING_RULES` | Review recoding rules |
| 7 | `STEP_7_GENERATE_PSPP_RECODING_SYNTAX` | Generate PSPP recoding syntax |
| 8 | `STEP_8_EXECUTE_PSPP_RECODING` | Execute PSPP recoding |
| 9 | `STEP_9_GENERATE_INDICATORS` | Generate indicators |
| 10 | `STEP_10_VALIDATE_INDICATORS` | Validate indicators |
| 11 | `STEP_11_REVIEW_INDICATORS` | Review indicators |
| 12 | `STEP_12_GENERATE_TABLE_SPECIFICATIONS` | Generate table specifications |
| 13 | `STEP_13_VALIDATE_TABLE_SPECIFICATIONS` | Validate table specifications |
| 14 | `STEP_14_REVIEW_TABLE_SPECIFICATIONS` | Review table specifications |
| 15 | `STEP_15_GENERATE_PSPP_TABLE_SYNTAX` | Generate PSPP table syntax |
| 16 | `STEP_16_EXECUTE_PSPP_TABLES` | Execute PSPP tables |
| 17 | `STEP_17_GENERATE_STATISTICS_SCRIPT` | Generate statistics script |
| 18 | `STEP_18_EXECUTE_STATISTICS_SCRIPT` | Execute statistics script |
| 19 | `STEP_19_GENERATE_FILTER_LIST` | Generate filter list |
| 20 | `STEP_20_APPLY_FILTER_TO_TABLES` | Apply filter to tables |
| 21 | `STEP_21_GENERATE_POWERPOINT` | Generate PowerPoint |
| 22 | `STEP_22_GENERATE_HTML_DASHBOARD` | Generate HTML dashboard |

**Review Steps** (three-node pattern approval steps):
- `STEP_6_REVIEW_RECODING_RULES`
- `STEP_11_REVIEW_INDICATORS`
- `STEP_14_REVIEW_TABLE_SPECIFICATIONS`

#### Approval Comment Schema

```python
{
    "step": str,              # "recoding" | "indicators" | "table_specs"
    "decision": str,          # "approved" | "rejected" | "modified"
    "comments": str,          # Human comments
    "timestamp": str          # ISO timestamp
}
```

### 2.11 TrackingState

```python
class TrackingState(TypedDict):
    """Execution tracking (crosses all steps)"""

    errors: List[str]
    warnings: List[str]
```

| Field | Type | Description |
|-------|------|-------------|
| `errors` | `List[str]` | Error messages |
| `warnings` | `List[str]` | Warning messages |

---

## 3. File Format Schemas

### 3.1 Input File: SPSS (.sav)

The `.sav` file format is the standard SPSS/PASW statistics data file format.

| Component | Description |
|-----------|-------------|
| **Library** | `pyreadstat` |
| **Content** | Survey response data + variable metadata |
| **Extraction** | `pyreadstat.read_sav()` |

#### Extracted Metadata Structure

```python
{
    "number_columns": int,
    "number_rows": int,
    "column_labels": Dict[str, str],        # variable_name -> label
    "column_value_labels": Dict[str, Dict], # variable_name -> {value: label}
    "variable_types": Dict[str, str]        # variable_name -> type
}
```

### 3.2 Output Files: JSON Schemas

#### 3.2.1 Recoding Rules (`recoding_rules.json`)

```json
{
    "recoding_rules": [
        {
            "id": "string",
            "source_variable": "string",
            "target_variable": "string",
            "rule_type": "mapping" | "range" | "formula",
            "transformations": [
                {
                    "source": [int | string],
                    "target": int | string,
                    "label": "string"
                }
            ],
            "description": "string"
        }
    ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `source_variable` | `str` | Original variable name (must exist in metadata) |
| `target_variable` | `str` | New variable name (must be unique) |
| `rule_type` | `str` | Type of recoding rule |
| `transformations` | `List` | Array of transformation mappings |
| `description` | `str` | Human-readable description |

#### 3.2.2 Indicators (`indicators.json`)

```json
{
    "indicators": [
        {
            "id": "string",
            "description": "string",
            "metric": "average" | "percentage" | "distribution",
            "underlying_variables": ["string", ...],
            "theme": "string"
        }
    ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | Unique identifier |
| `description` | `str` | Human-readable description |
| `metric` | `str` | Type of metric |
| `underlying_variables` | `List[str]` | Variable names in this indicator |
| `theme` | `str` | Semantic theme (e.g., "satisfaction", "demographics") |

#### 3.2.3 Table Specifications (`table_specifications.json`)

```json
{
    "tables": [
        {
            "id": "string",
            "description": "string",
            "row_indicators": ["string", ...],
            "column_indicators": ["string", ...],
            "sort_rows": "none" | "asc" | "desc",
            "sort_columns": "none" | "asc" | "desc",
            "min_count": 10,
            "cramers_v_threshold": 0.1
        }
    ],
    "weighting_variable": "string" | null
}
```

| Field | Type | Description |
|-------|------|-------------|
| `row_indicators` | `List[str]` | Variables for table rows |
| `column_indicators` | `List[str]` | Variables for table columns |
| `sort_rows` | `str` | Row sorting order |
| `sort_columns` | `str` | Column sorting order |
| `min_count` | `int` | Minimum cell count threshold |
| `cramers_v_threshold` | `float` | Minimum Cramer's V effect size |
| `weighting_variable` | `str` | Variable to weight by |

#### 3.2.4 Significant Tables (`significant_tables.json`)

```json
{
    "tables": [
        {
            "name": "string",
            "rows": "string",
            "columns": "string",
            "data": {
                "row_labels": ["string", ...],
                "column_labels": ["string", ...],
                "counts": [
                    [int, int, ...],
                    [int, int, ...]
                ],
                "row_percentages": [
                    [float, float, ...],
                    [float, float, ...]
                ],
                "column_percentages": [
                    [float, float, ...],
                    [float, float, ...]
                ]
            },
            "statistics": {
                "chi_square": float,
                "p_value": float,
                "degrees_of_freedom": int,
                "cramers_v": float,
                "interpretation": "negligible" | "small" | "medium" | "large"
            },
            "sample_size": int
        }
    ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `row_labels` | `List[str]` | Category labels for rows |
| `column_labels` | `List[str]` | Category labels for columns |
| `counts` | `List[List[int]]` | 2D array of cell counts |
| `row_percentages` | `List[List[float]]` | Row percentages |
| `column_percentages` | `List[List[float]]` | Column percentages |
| `statistics` | `Dict` | Chi-square test results |
| `sample_size` | `int` | Total sample size |

#### 3.2.5 Statistical Analysis Summary (`statistical_analysis_summary.json`)

```json
[
    {
        "table_name": "string",
        "chi_square": float,
        "p_value": float,
        "degrees_of_freedom": int,
        "cramers_v": float,
        "interpretation": "negligible" | "small" | "medium" | "large",
        "sample_size": int,
        "is_significant": boolean
    }
]
```

| Field | Type | Description |
|-------|------|-------------|
| `table_name` | `str` | Table identifier |
| `chi_square` | `float` | Chi-square statistic |
| `p_value` | `float` | P-value for significance test |
| `degrees_of_freedom` | `int` | Degrees of freedom |
| `cramers_v` | `float` | Effect size (0-1) |
| `interpretation` | `str` | Effect size category |
| `sample_size` | `int` | Total sample size |
| `is_significant` | `bool` | Meets significance threshold |

#### 3.2.6 Filter List (`filter_list.json`)

```json
[
    {
        "table_name": "string",
        "passes_cramers_v": boolean,
        "passes_sample_size": boolean,
        "passes_significance": boolean,
        "include": boolean,
        "reason": "string"
    }
]
```

### 3.3 Output Files: Other Formats

| File | Format | Description |
|------|--------|-------------|
| `presentation.pptx` | PowerPoint | Executive summary with significant tables |
| `dashboard.html` | HTML | Full report with all tables and charts |
| `*.sps` | PSPP Syntax | Generated PSPP command files |

---

## 4. Data Transformation Flow

### 4.1 State Evolution Timeline

```mermaid
graph TD
    STEP0["Step 0<br/>InputState<br/>input_file_path"]
    STEP1["Step 1<br/>ExtractionState<br/>original_metadata"]
    STEP2["Step 2<br/>variable_centered_metadata"]
    STEP3["Step 3<br/>filtered_metadata<br/>filtered_out_variables"]
    STEP4["Step 4<br/>RecodingState<br/>recoding_rules"]
    STEP5["Step 5<br/>recoding_validation_result"]
    STEP6["Step 6<br/>recoding_approved"]
    STEP7["Step 7<br/>PSPP syntax generation"]
    STEP8["Step 8<br/>new_data_file<br/>new_metadata"]
    STEP9["Step 9<br/>IndicatorState<br/>indicators"]
    STEP10["Step 10<br/>indicator_validation_result"]
    STEP11["Step 11<br/>indicators_approved"]
    STEP12["Step 12<br/>CrossTableState<br/>table_specifications"]
    STEP13["Step 13<br/>table_validation_result"]
    STEP14["Step 14<br/>table_specs_approved"]
    STEP15["Step 15<br/>table_syntax_file"]
    STEP16["Step 16<br/>cross_table_file"]
    STEP17["Step 17<br/>StatisticalAnalysisState<br/>statistics_script"]
    STEP18["Step 18<br/>statistical_summary"]
    STEP19["Step 19<br/>FilteringState<br/>filter_list"]
    STEP20["Step 20<br/>significant_tables"]
    STEP21["Step 21<br/>PresentationState<br/>powerpoint_file"]
    STEP22["Step 22<br/>html_dashboard_file"]

    STEP0 --> STEP1 --> STEP2 --> STEP3
    STEP3 --> STEP4 --> STEP5 --> STEP6
    STEP6 --> STEP7 --> STEP8
    STEP8 --> STEP9 --> STEP10 --> STEP11
    STEP11 --> STEP12 --> STEP13 --> STEP14
    STEP14 --> STEP15 --> STEP16
    STEP16 --> STEP17 --> STEP18
    STEP18 --> STEP19 --> STEP20
    STEP20 --> STEP21
    STEP16 --> STEP22

    style STEP0 fill:#e3f2fd
    style STEP1 fill:#e8f5e9
    style STEP4 fill:#fff9c4
    style STEP9 fill:#fff9c4
    style STEP12 fill:#fff9c4
    style STEP17 fill:#e8f5e9
    style STEP19 fill:#e8f5e9
    style STEP21 fill:#c8e6c9
    style STEP22 fill:#c8e6c9
```

### 4.2 Data Flow Summary

| Stage | Input | Key Transformation | Output |
|-------|-------|-------------------|--------|
| **1** | `.sav` file | Extract data and metadata | `original_metadata` |
| **2** | Original metadata | Group by variable | `variable_centered_metadata` |
| **3** | Variable metadata | Filter out不需要的变量 | `filtered_metadata` |
| **4** | Filtered metadata | LLM generates recoding rules | `recoding_rules` |
| **7** | Recoding rules | Convert to PSPP syntax | `pspp_recoding_syntax` |
| **8** | Original data + PSPP | Execute recoding | `new_data.sav`, `new_metadata` |
| **9** | New metadata | LLM groups variables | `indicators` |
| **12** | New metadata + indicators | LLM defines tables | `table_specifications` |
| **15** | Table specifications | Convert to PSPP syntax | `pspp_table_syntax` |
| **16** | New data + PSPP | Execute CTABLES | `cross_table.sav` |
| **18** | Cross-table data | Chi-square analysis | `statistical_summary` |
| **20** | All tables + stats | Filter by significance | `significant_tables` |
| **21** | Significant tables | Generate PowerPoint | `presentation.pptx` |
| **22** | All tables | Generate HTML dashboard | `dashboard.html` |

---

## 5. Validation Schemas

### 5.1 ValidationResult

```python
@dataclass
class ValidationResult:
    """Standard validation result structure"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    checks_performed: List[str]
```

| Field | Type | Description |
|-------|------|-------------|
| `is_valid` | `bool` | Overall validation status |
| `errors` | `List[str]` | Critical errors that must be fixed |
| `warnings` | `List[str]` | Non-critical issues |
| `checks_performed` | `List[str]` | List of validation checks run |

### 5.2 Feedback Schema

```python
{
    "iteration": int,
    "source": "validation" | "human",
    "is_valid": bool,
    "errors": [str, ...],
    "warnings": [str, ...],
    "issues": [str, ...],      # Human-identified issues
    "suggestions": [str, ...]  # Human suggestions
}
```

### 5.3 Validation Checks

#### Recoding Rules Validation

| Check | Description | Error Condition |
|-------|-------------|-----------------|
| **Source variable exists** | Verify source variable in metadata | Variable not found |
| **Target variable unique** | Ensure no duplicate targets | Duplicate name |
| **Valid range** | Range rules have start ≤ end | Invalid range |
| **Non-overlapping** | Source ranges don't overlap | Overlapping ranges |
| **JSON syntax** | Valid JSON structure | Parse error |

#### Indicators Validation

| Check | Description | Error Condition |
|-------|-------------|-----------------|
| **Variables exist** | All variables in metadata | Variable not found |
| **Min variables** | At least 2 per indicator | Too few variables |
| **Unique names** | No duplicate indicator names | Duplicate name |

#### Table Specifications Validation

| Check | Description | Error Condition |
|-------|-------------|-----------------|
| **Variables exist** | Row/column vars in metadata | Variable not found |
| **Categorical only** | Variables are categorical | Continuous variable |
| **Valid statistics** | Statistics match table type | Invalid stat |

---

## 6. Configuration Schema

### 6.1 DEFAULT_CONFIG

> **Note**: The application uses a multi-provider LLM system (Kimi, DeepSeek, Zhipu). The configuration below shows the default values when using Zhipu as the provider. For complete LLM provider configuration details, see [Configuration](./system-configuration.md#2-llm-provider-configuration).

```python
DEFAULT_CONFIG = {
    # LLM Configuration (defaults for Zhipu provider)
    "llm_provider": "ZHIPU",          # Options: KIMI, DEEPSEEK, ZHIPU
    "model": "glm-4.7",                # Zhipu GLM model
    "temperature": 0.1,
    "max_tokens": 4000,

    # Three-Node Pattern
    "max_self_correction_iterations": 3,
    "enable_human_review": True,

    # Step 3: Filtering
    "cardinality_threshold": 30,
    "filter_binary": True,
    "filter_other_text": True,

    # PSPP
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

### 6.2 Configuration Sections

| Category | Option | Type | Default | Description |
|----------|--------|------|---------|-------------|
| **LLM** | `llm_provider` | `str` | `"ZHIPU"` | LLM provider (KIMI, DEEPSEEK, ZHIPU) |
| **LLM** | `model` | `str` | `"glm-4.7"` | Model name (provider-specific) |
| **LLM** | `temperature` | `float` | `0.1` | LLM temperature |
| **LLM** | `max_tokens` | `int` | `4000` | Max response tokens |
| **Pattern** | `max_self_correction_iterations` | `int` | `3` | Max retry iterations |
| **Pattern** | `enable_human_review` | `bool` | `True` | Enable human review |
| **Filter** | `cardinality_threshold` | `int` | `30` | Max distinct values |
| **Filter** | `filter_binary` | `bool` | `True` | Filter binary vars |
| **Filter** | `filter_other_text` | `bool` | `True` | Filter text fields |
| **PSPP** | `pspp_path` | `str` | `"/usr/bin/pspp"` | PSPP executable |
| **PSPP** | `pspp_output_path` | `str` | `"output/pspp_logs.txt"` | Log file |
| **Paths** | `output_dir` | `str` | `"output"` | Output directory |
| **Paths** | `temp_dir` | `str` | `"temp"` | Temp directory |
| **Stats** | `significance_level` | `float` | `0.05` | P-value threshold |
| **Stats** | `min_cramers_v` | `float` | `0.1` | Min effect size |
| **Stats** | `min_cell_count` | `int` | `10` | Min expected count |
| **Output** | `powerpoint_template` | `str` | `None` | Custom template |
| **Output** | `html_theme` | `str` | `"default"` | HTML theme |

---

## Related Documents

| Document | Content |
|----------|---------|
| **[Data Flow](./data-flow.md)** | Workflow design and step specifications |
| **[System Architecture](./system-architecture.md)** | System components, deployment, and troubleshooting |
| **[Configuration](./system-configuration.md)** | Configuration options and usage examples |
| **[Project Structure](./project-structure.md)** | Directory structure and file locations |
| **[Web Interface](./web-interface.md)** | Agent Chat UI setup and usage |
| **[User Guide](./features-and-usage.md)** | Product introduction for end users |
