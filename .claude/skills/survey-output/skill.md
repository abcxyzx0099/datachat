# Survey Output Generator

Generates final reports (PowerPoint presentation and HTML dashboard) from analyzed data.

## Overview

This skill creates the final outputs of the survey analysis workflow:

1. **PowerPoint Presentation** - Executive summary with significant tables only
2. **HTML Dashboard** - Interactive dashboard with all tables and charts

## When to Use

Use this skill when:
1. You have completed the analysis workflow (cross-tables, statistics, filtering)
2. You want to generate the final reports
3. You need to present results to stakeholders

## Input Requirements

The skill requires:
1. **Table specification** - The validated `table_specification.json`
2. **Cross-table data** - Generated cross-tabulation tables
3. **Statistical summary** - Chi-square and Cramer's V results
4. **Filtered tables** - List of significant tables (for PowerPoint)

## Output

Produces:
- `presentation.pptx` - PowerPoint with significant tables
- `dashboard.html` - Interactive HTML dashboard with all tables

## PowerPoint Contents

The PowerPoint includes:
- Title slide
- Methodology slide
- Significant tables (up to `max_tables_ppt` from specification)
- Each table shows:
  - Cross-tabulation with counts and percentages
  - Statistical test results (χ², p-value, Cramer's V)
  - Significance indicator

## HTML Dashboard Contents

The HTML dashboard includes:
- All tables (not just significant ones)
- Interactive charts (heatmaps, bar charts)
- Sidebar navigation
- Statistical summaries
- CSV export functionality
- Significance highlighting

## Example Usage

```
Generate the final reports:

Specification: table_specification.json
Cross-tables: output/cross_tables.csv
Statistics: output/statistical_summary.json
Filtered tables: output/filtered_tables.json
```

## Customization

The output can be customized via the specification's `output_settings`:
- `dashboard_title` - Custom title for HTML dashboard
- `include_charts` - Include or exclude charts
- `chart_type` - Chart style (bar, column, heatmap, mosaic)
- `ppt_template` - Custom PowerPoint template
