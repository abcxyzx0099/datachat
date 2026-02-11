---
name: spss-statistics
description: 'Compute Chi-square test of independence and Cramer's V effect size for cross-tabulation tables. Use when you need to analyze statistical relationships between categorical variables in survey data.'
license: Apache-2.0
---

# SPSS Statistics Skill

Calculate statistical tests for cross-tabulation tables using the SPSS Analyzer library.

## Features

- **Chi-square test of independence** - Tests whether two categorical variables are related
- **Cramer's V effect size** - Measures strength of association (negligible, small, medium, large)
- **P-value calculation** - Statistical significance testing
- **Assumption validation** - Checks expected frequencies and cell counts
- **Effect size interpretation** - Automatic classification based on Cohen's guidelines

## Usage

### Basic Usage

```
User: Calculate statistics for this table: Male/Female vs Yes/No with counts [[45, 32], [52, 28]]

Assistant: I'll calculate the Chi-square test and Cramer's V for your table.

Results:
- Chi-square: 1.4149
- Degrees of freedom: 1
- P-value: 0.2342
- Cramer's V: 0.0841 (negligible)
- Significant (p<0.05): No

The relationship between gender and response is not statistically significant.
```

### From File

```
User: Compute statistics for all cross-tables in /data/cross_table.json

Assistant: I'll compute Chi-square and Cramer's V for each table in your file.

Processing 15 tables...
[Calculating...]

Results summary:
- Total tables: 15
- Significant: 8 (53.3%)
- Not significant: 7 (46.7%)

See /data/statistics_results.json for detailed results.
```

## Input Formats

### Table Data (Dictionary)

```python
{
    "counts": [[45, 32], [52, 28]],      # 2x2 contingency table
    "row_labels": ["Male", "Female"],
    "column_labels": ["Yes", "No"]
}
```

### From File

Provide path to JSON file with cross-table data:
```json
{
    "tables": [
        {
            "table_name": "gender_x_response",
            "row_labels": ["Male", "Female"],
            "col_labels": ["Yes", "No"],
            "counts": [[45, 32], [52, 28]]
        }
    ]
}
```

## Output

The skill returns a dictionary with:

| Field | Description |
|-------|-------------|
| `chi_square` | Chi-square test statistic |
| `degrees_of_freedom` | Degrees of freedom for the test |
| `p_value` | P-value (probability under null hypothesis) |
| `cramers_v` | Cramer's V effect size (0-1) |
| `interpretation` | Effect size category (negligible/small/medium/large) |
| `is_significant` | True if p < significance_level (default 0.05) |
| `is_valid` | True if test assumptions were met |
| `error` | Error message if assumptions violated |

## Interpretation Guidelines

### Cramer's V Effect Size

| Value | Interpretation |
|-------|----------------|
| 0.00 - 0.10 | Negligible association |
| 0.10 - 0.30 | Small association |
| 0.30 - 0.50 | Medium association |
| > 0.50 | Large association |

### P-Value

- **p < 0.05**: Statistically significant (reject null hypothesis)
- **p >= 0.05**: Not statistically significant (fail to reject null)

## Configuration Options

```
User: Set significance level to 0.01 and minimum expected frequency to 10

Assistant: Configuration updated:
- Significance level: 0.01 (more stringent)
- Minimum expected frequency: 10
- Minimum cell count: 10
```

## Requirements

- Python 3.11+
- scipy (for chi-square calculation)
- numpy (for numerical operations)

## Example Code

```python
from spss_analyzer.analysis import StatisticsCalculator

calc = StatisticsCalculator(significance_level=0.05)
result = calc.analyze_table(
    counts=[[45, 32], [52, 28]],
    row_labels=["Male", "Female"],
    column_labels=["Yes", "No"]
)
```

## Related Skills

- `spss-filter` - Filter tables by significance criteria
- `spss-reports` - Generate PowerPoint and HTML reports with statistics
