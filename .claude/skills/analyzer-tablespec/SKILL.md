---
name: analyzer-tablespec
description: Stage 4: Table Specification - Build table_specification.jsonc from indicators using LLM classification. Combines indicator classification and table building in one step.
working_directory: /home/admin/workspaces/datachat/survey_analyzer
---

# Table Specification

Builds the final `table_specification.jsonc` from indicators using LLM-based classification.

## When to Use

Use this skill after **Stage 3** (Indicator Generation) when:
- `indicators.json` is ready
- Need to create `table_specification.jsonc` for cross-tabulation analysis

## Workflow

```
indicators.json (without is_row/is_column)
    ↓
[LLM Classification - adds is_row/is_column]
    ↓
[Separate into row_indicators/column_indicators]
    ↓
table_specification.jsonc
```

## What It Does

### 1. Classify Indicators (LLM)
Uses GLM-4.7 LLM to classify each indicator:
- **Row indicators**: Research content (purchase intent, usage, satisfaction)
- **Column indicators**: Demographics (gender, age, income, education)
- **Both**: Variables that can serve both roles

### 2. Build Specification
Creates `table_specification.jsonc` with:
- `metadata`: Document metadata and indicator counts
- `filter_clause`: Data filtering rules
- `row_indicators`: All indicators where `is_row=true`
- `column_indicators`: All indicators where `is_column=true`

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| `indicators.json` | Yes | Output from Stage 3 (indicator generation) |

## Outputs

| Output | Description |
|--------|-------------|
| `table_specification.jsonc` | Final table specification ready for Stage 5 |

## Usage

```bash
# Basic usage
python -m survey_analyzer.tablespec.tablespec \
  --indicators-file output/indicators.json \
  --output-file output/table_specification.jsonc

# With project metadata
python -m survey_analyzer.tablespec.tablespec \
  --indicators-file output/indicators.json \
  --output-file output/table_specification.jsonc \
  --project-id proj_survey \
  --dataset-id ds_survey_data
```

## Output Structure

### table_specification.jsonc

```jsonc
{
  "metadata": {
    "spec_id": "tablespec_proj_survey_20260225_123456",
    "project_id": "proj_survey",
    "dataset_id": "ds_survey_data",
    "indicator_counts": {
      "total": 92,
      "row": 85,
      "column": 7
    }
  },
  "filter_clause": {
    "exclude_incomplete": true
  },
  "weight_indicator": null,
  "row_indicators": [
    {
      "indicator_code": "Q10_ENGINE",
      "indicator_label": "Q10 - 排量偏好",
      "is_row": true,
      "is_column": false,
      ...
    }
  ],
  "column_indicators": [
    {
      "indicator_code": "GENDER",
      "indicator_label": "S0 - 性别",
      "is_row": false,
      "is_column": true,
      ...
    }
  ]
}
```

## Classification Criteria

| Type | is_row | is_column | Examples |
|------|--------|-----------|----------|
| Research Content | true | false | Purchase intent, usage, satisfaction |
| Demographic | false | true | Gender, age, income, education |
| Dual Purpose | true | true | Vehicle type, buyer type |

## Environment Variables

Required in `.env`:
```
ZHIPU_API_KEY=your_api_key_here
# or
GLM_API_KEY=your_api_key_here
```

## Related Skills

| Skill | Previous/Next Stage |
|-------|---------------------|
| `analyzer-indicator-generation` | Stage 3 - Generates indicators |
| `analyzer-crosstabs` | Stage 5 - Uses table_specification.jsonc |

## Complete Workflow

```
Stage 1: Data Read & Filter
  → filtered_metadata.json

Stage 2: Question Extraction
  → questions.json

Stage 3: Indicator Generation
  → indicators.json

Stage 4: Table Specification (THIS SKILL)
  → table_specification.jsonc

Stage 5: Cross-Table Generation
  → cross_tables.json

Stage 6: Statistical Filtering
  → filtered_results.json

Stage 7: Reporting
  → presentation.pptx, dashboard.html
```
