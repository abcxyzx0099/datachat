---
name: stage4-statistics
description: 'Stage 6: Statistical Filtering - Filters tables by significance (p-value) and generates summary report. Statistics are calculated in Stage 5. Use when cross-tables with statistics are ready and filtering is needed.'
license: Apache-2.0
---

# Stage 6: Statistical Filtering

Filters tables by significance and generates summary report.

## Overview

Executes **Steps 10-11** of the workflow:
- Step 10: Filter tables by p-value < 0.05
- Step 11: Generate statistical summary report

**Note:** Chi-square and Cramer's V statistics are calculated in **Stage 5**. This stage only filters and summarizes results.

## When to Use

Use this skill when:
- Cross-tables with statistics are computed (Stage 5)
- Need to filter tables for reporting
- Preparing data for presentation generation
- Generating statistical summary

## Usage

```
User: Filter significant tables from the crosstabs

Assistant: [Step 10] Filtering by significance...
           Input tables: 18
           Threshold: p < 0.05

           Results:
           - Significant: 8 tables (44.4%)
           - Not significant: 10 tables (55.6%)

           [Step 11] Generating summary...
           Created statistical summary report

           Top significant findings:
           - Gender × Satisfaction: χ²=12.34, p=0.002 **
           - Age × Brand Rating: χ²=8.91, p=0.031 *
           - Region × NPS: χ²=15.67, p=0.004 **

           Saved: statistical_summary.json
           Saved: filtered_tables.json

           Stage 6 complete!
```

## Input

| Input | Required | Description |
|--------|-----------|-------------|
| `--crosstabs-file` | Yes | Path to cross_tables_with_stats.json from Stage 5 |
| `--threshold` | No | Significance threshold (default: 0.05) |
| `--output-dir` | No | Output directory (default: output/) |

## Output

| File | Content |
|-------|----------|
| `filtered_tables.json` | Tables with p-value < threshold |
| `statistical_summary.json` | Summary of all statistical tests |

## Pure Python Implementation

### Dependencies

```python
import json
from pathlib import Path
from typing import List, Dict, Any
```

### Step 10: Filter by Significance

```python
def filter_significance(
    tables: List[Dict[str, Any]],
    threshold: float = 0.05
) -> tuple[List[Dict], Dict]:
    """
    Filter tables by p-value threshold.

    Args:
        tables: List of tables with statistics
        threshold: P-value threshold for significance

    Returns:
        Tuple of (filtered_tables, summary_dict)
    """
    significant = []
    not_significant = []
    summary_stats = {
        'total_tables': len(tables),
        'significant_count': 0,
        'not_significant_count': 0,
        'significance_threshold': threshold,
        'tables': []
    }

    for table in tables:
        stats = table.get('statistics', {})
        p_value = stats.get('p_value')

        if p_value is None:
            # Handle missing statistics
            table['is_significant'] = False
            table['error'] = 'Missing p_value'
            not_significant.append(table)
        elif p_value < threshold:
            table['is_significant'] = True
            significant.append(table)
            summary_stats['significant_count'] += 1
        else:
            table['is_significant'] = False
            not_significant.append(table)
            summary_stats['not_significant_count'] += 1

        # Add to summary
        summary_stats['tables'].append({
            'table_id': table.get('table_id'),
            'p_value': p_value,
            'chi_square': stats.get('chi_square'),
            'cramers_v': stats.get('cramers_v'),
            'is_significant': table['is_significant']
        })

    return significant, summary_stats
```

### Step 11: Generate Summary Report

