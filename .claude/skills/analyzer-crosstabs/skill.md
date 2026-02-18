---
name: stage3-crosstabs
description: 'Stage 3: Cross-Tabulation Generation - Applies transformations, generates cross-tables with chi-square and Cramer''s V statistics. Use when table specification is ready and cross-tabulation with statistics is needed.'
license: Apache-2.0
---

# Stage 3: Cross-Tabulation Generation

Applies transformations, generates cross-tables with chi-square and Cramer's V statistics.

## Overview

Executes **Steps 7-9** of the workflow:
- Step 7: Apply recoding and transformation rules
- Step 8: Generate cross-tabulations with statistics
- Step 9: Export tables + statistics to JSON

## When to Use

Use this skill when:
- Table specification is approved (Stage 2)
- Need to generate cross-tabulations
- Calculate chi-square and Cramer's V statistics
- Prepare data for significance filtering

## Usage

```
User: Generate crosstabs from the table specification

Assistant: [Step 7] Applying transformations...
           Processing 45 indicators with transformation rules
           - Recoded: 12 indicators
           - No transformation: 33 indicators

           [Step 8] Generating cross-tabulations...
           Table pairs: 18 combinations
           Computing chi-square and Cramer's V for each table...

           Progress:
           ████████████████████████████████ 100%

           [Step 9] Exporting results...
           Tables generated: 18
           Statistics calculated: 18 chi-square tests, 18 Cramer's V

           Saved: cross_tables_with_stats.json

           Stage 3 complete!
```

## Input

| Input | Required | Description |
|--------|-----------|-------------|
| `--spec-file` | Yes | Path to table_specification.json from Stage 2 |
| `--metadata-file` | Yes | Path to filtered_metadata.json from Stage 1 |
| `--output-dir` | No | Output directory (default: output/) |

## Output

| File | Content |
|-------|----------|
| `cross_tables_with_stats.json` | Cross-tables with chi-square, p-value, Cramer's V |

## Pure Python Implementation

### Dependencies

```python
import pandas as pd
from scipy.stats import chi2_contingency
import numpy as np
import json
from pathlib import Path
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
    result_df = df.copy()

    for indicator in indicators:
        code = indicator['indicator_code']
        rules = indicator.get('transformation_rules')

        if rules and rules.lower() != 'null':
            # Parse transformation rules: "(1 THRU 2=1) (3=2) (4 THRU 5=3)"
            recoded = parse_and_apply_recode(df[indicator['source_variables'][0]], rules)
            result_df[code] = recoded
        else:
            # No transformation, use source as-is
            result_df[code] = df[indicator['source_variables'][0]]

    return result_df
```

### Step 8: Generate Cross-Tables with Statistics

```python
def generate_crosstab_with_stats(df, row_var, col_var, weight_var=None):
    """
    Generate cross-tabulation with chi-square and Cramer's V.

    Args:
        df: pandas DataFrame
        row_var: Row variable name
        col_var: Column variable name
        weight_var: Optional weight variable

    Returns:
        Dict with crosstab and statistics
    """
    # Create contingency table
    if weight_var:
        crosstab = pd.crosstab(
            index=df[row_var],
            columns=df[col_var],
            values=df[weight_var],
            aggfunc='sum',
            margins=True,
            normalize='columns'
        )
    else:
        crosstab = pd.crosstab(
            index=df[row_var],
            columns=df[col_var],
            margins=True,
            normalize='columns'
        )

    # Remove margins for statistical test
    crosstab_for_test = crosstab.iloc[:-1, :-1]

    # Calculate chi-square test
    chi2, p_value, dof, expected = chi2_contingency(crosstab_for_test)

    # Calculate Cramer's V (effect size)
    n = crosstab_for_test.sum().sum()
    min_dim = min(crosstab_for_test.shape[0]-1, crosstab_for_test.shape[1]-1)
    cramers_v = np.sqrt(chi2 / (n * min_dim)) if min_dim > 0 else 0

    return {
        'crosstab': crosstab.to_dict(),
        'statistics': {
            'chi_square': float(chi2),
            'p_value': float(p_value),
            'degrees_of_freedom': int(dof),
            'cramers_v': float(cramers_v)
        }
    }
```

