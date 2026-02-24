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

## Workflow

This skill follows a **two-mode workflow**:

```
┌─────────────────────────────────────────────────────────────────┐
│                    CHECK REQUIRED FILES                         │
├─────────────────────────────────────────────────────────────────┤
│  Check output/ directory for:                                    │
│  • filtered_metadata.json (REQUIRED)                            │
│  • table-specification.xlsx (OPTIONAL)                           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
        ┌─────────────────────────────────────────┐
        │ filtered_metadata.json FOUND?           │
        └─────────────────────────────────────────┘
           │ YES                      │ NO
           ↓                          ↓
    Continue              ❌ STOP: "Run Stage 1 first"
                              ↓
        ┌─────────────────────────────────────────┐
        │ BACKUP existing specification?          │
├─────────────────────────────────────────────────────────────────┤
│  If table_specification.jsonc exists:                               │
│  • Create backup: table_specification_YYYYMMDD_HHMMSS.jsonc       │
│  • Preserves history of all specification versions                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
        ┌─────────────────────────────────────────┐
        │ table-specification.xlsx FOUND?         │
        └─────────────────────────────────────────┘
           │ YES                      │ NO
           ↓                          ↓
    ┌──────────────┐         ┌──────────────────┐
    │ EVALUATE     │         │ AUTOMATIC MODE    │
    │ Excel File   │         │ (no user input)   │
    └──────────────┘         └──────────────────┘
           │                          │
           ↓                          ↓
    ┌──────────────┐         Generate spec from
    │ Valid?       │         metadata only
    └──────────────┘         + REMINDER user
           │                          │
    ┌──────┴──────┐                  │
    │ YES    │ NO                    │
    ↓       ↓                       ↓
  Use    INTERACTIVE         Present result +
  Excel  Ask for fixes      Reminder together
```

## Inputs

| Input | Required | Description |
|--------|-----------|-------------|
| `filtered_metadata.json` | **YES** | SPSS metadata from Stage 1 (variable labels, value labels). **STOP if missing.** |
| `table-specification.xlsx` | No | Optional: User-edited Excel with indicator selections. Template: `.claude/skills/analyzer-tablespec-gen/templates/table-specification-template.xlsx` |

## IMPORTANT: How This Skill Works

**⚠️ NEVER CREATE PYTHON SCRIPTS** - This skill uses AI intelligence to directly analyze and create the specification file.

| DO ✅ | DON'T ❌ |
|--------|----------|
| Read `filtered_metadata.json` directly | Create `temp/*.py` scripts |
| Analyze metadata with AI intelligence | Write helper scripts |
| Use `Write` tool to create `table_specification.jsonc` | Use `Bash` with Python for generation |
| Extract labels intelligently from metadata | Process data with fixed code |

**How to generate the specification:**
1. **BACKUP** (if exists): If `output/table_specification.jsonc` exists, create timestamped backup
2. Read `filtered_metadata.json` using the `Read` tool
3. Analyze variable patterns, labels, and values using AI intelligence
4. Extract proper question labels (see Label Extraction Guidelines below)
5. Use the `Write` tool to directly create `output/table_specification.jsonc`

## Why Pure AI Approach (No Scripts)

### The Philosophy

This skill uses **pure AI intelligence** instead of programming/scripts for important reasons:

| Benefit | Why It Matters |
|---------|----------------|
| **Semantic Understanding** | AI reads the actual question text (e.g., "请问您的性别？") and understands it's a demographic question. Scripts only see patterns like "S0" and may fail with different naming. |
| **Works With Any Survey** | No hardcoded patterns. Whether variables are named Q1, QUESTION_1, var_001, or 使用场景, AI analyzes content, not names. |
| **Intelligent Grouping** | AI recognizes that Q2A_1 through Q2A_12 share the same question stem ("请问您要购买的新车通常将如何使用？") and groups them appropriately. |
| **No Technical Debt** | Scripts in `temp/` create throwaway code that clutters the project. AI reasoning leaves no artifacts. |
| **Explainable Decisions** | AI can articulate why it made each choice. Scripts are black boxes. |
| **Adapts to Feedback** | If user says "that's wrong," AI adjusts immediately. Scripts need to be rewritten. |

### The Trap to Avoid

