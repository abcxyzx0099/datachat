---
name: analyzer-coordinator
description: 'Survey Analysis Orchestrator - Coordinates 7-stage workflow for SPSS survey analysis using pure Python. Use when running complete analysis pipeline, managing stage dependencies, handling checkpoints, or recovering from errors.'
license: Apache-2.0
---

# Analyzer Coordinator

Orchestrates the complete 7-stage survey analysis workflow.

## Overview

The coordinator manages the entire analysis pipeline:

| Stage | Description | Skill |
|-------|-------------|-------|
| 1 | Data Preparation | `analyzer-data-prep` |
| 2 | Question Extraction | `analyzer-question-extraction` |
| 3 | Indicator Generation | `analyzer-indicator-generation` |
| 4 | Table Specification | `analyzer-tablespec` |
| 5 | Cross-Tabulation Generation | `analyzer-crosstabs` |
| 6 | Statistical Filtering | `analyzer-statistics` |
| 7 | Reporting | `analyzer-reports` |

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

Assistant: [Starting 7-Stage Workflow]
           [Stage 1] Data Preparation...
           Loaded 150 variables, filtered to 45 analysis variables
           Saved: filtered_metadata.json

           [Stage 2] Question Extraction...
           Extracted 90 questions from 345 variables
           Saved: questions.json

           [Stage 3] Indicator Generation...
           Generated 90 indicators using LLM
           Saved: indicators.json

           [Stage 4] Table Specification...
           Classified indicators (row/column) using LLM
           Built table specification
           Saved: table_specification.jsonc

           [Stage 5] Cross-Tabulation Generation...
           Applied transformations, generated cross-tabs
           Computed chi-square and Cramer's V
           Saved: cross_tables_with_stats.json

           [Stage 6] Statistical Filtering...
           Filtered by significance (p < 0.05)
           Significant tables: X of Y (Z%)
           Saved: filtered_tables.json, statistical_summary.json

           [Stage 7] Reporting...
           Generated presentation and dashboard
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
Use skill: analyzer-data-prep
Input: survey.sav file
Output: filtered_metadata.json
```

#### Stage 2: Question Extraction
```bash
Use skill: analyzer-question-extraction
Input: filtered_metadata.json
Output: questions.json
```

#### Stage 3: Indicator Generation
```bash
Use skill: analyzer-indicator-generation
Input: questions.json, filtered_metadata.json
Output: indicators.json
```

#### Stage 4: Table Specification
```bash
Use skill: analyzer-tablespec
Input: indicators.json
Output: table_specification.jsonc
```

#### Stage 5: Cross-Tabulation
```bash
Use skill: analyzer-crosstabs
Input: table_specification.jsonc, filtered_metadata.json
Output: cross_tables_with_stats.json
```

#### Stage 6: Statistical Filtering
```bash
Use skill: analyzer-statistics
Input: cross_tables_with_stats.json
Output: filtered_tables.json, statistical_summary.json
```

#### Stage 7: Reporting
```bash
Use skill: analyzer-reports
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
Stage 2 (Question Extraction)
    ↓
Stage 3 (Indicator Generation)
    ↓
Stage 4 (Table Specification)
    ↓
Stage 5 (Cross-Tabulation)
    ↓
Stage 6 (Statistical Filtering)
    ↓
Stage 7 (Reports)
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
