---
name: survey-coordinator
description: 'Survey Analysis Coordinator - Orchestrates all 5 stages of the workflow. Use when running complete end-to-end survey analysis from SPSS data to final reports.'
license: Apache-2.0
---

# Survey Coordinator - Workflow Orchestrator

Orchestrate the complete 5-stage survey analysis workflow.

## Overview

This skill coordinates all stage skills to execute the full workflow:

```
Stage 1: Data Preparation (Steps 1-3)
    ↓
Stage 2: Table Specification (Steps 4-6)
    ↓
Stage 3: Cross-Table Calculation (Steps 7-9)
    ↓
Stage 4: Statistical Analysis (Steps 10-11)
    ↓
Stage 5: Reporting (Steps 12-13)
```

## When to Use

Use this skill when:
- Running complete end-to-end analysis
- Need to orchestrate multiple stages
- Want automated pipeline execution

## Usage

### Full Pipeline

```
User: Analyze my survey data

Assistant: Starting complete analysis pipeline...

           === Stage 1: Data Preparation ===
           Loading survey_data.sav...
           Extracting 156 variables...
           Filtering to relevant variables...
           ✓ Complete

           === Stage 2: Table Specification ===
           Generating specification with AI...
           Validating structure...
           Please review specification...
           ✓ Approved

           === Stage 3: Cross-Table Calculation ===
           Applying recoding...
           Computing indicators...
           Generating cross-tables...
           ✓ Complete (25 tables)

           === Stage 4: Statistical Analysis ===
           Running chi-square tests...
           Filtering significant tables...
           ✓ Complete (18 significant)

           === Stage 5: Reporting ===
           Creating PowerPoint...
           Creating HTML dashboard...
           ✓ Complete

           === ANALYSIS COMPLETE ===
           Reports ready:
           - presentation.pptx
           - dashboard.html
```

### Resume from Stage

```
User: Continue analysis from Stage 3

Assistant: Resuming from Stage 3: Cross-Table Calculation...
           Using existing: table_specification.json
           ✓ Complete
           Continuing to Stage 4...
```

## Stage Skills

| Stage | Skill | Purpose |
|--------|---------|---------|
| 1 | `stage1-data-prep` | Load and filter metadata |
| 2 | `stage2-spec-gen` | Generate/validate specification |
| 3 | `stage3-crosstabs` | Recoding, indicators, cross-tables |
| 4 | `stage4-statistics` | Statistical tests, filtering |
| 5 | `stage5-reports` | PowerPoint, dashboard |

## Orchestration Features

- **Checkpointing**: Resume from any stage
- **Error handling**: Stop on failure, report issue
- **Progress tracking**: Show stage-by-stage progress
- **Dependency management**: Ensure inputs are ready

## Input Requirements

| Input | Required | From |
|--------|-----------|--------|
| `.sav` file path | Yes | User input |
| Start stage | No | Default: Stage 1 |

## Output Artifacts

Complete pipeline produces:

| Stage | Output |
|--------|---------|
| 1 | `filtered_metadata.json` |
| 2 | `table_specification.json` |
| 3 | `recoded_data.sav`, `indicators.csv`, `cross_tables.csv` |
| 4 | `statistical_summary.json`, `filtered_tables.json` |
| 5 | `presentation.pptx`, `dashboard.html` |

## Error Handling

| Error | Action |
|--------|---------|
| Stage 1 fails | Check .sav file path |
| Stage 2 validation fails | Review specification manually |
| Stage 3 fails | Check PSPP installation |
| Stage 4 fails | Review cross-tables data |
| Stage 5 fails | Check filtered results |

## Workflow Control

### Checkpoint Resume

```bash
# Resume from specific stage
survey-coordinator --resume-from stage3
```

### Dry Run

```bash
# Validate pipeline without execution
survey-coordinator --dry-run
```
