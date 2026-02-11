---
name: spss-filter
description: 'Filter cross-tabulation tables by statistical significance criteria (p-value, Cramer's V, validity). Use when you need to identify which tables show significant relationships and should be included in reports.'
license: Apache-2.0
---

# SPSS Filter Skill

Filter cross-tabulation tables based on statistical significance criteria.

## Features

- **P-value filtering** - Include only tables below significance threshold
- **Cramer's V filtering** - Include only tables with sufficient effect size
- **Validity filtering** - Exclude tables with violated test assumptions
- **Detailed reporting** - See why each table was included/excluded
- **Summary statistics** - Inclusion rates, exclusion reasons

## Usage

### Basic Filtering

```
User: Filter these tables by significance (p<0.05, V>=0.1):

Table 1: p=0.032, V=0.18, valid=True
Table 2: p=0.156, V=0.08, valid=True
Table 3: p=0.003, V=0.32, valid=True
Table 4: p=0.044, V=0.09, valid=True
Table 5: p=0.002, V=0.28, invalid=True

Assistant: I'll filter your tables using default criteria (p<0.05, V>=0.10, require valid).

Results:
✓ Table 1: INCLUDE - Passed all filters
✗ Table 2: EXCLUDE - Not statistically significant (p=0.156 >= 0.05)
✓ Table 3: INCLUDE - Passed all filters
✗ Table 4: EXCLUDE - Effect size too small (V=0.09 < 0.10)
✗ Table 5: EXCLUDE - Invalid table (insufficient cell count)

Summary:
- Total: 5 tables
- Included: 2 (40%)
- Excluded: 3 (60%)

Exclusion reasons:
- Not significant: 1
- Effect size too small: 1
- Invalid table: 1
```

### From File

```
User: Filter tables in /data/statistics_results.json using lenient criteria

Assistant: I'll apply lenient filtering to your results.

Using lenient criteria:
- Significance level: 0.10 (instead of 0.05)
- Minimum Cramer's V: 0.05 (instead of 0.10)

Filtered results saved to /data/filtered_tables.json
```

### Custom Criteria

```
User: Filter with p<0.01 and only medium or larger effect sizes

Assistant: I'll filter using your stringent criteria.

Configuration:
- Significance level: 0.01 (highly significant)
- Minimum Cramer's V: 0.30 (medium effect)
- Require valid: Yes

Only tables with strong statistical evidence and meaningful effect sizes will be included.
```

## Filter Criteria

### Default Settings

| Criterion | Value | Description |
|-----------|-------|-------------|
| `significance_level` | 0.05 | Maximum p-value for inclusion |
| `min_cramers_v` | 0.1 | Minimum effect size for inclusion |
| `min_cell_count` | 10 | Minimum count in any cell |
| `require_valid` | True | Exclude tests with assumption violations |

### Criteria Presets

| Preset | Significance | Cramer's V | Use Case |
|--------|-------------|------------|----------|
| `default` | 0.05 | 0.10 | Standard market research |
| `lenient` | 0.10 | 0.05 | Exploratory analysis |
| `stringent` | 0.01 | 0.30 | High-impact findings only |
| `very_stringent` | 0.001 | 0.50 | Only very strong effects |

## Input Format

```json
{
    "tables": [
        {
            "table_name": "gender_x_satisfaction",
            "p_value": 0.032,
            "cramers_v": 0.18,
            "is_valid": true
        }
    ]
}
```

## Output

### Filter Results

```json
{
    "filters": [
        {
            "table_id": "gender_x_satisfaction",
            "include": true,
            "passes_significance": true,
            "passes_cramers_v": true,
            "passes_validity": true,
            "reason": "Passed all filters"
        }
    ],
    "summary": {
        "total_tables": 5,
        "included": 2,
        "excluded": 3,
        "inclusion_rate": 40.0
    }
}
```

### Apply Filter

Use the filter results to extract only included tables:

```
User: Extract only the significant tables from the original data

Assistant: I'll apply the filter to your cross-table data.

Included tables:
- gender_x_satisfaction
- region_x_preference

Filtered data saved to /data/significant_tables.json
```

## Configuration

```
User: Set custom filter criteria

Assistant: Current filter settings:
- Significance level: 0.05
- Minimum Cramer's V: 0.10
- Require valid: True

Available options:
1. Use preset (default/lenient/stringent)
2. Set custom values
3. Disable validity check

Which would you like?
```

## Requirements

- Python 3.11+
- Statistics results with p_value, cramers_v, is_valid fields

## Example Code

```python
from spss_analyzer.filtering import SignificanceFilter, FilterCriteria

criteria = FilterCriteria(
    significance_level=0.05,
    min_cramers_v=0.1,
    require_valid=True
)
filter_obj = SignificanceFilter(criteria)
filter_list = filter_obj.filter_tables(tables_with_stats)

# Apply filter to get only included tables
included = filter_obj.apply_filter(tables, filter_list.filters)
```

## Related Skills

- `spss-statistics` - Compute statistics before filtering
- `spss-reports` - Generate reports from filtered tables
