---
name: analyzer-debug
description: 'Survey Analysis Debugging & Testing - Test skills, validate data flows, debug issues. Use when investigating problems, testing workflows, or debugging data processing.'
license: Apache-2.0
---

# Analyzer Debug

Testing and debugging utilities for survey analysis workflow.

## Overview

Provides debugging and testing capabilities for:
- Individual stage skills
- Data flow validation
- Intermediate file inspection
- Error diagnosis and recovery

## When to Use

Use this skill when:
- A stage produces unexpected output
- Need to inspect intermediate files
- Testing library functions directly
- Debugging data transformations

## Usage

```
User: Debug Stage 3 crosstabs

Assistant: [Debug Mode] Testing Stage 3...
           Loading cross_tables.json...
           Tables: 20 found
           Validating table structures...
           Table 001: ✓ Valid
           Table 002: ⚠ Warning - counts array is empty for variable S5X1E
           Validation complete!
```

## Debug Features

| Feature | Description |
|---------|-------------|
| **Stage Testing** | Test individual stages in isolation |
| **Data Inspection** | View JSON outputs (tables, indicators, metadata) |
| **Validation** | Check data structures and formats |
| **Logging** | Enable detailed logging for operations |
| **Dry Run** | Validate pipeline without actual execution |

## Library Modules

| Module | Purpose |
|---------|---------|
| `survey_analyzer.io.SPSSReader` | Test SPSS file reading |
| `survey_analyzer.io.MetadataTransformer` | Test metadata transformation |
| `survey_analyzer.specification.SpecificationGenerator` | Test spec generation |

## Output Files

| File | Purpose |
|-------|----------|
| `output/cross_tables.json` | Debug log of Stage 3 output |
| `output/filtered_tables.json` | Debug log of Stage 4 output |
| `output/dashboard.html` | Inspect generated dashboard |
