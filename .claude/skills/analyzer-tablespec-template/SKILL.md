---
name: analyzer-tablespec-template
description: 'Excel Template Guide - Provides template and guidance for users to optionally provide domain knowledge via Excel file. Use when you want to enhance table specification quality with user input. The template helps users specify which indicators should be row/column, transformations, and analysis priorities.'
license: Apache-2.0
---

# Table Specification Template Guide

> **Optional Enhancement** - Use this template to provide domain knowledge and improve analysis quality

## Overview

The Excel template (`table-specification-template.xlsx`) allows you to provide domain knowledge that enhances the LLM-based table specification. While the system can work entirely through LLM automation, providing your expertise via this template improves results.

## Why Provide the Excel File?

| Benefit | Description |
|---------|-------------|
| **Domain expertise** | You know your research questions better than any AI |
| **Row/column decisions** | Specify which variables are dependent (rows) vs independent (columns) |
| **Transformation rules** | Define recoding, top-2-box, computations based on research goals |
| **Analysis priorities** | Mark which tables are most important for your research |
| **Faster processing** | Reduces LLM API calls and processing time |

## When to Use This Template

**Use this template when:**
- You have specific research hypotheses to test
- You know which variables should be rows vs columns
- You need custom transformations for specific indicators
- You want to ensure certain tables are generated

**Skip this template when:**
- You want fully automated LLM-based specification
- You're exploring the data without specific hypotheses
- Time is limited and automation is preferred

## How to Use

### Step 1: Get the Template

The template is located at:
```
.claude/skills/analyzer-tablespec-template/templates/table-specification-template.xlsx
```

### Step 2: Fill the Template

The template has **4 sheets**:

#### Sheet 1: questionnaire_questions
Define your research questions and their types.

| Column | Description | Example |
|--------|-------------|---------|
| `code` | Unique question identifier | `Q1`, `S0`, `F2X1` |
| `label` | Full question text | "请选择您的性别" |
| `type` | Single Choice, Multiple Choice, Matrix, Rating Scale | Single Choice |

#### Sheet 2: base_variables
Map SPSS variables to questions with metadata.

| Column | Description | Example |
|--------|-------------|---------|
| `name` | SPSS variable name | `Q1_1`, `S0` |
| `question_code` | Links to questionnaire_questions.code | `Q1` |
| `label` | Variable label | "选项1: 非常满意" |
| `suffix` | Transformation type | `_raw`, `_cat`, `_t2b`, `_bin` |
| `values` | Value mapping (JSON) | `{"1": "男", "2": "女"}` |

#### Sheet 3: tabulation_statistics
Define how each question should be tabulated.

| Column | Description | Example |
|--------|-------------|---------|
| `indicator_code` | Unique indicator ID | `Q1_SATISFACTION` |
| `question_code` | Links to questionnaire_questions.code | `Q1` |
| `type` | `categorical` or `scalar` | categorical |
| `metric` | `column_percent` or `descriptive_statistics` | column_percent |
| `explicit` | Whether to always generate this table | true |

#### Sheet 4: row_column_marking (IMPORTANT!)
Specify which indicators are rows vs columns.

| Column | Description | Example |
|--------|-------------|---------|
| `indicator_code` | Links to tabulation_statistics.indicator_code | Q1_SATISFACTION |
| `is_row` | `TRUE` if this is a dependent variable (research content) | TRUE |
| `is_column` | `TRUE` if this is a breakout variable (demographics) | FALSE |

**Rule of thumb:**
- **Row indicators** = Research content (satisfaction, usage, ratings)
- **Column indicators** = Breakout variables (gender, age, region, income)

### Step 3: Use in Analysis

Once filled, use the Excel file in Stage 4 (Table Specification):

```bash
# With Excel template (recommended)
python -m survey_analyzer.tablespec build \
  --indicators-file output/indicators.json \
  --excel-file table-specification.xlsx \
  --output-file output/table_specification.jsonc

# Without Excel (LLM-only)
python -m survey_analyzer.tablespec build \
  --indicators-file output/indicators.json \
  --output-file output/table_specification.jsonc
```

## Template Structure

```
table-specification-template.xlsx
├── questionnaire_questions    # Your research questions
├── base_variables              # SPSS variable mapping
├── tabulation_statistics       # How to tabulate each
└── row_column_marking          # Row vs column (CRITICAL!)
```

## Tips for Quality Input

1. **Be consistent** - Use the same codes across all sheets
2. **Mark row/column clearly** - This is the most valuable information you provide
3. **Specify transformations** - Use suffixes like `_t2b` for top-2-box, `_bin` for binary
4. **Prioritize important tables** - Set `explicit = true` for must-have tables
5. **Use clear labels** - Good labels help understand the output

## What Happens With Your Input?

| Scenario | Behavior |
|----------|----------|
| **Excel provided** | Uses your row/column markings, respects your transformations |
| **Excel not provided** | LLM classifies indicators automatically |
| **Partial Excel** | Uses your input where provided, LLM fills gaps |

## File Locations

| File | Location |
|------|----------|
| Template | `.claude/skills/analyzer-tablespec-template/templates/table-specification-template.xlsx` |
| Reference | `docs/data-related/table-specification.xlsx` |
| Your input | Place in project root or `data/` directory |

## Related Skills

| Skill | Purpose |
|-------|---------|
| `analyzer-data-prep` | Stage 1 - Prepare filtered_metadata.json |
| `analyzer-indicator-generation` | Stage 3 - Generate indicators.json |
| `analyzer-tablespec` | Stage 4 - Build table_specification.jsonc (uses your Excel!) |

## Example Output Comparison

**Without Excel:**
```
LLM tries to guess which indicators are rows vs columns
May miss domain-specific knowledge
Requires more API calls
```

**With Excel:**
```
Your expertise directly informs the analysis
Faster processing (fewer LLM calls)
Results aligned with your research goals
```

## Quality Checklist

Before using your Excel file, verify:

- [ ] All `question_code` values match across sheets
- [ ] Each indicator has `is_row` or `is_column` marked
- [ ] Suffixes (`_cat`, `_t2b`, `_bin`) are consistent
- [ ] Value mappings in `base_variables.values` are valid JSON
- [ ] No duplicate `indicator_code` values
- [ ] At least 1 column indicator (demographics) marked
