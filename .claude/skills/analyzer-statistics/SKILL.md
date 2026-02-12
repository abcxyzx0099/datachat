---
name: stage4-statistics
description: 'Stage 4: Statistical Analysis - Calculates chi-square tests and filters significant tables. Use when cross-tables are ready and statistical testing is needed.'
license: Apache-2.0
---

# Stage 4: Statistical Analysis

Performs chi-square tests and filters significant tables.

## Overview

Executes **Steps 10-11** of the workflow:
- Step 10: Calculate chi-square statistics
- Step 11: Filter significant tables

## When to Use

Use this skill when:
- Cross-tables are computed (Stage 3)
- Need to test table significance
- Filtering tables for reporting
- Preparing data for presentation generation

## Usage

```
User: Test significance of all crosstabs

Assistant: [Step 10] Calculating statistics...
           Chi-square tests: 18 tables
           Using threshold: p < 0.05

           Results:
           - Significant: 8 tables (44.4%)
           - Not significant: 10 tables (55.6%)
           - Errors: 0 tables

           Top significant findings:
           - Gender × Satisfaction: χ²=12.34, p=0.002 **
           - Age × Brand Rating: χ²=8.91, p=0.031 *
           - Region × NPS: χ²=15.67, p=0.004 **

           [Step 11] Filtering tables...
           Selected 8 significant tables for reporting
           Excluded 10 non-significant tables

           Saved: statistical_summary.json
           Saved: filtered_tables.json

           Stage 4 complete!
```

## Input

| Input | Required | Description |
|--------|-----------|-------------|
| `--crosstabs-file` | Yes | Path to cross_tables.json from Stage 3 |
| `--spec-file` | Yes | Path to table_specification.json |
| `--output-dir` | No | Output directory (default: output/) |
| `--threshold` | No | Override significance threshold (default: from spec) |

## Output

| File | Content |
|-------|----------|
| `statistical_summary.json` | Summary of all statistical tests |
| `filtered_tables.json` | List of significant tables only |

## Statistical Test

Chi-square test of independence:
- **Tests**: Whether row and column variables are independent
- **Null hypothesis**: Variables are independent (no relationship)
- **Alternative hypothesis**: Variables are related
- **Significance**: p < threshold (default 0.05)

## Output Format

### statistical_summary.json
```json
{
  "total_tests": 18,
  "significant_count": 8,
  "significance_threshold": 0.05
}
```

### filtered_tables.json
```json
[
  {
    "table_id": "gender_x_satisfaction",
    "table_name": "Gender by Satisfaction",
    "chi_square": 12.34,
    "p_value": 0.002,
    "degrees_of_freedom": 4,
    "expected": [[10.5, 12.3, ...], [...]],
    "significant": true
  }
]
```

## Significance Levels

| p-value range | Interpretation | Symbol |
|---------------|----------------|--------|
| p < 0.001 | Highly significant | *** |
| p < 0.01 | Very significant | ** |
| p < 0.05 | Significant | * |
| p >= 0.05 | Not significant | ns |

## Library Modules

| Module | Purpose |
|---------|---------|
| `scipy.stats.chi2_contingency` | Chi-square test |
| `pandas.DataFrame` | Data manipulation |
| `json` | Data serialization |

## Data Flow

```
Stage 3 Crosstabs
    ↓ (cross_tables.json)
Stage 4 Statistics
    ↓ (statistical_summary.json)
    ↓ (filtered_tables.json)
Stage 5 Reports
```

## Error Handling

| Error Type | Handling |
|------------|-----------|
| **Insufficient data** | Table marked with error, excluded |
| **Zero expected count** | Chi-square not computed, marked as error |
| **Invalid table format** | Error message logged, processing continues |

## Next Stage

After Stage 4 completes, proceed to **Stage 5: Reporting** (`stage5-reports`)
