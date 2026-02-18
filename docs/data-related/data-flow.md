# Data Flow

This document describes the simplified workflow design for the Survey Analysis & Visualization system using a **Pure Python Library + Claude Code Skills** architecture.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Architecture](#2-architecture)
3. [Data Flow](#3-data-flow)
4. [Table Specification](#4-table-specification)
5. [Workflow Steps](#5-workflow-steps)
6. [Key Terminology](#6-key-terminology)

---

## 1. Overview

### 1.1 Purpose

Design and implement an automated workflow for market research survey data analysis and visualization using a **Python library** orchestrated by **Claude Code Skills**. The system processes PSPP survey data, applies AI-orchestrated transformations, generates indicators, performs statistical analysis, and produces outputs in PowerPoint and HTML formats.

### 1.2 Scope

| Aspect | Description |
|--------|-------------|
| **Input** | PSPP (.sav) survey data files |
| **Processing** | AI-orchestrated recoding, transformation, and indicator generation |
| **Output** | PowerPoint presentations, HTML dashboards with visualizations |
| **Target** | Market research industry professionals |

### 1.3 Key Objectives

| Objective | Description |
|-----------|-------------|
| **Simplicity** | Single consolidated artifact for all AI-generated specifications |
| **Modularity** | Pure Python library separate from AI orchestration |
| **Flexibility** | Handle various survey structures and question types |
| **Accuracy** | Maintain statistical rigor with significance testing |
| **Presentation** | Deliver insights through multiple formats (PPT, HTML) |

---

## 2. Architecture

### 2.1 Component Structure

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Claude Code Skills                          │
│  (AI Orchestration & Coordination)                            │
└────────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    survey_analyzer Library                        │
│  (Pure Python: Data Processing & Computation)                    │
├─────────────────────────────────────────────────────────────────────────┤
│ specification/  │ Schema & validator for table_specification.json      │
│ io/             │ SPSS file I/O and metadata handling                │
│ analysis/         │ Cross-tabulation, statistics, and indicators        │
│ filtering/        │ Significance filtering                                  │
│ reporting/        │ PowerPoint and HTML generation                       │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Skill Responsibilities

| Skill | Stage | Purpose | Type |
|--------|---------|-----------|------|
| **stage1-data-prep** | 1 | Load .sav, extract/filter metadata | Deterministic |
| **stage2-spec-gen** | 2 | Generate/validate table specification (AI-orchestrated) | AI |
| **stage3-crosstabs** | 3 | Recoding, cross-tabulation, statistics calculation | Deterministic |
| **stage4-statistics** | 4 | Significance filtering | Deterministic |
| **stage5-reports** | 5 | PowerPoint, HTML dashboard | Deterministic |
| **survey-coordinator** | All | Orchestrate complete 5-stage pipeline | Coordinator |

---

## 3. Data Flow

The workflow consists of **13 steps** organized into **5 stages**:

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
        S3["Step 3<br/>Transform & Filter Metadata"]:::processingGreen
        metadata[("filtered_metadata")]:::artifactStyle
    end

    %% STAGE 2: Table Specification
    subgraph STAGE2[" "]
        direction TB
        stage2_label["**STAGE 2: Table Specification**"]:::stageLabelStyle

        excel[("table-specification.xlsx")]:::artifactStyle
        S4["Step 4<br/>Generate Table Specification<br/>(Skill: AI-orchestrated)"]:::processingBlue
        S5["Step 5<br/>Validate Specification"]:::processingOrange
        S6["Step 6<br/>Review & Approve"]:::processingPurple
        tableSpec[("table_specification.jsonc")]:::artifactStyle
    end

    %% STAGE 3: Cross-Tabulation Generation
    subgraph STAGE3[" "]
        direction TB
        stage3_label["**STAGE 3: Cross-Tabulation Generation**"]:::stageLabelStyle

        S7["Step 7<br/>Apply Recoding<br/>& Transformations"]:::processingGreen
        S8["Step 8<br/>Generate Cross-Tables<br/>with Statistics"]:::processingGreen
        S9["Step 9<br/>Export Tables + Statistics"]:::processingGreen
        crosstabs[("cross_tables_with_stats.json")]:::artifactStyle
    end

    %% STAGE 4: Statistical Filtering
    subgraph STAGE4[" "]
        direction TB
        stage4_label["**STAGE 4: Statistical Filtering**"]:::stageLabelStyle

        S10["Step 10<br/>Filter by Significance<br/>(p-value < 0.05)"]:::processingGreen
        S11["Step 11<br/>Generate Summary Report"]:::processingGreen
        results[("filtered_tables<br/>statistical_summary")]:::artifactStyle
    end

    %% STAGE 5: Reporting
    subgraph STAGE5[" "]
        direction TB
        stage5_label["**STAGE 5: Reporting**"]:::stageLabelStyle

        S12["Step 12<br/>Generate PowerPoint"]:::processingGreen
        S13["Step 13<br/>Generate HTML Dashboard"]:::processingGreen
        outputs[("presentation.pptx<br/>dashboard.html")]:::artifactStyle
    end

    %% Data flow edges
    S1 --> S2 --> S3 --> metadata
    metadata ==> S4
    excel ==> S4
    S4 --> S5
    S5 -->|Valid| S6
    S5 -.->|Invalid| S4
    S6 -->|Approve| tableSpec
    S6 -.->|Reject| S4

    tableSpec ==> S7 --> S8 --> S9 --> crosstabs

    crosstabs ==> S10 --> S11 --> results

    results ==> S12 --> ppt
    results ==> S13 --> html
```

**Legend:**

| Shape | Meaning |
|-------|---------|
| `Rectangle` | **Processing Node** (Action/Step) |
| `Cylinder` | **Data Artifact** (Output/File) |

| Color | Meaning | Examples |
|-------|---------|----------|
| 🔵 **Blue** | AI-Orchestrated Processing (Skill generates artifact) | Step 4 |
| 🟢 **Green** | Deterministic Processing (Python library: pandas, scipy, numpy) | Steps 1-3, 7-13 |
| 🟠 **Orange** | Validation (Python checks syntax/references) | Step 5 |
| 🟣 **Purple** | Review (Human validates semantic quality) | Step 6 |
| 🟡 **Yellow** | Data Artifacts (Files and outputs) | `.sav`, `.json`, `.pptx`, `.html` |

**Line Styles:**
- `-->` Solid line: Forward flow to next step
- `==>` Thick line: Major data flow between stages
- `-.->` Dotted line: Feedback loop (validation/review triggering regeneration)

### 3.2 Stage Descriptions

| Stage | Steps | Description | Input | Output |
|-------|--------|-------------|-------|--------|
| **1** | 1-3 | Load data, extract/transform/filter metadata | .sav file | `filtered_metadata.json` |
| **2** | 4-6 | Generate, validate, review table specification (AI-orchestrated) | `filtered_metadata.json` + `table-specification.xlsx` | `table_specification.jsonc` |
| **3** | 7-9 | Apply transformations, generate cross-tables with statistics | `table_specification.jsonc` | `cross_tables_with_stats.json` |
| **4** | 10-11 | Filter tables by significance, generate summary | `cross_tables_with_stats.json` | `filtered_tables.json`, `statistical_summary.json` |
| **5** | 12-13 | Generate PowerPoint and HTML dashboard | Filtered results | `presentation.pptx`, `dashboard.html` |

---

## 4. Table Specification

The **table_specification.jsonc** is a consolidated artifact generated from `filtered_metadata.json` and user-edited `table-specification.xlsx`.

### 4.1 Structure

```jsonc
{
  "spec_id": "crosstab_2024_consumer_survey_001",
  "project_id": "proj_2024_china_consumer_insights",
  "dataset_id": "ds_q1_2024_national_survey",
  "description": "Cross-tabulation analysis for market research survey",

  "filter_clause": {
    "age_min": 18,
    "age_max": 65,
    "exclude_incomplete": true
  },

  "weight_indicator": "weight1",

  "row_indicators": [
    {
      "indicator_code": "Q1_GENDER_RAW",
      "question_code": "Q1",
      "question_description": "Gender",
      "question_label": "请问您的性别是？(单选)",
      "question_type": "Single Choice",
      "source_variables": ["Q1_GENDER"],
      "transformation_rules": null,
      "statistic_type": "categorical"
    }
  ],

  "column_indicators": [
    {
      "indicator_code": "GENDER",
      "question_code": "Q1",
      "question_description": "Gender",
      "question_label": "性别",
      "question_type": "Single Choice",
      "source_variables": ["GENDER"],
      "explicit": ["1", "2"],
      "transformation_rules": null,
      "statistic_type": "categorical"
    }
  ]
}
```

### 4.2 Field Descriptions

| Field | Description | Source |
|-------|-------------|--------|
| `spec_id`, `project_id`, `dataset_id` | Project identification | Excel Metadata sheet |
| `filter_clause` | Data filtering rules | Excel Metadata sheet |
| `weight_indicator` | Weight variable name | Excel Weight Indicator sheet |
| `indicator_code` | Internal variable identifier | Generated |
| `question_code` | SPSS variable prefix (Q1, S1, D1) | Excel Question Code column |
| `question_description` | Concise English label | Excel Question Description column |
| `question_label` | Full Chinese question text | filtered_metadata.json |
| `question_type` | Single Choice, Multiple Choice, Matrix, etc. | Excel Question Type dropdown |
| `source_variables` | Real SPSS variable names | Mapped from question_code + metadata |
| `transformation_rules` | PSPP recoding syntax | Excel Transformation Rules column |
| `statistic_type` | categorical or scalar | Excel Statistic Type column |

### 4.3 Transformation Rules Format

The `transformation_rules` field uses a simplified syntax that Python translates into pandas operations:

| Format | Example | Description |
|--------|---------|-------------|
| Single value | `(3=2)` | Recode value 3 to 2 |
| Range | `(1 THRU 3=99)` | Recode values 1-3 to 99 |
| Multiple rules | `(1=1)(2=2)(3 THRU 5=99)` | Chain multiple recoding rules |
| Compute | `COMPUTE var = a + b` | Calculate new variable |
| Null | `null` | No transformation |

**Example:**
```jsonc
"transformation_rules": "(1 THRU 2=1) (3=2) (4 THRU 5=3)"
```

Python implementation using pandas:
```python
import pandas as pd

# Parse transformation rules and apply
def apply_recode(series, rules):
    # Parse "(1 THRU 2=1) (3=2) (4 THRU 5=3)"
    # Apply using pandas map/cut
    return recoded_series
```

---

## 5. Workflow Steps

### Stage 1: Data Preparation (Steps 1-3)

| Step | Skill | Module | Purpose | Type |
|------|--------|---------|------|
| 1 | `stage1-data-prep` | `survey_analyzer.io.SPSSReader` | Load .sav file | Deterministic |
| 2 | `stage1-data-prep` | `survey_analyzer.io.MetadataTransformer` | Extract & transform metadata | Deterministic |
| 3 | `stage1-data-prep` | `survey_analyzer.io.MetadataTransformer` | Filter variables | Deterministic |

**Skill:** `stage1-data-prep` handles all Stage 1 operations.

**Output:** `filtered_metadata.json`

### Stage 2: Table Specification (Steps 4-6)

| Step | Skill | Purpose | Type |
|------|--------|---------|------|
| 4 | `stage2-spec-gen` | Generate table_specification.jsonc (AI-orchestrated) | AI |
| 5 | `stage2-spec-gen` | Validate specification | Validation |
| 6 | Human review via skill interaction | Approve/reject specification | Review |

**Skill:** `stage2-spec-gen` handles all Stage 2 operations.

**Inputs:**
- `filtered_metadata.json` (from Stage 1)
- `table-specification.xlsx` (user-edited Excel file)

**Output:** `table_specification.jsonc`

**Why AI Agent?**
- Requires intelligent interpretation of user selections from Excel
- Mapping question codes (Q1, S1) to real variable names from metadata
- Understanding transformation rule descriptions and converting to PSPP syntax
- Validating semantic correctness of the specification

**Feedback Loop:** If validation fails or review rejects, regenerate from Step 4.

### Stage 3: Cross-Tabulation Generation (Steps 7-9)

| Step | Skill | Module | Purpose | Type |
|------|--------|---------|------|
| 7 | `stage3-crosstabs` | `survey_analyzer.analysis.TransformationEngine` | Apply recoding and transformation rules | Deterministic |
| 8 | `stage3-crosstabs` | `survey_analyzer.analysis.CrossTabGenerator` | Generate cross-tables with chi-square and Cramer's V | Deterministic |
| 9 | `stage3-crosstabs` | `survey_analyzer.analysis.ResultsExporter` | Export tables + statistics to JSON | Deterministic |

**Skill:** `stage3-crosstabs` handles all Stage 3 operations.

**Input:** `table_specification.jsonc`

**Outputs:**
- `cross_tables_with_stats.json` (cross-tables + chi-square + Cramer's V)

**Python Implementation:**
```python
import pandas as pd
from scipy.stats import chi2_contingency
import numpy as np

# Step 7: Apply transformations
def apply_transformations(df, indicators):
    for indicator in indicators:
        if indicator['transformation_rules']:
            # Parse and apply recoding rules
            df[indicator['indicator_code']] = recode(
                df[indicator['source_variables']],
                indicator['transformation_rules']
            )

# Step 8: Generate cross-tabs with statistics
def generate_crosstab_with_stats(row_var, col_var, weight_var=None):
    # Create contingency table
    crosstab = pd.crosstab(
        index=df[row_var],
        columns=df[col_var],
        values=df[weight_var] if weight_var else None,
        aggfunc='sum' if weight_var else 'count',
        margins=True,
        normalize='columns'  # Column percentages
    )

    # Calculate chi-square test
    chi2, p_value, dof, expected = chi2_contingency(crosstab)

    # Calculate Cramer's V (effect size)
    n = crosstab.sum().sum()
    min_dim = min(crosstab.shape[0]-1, crosstab.shape[1]-1)
    cramers_v = np.sqrt(chi2 / (n * min_dim))

    return {
        'crosstab': crosstab.to_dict(),
        'statistics': {
            'chi_square': float(chi2),
            'p_value': float(p_value),
            'degrees_of_freedom': int(dof),
            'cramers_v': float(cramers_v)
        }
    }
```

**Dependencies:**
- `pandas` - Data manipulation and cross-tabulation
- `scipy` - Chi-square statistical test
- `numpy` - Numerical operations for Cramer's V
- `pyreadstat` - Reading SPSS (.sav) files

**Why Pure Python?**
- No external PSPP dependency required
- Easier deployment and CI/CD
- Full control over statistical calculations
- Python-native error handling and debugging

### Stage 4: Statistical Filtering (Steps 10-11)

| Step | Skill | Module | Purpose | Type |
|------|--------|---------|------|
| 10 | `stage4-statistics` | `survey_analyzer.filtering.SignificanceFilter` | Filter tables by p-value < 0.05 | Deterministic |
| 11 | `stage4-statistics` | `survey_analyzer.reporting.SummaryGenerator` | Generate statistical summary | Deterministic |

**Skill:** `stage4-statistics` handles all Stage 4 operations.

**Input:** `cross_tables_with_stats.json` (from Stage 3)

**Processing:**
```python
def filter_significance(tables_with_stats, alpha=0.05):
    """Filter tables by p-value threshold"""
    significant = []
    for table in tables_with_stats:
        p_value = table['statistics']['p_value']
        table['is_significant'] = p_value < alpha
        if table['is_significant']:
            significant.append(table)
    return significant, tables_with_stats  # Return both filtered and all
```

**Outputs:**
- `filtered_tables.json` (only significant tables, p-value < 0.05)
- `statistical_summary.json` (chi-square, p-value, Cramer's V for all tables)

**Why Direct Programming?**
- Simple filtering by p-value threshold
- Statistical calculations already completed in Stage 3
- Pure Python list comprehension filtering

### Stage 5: Reporting (Steps 12-13)

| Step | Skill | Module | Purpose | Type |
|------|--------|---------|------|
| 12 | `stage5-reports` | `survey_analyzer.reporting.PowerPointGenerator` | Create .pptx | Deterministic |
| 13 | `stage5-reports` | `survey_analyzer.reporting.HTMLDashboardGenerator` | Create .html | Deterministic |

**Skill:** `stage5-reports` handles all Stage 5 operations.

**Outputs:** `presentation.pptx`, `dashboard.html`

---

## 6. Key Terminology

| Term | Definition |
|------|------------|
| **Table Specification (JSONC)** | Consolidated JSONC artifact containing row/column indicators with transformation rules |
| **Excel Specification** | User-friendly `table-specification.xlsx` for editing indicators, metadata, and settings |
| **question_code** | SPSS variable prefix (Q1, Q2, S1, S2, D1, D2) from Excel |
| **question_label** | Full Chinese question text from `filtered_metadata.json` |
| **question_description** | Concise English label from Excel |
| **question_type** | Single Choice, Multiple Choice, Matrix, Numeric Input, Rating Scale (dropdown in Excel) |
| **transformation_rules** | Simplified recoding syntax translated to pandas operations (e.g., "(1 THRU 3=99) (4=100)") |
| **statistic_type** | `categorical` (column percent) or `scalar` (mean, median, min, max) |
| **cross_tables_with_stats.json** | Python-generated output with cross-tables, chi-square, p-value, Cramer's V |
| **filtered_tables.json** | Tables that passed significance test (p-value < 0.05) |
| **statistical_summary.json** | Summary report with all chi-square and Cramer's V statistics |
| **AI-orchestrated step** | Workflow step where Skill uses AI to generate content (Stage 2 only) |
| **Deterministic processing** | Pure Python functions with predictable outputs (All stages except Stage 2) |
| **Skill orchestration** | Claude Code Skills coordinating library module execution |
| **Specification validation** | Checking JSONC structure, variable references, and business logic |

---

## Related Documents

| Document | Content |
|----------|---------|
| **[project-structure.md](./project-structure.md)** | Complete directory structure and file locations |
| **[system-architecture.md](./system-architecture.md)** | System components, deployment, and troubleshooting |
| **[technology-stack.md](./technology-stack.md)** | Technologies and versions |
| **[System Configuration](./system-configuration.md)** | Configuration options and usage examples |
| **[features-and-usage.md](./features-and-usage.md)** | Product introduction for end users |
| **[web-interface.md](./web-interface.md)** | Agent Chat UI setup and usage |
