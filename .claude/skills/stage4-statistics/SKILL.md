---
name: stage4-statistics
description: 'Stage 4: Statistical Analysis - Calculate statistics (chi-square, Cramer's V) and filter significant tables. Output: statistical_summary.json, filtered_tables.json. Use when analyzing cross-tables for significance.'
license: Apache-2.0
---

# Stage 4: Statistical Analysis

Perform statistical testing and significance filtering on cross-tables.

## Overview

Executes **Steps 10-11** of the workflow:
- Step 10: Statistical analysis
- Step 11: Filter significant tables

## When to Use

Use this skill when:
- Cross-tables are generated (Stage 3 complete)
- Need to identify significant findings
- Preparing for report generation

## Usage

```
User: Run statistical analysis

Assistant: [Step 10] Calculating statistics...
           Chi-square tests: 25 tables
           Cramer's V computed: 25 tables
           Created: statistical_summary.json

           [Step 11] Filtering significant tables...
           Threshold: p < 0.05
           Passed: 18/25 tables (72%)
           Created: filtered_tables.json

Stage 4 complete! Ready for report generation.
```

## Input

| Input | Required | Description |
|--------|-----------|-------------|
| `cross_tables.csv` | Yes | From Stage 3 output |
| `table_specification.json` | Yes | For significance threshold |

## Output

| File | Content |
|-------|----------|
| `statistical_summary.json` | Chi-square, p-values, Cramer's V |
| `filtered_tables.json` | Tables passing significance threshold |

## Statistical Tests

| Test | Purpose |
|-------|---------|
| Chi-square | Test independence between variables |
| p-value | Significance level |
| Cramer's V | Effect size for categorical data |

## Library Modules

| Module | Purpose |
|---------|---------|
| `spss_analyzer.analysis.StatisticsCalculator` | Chi-square, p-value, Cramer's V |
| `spss_analyzer.filtering.SignificanceFilter` | Filter by significance threshold |

## Configuration

Significance threshold from `table_specification.json`:

```json
{
  "output_settings": {
    "significance_threshold": 0.05,
    "min_sample_size": 30
  }
}
```
