# Survey Analysis Detailed Specifications

> This document contains complete implementation details for the Survey Analysis & Visualization Workflow. For the concise workflow design and architecture overview, refer to [Workflow Architecture](./workflow-architecture.md).

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
    new_metadata: Dict[str, Any]              # Complete metadata extracted from new_data.sav (all variables)

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
    statistical_summary: List[Dict]           # Summary of all statistical tests (loaded from file)


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
    charts_generated: List[Dict]             # Chart metadata (populated in both Steps 21 and 22)


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
| 8 | `RecodingState` | `new_data_path`, `new_metadata` | All recoding fields now populated |
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

    Args:
        filtered_metadata: List of variable dictionaries requiring recoding

    Returns:
        Formatted prompt string for LLM
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

    Args:
        metadata: Original metadata for reference
        validation_result: Previous validation result with errors
        iteration: Current iteration number

    Returns:
        Formatted prompt string with error context
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

    Args:
        metadata: Original metadata for reference
        human_feedback: Human review feedback with issues and suggestions
        iteration: Current iteration number

    Returns:
        Formatted prompt string with human feedback context
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
def build_initial_indicators_prompt(new_metadata: Dict) -> str:
    """
    Generate initial prompt for indicator grouping.

    Args:
        new_metadata: Complete metadata from new_data.sav

    Returns:
        Formatted prompt string for LLM
    """
    prompt = f"""You are a market research analyst. Group survey variables into semantic indicators.

PRINCIPLES:
1. Group variables that measure the same underlying concept
2. Create indicators for multi-item scales (e.g., satisfaction scales)
3. Group demographic variables separately
4. Limit to 3-7 variables per indicator

INPUT METADATA:
{format_metadata_for_llm(new_metadata)}

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
    new_metadata: Dict,
    indicators: List[Dict]
) -> str:
    """
    Generate initial prompt for table specification.

    Args:
        new_metadata: Complete metadata from new_data.sav
        indicators: Approved indicator definitions

    Returns:
        Formatted prompt string for LLM
    """
    prompt = f"""You are a market research analyst. Define cross-tabulation tables for analysis.

PRINCIPLES:
1. Create tables comparing demographics against satisfaction indicators
2. Use categorical variables in rows and columns
3. Include count and column percentages
4. Limit to tables with meaningful relationships