### Step 9: Export Results

```python
def export_results(tables, output_dir):
    """
    Export all tables with statistics to JSON.

    Args:
        tables: List of table dicts with crosstab and statistics
        output_dir: Output directory path
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    with open(output_path / "cross_tables_with_stats.json", "w") as f:
        json.dump(tables, f, indent=2)

    return output_path / "cross_tables_with_stats.json"
```

## Complete Workflow Example

```python
#!/usr/bin/env python3
"""
Stage 3: Cross-Tabulation Generation
Pure Python implementation using pandas and scipy.
"""

from pathlib import Path
import json
import pandas as pd
from scipy.stats import chi2_contingency
import numpy as np
from survey_analyzer.io import SPSSReader

def stage3_crosstabs(
    spec_file: str,
    metadata_file: str,
    output_dir: str = "output/"
):
    """
    Execute Stage 3: Cross-tabulation with statistics.

    Args:
        spec_file: Path to table_specification.json
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

    # Step 8: Generate cross-tabs with statistics
    print("[Step 8] Generating cross-tabulations...")
    tables = []

    for row_ind in spec['row_indicators']:
        for col_ind in spec['column_indicators']:
            result = generate_crosstab_with_stats(
                df_transformed,
                row_ind['indicator_code'],
                col_ind['indicator_code'],
                spec.get('weight_indicator')
            )
            tables.append(result)

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
    "table_id": "Q1_GENDER_RAW_x_GENDER",
    "row_indicator": "Q1_GENDER_RAW",
    "column_indicator": "GENDER",
    "crosstab": {
      "1": {"1": 45.2, "2": 54.8, "All": 100.0},
      "2": {"1": 52.1, "2": 47.9, "All": 100.0}
    },
    "statistics": {
      "chi_square": 12.34,
      "p_value": 0.002,
      "degrees_of_freedom": 1,
      "cramers_v": 0.087
    }
  }
]
```

## Statistical Interpretation

| Statistic | Description | Interpretation |
|-----------|-------------|----------------|
| **chi_square** | Chi-square test statistic | Larger values = stronger association |
| **p_value** | Probability of null hypothesis | p < 0.05 = significant relationship |
| **cramers_v** | Effect size (0-1) | 0.1=small, 0.3=medium, 0.5=large |

## Library Modules

| Module | Purpose |
|---------|---------|
| `survey_analyzer.analysis.TransformationEngine` | Apply recoding and transformations |
| `survey_analyzer.analysis.CrossTabGenerator` | Generate cross-tabs with statistics |
| `survey_analyzer.analysis.ResultsExporter` | Export to JSON format |

## Data Flow

```
Stage 2 Specification
    ↓ (table_specification.json)
Stage 1 Metadata
    ↓ (filtered_metadata.json)
Stage 3 Crosstabs
    ↓ (cross_tables_with_stats.json)
Stage 4 Statistics (filtering only)
```

## Error Handling

| Error Type | Handling |
|------------|-----------|
| **Missing variable** | Skip table, log warning |
| **Insufficient data** | Table marked with error, excluded |
| **Zero expected count** | Chi-square not computed, p_value = None |
| **Invalid transformation** | Use source variable as-is |

## Performance Notes

| Dataset Size | Estimated Time |
|--------------|----------------|
| 1,000 cases, 10 tables | ~2 seconds |
| 10,000 cases, 50 tables | ~15 seconds |
| 100,000 cases, 100 tables | ~2 minutes |

## Next Stage

After Stage 3 completes, proceed to **Stage 4: Statistical Filtering** (`stage4-statistics`)