**When processing 300+ variables, AI is tempted to:**
- Write a Python script "just this once"
- Use Bash for "reliable" processing
- Create "helper" functions

**Don't do it.** The script will:
- ❌ Use brittle patterns (`if var.startswith('Q')`)
- ❌ Fail with edge cases (Q99, Q_oth, "Other" fields)
- ❌ Create technical debt (temp/ scripts to maintain)
- ❌ Not understand semantic meaning

### The Right Approach

**Use your intelligence:**
1. Read the metadata with the `Read` tool
2. Analyze variable content (labels, values, patterns)
3. Make decisions based on meaning, not naming
4. Write the output directly with the `Write` tool

**Remember**: This skill works with ANY SPSS survey, not just ones following specific naming conventions. That flexibility comes from AI intelligence, not code.

## Backup Step

**⚠️ IMPORTANT: Always backup existing specification before overwriting**

When `output/table_specification.jsonc` already exists:

1. **Create backup** with timestamp: `table_specification_YYYYMMDD_HHMMSS.jsonc`
2. **Location**: Same directory as the original (`output/`)
3. **Purpose**: Preserve history - never lose previous work

**Backup command:**
```bash
# Use Bash tool to create backup
cp output/table_specification.jsonc output/table_specification_$(date +%Y%m%d_%H%M%S).jsonc
```

**Backup file format:**
- `table_specification_20260220_143052.jsonc`
- `table_specification_20260221_091234.jsonc`
- etc.

## Operation Modes

### Mode 1: Automatic (Default)

| Condition | Behavior |
|-----------|----------|
| Excel file NOT provided | Generate specification from metadata automatically |
| Excel file provided AND valid | Use Excel selections |
| Output | Result + Reminder (no stopping) |

**Reminder shown:**
> ℹ️ **Tip**: Providing `table-specification.xlsx` with your variable selections produces more accurate and robust results. Template available at: `.claude/skills/analyzer-tablespec-gen/templates/table-specification-template.xlsx`

### Mode 2: Interactive

| Condition | Behavior |
|-----------|----------|
| Excel file provided BUT has issues | Evaluate and ask user for corrections |
| User response | Wait for user input before proceeding |
| Output | Iterative feedback + Final result |

**Evaluation criteria for Excel:**
- **Structure**: Required sheets present (Metadata, Row Indicators, Column Indicators)
- **Content**: Question codes exist in `filtered_metadata.json`
- **Validity**: Value ranges, transformation rules are valid
- **Completeness**: Required fields are filled

## Output

| File | Content |
|-------|----------|
| `table_specification.jsonc` | Complete table specification with row/column indicators |

## Specification Structure

The generated `table_specification.jsonc` uses a **simplified structure**.

### Minimal Example

```jsonc
{
  "metadata": {
    "spec_id": "example_spec_001",
    "project_id": "proj_example",
    "dataset_id": "ds_example",
    "description": "Example table specification"
  },
  "filter_clause": {"exclude_incomplete": true},
  "weight_indicator": null,
  "row_indicators": [
    {
      "indicator_code": "Q1_GENDER",
      "indicator_label": "Gender",
      "question_code": "Q1",
      "question_type": "Single Choice",
      "tabulation_type": "categorical",
      "tabulation_metric": "column_percent",
      "base_variables": {"Q1_cat": "Gender"},
      "base_variables_transformations": null,
      "base_variables_value_labels": {"1": "Male", "2": "Female"}
    }
  ],
  "column_indicators": [
    {
      "indicator_code": "AGE_GROUP",
      "indicator_label": "Age group",
      "question_code": "S1",
      "question_type": "Single Choice",
      "tabulation_type": "categorical",
      "tabulation_metric": "column_percent",
      "base_variables": {"S1_cat": "Age group"},
      "base_variables_transformations": null,
      "base_variables_value_labels": {"1": "18-25", "2": "26-35", "3": "36-45"}
    }
  ]
}
```

### Complete Examples

**For comprehensive examples covering all indicator types, see:**

- [examples/table_specification.jsonc](examples/table_specification.jsonc) - Complete reference with 7 row indicator types and 11 demographic columns
- [output/table_specification.jsonc](output/table_specification.jsonc) - Latest generated specification

