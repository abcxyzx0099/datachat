---
name: analyzer-tablespec-gen
description: 'Stage 2: AI Table Specification - Generates analysis table and indicator specifications using Claude AI. Use when metadata is ready and analysis plan is needed. Reads filtered_metadata.json and table-specification.xlsx, generates table_specification.jsonc for cross-tabulation analysis.'
license: Apache-2.0
---

# Analyzer Table Specification (Stage 2)

Generates table and indicator specifications for survey cross-tabulation analysis using AI.

## Overview

Executes **Steps 4-6** of the workflow:
- Step 4: Analyze metadata and generate table specification (AI-orchestrated)
- Step 5: Validate specification structure and references
- Step 6: Review and approve specification

## When to Use

Use this skill when:
- Stage 1 data preparation is complete (`filtered_metadata.json` exists)
- Need to define cross-tabulation tables (row × column indicators)
- Need to specify transformation rules (recoding, computing)
- Creating analysis plan for survey data

## Inputs

| Input | Required | Description |
|--------|-----------|-------------|
| `filtered_metadata.json` | Yes | SPSS metadata from Stage 1 (variable labels, value labels) |
| `table-specification.xlsx` | Yes | User-edited Excel with indicator selections |

## Output

| File | Content |
|-------|----------|
| `table_specification.jsonc` | Complete table specification with row/column indicators |

## Specification Structure

The generated `table_specification.jsonc` contains:

```jsonc
{
  "metadata": {
    "spec_id": "crosstab_2024_consumer_survey_001",
    "project_id": "proj_2024_china_consumer_insights",
    "dataset_id": "ds_q1_2024_national_survey",
    "description": "Cross-tabulation analysis for market research survey"
  },
  "filter_clause": {
    "age_min": 18,
    "age_max": 65,
    "exclude_incomplete": true
  },
  "weight_indicator": "weight1",
  "row_indicators": [
    {
      "indicator_code": "Q1_GENDER_RAW",
      "question_code": "Q1",
      "question_description": "Gender",
      "question_label": "请问您的性别是？(单选)",
      "question_type": "Single Choice",
      "source_variables": ["Q1_GENDER"],
      "transformation_rules": null,
      "statistic_type": "categorical"
    }
  ],
  "column_indicators": [
    {
      "indicator_code": "AGE_GROUP",
      "question_code": "S1",
      "question_description": "Age group",
      "question_label": "年龄分组",
      "question_type": "Single Choice",
      "source_variables": ["AGE_GROUP"],
      "explicit": ["1", "2", "3", "4", "5"],
      "transformation_rules": null,
      "statistic_type": "categorical"
    }
  ]
}
```

See [examples/table_specification.jsonc](examples/table_specification.jsonc) for complete reference.

## Field Descriptions

| Field | Description | Source |
|-------|-------------|--------|
| `spec_id`, `project_id`, `dataset_id` | Project identification | Excel Metadata sheet |
| `filter_clause` | Data filtering rules | Excel Metadata sheet |
| `weight_indicator` | Weight variable name | Excel Weight Indicator sheet |
| `indicator_code` | Internal variable identifier | Generated |
| `question_code` | SPSS variable prefix (Q1, S1, D1) | Excel Question Code column |
| `question_description` | Concise English label | Excel Question Description column |
| `question_label` | Full Chinese question text | filtered_metadata.json |
| `question_type` | Single Choice, Multiple Choice, Matrix, etc. | Excel Question Type dropdown |
| `source_variables` | Real SPSS variable names | Mapped from question_code + metadata |
| `transformation_rules` | SPSS-compatible recoding syntax | Excel Transformation Rules column |
| `statistic_type` | categorical or scalar | **CRITICAL: Determined by rules below** |

## Statistic Type Determination Rules

**CRITICAL**: The `statistic_type` field determines how Stage 3 processes the indicator. Use these rules:

### Rule 1: Check transformation_rules First

| Transformation Rule | statistic_type | Reason |
|---------------------|----------------|--------|
| Contains `COMPUTE` | **`scalar`** | Computed values are numeric/scalar |
| Null or recoding rules `(x=y)` | Determined by question_type | See Rule 2 |

### Rule 2: Determine by question_type (when no COMPUTE)