INPUT METADATA:
{format_metadata_for_llm(new_metadata)}

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

    def __init__(self, is_valid: bool, errors: List[str], warnings: List[str], checks_performed: List[str] = None):
        self.is_valid = is_valid
        self.errors = errors
        self.warnings = warnings
        self.checks_performed = checks_performed or []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for state storage."""
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "checks_performed": self.checks_performed
        }
```

### 3.2 Indicators Validation

```python
class IndicatorValidator:
    """Validates AI-generated indicators."""

    def __init__(self, new_metadata: Dict):
        self.new_metadata = new_metadata
        self.variable_names = {var["name"] for var in new_metadata.get("variables", [])}
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

    def __init__(self, new_metadata: Dict):
        self.new_metadata = new_metadata
        self.variable_names = {var["name"] for var in new_metadata.get("variables", [])}
        self.categorical_vars = self._get_categorical_variables()
        self.errors = []
        self.warnings = []

    def _get_categorical_variables(self) -> set:
        """Get set of categorical variable names."""
        categorical = set()
        for var in self.new_metadata.get("variables", []):
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

### 4.3 Step 3: Preliminary Filtering (Complete Implementation)

**Node**: `filter_metadata_node`

**Purpose**: Filter out variables that don't need recoding to reduce AI context.

**Input**:
- `variable_centered_metadata`: All variables from transformed metadata
- `config` containing:
  - `cardinality_threshold`: Max distinct values (default: 30)
  - `filter_binary`: Whether to filter binary variables (default: true)
  - `filter_other_text`: Whether to filter "other" text fields (default: true)

**Filtering Rules**:

| Rule | Condition | Reason |
|------|-----------|--------|
| Binary variables | Exactly 2 distinct values | No room for recoding |
| High cardinality | Distinct values > threshold | Typically IDs, open-ended |
| Other text fields | Name contains "other" AND type is character | Open-ended feedback |

**Output**:
- `filtered_metadata`: Variables needing recoding
- `filtered_out_variables`: Excluded variables with reasons

**Implementation**:

```python
def filter_metadata_node(state: WorkflowState) -> WorkflowState:
    """
    Filter out variables that don't need recoding to reduce AI context.

    Input:
        - state["variable_centered_metadata"]: All variables from transformed metadata
        - state["config"]: Configuration parameters

    Output:
        - state["filtered_metadata"]: Variables passing filters (need recoding)
        - state["filtered_out_variables"]: Excluded variables with reasons
    """
    variable_centered_metadata = state["variable_centered_metadata"]
    config = state.get("config", {})

    # Get filtering configuration parameters
    cardinality_threshold = config.get("cardinality_threshold", 30)
    filter_binary = config.get("filter_binary", True)
    filter_other_text = config.get("filter_other_text", True)

    filtered_metadata = []
    filtered_out_variables = []

    for variable in variable_centered_metadata:
        var_name = variable.get("name")
        var_type = variable.get("type", "unknown")
        values = variable.get("values", [])
        num_distinct = len(values)

        # Rule 1: Binary variables (exactly 2 distinct values)
        if filter_binary and num_distinct == 2:
            filtered_out_variables.append({
                "name": var_name,
                "reason": "Binary variable (2 distinct values) - no room for recoding",
                "rule": "binary",
                "distinct_count": num_distinct
            })
            continue

        # Rule 2: High cardinality (distinct values > threshold)
        if num_distinct > cardinality_threshold:
            filtered_out_variables.append({
                "name": var_name,
                "reason": f"High cardinality ({num_distinct} distinct values) - typically IDs or open-ended",
                "rule": "high_cardinality",
                "distinct_count": num_distinct
            })
            continue

        # Rule 3: Other text fields (name contains "other" AND type is character/string)
        if filter_other_text and "other" in var_name.lower() and var_type in ["string", "character"]:
            filtered_out_variables.append({
                "name": var_name,
                "reason": "Other text field - open-ended feedback",
                "rule": "other_text",
                "type": var_type
            })
            continue

        # Variable passes all filters
        filtered_metadata.append(variable)

    # Store results in state
    state["filtered_metadata"] = filtered_metadata
    state["filtered_out_variables"] = filtered_out_variables

    # Log execution
    state["execution_log"].append({
        "step": "filter_metadata",
        "status": "completed",
        "total_variables": len(variable_centered_metadata),
        "filtered_in": len(filtered_metadata),
        "filtered_out": len(filtered_out_variables),
        "filters_applied": {
            "binary": filter_binary,
            "high_cardinality": f">{cardinality_threshold}",
            "other_text": filter_other_text
        }
    })

    return state
```

### 4.4 Step 4: Generate Recoding Rules (Complete Implementation)

```python
from langchain_openai import ChatOpenAI
import json

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

### 4.5 Step 7: Generate PSPP Recoding Syntax (Complete Implementation)

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

### 6.1 Helper Functions for Contingency Table Extraction

```python
def extract_contingency_table_from_csv(
    csv_data: pd.DataFrame,
    table_name: str,
    rows_var: str,
    cols_var: str
) -> pd.DataFrame:
    """
    Extract contingency table from cross-table CSV data.

    Args:
        csv_data: DataFrame containing cross-table data
        table_name: Name of the table to extract
        rows_var: Row variable name
        cols_var: Column variable name

    Returns:
        Contingency table as DataFrame with counts
    """
    # Filter data for the specific table
    table_data = csv_data[
        (csv_data['table_name'] == table_name) &
        (csv_data['row_var'] == rows_var) &
        (csv_data['col_var'] == cols_var)
    ]

    # Pivot to create contingency table
    contingency = table_data.pivot_table(
        index='row_value',
        columns='col_value',
        values='count',
        fill_value=0
    )

    return contingency
```

### 6.2 Python Statistics Script Generation

```python
import json
import subprocess

def generate_python_statistics_script_node(state: WorkflowState) -> WorkflowState:
    """
    Generate Python script to compute Chi-square tests and Cramer's V.

    Input:
        - state["table_specifications"]: Table definitions
        - state["cross_table_json_path"]: Cross-table metadata
        - state["cross_table_csv_path"]: Cross-table data
        - state["config"]["output_dir"]: Output directory

    Output:
        - state["python_stats_script"]: Generated Python script
        - state["python_stats_script_path"]: Path to .py file
    """

    try:
        # Load table specifications
        with open(state["cross_table_json_path"], 'r') as f:
            table_data = json.load(f)

        output_dir = state["config"].get("output_dir", "output")
        csv_path = state["cross_table_csv_path"]
        json_path = state["cross_table_json_path"]

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
            f"with open('{csv_path}', 'r') as f:",
            "    csv_data = pd.read_csv(f)",
            "",
            f"with open('{json_path}', 'r') as f:",
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
            f"with open('{output_dir}/statistical_analysis_summary.json', 'w') as f:",
            "    json.dump(all_results, f, indent=2)",
            "",
            "print(f'Processed {len(all_results)} tables')"
        ]

        script = "\n".join(script_lines)

        # Save script
        script_path = f"{output_dir}/python_stats_script.py"
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
        state["execution_log"].append({
            "step": "generate_python_statistics_script",
            "status": "failed",
            "error": str(e)
        })

    return state


def execute_python_statistics_script_node(state: WorkflowState) -> WorkflowState:
    """
    Execute generated Python script to compute statistical tests.

    Input:
        - state["python_stats_script_path"]: Path to Python script

    Output:
        - state["statistical_summary"]: Loaded from generated JSON file
        - state["statistical_summary_path"]: Path to JSON file
    """

    try:
        script_path = state["python_stats_script_path"]
        output_dir = state["config"].get("output_dir", "output")
        summary_path = f"{output_dir}/statistical_analysis_summary.json"

        # Execute the Python script
        result = subprocess.run(
            ["python", script_path],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )

        if result.returncode != 0:
            raise RuntimeError(f"Script execution failed: {result.stderr}")

        # Load the generated statistical summary
        with open(summary_path, 'r') as f:
            statistical_summary = json.load(f)

        state["statistical_summary"] = statistical_summary
        state["statistical_summary_path"] = summary_path

        state["execution_log"].append({
            "step": "execute_python_statistics_script",
            "status": "completed",
            "tables_processed": len(statistical_summary)
        })

    except Exception as e:
        state["errors"].append(f"Failed to execute statistics script: {str(e)}")
        state["execution_log"].append({
            "step": "execute_python_statistics_script",
            "status": "failed",
            "error": str(e)
        })

    return state
```

---

## 7. Output Generation

### 7.1 Helper Functions for PowerPoint

```python
def add_contingency_table_to_slide(slide, table_data: pd.DataFrame, position):
    """
    Add a contingency table to a PowerPoint slide.

    Args:
        slide: PowerPoint slide object
        table_data: DataFrame with the table data
        position: Tuple of (left, top, width, height) in Inches
    """
    from pptx.util import Inches

    left, top, width, height = position

    # Create table shape
    rows, cols = table_data.shape
    table_shape = slide.shapes.add_table(
        rows + 1,  # +1 for header row
        cols,
        left,
        top,
        width,
        height
    )

    # Get the table
    table = table_shape.table

    # Set header row
    for col_idx, col_name in enumerate(table_data.columns):
        cell = table.cell(0, col_idx)
        cell.text = str(col_name)
        # Apply header formatting
        for paragraph in cell.text_frame.paragraphs:
            paragraph.font.bold = True

    # Fill data rows
    for row_idx, (row_name, row_data) in enumerate(table_data.iterrows()):
        # First column is the row name/index
        table.cell(row_idx + 1, 0).text = str(row_name)

        # Fill data cells
        for col_idx, value in enumerate(row_data):
            table.cell(row_idx + 1, col_idx + 1).text = str(int(value) if pd.notna(value) else "0")
```

### 7.2 PowerPoint Generation with Native Editable Charts

> **Implementation File**: `workflow/nodes/presentation.py`

This section describes the complete implementation of PowerPoint generation with **native editable charts** for cross-tabulation survey data. The implementation creates professional presentations with bar charts, stacked bar charts, and horizontal bar charts based on table dimensions.

**Key Feature**: Charts are created using python-pptx's `add_chart()` API, making them **fully editable** in PowerPoint, LibreOffice Impress, and compatible applications. Users can:
- Modify data directly in the spreadsheet editor
- Change chart type (bar → line, pie, etc.)
- Adjust styling, colors, and fonts
- Edit labels and titles
- All through the standard PowerPoint interface

#### 7.2.1 Main Node Function

```python
def generate_powerpoint(state: State) -> State:
    """
    Create PowerPoint presentation with native editable charts from significant tables.

    This is the main node for Phase 7 (Step 21) of the workflow. It:
    1. Loads significant tables from JSON file
    2. Loads statistical summary (Chi-square, p-value, Cramer's V)
    3. Generates a slide for each table with:
       - Slide title
       - Native PowerPoint bar chart or stacked bar chart (editable!)
       - Statistical summary text below the chart

    Charts are created using python-pptx's add_chart() API, making them fully
    editable in PowerPoint, LibreOffice Impress, and other compatible applications.
    Users can modify data, change chart types, adjust styling, and edit labels.

    Input state fields:
        - significant_tables_json_path: Path to filtered significant tables JSON
        - statistical_summary_path: Path to statistical test results JSON
        - config["output_dir"]: Output directory for PowerPoint file

    Output state fields:
        - powerpoint_path: Path to generated .pptx file
        - charts_generated: List of chart metadata (table_name, chart_type, statistics)

    Args:
        state: Current workflow state

    Returns:
        Updated state with PowerPoint generation results
    """
    try:
        output_dir = state.get("config", {}).get("output_dir", "output")
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Load data files
        tables = _load_significant_tables(state["significant_tables_json_path"])
        statistics = _load_statistical_summary(state["statistical_summary_path"])

        if not tables:
            return {
                **state,
                "warnings": state.get("warnings", []) + [
                    "No significant tables found. PowerPoint generation skipped."
                ],
                "execution_log": state.get("execution_log", []) + [{
                    "step": "generate_powerpoint",
                    "status": "skipped",
                    "reason": "no_significant_tables"
                }]
            }

        # Create presentation with native charts
        ppt_path, charts_generated = _create_presentation_with_native_charts(
            tables=tables,
            statistics=statistics,
            output_dir=output_dir
        )

        return {
            **state,
            "powerpoint_path": ppt_path,
            "charts_generated": charts_generated,
            "messages": [
                *state.get("messages", []),
                {
                    "role": "assistant",
                    "content": f"Generated PowerPoint with {len(charts_generated)} native editable chart slides"
                }
            ],
            "execution_log": state.get("execution_log", []) + [{
                "step": "generate_powerpoint",
                "status": "completed",
                "ppt_path": ppt_path,
                "charts_generated": len(charts_generated)
            }]
        }

    except Exception as e:
        return {
            **state,
            "errors": state.get("errors", []) + [
                f"Failed to generate PowerPoint: {str(e)}"
            ],
            "execution_log": state.get("execution_log", []) + [{
                "step": "generate_powerpoint",
                "status": "failed",
                "error": str(e)
            }]
        }
```

#### 7.2.2 Data Loading Functions

```python
def _load_significant_tables(json_path: str) -> List[Dict[str, Any]]:
    """
    Load significant tables from JSON file.

    Args:
        json_path: Path to significant_tables JSON file

    Returns:
        List of table dictionaries with structure:
        {
            "name": str,
            "rows": str,  # row variable name
            "columns": str,  # column variable name
            "data": {
                "row_labels": List[str],
                "column_labels": List[str],
                "counts": List[List[int]],  # 2D array of counts
                "row_percentages": List[List[float]],  # optional
                "column_percentages": List[List[float]]  # optional
            }
        }
    """
    with open(json_path, 'r') as f:
        data = json.load(f)

    # Handle different JSON structures
    if isinstance(data, dict):
        if "tables" in data:
            return data["tables"]
        elif "significant_tables" in data:
            return data["significant_tables"]
        else:
            # Assume the dict itself contains table data
            return [data]
    elif isinstance(data, list):
        return data

    raise ValueError(f"Unexpected JSON structure in {json_path}")


def _load_statistical_summary(json_path: str) -> List[Dict[str, Any]]:
    """
    Load statistical summary from JSON file.

    Args:
        json_path: Path to statistical_analysis_summary JSON file

    Returns:
        List of statistical result dictionaries with structure:
        {
            "table_name": str,
            "chi_square": float,
            "p_value": float,
            "degrees_of_freedom": int,
            "cramers_v": float,
            "interpretation": str,  # "negligible", "small", "medium", "large"
            "sample_size": int
        }
    """
    with open(json_path, 'r') as f:
        data = json.load(f)

    if isinstance(data, dict) and "results" in data:
        return data["results"]
    elif isinstance(data, list):
        return data

    raise ValueError(f"Unexpected JSON structure in {json_path}")
```

#### 7.2.3 Native Chart Creation with add_chart()

```python
def _add_table_slide_with_native_chart(
    prs,
    table_data: Dict[str, Any],
    statistics: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Add a slide with native editable PowerPoint chart for a single table.

    Args:
        prs: PowerPoint Presentation object
        table_data: Table data including labels and counts
        statistics: Statistical test results (optional)

    Returns:
        Chart metadata dictionary

    Slide Layout:
        - Title at top (0.3" from top)
        - Native chart in center (1.0" to 4.0" from top, 9" wide)
        - Statistics text at bottom (4.2" from top)
    """
    from pptx.util import Inches, Pt
    from pptx.enum.chart import XL_CHART_TYPE
    from pptx.chart.data import CategoryChartData

    table_name = table_data.get("name", "Unnamed Table")

    # Create blank slide
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    # Add title
    title_left = Inches(0.5)
    title_top = Inches(0.3)
    title_width = Inches(9)
    title_height = Inches(0.5)

    title_box = slide.shapes.add_textbox(title_left, title_top, title_width, title_height)
    title_frame = title_box.text_frame
    title_frame.text = table_name
    title_para = title_frame.paragraphs[0]
    title_para.font.size = Pt(28)
    title_para.font.bold = True

    # Extract table data
    chart_data_input = table_data.get("data", {})
    row_labels = chart_data_input.get("row_labels", [])
    col_labels = chart_data_input.get("column_labels", [])
    counts = chart_data_input.get("counts", [])

    n_rows = len(row_labels)
    n_cols = len(col_labels)

    # Determine chart type based on table dimensions
    chart_type, xl_chart_type = _determine_chart_type(n_rows, n_cols)

    # Prepare chart data for python-pptx
    category_chart_data = _prepare_category_chart_data(
        row_labels=row_labels,
        col_labels=col_labels,
        counts=counts,
        chart_type=chart_type
    )

    # Add native chart to slide using add_chart() API
    chart_left = Inches(0.5)
    chart_top = Inches(1.0)
    chart_width = Inches(9)
    chart_height = Inches(3.0)

    chart = slide.shapes.add_chart(
        xl_chart_type,
        chart_left,
        chart_top,
        chart_width,
        chart_height,
        category_chart_data
    ).chart

    # Configure chart appearance
    _configure_chart_style(chart, table_name, chart_type)

    # Add statistics summary text box (bottom portion)
    if statistics:
        stats_left = Inches(0.5)
        stats_top = Inches(4.2)
        stats_width = Inches(9)
        stats_height = Inches(1.2)

        stats_text = (
            f"Statistical Summary:\n"
            f"Chi-Square: {statistics['chi_square']:.3f}  |  "
            f"p-value: {statistics['p_value']:.4f}  |  "
            f"Cramer's V: {statistics['cramers_v']:.3f} ({statistics['interpretation']})"
        )

        stats_box = slide.shapes.add_textbox(stats_left, stats_top, stats_width, stats_height)
        stats_frame = stats_box.text_frame
        stats_frame.word_wrap = True
        stats_frame.text = stats_text

        # Format statistics text
        stats_para = stats_frame.paragraphs[0]
        stats_para.font.size = Pt(14)
        stats_para.font.color.rgb = _get_rgb_color(64, 64, 64)

    # Return chart metadata
    return {
        "table_name": table_name,
        "chart_type": chart_type,
        "dimensions": f"{n_rows}x{n_cols}",
        "statistics": statistics
    }
```

#### 7.2.4 Chart Type Selection

```python
def _determine_chart_type(n_rows: int, n_cols: int) -> Tuple[str, int]:
    """
    Determine the best chart type based on table dimensions.

    Args:
        n_rows: Number of rows in the table
        n_cols: Number of columns in the table

    Returns:
        Tuple of (chart_type_string, xl_chart_type_enum)
        - chart_type_string: "bar", "stacked_bar", or "horizontal_bar"
        - xl_chart_type_enum: XL_CHART_TYPE enum value
    """
    from pptx.enum.chart import XL_CHART_TYPE

    # For 2x2 tables, use clustered column chart
    if n_rows == 2 and n_cols == 2:
        return "bar", XL_CHART_TYPE.COLUMN_CLUSTERED

    # For tables with many rows, use horizontal bar chart
    if n_rows > 5:
        return "horizontal_bar", XL_CHART_TYPE.BAR_CLUSTERED

    # For tables with many columns, use stacked bar chart
    if n_cols > 4:
        return "stacked_bar", XL_CHART_TYPE.COLUMN_STACKED_100

    # Default to clustered column chart
    return "bar", XL_CHART_TYPE.COLUMN_CLUSTERED
```

#### 7.2.5 Chart Data Preparation for CategoryChartData

```python
def _prepare_category_chart_data(
    row_labels: List[str],
    col_labels: List[str],
    counts: List[List[int]],
    chart_type: str
) -> 'CategoryChartData':
    """
    Transform cross-tabulation data to python-pptx CategoryChartData format.

    Args:
        row_labels: Labels for row categories
        col_labels: Labels for column categories
        counts: 2D array of counts [row][col]
        chart_type: Type of chart ("bar", "horizontal_bar", "stacked_bar")

    Returns:
        CategoryChartData object ready for add_chart()

    Data Transformation:
        - Row labels become chart categories (x-axis)
        - Each column label becomes a data series
        - Counts become series values
    """
    from pptx.chart.data import CategoryChartData

    # Create chart data
    chart_data = CategoryChartData()

    # Add categories (row labels become chart categories)
    chart_data.categories = row_labels

    # For each column label, create a data series
    for col_idx, col_label in enumerate(col_labels):
        # Extract data for this series (one value per row/category)
        series_data = [counts[row_idx][col_idx] for row_idx in range(len(row_labels))]

        # Add series to chart data
        chart_data.add_series(col_label, series_data)

    return chart_data
```

**Example Data Transformation**:
```
Input Table:
           Male  Female
18-24       10      12
25-34       25      28
35-44       30      35

Output CategoryChartData:
- categories: ["18-24", "25-34", "35-44"]
- series[0]: name="Male", data=[10, 25, 30]
- series[1]: name="Female", data=[12, 28, 35]
```

#### 7.2.6 Chart Styling Configuration

```python
def _configure_chart_style(chart, table_name: str, chart_type: str) -> None:
    """
    Configure chart styling for professional presentation.

    Args:
        chart: PowerPoint chart object
        table_name: Name for chart title
        chart_type: Type of chart being configured
    """
    from pptx.util import Pt

    # Set chart title
    if chart.has_title:
        title = chart.chart_title
        title.text_frame.text = table_name
        title.text_frame.paragraphs[0].font.size = Pt(14)
        title.text_frame.paragraphs[0].font.bold = True

    # Apply professional color scheme
    _apply_chart_colors(chart, chart_type)

    # Display legend
    if chart.has_legend:
        legend = chart.legend
        legend.include_in_layout = False
        legend.position = 2  # Right side

    # Set axis titles if applicable
    _set_axis_titles(chart, chart_type)
```

```python
def _apply_chart_colors(chart, chart_type: str) -> None:
    """
    Apply professional color scheme to chart series.

    Args:
        chart: PowerPoint chart object
        chart_type: Type of chart

    Color Palette (Market Research Standard):
        Blue:     #2E86AB (46, 134, 171)
        Purple:   #A23B72 (162, 59, 114)
        Orange:   #F18F01 (241, 143, 1)
        Red:      #C73E1D (199, 62, 29)
        Green:    #6A994E (106, 153, 78)
        Maroon:   #BC4B51 (188, 75, 81)
        Steel:    #5C6E8A (92, 110, 138)
        Olive:    #88B04B (136, 176, 75)
    """
    # Market research professional color palette
    colors_rgb = [
        (46, 134, 171),   # Blue #2E86AB
        (162, 59, 114),   # Purple #A23B72
        (241, 143, 1),    # Orange #F18F01
        (199, 62, 29),    # Red #C73E1D
        (106, 153, 78),   # Green #6A994E
        (188, 75, 81),    # Maroon #BC4B51
        (92, 110, 138),   # Steel Blue #5C6E8A
        (136, 176, 75),   # Olive Green #88B04B
    ]

    # Apply colors to each series
    for idx, series in enumerate(chart.series):
        if idx < len(colors_rgb):
            r, g, b = colors_rgb[idx]
            series.format.fill.solid()
            series.format.fill.fore_color.rgb = _get_rgb_color(r, g, b)
```

#### 7.2.7 Title Slide Creation

```python
def _add_title_slide(prs) -> None:
    """
    Add title slide to presentation.

    Args:
        prs: PowerPoint Presentation object

    Layout:
        - "Survey Analysis Results" as main title
        - Current date as subtitle
        - Centered text
        - Professional formatting
    """
    from pptx.util import Inches, Pt
    from datetime import datetime

    # Use blank layout for custom title slide
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    # Add title
    left = Inches(1)
    top = Inches(2)
    width = Inches(8)
    height = Inches(1)

    title_box = slide.shapes.add_textbox(left, top, width, height)
    title_frame = title_box.text_frame
    title_frame.text = "Survey Analysis Results"
    title_para = title_frame.paragraphs[0]
    title_para.font.size = Pt(44)
    title_para.font.bold = True
    title_para.alignment = 1  # Center

    # Add subtitle with date
    top = Inches(3.2)
    subtitle_box = slide.shapes.add_textbox(left, top, width, height)
    subtitle_frame = subtitle_box.text_frame
    subtitle_frame.text = f"Generated on {datetime.now().strftime('%B %d, %Y')}"
    subtitle_para = subtitle_frame.paragraphs[0]
    subtitle_para.font.size = Pt(18)
    subtitle_para.alignment = 1  # Center
```

#### 7.2.8 Error Handling

```python
def _add_error_slide(prs, table_name: str, error_message: str) -> None:
    """
    Add a slide with error message when chart generation fails.

    Args:
        prs: PowerPoint Presentation object
        table_name: Name of the table that failed
        error_message: Error message to display

    This ensures the presentation is still generated even if
    individual charts fail. The error slide documents what went
    wrong for debugging purposes.
    """
    from pptx.util import Inches, Pt
    from pptx.enum.text import PP_ALIGN

    slide = prs.slides.add_slide(prs.slide_layouts[6])

    # Add title
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(9), Inches(0.5))
    title_frame = title_box.text_frame
    title_frame.text = f"{table_name} - Chart Generation Failed"
    title_para = title_frame.paragraphs[0]
    title_para.font.size = Pt(24)
    title_para.font.bold = True
    title_para.font.color.rgb = _get_rgb_color(192, 0, 0)

    # Add error message
    error_box = slide.shapes.add_textbox(Inches(1), Inches(2), Inches(8), Inches(2))
    error_frame = error_box.text_frame
    error_frame.text = f"Error: {error_message}"
    error_para = error_frame.paragraphs[0]
    error_para.font.size = Pt(14)
    error_para.alignment = PP_ALIGN.CENTER
