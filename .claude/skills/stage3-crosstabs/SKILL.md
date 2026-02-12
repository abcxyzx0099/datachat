---
name: stage3-crosstabs
description: 'Stage 3: Cross-Table Calculation - Executes recoding, computes indicators, and generates cross-tables using PSPP. Use when table specification is ready and computation is needed.'
license: Apache-2.0
---

# Stage 3: Cross-Table Calculation

Computes indicators and generates cross-tables from survey data.

## Overview

Executes **Steps 7-9** of the workflow:
- Step 7: Apply recoding rules
- Step 8: Compute indicators
- Step 9: Generate cross-tables

## When to Use

Use this skill when:
- Table specification is complete (Stage 2)
- Need to compute derived indicators
- Need to generate cross-tabulation tables
- Preparing data for statistical testing

## Usage

```
User: Compute crosstabs for our survey

Assistant: [Step 7] Applying recoding rules...
           No global recodings defined - skipping

           [Step 8] Computing indicators...
           Computed 6 indicators:
           - sat_overall: 3.42 (mean)
           - top2_box: 67.8% (percentage)
           - nps_score: 42 (NPS)
           - ... (3 more)

           Saved: indicators.csv

           [Step 9] Generating cross-tables...
           Generated 18 cross-table specifications:
           PSPP syntax created: pspp_crosstabs.sps
           Tables ready for PSPP execution

           Stage 3 complete!
```

## Input

| Input | Required | Description |
|--------|-----------|-------------|
| `--sav-file` | Yes | Path to SPSS .sav file |
| `--spec-file` | Yes | Path to table_specification.json |
| `--metadata-file` | Yes | Path to filtered_metadata.json |

## Output

| File | Content |
|-------|----------|
| `indicators.csv` | Computed indicator values |
| `cross_tables.json` | Cross-table results |
| `pspp_recoding.sps` | PSPP recoding syntax (if applicable) |
| `pspp_crosstabs.sps` | PSPP crosstabs syntax |

## Recoding Types

| Type | Description | Example |
|-------|-------------|----------|
| **Value map** | Remap specific values | 1→100, 2→75, 3→50 |
| **Range** | Group values into categories | 1-3→"Low", 4-5→"High" |
| **Missing** | Set values as system missing | 99→$SYSMIS |

## Indicator Computation

| Aggregation | Formula | Use Case |
|-------------|---------|-----------|
| `mean` | Average of values | Scale variables (satisfaction, ratings) |
| `sum` | Sum of values | Total counts, scores |
| `count` | Non-null count | Sample sizes, response counts |
| `median` | Middle value | Robust central tendency |
| `min` | Minimum value | Range analysis |
| `max` | Maximum value | Range analysis |

## PSPP Integration

This skill generates PSPP syntax for:
- **Recoding**: Variable transformations
- **Crosstabs**: Cross-tabulation tables
- **CTABLES**: Custom table format with statistics

Generated syntax can be executed with:
```bash
pspp pspp_crosstabs.sps -o output.txt
```

## Library Modules

| Module | Purpose |
|---------|---------|
| `survey_analyzer.io.SPSSReader` | Read .sav files |
| `survey_analyzer.pspp.PSPPExecutor` | Execute PSPP commands |
| `survey_analyzer.pspp.RecodingSyntaxGenerator` | Generate recode syntax |
| `survey_analyzer.pspp.CTablesSyntaxGenerator` | Generate ctables syntax |

## Data Flow

```
Stage 2 Specification
    ↓
Stage 3 Computation
    ↓ (indicators.csv)
    ↓ (cross_tables.json)
Stage 4 Statistics
```

## Next Stage

After Stage 3 completes, proceed to **Stage 4: Statistical Analysis** (`stage4-statistics`)