| question_type | source_variables count | statistic_type | Stage 3 Scenario |
|---------------|------------------------|----------------|------------------|
| **Single Choice** | 1 | `categorical` | cat_single (column %) |
| **Multiple Choice** | > 1 (binary variables) | `categorical` | cat_multi (% of Yes) |
| **Matrix** | 1 | `categorical` | cat_single (column %) |
| **Numeric Input** | 1 | `scalar` | scalar_single (mean, etc.) |
| **Rating Scale** | 1 | `categorical` | cat_single (column %) |
| **Rating Scale** | > 1 (attributes) | `scalar` | scalar_multi (mean per attribute) |

### Rule 3: Special Cases

| Scenario | statistic_type | Explanation |
|----------|----------------|-------------|
| Multiple source vars with COMPUTE | `scalar` | Computed index = single scalar value |
| Multiple binary vars (no COMPUTE) | `categorical` | True multiple choice (% of Yes) |
| Rating scale with means needed | `scalar` | Each attribute gets mean statistics |
| Rating scale with column % needed | `categorical` | Show column percentages instead |

### Examples

```jsonc
// Example 1: Single categorical variable
{
  "indicator_code": "Q1_GENDER",
  "question_type": "Single Choice",
  "source_variables": ["Q1_GENDER"],
  "transformation_rules": null,
  "statistic_type": "categorical"  // → Stage 3: cat_single (column %)
}

// Example 2: Multiple choice (binary variables)
{
  "indicator_code": "S1_BRAND_AWARENESS",
  "question_type": "Multiple Choice",
  "source_variables": ["S1_BRAND_A", "S1_BRAND_B", "S1_BRAND_C"],
  "transformation_rules": null,
  "statistic_type": "categorical"  // → Stage 3: cat_multi (% of Yes)
}

// Example 3: Single numeric variable
{
  "indicator_code": "S1_AGE",
  "question_type": "Numeric Input",
  "source_variables": ["S1_AGE"],
  "transformation_rules": null,
  "statistic_type": "scalar"  // → Stage 3: scalar_single (mean, median, etc.)
}

// Example 4: Computed index (IMPORTANT: scalar, not categorical!)
{
  "indicator_code": "INCOME_INDEX",
  "question_type": "Numeric Input",
  "source_variables": ["SALARY_MONTHLY", "BONUS_MONTHLY", "OTHER_INCOME"],
  "transformation_rules": "COMPUTE INCOME_INDEX = SALARY_MONTHLY + BONUS_MONTHLY + OTHER_INCOME",
  "statistic_type": "scalar"  // → Stage 3: scalar_multi (computed value)
}

// Example 5: Rating scale (multiple attributes)
{
  "indicator_code": "D1_ATTRIBUTE_RATINGS",
  "question_type": "Rating Scale",
  "source_variables": ["D1_QUALITY", "D1_PRICE", "D1_SERVICE", "D1_SELECTION", "D1_VALUE"],
  "transformation_rules": null,
  "statistic_type": "scalar"  // → Stage 3: scalar_multi (mean per attribute)
}
```

## Transformation Rules Format

The `transformation_rules` field uses **SPSS-compatible syntax** (parsed by Python):

| Format | Example | Description |
|--------|---------|-------------|
| Single value | `(3=2)` | Recode value 3 to 2 |
| Range | `(1 THRU 3=99)` | Recode values 1-3 to 99 |
| Compute | `COMPUTE var = a + b` | Calculate new variable |
| Null | `null` | No transformation |

**Example:**
```jsonc
"transformation_rules": "(1 THRU 2=1) (3=2) (4 THRU 5=3)"
```

Applied by `TransformationEngine` using pandas:
```python
# Parsed and applied as: series.map({1: 1, 2: 1, 3: 2, 4: 3, 5: 3})
```

## Library Modules

| Module | Purpose |
|---------|---------|
| `survey_analyzer.specification.schema` | JSON schema validation |
| `survey_analyzer.specification.validator` | Specification validation |
| `survey_analyzer.analysis.transformation.TransformationEngine` | Apply transformation rules |
| `survey_analyzer.analysis.crosstab.CrossTabGenerator` | Generate cross-tables |

## Validation Steps

1. **Structure validation**: JSON schema check
2. **Reference validation**: Variables exist in metadata
3. **Business logic validation**: Transformation rules are valid
4. **User review**: Semantic quality check

## Next Stage

After Stage 2 completes, proceed to **Stage 3: Cross-Table Calculation** (`stage3-crosstabs`)