**Key fields at the indicator level:**

| Field | Description |
|-------|-------------|
| `indicator_code` | Unique identifier for this indicator |
| `indicator_label` | Human-readable description (Chinese question text) |
| `question_code` | Question identifier (e.g., "Q1", "S1") |
| `question_type` | Single Choice, Multiple Choice, Rating Scale, etc. |
| `base_variables` | Dictionary of variable names to labels |
| `base_variables_transformations` | SPSS transformation syntax or `null` |
| `base_variables_value_labels` | Value labels mapping for all variables |
| `tabulation_type` | `categorical` or `scalar` |
| `tabulation_metric` | `column_percent` or `descriptive_statistics` |

## Field Descriptions

### Top-Level Structure

| Field | Type | Description |
|-------|------|-------------|
| `metadata` | Object | Project identification metadata (nested) |
| `filter_clause` | Object | Data filtering rules |
| `weight_indicator` | String/null | Weight variable name or `null` |
| `row_indicators` | Array | List of row indicator objects |
| `column_indicators` | Array | List of column indicator objects |

### metadata (Object)

| Field | Type | Description |
|-------|------|-------------|
| `spec_id` | String | Unique specification identifier |
| `project_id` | String | Project identifier |
| `dataset_id` | String | Dataset identifier |
| `description` | String | Human-readable description |
| `generated_at` | String | ISO timestamp of generation |
| `source_file` | String | Original SPSS filename |
| `case_count` | Number | Number of cases in dataset |

### Indicator Object (Element in row_indicators/column_indicators arrays)

| Field | Type | Description |
|-------|------|-------------|
| `indicator_code` | String | Unique identifier for the indicator |
| `indicator_label` | String | Human-readable label (Chinese question text) |
| `question_code` | String | Question identifier (e.g., "Q1", "S1") |
| `question_type` | String | Question type: Single Choice, Multiple Choice, Matrix, Rating Scale, Numeric Input, etc. |
| `tabulation_type` | String | `categorical` or `scalar` |
| `tabulation_metric` | String | `column_percent` or `descriptive_statistics` |
| `base_variables` | Object | Dictionary of variable names to labels |
| `base_variables_transformations` | String/null | SPSS transformation syntax or `null` |
| `base_variables_value_labels` | Object | Value labels mapping for all variables |

### base_variables (Dictionary)

Dictionary of variable names to labels:

| Field | Type | Description |
|-------|------|-------------|
| Key | String | Variable name (with suffix, e.g., "Q2A_1_bin") |
| Value | String | Human-readable variable label |

Example:
```jsonc
"base_variables": {
  "Q2A_1_bin": "上/下班用",
  "Q2A_2_bin": "和家庭成员/朋友/同事一起出外娱乐聚餐",
  "Q2A_3_bin": "去购物"
}
```

### base_variables_transformations

SPSS transformation syntax or `null`:

| Value | Description |
|-------|-------------|
| `null` | No transformation (raw variables) |
| String | SPSS transformation rules |

### base_variables_value_labels (Object)

Value labels mapping shared across all base variables:

| Field | Type | Description |
|-------|------|-------------|
| Key | String | Numeric value as string |
| Value | String | Human-readable value label |

Example:
```jsonc
"base_variables_value_labels": {
  "1": "是",
  "0": "否"
}
```

## Tabulation Type Determination Rules

**CRITICAL**: The `tabulation_type` field determines how Stage 3 processes the indicator.

### Rule 1: Determine by question_type

| question_type | base_variables count | tabulation_type | Stage 3 Scenario |
|---------------|---------------------|------------------|------------------|
| **Single Choice** | 1 | `categorical` | cat_single (column %) |
| **Multiple Choice** | > 1 (binary variables) | `categorical` | cat_multi (% of Yes) |
| **Matrix** | 1 | `categorical` | cat_single (column %) |
| **Numeric Input** | 1 | `scalar` | scalar_single (mean, etc.) |
| **Rating Scale** | 1 | `categorical` | cat_single (column %) |
| **Rating Scale** | > 1 (attributes) | `scalar` | scalar_multi (mean per attribute) |

### Rule 2: Tabulation Type Metric Mapping

