---
name: stage5-reports
description: 'Stage 7: Reporting - Generate PowerPoint presentation and interactive HTML dashboard from filtered results. Output: presentation.pptx, dashboard.html. Use when analysis is complete and reports are needed.'
license: Apache-2.0
---

# Stage 7: Reporting

Generate final deliverables: PowerPoint presentation and HTML dashboard.

## Overview

Executes **Steps 12-13** of the workflow:
- Step 12: Generate PowerPoint
- Step 13: Generate HTML dashboard

## When to Use

Use this skill when:
- Statistical analysis is complete (Stage 6)
- Need client-ready reports
- Sharing results with stakeholders

## Usage

```
User: Generate final reports

Assistant: [Step 12] Creating PowerPoint presentation...
           24 slides generated
           - Title slide, summary, key findings
           - 18 significant tables with charts
           Created: presentation.pptx

           [Step 13] Creating HTML dashboard...
           - 18 interactive tables
           - Search, filter, export features
           Created: dashboard.html

Stage 5 complete! Reports ready for delivery.
```

## Input

| Input | Required | Description |
|--------|-----------|-------------|
| `filtered_tables.json` | Yes | Significant tables from Stage 4 |
| `statistical_summary.json` | Yes | Test results |
| `table_specification.json` | No | For styling preferences |

## Output

| File | Content |
|-------|----------|
| `presentation.pptx` | Executive summary slides |
| `dashboard.html` | Interactive visualization |

## PowerPoint Features

- Title slide with study overview
- Key findings summary
- Significant tables with embedded charts
- Statistical highlights
- Methodology notes
- Branded styling

## HTML Dashboard Features

- Browse all filtered tables
- Search by keyword
- Filter by significance/variable
- Export to Excel/PDF
- Statistical test results
- Responsive design (mobile-friendly)

## Library Modules

| Module | Purpose |
|---------|---------|
| `survey_analyzer.reporting.PowerPointGenerator` | Create .pptx files |
| `survey_analyzer.reporting.HTMLDashboardGenerator` | Create .html files |

## Dependencies

- `python-pptx` - PowerPoint generation
- `jinja2` - HTML templating
- `plotly` - Interactive charts

## Viewing Outputs

| Output | How to View |
|----------|---------------|
| `presentation.pptx` | PowerPoint, Keynote, Google Slides |
| `dashboard.html` | Any web browser (static file) |
