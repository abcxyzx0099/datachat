---
name: analyzer-data-prep
description: Stage 1: Data Preparation - Load SPSS (.sav) files and extract metadata using the survey_analyzer library. Outputs filtered_metadata.json for table specification generation.
---

# Analyzer Data Preparation

> **Stage 1: Data Preparation** - Load SPSS files and extract metadata using `survey_analyzer` library

## Overview

This skill guides you through using the **`survey_analyzer` library** to prepare SPSS survey data for analysis. The library provides:

| Component | Module | Purpose |
|-----------|--------|---------|
| **SPSSReader** | `survey_analyzer.io.reader` | Read SPSS (.sav) files |
| **MetadataTransformer** | `survey_analyzer.io.metadata` | Transform and filter variables |

**Output**: `filtered_metadata.json` - Ready for Stage 2 (Table Specification)

---

## Quick Start

### Natural Language

```
"Prepare metadata from survey.sav"
"Load and extract SPSS metadata for analysis"
"Process survey data and filter variables"
```

### Using the Library

```python
from survey_analyzer.io import SPSSReader
from survey_analyzer.io.metadata import MetadataTransformer
import json

# Step 1: Read SPSS file
reader = SPSSReader(encoding="UTF-8")
df, metadata = reader.read("data/survey.sav")

# Step 2: Transform to variable-centered format
transformer = MetadataTransformer()
variable_metadata = transformer.to_variable_centered(metadata)

# Step 3: Filter variables by business rules
filtered_metadata = transformer.filter_variables(
    variable_metadata,
    min_categories=2,
    max_categories=30  # Per business rules
)

# Step 4: Get analysis-ready variables
analysis_vars = transformer.get_analysis_variables(filtered_metadata)

# Step 5: Save output
output = {
    "file_info": {
        "path": "data/survey.sav",
        "case_count": len(df) if df is not None else 0,
    },
    "variables": {k: v for k, v in filtered_metadata.items() if k in analysis_vars},
    "variable_names": analysis_vars
}

with open("output/filtered_metadata.json", "w") as f:
    json.dump(output, f, indent=2)
```

---

## Library Reference

### SPSSReader

```python
from survey_analyzer.io import SPSSReader

reader = SPSSReader(
    encoding="UTF-8",           # File encoding
    apply_value_formats=False   # Keep raw values
)

# Read file with data
df, metadata = reader.read("survey.sav")

# Read metadata only (faster for large files)
df, metadata = reader.read("survey.sav", metadata_only=True)
```

**Returns:**
| Element | Description |
|---------|-------------|
| `df` | pandas DataFrame with data (None if metadata_only=True) |
| `metadata` | Dict with file_name, file_label, variable_labels, value_labels |

### MetadataTransformer

```python
from survey_analyzer.io.metadata import MetadataTransformer

transformer = MetadataTransformer()

# Convert to variable-centered format
variable_metadata = transformer.to_variable_centered(metadata)

# Filter variables by category count
filtered = transformer.filter_variables(
    variable_metadata,
    min_categories=2,      # Minimum categories
    max_categories=30,     # Maximum categories (business rules)
    include_patterns=[r"^q\d+"],  # Optional: regex include
    exclude_patterns=[r".*_other$"]  # Optional: regex exclude
)

# Get variables suitable for cross-tabulation
analysis_vars = transformer.get_analysis_variables(filtered)
```

---

## Business Rules (from docs/application-design/business-rules.md)

### Filtering Rules

| Rule | Condition | Default |
|------|-----------|---------|
| **Binary Variables** | Exactly 2 distinct values | Filter (no recoding needed) |
| **High Cardinality** | Distinct values > 30 | Filter |
| **Other Text Fields** | Name contains "other" AND type is string | Filter |

### Configuration Parameters

| Parameter | Default | Source |
|-----------|---------|--------|
| `cardinality_threshold` | **30** | business-rules.md |
| `max_categories` | **30** | Applied in filter_variables() |