| tabulation_type | tabulation_metric | Description |
|------------------|-------------------|-------------|
| `categorical` | `column_percent` | Column percentage for each category |
| `scalar` | `descriptive_statistics` | Mean, median, std_dev, min, max |

## base_variables_transformations Format

The `base_variables_transformations` field uses **SPSS-compatible syntax**:

| Scenario | base_variables_transformations Value | Example |
|----------|--------------------------------------|---------|
| Raw variable (no transformation) | `null` | Raw SPSS variable used directly |
| Recode | `RECODE source (old=new) INTO target` | `"RECODE Q5_SAT (1 THRU 2=1) (3=2) INTO Q5_SAT_cat"` |
| Compute | `COMPUTE target = expression` | `"COMPUTE INCOME_INDEX = SALARY + BONUS + OTHER"` |
| Validate | `SELECT IF condition` | `"SELECT IF NOT MISSING(var) AND var GT 0"` |

**Note**: The transformation rule is self-documenting - it shows source, operation, and target variable.

### Complete Examples

**For comprehensive examples covering all indicator types, see:**

| File | Description |
|------|-------------|
| [examples/table_specification.jsonc](examples/table_specification.jsonc) | Complete reference with 7 row indicator types and 11 demographic columns |
| [output/table_specification.jsonc](output/table_specification.jsonc) | Latest generated specification from actual data |

**Indicator types covered in examples:**
- Single Choice (e.g., Gender, Age, City Tier)
- Multiple Choice (e.g., Usage scenarios with _bin variables)
- Rating Scale - Single Variable (e.g., Satisfaction factor)
- Rating Scale - Multiple Attributes (e.g., Satisfaction dimensions)
- Frequency Scale (e.g., Usage frequency)
- Multi-Item Scale (e.g., Attribute importance ratings)
- Budget/Purchase Range (e.g., Purchase budget)

## Suffix Field

The suffix is derived from the variable name in `base_variables` and indicates the transformation type. Variable names are self-documenting by including their suffix.

### Suffix Options

| Suffix | Type | Meaning | Example Variable |
|--------|------|---------|-----------------|
| `_raw` | categorical/scalar | Raw SPSS variable, no transformation | `Q1_GENDER_raw` |
| `_bin` | categorical | Binary (0/1, Yes/No) | `Q1_AWARE_bin` |
| `_cat` | categorical | Recoded into categories | `Q5_SAT_cat` |
| `_t2b` | categorical | Top 2 Box (highest categories combined) | `Q5_SAT_t2b` |
| `_b2b` | categorical | Bottom 2 Box (lowest categories combined) | `Q5_SAT_b2b` |
| `_nps` | categorical | NPS categorization (Promoter/Passive/Detractor) | `Q_REC_nps` |
| `_sca` | scalar | Numeric/continuous | `S1_AGE_sca` |
| `_idx` | scalar | Computed index from multiple variables | `SATISFACTION_idx` |
| `_z` | scalar | Z-score normalized | `D1_SCORE_z` |
| `_pct` | scalar | Percentile rank | `D1_SCORE_pct` |

### Suffix Mapping Examples

| Scenario | Suffix | Example Variable Name |
|----------|--------|----------------------|
| Raw gender variable | `_raw` | `Q1_GENDER_raw` |
| Binary awareness variable | `_bin` | `Q1_AWARE_bin` |
| Recoded satisfaction | `_cat` | `Q5_SAT_cat` |
| Top 2 Box satisfaction | `_t2b` | `Q5_SAT_t2b` |
| Satisfaction index | `_idx` | `SATISFACTION_idx` |
| Z-scored rating | `_z` | `D1_QUALITY_z` |

### Transformation Rules by Suffix

The suffix in variable names indicates the transformation type. For `base_variables_transformations`:

| Suffix | Typical `base_variables_transformations` Value |
|--------|------------------------------|
| `_cat` | `null` (most common - raw category) or `"RECODE Q5_SAT (1 THRU 2=1) (3=2) (4 THRU 5=3)"` |
| `_bin` | `null` (binary variables are typically raw) |
| `_sca` | `null` (numeric variable - no transformation) |

**Note**: In the simplified structure, `base_variables_transformations` applies to all variables in the indicator. For most cases, use `null` (raw variables).

