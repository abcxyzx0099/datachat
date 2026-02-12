---
name: analyzer-coordinator
description: 'Survey Analysis Orchestrator - Coordinates 5-stage workflow for SPSS survey analysis. Use when running complete analysis pipeline, managing stage dependencies, handling checkpoints, or recovering from errors.'
license: Apache-2.0
---

# Analyzer Coordinator (Stage 1)

Orchestrates the complete 5-stage survey analysis workflow.

## Overview

The coordinator manages the entire analysis pipeline:

| Stage | Description | CLI Command |
|-------|-------------|-------------|
| 1 | Data Preparation | `spss-analyzer data read` |
| 2 | Table Specification | `spss-analyzer spec tables` |
| 3 | Indicators & Crosstabs | `spss-analyzer analysis indicators/crosstabs` |
| 4 | Statistical Analysis | `spss-analyzer stats test/filter` |
| 5 | Reporting | `spss-analyzer reporting ppt/html` |

## When to Use

Use this skill when:
- Running complete survey analysis from .sav file
- Need to coordinate multi-stage workflow
- Managing stage dependencies and data flow
- Implementing checkpoint/recovery mechanism
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
           Saved: indicators.json, cross_tables.json

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

## CLI Commands

### Complete Workflow (All Stages)

```bash
spss-analyzer all \
  --sav-file data/survey.sav \
  --output-dir output/
```

### Individual Stages

#### Stage 1: Data Preparation
```bash
spss-analyzer data read \
  --sav-file data/survey.sav \
  --output-file output/filtered_metadata.json
```

#### Stage 2: Table Specification
```bash
spss-analyzer spec tables \
  --metadata-file output/filtered_metadata.json \
  --output-file output/table_specification.json
```

#### Stage 3: Indicators
```bash
spss-analyzer analysis indicators \
  --spec-file output/table_specification.json \
  --metadata-file output/filtered_metadata.json \
  --output-file output/indicators.json
```

#### Stage 3: Crosstabs
```bash
spss-analyzer analysis crosstabs \
  --spec-file output/table_specification.json \
  --metadata-file output/filtered_metadata.json \
  --output-file output/cross_tables.json
```

#### Stage 4: Statistical Test
```bash
spss-analyzer stats test \
  --crosstabs-file output/cross_tables.json \
  --output-file output/test_results.json
```

#### Stage 4: Filter by Significance
```bash
spss-analyzer stats filter \
  --crosstabs-file output/test_results.json \
  --output-file output/filtered_tables.json
```

#### Stage 5: PowerPoint Report
```bash
spss-analyzer reporting ppt \
  --tables-file output/filtered_tables.json \
  --output-dir output/
```

#### Stage 5: HTML Dashboard
```bash
spss-analyzer reporting html \
  --tables-file output/filtered_tables.json \
  --output-dir output/
```

### Skipping Stages

```bash
spss-analyzer all \
  --sav-file data/survey.sav \
  --output-dir output/ \
  --skip "3,4"
```

## Input

| Input | Required | Description |
|--------|-----------|-------------|
| `--sav-file` | Yes | Path to SPSS .sav file |
| `--output-dir` | No | Output directory (default: output/) |
| `--skip` | No | Stages to skip (e.g., "3,4") |

## Output

| File/Directory | Content |
|----------------|----------|
| `output/filtered_metadata.json` | Analysis variables from Stage 1 |
| `output/table_specification.json` | Table/indicator specs from Stage 2 |
| `output/indicators.json` | Computed indicators from Stage 3 |
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

## References

| Resource | Location |
|----------|----------|
| PSPP Manual | `references/pspp_manual.txt` |
| PSPP Syntax Reference | `docs/knowledge/pspp-syntax/pspp-syntax-reference.md` |
