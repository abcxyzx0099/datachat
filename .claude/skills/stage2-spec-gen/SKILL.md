---
name: stage2-spec-gen
description: 'Stage 2: AI Table Specification - Generates analysis table and indicator specifications using Claude AI. Use when metadata is ready and analysis plan is needed.'
license: Apache-2.0
---

# Stage 2: Table Specification

Generates table and indicator specifications using AI analysis.

## Overview

Executes **Steps 4-6** of the workflow:
- Step 4: Analyze metadata
- Step 5: Generate table specifications
- Step 6: Generate indicator specifications

## When to Use

Use this skill when:
- Stage 1 data preparation is complete
- Need to define analysis tables
- Need to specify indicators for calculation
- Creating analysis plan for survey data

## Usage

```
User: Generate table specifications for our survey

Assistant: [Step 4] Analyzing survey metadata...
           Found: 45 analysis variables
           Variable types: 25 categorical, 15 ordinal, 5 scale

           [Step 5] Generating table specifications...
           Created 18 cross-table specifications:
           - Gender × Age
           - Gender × Satisfaction
           - Satisfaction × Brand Rating
           ... (15 more)

           [Step 6] Generating indicator specifications...
           Created 6 indicator definitions:
           - Overall Satisfaction (mean)
           - Top 2 Box Score (percentage)
           - NPS Score (categorical)
           ... (3 more)

           Saved: table_specification.json
           Stage 2 complete!
```

## Input

| Input | Required | Description |
|--------|-----------|-------------|
| `--metadata-file` | Yes | Path to filtered_metadata.json from Stage 1 |

## Output

| File | Content |
|-------|----------|
| `table_specification.json` | Complete table and indicator specifications |

## Specification Structure

The generated `table_specification.json` contains:

```json
{
  "version": "1.0",
  "tables": [
    {
      "id": "table_001",
      "name": "Gender by Age Group",
      "rows": {"variable": "dem_gender"},
      "columns": {"variable": "dem_age"},
      "metrics": ["count", "row_percent", "col_percent"]
    }
  ],
  "indicators": [
    {
      "id": "sat_overall",
      "name": "Overall Satisfaction",
      "variables": ["q1_satisfaction"],
      "aggregation": "mean"
    }
  ],
  "global_recodings": [],
  "output_settings": {
    "significance_threshold": 0.05
  }
}
```

## Table Types Generated

| Type | Description | Example |
|-------|-------------|----------|
| **Demographic crosstabs** | Breakdown by demographic variables | Gender × Age, Region × Income |
| **Satisfaction tables** | Key satisfaction metrics | Overall × Brand, Question × Category |
| **Indicator tables** | Summary statistics | Mean scores, top box percentages |
| **NPS tables** | Net Promoter Score analysis | Promoters × Detractors × Passives |

## Indicator Types

| Type | Aggregation | Description |
|-------|-------------|-------------|
| **Mean** | mean | Average of scale values |
| **Sum** | sum | Total count or value |
| **Count** | count | Number of responses |
| **Median** | median | Middle value |
| **Percentage** | custom | % meeting criteria (e.g., Top 2 Box) |

## Library Modules

| Module | Purpose |
|---------|---------|
| `survey_analyzer.specification.SpecificationGenerator` | Generate table/indicator specs |
| `survey_analyzer.io.MetadataTransformer` | Transform and filter metadata |

## AI Analysis

This skill uses Anthropic Claude AI to:
- Analyze variable types and relationships
- Select appropriate table combinations
- Define statistically valid indicators
- Apply domain knowledge for survey analysis

## Next Stage

After Stage 2 completes, proceed to **Stage 3: Cross-Table Calculation** (`stage3-crosstabs`)