**Note**: Source variables in transformations do NOT have `_raw` suffix. Use base name like `Q5_SAT`, not `Q5_SAT_raw`.

## Library Modules

| Module | Purpose |
|---------|---------|
| `survey_analyzer.specification.schema` | JSON schema validation |
| `survey_analyzer.specification.validator` | Specification validation |
| `survey_analyzer.analysis.transformation.TransformationEngine` | Apply transformation rules |
| `survey_analyzer.analysis.crosstab.CrossTabGenerator` | Generate cross-tables |

## Validation Steps

### When Excel File is Provided

1. **Excel Structure Validation**:
   - Check required sheets exist (Metadata, Row Indicators, Column Indicators)
   - Verify column headers match expected format
   - Validate data types in each column

2. **Reference Validation**:
   - Question codes in Excel exist in `filtered_metadata.json`
   - Variable names are correctly referenced
   - Value labels match available options

3. **Content Validation**:
   - Transformation rules use correct SPSS syntax
   - Value ranges are valid
   - Explicit values are within category bounds

4. **Interactive Feedback** (if issues found):
   ```
   ⚠️ Excel Evaluation Results:
   ┌────────────────────────────────────────────────────────────┐
   │ Issues Found:                                               │
   │ • Question code "Q99" not found in metadata                │
   │ • Transformation rule has invalid syntax: "RECODE Q5 (...)" │
   │ • Explicit value "99" not in category range [1-5]          │
   │                                                            │
   │ Recommendations:                                            │
   │ • Remove Q99 or verify variable name                        │
   │ • Fix transformation syntax: (1 THRU 2=1) (3=2)            │
   │ • Use valid explicit values: 1,2,3,4,5                     │
   │                                                            │
   │ Continue with auto-corrections? [y/n]                      │
   └────────────────────────────────────────────────────────────┘
   ```

### When No Excel File (Automatic Mode)

1. **Metadata Analysis**: Analyze the filtered_metadata.json to understand the survey structure
2. **AI-Assisted Selection**: Use intelligence to identify row and column indicators:
   - **Row Indicators**: INCLUDE ALL suitable analysis variables (all question/measure variables)
   - **Column Indicators**: Select demographic/banner variables only (respondent characteristics with 10-30 limit)
3. **Apply Selection Rules**:
   - **Row Indicators**: NO LIMITATION - Every question/measure should be analyzed (exclude only metadata/technical fields)
   - **Column Indicators**: HEURISTIC LIMIT - Select 10-30 demographic variables for usable banner analysis
4. **Generate Specification**: Create complete JSONC specification
5. **Present with Reminder**: Show result + improvement tip

### Label Extraction Guidelines

**⚠️ CRITICAL: Extract proper question labels from value labels**

Many SPSS files store the full question text inside the value labels, not in the variable label field.

**Example - Wrong vs Right:**

```json
// Metadata structure:
"Q26_1": {
  "label": "labels26",
  "value_labels": {
    "1.0": "睡觉 (如果您的汽车将是完全自动驾驶的，这意味着...)"
  }
}

// WRONG - Taking only first part of value label:
{
  "indicator_label": "Q26 - 睡觉"
}

// RIGHT - Extracting full question from parentheses:
{
  "indicator_label": "Q26 - 如果您的汽车将是完全自动驾驶的，这意味着只需要您输入目的地"
}
```

**Label Extraction Rules:**

| Pattern | Action | Example |
|---------|--------|---------|
| Value contains `(text)` | Extract text in parentheses as question | "睡觉 (如果您的汽车...)" → "如果您的汽车..." |
| Multiple vars share prefix | Extract common question text | Q26_1, Q26_2 share same question |
| Variable label is descriptive | Use variable label directly | If `label` has actual question text |
| No clear question found | Use variable name or first 50 chars of value | Fallback option |

**Example - Multiple related variables:**

```json
// Q26_1 through Q26_7 all share the same question:
Q26_1: "睡觉 (如果您的汽车将是完全自动驾驶的...)"
Q26_2: "工作 (如果您的汽车将是完全自动驾驶的...)"
Q26_3: "放松 (如果您的汽车将是完全自动驾驶的...)"
...
// Extract once: "如果您的汽车将是完全自动驾驶的，这意味着只需要您输入目的地"
```

