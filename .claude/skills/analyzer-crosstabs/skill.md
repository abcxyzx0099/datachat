---
name: stage3-crosstabs
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
           - Recoded: 12 indicators
           - COMPUTE: 3 indicators
           - No transformation: 30 indicators

           [Step 8] Generating cross-tabulations...
           Table pairs: 18 combinations
           Scenario detection:
           - cat_single (Single Categorical): 8 tables
           - cat_multi (Multiple Choice): 3 tables
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
- `statistic_type` (categorical or scalar)
- `source_variables` count (1 or multiple)

| Scenario | Row Type | source_variables | Output |
|----------|----------|------------------|--------|
| **1. cat_single** | Single Categorical | 1 | Column %, Total row with 100%, chi-square |
| **2. cat_multi** | Multiple Binary (Multiple Choice) | > 1 | % of Yes, Total row with base N only |
| **3. scalar_single** | Single Scalar | 1 | Mean, Median, Std, Min, Max |
| **4. scalar_multi** | Multiple Scalar (Rating Scale) | > 1 | Mean per attribute, Total row with base N |

### Scenario Examples

```
Scenario 1: Single Categorical × Single Categorical
Row: Q2_SATISFACTION (Very Satisfied, Satisfied, Neutral, Dissatisfied)
Col: Q1_GENDER (Male, Female)
Output: Column percentages, chi-square test

Scenario 2: Multiple Binary × Single Categorical (Multiple Choice)
Row: S1_BRAND_AWARENESS (Brand A, Brand B, Brand C, Brand D)
Col: Q1_GENDER (Male, Female)
Output: % of Yes for each brand, no chi-square

Scenario 3: Single Scalar × Single Categorical
Row: SAT_OVERALL (0-10 scale)
Col: Q1_GENDER (Male, Female)
Output: Mean, Median, Std, Min, Max by gender

Scenario 4: Multiple Scalar × Single Categorical (Rating Scale)
Row: D1_RATINGS (Quality, Price, Service, Selection, Value)
Col: Q1_GENDER (Male, Female)
Output: Mean for each attribute by gender
```

## Pure Python Implementation

### Dependencies

```python
import pandas as pd
from scipy.stats import chi2_contingency
import numpy as np
import json
from pathlib import Path
from survey_analyzer.analysis import CrosstabProcessor
```

### Step 7: Apply Transformations

```python
def apply_transformations(df, indicators):
    """
    Apply recoding and transformation rules from specification.

    Args:
        df: pandas DataFrame with SPSS data
        indicators: List of indicator specs with transformation_rules

    Returns:
        DataFrame with transformed variables
    """
    from survey_analyzer.analysis import TransformationEngine

    result_df = df.copy()
    engine = TransformationEngine()

    for indicator in indicators:
        code = indicator['indicator_code']
        source_vars = indicator.get('source_variables', [])
        rules = indicator.get('transformation_rules')

        if not rules or rules.lower() == 'null':
            # No transformation, use source as-is
            if source_vars and len(source_vars) == 1:
                result_df[code] = df[source_vars[0]]
            continue

        # Apply transformation
        if rules.startswith('COMPUTE'):
            # Computed variable
            result_df[code] = engine._apply_compute(result_df, rules, code)
        else:
            # Recoding rules
            result_df[code] = engine._apply_recode(df[source_vars[0]], rules)

    return result_df
```

### Step 8: Generate Cross-Tables (All Scenarios)

```python
def generate_all_crosstabs(df, spec):
    """
    Generate cross-tabulations for all row × column combinations.
    Auto-detects scenario and uses appropriate processor.

    Args:
        df: pandas DataFrame (transformed)
        spec: table_specification dict

    Returns:
        List of CrosstabResult objects
    """
    from survey_analyzer.analysis import CrosstabProcessor

    processor = CrosstabProcessor()
    results = processor.generate_batch(
        df=df,
        row_indicators=spec['row_indicators'],
        col_indicators=spec['column_indicators'],
        weight_var=spec.get('weight_indicator')
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
    # Load specification
    with open(spec_file) as f:
        spec = json.load(f)

    with open(metadata_file) as f:
        metadata = json.load(f)

    # Load SPSS data
    reader = SPSSReader()
    df, _ = reader.read(metadata['file_info']['path'])

    # Step 7: Apply transformations
    print("[Step 7] Applying transformations...")
    df_transformed = apply_transformations(df, spec['row_indicators'])

    # Step 8: Generate cross-tabs with statistics (auto-detect scenarios)
    print("[Step 8] Generating cross-tabulations...")
    processor = CrosstabProcessor()
    tables = processor.generate_batch(
        df=df_transformed,
        row_indicators=spec['row_indicators'],
        col_indicators=spec['column_indicators'],
        weight_var=spec.get('weight_indicator')
    )

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
```

## Output Format

### cross_tables_with_stats.json

```json
[
  {
    "table_id": "Q2_SATISFACTION_x_Q1_GENDER",
    "row_indicator": {
      "indicator_code": "Q2_SATISFACTION",
      "statistic_type": "categorical",
      "source_variables": ["Q2_SATISFACTION"],
      "question_type": "Single Choice"
    },
    "column_indicator": {
      "indicator_code": "Q1_GENDER",
      "statistic_type": "categorical",
      "source_variables": ["Q1_GENDER"],
      "question_type": "Single Choice"
    },
    "row_scenario": "cat_single",
    "col_scenario": "cat_single",
    "data": {
      "rows": [
        {"label": "Very Satisfied", "values": {"Male": 32.5, "Female": 38.8, "Total": 35.5}},
        {"label": "Satisfied", "values": {"Male": 45.2, "Female": 42.1, "Total": 43.7}}
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
| `survey_analyzer.analysis.CrosstabProcessor` | Main processor with scenario detection |
| `survey_analyzer.analysis.TransformationEngine` | Apply recoding and transformations |
| `survey_analyzer.analysis.scenario_detector.ScenarioDetector` | Detect crosstab scenario type |
| `survey_analyzer.analysis.processors.categorical_single` | Scenario 1 processor |
| `survey_analyzer.analysis.processors.categorical_multi` | Scenario 2 processor |
| `survey_analyzer.analysis.processors.scalar_single` | Scenario 3 processor |
| `survey_analyzer.analysis.processors.scalar_multi` | Scenario 4 processor |

## Data Flow

```
Stage 2 Specification (table_specification.jsonc)
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
| **Invalid transformation** | Use source variable as-is with warning |

## Statistical Interpretation

| Statistic | Description | Interpretation |
|-----------|-------------|----------------|
| **chi_square** | Chi-square test statistic | Larger values = stronger association |
| **p_value** | Probability of null hypothesis | p < 0.05 = significant relationship |
| **cramers_v** | Effect size (0-1) | 0.1=small, 0.3=medium, 0.5=large |

**Note**: Statistics are only calculated for categorical × categorical scenarios (cat_single × cat_single).

## Performance Notes

| Dataset Size | Estimated Time |
|--------------|----------------|
| 1,000 cases, 10 tables | ~2 seconds |
| 10,000 cases, 50 tables | ~15 seconds |
| 100,000 cases, 100 tables | ~2 minutes |

## Next Stage

After Stage 3 completes, proceed to **Stage 4: Statistical Filtering** (`analyzer-statistics`)
