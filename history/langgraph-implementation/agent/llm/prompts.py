"""
LLM Prompt Templates for Survey Analysis Workflow

This module provides prompt generation functions for LLM-orchestrated steps
in the workflow: recoding rules, indicators, and table specifications.

Each prompt function supports three modes:
1. Initial prompt (no feedback)
2. Validation retry (with validation feedback)
3. Human feedback retry (with human guidance)

Implemented prompts:
- generate_recoding_rules_prompt(): For Step 4 (Recoding Rules Generation)
- generate_indicators_prompt(): For Step 9 (Indicator Generation)
- generate_table_specifications_prompt(): For Step 12 (Table Specifications)

Example:
    >>> from agent.llm.prompts import generate_recoding_rules_prompt, generate_indicators_prompt, generate_table_specifications_prompt
    >>> metadata = [{"name": "age", "label": "Age", ...}]
    >>> prompt = generate_recoding_rules_prompt(metadata)
    >>> print(prompt)
"""

import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


# =============================================================================
# Recoding Rules Prompt
# =============================================================================

def generate_recoding_rules_prompt(
    metadata: List[Dict[str, Any]],
    validation_feedback: Optional[str] = None,
    human_feedback: Optional[str] = None
) -> str:
    """
    Generate prompt for LLM to create recoding rules for survey variables.

    This prompt instructs the LLM to follow market research best practices:
    - Range grouping for continuous variables
    - Category consolidation for sparse categories
    - Derived variables for composite measures
    - Top/bottom box scoring for satisfaction ratings

    Args:
        metadata: List of variable metadata dictionaries (filtered_metadata)
        validation_feedback: Optional feedback from validation node (Step 5)
        human_feedback: Optional feedback from human reviewer (Step 6)

    Returns:
        Complete prompt string for LLM

    Example:
        >>> metadata = [
        ...     {
        ...         "name": "age",
        ...         "label": "Respondent Age",
        ...         "variable_type": "numeric",
        ...         "min_value": 18,
        ...         "max_value": 99,
        ...         "value_labels": {}
        ...     }
        ... ]
        >>> prompt = generate_recoding_rules_prompt(metadata)
    """
    # Build base prompt
    prompt = """You are a market research data analyst specializing in survey data preparation and cross-tabulation analysis.

Generate recoding rules for the following survey variables to prepare them for cross-tabulation analysis.

## Survey Variables Metadata
"""
    # Add formatted metadata
    prompt += _format_metadata(metadata)

    # Add recoding principles
    prompt += """

## Recoding Principles

### 1. Range Grouping
- Group continuous numeric variables into meaningful ranges
- Use equal intervals or natural breakpoints (quartiles, median split)
- Create 3-5 categories per variable
- Example: Age (18-99) → Age Groups (18-24, 25-34, 35-44, 45-54, 55+)

### 2. Category Consolidation
- Combine sparse categories (<5% of sample) into "Other" category
- Merge semantically similar response options
- Maintain analytical validity while simplifying complexity
- Example: Region (10 regions) → Region Group (North, South, West, Other)

### 3. Derived Variables
- Create composite scores from multiple related items when meaningful
- Apply top/bottom box scoring for satisfaction ratings
- Calculate means or sums for scale items when appropriate
- Example: 10-point satisfaction → Top 2 Box (9-10 vs 1-8)

### 4. Target Variable Constraints
- Target variable names must be unique across all rules
- Use descriptive naming: {original_var}_recoded or {original_var}_{concept}
- Target categories must be mutually exclusive (no overlapping ranges)
- Target values should be integers for categorical analysis

## Output Format

Return ONLY a valid JSON object with this structure:
```json
{
    "recoding_rules": [
        {
            "source_variable": "var_name",
            "target_variable": "var_name_recoded",
            "transformation_type": "range_grouping",
            "rules": [
                {"source_min": 1, "source_max": 3, "target_value": 1, "target_label": "Low"},
                {"source_min": 4, "source_max": 7, "target_value": 2, "target_label": "Medium"},
                {"source_min": 8, "source_max": 10, "target_value": 3, "target_label": "High"}
            ],
            "description": "Brief explanation of recoding logic"
        }
    ]
}
```

### Transformation Types
- "range_grouping": Group numeric ranges (use source_min/source_max)
- "category_consolidation": Map specific values to groups (use source_values array)
- "derived": Create new variable from formula (use formula field)
- "top_bottom_box": Collapse satisfaction scales (use source_values array)

### Rule Fields by Type

**Range Grouping:**
```json
{
    "source_variable": "age",
    "target_variable": "age_group",
    "transformation_type": "range_grouping",
    "rules": [
        {"source_min": 18, "source_max": 24, "target_value": 1, "target_label": "18-24"},
        {"source_min": 25, "source_max": 34, "target_value": 2, "target_label": "25-34"},
        {"source_min": 35, "source_max": 44, "target_value": 3, "target_label": "35-44"},
        {"source_min": 45, "source_max": 54, "target_value": 4, "target_label": "45-54"},
        {"source_min": 55, "source_max": 99, "target_value": 5, "target_label": "55+"}
    ],
    "description": "Group age into 5-year brackets"
}
```

**Category Consolidation:**
```json
{
    "source_variable": "region",
    "target_variable": "region_group",
    "transformation_type": "category_consolidation",
    "rules": [
        {"source_values": [1, 2], "target_value": 1, "target_label": "North"},
        {"source_values": [3, 4], "target_value": 2, "target_label": "South"},
        {"source_values": [5, 6, 7], "target_value": 3, "target_label": "West"},
        {"source_values": [8, 9, 10], "target_value": 4, "target_label": "Other"}
    ],
    "description": "Consolidate 10 regions into 4 groups"
}
```

**Top/Bottom Box:**
```json
{
    "source_variable": "q5_satisfaction",
    "target_variable": "q5_satisfaction_top2box",
    "transformation_type": "top_bottom_box",
    "rules": [
        {"source_values": [1, 2, 3, 4, 5, 6, 7, 8], "target_value": 0, "target_label": "Not Top 2 Box"},
        {"source_values": [9, 10], "target_value": 1, "target_label": "Top 2 Box"}
    ],
    "description": "Top 2 Box scoring for satisfaction question"
}
```

**Derived Variable:**
```json
{
    "source_variable": "sat_q1,sat_q2,sat_q3",
    "target_variable": "satisfaction_index",
    "transformation_type": "derived",
    "formula": "mean(sat_q1, sat_q2, sat_q3)",
    "rules": [
        {"source_min": 1, "source_max": 3.33, "target_value": 1, "target_label": "Low Satisfaction"},
        {"source_min": 3.34, "source_max": 6.66, "target_value": 2, "target_label": "Medium Satisfaction"},
        {"source_min": 6.67, "source_max": 10, "target_value": 3, "target_label": "High Satisfaction"}
    ],
    "description": "Mean of 3 satisfaction questions, grouped into 3 categories"
}
```

## Guidelines

1. **Prioritize analytical value**: Focus on variables that will be used in cross-tabulations
2. **Balance detail and simplicity**: Create enough categories for insight but not too many for small sample sizes
3. **Use meaningful labels**: Target labels should be clear and interpretable
4. **Handle missing data**: Explicitly mention how missing values (system-missing, -99, etc.) should be handled
5. **Generate 3-10 rules**: Focus on the most analysis-relevant variables

Return ONLY the JSON object. No explanations, no markdown code blocks.
"""

    # Add validation feedback if provided
    if validation_feedback:
        prompt += f"""

## Validation Feedback

The previous recoding rules had validation errors. Please fix the following issues:

{validation_feedback}

Ensure all rules address the validation feedback above. Return ONLY the corrected JSON object.
"""

    # Add human feedback if provided
    if human_feedback:
        prompt += f"""

## Human Reviewer Feedback

The human reviewer provided the following feedback:

{human_feedback}

Please incorporate this guidance in your revised recoding rules. Return ONLY the corrected JSON object.
"""

    return prompt


