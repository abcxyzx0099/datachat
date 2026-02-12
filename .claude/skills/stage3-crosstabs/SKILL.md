---
name: stage3-crosstabs
description: 'Stage 3: Cross-Table Calculation - Apply recoding, compute indicators, generate cross-tables using PSPP. Output: recoded_data.sav, indicators.csv, cross_tables.csv. Use when running computation on validated specification.'
license: Apache-2.0
---

# Stage 3: Cross-Table Calculation

Execute recoding, indicator computation, and cross-table generation.

## Overview

Executes **Steps 7-9** of the workflow:
- Step 7: Apply recoding rules (PSPP)
- Step 8: Compute indicators
- Step 9: Generate cross-tables (PSPP)

## When to Use

Use this skill when:
- Table specification is validated
- Ready to run computation
- Need to prepare data for statistical analysis

## Usage

```
User: Run cross-table calculation

Assistant: [Step 7] Applying recoding rules via PSPP...
           Created: recoded_data.sav (50 variables recoded)

           [Step 8] Computing indicators...
           Created: indicators.csv (5 indicators)

           [Step 9] Generating cross-tables via PSPP...
           Created: cross_tables.csv (25 tables)

Stage 3 complete! Ready for statistical analysis.
```

## Input

| Input | Required | Description |
|--------|-----------|-------------|
| `table_specification.json` | Yes | Validated specification |
| Source `.sav` file | Yes | Original survey data |

## Output

| File | Content |
|-------|----------|
| `recoded_data.sav` | Data after recoding |
| `indicators.csv` | Computed indicator values |
| `cross_tables.csv` | Raw cross-tabulations |

## Library Modules

| Module | Purpose |
|---------|---------|
| `spss_analyzer.pspp.RecodingSyntaxGenerator` | Generate PSPP recoding syntax |
| `spss_analyzer.pspp.PSPPExecutor` | Execute PSPP commands |
| `spss_analyzer.analysis.IndicatorGenerator` | Compute indicators |
| `spss_analyzer.pspp.CTablesSyntaxGenerator` | Generate cross-table syntax |

## Dependencies

- PSPP (external package)
- Source .sav file
- Validated table specification
