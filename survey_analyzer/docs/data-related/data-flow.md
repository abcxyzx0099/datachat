# Data Flow

This document describes the workflow for the SPSS Survey Analysis system using a **7-stage unified pipeline** with a single `table_specification.jsonc` file as the source of truth.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Architecture](#2-architecture)
3. [7-Stage Workflow](#3-7-stage-workflow)
4. [Unified Specification](#4-unified-specification)
5. [CLI Commands](#5-cli-commands)
6. [Stage Details](#6-stage-details)
7. [Key Terminology](#7-key-terminology)

---

## 1. Overview

### 1.1 Purpose

Design and implement an automated workflow for SPSS survey data analysis using a **7-stage unified pipeline**. The system processes SPSS (.sav) survey data, applies AI-orchestrated transformations, generates indicators, performs statistical analysis, and produces outputs in PowerPoint and HTML formats.

### 1.2 Scope

| Aspect | Description |
|--------|-------------|
| **Input** | SPSS (.sav) survey data files |
| **Processing** | AI-orchestrated indicator generation, classification, and statistical analysis |
| **Output** | PowerPoint presentations, HTML dashboards with visualizations |
| **Target** | Market research industry professionals |

### 1.3 Key Design Principles

| Principle | Description |
|-----------|-------------|
| **Single Source of Truth** | One `table_specification.jsonc` file for all stages |
| **Stage-Based Progression** | Each stage updates the spec with new data |
| **Checkpointing** | Save progress after each question for resume capability |
| **Optional AI Stages** | Stages 3 and 4 use LLM, but can be manually overridden |
| **Metadata Preservation** | Stage history tracked in spec metadata |

---

## 2. Architecture

### 2.1 Component Structure

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           CLI Interface                                 │
│                    (survey_analyzer cli.py)                             │
└────────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    survey_analyzer Library                              │
│  (Pure Python: Data Processing & Computation)                          │
├─────────────────────────────────────────────────────────────────────────┤
│ io/             │ SPSS file I/O, metadata handling                      │
│ questions/      │ Question extraction and variable grouping             │
│ indicators/     │ LLM-based indicator generation (batch processor)      │
│ tablespec/      │ LLM-based row/column classification                  │
│ analysis/       │ Crosstabs and statistical calculations                │
│ filtering/      │ Significance filtering                                │
│ reporting/      │ PowerPoint and HTML generation                        │
└─────────────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                  Single Source of Truth                                  │
│              table_specification.jsonc                                   │
│  - Questions (Stage 2)                                                   │
│  - Indicators (Stage 3)                                                  │
│  - Classification (Stage 4)                                              │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Module Responsibilities

| Module | Stage | Purpose | AI Required |
|--------|-------|---------|-------------|
| **io/** | 1 | Load .sav, extract/filter metadata | No |
| **questions/** | 2 | Extract question codes, group variables | No |
| **indicators/** | 3 | Generate indicators using LLM | Yes |
| **tablespec/** | 4 | Classify indicators as row/column | Yes |
| **analysis/** | 5 | Compute crosstabs and statistics | No |
| **filtering/** | 6 | Filter by significance | No |
| **reporting/** | 7 | Generate PowerPoint and HTML | No |

---

## 3. 7-Stage Workflow

### 3.1 Workflow Diagram

```mermaid
flowchart TD
    %% Define styles
    classDef processingGreen fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000
    classDef processingBlue fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#000
    classDef processingOrange fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#000
    classDef processingPurple fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#000
    classDef artifactStyle fill:#fff8e1,stroke:#f57c00,stroke-width:2px,color:#000
    classDef stageLabelStyle fill:#f5f5f5,stroke:#9e9e9e,stroke-width:2px,stroke-dasharray:5 5,color:#424242

    %% STAGE 1: Data Preparation
    subgraph STAGE1[" "]
        direction TB
        stage1_label["**STAGE 1: Data Preparation**"]:::stageLabelStyle
        S1["Step 1<br/>Load .sav File"]:::processingGreen
        S2["Step 2<br/>Extract Metadata"]:::processingGreen
        S3["Step 3<br/>Filter by Category Count"]:::processingGreen
        metadata[("filtered_metadata.json")]:::artifactStyle
    end

    %% STAGE 2: Question Extraction
    subgraph STAGE2[" "]
        direction TB
        stage2_label["**STAGE 2: Question Extraction**"]:::stageLabelStyle
        S4["Step 4<br/>Extract Question Codes"]:::processingGreen
        S5["Step 5<br/>Group Variables by Question"]:::processingGreen
        tableSpec[("table_specification.jsonc<br/>(with questions)")]:::artifactStyle
    end

    %% STAGE 3: Indicator Generation
    subgraph STAGE3[" "]
        direction TB
        stage3_label["**STAGE 3: Indicator Generation (AI)"]"]:::stageLabelStyle
        S6["Step 6<br/>Generate Indicators via LLM<br/>(Batch Processing)"]:::processingBlue
        tableSpec2[("table_specification.jsonc<br/>(with indicators)")]:::artifactStyle
    end

    %% STAGE 4: Classification
    subgraph STAGE4[" "]
        direction TB
        stage4_label["**STAGE 4: Classification (AI)**"]:::stageLabelStyle
        S7["Step 7<br/>Classify Indicators<br/>(Row vs Column)"]:::processingBlue
        S8["Step 8<br/>Apply is_row/is_column"]:::processingOrange
        tableSpec3[("table_specification.jsonc<br/>(with classification)")]:::artifactStyle
    end

    %% STAGE 5: Analysis
    subgraph STAGE5[" "]
        direction TB
        stage5_label["**STAGE 5: Cross-Table Generation**"]:::stageLabelStyle
        S9["Step 9<br/>Generate Crosstabs"]:::processingGreen
        S10["Step 10<br/>Calculate Statistics"]:::processingGreen
        crosstabs[("cross_tables.json")]:::artifactStyle
    end

    %% STAGE 6: Statistics
    subgraph STAGE6[" "]
        direction TB
        stage6_label["**STAGE 6: Statistical Filtering**"]:::stageLabelStyle
        S11["Step 11<br/>Filter by Significance"]:::processingGreen
        S12["Step 12<br/>Apply Cramer's V Threshold"]:::processingGreen
        filtered[("filtered_tables.json")]:::artifactStyle
    end

    %% STAGE 7: Reporting
    subgraph STAGE7[" "]
        direction TB
        stage7_label["**STAGE 7: Reporting**"]:::stageLabelStyle
        S13["Step 13<br/>Generate PowerPoint"]:::processingGreen
        S14["Step 14<br/>Generate HTML Dashboard"]:::processingGreen
        outputs[("presentation.pptx<br/>dashboard.html")]:::artifactStyle
    end

    %% Connections
    savFile[("survey.sav")]:::artifactStyle
    savFile --> S1
    S1 --> S2 --> S3 --> metadata
    metadata --> S4 --> S5 --> tableSpec
    tableSpec --> S6 --> tableSpec2
    tableSpec2 --> S7 --> S8 --> tableSpec3
    tableSpec3 --> S9 --> S10 --> crosstabs
    crosstabs --> S11 --> S12 --> filtered
    filtered --> S13 --> S14 --> outputs
```

### 3.2 Stage Summary

| Stage | Name | Input | Output | AI Required |
|-------|------|-------|--------|-------------|
| 1 | Data Preparation | `survey.sav` | `filtered_metadata.json` | No |
| 2 | Question Extraction | `filtered_metadata.json` | `table_specification.jsonc` | No |
| 3 | Indicator Generation | `table_specification.jsonc` + metadata | Updated `table_specification.jsonc` | **Yes** |
| 4 | Classification | `table_specification.jsonc` | Updated `table_specification.jsonc` | **Yes** |
| 5 | Cross-Table Generation | `table_specification.jsonc` + data | `cross_tables.json` | No |
| 6 | Statistical Filtering | `cross_tables.json` | `filtered_tables.json` | No |
| 7 | Reporting | `filtered_tables.json` | `presentation.pptx`, `dashboard.html` | No |

---

## 4. Unified Specification

### 4.1 table_specification.jsonc Structure

```jsonc
// Unified Table Specification
// Single source of truth for all stages

{
  "metadata": {
    "spec_id": "unique-spec-id",
    "project_id": "project-name",
    "stage": "current_stage_name",
    "stage_history": [
      {"stage": 1, "timestamp": "2024-01-01T00:00:00Z", "description": "Data prepared"},
      {"stage": 2, "timestamp": "2024-01-01T01:00:00Z", "description": "Questions extracted"},
      ...
    ]
  },
  "questions": [
    {
      "question_code": "Q1",
      "question_type": "Single Choice",
      "question_text": "Sample question text",
      "original_variables": ["Q1_1", "Q1_2", "Q1_3"],
      "indicators": [
        {
          "indicator_code": "Q1_SAT",
          "indicator_label": "Satisfaction Level",
          "indicator_variables": ["Q1_1"],
          "transformation": null,
          "tabulation_type": "categorical",
          "tabulation_metric": "column_percent",
          "indicator_value_labels": {"1": "Very Satisfied", "2": "Satisfied"},
          "is_row": true,
          "is_column": false
        }
      ]
    }
  ],
  "filter_clause": {},
  "weight_indicator": null
}
```

### 4.2 Field Naming Conventions

| Level | Field Name | Description |
|-------|------------|-------------|
| Question | `question_code` | Unique identifier (e.g., "Q1", "S0") |
| Question | `original_variables` | Raw SPSS variables belonging to this question |
| Indicator | `indicator_code` | Unique identifier (e.g., "Q1_SAT", "S0_GENDER") |
| Indicator | `indicator_variables` | Variables used for this indicator |
| Indicator | `indicator_value_labels` | Value label mappings |

### 4.3 Stage Evolution

The spec file evolves through each stage:

| Stage | State | Changes |
|-------|-------|---------|
| 1 | Not applicable | `filtered_metadata.json` created |
| 2 | `questions_extracted` | Questions added with empty `indicators: []` |
| 3 | `indicators_generated` | Indicators added to each question |
| 4 | `classification_complete` | `is_row`/`is_column` fields added |
| 5+ | Not applicable | Spec used as reference for analysis |

---

## 5. CLI Commands

### 5.1 Command Structure

```bash
python -m survey_analyzer <command> <subcommand> [options]
```

### 5.2 Stage 1: Data Preparation

```bash
# Read SPSS file and output metadata
python -m survey_analyzer data read --sav-file survey.sav --output-file metadata.json

# Filter metadata by category count
python -m survey_analyzer data filter --metadata-file metadata.json --max-categories 20

# Combined: read and filter in one command
python -m survey_analyzer data prep --sav-file survey.sav --output-file output/filtered_metadata.json
```

### 5.3 Stage 2: Question Extraction

```bash
python -m survey_analyzer questions extract \
  --metadata-file output/filtered_metadata.json \
  --output-file output/table_specification.jsonc \
  --backup-file output/questions.json
```

### 5.4 Stage 3: Indicator Generation

```bash
# Process all questions
python -m survey_analyzer indicators batch \
  --spec-file output/table_specification.jsonc \
  --metadata-file output/filtered_metadata.json

# Process specific questions
python -m survey_analyzer indicators batch \
  --spec-file output/table_specification.jsonc \
  --metadata-file output/filtered_metadata.json \
  --questions "Q1,Q2,S0"

# Disable resume (reprocess all)
python -m survey_analyzer indicators batch \
  --spec-file output/table_specification.jsonc \
  --metadata-file output/filtered_metadata.json \
  --no-resume

# Stop on first error
python -m survey_analyzer indicators batch \
  --spec-file output/table_specification.jsonc \
  --metadata-file output/filtered_metadata.json \
  --stop-on-error
```

### 5.5 Stage 4: Classification

```bash
# Show Excel template info (optional guidance)
python -m survey_analyzer tablespec template

# Classify indicators as row/column
python -m survey_analyzer tablespec build \
  --spec-file output/table_specification.jsonc \
  --output-file output/table_specification.jsonc
```

### 5.6 Stage 5: Cross-Table Generation

```bash
python -m survey_analyzer analysis indicators \
  --spec-file output/table_specification.jsonc \
  --metadata-file output/filtered_metadata.json \
  --output-file output/cross_tables.json
```

### 5.7 Stage 6: Statistical Filtering

```bash
# Calculate chi-square tests
python -m survey_analyzer stats test \
  --crosstabs-file output/cross_tables.json \
  --threshold 0.05 \
  --output-file output/test_results.json

# Filter by significance
python -m survey_analyzer stats filter \
  --crosstabs-file output/cross_tables.json \
  --threshold 0.05 \
  --output-file output/filtered_tables.json
```

### 5.8 Stage 7: Reporting

```bash
# Generate PowerPoint
python -m survey_analyzer reporting ppt \
  --tables-file output/filtered_tables.json \
  --output-dir output

# Generate HTML dashboard
python -m survey_analyzer reporting html \
  --tables-file output/filtered_tables.json \
  --output-dir output
```

---

## 6. Stage Details

### 6.1 Stage 1: Data Preparation

**Purpose**: Load SPSS file and extract variable metadata

**Process**:
1. Load `.sav` file using `pyreadstat`
2. Extract variable labels, value labels, and metadata
3. Filter variables by category count (default: max 20 categories)
4. Output: `filtered_metadata.json`

**Output Format**:
```json
{
  "Q1_1": {
    "variable_name": "Q1_1",
    "label": "Option 1",
    "value_labels": {"1": "Yes", "2": "No"},
    "category_count": 2
  }
}
```

### 6.2 Stage 2: Question Extraction

**Purpose**: Extract question codes and group variables

**Process**:
1. Parse variable names to extract question codes (e.g., `Q1_1` → `Q1`)
2. Group variables by question code
3. Create `table_specification.jsonc` with questions
4. Output: Updated `table_specification.jsonc`

**Question Grouping Logic**:
- Variables with same prefix before first underscore are grouped
- Single variables without underscore become their own question
- Questions sorted alphabetically by code

### 6.3 Stage 3: Indicator Generation (AI)

**Purpose**: Generate indicators for each question using LLM

**Process**:
1. For each question, send metadata and question info to LLM
2. LLM generates indicators with:
   - Indicator code and label
   - Variable selection
   - Transformation rules (if needed)
   - Tabulation type and metric
   - Value labels
3. Batch processing with checkpointing after each question
4. Resume capability: skip questions with existing indicators
5. Output: Updated `table_specification.jsonc` with indicators

**Batch Processing Features**:
- Progress callback for monitoring
- Continue on error (default) or stop on error
- Save checkpoint after each question
- Support for specific question selection

### 6.4 Stage 4: Classification (AI)

**Purpose**: Classify indicators as row or column for crosstabs

**Process**:
1. Send all indicators to LLM with context
2. LLM classifies each as:
   - `is_row`: true/false
   - `is_column`: true/false
3. Apply classification to indicators in spec
4. Output: Updated `table_specification.jsonc` with classification

**Helper Methods**:
- `get_row_indicators()`: Return all row indicators
- `get_column_indicators()`: Return all column indicators

### 6.5 Stage 5: Cross-Table Generation

**Purpose**: Generate crosstabs and calculate statistics

**Process**:
1. For each row/column indicator pair:
   - Apply transformations
   - Generate crosstab
   - Calculate chi-square test
   - Calculate Cramer's V
2. Output: `cross_tables.json`

**Statistics Calculated**:
- Chi-square test
- P-value
- Cramer's V (effect size)
- Degrees of freedom

### 6.6 Stage 6: Statistical Filtering

**Purpose**: Filter tables by statistical significance

**Process**:
1. Filter by p-value threshold (default: 0.05)
2. Filter by Cramer's V threshold (default: 0.1)
3. Generate summary statistics
4. Output: `filtered_tables.json`

**Summary Includes**:
- Total tables tested
- Significant tables count
- Effect size distribution

### 6.7 Stage 7: Reporting

**Purpose**: Generate presentation-ready reports

**PowerPoint Output**:
- Title slide
- Table slides with statistics
- Charts for visualizations
- Professional formatting

**HTML Dashboard Output**:
- Interactive filtering
- Visualizations
- Statistical summaries
- Responsive design

---

## 7. Key Terminology

| Term | Definition |
|------|------------|
| **Question** | A survey question (e.g., "Q1: Satisfaction Level") |
| **Variable** | Raw SPSS variable (e.g., "Q1_1", "Q1_2") |
| **Indicator** | Derived measure for analysis (e.g., "Q1_SAT") |
| **Transformation** | SPSS-style recoding or computing |
| **Crosstab** | Cross-tabulation of row and column indicators |
| **Row Indicator** | Variable used as rows in crosstab |
| **Column Indicator** | Variable used as columns in crosstab |
| **Checkpoint** | Saved state after processing each question |
| **Resume** | Continue from last checkpoint, skip completed |
| **Unified Spec** | Single `table_specification.jsonc` file for all stages |

---

## Appendix A: Environment Setup

### Required Environment Variables

| Variable | Purpose | Required For |
|----------|---------|--------------|
| `GLM_API_KEY` | Zhipu AI API key for LLM | Stages 3, 4 |
| `ZHIPU_API_KEY` | Alternative to GLM_API_KEY | Stages 3, 4 |

### Install Dependencies

```bash
# Basic installation
pip install -e survey_analyzer

# With AI support (required for Stages 3-4)
pip install zai-sdk

# With all dependencies
pip install -e "survey_analyzer[dev]"
```

---

## Appendix B: Common Workflows

### Complete Analysis Workflow

```bash
# Stage 1: Prepare data
python -m survey_analyzer data prep --sav-file survey.sav

# Stage 2: Extract questions
python -m survey_analyzer questions extract \
  --metadata-file output/filtered_metadata.json

# Stage 3: Generate indicators (AI)
python -m survey_analyzer indicators batch \
  --spec-file output/table_specification.jsonc \
  --metadata-file output/filtered_metadata.json

# Stage 4: Classify indicators (AI)
python -m survey_analyzer tablespec build \
  --spec-file output/table_specification.jsonc

# Stage 5: Generate crosstabs
python -m survey_analyzer analysis indicators \
  --spec-file output/table_specification.jsonc \
  --metadata-file output/filtered_metadata.json \
  --output-file output/cross_tables.json

# Stage 6: Filter by significance
python -m survey_analyzer stats filter \
  --crosstabs-file output/cross_tables.json \
  --output-file output/filtered_tables.json

# Stage 7: Generate reports
python -m survey_analyzer reporting ppt \
  --tables-file output/filtered_tables.json
python -m survey_analyzer reporting html \
  --tables-file output/filtered_tables.json
```

### Resume Interrupted Batch Processing

```bash
# Will continue from where it left off
python -m survey_analyzer indicators batch \
  --spec-file output/table_specification.jsonc \
  --metadata-file output/filtered_metadata.json
```

### Process Specific Questions

```bash
# Only process Q1, Q2, and S0
python -m survey_analyzer indicators batch \
  --spec-file output/table_specification.jsonc \
  --metadata-file output/filtered_metadata.json \
  --questions "Q1,Q2,S0"
```
