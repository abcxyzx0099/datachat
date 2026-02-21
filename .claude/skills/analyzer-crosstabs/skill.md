---
name: analyzer-crosstabs
description: 'Stage 3: Cross-Tabulation Generation - Applies transformations, generates cross-tables for all 4 scenarios (categorical single/multi, scalar single/multi) with chi-square and Cramer''s V statistics. Use when table specification is ready and cross-tabulation with statistics is needed.'
license: Apache-2.0
---

# Stage 3: Cross-Tabulation Generation

Applies transformations, generates cross-tabulations for all 4 indicator scenarios with statistics.

## Overview

Executes **Steps 7-9** of the workflow:
- Step 7: Apply recoding and transformation rules
- Step 8: Generate cross-tabulations (auto-detects scenario type)
- Step 9: Export tables + statistics to JSON

## When to Use

Use this skill when:
- Table specification is approved (Stage 2)
- Need to generate cross-tabulations for any indicator type
- Calculate chi-square and Cramer's V statistics (for categorical × categorical)
- Prepare data for significance filtering

## Usage

```
User: Generate crosstabs from the table specification

Assistant: [Step 7] Applying transformations...
           Processing 45 indicators with transformation rules
           - Raw (no transformation): 15 indicators
           - Recoded (_cat): 12 indicators
           - Top 2 Box (_t2b): 8 indicators
           - Computed (_idx): 3 indicators
           - Binary (_bin): 7 indicators

           [Step 8] Generating cross-tabulations...
           Table pairs: 18 combinations
           Scenario detection based on tabulation_statistics.type and base_variables count:
           - cat_single (Single Categorical): 8 tables
           - cat_multi (Multiple Binary): 3 tables
           - scalar_single (Single Scalar): 2 tables
           - scalar_multi (Rating Scale): 5 tables
           Computing statistics...

           Progress:
           ████████████████████████████████ 100%

           [Step 9] Exporting results...
           Tables generated: 18
           Statistics calculated: 11 chi-square tests (categorical × categorical)

           Saved: cross_tables_with_stats.json

           Stage 3 complete!
```

## Input

| Input | Required | Description |
|--------|-----------|-------------|
| `--spec-file` | Yes | Path to table_specification.jsonc from Stage 2 |
| `--metadata-file` | Yes | Path to filtered_metadata.json from Stage 1 |
| `--output-dir` | No | Output directory (default: output/) |

## Output

| File | Content |
|-------|----------|
| `cross_tables_with_stats.json` | Cross-tables with chi-square, p-value, Cramer's V (when applicable) |

## The 4 Crosstab Scenarios

The `CrosstabProcessor` automatically detects the scenario based on:
- `tabulation_statistics.type` (categorical or scalar)
- `base_variables` count (1 or multiple)

| Scenario | Row Type | base_variables count | Output |
|----------|----------|---------------------|--------|
| **1. cat_single** | Single Categorical | 1 | Column %, Total row with 100%, chi-square |
| **2. cat_multi** | Multiple Binary (_bin) | > 1 | % of Yes, Total row with base N only |
| **3. scalar_single** | Single Scalar (_raw, _sca, _z, _pct) | 1 | Mean, Median, Std, Min, Max |
| **4. scalar_multi** | Multiple Scalar (Rating Scale attributes) | > 1 | Mean per attribute, Total row with base N |

### Scenario Examples

```
Scenario 1: Single Categorical × Single Categorical
Row: Q5_SATISFACTION_cat (Satisfaction - Low/Medium/High)
Col: Q1_GENDER_raw (Male, Female)
suffix: _cat for row, _raw for column
Output: Column percentages, chi-square test

Scenario 2: Multiple Binary × Single Categorical (Multiple Choice)
Row: Q1_BRAND_A_bin, Q1_BRAND_B_bin (Brand A, Brand B - Yes/No)
Col: Q1_GENDER_raw (Male, Female)
suffix: _bin for row variables
Output: % of Yes for each brand, no chi-square

Scenario 3: Single Scalar × Single Categorical
Row: S1_AGE_raw (Age in years)
Col: Q1_GENDER_raw (Male, Female)
suffix: _raw or _sca
Output: Mean, Median, Std, Min, Max by gender

Scenario 4: Multiple Scalar × Single Categorical (Rating Scale)
Row: D1_QUALITY_raw, D1_PRICE_raw, D1_SERVICE_raw (Quality, Price, Service ratings)
Col: Q1_GENDER_raw (Male, Female)
suffix: _raw for each attribute
Output: Mean for each attribute by gender
```