def _format_metadata(metadata: List[Dict[str, Any]]) -> str:
    """
    Format variable metadata for inclusion in LLM prompt.

    Creates a readable text representation of variables with their
    properties, highlighting those suitable for each transformation type.

    Args:
        metadata: List of variable metadata dictionaries

    Returns:
        Formatted text string for prompt inclusion

    Example:
        >>> metadata = [
        ...     {"name": "age", "label": "Age", "variable_type": "numeric",
        ...      "min_value": 18, "max_value": 99, "value_labels": {}}
        ... ]
        >>> _format_metadata(metadata)
        '### Variables Suitable for Recoding\\n\\n1. **age** (Age)\\n   - Type: numeric\\n  ...'
    """
    if not metadata:
        return "No variables available for recoding."

    lines = ["### Variables Requiring Recoding\n"]

    # Identify variables by transformation type
    range_candidates = []
    category_candidates = []
    derived_candidates = []

    for var in metadata:
        var_name = var.get("name", "unknown")
        var_label = var.get("label", "")
        var_type = var.get("variable_type", "unknown")
        min_val = var.get("min_value")
        max_val = var.get("max_value")
        value_labels = var.get("value_labels", {})

        # Build variable description
        var_desc = f"\n**{var_name}** ({var_label})\n"
        var_desc += f"   - Type: {var_type}\n"

        if var_type == "numeric" and min_val is not None and max_val is not None:
            var_desc += f"   - Range: {min_val} to {max_val}\n"

            # Determine suitability
            distinct_count = max_val - min_val + 1 if min_val is not None and max_val is not None else 0

            if distinct_count > 10:
                # Good candidate for range grouping
                range_candidates.append((var_desc, var))
            elif value_labels and len(value_labels) > 5:
                # Good candidate for category consolidation
                category_candidates.append((var_desc, var))
            elif "satisfaction" in var_name.lower() or "rating" in var_name.lower():
                # Good candidate for top/bottom box
                range_candidates.append((var_desc, var))

        if value_labels:
            var_desc += f"   - Categories: {len(value_labels)} options\n"
            if len(value_labels) <= 10:
                var_desc += f"   - Values: {dict(list(value_labels.items())[:5])}{'...' if len(value_labels) > 5 else ''}\n"

        # Check for satisfaction-related variables for derived index
        if any(keyword in var_name.lower() for keyword in ["sat", "satisfaction", "rating"]):
            derived_candidates.append((var_desc, var))

    # Organize by transformation type
    if range_candidates:
        lines.append("\n**Best for Range Grouping:**")
        for var_desc, _ in range_candidates[:10]:  # Limit to 10
            lines.append(var_desc)

    if category_candidates:
        lines.append("\n**Best for Category Consolidation:**")
        for var_desc, _ in category_candidates[:10]:
            lines.append(var_desc)

    if derived_candidates:
        lines.append("\n**Best for Derived Variables / Top-Box Scoring:**")
        for var_desc, _ in derived_candidates[:10]:
            lines.append(var_desc)

    # If we didn't categorize, just list all
    if not (range_candidates or category_candidates or derived_candidates):
        for var in metadata[:20]:  # Limit to 20 variables
            var_name = var.get("name", "unknown")
            var_label = var.get("label", "")
            var_type = var.get("variable_type", "unknown")
            lines.append(f"\n**{var_name}** ({var_label})")
            lines.append(f"   - Type: {var_type}")

    # Add note about filtering
    if len(metadata) > 20:
        lines.append(f"\n*Showing 20 of {len(metadata)} variables. Focus on the most analysis-relevant variables.*")

    return "\n".join(lines)


