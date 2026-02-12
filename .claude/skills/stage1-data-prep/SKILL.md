---
name: stage1-data-prep
description: 'Stage 1: Data Preparation - Load SPSS .sav file, extract metadata, transform and filter variables. Output: filtered_metadata.json. Use when starting analysis on new survey data.'
license: Apache-2.0
---

# Stage 1: Data Preparation

Load and prepare SPSS survey data for analysis.

## Overview

Executes **Steps 1-3** of the workflow:
- Step 1: Load .sav file
- Step 2: Extract metadata
- Step 3: Transform and filter metadata

## When to Use

Use this skill when:
- Starting analysis on a new SPSS file
- Need to extract variable metadata
- Preparing data for specification generation

## Usage

```
User: Prepare data from survey_data.sav

Assistant: [Step 1] Loading SPSS file...
           [Step 2] Extracting metadata (156 variables)...
           [Step 3] Transforming and filtering...

Complete! Output: filtered_metadata.json
```

## Input

| Input | Required | Description |
|--------|-----------|-------------|
| `.sav` file path | Yes | SPSS survey data file |

## Output

| File | Content |
|-------|----------|
| `filtered_metadata.json` | Variables, labels, value ranges, types |

## Library Modules

- `spss_analyzer.io.SPSSReader` - Read .sav files
- `spss_analyzer.io.MetadataTransformer` - Transform/filter metadata