## Suffix-Based Detection

The scenario type is determined by examining `base_variables[].suffix`:

| Suffix Pattern | Scenario |
|---------------|----------|
| Single variable with `_raw`, `_cat`, `_bin`, `_t2b`, `_b2b`, `_nps` | `cat_single` or `scalar_single` |
| Multiple variables with `_bin` | `cat_multi` |
| Single variable with `_sca`, `_idx`, `_z`, `_pct` | `scalar_single` |
| Multiple variables with `_raw` (rating attributes) | `scalar_multi` |

## Pure Python Implementation

### Dependencies

```python
import pandas as pd
from scipy.stats import chi2_contingency
import numpy as np
import json
from pathlib import Path
from survey_analyzer.specification.schema import TableSpecification
```

### Step 7: Apply Transformations

```python
def apply_transformations(df, indicators):
    """
    Apply recoding and transformation rules from specification.

    Args:
        df: pandas DataFrame with SPSS data
        indicators: List of IndicatorSpec from table_specification.jsonc

    Returns:
        DataFrame with transformed variables
    """
    from survey_analyzer.analysis import TransformationEngine

    result_df = df.copy()
    engine = TransformationEngine()

    for indicator in indicators:
        for base_var in indicator.base_variables:
            var_name = base_var.name
            generation = base_var.generation

            if not generation or generation.lower() == 'null':
                # Raw variable - copy from source if needed
                # The base_variable.name should exist in df or be created from source
                if var_name not in df.columns:
                    # Try to find source variable (name without suffix)
                    source_name = var_name.rsplit('_', 1)[0]  # Remove suffix to get source
                    if source_name in df.columns:
                        result_df[var_name] = df[source_name]
                continue

            # Apply transformation based on generation syntax
            if generation.startswith('RECODE'):
                result_df[var_name] = engine._apply_recode(df, generation)
            elif generation.startswith('COMPUTE'):
                result_df[var_name] = engine._apply_compute(result_df, generation, var_name)
            elif generation.startswith('SELECT IF'):
                # Validation rule - filter rows
                # This is handled at dataset level, not variable level
                pass

    return result_df
```

### Step 8: Generate Cross-Tables (All Scenarios)

```python
def generate_all_crosstabs(df, spec: TableSpecification):
    """
    Generate cross-tabulations for all row × column combinations.
    Auto-detects scenario based on tabulation_statistics.type and base_variables.

    Args:
        df: pandas DataFrame (transformed)
        spec: TableSpecification object

    Returns:
        List of CrosstabResult objects
    """
    from survey_analyzer.analysis import CrosstabProcessor

    processor = CrosstabProcessor()
    results = processor.generate_batch(
        df=df,
        row_indicators=spec.row_indicators,
        col_indicators=spec.column_indicators,
        weight_var=spec.weight_indicator
    )

    return results
```

### Step 9: Export Results

```python
def export_results(tables, output_dir):
    """
    Export all tables with statistics to JSON.

    Args:
        tables: List of CrosstabResult objects
        output_dir: Output directory path
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Convert to dict format
    tables_dict = [t.to_dict() for t in tables]

    with open(output_path / "cross_tables_with_stats.json", "w") as f:
        json.dump(tables_dict, f, indent=2, default=str)

    return output_path / "cross_tables_with_stats.json"
```

## Complete Workflow Example