# =============================================================================
# Indicators Prompt
# =============================================================================

def generate_indicators_prompt(
    metadata: List[Dict[str, Any]],
    validation_feedback: Optional[str] = None,
    human_feedback: Optional[str] = None
) -> str:
    """
    Generate prompt for LLM to create indicator definitions.

    This prompt instructs the LLM to group semantically related variables
    into indicators for cross-tabulation analysis.

    Args:
        metadata: List of variable metadata dictionaries (new_metadata from Step 8)
        validation_feedback: Optional feedback from validation node (Step 10)
        human_feedback: Optional feedback from human reviewer (Step 11)

    Returns:
        Complete prompt string for LLM

    Example:
        >>> metadata = [
        ...     {"name": "sat_quality", "label": "Satisfaction with Quality", ...},
        ...     {"name": "sat_price", "label": "Satisfaction with Price", ...}
        ... ]
        >>> prompt = generate_indicators_prompt(metadata)
        >>> print(prompt)
    """
    # Build base prompt
    prompt = """You are a market research analyst specializing in survey analysis and indicator construction.

Group the survey variables into meaningful indicators (composite measures) for cross-tabulation analysis.

## Survey Variables Metadata
"""
    # Add formatted metadata for indicators
    prompt += _format_metadata_for_indicators(metadata)

    # Add indicator grouping principles
    prompt += """

## Indicator Grouping Principles

### 1. Semantic Cohesion
- Group variables that measure the same underlying concept
- Look for naming patterns (sat_*, cust_*, prod_*, imp_*, like_*)
- Consider variable labels for semantic meaning
- Group variables that form a logical scale (e.g., satisfaction across touchpoints)

### 2. Multi-Item Scales
- Group variables that form validated multi-item scales
- Common patterns: satisfaction scales, importance ratings, likelihood ratings
- Example: sat_quality, sat_price, sat_service, sat_selection → "Customer_Satisfaction_Indicator"
- Example: imp_quality, imp_price, imp_service, imp_selection → "Attribute_Importance_Indicator"

### 3. Demographic Separation
- **DO NOT** group demographic variables (age, gender, income, region, education) with attitudinal variables
- Demographics are used as breakdown variables in cross-tabs, not as composite indicators
- If grouping demographics, keep them as a separate "Demographics" indicator

### 4. Size Limits
- **Optimal**: 3-7 variables per indicator
- **Minimum**: 2 variables per indicator (single variables should be left ungrouped)
- **Maximum**: 10 variables per indicator (for practicality in cross-tabulation)
- Generate 3-8 indicators total (prioritize the most analysis-relevant groups)

### 5. Analytical Validity
- Variables in an indicator should have similar response scales
- Avoid mixing different measurement types (e.g., 5-point satisfaction with 10-point satisfaction)
- Consider variable roles: grouping should make sense for cross-tabulation analysis
- Indicators should represent meaningful constructs for market research reporting

## Output Format

Return ONLY a valid JSON object with this structure:
```json
{
    "indicators": [
        {
            "name": "Customer_Satisfaction_Index",
            "description": "Overall customer satisfaction across multiple product and service attributes",
            "variables": ["sat_quality", "sat_price", "sat_service", "sat_selection"]
        }
    ]
}
```

### Field Requirements:
- **name**: Unique, descriptive indicator name (use underscores instead of spaces, snake_case)
- **description**: Concise explanation of what the indicator measures (1-2 sentences)
- **variables**: Array of variable names that form this indicator (2-10 variables)

## Examples

### Example 1: Satisfaction Indicator (Good Grouping)
```json
{
    "name": "Product_Satisfaction",
    "description": "Customer satisfaction ratings across key product attributes",
    "variables": ["sat_quality", "sat_variety", "sat_price", "sat_freshness"]
}
```

### Example 2: Importance Indicator (Good Grouping)
```json
{
    "name": "Attribute_Importance",
    "description": "Perceived importance of various product attributes in purchase decisions",
    "variables": ["imp_quality", "imp_variety", "imp_price", "imp_freshness"]
}
```

### Example 3: What NOT to Do (Bad Grouping)
```json
{
    "name": "Mixed_Variables",
    "description": "This is WRONG - do not mix demographics with satisfaction",
    "variables": ["sat_quality", "age", "gender", "region"]
}
```
**Why this is wrong**: Demographics (age, gender, region) should not be mixed with attitudinal variables.

## Guidelines

1. **Focus on analysis value**: Prioritize groupings that will produce meaningful cross-tabulations
2. **Use clear naming**: Indicator names should be descriptive and use snake_case
3. **Leave standalone variables**: Not all variables need to be grouped - single variables can be analyzed individually
4. **Check variable existence**: Only include variables that exist in the provided metadata
5. **Avoid redundancy**: Do not create indicators that duplicate the same variable groups

Return ONLY the JSON object. No explanations, no markdown code blocks.
"""

    # Add validation feedback if provided
    if validation_feedback:
        prompt += f"""

## Validation Feedback

The previous indicator grouping had validation errors. Please fix the following issues:

{validation_feedback}

Ensure all indicators address the validation feedback above. Return ONLY the corrected JSON object.
"""

    # Add human feedback if provided
    if human_feedback:
        prompt += f"""

## Human Reviewer Feedback

The human reviewer provided the following feedback:

{human_feedback}

Please incorporate this guidance in your revised indicator grouping. Return ONLY the corrected JSON object.
"""

    return prompt