---

## Complete Example Script

```python
#!/usr/bin/env python3
"""
Stage 1: Data Preparation
Uses survey_analyzer library to prepare SPSS data for analysis.
"""

from pathlib import Path
from survey_analyzer.io import SPSSReader
from survey_analyzer.io.metadata import MetadataTransformer
import json

def prepare_data(
    sav_file: str,
    output_dir: str = "output/",
    cardinality_threshold: int = 30
):
    """
    Prepare SPSS data for analysis.

    Args:
        sav_file: Path to SPSS (.sav) file
        output_dir: Output directory for results
        cardinality_threshold: Max distinct values (default: 30 per business rules)
    """
    # Read SPSS file
    reader = SPSSReader()
    df, metadata = reader.read(sav_file)

    # Transform metadata
    transformer = MetadataTransformer()
    variable_metadata = transformer.to_variable_centered(metadata)

    # Filter by business rules
    filtered = transformer.filter_variables(
        variable_metadata,
        min_categories=2,
        max_categories=cardinality_threshold
    )

    # Get analysis variables
    analysis_vars = transformer.get_analysis_variables(filtered)

    # Build output
    output = {
        "file_info": {
            "path": str(Path(sav_file).absolute()),
            "name": Path(sav_file).name,
            "case_count": len(df) if df is not None else 0,
        },
        "variables": {k: v for k, v in filtered.items() if k in analysis_vars},
        "variable_names": analysis_vars,
        "summary": {
            "total_variables": len(variable_metadata),
            "filtered_variables": len(filtered),
            "analysis_variables": len(analysis_vars),
        }
    }

    # Save output
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    with open(output_path / "filtered_metadata.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"✓ Processed {len(analysis_vars)} variables")
    print(f"✓ Output: {output_path / 'filtered_metadata.json'}")

    return output

if __name__ == "__main__":
    prepare_data("data/survey.sav")
```

---

## Output Format

### filtered_metadata.json

```json
{
  "file_info": {
    "path": "/path/to/survey.sav",
    "name": "survey.sav",
    "case_count": 13064
  },
  "variables": {
    "q1": {
      "label": "Question 1: Satisfaction",
      "value_labels": {
        "1": "Very Dissatisfied",
        "2": "Somewhat Dissatisfied",
        "3": "Neutral",
        "4": "Somewhat Satisfied",
        "5": "Very Satisfied"
      },
      "variable_type": "ordinal"
    }
  },
  "variable_names": ["q1", "q2", "q3", "gender", "age"],
  "summary": {
    "total_variables": 376,
    "filtered_variables": 150,
    "analysis_variables": 95
  }
}
```

---

## Test Data

This project includes real survey data for testing:

| File | Size | Location |
|------|------|----------|
| **real-data.sav** | 9.6 MB | `data/real-data.sav` |
| **simple-data.sav** | 3.6 KB | `data/simple-data.sav` |

**Example with test data:**
```python
from survey_analyzer.io import SPSSReader

# Use provided test data
df, metadata = SPSSReader().read("data/real-data.sav")
```

---

## Dependencies

Ensure the `survey_analyzer` package is installed:

```bash
# Development install (from project root)
pip install -e ./survey_analyzer

# Or install required packages directly
pip install pyreadstat pandas
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ImportError: pyreadstat` | Install with `pip install pyreadstat` |
| `EncodingError` | Try different encoding: `SPSSReader(encoding="Latin-1")` |
| Empty filtered_metadata | Adjust `max_categories` threshold |
| No analysis variables | Check that variables have value labels |

---

## Related Skills

| Skill | Next Stage |
|-------|------------|
| `analyzer-tablespec-gen` | Stage 2: Table Specification (uses filtered_metadata.json) |

---

## Library Documentation

Full API documentation: `survey_analyzer/src/survey_analyzer/io/`