```python
def generate_summary_report(summary_stats: Dict) -> Dict:
    """
    Generate statistical summary report.

    Args:
        summary_stats: Summary dictionary from filter_significance

    Returns:
        Enhanced summary with interpretations
    """
    total = summary_stats['total_tables']
    sig_count = summary_stats['significant_count']

    # Calculate percentages
    summary_stats['significant_percentage'] = round(
        (sig_count / total * 100) if total > 0 else 0, 1
    )

    # Sort by p-value for ranking
    sorted_tables = sorted(
        [t for t in summary_stats['tables'] if t['p_value'] is not None],
        key=lambda x: x['p_value']
    )

    summary_stats['top_findings'] = sorted_tables[:10]

    # Add significance level interpretations
    for table in summary_stats['tables']:
        if table['p_value'] is not None:
            if table['p_value'] < 0.001:
                table['significance_level'] = '***'
                table['interpretation'] = 'Highly significant'
            elif table['p_value'] < 0.01:
                table['significance_level'] = '**'
                table['interpretation'] = 'Very significant'
            elif table['p_value'] < 0.05:
                table['significance_level'] = '*'
                table['interpretation'] = 'Significant'
            else:
                table['significance_level'] = 'ns'
                table['interpretation'] = 'Not significant'

    return summary_stats
```

### Complete Workflow

```python
#!/usr/bin/env python3
"""
Stage 6: Statistical Filtering
Filters tables by significance and generates summary.
"""

from pathlib import Path
import json

def stage4_filtering(
    crosstabs_file: str,
    output_dir: str = "output/",
    threshold: float = 0.05
):
    """
    Execute Stage 6: Statistical filtering.

    Args:
        crosstabs_file: Path to cross_tables_with_stats.json
        output_dir: Output directory
        threshold: Significance threshold
    """
    # Load tables with statistics
    with open(crosstabs_file) as f:
        tables = json.load(f)

    # Step 10: Filter by significance
    print(f"[Step 10] Filtering by significance (p < {threshold})...")
    filtered_tables, summary = filter_significance(tables, threshold)

    print(f"  Total tables: {summary['total_tables']}")
    print(f"  Significant: {summary['significant_count']} ({summary['significant_percentage']}%)")
    print(f"  Not significant: {summary['not_significant_count']}")

    # Step 11: Generate summary
    print("[Step 11] Generating summary report...")
    summary = generate_summary_report(summary)

    # Save outputs
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    with open(output_path / "filtered_tables.json", "w") as f:
        json.dump(filtered_tables, f, indent=2)

    with open(output_path / "statistical_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    print(f"✓ Saved: {output_path / 'filtered_tables.json'}")
    print(f"✓ Saved: {output_path / 'statistical_summary.json'}")

    return filtered_tables, summary
```

## Output Format

### filtered_tables.json

```json
[
  {
    "table_id": "gender_x_satisfaction",
    "row_indicator": "Q1_GENDER_RAW",
    "column_indicator": "GENDER",
    "crosstab": {...},
    "statistics": {
      "chi_square": 12.34,
      "p_value": 0.002,
      "degrees_of_freedom": 1,
      "cramers_v": 0.087
    },
    "is_significant": true
  }
]
```

### statistical_summary.json

```json
{
  "total_tables": 18,
  "significant_count": 8,
  "not_significant_count": 10,
  "significance_threshold": 0.05,
  "significant_percentage": 44.4,
  "top_findings": [
    {
      "table_id": "region_x_nps",
      "p_value": 0.001,
      "chi_square": 15.67,
      "cramers_v": 0.12,
      "is_significant": true,
      "significance_level": "***",
      "interpretation": "Highly significant"
    }
  ],
  "tables": [...]
}
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
| `survey_analyzer.filtering.SignificanceFilter` | Filter by p-value threshold |
| `survey_analyzer.reporting.SummaryGenerator` | Generate statistical summary |

## Data Flow

```
Stage 5 Crosstabs (with statistics)
    ↓ (cross_tables_with_stats.json)
Stage 6 Filtering
    ↓ (filtered_tables.json)
    ↓ (statistical_summary.json)
Stage 7 Reports
```

## Error Handling

| Error Type | Handling |
|------------|-----------|
| **Missing p_value** | Table marked as not significant, logged |
| **Invalid threshold** | Use default 0.05, log warning |
| **Empty input** | Return empty results, log error |

## Next Stage

After Stage 6 completes, proceed to **Stage 7: Reporting** (`analyzer-reports`)