def _format_metadata_for_indicators(metadata: List[Dict[str, Any]]) -> str:
    """
    Format variable metadata for indicator generation prompt.

    Emphasizes variable names, labels, and semantic patterns to help LLM
    identify meaningful groupings.

    Args:
        metadata: List of variable metadata dictionaries

    Returns:
        Formatted text string for prompt inclusion

    Example:
        >>> metadata = [
        ...     {"name": "sat_quality", "label": "Satisfaction with Quality", ...}
        ... ]
        >>> _format_metadata_for_indicators(metadata)
        '### Variables Available for Indicator Grouping\\n\\n1. **sat_quality** (Satisfaction with Quality)...'
    """
    if not metadata:
        return "No variables available for indicator grouping."

    lines = ["### Variables Available for Indicator Grouping\n"]

    # Group variables by semantic patterns for better organization
    semantic_groups = {
        "satisfaction": [],
        "importance": [],
        "likelihood": [],
        "demographics": [],
        "usage": [],
        "rating": [],
        "other": []
    }

    # Categorize variables by semantic patterns
    for var in metadata:
        var_name = var.get("name", "unknown")
        var_label = var.get("label", "")
        var_type = var.get("variable_type", "unknown")

        # Build variable description
        var_desc = f"**{var_name}**"
        if var_label:
            var_desc += f" ({var_label})"
        var_desc += f" [Type: {var_type}]"

        # Categorize by naming patterns
        var_lower = var_name.lower()
        if any(kw in var_lower for kw in ["sat", "satisfaction"]):
            semantic_groups["satisfaction"].append(var_desc)
        elif any(kw in var_lower for kw in ["imp", "importance"]):
            semantic_groups["importance"].append(var_desc)
        elif any(kw in var_lower for kw in ["like", "likelihood", "prob", "probability"]):
            semantic_groups["likelihood"].append(var_desc)
        elif any(kw in var_lower for kw in ["age", "gender", "income", "region", "education", "ethnic"]):
            semantic_groups["demographics"].append(var_desc)
        elif any(kw in var_lower for kw in ["use", "usage", "freq", "frequency"]):
            semantic_groups["usage"].append(var_desc)
        elif any(kw in var_lower for kw in ["rate", "rating", "score"]):
            semantic_groups["rating"].append(var_desc)
        else:
            semantic_groups["other"].append(var_desc)

    # Display grouped variables
    for group_name, group_vars in semantic_groups.items():
        if group_vars:
            lines.append(f"\n**{group_name.capitalize()} Variables:**")
            for var_desc in group_vars[:15]:  # Limit to 15 per group
                lines.append(f"- {var_desc}")
            if len(group_vars) > 15:
                lines.append(f"  ... and {len(group_vars) - 15} more {group_name} variables")

    # Add note if many variables
    total_vars = sum(len(vars) for vars in semantic_groups.values())
    if total_vars > 50:
        lines.append(f"\n*Showing grouped variables. Total variables available: {total_vars}.*")

    return "\n".join(lines)


