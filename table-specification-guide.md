# Table Specification Usage Guide

## Overview

This guide explains how to use the JSONC specification files to generate PSPP CTABLES syntax for cross-tabulation analysis.

## Files

| File | Purpose |
|------|----------|
| `table-specification.jsonc` | Defines specific crosstab analysis (indicators, dimensions, filters) - JSONC format with comments |
| `table-settings.jsonc` | Shared templates for formatting (categorical, scalar, display, charts) - JSONC format with comments |

## Table Specification Structure

### Core Fields

| Field | Type | Description |
|-------|------|-------------|
| `spec_id` | string | Unique specification identifier |
| `project_id` | string | Project reference |
| `dataset_id` | string | Dataset reference |
| `description` | string | Human-readable description |
| `filter_clause` | object | Data filtering rules (age_min, age_max, exclude_incomplete) |
| `row_indicators` | array | Row dimension indicators |
| `column_indicators` | array | Column dimension indicators |
| `weight_indicator` | string | Weighting variable name |

### Indicator Fields

| Field | Type | Description |
|-------|------|-------------|
| `indicator_code` | string | SPSS variable name |
| `indicator_label` | string | Question text |
| `question_type` | enum | Single, MultiSelect, Frequency, Rating, Matrix, Ranking, Numeric |
| `explicit` | array or null | Specific values to include (null = all values) |
| `variable_format` | enum | Data type: numeric, string, date |
| `transformation_rules` | array | Recoding rules for subtotals |
| `validation` | object | Min/max constraints |
| `settings_template` | string | Template reference: categorical or scalar |

## Table Settings Structure

### Templates

| Template | Purpose |
|----------|----------|
| `categorical` | For Single, MultiSelect, Frequency, Rating, Matrix, Ranking questions |
| `scalar` | For Numeric questions (mean, median, stddev, etc.) |

### Categorical Template Fields

| Section | Fields |
|---------|--------|
| categories | order, sort_key, include_missing, totals, empty |
| percentages | show_row_pct, show_col_pct, show_table_pct |
| display | variable_label, category_label_position, hide_empty_categories |
| statistics | count, mean, median, mode, stddev, variance, min, max, sum, range, semean, missing, ptile |
| missing_values | exclude, include, mean_substitute |

### Scalar Template Fields

| Section | Fields |
|---------|--------|
| categories | order, sort_key, include_missing, totals, empty |
| percentages | show_row_pct, show_col_pct, show_table_pct |
| display | variable_label, category_label_position, hide_empty_categories |
| statistics | count, mean, median, mode, stddev, variance, min, max, sum, range, semean, missing, ptile |
| missing_values | exclude, include, mean_substitute |

### Default Settings

| Section | Fields |
|---------|--------|
| default_display_options | table_format, empty_display, missing_display, variable_labels, hide_empty_rows, hide_empty_columns, sort_by |
| default_chart_config | chart_type, color_scheme, show_labels, show_legend, title_template |

## PSPP CTABLES Syntax Generation

### Template Mappings

The `settings_template` field in each indicator maps to PSPP statistics:

| Template | Statistics in Brackets |
|----------|----------------------|
| `categorical` | `[COUNT COLPCT]` |
| `scalar` | `[MEAN MEDIAN STDDEV MIN MAX]` |

### Column Variables

All column variables are **always categorical** (no statistics in brackets).

### Row Variables

- **Categorical row** → `[COUNT COLPCT]`
- **Scalar row** → `[MEAN MEDIAN STDDEV MIN MAX]`

## Example CTABLES Generation

Given `table-specification.json`:

```json
{
  "row_indicators": [
    {"indicator_code": "Q1_GENDER", "settings_template": "categorical"},
    {"indicator_code": "S1_AGE", "settings_template": "scalar"}
  ],
  "column_indicators": [
    {"indicator_code": "S3_LICENSE", "settings_template": "categorical"}
  ],
  "weight_indicator": "weight1"
}
```

### Generated PSPP Syntax

```spss
GET FILE='/path/to/data.sav'

CTABLES
  /TABLE=Q1_GENDER [COUNT COLPCT] BY S3_LICENSE
  /TABLE=S1_AGE [MEAN MEDIAN STDDEV MIN MAX] BY S3_LICENSE
  /VLABELS VARIABLES=ALL DISPLAY=LABEL
  /CATEGORIES ORDER=A TOTAL=YES LABEL='总计'
  /WEIGHT BY weight1.
```

### Syntax Breakdown

| Component | Source | Generated Syntax |
|-----------|-------|-----------------|
| Row variable (categorical) | row_indicators with settings_template=categorical | `variable [COUNT COLPCT]` |
| Row variable (scalar) | row_indicators with settings_template=scalar | `variable [MEAN MEDIAN STDDEV MIN MAX]` |
| Column variable | column_indicators (always categorical) | `variable` (no statistics) |
| Weight | weight_indicator | `/WEIGHT BY variable_name` |
| Variable labels | default_display_options.variable_label | `/VLABELS VARIABLES=ALL DISPLAY=...` |
| Category order | categories.order | `/CATEGORIES ORDER=A` (A=asc, D=desc) |
| Totals | categories.totals | `/CATEGORIES ... TOTAL=YES LABEL='...'` |
| Missing values | missing_values | Handled by PSPP automatically |

## Question Type Mapping

| Question Type | Template | Statistics |
|---------------|----------|------------|
| Single | categorical | COUNT COLPCT |
| MultiSelect | categorical | COUNT COLPCT |
| Frequency | categorical | COUNT COLPCT |
| Rating | categorical | COUNT COLPCT |
| Matrix | categorical | COUNT COLPCT |
| Ranking | categorical | COUNT COLPCT |
| Numeric | scalar | MEAN MEDIAN STDDEV MIN MAX |

## Transformation Rules

Transformation rules in `transformation_rules` allow recoding values before display:

```json
{
  "transformation_rules": [
    {
      "source_values": ["1", "2", "3"],
      "target_value": "99",
      "target_label": "其他",
      "hide_categories": true
    }
  ]
}
```

**Effect**: Collapse source values into target value for display.

## Explicit Values

The `explicit` field limits which categories to include:

- `null` = Include all categories
- `["1", "2"]` = Only include categories 1 and 2

## Filter Clause

Apply data filters before generating crosstabs:

```json
{
  "filter_clause": {
    "age_min": 18,
    "age_max": 65,
    "exclude_incomplete": true
  }
}
```

Use SELECT IF or permanent filter in SPSS data before CTABLES.

## Usage Workflow

1. Load SPSS data file
2. Read `table-specification.json` for analysis definition
3. Read `table-settings.json` for formatting templates
4. Generate CTABLES syntax based on templates
5. Execute PSPP to produce crosstab output
