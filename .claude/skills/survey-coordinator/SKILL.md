---
name: survey-coordinator
description: 'Survey Analysis Orchestrator - Coordinates 5-stage workflow for SPSS survey analysis. Use when running complete analysis pipeline, managing stage dependencies, handling checkpoints, or recovering from errors.'
license: Apache-2.0
---

# Survey Coordinator

Orchestrates the complete 5-stage survey analysis workflow.

## Overview

The survey coordinator manages the entire analysis pipeline:
- **Stage 1**: Data Preparation (`stage1-data-prep`)
- **Stage 2**: Table Specification (`stage2-spec-gen`)
- **Stage 3**: Cross-Table Calculation (`stage3-crosstabs`)
- **Stage 4**: Statistical Analysis (`stage4-statistics`)
- **Stage 5**: Reporting (`stage5-reports`)

## When to Use

Use this skill when:
- Running complete survey analysis from .sav file
- Need to coordinate multi-stage workflow
- Managing stage dependencies and data flow
- Implementing checkpoint/recovery机制
- Need progress tracking across stages

## Usage

```
User: Analyze survey_data.sav with full workflow

Assistant: [Starting 5-Stage Workflow]
           [Stage 1] Data Preparation...
           Loaded 150 variables, filtered to 45 analysis variables
           Saved: filtered_metadata.json

           [Stage 2] Table Specification...
           Generated 18 tables, 6 indicators
           Saved: table_specification.json

           [Stage 3] Cross-Table Calculation...
           Computed 6 indicators, generated crosstabs
           Saved: indicators.csv, cross_tables.json

           [Stage 4] Statistical Analysis...
           Chi-square tests: 18 tables
           Significant (p<0.05): 8 tables
           Saved: statistical_summary.json, filtered_tables.json

           [Stage 5] Reporting...
           Generated 24-slide presentation
           Created interactive HTML dashboard
           Saved: presentation.pptx, dashboard.html

           Analysis complete! All outputs in output/
```

## Input

| Input | Required | Description |
|--------|-----------|-------------|
| `--sav-file` | Yes | Path to SPSS .sav file |
| `--output-dir` | No | Output directory (default: output/) |

## Output

| File/Directory | Content |
|----------------|----------|
| `output/filtered_metadata.json` | Analysis variables from Stage 1 |
| `output/table_specification.json` | Table/indicator specs from Stage 2 |
| `output/indicators.csv` | Computed indicators from Stage 3 |
| `output/cross_tables.json` | Cross-table results from Stage 3 |
| `output/statistical_summary.json` | Test results from Stage 4 |
| `output/filtered_tables.json` | Significant tables from Stage 4 |
| `output/presentation.pptx` | PowerPoint presentation from Stage 5 |
| `output/dashboard.html` | Interactive dashboard from Stage 5 |

## Workflow Features

- **Checkpointing**: Each stage saves progress for recovery
- **Dependency Management**: Ensures stages execute in correct order
- **Error Recovery**: Can resume from failed stage
- **Progress Tracking**: Reports completion status for each stage
- **Data Validation**: Verifies inputs before each stage

## Library Modules

| Module | Purpose |
|---------|---------|
| `survey_analyzer.io.SPSSReader` | Read .sav files |
| `survey_analyzer.io.MetadataTransformer` | Transform/filter metadata |
| `survey_analyzer.specification.SpecificationGenerator` | Generate table specs |
| `survey_analyzer.pspp.PSPPExecutor` | Execute PSPP syntax |

## Stage Dependencies

```
Stage 1 (Data Prep)
    ↓
Stage 2 (Specification)
    ↓
Stage 3 (Crosstabs)
    ↓
Stage 4 (Statistics)
    ↓
Stage 5 (Reports)
```

## Running Individual Stages

To run a single stage:
```bash
# Stage 1 only
stage1-data-prep --sav-file data.sav --output-dir output/

# Stage 2 only (requires Stage 1 output)
stage2-spec-gen --metadata-file output/filtered_metadata.json

# Stage 3 only (requires Stages 1-2 output)
stage3-crosstabs --sav-file data.sav --spec-file output/table_specification.json

# Stage 4 only (requires Stage 3 output)
stage4-statistics --crosstabs-file output/cross_tables.json

# Stage 5 only (requires Stage 4 output)
stage5-reports --filtered-file output/filtered_tables.json
```