# =============================================================================
# Table Specifications Prompt
# =============================================================================

def generate_table_specifications_prompt(
    metadata: List[Dict[str, Any]],
    indicators: Optional[Dict[str, Any]] = None,
    validation_feedback: Optional[str] = None,
    human_feedback: Optional[str] = None
) -> str:
    """
    Generate prompt for LLM to create cross-tabulation table specifications.

    This prompt instructs the LLM to define tables following market research
    best practices: demographic variables as rows, outcome/indicator variables
    as columns, with chi-square statistics.

    Args:
        metadata: List of variable metadata dictionaries (new_metadata from Step 8)
        indicators: Optional indicator definitions from Step 11
        validation_feedback: Optional feedback from validation node (Step 13)
        human_feedback: Optional feedback from human reviewer (Step 14)

    Returns:
        Complete prompt string for LLM

    Example:
        >>> metadata = [
        ...     {"name": "gender", "label": "Gender", "variable_type": "numeric", ...},
        ...     {"name": "sat_quality", "label": "Satisfaction with Quality", ...}
        ... ]
        >>> prompt = generate_table_specifications_prompt(metadata)
        >>> print(prompt)
    """
    # Build base prompt
    prompt = """You are a market research analyst specializing in cross-tabulation analysis for survey data.

Define the cross-tabulation tables to generate for this survey analysis.

## Variables Metadata
"""
    # Add formatted metadata highlighting demographic vs outcome variables
    prompt += _format_metadata_for_tables(metadata)

    # Add indicators if provided
    if indicators and indicators.get("indicators"):
        prompt += """

## Indicators
"""
        prompt += _format_indicators_for_tables(indicators)

    # Add table specification principles
    prompt += """

## Table Specification Principles

### 1. Demographic × Outcome Pattern
- **Rows**: Demographic/breakdown variables (age, gender, income, region, education, etc.)
- **Columns**: Outcome/indicator variables (satisfaction, likelihood, agreement ratings, etc.)
- This is the standard market research crosstab format
- Example: Gender (rows) × Satisfaction (columns)

### 2. Categorical Variables Only
- Both row and column variables must be categorical (not continuous)
- Use recoded variables (already created in previous workflow steps)
- Do NOT use raw continuous variables like age, income without recoding
- Look for variables ending in "_recoded", "_group", or similar

### 3. Table Statistics
For each table, include these statistics:
- **count** (n): Cell counts
- **columnpct** (%): Column percentages (show distribution within each column)
- **chisq** (χ²): Chi-square test of independence
- **cramersv** (V): Cramer's V effect size

### 4. Meaningful Tables Only
- Each table should provide analytical insight
- Avoid tables where both variables are from the same semantic domain (e.g., satisfaction × satisfaction)
- Prioritize tables that answer research questions
- Focus on relationships that reveal patterns

### 5. Manageable Number
- Generate 5-15 tables total
- Focus on most analysis-relevant combinations
- Include key demographic breakdowns for major outcome variables
- Quality over quantity

## Variable Types

**Demographic variables** (use as ROWS):
- age_recoded, age_group, gender, income_recoded, income_group, region, education, etc.
- Any variable that segments respondents into groups

**Outcome/Indicator variables** (use as COLUMNS):
- Satisfaction indicators (sat_*, satisfaction_*)
- Likelihood ratings (like_*, likelihood_*, prob_*)
- Agreement scales (agree_*, importance_*, imp_*)
- Derived scores or indexes

## Output Format

Return ONLY a valid JSON object with this structure:
```json
{
    "tables": [
        {
            "table_id": "gender_x_satisfaction",
            "row_variable": "gender",
            "column_variable": "Satisfaction_Index",
            "weight_variable": null,
            "statistics": ["count", "columnpct", "chisq", "cramersv"]
        }
    ]
}
```

### Field Requirements:
- **table_id**: Unique identifier (use pattern: "{row_var}_x_{col_var}")
- **row_variable**: Name of demographic variable for table rows (must exist in metadata)
- **column_variable**: Name of outcome/indicator variable for table columns (must exist in metadata)
- **weight_variable**: Optional weighting variable (set to null if no weighting)
- **statistics**: Array of statistics - always include ["count", "columnpct", "chisq", "cramersv"]

## Examples

### Example 1: Demographic × Satisfaction (Good Table)
```json
{
    "table_id": "gender_x_satisfaction",
    "row_variable": "gender",
    "column_variable": "sat_quality",
    "weight_variable": null,
    "statistics": ["count", "columnpct", "chisq", "cramersv"]
}
```
**Why this is good**: Gender (demographic) breaks down satisfaction ratings (outcome).

### Example 2: Age Group × Top 2 Box (Good Table)
```json
{
    "table_id": "age_group_x_top2box",
    "row_variable": "age_recoded",
    "column_variable": "sat_top2box",
    "weight_variable": null,
    "statistics": ["count", "columnpct", "chisq", "cramersv"]
}
```
**Why this is good**: Age groups show different satisfaction patterns.

### Example 3: What NOT to Do (Bad Table)
```json
{
    "table_id": "satisfaction_x_satisfaction",
    "row_variable": "sat_quality",
    "column_variable": "sat_price",
    "weight_variable": null,
    "statistics": ["count", "columnpct", "chisq", "cramersv"]
}
```
**Why this is wrong**: Both variables are satisfaction (same semantic domain). This doesn't follow demographic × outcome pattern.

## Guidelines

1. **Follow demographic × outcome pattern**: Always use demographic/breakdown variables as rows
2. **Use categorical variables only**: Ensure both variables are categorical, not continuous
3. **Check variable existence**: Only use variables that exist in the provided metadata
4. **Prioritize analytical value**: Focus on tables that reveal meaningful insights
5. **Avoid redundancy**: Don't create multiple tables with the same variables in different orders
6. **Unique table IDs**: Each table_id must be unique

Return ONLY the JSON object. No explanations, no markdown code blocks.
"""

    # Add validation feedback if provided
    if validation_feedback:
        prompt += f"""

## Validation Feedback

The previous table specifications had validation errors. Please fix the following issues:

{validation_feedback}

Ensure all tables address the validation feedback above. Return ONLY the corrected JSON object.
"""

    # Add human feedback if provided
    if human_feedback:
        prompt += f"""

## Human Reviewer Feedback

The human reviewer provided the following feedback:

{human_feedback}

Please incorporate this guidance in your revised table specifications. Return ONLY the corrected JSON object.
"""

    return prompt


