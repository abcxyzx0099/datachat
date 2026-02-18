---
name: analyzer-coordinator
description: 'Survey Analysis Orchestrator - Coordinates 5-stage workflow for SPSS survey analysis using pure Python. Use when running complete analysis pipeline, managing stage dependencies, handling checkpoints, or recovering from errors.'
license: Apache-2.0
---

# Analyzer Coordinator

Orchestrates the complete 5-stage survey analysis workflow.

## Overview

The coordinator manages the entire analysis pipeline:

| Stage | Description | Skill |
|-------|-------------|-------|
| 1 | Data Preparation | `stage1-data-prep` |
| 2 | Table Specification | `stage2-spec-gen` |
| 3 | Cross-Tabulation Generation | `stage3-crosstabs` |
| 4 | Statistical Filtering | `stage4-statistics` |
| 5 | Reporting | `stage5-reports` |

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
           Generated 18 tables, 6 indicators (AI-orchestrated)
           Saved: table_specification.jsonc

           [Stage 3] Cross-Tabulation Generation...
           Applied transformations, generated cross-tabs
           Computed chi-square and Cramer's V for 18 tables
           Saved: cross_tables_with_stats.json

           [Stage 4] Statistical Filtering...
           Filtered by significance (p < 0.05)
           Significant tables: 8 of 18 (44.4%)
           Saved: filtered_tables.json, statistical_summary.json

           [Stage 5] Reporting...
           Generated 24-slide presentation
           Created interactive HTML dashboard
           Saved: presentation.pptx, dashboard.html

           Analysis complete! All outputs in output/
```

## CLI Commands

### Complete Workflow (All Stages)

```bash
# Invoke via skills
Use skill: analyzer-coordinator
Input: survey.sav file

# Or run stages sequentially via individual skills
```

### Individual Stages (via Skills)

#### Stage 1: Data Preparation
```bash
Use skill: stage1-data-prep
Input: survey.sav file
Output: filtered_metadata.json
```

#### Stage 2: Table Specification
```bash
Use skill: stage2-spec-gen
Input: filtered_metadata.json, table-specification.xlsx
Output: table_specification.jsonc
```

#### Stage 3: Cross-Tabulation
```bash
Use skill: stage3-crosstabs
Input: table_specification.jsonc, filtered_metadata.json
Output: cross_tables_with_stats.json
```

#### Stage 4: Statistical Filtering
```bash
Use skill: stage4-statistics
Input: cross_tables_with_stats.json
Output: filtered_tables.json, statistical_summary.json
```

#### Stage 5: Reporting
```bash
Use skill: stage5-reports
Input: filtered_tables.json
Output: presentation.pptx, dashboard.html
```

## Input

| Input | Required | Description |
|--------|-----------|-------------|
| `--sav-file` | Yes | Path to SPSS .sav file |
| `--output-dir` | No | Output directory (default: output/) |
| `--skip` | No | Stages to skip (e.g., "3,4") |

## Output

| File/Directory | Stage | Content |
|----------------|-------|----------|
| `output/filtered_metadata.json` | 1 | Analysis variables |
| `output/table_specification.jsonc` | 2 | Table/indicator specs |
| `output/cross_tables_with_stats.json` | 3 | Cross-tables + chi-square + Cramer's V |
| `output/filtered_tables.json` | 4 | Significant tables only |
| `output/statistical_summary.json` | 4 | All statistics summary |
| `output/presentation.pptx` | 5 | PowerPoint presentation |
| `output/dashboard.html` | 5 | Interactive HTML dashboard |

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
| `survey_analyzer.analysis.TransformationEngine` | Apply recoding/transformations |
| `survey_analyzer.analysis.CrossTabGenerator` | Generate cross-tabs with statistics |
| `survey_analyzer.filtering.SignificanceFilter` | Filter by p-value |

## Stage Dependencies

```
Stage 1 (Data Prep)
    ↓
Stage 2 (Specification - AI)
    ↓
Stage 3 (Cross-Tabulation)
    ↓
Stage 4 (Statistical Filtering)
    ↓
Stage 5 (Reports)
```

## References

| Resource | Location |
|----------|----------|
| Data Flow Document | `docs/data-related/data-flow.md` |
| System Architecture | `docs/application-design/system-architecture.md` |
| Business Rules | `docs/application-design/business-rules.md` |

## Technology Stack

| Component | Technology |
|-----------|------------|
| **Data Processing** | pandas, numpy |
| **Statistical Tests** | scipy.stats (chi2_contingency) |
| **SPSS I/O** | pyreadstat |
| **Coordination** | Claude Code Skills |
