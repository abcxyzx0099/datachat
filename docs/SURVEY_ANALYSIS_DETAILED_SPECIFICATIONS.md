# Survey Analysis Detailed Specifications

> This document contains complete implementation details for the Survey Analysis & Visualization Workflow. For the concise workflow design and architecture overview, refer to [Survey Analysis Workflow Design](./SURVEY_ANALYSIS_WORKFLOW_DESIGN.md).

# Table of Contents

1. [State Management](#1-state-management)
2. [LLM Prompt Templates](#2-llm-prompt-templates)
3. [Validation Specifications](#3-validation-specifications)
4. [Step Implementations](#4-step-implementations)
5. [PSPP Syntax Reference](#5-pspp-syntax-reference)
6. [Statistical Analysis](#6-statistical-analysis)
7. [Output Generation](#7-output-generation)

---

## 1. State Management

### 1.1 Complete TypedDict Definitions

```python
from typing import TypedDict, List, Dict, Any, Optional
from pandas import DataFrame

# ============================================================================
# FUNCTION-SPECIFIC SUB-STATES
# ============================================================================

class InputState(TypedDict):
    """Initial input configuration"""
    spss_file_path: str                      # Path to input .sav file
    config: Dict[str, Any]                   # Configuration parameters


class ExtractionState(TypedDict):
    """Data extraction and preparation - Step 1-3"""
    raw_data: DataFrame                      # Extracted survey data
    original_metadata: Dict[str, Any]        # Raw metadata from pyreadstat
    variable_centered_metadata: List[Dict]   # Metadata grouped by variable
    filtered_metadata: List[Dict]            # Metadata after filtering
    filtered_out_variables: List[Dict]       # Variables removed + reasons


class RecodingState(TypedDict):
    """New dataset generation through LLM-orchestrated recoding - Steps 4-8"""

    # Three-node pattern fields (Steps 4-6)
    recoding_rules: Dict[str, Any]            # AI-generated recoding rules
    recoding_rules_json_path: str             # Saved recoding rules file
    recoding_iteration: int                   # Current iteration count
    recoding_validation: Dict[str, Any]       # Automated validation results
    recoding_feedback: Optional[Dict]         # Feedback from validation or human
    recoding_feedback_source: Optional[str]   # "validation" or "human"
    recoding_approved: bool                   # Human approval status

    # PSPP execution fields (Steps 7-8)
    pspp_recoding_syntax: str                 # Generated PSPP syntax
    pspp_recoding_syntax_path: str            # Saved syntax file
    new_data_path: str                        # Path to new dataset (original + recoded variables)
    new_metadata: Dict[str, Any]              # Complete metadata extracted from new_data.sav (aka updated_metadata)

    # Shared configuration
    max_self_correction_iterations: int       # Maximum allowed (default: 3)


class IndicatorState(TypedDict):
    """Indicator generation and semantic grouping - Steps 9-11"""

    # Three-node pattern fields (Steps 9-11)
    indicators: List[Dict[str, Any]]         # Generated indicators
    indicators_json_path: str                # Saved indicators file
    indicators_iteration: int                # Current iteration count
    indicators_validation: Dict[str, Any]    # Validation results
    indicators_feedback: Optional[Dict]      # Feedback from validation or human
    indicators_feedback_source: Optional[str]# "validation" or "human"
    indicators_approved: bool                # Human approval status

    # Input metadata
    indicator_metadata: List[Dict]           # Metadata for indicator generation


class CrossTableState(TypedDict):
    """Cross-table specification and generation - Steps 12-16"""

    # Three-node pattern fields (Steps 12-14)
    table_specifications: Dict[str, Any]     # Table structure definitions
    table_specs_json_path: str               # Saved table specs
    table_specs_iteration: int               # Current iteration count
    table_specs_validation: Dict[str, Any]   # Validation results
    table_specs_feedback: Optional[Dict]     # Feedback from validation or human
    table_specs_feedback_source: Optional[str] # "validation" or "human"
    table_specs_approved: bool               # Human approval status

    # PSPP execution fields (Steps 15-16)
    pspp_table_syntax: str                   # Generated cross-table syntax
    pspp_table_syntax_path: str              # Saved syntax file
    cross_table_csv_path: str                # Exported cross-table CSV file
    cross_table_json_path: str               # Exported cross-table JSON file

    # Additional configuration
    weighting_variable: Optional[str]        # Weighting variable for cross-tables


class StatisticalAnalysisState(TypedDict):
    """Python script generation and Chi-square statistics computation - Steps 17-18"""
    python_stats_script: str                 # Generated Python script for statistics
    python_stats_script_path: str            # Saved Python script file
    all_small_tables: List[Dict]             # All tables with chi-square stats
    statistical_summary_path: str             # Path to statistical_analysis_summary.json
    statistical_summary: Dict[str, Any]       # Summary of all statistical tests


class FilteringState(TypedDict):
    """Filter list generation and significant tables selection - Steps 19-20"""
    # Step 19: Generate filter list from statistical summary
    filter_list: List[Dict]                  # Pass/fail status for all tables
    filter_list_json_path: str               # Saved filter list

    # Step 20: Apply filter to cross-table results
    significant_tables: List[Dict]           # Tables filtered by Cramer's V + count
    significant_tables_json_path: str        # Saved filtered tables


class PresentationState(TypedDict):
    """Final output generation - Steps 21-22 (Phases 7-8)"""
    # Phase 7: PowerPoint (Step 21) - based on significant_tables
    powerpoint_path: str                     # Generated PowerPoint file
    # Phase 8: HTML Dashboard (Step 22) - based on cross_table files (all tables)
    html_dashboard_path: str                 # Generated HTML dashboard
    charts_generated: List[Dict]             # Chart metadata


class ApprovalState(TypedDict):
    """Human-in-the-loop approval tracking (crosses all steps)"""
    approval_comments: List[Dict]            # Human feedback and comments
    pending_approval_step: Optional[str]     # Current step awaiting review


class TrackingState(TypedDict):
    """Execution tracking (crosses all steps)"""
    execution_log: List[Dict]                # Step-by-step execution log
    errors: List[str]                        # Error messages
    warnings: List[str]                      # Warning messages


# ============================================================================
# COMBINED WORKFLOW STATE
# ============================================================================

class WorkflowState(
    InputState,
    ExtractionState,
    RecodingState,
    IndicatorState,
    CrossTableState,
    StatisticalAnalysisState,
    FilteringState,
    PresentationState,
    ApprovalState,
    TrackingState,
    total=False
):
    """
    Combined workflow state that inherits all functionally-specific sub-states.

    Using `total=False` allows fields to be optional, populated only when
    their respective step completes. This reduces state complexity and
    improves debugging by clearly indicating which function each field belongs to.

    Example usage in nodes:
        def extract_spss_node(state: WorkflowState) -> WorkflowState:
            state["raw_data"] = df  # ExtractionState field
            state["original_metadata"] = meta  # ExtractionState field
            return state
    """
    pass
```

### 1.2 State Evolution Timeline

| Step | Sub-State | Key Fields Added | Optional Fields |
|------|-----------|------------------|-----------------|
| 0 | `InputState` | `spss_file_path`, `config` | All fields initially None |
| 1 | `ExtractionState` | `raw_data`, `original_metadata` | `variable_centered_metadata`, `filtered_metadata` still None |
| 2 | `ExtractionState` | `variable_centered_metadata` | `filtered_metadata` still None |
| 3 | `ExtractionState` | `filtered_metadata`, `filtered_out_variables` | All extraction fields now populated |
| 4 | `RecodingState` | `recoding_rules`, `recoding_iteration` | Validation/feedback fields still None |
| 5 | `RecodingState` | `recoding_validation` | `recoding_feedback`, `recoding_approved` still None |
| 6 | `RecodingState` | `recoding_approved` | May have `recoding_feedback` if rejected |
| 7 | `RecodingState` | `pspp_recoding_syntax`, `pspp_recoding_syntax_path` | `new_data_path` still None |
| 8 | `RecodingState` | `new_data_path`, `updated_metadata` | All recoding fields now populated |
| 9 | `IndicatorState` | `indicators`, `indicators_iteration` | Validation still pending |
| 10 | `IndicatorState` | `indicators_validation` | Approval still pending |
| 11 | `IndicatorState` | `indicators_approved` | All indicator fields populated |
| 12-14 | `CrossTableState` | `table_specifications`, `table_specs_validation`, `table_specs_approved` | Complete three-node cycle |
| 15-16 | `CrossTableState` | `pspp_table_syntax`, `cross_table_csv_path`, `cross_table_json_path` | PSPP execution complete |
| 17-18 | `StatisticalAnalysisState` | `python_stats_script`, `statistical_summary` | Analysis complete |
| 19-20 | `FilteringState` | `filter_list`, `significant_tables` | Filtering complete |
| 21-22 | `PresentationState` | `powerpoint_path`, `html_dashboard_path` | All outputs complete |

---

## 2. LLM Prompt Templates

### 2.1 Step 4: Generate Recoding Rules

#### Initial Prompt (First Iteration)

```python
def build_initial_recoding_prompt(filtered_metadata: List[Dict]) -> str:
    """
    Generate initial prompt for recoding rule creation.
    """
    prompt = f"""You are a market research data expert. Given survey variable metadata,
generate intelligent recoding rules.

PRINCIPLES:
1. Group continuous variables into meaningful ranges
2. Recode detailed categorical variables into broader groups
3. Create derived variables when semantically meaningful
4. Apply Top 2 Box / Top 3 Box for satisfaction ratings

INPUT METADATA:
{format_metadata_for_llm(filtered_metadata)}

OUTPUT FORMAT (JSON):
{{
    "recoding_rules": [
        {{
            "source_variable": "age",
            "target_variable": "age_group",
            "rule_type": "range",
            "transformations": [
                {{"source": [18, 24], "target": 1, "label": "18-24"}},
                {{"source": [25, 34], "target": 2, "label": "25-34"}},
                {{"source": [35, 44], "target": 3, "label": "35-44"}},
                {{"source": [45, 54], "target": 4, "label": "45-54"}},
                {{"source": [55, 99], "target": 5, "label": "55+"}}
            ]
        }},
        {{
            "source_variable": "q5_satisfaction",
            "target_variable": "q5_satisfaction_top2box",
            "rule_type": "value_mapping",
            "transformations": [
                {{"source": [1, 8], "target": 0, "label": "Others"}},
                {{"source": [9, 10], "target": 1, "label": "Top 2 Box"}}
            ]
        }}
    ]
}}

REQUIREMENTS:
- Return ONLY valid JSON, no markdown formatting
- All source variables must exist in the provided metadata
- Target variable names must be unique
- Range rules: ensure start ≤ end
- Value mappings: source ranges must not overlap
"""
    return prompt
```

#### Validation Retry Prompt

```python
def build_validation_retry_prompt(
    metadata: List[Dict],
    validation_result: Dict,
    iteration: int
) -> str:
    """
    Generate prompt for retrying after validation failure.
    """
    errors = validation_result.get("errors", [])
    warnings = validation_result.get("warnings", [])

    prompt = f"""## Previous Iteration Feedback (Iteration {iteration - 1})

Your previous attempt had the following validation errors:

**Errors:**
{format_errors_list(errors)}

**Warnings:**
{format_warnings_list(warnings) if warnings else "(None)"}

## Instructions for This Iteration

Please generate new recoding rules that address ALL of the errors above:

{get_specific_instructions(errors)}

[Original prompt with metadata...]
"""
    return prompt

def get_specific_instructions(errors: List[str]) -> str:
    """Generate specific instructions based on error types."""
    instructions = []

    for error in errors:
        if "not found in metadata" in error:
            instructions.append("- Use only source variables that exist in the provided metadata")
        elif "Invalid range" in error:
            instructions.append("- Ensure all ranges are valid (start value ≤ end value)")
        elif "Duplicate target" in error:
            instructions.append("- Ensure each target variable name is unique")
        elif "Overlapping source" in error:
            instructions.append("- Ensure source value ranges do not overlap within each rule")

    return "\n".join(instructions) if instructions else "- Fix all validation errors"
```

#### Human Feedback Prompt

```python
def build_human_feedback_prompt(
    metadata: List[Dict],
    human_feedback: Dict,
    iteration: int
) -> str:
    """
    Generate prompt for incorporating human review feedback.
    """
    issues = human_feedback.get("issues", [])
    suggestions = human_feedback.get("suggestions", [])

    prompt = f"""## Human Review Feedback (Iteration {iteration - 1})

The human reviewer provided the following feedback:

**Issues:**
{format_issues_list(issues)}

**Suggestions:**
{format_suggestions_list(suggestions) if suggestions else "(None)"}

## Instructions for This Iteration

Please generate new recoding rules that address the human reviewer's feedback:

{format_human_instructions(issues, suggestions)}

[Original prompt with metadata...]
"""
    return prompt
```

### 2.2 Step 9: Generate Indicators

#### Initial Prompt

```python
def build_initial_indicators_prompt(updated_metadata: Dict) -> str:
    """
    Generate initial prompt for indicator grouping.
    """
    prompt = f"""You are a market research analyst. Group survey variables into semantic indicators.

PRINCIPLES:
1. Group variables that measure the same underlying concept
2. Create indicators for multi-item scales (e.g., satisfaction scales)
3. Group demographic variables separately
4. Limit to 3-7 variables per indicator

INPUT METADATA:
{format_metadata_for_llm(updated_metadata)}

OUTPUT FORMAT (JSON):
{{
    "indicators": [
        {{
            "name": "Customer Satisfaction",
            "variables": ["sat_q1", "sat_q2", "sat_q3", "sat_q4"],
            "description": "Overall customer satisfaction metrics",
            "theme": "satisfaction"
        }},
        {{
            "name": "Demographics",
            "variables": ["age", "gender", "income", "education"],
            "description": "Respondent demographic characteristics",
            "theme": "demographics"
        }}
    ]
}}

REQUIREMENTS:
- Return ONLY valid JSON, no markdown formatting
- All variable names must exist in the provided metadata
- Each indicator must have at least 2 variables
- Indicator names must be unique and descriptive
"""
    return prompt
```

### 2.3 Step 12: Generate Table Specifications

#### Initial Prompt

```python
def build_initial_table_specs_prompt(
    updated_metadata: Dict,
    indicators: List[Dict]
) -> str:
    """
    Generate initial prompt for table specification.
    """
    prompt = f"""You are a market research analyst. Define cross-tabulation tables for analysis.

PRINCIPLES:
1. Create tables comparing demographics against satisfaction indicators
2. Use categorical variables in rows and columns
3. Include count and column percentages
4. Limit to tables with meaningful relationships

INPUT METADATA:
{format_metadata_for_llm(updated_metadata)}

AVAILABLE INDICATORS:
{format_indicators_for_llm(indicators)}

OUTPUT FORMAT (JSON):
{{
    "tables": [
        {{
            "name": "Gender by Satisfaction",
            "rows": "gender",
            "columns": "sat_q1",
            "weight": None,
            "statistics": ["count", "column_percent", "chi_square"]
        }},
        {{
            "name": "Age Group by Top 2 Box",
            "rows": "age_group",
            "columns": "sat_top2box",
            "weight": "weight_var",
            "statistics": ["count", "column_percent"]
        }}
    ]
}}

REQUIREMENTS:
- Return ONLY valid JSON, no markdown formatting
- Row and column variables must exist in metadata
- Row/column variables must be categorical (not continuous)
- Statistics must be valid for the table type
"""
    return prompt
```

---

## 3. Validation Specifications

### 3.1 Recoding Rules Validation

```python
from typing import List, Dict, Any

class RecodingValidator:
    """Validates AI-generated recoding rules."""

    def __init__(self, metadata: List[Dict]):
        self.metadata = metadata
        self.variable_names = {var["name"] for var in metadata}
        self.errors = []
        self.warnings = []

    def validate_all_rules(self, rules: Dict[str, Any]) -> ValidationResult:
        """
        Perform all validation checks on recoding rules.
        """
        self.errors = []
        self.warnings = []

        if not isinstance(rules, dict) or "recoding_rules" not in rules:
            self.errors.append("Invalid structure: missing 'recoding_rules' key")
            return ValidationResult(is_valid=False, errors=self.errors, warnings=self.warnings)

        recoding_rules = rules["recoding_rules"]

        # Check 1: Source variables exist
        self._validate_source_variables_exist(recoding_rules)

        # Check 2: No duplicate target variables
        self._validate_no_duplicate_targets(recoding_rules)

        # Check 3: Range validity
        self._validate_ranges(recoding_rules)

        # Check 4: Target uniqueness within rules
        self._validate_target_uniqueness(recoding_rules)

        # Check 5: Source non-overlap
        self._validate_source_non_overlap(recoding_rules)

        # Check 6: Transformation completeness
        self._validate_transformation_completeness(recoding_rules)

        # Check 7: Target conflicts (warning)
        self._validate_target_conflicts(recoding_rules)

        is_valid = len(self.errors) == 0
        checks_performed = [
            "source_variables_exist",
            "no_duplicate_targets",
            "range_validity",
            "target_uniqueness",
            "source_non_overlap",
            "transformation_completeness",
            "target_conflicts"
        ]

        return ValidationResult(
            is_valid=is_valid,
            errors=self.errors,
            warnings=self.warnings,
            checks_performed=checks_performed
        )

    def _validate_source_variables_exist(self, rules: List[Dict]):
        """Check 1: All source variables must exist in metadata."""
        for rule in rules:
            source_var = rule.get("source_variable")
            if source_var not in self.variable_names:
                self.errors.append(
                    f"Source variable '{source_var}' not found in metadata"
                )

    def _validate_no_duplicate_targets(self, rules: List[Dict]):
        """Check 2: Each target variable must be unique across all rules."""
        target_vars = [rule.get("target_variable") for rule in rules]
        duplicates = [var for var in set(target_vars) if target_vars.count(var) > 1]

        for duplicate in duplicates:
            self.errors.append(
                f"Duplicate target variables: '{duplicate}' appears {target_vars.count(duplicate)} times"
            )

    def _validate_ranges(self, rules: List[Dict]):
        """Check 3: For range rules, ensure start ≤ end."""
        for rule in rules:
            if rule.get("rule_type") != "range":
                continue

            transformations = rule.get("transformations", [])
            for transform in transformations:
                source_range = transform.get("source", [])
                if len(source_range) == 2 and source_range[0] > source_range[1]:
                    self.errors.append(
                        f"Invalid range in {rule['source_variable']}: "
                        f"[{source_range[0]}, {source_range[1]}] - start > end"
                    )

    def _validate_target_uniqueness(self, rules: List[Dict]):
        """Check 4: Target values must be unique within each rule."""
        for rule in rules:
            transformations = rule.get("transformations", [])
            target_values = [t.get("target") for t in transformations]

            duplicates = [val for val in set(target_values) if target_values.count(val) > 1]
            for duplicate in duplicates:
                self.errors.append(
                    f"Duplicate target value {duplicate} in rule for '{rule['source_variable']}'"
                )

    def _validate_source_non_overlap(self, rules: List[Dict]):
        """Check 5: Source values must not overlap within a rule."""
        for rule in rules:
            transformations = rule.get("transformations", [])

            if rule.get("rule_type") == "range":
                # Check for overlapping ranges
                for i, t1 in enumerate(transformations):
                    for t2 in transformations[i+1:]:
                        range1 = t1.get("source", [])
                        range2 = t2.get("source", [])
                        if self._ranges_overlap(range1, range2):
                            self.errors.append(
                                f"Overlapping source ranges in '{rule['source_variable']}': "
                                f"{range1} overlaps with {range2}"
                            )

    def _validate_transformation_completeness(self, rules: List[Dict]):
        """Check 6: All transformations must have non-empty source values."""
        for rule in rules:
            transformations = rule.get("transformations", [])
            for i, transform in enumerate(transformations):
                if not transform.get("source"):
                    self.errors.append(
                        f"Empty source values in transformation {i+1} "
                        f"for '{rule['source_variable']}'"
                    )

    def _validate_target_conflicts(self, rules: List[Dict]):
        """Check 7: Warn if target variables already exist in metadata."""
        for rule in rules:
            target_var = rule.get("target_variable")
            if target_var in self.variable_names:
                self.warnings.append(
                    f"Target variable '{target_var}' already exists in metadata. "
                    f"It will be overwritten."
                )

    @staticmethod
    def _ranges_overlap(range1: List, range2: List) -> bool:
        """Check if two numeric ranges overlap."""
        if len(range1) != 2 or len(range2) != 2:
            return False
        return not (range1[1] < range2[0] or range2[1] < range1[0])


class ValidationResult:
    """Validation result container."""
    def __init__(self, is_valid: bool, errors: List[str], warnings: List[str], checks_performed: List[str]):
        self.is_valid = is_valid
        self.errors = errors
        self.warnings = warnings
        self.checks_performed = checks_performed
```

### 3.2 Indicators Validation

```python
class IndicatorValidator:
    """Validates AI-generated indicators."""

    def __init__(self, metadata: Dict):
        self.metadata = metadata
        self.variable_names = {var["name"] for var in metadata.get("variables", [])}
        self.errors = []
        self.warnings = []

    def validate_all(self, indicators: Dict) -> ValidationResult:
        """
        Perform all validation checks on indicators.
        """
        self.errors = []
        self.warnings = []

        if not isinstance(indicators, dict) or "indicators" not in indicators:
            self.errors.append("Invalid structure: missing 'indicators' key")
            return ValidationResult(is_valid=False, errors=self.errors, warnings=self.warnings)

        indicator_list = indicators["indicators"]

        # Structure validation
        self._validate_structure(indicator_list)

        # Reference validation
        self._validate_references(indicator_list)

        # Uniqueness validation
        self._validate_uniqueness(indicator_list)

        # Non-empty validation
        self._validate_non_empty(indicator_list)

        is_valid = len(self.errors) == 0
        return ValidationResult(is_valid=is_valid, errors=self.errors, warnings=self.warnings, checks_performed=[])

    def _validate_structure(self, indicators: List[Dict]):
        """Check required fields."""
        required_fields = ["name", "variables", "description"]
        for i, indicator in enumerate(indicators):
            for field in required_fields:
                if field not in indicator:
                    self.errors.append(
                        f"Indicator {i+1}: missing required field '{field}'"
                    )

    def _validate_references(self, indicators: List[Dict]):
        """Check all variables exist in metadata."""
        for indicator in indicators:
            variables = indicator.get("variables", [])
            for var in variables:
                if var not in self.variable_names:
                    self.errors.append(
                        f"Variable '{var}' in indicator '{indicator.get('name', 'Unknown')}' "
                        f"not found in metadata"
                    )

    def _validate_uniqueness(self, indicators: List[Dict]):
        """Check indicator names are unique."""
        names = [ind.get("name") for ind in indicators]
        duplicates = [name for name in set(names) if names.count(name) > 1]
        for duplicate in duplicates:
            self.errors.append(f"Duplicate indicator name: '{duplicate}'")

    def _validate_non_empty(self, indicators: List[Dict]):
        """Check each indicator has at least 2 variables."""
        for indicator in indicators:
            variables = indicator.get("variables", [])
            if len(variables) < 2:
                self.errors.append(
                    f"Indicator '{indicator.get('name', 'Unknown')}' has only "
                    f"{len(variables)} variable(s). Minimum: 2."
                )
```

### 3.3 Table Specifications Validation

```python
class TableSpecValidator:
    """Validates AI-generated table specifications."""

    def __init__(self, metadata: Dict):
        self.metadata = metadata
        self.variable_names = {var["name"] for var in metadata.get("variables", [])}
        self.categorical_vars = self._get_categorical_variables()
        self.errors = []
        self.warnings = []

    def _get_categorical_variables(self) -> set:
        """Get set of categorical variable names."""
        categorical = set()
        for var in self.metadata.get("variables", []):
            if var.get("type") in ["numeric", "string"] and len(var.get("values", [])) > 0:
                categorical.add(var["name"])
        return categorical

    def validate_all(self, table_specs: Dict) -> ValidationResult:
        """Perform all validation checks."""
        self.errors = []
        self.warnings = []

        if not isinstance(table_specs, dict) or "tables" not in table_specs:
            self.errors.append("Invalid structure: missing 'tables' key")
            return ValidationResult(is_valid=False, errors=self.errors, warnings=self.warnings)

        tables = table_specs["tables"]

        for table in tables:
            self._validate_table_structure(table)
            self._validate_table_references(table)
            self._validate_table_types(table)
            self._validate_table_statistics(table)

        is_valid = len(self.errors) == 0
        return ValidationResult(is_valid=is_valid, errors=self.errors, warnings=self.warnings, checks_performed=[])

    def _validate_table_structure(self, table: Dict):
        """Check required fields."""
        required_fields = ["name", "rows", "columns", "statistics"]
        for field in required_fields:
            if field not in table:
                self.errors.append(
                    f"Table '{table.get('name', 'Unknown')}': missing field '{field}'"
                )

    def _validate_table_references(self, table: Dict):
        """Check row/column variables exist."""
        rows = table.get("rows")
        columns = table.get("columns")

        if rows and rows not in self.variable_names:
            self.errors.append(
                f"Table '{table['name']}': Row variable '{rows}' not found in metadata"
            )

        if columns and columns not in self.variable_names:
            self.errors.append(
                f"Table '{table['name']}': Column variable '{columns}' not found in metadata"
            )

    def _validate_table_types(self, table: Dict):
        """Check row/column variables are categorical."""
        rows = table.get("rows")
        columns = table.get("columns")

        if rows and rows not in self.categorical_vars:
            self.errors.append(
                f"Table '{table['name']}': Row variable '{rows}' is not categorical"
            )

        if columns and columns not in self.categorical_vars:
            self.errors.append(
                f"Table '{table['name']}': Column variable '{columns}' is not categorical"
            )

    def _validate_table_statistics(self, table: Dict):
        """Check requested statistics are valid."""
        valid_statistics = ["count", "row_percent", "column_percent", "chi_square"]
        statistics = table.get("statistics", [])

        for stat in statistics:
            if stat not in valid_statistics:
                self.warnings.append(
                    f"Table '{table['name']}': Unknown statistic '{stat}'"
                )
```

---

## 4. Step Implementations

### 4.1 Step 1: Extract .sav File (Complete Implementation)

```python
import pyreadstat
from pandas import DataFrame

def extract_spss_node(state: WorkflowState) -> WorkflowState:
    """
    Extract raw survey data and metadata from input .sav file.

    Input:
        - state["spss_file_path"]: Path to input .sav file

    Output:
        - state["raw_data"]: Pandas DataFrame with survey responses
        - state["original_metadata"]: Metadata from pyreadstat
    """
    file_path = state["spss_file_path"]

    try:
        # Read .sav file using pyreadstat
        df, meta = pyreadstat.read_sav(file_path)

        # Store raw data
        state["raw_data"] = df

        # Store metadata
        state["original_metadata"] = {
            "variable_labels": meta.variable_labels,
            "value_labels": meta.value_labels,
            "variable_types": meta.variable_to_type,
            "variable_measurements": meta.variable_measurements,
            "number_of_cases": meta.number_rows,
            "number_of_variables": meta.number_columns
        }

        # Log execution
        state["execution_log"].append({
            "step": "extract_spss",
            "status": "completed",
            "file_path": file_path,
            "rows": len(df),
            "columns": len(df.columns)
        })

    except Exception as e:
        state["errors"].append(f"Failed to extract .sav file: {str(e)}")
        state["execution_log"].append({
            "step": "extract_spss",
            "status": "failed",
            "error": str(e)
        })

    return state
```

### 4.2 Step 2: Transform Metadata (Complete Implementation)

```python
def transform_metadata_node(state: WorkflowState) -> WorkflowState:
    """
    Convert section-based metadata to variable-centered format.

    Input:
        - state["original_metadata"]: Section-based metadata from pyreadstat

    Output:
        - state["variable_centered_metadata"]: List of variable dictionaries
    """
    original = state["original_metadata"]

    try:
        variable_centered = []

        # Get all variable names
        var_names = list(original["variable_labels"].keys())

        for var_name in var_names:
            var_dict = {
                "name": var_name,
                "label": original["variable_labels"].get(var_name, ""),
                "type": original["variable_types"].get(var_name, "unknown"),
                "measurement": original["variable_measurements"].get(var_name, "unknown"),
                "values": []
            }

            # Add value labels if present
            if var_name in original["value_labels"]:
                value_labels = original["value_labels"][var_name]
                for value, label in value_labels.items():
                    var_dict["values"].append({
                        "value": value,
                        "label": label
                    })

            variable_centered.append(var_dict)

        state["variable_centered_metadata"] = variable_centered

        state["execution_log"].append({
            "step": "transform_metadata",
            "status": "completed",
            "variables_transformed": len(variable_centered)
        })

    except Exception as e:
        state["errors"].append(f"Failed to transform metadata: {str(e)}")
        state["execution_log"].append({
            "step": "transform_metadata",
            "status": "failed",
            "error": str(e)
        })

    return state
```

### 4.3 Step 4: Generate Recoding Rules (Complete Implementation)

```python
from langchain_openai import ChatOpenAI

def generate_recoding_rules_node(state: WorkflowState) -> WorkflowState:
    """
    LLM generates recoding rules.
    Builds prompt based on feedback source if retrying.

    Input:
        - state["filtered_metadata"]: Variables needing recoding
        - state["recoding_feedback"]: Feedback from previous iteration (if any)
        - state["recoding_iteration"]: Current iteration number

    Output:
        - state["recoding_rules"]: Generated recoding rules
        - state["recoding_iteration"]: Incremented iteration count
    """
    iteration = state.get("recoding_iteration", 1)
    feedback = state.get("recoding_feedback")
    feedback_source = state.get("recoding_feedback_source")

    # Build prompt based on iteration and feedback source
    if feedback_source == "validation":
        prompt = build_validation_retry_prompt(
            metadata=state["filtered_metadata"],
            validation_result=feedback,
            iteration=iteration
        )
    elif feedback_source == "human":
        prompt = build_human_feedback_prompt(
            metadata=state["filtered_metadata"],
            human_feedback=feedback,
            iteration=iteration
        )
    else:
        prompt = build_initial_recoding_prompt(state["filtered_metadata"])

    try:
        # Initialize LLM
        llm = ChatOpenAI(
            model=state["config"].get("model", "gpt-4"),
            temperature=state["config"].get("temperature", 0.7)
        )

        # Invoke LLM
        response = llm.invoke(prompt)
        content = response.content

        # Parse JSON response
        import json
        # Remove markdown code blocks if present
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        rules = json.loads(content)

        # Validate structure
        if "recoding_rules" not in rules:
            raise ValueError("Missing 'recoding_rules' key in LLM response")

        state["recoding_rules"] = rules
        state["recoding_iteration"] = iteration + 1

        # Save to file
        import json
        rules_path = f"{state['config']['output_dir']}/recoding_rules_iter_{iteration}.json"
        with open(rules_path, 'w') as f:
            json.dump(rules, f, indent=2)
        state["recoding_rules_json_path"] = rules_path

        state["execution_log"].append({
            "step": "generate_recoding_rules",
            "status": "completed",
            "iteration": iteration,
            "rules_count": len(rules.get("recoding_rules", []))
        })

    except Exception as e:
        state["errors"].append(f"Failed to generate recoding rules: {str(e)}")
        state["execution_log"].append({
            "step": "generate_recoding_rules",
            "status": "failed",
            "error": str(e),
            "iteration": iteration
        })

    return state
```

### 4.4 Step 7: Generate PSPP Recoding Syntax (Complete Implementation)

```python
def generate_pspp_recoding_syntax_node(state: WorkflowState) -> WorkflowState:
    """
    Convert validated recoding rules to PSPP syntax.

    Input:
        - state["recoding_rules"]: Validated recoding rules
        - state["spss_file_path"]: Original .sav file path
        - state["config"]["output_dir"]: Output directory

    Output:
        - state["pspp_recoding_syntax"]: PSPP recoding commands
        - state["pspp_recoding_syntax_path"]: Path to saved .sps file
    """
    rules = state["recoding_rules"]["recoding_rules"]
    input_path = state["spss_file_path"]
    output_dir = state["config"]["output_dir"]

    try:
        syntax_lines = []

        # Header
        syntax_lines.append("* Recoding rules generated by AI agent")
        syntax_lines.append(f"GET FILE='{input_path}'.")
        syntax_lines.append("EXECUTE.")
        syntax_lines.append("")

        # Generate RECODE commands for each rule
        for rule in rules:
            source_var = rule["source_variable"]
            target_var = rule["target_variable"]
            rule_type = rule["rule_type"]

            if rule_type == "range":
                # Range-based recoding
                recode_parts = []
                for transform in rule["transformations"]:
                    source_range = transform["source"]
                    target_value = transform["target"]
                    recode_parts.append(f"({source_range[0]} THRU {source_range[1]}={target_value})")

                recode_line = f"RECODE {source_var} {' '.join(recode_parts)} INTO {target_var}."
                syntax_lines.append(recode_line)

            elif rule_type == "value_mapping":
                # Value-based recoding
                recode_parts = []
                for transform in rule["transformations"]:
                    source_range = transform["source"]
                    target_value = transform["target"]
                    if len(source_range) == 1:
                        recode_parts.append(f"({source_range[0]}={target_value})")
                    else:
                        recode_parts.append(f"({source_range[0]} THRU {source_range[1]}={target_value})")

                recode_line = f"RECODE {source_var} {' '.join(recode_parts)} INTO {target_var}."
                syntax_lines.append(recode_line)

            # Variable label
            target_label = rule.get("target_label", target_var)
            syntax_lines.append(f"VARIABLE LABELS {target_var} '{target_label}'.")

            # Value labels
            value_label_parts = []
            for transform in rule["transformations"]:
                target_value = transform["target"]
                target_value_label = transform["label"]
                value_label_parts.append(f"{target_value} '{target_value_label}'")

            syntax_lines.append(f"VALUE LABELS {target_var} {' '.join(value_label_parts)}.")
            syntax_lines.append("EXECUTE.")
            syntax_lines.append("")

        # Save output
        new_data_path = f"{output_dir}/new_data.sav"
        syntax_lines.append(f"SAVE OUTFILE='{new_data_path}'.")

        # Join all lines
        pspp_syntax = "\n".join(syntax_lines)

        # Save to file
        syntax_path = f"{output_dir}/pspp_recoding.sps"
        with open(syntax_path, 'w') as f:
            f.write(pspp_syntax)

        state["pspp_recoding_syntax"] = pspp_syntax
        state["pspp_recoding_syntax_path"] = syntax_path
        state["new_data_path"] = new_data_path

        state["execution_log"].append({
            "step": "generate_pspp_recoding_syntax",
            "status": "completed",
            "syntax_path": syntax_path,
            "rules_processed": len(rules)
        })

    except Exception as e:
        state["errors"].append(f"Failed to generate PSPP syntax: {str(e)}")
        state["execution_log"].append({
            "step": "generate_pspp_recoding_syntax",
            "status": "failed",
            "error": str(e)
        })

    return state
```

---

## 5. PSPP Syntax Reference

### 5.1 Recoding Syntax Examples

#### Age Grouping

```spss
* Age grouping into 5 categories.
RECODE age (18 THRU 24=1) (25 THRU 34=2) (35 THRU 44=3) (45 THRU 54=4) (55 THRU 99=5) INTO age_group.
VARIABLE LABELS age_group 'Respondent Age Group'.
VALUE LABELS age_group 1 '18-24' 2 '25-34' 3 '35-44' 4 '45-54' 5 '55+'.
EXECUTE.
```

#### Top 2 Box for Satisfaction Ratings

```spss
* Top 2 Box for 10-point satisfaction scale.
RECODE q5_rating (1 THRU 8=0) (9 THRU 10=1) INTO q5_rating_top2box.
VARIABLE LABELS q5_rating_top2box 'Satisfaction - Top 2 Box (9-10)'.
VALUE LABELS q5_rating_top2box 0 'Others' 1 'Top 2 Box'.
EXECUTE.
```

#### Value Mapping for Categorical Variables

```spss
* Group detailed categories into broader groups.
RECODE region (1=1) (2=1) (3=2) (4=2) (5=3) INTO region_group.
VARIABLE LABELS region_group 'Geographic Region Group'.
VALUE LABELS region_group 1 'North' 2 'South' 3 'West'.
EXECUTE.
```

### 5.2 Cross-Table Syntax Examples

#### Simple Two-Way Table

```spss
* Gender by Age Group crosstabulation.
CTABLES
  /VLABELS VARIABLES=gender age_group DISPLAY=DEFAULT
  /TABLE gender BY age_group
  /CRITERIA CILEVEL=95.
```

#### Table with Statistics

```spss
* Gender by Satisfaction with statistics.
CTABLES
  /VLABELS VARIABLES=gender sat_top2box DISPLAY=DEFAULT
  /TABLE gender BY sat_top2box
  /STATISTICS
    count ('Count')
    columnpct ('Column %')
    chisq ('Chi-Square')
  /CRITERIA CILEVEL=95.
```

#### Weighted Table

```spss
* Weighted crosstabulation.
CTABLES
  /VLABELS VARIABLES=gender age_group DISPLAY=DEFAULT
  /TABLE gender BY age_group
  /SLICES=weight_var
  /STATISTICS
    count ('Weighted Count')
    columnpct ('Weighted Column %')
  /CRITERIA CILEVEL=95.
```

---

## 6. Statistical Analysis

### 6.1 Python Statistics Script Generation

```python
def generate_python_statistics_script_node(state: WorkflowState) -> WorkflowState:
    """
    Generate Python script to compute Chi-square tests and Cramer's V.

    Input:
        - state["table_specifications"]: Table definitions
        - state["cross_table_json_path"]: Cross-table metadata

    Output:
        - state["python_stats_script"]: Generated Python script
        - state["python_stats_script_path"]: Path to .py file
    """
    import json

    try:
        # Load table specifications
        with open(state["cross_table_json_path"], 'r') as f:
            table_data = json.load(f)

        # Generate Python script
        script_lines = [
            "import pandas as pd",
            "import json",
            "from scipy.stats import chi2_contingency",
            "import numpy as np",
            "",
            "def compute_cramers_v(contingency_table):",
            "    \"\"\"Compute Cramer's V effect size.\"\"\"",
            "    chi2 = chi2_contingency(contingency_table)[0]",
            "    n = contingency_table.sum()",
            "    phi2 = chi2 / n",
            "    r, k = contingency_table.shape",
            "    phi2_corrected = max(0, phi2 - ((k-1)*(r-1))/(n-1))",
            "    v_corrected = np.sqrt(phi2_corrected / min((k-1), (r-1)))",
            "    return v_corrected",
            "",
            "def interpret_cramers_v(v):",
            "    \"\"\"Interpret Cramer's V effect size.\"\"\"",
            "    if v < 0.1:",
            "        return 'negligible'",
            "    elif v < 0.3:",
            "        return 'small'",
            "    elif v < 0.5:",
            "        return 'medium'",
            "    else:",
            "        return 'large'",
            "",
            "# Load cross-table data",
            "with open('" + state["cross_table_csv_path"] + "', 'r') as f:",
            "    csv_data = pd.read_csv(f)",
            "",
            "with open('" + state["cross_table_json_path"] + "', 'r') as f:",
            "    json_data = json.load(f)",
            "",
            "# Initialize results",
            "all_results = []",
            "",
            "# Process each table",
            "for table in json_data['tables']:",
            "    table_name = table['name']",
            "    rows_var = table['rows']",
            "    cols_var = table['columns']",
            "    ",
            "    # Extract contingency table from CSV data",
            "    # (Implementation depends on CSV structure)",
            "    contingency_table = extract_contingency_table(csv_data, table)",
            "    ",
            "    # Compute Chi-square test",
            "    chi2, p_value, dof, expected = chi2_contingency(contingency_table)",
            "    ",
            "    # Compute Cramer's V",
            "    cramers_v = compute_cramers_v(contingency_table)",
            "    ",
            "    # Store results",
            "    result = {",
            "        'table_name': table_name,",
            "        'chi_square': float(chi2),",
            "        'p_value': float(p_value),",
            "        'degrees_of_freedom': int(dof),",
            "        'cramers_v': float(cramers_v),",
            "        'interpretation': interpret_cramers_v(cramers_v),",
            "        'sample_size': int(contingency_table.sum())",
            "    }",
            "    all_results.append(result)",
            "",
            "# Save results",
            "with open('" + state["config"]["output_dir"] + "/statistical_analysis_summary.json', 'w') as f:",
            "    json.dump(all_results, f, indent=2)",
            "",
            "print(f'Processed {len(all_results)} tables')"
        ]

        script = "\n".join(script_lines)

        # Save script
        script_path = f"{state['config']['output_dir']}/python_stats_script.py"
        with open(script_path, 'w') as f:
            f.write(script)

        state["python_stats_script"] = script
        state["python_stats_script_path"] = script_path

        state["execution_log"].append({
            "step": "generate_python_statistics_script",
            "status": "completed",
            "script_path": script_path
        })

    except Exception as e:
        state["errors"].append(f"Failed to generate statistics script: {str(e)}")

    return state
```

---

## 7. Output Generation

### 7.1 PowerPoint Generation

```python
from pptx import Presentation
from pptx.util import Inches

def generate_powerpoint_node(state: WorkflowState) -> WorkflowState:
    """
    Create PowerPoint presentation with charts from significant tables.

    Input:
        - state["significant_tables_json_path"]: Filtered table data
        - state["statistical_summary"]: Statistical test results

    Output:
        - state["powerpoint_path"]: Path to generated .pptx file
    """
    import json
    import pandas as pd

    try:
        # Load data
        with open(state["significant_tables_json_path"], 'r') as f:
            tables = json.load(f)

        with open(state["config"]["output_dir"] + "/statistical_analysis_summary.json", 'r') as f:
            stats = json.load(f)

        # Create presentation
        prs = Presentation()

        # Title slide
        title_slide = prs.slides.add_slide(prs.slide_layouts[0])
        title = title_slide.shapes.title
        subtitle = title_slide.placeholders[1]
        title.text = "Survey Analysis Results"
        subtitle.text = f"Generated on {pd.Timestamp.now().strftime('%Y-%m-%d')}"

        # Add slides for each table
        for table_data in tables:
            table_name = table_data["name"]

            # Find matching statistics
            table_stats = next((s for s in stats if s["table_name"] == table_name), None)

            # Create slide
            slide = prs.slides.add_slide(prs.slide_layouts[5])

            # Add title
            title_shape = slide.shapes.title
            title_shape.text = table_name

            # Add statistics summary
            if table_stats:
                stats_text = (
                    f"Chi-Square: {table_stats['chi_square']:.3f}\n"
                    f"p-value: {table_stats['p_value']:.4f}\n"
                    f"Cramer's V: {table_stats['cramers_v']:.3f} ({table_stats['interpretation']})"
                )

                left = Inches(0.5)
                top = Inches(1.5)
                width = Inches(9)
                height = Inches(1)
                textbox = slide.shapes.add_textbox(left, top, width, height)
                text_frame = textbox.text_frame
                text_frame.text = stats_text

            # Add table
            # (Implementation depends on data structure)
            # add_table_to_slide(slide, table_data)

        # Save presentation
        ppt_path = f"{state['config']['output_dir']}/survey_analysis.pptx"
        prs.save(ppt_path)

        state["powerpoint_path"] = ppt_path

        state["execution_log"].append({
            "step": "generate_powerpoint",
            "status": "completed",
            "ppt_path": ppt_path,
            "tables_included": len(tables)
        })

    except Exception as e:
        state["errors"].append(f"Failed to generate PowerPoint: {str(e)}")

    return state
```

### 7.2 HTML Dashboard Generation

```python
def generate_html_dashboard_node(state: WorkflowState) -> WorkflowState:
    """
    Create interactive HTML dashboard with all tables.

    Input:
        - state["cross_table_csv_path"]: All cross-table data
        - state["cross_table_json_path"]: Table metadata
        - state["statistical_summary"]: Statistical results

    Output:
        - state["html_dashboard_path"]: Path to generated .html file
    """
    import json
    import pandas as pd

    try:
        # Load data
        with open(state["cross_table_json_path"], 'r') as f:
            tables = json.load(f)

        with open(state["config"]["output_dir"] + "/statistical_analysis_summary.json", 'r') as f:
            stats = json.load(f)

        # Generate HTML
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Survey Analysis Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .sidebar {{ float: left; width: 250px; }}
        .content {{ margin-left: 270px; }}
        .table-card {{ border: 1px solid #ddd; padding: 20px; margin-bottom: 20px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: center; }}
        th {{ background-color: #4CAF50; color: white; }}
        .significant {{ background-color: #ffffcc; }}
        canvas {{ max-width: 100%; }}
    </style>
</head>
<body>
    <h1>Survey Analysis Dashboard</h1>
    <p>Generated on {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}</p>

    <div class="sidebar">
        <h3>Tables</h3>
        <ul>
"""

        # Add navigation links
        for table_data in tables:
            table_id = table_data["name"].replace(" ", "_").lower()
            html_content += f'            <li><a href="#{table_id}">{table_data["name"]}</a></li>\n'

        html_content += "        </ul>\n    </div>\n\n    <div class=\"content\">\n"

        # Add tables
        for table_data in tables:
            table_name = table_data["name"]
            table_id = table_name.replace(" ", "_").lower()

            # Find statistics
            table_stats = next((s for s in stats if s["table_name"] == table_name), None)

            # Determine if significant
            is_sig = table_stats and table_stats["p_value"] < 0.05
            sig_class = "significant" if is_sig else ""

            html_content += f"""
        <div class="table-card {sig_class}" id="{table_id}">
            <h2>{table_name}</h2>
"""

            if table_stats:
                html_content += f"""
            <p><strong>Statistical Summary:</strong></p>
            <ul>
                <li>Chi-Square: {table_stats["chi_square"]:.3f}</li>
                <li>p-value: {table_stats["p_value"]:.4f}</li>
                <li>Cramer's V: {table_stats["cramers_v"]:.3f} ({table_stats["interpretation"]})</li>
                <li>Sample Size: {table_stats["sample_size"]}</li>
            </ul>
"""

            # Add table (implementation depends on data structure)
            html_content += "            <table>\n"
            # ... add table rows
            html_content += "            </table>\n"

            # Add chart canvas
            chart_canvas_id = f"chart_{table_id}"
            html_content += f"""
            <h3>Chart</h3>
            <canvas id="{chart_canvas_id}"></canvas>
            <script>
                // Chart implementation for {table_name}
                // ... chart.js code
            </script>
"""

            html_content += "        </div>\n"

        html_content += """
    </div>
</body>
</html>
"""

        # Save HTML
        html_path = f"{state['config']['output_dir']}/survey_dashboard.html"
        with open(html_path, 'w') as f:
            f.write(html_content)

        state["html_dashboard_path"] = html_path

        state["execution_log"].append({
            "step": "generate_html_dashboard",
            "status": "completed",
            "html_path": html_path,
            "tables_included": len(tables)
        })

    except Exception as e:
        state["errors"].append(f"Failed to generate HTML dashboard: {str(e)}")

    return state
```

---

## Appendix

### A. Utility Functions

```python
def format_metadata_for_llm(metadata: List[Dict]) -> str:
    """Format metadata for LLM prompt."""
    lines = []
    for var in metadata:
        line = f"- {var['name']}: {var['label']}"
        if var.get('values'):
            value_str = ", ".join([f"{v['value']}={v['label']}" for v in var['values']])
            line += f" [{value_str}]"
        lines.append(line)
    return "\n".join(lines)


def format_errors_list(errors: List[str]) -> str:
    """Format errors for prompt."""
    return "\n".join([f"{i+1}. {error}" for i, error in enumerate(errors)])


def format_warnings_list(warnings: List[str]) -> str:
    """Format warnings for prompt."""
    return "\n".join([f"{i+1}. {warning}" for i, warning in enumerate(warnings)])


def format_issues_list(issues: List[str]) -> str:
    """Format issues for prompt."""
    return "\n".join([f"- {issue}" for issue in issues])


def format_suggestions_list(suggestions: List[str]) -> str:
    """Format suggestions for prompt."""
    return "\n".join([f"- {suggestion}" for suggestion in suggestions])
```

### B. Edge Routing Functions

```python
def should_retry_recoding(state: WorkflowState) -> str:
    """
    Route based on recoding validation result.
    """
    validation = state["recoding_validation"]
    iteration = state["recoding_iteration"]
    max_iterations = state["config"].get("max_self_correction_iterations", 3)

    if validation["is_valid"]:
        return "review_recoding_rules"
    elif iteration >= max_iterations:
        return "review_recoding_rules"
    else:
        state["recoding_feedback"] = validation
        state["recoding_feedback_source"] = "validation"
        return "generate_recoding_rules"


def should_approve_recoding(state: WorkflowState) -> str:
    """
    Route based on human review decision.
    """
    if state["recoding_approved"]:
        return "generate_pspp_recoding_syntax"
    else:
        return "generate_recoding_rules"
```

---

**Document Version**: This document provides complete implementation details for the Survey Analysis & Visualization Workflow. For architectural overview, see [Survey Analysis Workflow Design](./SURVEY_ANALYSIS_WORKFLOW_DESIGN.md).