def _format_metadata_for_tables(metadata: List[Dict[str, Any]]) -> str:
    """
    Format variable metadata for table specification prompt.

    Emphasizes demographic vs outcome variable categorization to guide
    the LLM in creating demographic × outcome table patterns.

    Args:
        metadata: List of variable metadata dictionaries

    Returns:
        Formatted text string for prompt inclusion

    Example:
        >>> metadata = [
        ...     {"name": "gender", "label": "Gender", "variable_type": "numeric", ...},
        ...     {"name": "sat_quality", "label": "Satisfaction with Quality", ...}
        ... ]
        >>> _format_metadata_for_tables(metadata)
        '### Variables Available for Cross-Tabulation\\n\\n**Demographic Variables (use as ROWS):**...'
    """
    if not metadata:
        return "No variables available for table generation."

    lines = ["### Variables Available for Cross-Tabulation\n"]

    # Categorize variables
    demographic_vars = []
    outcome_vars = []

    # Demographic variable patterns
    demographic_patterns = [
        "age", "gender", "sex", "income", "region", "education", "ethnic",
        "employment", "marital", "household", "children", "urban", "location"
    ]

    # Outcome variable patterns
    outcome_patterns = [
        "sat", "satisfaction", "like", "likelihood", "prob", "probability",
        "agree", "agreement", "imp", "importance", "rate", "rating",
        "quality", "value", "recommend", "loyalty", "trust", "nps"
    ]

    for var in metadata:
        var_name = var.get("name", "unknown")
        var_label = var.get("label", "")
        var_type = var.get("variable_type", "unknown")
        value_labels = var.get("value_labels", {})

        # Build variable description
        var_desc = f"**{var_name}**"
        if var_label:
            var_desc += f" ({var_label})"
        var_desc += f" [Type: {var_type}]"

        if value_labels:
            num_categories = len(value_labels)
            var_desc += f" [{num_categories} categories]"

        # Categorize by naming patterns
        var_lower = var_name.lower()

        # Check for demographic variables
        is_demographic = any(pattern in var_lower for pattern in demographic_patterns)

        # Check for outcome variables
        is_outcome = any(pattern in var_lower for pattern in outcome_patterns)

        # Special handling for recoded variables
        if "_recoded" in var_lower or "_group" in var_lower or "_bracket" in var_lower:
            # Recoded variables are typically demographics
            is_demographic = True
            is_outcome = False

        # Categorize
        if is_demographic and not is_outcome:
            demographic_vars.append(var_desc)
        elif is_outcome and not is_demographic:
            outcome_vars.append(var_desc)
        elif is_demographic and is_outcome:
            # Ambiguous - put in both with note
            demographic_vars.append(var_desc + " [demographic?]")
            outcome_vars.append(var_desc + " [outcome?]")
        else:
            # Unclear - add to outcome as default
            outcome_vars.append(var_desc)

    # Display categorized variables
    if demographic_vars:
        lines.append("\n**Demographic Variables (use as ROWS):**")
        for var_desc in demographic_vars[:15]:  # Limit to 15
            lines.append(f"- {var_desc}")
        if len(demographic_vars) > 15:
            lines.append(f"  ... and {len(demographic_vars) - 15} more demographic variables")

    if outcome_vars:
        lines.append("\n**Outcome/Indicator Variables (use as COLUMNS):**")
        for var_desc in outcome_vars[:15]:  # Limit to 15
            lines.append(f"- {var_desc}")
        if len(outcome_vars) > 15:
            lines.append(f"  ... and {len(outcome_vars) - 15} more outcome variables")

    # Add note if many variables
    total_vars = len(metadata)
    if total_vars > 50:
        lines.append(f"\n*Showing categorized variables. Total variables available: {total_vars}.*")

    return "\n".join(lines)