**AI Selection Guidelines:**

| Consideration | How to Evaluate |
|---------------|-----------------|
| Variable labels | Look for keywords like "satisfaction", "rating", "agreement" → likely row indicators |
| Variable labels | Look for keywords like "gender", "age", "region", "segment" → likely column indicators |
| Category counts | Very high counts (>50) might be open-ended text → exclude from both |
| Variable naming | Use patterns as hints, but don't rely on them exclusively |
| Context clues | Variables measuring attitudes/behaviors → rows; describing respondents → columns |

**CRITICAL: Row vs Column Selection Rules**

| Indicator Type | Selection Rule | Rationale |
|----------------|----------------|-----------|
| **Row Indicators** | **INCLUDE ALL** - Every suitable analysis variable should be included | Main questions/measures need comprehensive analysis |
| **Column Indicators** | **LIMITED** - Select 10-30 demographic/banner variables only | Too many columns make tables unusable |

**Row Indicator Selection (NO LIMITATION)**:
- Include ALL question/measure variables from the survey
- Include ALL suitable analysis variables
- Exclude only: metadata fields (e.g., SAMPLE, DEVICE_INFO), open-ended text fields, system variables
- DO NOT limit based on category count or question count
- Analyze actual variable labels and content to determine suitability

**Column Indicator Selection (HEURISTIC LIMIT)**:
- Select ONLY demographic/banner variables (respondent characteristics like gender, age, region, income, education)
- Limit to 10-30 maximum for usable cross-tabulation
- Identify by analyzing variable labels and content (keywords: gender, age, region, income, education, occupation, etc.)
- Exclude: repeated measures, multi-item scales, main question variables

**Important Notes:**
- **Work with ANY SPSS data**: This skill works with surveys using ANY variable naming convention. Always analyze actual metadata content (labels, values), never assume specific prefixes or patterns.
- **Use your judgment**: Analyze the actual metadata content, don't assume naming patterns
- **Be flexible**: Different surveys use different naming conventions
- **No arbitrary category limits**: Include variables regardless of their category count
- **Limit column indicators to a reasonable number**: Typically 10-30 for usable banner analysis

### Final Output Validation

1. **Structure validation**: JSON schema check
2. **Reference validation**: Variables exist in metadata
3. **Business logic validation**: Transformation rules are valid
4. **Statistics type validation**: Correct `tabulation_type` assignment

## Output Format

### Implementation Summary (End of Stage 2)

Always present a concise summary, NOT detailed results:

```
┌─────────────────────────────────────────────────────────────┐
│              STAGE 2: IMPLEMENTATION SUMMARY                 │
├─────────────────────────────────────────────────────────────┤
│ ✓ Generated: table_specification.jsonc                      │
│ ✓ Row Indicators: {count} (main questions)                  │
│ ✓ Column Indicators: {count} (demographics)                 │
│ ✓ Total Tables: {rows} × {cols} = {total}                   │
├─────────────────────────────────────────────────────────────┤
│ 📁 Output Location:                                          │
│    output/table_specification.jsonc                          │
│                                                              │
│ 💡 Tip: For more accurate results, provide                  │
│    table-specification.xlsx with your selections.           │
│    Template: .claude/skills/analyzer-tablespec-gen/         │
│             templates/table-specification-template.xlsx     │
└─────────────────────────────────────────────────────────────┘
```

**DO NOT** show:
- Full list of all indicators (unless user asks)
- Detailed variable information
- Complete specification content

**DO** show:
- Summary counts
- Output file location
- Reminder about Excel template

### Example Output (GOOD):

```
STAGE 2: TABLE SPECIFICATION - COMPLETE ✓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Generated: table_specification.jsonc
  Row Indicators: 156 (main questions)
  Column Indicators: 18 (demographics/banners)
  Total Tables: 2,808 (156 × 18)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  📁 Output Location: output/table_specification.jsonc

  💡 Tip: For better results, provide table-specification.xlsx
         Template: .claude/skills/analyzer-tablespec-gen/
                  templates/table-specification-template.xlsx
```

## Next Stage

After Stage 2 completes, proceed to **Stage 3: Cross-Table Calculation** (`stage3-crosstabs`)