```

#### 7.2.9 RGB Color Helper

```python
def _get_rgb_color(r: int, g: int, b: int):
    """
    Create an RGB color object for python-pptx.

    Args:
        r: Red component (0-255)
        g: Green component (0-255)
        b: Blue component (0-255)

    Returns:
        RGB color object compatible with python-pptx
    """
    try:
        from pptx.util import RGBColor as PptxRGBColor
        return PptxRGBColor(r, g, b)
    except ImportError:
        # Fallback for older python-pptx versions
        class RGBColor:
            def __init__(self, r: int, g: int, b: int):
                self.r = r
                self.g = g
                self.b = b
        return RGBColor(r, g, b)
```

#### 7.2.10 Usage Example

```python
from workflow.nodes import generate_powerpoint

# State should have these fields populated:
state = {
    "significant_tables_json_path": "output/significant_tables.json",
    "statistical_summary_path": "output/statistical_analysis_summary.json",
    "config": {
        "output_dir": "output"
    },
    "messages": [],
    "execution_log": [],
    "errors": [],
    "warnings": []
}

# Generate PowerPoint
updated_state = generate_powerpoint(state)

# Results:
# - updated_state["powerpoint_path"] = "output/survey_analysis_with_charts.pptx"
# - updated_state["charts_generated"] = [
#     {
#         "table_name": "Gender by Satisfaction",
#         "chart_type": "bar",
#         "dimensions": "2x5",
#         "statistics": {...}
#     },
#     ...
# ]
```

#### 7.2.11 Sample Data Format

**significant_tables.json:**
```json
{
    "tables": [
        {
            "name": "Gender by Satisfaction",
            "rows": "gender",
            "columns": "satisfaction",
            "data": {
                "row_labels": ["Male", "Female"],
                "column_labels": ["Very Dissatisfied", "Dissatisfied", "Neutral", "Satisfied", "Very Satisfied"],
                "counts": [
                    [10, 15, 25, 40, 30],
                    [12, 18, 20, 35, 45]
                ]
            }
        }
    ]
}
```

**statistical_analysis_summary.json:**
```json
[
    {
        "table_name": "Gender by Satisfaction",
        "chi_square": 2.456,
        "p_value": 0.652,
        "degrees_of_freedom": 4,
        "cramers_v": 0.067,
        "interpretation": "negligible",
        "sample_size": 250
    }
]
```

#### 7.2.12 Dependencies

Required Python packages:
```bash
pip install python-pptx
```

- **python-pptx**: PowerPoint file manipulation with native chart support
  - `from pptx import Presentation`
  - `from pptx.util import Inches, Pt`
  - `from pptx.enum.chart import XL_CHART_TYPE`
  - `from pptx.chart.data import CategoryChartData`

**No matplotlib required** - charts are native PowerPoint objects!

#### 7.2.13 Complete Implementation Location

The complete implementation is located in:
- **File**: `workflow/nodes/presentation.py`
- **Export**: `workflow/nodes/__init__.py` (as `generate_powerpoint`)
- **State**: Uses `State` from `workflow/state.py`

The implementation includes:
1. **Native chart generation** with `add_chart()` API (no matplotlib)
2. **Smart chart type selection** based on table dimensions
3. **Professional color scheme** for market research presentations
4. **Editable charts** - modify data, change types, adjust styling in PowerPoint
5. **Error handling** that continues on individual failures
6. **CategoryChartData** transformation from cross-tabulation format
7. **Title slide** with date
8. **Statistical summary** display on each slide
9. **Type hints and docstrings** throughout
5. Temporary image cleanup after embedding in PowerPoint
6. Statistical summary display on each slide
7. Title slide with date
8. Type hints and docstrings throughout

### 7.3 HTML Dashboard Generation

```python
import json

