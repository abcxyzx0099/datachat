"""
Prompt builders for LangGraph survey analysis workflow.

This module provides structured prompt builders for all AI-powered tasks
in the survey analysis workflow. Each prompt builder follows a consistent
pattern with three variants:
- initial: First generation with metadata/context
- validation_retry: After validation failure
- human_feedback: After human rejection with feedback

Prompt Builders:
    build_recoding_prompt: For Step 4 (Recoding Rules Generation)
    build_indicators_prompt: For Step 8 (Indicator Construction)
    build_table_specs_prompt: For Step 9 (Table Specifications)
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json


# ============================================================================
# FORMATTING HELPERS
# ============================================================================

def _format_metadata_table(metadata: List[Dict[str, Any]]) -> str:
    """
    Format variable metadata into a markdown table.

    Args:
        metadata: List of variable metadata dictionaries

    Returns:
        Markdown table string
    """
    lines = ["| Variable | Type | Label | Range/Values | Missing |"]
    lines.append("|----------|------|-------|--------------|---------|")

    for var in metadata:
        name = var.get("name", "N/A")
        var_type = var.get("variable_type", "unknown")
        label = var.get("label", "N/A")

        # Format range or values
        if var_type == "numeric":
            min_val = var.get("min_value")
            max_val = var.get("max_value")
            if min_val is not None and max_val is not None:
                range_str = f"{min_val} - {max_val}"
            else:
                range_str = "N/A"
        else:
            categories = var.get("categories")
            value_labels = var.get("value_labels", {})
            if categories:
                range_str = f"{len(categories)} categories"
            elif value_labels:
                range_str = f"{len(value_labels)} values"
            else:
                range_str = "N/A"

        # Format missing values
        missing = var.get("missing_values", [])
        missing_str = f"{len(missing)} values" if missing else "None"

        lines.append(
            f"| {name} | {var_type} | {label} | {range_str} | {missing_str} |"
        )

    return "\n".join(lines)


def _format_validation_errors(validation_result: Dict[str, Any]) -> str:
    """
    Format validation errors into a structured markdown section.

    Args:
        validation_result: ValidationResult dictionary with errors and warnings

    Returns:
        Formatted error section
    """
    errors = validation_result.get("errors", [])
    warnings = validation_result.get("warnings", [])

    sections = []

    if errors:
        sections.append("**Critical Errors:**")
        for i, error in enumerate(errors, 1):
            sections.append(f"{i}. {error}")
        sections.append("")

    if warnings:
        sections.append("**Warnings:**")
        for i, warning in enumerate(warnings, 1):
            sections.append(f"{i}. {warning}")
        sections.append("")

    if not errors and not warnings:
        sections.append("No validation errors found.")

    return "\n".join(sections)


def _format_rules_json(rules: List[Dict[str, Any]]) -> str:
    """
    Format rules as JSON for display in prompts.

    Args:
        rules: List of rule dictionaries

    Returns:
        JSON-formatted string
    """
    return json.dumps(rules, indent=2)


def _format_indicators_json(indicators: List[Dict[str, Any]]) -> str:
    """
    Format indicators as JSON for display in prompts.

    Args:
        indicators: List of indicator dictionaries

    Returns:
        JSON-formatted string
    """
    return json.dumps(indicators, indent=2)


def _format_table_specs_json(table_specs: List[Dict[str, Any]]) -> str:
    """
    Format table specifications as JSON for display in prompts.

    Args:
        table_specs: List of table specification dictionaries

    Returns:
        JSON-formatted string
    """
    return json.dumps(table_specs, indent=2)


# ============================================================================
# RECODING RULES PROMPT BUILDER (Step 4)
# ============================================================================

class RecodingPromptBuilder:
    """
    Prompt builder for recoding rules generation (Step 4).

    Generates prompts for three scenarios:
    - Initial generation with metadata
    - Validation retry after failure
    - Human feedback incorporation
    """

    @staticmethod
    def build_initial_prompt(
        metadata: List[Dict[str, Any]],
        config: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Build the initial prompt for recoding rules generation.

        Args:
            metadata: List of variable metadata dictionaries
            config: Optional configuration parameters

        Returns:
            Prompt string for the LLM
        """
        config = config or {}
        metadata_table = _format_metadata_table(metadata)

        prompt = f"""# Recoding Rules Generation

You are an expert in survey data analysis and variable recoding. Your task is to generate
recoding rules for survey variables based on their metadata and analysis requirements.

## Input Variable Metadata

{metadata_table}

## Recoding Rule Types

You should generate rules of the following types:

### 1. Range Grouping
Group continuous numeric values into meaningful ranges.
- **Example**: Age (18-99) → age_group (18-24, 25-34, 35-44, 45-54, 55-64, 65+)
- **Use cases**: Age groups, income brackets, frequency distributions

### 2. Value Mapping
Map specific values to new values (relabeling or consolidation).
- **Example**: Reverse coding (1→5, 2→4, 3→3, 4→2, 5→1)
- **Example**: Category consolidation (1,2→1, 3,4→2, 5→3)
- **Use cases**: Scale reversal, category simplification

### 3. Derived Variables
Create new variables based on transformations of existing variables.
- **Example**: Top-2-box (values 9-10 → 1, others → 0)
- **Example**: Bottom-3-box (values 1-3 → 1, others → 0)
- **Example**: Middle category (value 3 → 1, others → 0)
- **Use cases**: Satisfaction summarization, response clustering

### 4. Category Grouping
Group categorical values into broader categories.
- **Example**: Multiple choice responses into "Yes", "No", "Other"
- **Use cases**: Response simplification, creating meaningful aggregations

## Output Format

Return a JSON object with the following structure:

```json
{{
  "recoding_rules": [
    {{
      "source_variable": "original_var_name",
      "target_variable": "new_var_name",
      "rule_type": "range|mapping|derived|category",
      "transformations": [
        {{
          "source": [value_or_range],
          "target": target_value,
          "label": "Human readable label"
        }}
      ],
      "rationale": "Explanation of why this recoding makes sense for the analysis"
    }}
  ],
  "generation_notes": "Any notes about the recoding decisions made"
}}
```

### Field Descriptions

- **source_variable**: Name of the original variable from the metadata
- **target_variable**: Name for the new recoded variable (use descriptive names)
- **rule_type**: One of: range, mapping, derived, category
- **transformations**: Array of transformation objects:
  - **source**: Source value(s) - single value [5] or range [1, 3] for inclusive range
  - **target**: Target value to assign
  - **label**: Human-readable label for the target value
- **rationale**: Why this recoding is useful for analysis

## Guidelines

### Quality Requirements
- Only generate rules for variables that would benefit from recoding
- Use descriptive, meaningful variable names (e.g., `age_group` not `var1_recoded`)
- Ensure all transformations are logically sound and complete
- Create non-overlapping ranges for range grouping
- Preserve data integrity (no loss of information without good reason)

### Range Grouping Best Practices
- Create ranges that make analytical sense (e.g., standard age cohorts)
- Ensure all possible values are covered
- Use inclusive ranges: [1, 3] means 1, 2, and 3
- Avoid gaps between ranges

### Derived Variable Best Practices
- Clearly explain the business logic in the rationale
- Use common patterns (top-box, bottom-box, middle) when applicable
- Ensure derived variables are interpretable

### Example Output

```json
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
      ],
      "rationale": "Standard age cohorts for demographic analysis"
    }},
    {{
      "source_variable": "satisfaction",
      "target_variable": "sat_top2box",
      "rule_type": "derived",
      "transformations": [
        {{"source": [9, 10], "target": 1, "label": "Top 2 Box"}},
        {{"source": [0, 8], "target": 0, "label": "Other"}}
      ],
      "rationale": "Identify highly satisfied respondents (scores 9-10)"
    }}
  ],
  "generation_notes": "Generated 2 recoding rules based on analysis needs"
}}
```

## Task

Generate appropriate recoding rules for the provided variables. Focus on creating
rules that will be most useful for subsequent statistical analysis and reporting.
"""
        return prompt

    @staticmethod
    def build_validation_retry_prompt(
        metadata: List[Dict[str, Any]],
        previous_rules: List[Dict[str, Any]],
        validation_result: Dict[str, Any],
        iteration: int,
        config: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Build a prompt for retrying after validation failure.

        Args:
            metadata: List of variable metadata dictionaries
            previous_rules: Rules from the previous iteration
            validation_result: Validation result with errors
            iteration: Current iteration number
            config: Optional configuration parameters

        Returns:
            Prompt string for the LLM
        """
        config = config or {}
        metadata_table = _format_metadata_table(metadata)
        errors_formatted = _format_validation_errors(validation_result)
        rules_json = _format_rules_json(previous_rules)

        prompt = f"""# Recoding Rules Generation - Validation Retry (Iteration {iteration})

Your previous attempt at generating recoding rules failed validation. Please review
the errors below and generate corrected rules.

## Input Variable Metadata

{metadata_table}

## Validation Errors from Previous Attempt

{errors_formatted}

## Previous Rules (For Reference)

```json
{rules_json}
```

## Instructions for This Iteration

You MUST address ALL of the validation errors listed above. Common issues include:

### Source Variable Errors
- **Issue**: Referenced variable does not exist in metadata
- **Fix**: Use only variable names from the metadata table above

### Range Errors
- **Issue**: Invalid ranges (e.g., start > end, negative ranges)
- **Fix**: Ensure [start, end] where start <= end

### Transformation Errors
- **Issue**: Incomplete or overlapping transformations
- **Fix**: Ensure all possible values are covered with no overlaps

### Duplicate Target Variables
- **Issue**: Multiple rules creating the same target variable
- **Fix**: Use unique target variable names

## Output Format

Return a JSON object with the following structure:

```json
{{
  "recoding_rules": [
    {{
      "source_variable": "original_var_name",
      "target_variable": "new_var_name",
      "rule_type": "range|mapping|derived|category",
      "transformations": [
        {{
          "source": [value_or_range],
          "target": target_value,
          "label": "Human readable label"
        }}
      ],
      "rationale": "Explanation of the recoding"
    }}
  ],
  "correction_notes": "Explanation of how validation errors were fixed"
}}
```

## Validation Checklist

Before returning, verify your rules address:
- [ ] All source variables exist in the metadata
- [ ] All ranges are valid (start <= end)
- [ ] All target variable names are unique
- [ ] All transformations are complete and non-overlapping
- [ ] All source values are within the variable's range

Generate corrected recoding rules now.
"""
        return prompt

    @staticmethod
    def build_human_feedback_prompt(
        metadata: List[Dict[str, Any]],
        previous_rules: List[Dict[str, Any]],
        feedback: str,
        iteration: int,
        config: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Build a prompt for incorporating human feedback.

        Args:
            metadata: List of variable metadata dictionaries
            previous_rules: Rules from the previous iteration
            feedback: Human feedback/comments
            iteration: Current iteration number
            config: Optional configuration parameters

        Returns:
            Prompt string for the LLM
        """
        config = config or {}
        metadata_table = _format_metadata_table(metadata)
        rules_json = _format_rules_json(previous_rules)

        prompt = f"""# Recoding Rules Generation - Human Feedback (Iteration {iteration})

A human analyst has reviewed your previous recoding rules and provided feedback.
Please revise the rules based on their comments.

## Input Variable Metadata

{metadata_table}

## Human Feedback

{feedback}

## Previous Rules (For Reference)

```json
{rules_json}
```

## Instructions

Carefully review the human feedback above and revise your recoding rules accordingly.
The analyst has domain expertise and their suggestions should guide your revisions.

### Common Feedback Types

**Analysis Focus**: "We need to focus on X segment"
- Adjust your rules to highlight the relevant segment

**Grouping Preferences**: "Use different age groups"
- Modify your range groupings to match preferences

**Business Logic**: "Our standard approach is..."
- Align your derived variables with business practices

**Clarity**: "Variable names should be..."
- Improve naming and labeling for clarity

## Output Format

Return a JSON object with the following structure:

```json
{{
  "recoding_rules": [
    {{
      "source_variable": "original_var_name",
      "target_variable": "new_var_name",
      "rule_type": "range|mapping|derived|category",
      "transformations": [
        {{
          "source": [value_or_range],
          "target": target_value,
          "label": "Human readable label"
        }}
      ],
      "rationale": "Explanation of the recoding"
    }}
  ],
  "revision_notes": "Explanation of how human feedback was incorporated"
}}
```

Generate revised recoding rules that address the human feedback.
"""
        return prompt


# ============================================================================
# INDICATORS PROMPT BUILDER (Step 8)
# ============================================================================

class IndicatorsPromptBuilder:
    """
    Prompt builder for indicator construction (Step 8).

    Generates prompts for three scenarios:
    - Initial generation with variable metadata
    - Validation retry after failure
    - Human feedback incorporation
    """

    @staticmethod
    def build_initial_prompt(
        metadata: List[Dict[str, Any]],
        recoding_rules: Optional[List[Dict[str, Any]]] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Build the initial prompt for indicator generation.

        Args:
            metadata: List of variable metadata dictionaries
            recoding_rules: Optional list of previously generated recoding rules
            config: Optional configuration parameters

        Returns:
            Prompt string for the LLM
        """
        config = config or {}
        metadata_table = _format_metadata_table(metadata)

        recoding_context = ""
        if recoding_rules:
            recoding_context = f"""

## Previously Generated Recoding Rules

The following recoding rules were generated earlier and may be useful:

```json
{_format_rules_json(recoding_rules)}
```

You can reference the recoded variables (target_variable) in your indicators.
"""

        prompt = f"""# Indicator Construction

You are an expert in survey analysis and indicator construction. Your task is to
design meaningful indicators (composite measures) for statistical analysis.

## Available Variables

{metadata_table}
{recoding_context}

## What Are Indicators?

Indicators are composite measures created from multiple variables or through
transformations that capture key constructs for analysis. They simplify complex
data into interpretable metrics.

## Indicator Types

### 1. Index Scores
Combine multiple related variables into a single score.
- **Example**: Customer Satisfaction Index = mean(satisfaction, quality, value)
- **Formula**: (var1 + var2 + var3) / 3 or weighted average
- **Use case**: Overall satisfaction, brand perception, NPS

### 2. Scales and Summations
Sum or average responses across related items.
- **Example**: "Agreement scale" = sum(q1, q2, q3, q4, q5)
- **Formula**: Sum or average of variables
- **Use case**: Likert scales, agreement indices

### 3. Categorical Indicators
Create binary flags based on complex conditions.
- **Example**: "High value customer" = (purchase_freq > 4 AND spend > 100)
- **Formula**: Logical combinations with AND/OR
- **Use case**: Segment identification, response classification

### 4. Derived Metrics
Mathematical transformations of single or multiple variables.
- **Example**: "Tenure in years" = (current_date - signup_date) / 365
- **Formula**: Mathematical expressions
- **Use case**: Time-based metrics, ratios, percentages

## Output Format

Return a JSON object with the following structure:

```json
{{
  "indicators": [
    {{
      "id": "IND_001",
      "description": "What this indicator measures and why it's useful",
      "metric": "average|percentage|distribution",
      "underlying_variables": ["var1", "var2", "var3"]
    }}
  ],
  "generation_notes": "Notes about indicator design decisions"
}}
```

### Field Descriptions

- **id**: Unique identifier for the indicator (use IND_XXX format)
- **description**: What the indicator measures and its analytical purpose
- **metric**: Type of aggregation:
  - `average`: Use for rating scales (numeric) - each variable becomes ONE ROW
  - `percentage`: Use for binary variables (0/1) - creates MULTIPLE RESPONSE SET
  - `distribution`: Use for categorical variables - creates SEPARATE TABLE per variable
- **underlying_variables**: List of source variable names used in the indicator

## Guidelines

### Best Practices
- Use variables that measure related constructs
- Ensure variables have compatible scales before averaging
- Provide clear descriptions
- Use established measurement approaches when available

### Metric Selection
- **average**: For 1-10 scales, 1-7 scales, Likert scales (numeric variables)
- **percentage**: For select all that apply, checkbox questions (binary 0/1 variables)
- **distribution**: For single-select questions, demographics (categorical variables)

### Example Output

```json
{{
  "indicators": [
    {{
      "id": "IND_001",
      "description": "Customer Satisfaction Index combining product quality, service, and value ratings",
      "metric": "average",
      "underlying_variables": ["prod_quality", "service_quality", "value_rating"]
    }},
    {{
      "id": "IND_002",
      "description": "Brand awareness across multiple brands (yes/no for each)",
      "metric": "percentage",
      "underlying_variables": ["aware_brand_a", "aware_brand_b", "aware_brand_c"]
    }},
    {{
      "id": "IND_003",
      "description": "Gender distribution of respondents",
      "metric": "distribution",
      "underlying_variables": ["gender"]
    }}
  ],
  "generation_notes": "Created 3 indicators: satisfaction index, brand awareness, and demographics"
}}
```

## Task

Generate meaningful indicators based on the available variables. Focus on creating
indicators that will support the statistical analysis and cross-tabulation goals.
"""
        return prompt

    @staticmethod
    def build_validation_retry_prompt(
        metadata: List[Dict[str, Any]],
        previous_indicators: List[Dict[str, Any]],
        validation_result: Dict[str, Any],
        iteration: int,
        config: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Build a prompt for retrying after validation failure.

        Args:
            metadata: List of variable metadata dictionaries
            previous_indicators: Indicators from the previous iteration
            validation_result: Validation result with errors
            iteration: Current iteration number
            config: Optional configuration parameters

        Returns:
            Prompt string for the LLM
        """
        config = config or {}
        metadata_table = _format_metadata_table(metadata)
        errors_formatted = _format_validation_errors(validation_result)
        indicators_json = _format_indicators_json(previous_indicators)

        prompt = f"""# Indicator Construction - Validation Retry (Iteration {iteration})

Your previous attempt at generating indicators failed validation. Please review
the errors below and generate corrected indicators.

## Available Variables

{metadata_table}

## Validation Errors from Previous Attempt

{errors_formatted}

## Previous Indicators (For Reference)

```json
{indicators_json}
```

## Instructions for This Iteration

You MUST address ALL of the validation errors listed above. Common issues include:

### Variable Reference Errors
- **Issue**: Referenced variable does not exist in metadata
- **Fix**: Use only variable names from the metadata table above

### Metric Errors
- **Issue**: Invalid metric type or mismatch with variable type
- **Fix**: Use valid metric: average (numeric), percentage (binary), distribution (categorical)

### Duplicate IDs
- **Issue**: Multiple indicators with the same id
- **Fix**: Ensure each indicator has a unique IND_XXX id

### Empty Variables
- **Issue**: Indicator with no underlying_variables
- **Fix**: Each indicator must have at least one underlying variable

## Output Format

Return a JSON object with the following structure:

```json
{{
  "indicators": [
    {{
      "id": "IND_001",
      "description": "What this indicator measures",
      "metric": "average|percentage|distribution",
      "underlying_variables": ["var1", "var2"]
    }}
  ],
  "correction_notes": "Explanation of how validation errors were fixed"
}}
```

## Validation Checklist

Before returning, verify:
- [ ] All variables in underlying_variables exist in the metadata
- [ ] All metrics are valid (average, percentage, or distribution)
- [ ] All indicator IDs are unique
- [ ] Each indicator has at least one underlying variable
- [ ] Metric matches variable type (average for numeric, percentage for binary, distribution for categorical)

Generate corrected indicators now.
"""
        return prompt

    @staticmethod
    def build_human_feedback_prompt(
        metadata: List[Dict[str, Any]],
        previous_indicators: List[Dict[str, Any]],
        feedback: str,
        iteration: int,
        config: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Build a prompt for incorporating human feedback.

        Args:
            metadata: List of variable metadata dictionaries
            previous_indicators: Indicators from the previous iteration
            feedback: Human feedback/comments
            iteration: Current iteration number
            config: Optional configuration parameters

        Returns:
            Prompt string for the LLM
        """
        config = config or {}
        metadata_table = _format_metadata_table(metadata)
        indicators_json = _format_indicators_json(previous_indicators)

        prompt = f"""# Indicator Construction - Human Feedback (Iteration {iteration})

A human analyst has reviewed your previous indicators and provided feedback.
Please revise the indicators based on their comments.

## Available Variables

{metadata_table}

## Human Feedback

{feedback}

## Previous Indicators (For Reference)

```json
{indicators_json}
```

## Instructions

Carefully review the human feedback and revise your indicators accordingly.
The analyst has domain expertise and measurement theory knowledge.

### Common Feedback Types

**Conceptual Changes**: "We need to measure X differently"
- Restructure the indicator to capture the intended construct

**Variable Selection**: "Use different variables"
- Swap variables or adjust the variable composition

**Metric Adjustments**: "Change the metric to..."
- Modify the metric type (average/percentage/distribution)

**Grouping**: "Group these variables separately"
- Split or combine indicators as suggested

## Output Format

Return a JSON object with the following structure:

```json
{{
  "indicators": [
    {{
      "id": "IND_001",
      "description": "What this indicator measures",
      "metric": "average|percentage|distribution",
      "underlying_variables": ["var1", "var2"]
    }}
  ],
  "revision_notes": "Explanation of how human feedback was incorporated"
}}
```

Generate revised indicators that address the human feedback.
"""
        return prompt


# ============================================================================
# TABLE SPECIFICATIONS PROMPT BUILDER (Step 9)
# ============================================================================

class TableSpecsPromptBuilder:
    """
    Prompt builder for table specifications generation (Step 9).

    Generates prompts for three scenarios:
    - Initial generation with indicators
    - Validation retry after failure
    - Human feedback incorporation
    """

    @staticmethod
    def build_initial_prompt(
        metadata: List[Dict[str, Any]],
        indicators: List[Dict[str, Any]],
        config: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Build the initial prompt for table specifications generation.

        Args:
            metadata: List of variable metadata dictionaries
            indicators: List of generated indicators
            config: Optional configuration parameters

        Returns:
            Prompt string for the LLM
        """
        config = config or {}
        indicators_formatted = _format_indicators_for_table_specs(indicators)

        # Identify potential weighting variable from metadata
        weighting_candidates = [
            var for var in metadata
            if "weight" in var.get("name", "").lower()
            or "weight" in var.get("label", "").lower()
        ]

        weighting_context = ""
        if weighting_candidates:
            weighting_context = f"""

## Weighting Variables

The following variables appear to be weighting variables:
{', '.join([v['name'] for v in weighting_candidates])}

Consider using appropriate weighting variables in table specifications.
"""

        prompt = f"""# Cross-Table Specifications Generation

You are an expert in survey analysis and cross-tabulation design. Your task is to
specify cross-tabulations (crosstabs) that will reveal meaningful insights from the
survey data.

## Available Indicators

{indicators_formatted}
{weighting_context}

## What Are Cross-Tabulations?

Cross-tabulations (crosstabs) are tables that display the relationship between
two or more indicators. They are essential for:
- Finding associations between variables
- Identifying patterns across segments
- Supporting statistical analysis (chi-square tests)

## Table Guidelines

### 1. Create Meaningful Crosstabs
Pair indicators that have logical relationships. Demographics vs metrics is common.

### 2. Demographics in Columns
Typically put demographic indicators (distribution metric) as columns.

### 3. No Overlap
An indicator should not appear in both rows and columns of the same table.

### 4. Set Minimum Sample Size
Use min_count (typically 30) for reliable statistics.

### 5. Identify Weighting Variable
If available, include the weighting variable name for weighted analysis.

## Output Format

```json
{{
  "tables": [
    {{
      "id": "TABLE_001",
      "description": "Table description",
      "row_indicators": ["IND_001", "IND_002"],
      "column_indicators": ["IND_003"],
      "sort_rows": "none|asc|desc",
      "sort_columns": "none|asc|desc",
      "min_count": 30
    }}
  ],
  "weighting_variable": "weight_var_name"
}}
```

### Field Descriptions

- **id**: Unique table identifier (TABLE_XXX format)
- **description**: What the table shows and why it's useful
- **row_indicators**: Indicators for table rows (typically metrics/outcomes)
- **column_indicators**: Indicators for table columns (typically demographics/segments)
- **sort_rows**: Sort order for rows ("none", "asc", "desc")
- **sort_columns**: Sort order for columns ("none", "asc", "desc")
- **min_count**: Minimum cell count for filtering (default: 30)
- **weighting_variable**: Optional variable to weight the data

## Sorting Guidelines

- **none**: Keep original order (use for categorical with meaningful order)
- **asc**: Ascending order (use for counts, percentages)
- **desc**: Descending order (use for ranking, highest values first)

## Example Output

```json
{{
  "tables": [
    {{
      "id": "TABLE_001",
      "description": "Satisfaction metrics by age group and gender",
      "row_indicators": ["IND_001", "IND_004"],
      "column_indicators": ["IND_003"],
      "sort_rows": "desc",
      "sort_columns": "none",
      "min_count": 30
    }},
    {{
      "id": "TABLE_002",
      "description": "Brand awareness by region",
      "row_indicators": ["IND_002"],
      "column_indicators": ["IND_005"],
      "sort_rows": "none",
      "sort_columns": "none",
      "min_count": 30
    }}
  ],
  "weighting_variable": "weight"
}}
```

## Task

Generate a comprehensive set of table specifications that will support statistical
analysis and insight generation. Prioritize tables that answer key research questions.
"""
        return prompt

    @staticmethod
    def build_validation_retry_prompt(
        metadata: List[Dict[str, Any]],
        indicators: List[Dict[str, Any]],
        previous_specs: List[Dict[str, Any]],
        validation_result: Dict[str, Any],
        iteration: int,
        config: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Build a prompt for retrying after validation failure.

        Args:
            metadata: List of variable metadata dictionaries
            indicators: List of available indicators
            previous_specs: Table specifications from the previous iteration
            validation_result: Validation result with errors
            iteration: Current iteration number
            config: Optional configuration parameters

        Returns:
            Prompt string for the LLM
        """
        config = config or {}
        indicators_formatted = _format_indicators_for_table_specs(indicators)
        errors_formatted = _format_validation_errors(validation_result)
        specs_json = _format_table_specs_json(previous_specs)

        prompt = f"""# Cross-Table Specifications - Validation Retry (Iteration {iteration})

Your previous attempt at generating table specifications failed validation.
Please review the errors below and generate corrected specifications.

## Available Indicators

{indicators_formatted}

## Validation Errors from Previous Attempt

{errors_formatted}

## Previous Table Specifications (For Reference)

```json
{specs_json}
```

## Instructions for This Iteration

You MUST address ALL of the validation errors listed above. Common issues include:

### Indicator Reference Errors
- **Issue**: Referenced indicator does not exist
- **Fix**: Use only indicator IDs from the indicators list above

### Duplicate Table IDs
- **Issue**: Multiple tables with the same id
- **Fix**: Ensure each table has a unique TABLE_XXX id

### Invalid Sort Options
- **Issue**: Invalid sort value
- **Fix**: Use one of: "none", "asc", "desc"

### Overlap Error
- **Issue**: Same indicator in both rows and columns
- **Fix**: Ensure no overlap between row_indicators and column_indicators

### Weighting Variable Error
- **Issue**: Weighting variable does not exist in metadata
- **Fix**: Use a valid variable name or set to null

## Output Format

```json
{{
  "tables": [
    {{
      "id": "TABLE_001",
      "description": "Table description",
      "row_indicators": ["IND_001"],
      "column_indicators": ["IND_002"],
      "sort_rows": "none|asc|desc",
      "sort_columns": "none|asc|desc",
      "min_count": 30
    }}
  ],
  "weighting_variable": "weight_var_name"
}}
```

## Validation Checklist

Before returning, verify:
- [ ] All indicators exist in the indicators list
- [ ] All table IDs are unique
- [ ] All sort values are valid ("none", "asc", or "desc")
- [ ] No overlap between row and column indicators
- [ ] Weighting variable exists in metadata (if specified)
- [ ] min_count is a positive integer (typically 30)

Generate corrected table specifications now.
"""
        return prompt

    @staticmethod
    def build_human_feedback_prompt(
        metadata: List[Dict[str, Any]],
        indicators: List[Dict[str, Any]],
        previous_specs: List[Dict[str, Any]],
        feedback: str,
        iteration: int,
        config: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Build a prompt for incorporating human feedback.

        Args:
            metadata: List of variable metadata dictionaries
            indicators: List of available indicators
            previous_specs: Table specifications from the previous iteration
            feedback: Human feedback/comments
            iteration: Current iteration number
            config: Optional configuration parameters

        Returns:
            Prompt string for the LLM
        """
        config = config or {}
        indicators_formatted = _format_indicators_for_table_specs(indicators)
        specs_json = _format_table_specs_json(previous_specs)

        prompt = f"""# Cross-Table Specifications - Human Feedback (Iteration {iteration})

A human analyst has reviewed your previous table specifications and provided feedback.
Please revise the specifications based on their comments.

## Available Indicators

{indicators_formatted}

## Human Feedback

{feedback}

## Previous Table Specifications (For Reference)

```json
{specs_json}
```

## Instructions

Carefully review the human feedback and revise your table specifications accordingly.
The analyst has domain expertise and understands the research objectives.

### Common Feedback Types

**Missing Tables**: "We need tables for X analysis"
- Add new tables to address the missing analysis

**Indicator Changes**: "Use different indicators"
- Swap row/column indicators as suggested

**Table Structure**: "Change the sort order"
- Modify sort_rows or sort_columns

**Priority**: "These tables are most important"
- Focus on high-value analytical tables

**Sample Size**: "Increase/decrease min_count"
- Adjust the minimum sample size threshold

## Output Format

```json
{{
  "tables": [
    {{
      "id": "TABLE_001",
      "description": "Table description",
      "row_indicators": ["IND_001"],
      "column_indicators": ["IND_002"],
      "sort_rows": "none|asc|desc",
      "sort_columns": "none|asc|desc",
      "min_count": 30
    }}
  ],
  "weighting_variable": "weight_var_name"
}}
```

Generate revised table specifications that address the human feedback.
"""
        return prompt


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def build_recoding_prompt(
    prompt_type: str,
    metadata: List[Dict[str, Any]],
    previous_rules: Optional[List[Dict[str, Any]]] = None,
    validation_result: Optional[Dict[str, Any]] = None,
    feedback: Optional[str] = None,
    iteration: int = 1,
    config: Optional[Dict[str, Any]] = None
) -> str:
    """
    Build a recoding rules prompt.

    Args:
        prompt_type: Type of prompt ("initial", "validation_retry", "human_feedback")
        metadata: List of variable metadata dictionaries
        previous_rules: Previous rules (for retry/feedback)
        validation_result: Validation result (for validation_retry)
        feedback: Human feedback (for human_feedback)
        iteration: Current iteration number
        config: Optional configuration parameters

    Returns:
        Prompt string for the LLM
    """
    builder = RecodingPromptBuilder()

    if prompt_type == "initial":
        return builder.build_initial_prompt(metadata, config)
    elif prompt_type == "validation_retry":
        if not previous_rules or not validation_result:
            raise ValueError("previous_rules and validation_result required for validation_retry")
        return builder.build_validation_retry_prompt(
            metadata, previous_rules, validation_result, iteration, config
        )
    elif prompt_type == "human_feedback":
        if not previous_rules or not feedback:
            raise ValueError("previous_rules and feedback required for human_feedback")
        return builder.build_human_feedback_prompt(
            metadata, previous_rules, feedback, iteration, config
        )
    else:
        raise ValueError(f"Invalid prompt_type: {prompt_type}. Must be 'initial', 'validation_retry', or 'human_feedback'")


def build_indicators_prompt(
    prompt_type: str,
    metadata: List[Dict[str, Any]],
    recoding_rules: Optional[List[Dict[str, Any]]] = None,
    previous_indicators: Optional[List[Dict[str, Any]]] = None,
    validation_result: Optional[Dict[str, Any]] = None,
    feedback: Optional[str] = None,
    iteration: int = 1,
    config: Optional[Dict[str, Any]] = None
) -> str:
    """
    Build an indicators prompt.

    Args:
        prompt_type: Type of prompt ("initial", "validation_retry", "human_feedback")
        metadata: List of variable metadata dictionaries
        recoding_rules: Previously generated recoding rules (for initial)
        previous_indicators: Previous indicators (for retry/feedback)
        validation_result: Validation result (for validation_retry)
        feedback: Human feedback (for human_feedback)
        iteration: Current iteration number
        config: Optional configuration parameters

    Returns:
        Prompt string for the LLM
    """
    builder = IndicatorsPromptBuilder()

    if prompt_type == "initial":
        return builder.build_initial_prompt(metadata, recoding_rules, config)
    elif prompt_type == "validation_retry":
        if not previous_indicators or not validation_result:
            raise ValueError("previous_indicators and validation_result required for validation_retry")
        return builder.build_validation_retry_prompt(
            metadata, previous_indicators, validation_result, iteration, config
        )
    elif prompt_type == "human_feedback":
        if not previous_indicators or not feedback:
            raise ValueError("previous_indicators and feedback required for human_feedback")
        return builder.build_human_feedback_prompt(
            metadata, previous_indicators, feedback, iteration, config
        )
    else:
        raise ValueError(f"Invalid prompt_type: {prompt_type}. Must be 'initial', 'validation_retry', or 'human_feedback'")


def build_table_specs_prompt(
    prompt_type: str,
    metadata: List[Dict[str, Any]],
    indicators: List[Dict[str, Any]],
    previous_specs: Optional[List[Dict[str, Any]]] = None,
    validation_result: Optional[Dict[str, Any]] = None,
    feedback: Optional[str] = None,
    iteration: int = 1,
    config: Optional[Dict[str, Any]] = None
) -> str:
    """
    Build a table specifications prompt.

    Args:
        prompt_type: Type of prompt ("initial", "validation_retry", "human_feedback")
        metadata: List of variable metadata dictionaries
        indicators: List of generated indicators
        previous_specs: Previous table specs (for retry/feedback)
        validation_result: Validation result (for validation_retry)
        feedback: Human feedback (for human_feedback)
        iteration: Current iteration number
        config: Optional configuration parameters

    Returns:
        Prompt string for the LLM
    """
    builder = TableSpecsPromptBuilder()

    if prompt_type == "initial":
        return builder.build_initial_prompt(metadata, indicators, config)
    elif prompt_type == "validation_retry":
        if not previous_specs or not validation_result:
            raise ValueError("previous_specs and validation_result required for validation_retry")
        return builder.build_validation_retry_prompt(
            metadata, indicators, previous_specs, validation_result, iteration, config
        )
    elif prompt_type == "human_feedback":
        if not previous_specs or not feedback:
            raise ValueError("previous_specs and feedback required for human_feedback")
        return builder.build_human_feedback_prompt(
            metadata, indicators, previous_specs, feedback, iteration, config
        )
    else:
        raise ValueError(f"Invalid prompt_type: {prompt_type}. Must be 'initial', 'validation_retry', or 'human_feedback'")


# ============================================================================
# LEGACY FUNCTIONS (Backward compatibility)
# ============================================================================

def build_initial_recoding_prompt(metadata: List[Dict[str, Any]]) -> str:
    """Legacy: Build initial prompt for recoding rules generation."""
    return build_recoding_prompt("initial", metadata)


def build_recoding_validation_retry_prompt(
    metadata: List[Dict[str, Any]],
    validation_result: Dict[str, Any],
    iteration: int
) -> str:
    """Legacy: Build prompt for recoding rules regeneration after validation failure."""
    return build_recoding_prompt("validation_retry", metadata,
                                 previous_rules=[],  # Not used in legacy
                                 validation_result=validation_result,
                                 iteration=iteration)


def build_recoding_human_feedback_prompt(
    metadata: List[Dict[str, Any]],
    human_feedback: Dict[str, Any],
    previous_rules: List[Dict[str, Any]],
    iteration: int
) -> str:
    """Legacy: Build prompt for recoding rules regeneration after human rejection."""
    feedback = human_feedback.get('comments', 'No comments provided')
    return build_recoding_prompt("human_feedback", metadata,
                                 previous_rules=previous_rules,
                                 feedback=feedback,
                                 iteration=iteration)


def build_initial_indicators_prompt(metadata: List[Dict[str, Any]]) -> str:
    """Legacy: Build initial prompt for indicators generation."""
    return build_indicators_prompt("initial", metadata)


def build_indicators_validation_retry_prompt(
    metadata: List[Dict[str, Any]],
    validation_result: Dict[str, Any],
    iteration: int
) -> str:
    """Legacy: Build prompt for indicators regeneration after validation failure."""
    return build_indicators_prompt("validation_retry", metadata,
                                   previous_indicators=[],  # Not used in legacy
                                   validation_result=validation_result,
                                   iteration=iteration)


def build_indicators_human_feedback_prompt(
    metadata: List[Dict[str, Any]],
    human_feedback: Dict[str, Any],
    previous_indicators: List[Dict[str, Any]],
    iteration: int
) -> str:
    """Legacy: Build prompt for indicators regeneration after human rejection."""
    feedback = human_feedback.get('comments', 'No comments provided')
    return build_indicators_prompt("human_feedback", metadata,
                                   previous_indicators=previous_indicators,
                                   feedback=feedback,
                                   iteration=iteration)


def build_initial_table_specs_prompt(
    indicators: List[Dict[str, Any]],
    metadata: List[Dict[str, Any]]
) -> str:
    """Legacy: Build initial prompt for table specifications generation."""
    return build_table_specs_prompt("initial", metadata, indicators)


def build_table_specs_validation_retry_prompt(
    indicators: List[Dict[str, Any]],
    metadata: List[Dict[str, Any]],
    validation_result: Dict[str, Any],
    iteration: int
) -> str:
    """Legacy: Build prompt for table specs regeneration after validation failure."""
    return build_table_specs_prompt("validation_retry", metadata, indicators,
                                   previous_specs=[],  # Not used in legacy
                                   validation_result=validation_result,
                                   iteration=iteration)


def build_table_specs_human_feedback_prompt(
    indicators: List[Dict[str, Any]],
    metadata: List[Dict[str, Any]],
    human_feedback: Dict[str, Any],
    previous_specs: Dict[str, Any],
    iteration: int
) -> str:
    """Legacy: Build prompt for table specs regeneration after human rejection."""
    feedback = human_feedback.get('comments', 'No comments provided')
    return build_table_specs_prompt("human_feedback", metadata, indicators,
                                   previous_specs=previous_specs.get('tables', []),
                                   feedback=feedback,
                                   iteration=iteration)


# ============================================================================
# PRIVATE HELPER FUNCTIONS
# ============================================================================

def _format_indicators_for_table_specs(indicators: List[Dict[str, Any]]) -> str:
    """Format indicators for table specs prompt."""
    lines = []
    for ind in indicators:
        lines.append(f"**{ind.get('id')}**: {ind.get('description')}")
        lines.append(f"  - Metric: {ind.get('metric')}")
        lines.append(f"  - Variables: {', '.join(ind.get('underlying_variables', []))}")
        lines.append("")

    return "\n".join(lines)
