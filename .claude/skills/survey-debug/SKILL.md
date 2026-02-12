---
name: survey-debug
description: 'Survey Analysis Debugging & Testing - Test skills, validate data flows, debug issues. Use when investigating problems, testing workflows, or debugging data processing.'
license: Apache-2.0
---

# Survey Debug - Debugging & Testing

Dedicated skill for testing and debugging the survey analysis workflow.

## Overview

The survey analysis workflow consists of multiple stages and library modules. When things don't work as expected, use this skill to:

- **Test individual skills** in isolation
- **Validate data flow** between stages
- **Debug library functions** with test data
- **Inspect intermediate outputs** (JSON, CSV files)
- **Run full pipeline** with detailed logging
- **Performance testing** for large datasets

## When to Use

Use this skill when:
- A skill produces unexpected output or errors
- Data flow breaks between stages
- Need to inspect intermediate files
- Testing library function changes
- Debugging data transformation issues
- Validating before full analysis run

## Usage

### Quick Test

```
User: Test Stage 1 data prep

Assistant: I'll test the stage1-data-prep skill...
[Loads sample data, runs validation, shows output]
```

### Debug Library Functions

```
User: Debug the SPSS reader function

Assistant: I'll test the survey_analyzer.io.SPSSReader class...
[Test with various file formats, check metadata extraction]
```

### Inspect Outputs

```
User: Show me the filtered_metadata.json

Assistant: [Reads and displays filtered_metadata.json]
```

### Full Pipeline Test

```
User: Run full analysis on survey_data.sav with debug mode

Assistant: Running full pipeline with --debug flag...
[Shows detailed progress for each step, logs all operations]
```

## Debugging Features

| Feature | Description |
|----------|-------------|
| **Skill Testing** | Test any skill by name with sample data |
| **Library Testing** | Test library functions directly with mock data |
| **Data Inspection** | View any intermediate file (JSON, CSV) |
| **Logging Control** | Enable/disable detailed logging |
| **Dry Run** | Validate pipeline without actual execution |

## Common Debugging Tasks

| Task | Command Example |
|-------|----------------|
| Test metadata extraction | `debug --test metadata` |
| Validate specification format | `debug --validate-spec` |
| Test PSPP syntax generation | `debug --test-pspp` |
| Inspect cross-tables | `debug --show-crosstabs` |
| Run single stage | `debug --run-stage 3` |
| Full pipeline with logging | `debug --run-pipeline --debug` |

## Testing Library Modules

Direct testing of library functions:

```python
# Example: Testing metadata transformer
from survey_analyzer.io import MetadataTransformer

transformer = MetadataTransformer()

# Test with empty metadata
result = transformer.filter_variables({})
assert result == {}, "Empty metadata should return empty"

# Test with various metadata formats
# ... more test cases
```

## Data Validation

Validate data at each stage:

| Stage | Validation Checks |
|-------|-------------------|
| Stage 1 | Metadata has required variables, valid labels |
| Stage 2 | Spec JSON has valid structure, all references exist |
| Stage 3 | Crosstabs have proper row/column variables, valid counts |
| Stage 4 | Statistics have valid p-values, degrees of freedom |
| Stage 5 | Reports have valid data sources |

## Error Recovery

When a stage fails:
1. Check error message
2. Identify root cause
3. Suggest fix action
4. Offer recovery options (retry, skip, continue)

## Implementation

This skill provides debugging tools without modifying production skills:

- Uses library modules directly
- Creates test data when needed
- Validates outputs without changing pipeline
- Logs all operations for investigation
- Can run in "dry-run" mode for safe testing