def generate_html_dashboard_node(state: WorkflowState) -> WorkflowState:
    """
    Create interactive HTML dashboard with all tables.

    Input:
        - state["cross_table_csv_path"]: All cross-table data
        - state["cross_table_json_path"]: Table metadata
        - state["statistical_summary_path"]: Path to statistical results JSON
        - state["config"]["output_dir"]: Output directory

    Output:
        - state["html_dashboard_path"]: Path to generated .html file
        - state["charts_generated"]: List of chart metadata
    """

    try:
        output_dir = state["config"].get("output_dir", "output")

        # Load data
        with open(state["cross_table_json_path"], 'r') as f:
            tables = json.load(f)

        with open(state["statistical_summary_path"], 'r') as f:
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

        # Generate chart metadata
        charts_generated = []

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

                # Add to chart metadata
                charts_generated.append({
                    "table_name": table_name,
                    "table_id": table_id,
                    "significant": is_sig,
                    "statistics": table_stats
                })

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
        html_path = f"{output_dir}/survey_dashboard.html"
        with open(html_path, 'w') as f:
            f.write(html_content)

        state["html_dashboard_path"] = html_path

        # Add to existing charts_generated or create new
        if "charts_generated" in state:
            state["charts_generated"].extend(charts_generated)
        else:
            state["charts_generated"] = charts_generated

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
        state["recoding_feedback_source"] = "human"
        return "generate_recoding_rules"