```python
#!/usr/bin/env python3
"""
Stage 3: Cross-Tabulation Generation
Pure Python implementation using CrosstabProcessor.
"""

from pathlib import Path
import json
import pandas as pd
from survey_analyzer.specification.schema import TableSpecification
from survey_analyzer.io import SPSSReader
from survey_analyzer.analysis import CrosstabProcessor, TransformationEngine

def stage3_crosstabs(
    spec_file: str,
    metadata_file: str,
    output_dir: str = "output/"
):
    """
    Execute Stage 3: Cross-tabulation with statistics.

    Args:
        spec_file: Path to table_specification.jsonc
        metadata_file: Path to filtered_metadata.json
        output_dir: Output directory
    """
    # Load specification using new schema
    spec = TableSpecification.load_from_file(spec_file)

    # Load metadata
    with open(metadata_file) as f:
        metadata = json.load(f)

    # Load SPSS data
    reader = SPSSReader()
    df, _ = reader.read(metadata['file_info']['path'])

    # Apply filter clause if present
    if spec.filter_clause:
        df = apply_filter_clause(df, spec.filter_clause)

    # Step 7: Apply transformations
    print("[Step 7] Applying transformations...")
    df_transformed = apply_transformations(df, spec.row_indicators)

    # Step 8: Generate cross-tabs with statistics (auto-detect scenarios)
    print("[Step 8] Generating cross-tabulations...")
    tables = generate_all_crosstabs(df_transformed, spec)

    # Log scenario breakdown
    scenarios = {}
    for table in tables:
        scenario = table.row_scenario
        scenarios[scenario] = scenarios.get(scenario, 0) + 1
    print(f"  Scenarios: {scenarios}")

    # Step 9: Export results
    print("[Step 9] Exporting results...")
    output_path = export_results(tables, output_dir)

    print(f"✓ Generated {len(tables)} tables")
    print(f"✓ Output: {output_path}")

    return tables


def apply_filter_clause(df, filter_clause):
    """Apply filter rules from specification."""
    filtered_df = df.copy()

    if 'age_min' in filter_clause and 'age_max' in filter_clause:
        age_col = None
        for col in df.columns:
            if 'age' in col.lower():
                age_col = col
                break
        if age_col:
            filtered_df = filtered_df[
                (filtered_df[age_col] >= filter_clause['age_min']) &
                (filtered_df[age_col] <= filter_clause['age_max'])
            ]

    if filter_clause.get('exclude_incomplete'):
        # Exclude rows with excessive missing values
        threshold = 0.5  # More than 50% missing
        missing_ratio = filtered_df.isnull().sum(axis=1) / len(filtered_df.columns)
        filtered_df = filtered_df[missing_ratio <= threshold]

    return filtered_df
```

## Output Format

### cross_tables_with_stats.json

```json
[
  {
    "table_id": "Q5_SATISFACTION_cat_x_Q1_GENDER_raw",
    "row_indicator": {
      "indicator_code": "Q5_SATISFACTION_CAT",
      "indicator_label": "Satisfaction - Categorical",
      "tabulation_statistics": {
        "type": "categorical",
        "metric": "column_percent"
      },
      "base_variables": [
        {
          "name": "Q5_SATISFACTION_cat",
          "suffix": "_cat",
          "label": "Satisfaction (grouped)"
        }
      ]
    },
    "column_indicator": {
      "indicator_code": "Q1_GENDER",
      "indicator_label": "Gender",
      "tabulation_statistics": {
        "type": "categorical",
        "metric": "column_percent"
      },
      "base_variables": [
        {
          "name": "Q1_GENDER_raw",
          "suffix": "_raw",
          "label": "Gender"
        }
      ]
    },
    "row_scenario": "cat_single",
    "col_scenario": "cat_single",
    "data": {
      "rows": [
        {"label": "Low", "values": {"Male": 32.5, "Female": 38.8, "Total": 35.5}},
        {"label": "Medium", "values": {"Male": 45.2, "Female": 42.1, "Total": 43.7}},
        {"label": "High", "values": {"Male": 22.3, "Female": 19.1, "Total": 20.8}}
      ],
      "total_row": {
        "label": "Total",
        "values": {"Male": 100.0, "Female": 100.0, "Total": 100.0},
        "base_n": {"Male": 180, "Female": 170, "Total": 350}
      }
    },
    "has_total_column": true,
    "has_total_row": true,
    "total_row_type": "full",
    "base_n": {"Male": 180, "Female": 170, "Total": 350},
    "statistics": {
      "chi_square": 2.34,
      "p_value": 0.31,
      "cramers_v": 0.08,
      "interpretation": "negligible",
      "is_significant": false
    },
    "is_valid": true
  }
]
```