def _format_indicators_for_tables(indicators: Dict[str, Any]) -> str:
    """
    Format indicator definitions for table specification prompt.

    Shows indicator groups that can be used as column variables.

    Args:
        indicators: Indicator definitions dictionary

    Returns:
        Formatted text string for prompt inclusion

    Example:
        >>> indicators = {
        ...     "indicators": [
        ...         {"name": "Customer_Satisfaction", "variables": ["sat_q1", "sat_q2"], ...}
        ...     ]
        ... }
        >>> _format_indicators_for_tables(indicators)
        '### Indicator Groups\\n\\n1. **Customer_Satisfaction**...'
    """
    if not indicators or not indicators.get("indicators"):
        return "No indicators defined."

    lines = ["### Indicator Groups (use as COLUMNS)\n"]

    for i, indicator in enumerate(indicators["indicators"][:10], 1):  # Limit to 10
        name = indicator.get("name", "Unknown")
        description = indicator.get("description", "")
        variables = indicator.get("variables", [])

        lines.append(f"{i}. **{name}**")
        if description:
            lines.append(f"   - Description: {description}")
        if variables:
            vars_str = ", ".join(variables[:5])  # Show first 5 variables
            if len(variables) > 5:
                vars_str += f" ... (+{len(variables) - 5} more)"
            lines.append(f"   - Variables: {vars_str}")
        lines.append("")

    if len(indicators["indicators"]) > 10:
        lines.append(f"... and {len(indicators['indicators']) - 10} more indicators")

    return "\n".join(lines)