def should_retry_indicators(state: WorkflowState) -> str:
    """Route based on indicators validation result."""
    validation = state["indicators_validation"]
    iteration = state["indicators_iteration"]
    max_iterations = state["config"].get("max_self_correction_iterations", 3)

    if validation["is_valid"]:
        return "review_indicators"
    elif iteration >= max_iterations:
        return "review_indicators"
    else:
        state["indicators_feedback"] = validation
        state["indicators_feedback_source"] = "validation"
        return "generate_indicators"


def should_approve_indicators(state: WorkflowState) -> str:
    """Route based on human review decision for indicators."""
    if state["indicators_approved"]:
        return "generate_table_specifications"
    else:
        state["indicators_feedback_source"] = "human"
        return "generate_indicators"


def should_retry_table_specs(state: WorkflowState) -> str:
    """Route based on table specs validation result."""
    validation = state["table_specs_validation"]
    iteration = state["table_specs_iteration"]
    max_iterations = state["config"].get("max_self_correction_iterations", 3)

    if validation["is_valid"]:
        return "review_table_specifications"
    elif iteration >= max_iterations:
        return "review_table_specifications"
    else:
        state["table_specs_feedback"] = validation
        state["table_specs_feedback_source"] = "validation"
        return "generate_table_specifications"


def should_approve_table_specs(state: WorkflowState) -> str:
    """Route based on human review decision for table specs."""
    if state["table_specs_approved"]:
        return "generate_pspp_table_syntax"
    else:
        state["table_specs_feedback_source"] = "human"
        return "generate_table_specifications"
```

---

For the concise workflow design and architecture overview, see [Survey Analysis Workflow Design](./SURVEY_ANALYSIS_WORKFLOW_DESIGN.md).