## Library Modules

| Module | Purpose |
|---------|---------|
| `survey_analyzer.specification.schema` | **NEW** TableSpecification, IndicatorSpec, BaseVariable, TabulationStats |
| `survey_analyzer.analysis.CrosstabProcessor` | Main processor with scenario detection |
| `survey_analyzer.analysis.TransformationEngine` | Apply recoding and transformations |
| `survey_analyzer.analysis.scenario_detector.ScenarioDetector` | Detect crosstab scenario type from suffix and count |
| `survey_analyzer.analysis.processors.categorical_single` | Scenario 1 processor |
| `survey_analyzer.analysis.processors.categorical_multi` | Scenario 2 processor |
| `survey_analyzer.analysis.processors.scalar_single` | Scenario 3 processor |
| `survey_analyzer.analysis.processors.scalar_multi` | Scenario 4 processor |

## Data Flow

```
Stage 2 Specification (table_specification.jsonc)
    ├─ questionnaire_questions[] (code, label, type)
    ├─ base_variables[] (name, label, suffix, values, generation)
    └─ tabulation_statistics{} (type, metric, explicit)
    ↓
Stage 1 Metadata (filtered_metadata.json)
    ↓
Stage 3 Crosstabs (CrosstabProcessor with 4 scenarios)
    ↓
cross_tables_with_stats.json
    ↓
Stage 4 Statistics (filtering by p-value)
```

## Error Handling

| Error Type | Handling |
|------------|-----------|
| **Missing variable** | Table marked invalid, error message included |
| **Insufficient data** | Statistics not computed, table still generated |
| **Zero expected count** | Chi-square not computed, p_value = None |
| **Invalid generation syntax** | Use source variable as-is with warning |

## Statistical Interpretation

| Statistic | Description | Interpretation |
|-----------|-------------|----------------|
| **chi_square** | Chi-square test statistic | Larger values = stronger association |
| **p_value** | Probability of null hypothesis | p < 0.05 = significant relationship |
| **cramers_v** | Effect size (0-1) | 0.1=small, 0.3=medium, 0.5=large |

**Note**: Statistics are only calculated for categorical × categorical scenarios (cat_single × cat_single).

## Suffix Reference

| Suffix | Meaning | Generation Pattern |
|--------|---------|-------------------|
| `_raw` | No transformation | `null` |
| `_bin` | Binary (0/1) | `RECODE var (values=1) (ELSE=0) INTO var_bin` |
| `_cat` | Categorical recoded | `RECODE var (old=new) INTO var_cat` |
| `_t2b` | Top 2 Box | `RECODE var (4 THRU 5=1) (ELSE=0) INTO var_t2b` |
| `_b2b` | Bottom 2 Box | `RECODE var (1 THRU 2=1) (ELSE=0) INTO var_b2b` |
| `_nps` | NPS categorization | `RECODE var (9 THRU 10=3) (7 THRU 8=2) INTO var_nps` |
| `_sca` | Scalar (no change) | `null` |
| `_idx` | Computed index | `COMPUTE var_idx = MEAN(v1, v2, v3)` |
| `_z` | Z-score | `COMPUTE var_z = (var - MEAN(var)) / SD(var)` |
| `_pct` | Percentile | `COMPUTE var_pct = RANK(var) / N * 100` |

## Performance Notes

| Dataset Size | Estimated Time |
|--------------|----------------|
| 1,000 cases, 10 tables | ~2 seconds |
| 10,000 cases, 50 tables | ~15 seconds |
| 100,000 cases, 100 tables | ~2 minutes |

## Next Stage

After Stage 3 completes, proceed to **Stage 4: Statistical Filtering** (`analyzer-statistics`)