# =============================================================================
# Utility Functions
# =============================================================================

def estimate_token_count(text: str) -> int:
    """
    Estimate token count for a text string.

    Approximate calculation: ~4 characters per token for English text.

    Args:
        text: Text string to estimate

    Returns:
        Estimated token count
    """
    return len(text) // 4


def truncate_metadata_for_token_limit(
    metadata: List[Dict[str, Any]],
    max_tokens: int = 3000
) -> List[Dict[str, Any]]:
    """
    Truncate metadata list to fit within token limit.

    Keeps the most recodable variables first (numeric with value ranges).

    Args:
        metadata: Full metadata list
        max_tokens: Maximum tokens for metadata section

    Returns:
        Truncated metadata list
    """
    # Sort by recodability: numeric with ranges first
    def recodability_score(var: Dict[str, Any]) -> int:
        score = 0
        if var.get("variable_type") == "numeric":
            score += 10
        if var.get("min_value") is not None:
            score += 5
        if var.get("max_value") is not None:
            score += 5
        if var.get("value_labels"):
            score += len(var["value_labels"])
        return score

    sorted_metadata = sorted(metadata, key=recodability_score, reverse=True)

    # Estimate tokens and truncate
    result = []
    current_tokens = 0

    for var in sorted_metadata:
        var_str = str(var)
        var_tokens = estimate_token_count(var_str)

        if current_tokens + var_tokens > max_tokens:
            break

        result.append(var)
        current_tokens += var_tokens

    logger.info(
        f"Truncated metadata from {len(metadata)} to {len(result)} variables "
        f"(~{current_tokens} tokens)"
    )

    return result
