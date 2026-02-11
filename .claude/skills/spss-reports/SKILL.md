---
name: spss-reports
description: 'Generate survey analysis reports including PowerPoint presentations and interactive HTML dashboards. Use when you need to create visual reports from cross-tabulation and statistical results.'
license: Apache-2.0
---

# SPSS Reports Skill

Generate professional survey analysis reports from cross-tabulation results.

## Features

- **PowerPoint presentations** - Executive summary with charts
- **HTML dashboards** - Interactive exploration with filtering
- **Significance highlighting** - Visual indication of significant tables
- **Professional styling** - Market research quality output
- **Multiple chart types** - Bar, horizontal bar, line, stacked

## Usage

### PowerPoint Report

```
User: Create PowerPoint from these significant tables

Assistant: I'll generate a PowerPoint presentation with your results.

Creating presentation with:
- Title slide: "Survey Analysis Results"
- Summary slide: 2/5 tables significant (40%)
- Table slides with charts:
  * Gender x Satisfaction (Significant)
  * Region x Preference (Significant)

Presentation saved to: output/survey_report.pptx
```

### HTML Dashboard

```
User: Generate an interactive HTML dashboard

Assistant: I'll create a dashboard with all your tables.

Dashboard features:
- Summary statistics
- All tables with interactive charts
- Significance highlighting (green/red borders)
- Filtering by significance, p-value, Cramer's V
- Sidebar navigation
- CSV export capability

Dashboard saved to: output/dashboard.html
```

### Custom Styling

```
User: Create PowerPoint with blue color scheme and company template

Assistant: I'll generate your custom presentation.

Configuration:
- Template: company_template.pptx
- Color scheme: Professional Blue
- Chart type: Clustered column
- Show statistics: Yes
- Show significance badges: Yes

Presentation saved to: output/company_report.pptx
```

## PowerPoint Options

| Option | Values | Default |
|--------|--------|---------|
| Template | Path to .pptx file | None (blank) |
| Color scheme | professional/blue/green | professional |
| Show charts | Yes/No | Yes |
| Show statistics | Yes/No | Yes |
| Show significance badge | Yes/No | Yes |
| Chart type | bar/horizontal/line | auto |

## HTML Dashboard Features

### Summary Section
- Total tables analyzed
- Number of significant tables
- Significance rate
- Valid tests count

### Table Cards
- Variable names (Row × Column)
- Interactive Chart.js chart
- Data table with counts and percentages
- Statistics footer (χ², p, V)
- Significance badge (green/red)

### Filtering Controls
- Search by table name
- Show significant only
- Filter by p-value threshold
- Filter by Cramer's V threshold
- Sort by name/p-value/Cramer's V
- Export visible tables to CSV

### Navigation
- Sidebar with all tables
- Significance indicators (✓/✗)
- Click to scroll to table

## Input Format

### Tables Data

```json
{
    "tables": [
        {
            "table_id": "gender_x_satisfaction",
            "table_name": "gender_x_satisfaction",
            "row_variable": "Gender",
            "column_variable": "Satisfaction",
            "data": {
                "row_labels": ["Male", "Female"],
                "column_labels": ["Satisfied", "Dissatisfied"],
                "counts": [[45, 32], [52, 28]],
                "column_percentages": [[58.4, 41.6], [65.0, 35.0]]
            }
        }
    ]
}
```

### Statistics Data

```json
{
    "significance_level": 0.05,
    "tables": [
        {
            "table_name": "gender_x_satisfaction",
            "chi_square": 2.15,
            "p_value": 0.032,
            "cramers_v": 0.18,
            "interpretation": "small",
            "is_significant": true,
            "is_valid": true
        }
    ]
}
```

## Output

### PowerPoint File
- Format: `.pptx`
- Slides: Title + Summary + One per table
- Charts: Based on table dimensions
- Styling: Professional market research theme

### HTML Dashboard
- Format: `.html`
- Size: ~15-30KB (self-contained)
- Dependencies: Chart.js CDN
- Browser: Modern browsers with JavaScript

## Configuration Examples

```
User: Create minimal dashboard (no charts, no filters)

Assistant: I'll generate a simplified HTML dashboard.

Minimal dashboard settings:
- Charts: Disabled
- Filtering: Disabled
- Export: Disabled
- Navigation: Simplified

Output: tables_only.html (compact, data-focused)
```

```
User: Create presentation with dark theme charts

Assistant: I'll configure dark theme for chart colors.

Dark theme applied:
- Background: Dark gray
- Chart colors: High contrast palette
- Text: White/light gray

Presentation: dark_theme_report.pptx
```

## Chart Type Selection

Automatic based on table dimensions:

| Row Categories | Column Categories | Chart Type |
|---------------|-------------------|------------|
| 2-3 | 2-3 | Clustered column |
| 2-4 | 2-3 | Clustered column |
| 3-8 | 2 | Horizontal bar |
| 3-8 | 3+ | Stacked column (100%) |
| Time series | Any | Line |

## Requirements

### PowerPoint
- Python 3.11+
- python-pptx: `pip install python-pptx`

### HTML Dashboard
- Python 3.11+
- No external dependencies (uses Chart.js CDN)

## Example Code

```python
from spss_analyzer.reporting import PowerPointGenerator, HTMLDashboardGenerator

# PowerPoint
ppt_gen = PowerPointGenerator(template="template.pptx")
ppt_gen.create_presentation(
    tables=filtered_tables,
    statistics=statistical_summary,
    title="Q1 2024 Survey Results"
)
ppt_gen.save("report.pptx")

# HTML Dashboard
dash_gen = HTMLDashboardGenerator()
html = dash_gen.generate_dashboard(
    cross_tables=cross_table_data,
    statistics=statistical_summary,
    filter_list=filter_results
)
dash_gen.save("dashboard.html", html)
```

## Related Skills

- `spss-statistics` - Compute statistics for reports
- `spss-filter` - Filter to significant tables first
