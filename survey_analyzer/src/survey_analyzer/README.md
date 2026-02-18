# SPSS Analyzer Library

A reusable Python library for SPSS survey data analysis, extracted from the DataChat LangGraph workflow.

## Overview

This library provides **pure Python** functions for analyzing SPSS survey data that can be called from:
- Python scripts
- CLI commands
- LangGraph nodes (via skill wrappers)
- Web applications (FastAPI)
- Other applications

## Pure Python Implementation (No PSPP Dependency)

This library uses pure Python for all computations:
- **pandas** for data manipulation and cross-tabulation
- **scipy.stats** for chi-square statistical testing
- **numpy** for numerical operations

No external PSPP binary required!

## Library Structure

```
lib/survey_analyzer/
├── __init__.py              # Package initialization
├── analysis/                # Core analysis functions
│   ├── __init__.py
│   ├── statistics.py        # Chi-square, Cramer's V calculator
│   ├── transformation.py    # Variable recoding with pandas (NEW)
│   ├── crosstab.py          # Cross-tabulation with statistics (NEW)
│   └── indicators.py        # Indicator generation from variables
├── filtering/               # Statistical significance filtering
│   ├── __init__.py
│   └── significance.py      # Filter tables by p-value, Cramer's V
├── io/                      # SPSS file I/O
│   ├── __init__.py
│   ├── reader.py            # SPSS file reader (pyreadstat wrapper)
│   └── metadata.py          # Metadata transformation utilities
├── reporting/               # Report generation
│   ├── __init__.py
│   ├── powerpoint.py        # PowerPoint presentation generator
│   └── dashboard.py         # HTML dashboard generator
├── specification/           # Table specification schema and validator
│   ├── __init__.py
│   ├── schema.py            # Data models for table specifications
│   └── validator.py         # Specification validation
└── examples/
    └── demo.py              # Demo and test script
```

## Implemented Modules

### 1. Statistics Calculator (`analysis/statistics.py`)

Computes statistical tests for cross-tabulation tables:
- Chi-square test of independence
- Cramer's V effect size
- Effect size interpretation (negligible, small, medium, large)
- Statistical significance testing
- Test validation (assumptions checking)

```python
from survey_analyzer.analysis import StatisticsCalculator

calc = StatisticsCalculator(significance_level=0.05)
result = calc.analyze_table(
    counts=[[45, 32], [52, 28]],
    row_labels=["Male", "Female"],
    column_labels=["Yes", "No"]
)
print(f"Chi-square: {result.chi_square:.4f}")
print(f"p-value: {result.p_value:.4f}")
print(f"Cramer's V: {result.cramers_v:.4f}")
```

### 2. Transformation Engine (`analysis/transformation.py`) ✨ NEW

Apply variable recoding and transformations using pandas:
- Parse PSPP-style recoding rules: `(1 THRU 2=1) (3=2)`
- Range mapping and value recoding
- COMPUTE expressions for calculated variables
- Batch transformation from indicator specifications

```python
from survey_analyzer.analysis import TransformationEngine, apply_recode

# Single variable recoding
recoded = apply_recode(df['age'], "(1 THRU 2=1) (3=2) (4 THRU 5=3)")

# Batch transformation
engine = TransformationEngine()
df_transformed = engine.apply_transformations(df, indicators)
```

### 3. Cross-Tabulation Generator (`analysis/crosstab.py`) ✨ NEW

Generate cross-tabulation tables with statistical tests:
- Cross-tabulation with pandas.crosstab()
- Chi-square test via scipy.stats.chi2_contingency
- Cramer's V effect size calculation
- Weight variable support
- Batch generation from indicator specifications

```python
from survey_analyzer.analysis import CrossTabGenerator, generate_crosstab

# Single table
result = generate_crosstab(df, "gender", "satisfaction", weight_var="weight")
print(f"p-value: {result['statistics']['p_value']:.4f}")

# Batch generation
generator = CrossTabGenerator()
results = generator.generate_batch(df, table_pairs)
```

### 4. Indicator Generator (`analysis/indicators.py`)

Generate indicator groupings from SPSS metadata:
- Keyword-based grouping
- Label-based grouping
- Manual groupings
- LLM-based semantic grouping (placeholder)

### 5. Significance Filter (`filtering/significance.py`)

Filter tables by statistical significance criteria:
- P-value threshold filtering
- Cramer's V minimum effect size
- Table validity checking
- Batch filtering with summary reports

### 6. SPSS I/O (`io/`)

Read SPSS (.sav) files and extract metadata:
- SPSS file reading with pyreadstat
- Metadata transformation to variable-centered format
- Variable filtering by business rules

### 7. Reporting (`reporting/`)

Generate output reports:
- PowerPoint presentations with tables and charts
- Interactive HTML dashboards with Chart.js

### 8. Table Specification (`specification/`)

Schema and validator for table specification documents:
- Pydantic data models
- Validation rules
- Error reporting

## Quick Start

### Installation

```bash
# From project root
cd /home/admin/workspaces/datachat
pip install -e ./survey_analyzer

# Or install dependencies directly
pip install pandas pyreadstat scipy numpy python-pptx
```

### Basic Usage

```python
import pandas as pd
from survey_analyzer.io import SPSSReader
from survey_analyzer.analysis import TransformationEngine, CrossTabGenerator
from survey_analyzer.filtering import filter_significant

# 1. Read SPSS file
reader = SPSSReader()
df, metadata = reader.read("survey.sav")

# 2. Apply transformations
engine = TransformationEngine()
indicators = [
    {'indicator_code': 'age_group', 'source_variables': ['age'],
     'transformation_rules': '(1 THRU 30=1) (31 THRU 50=2) (51 THRU HI=3)'}
]
df_transformed = engine.apply_transformations(df, indicators)

# 3. Generate cross-tabs with statistics
generator = CrossTabGenerator()
result = generator.generate(df_transformed, "gender", "satisfaction")

# 4. Filter by significance
if result.statistics['p_value'] < 0.05:
    print("Significant association found!")
```

## Module Status

| Module | File | Status | Notes |
|--------|------|--------|-------|
| 1. I/O | `io/reader.py`, `io/metadata.py` | ✅ Complete | Read .sav files |
| 2. Statistics | `analysis/statistics.py` | ✅ Complete | Chi-square, Cramer's V |
| 3. Transformation | `analysis/transformation.py` | ✅ Complete | Recoding with pandas |
| 4. Cross-Tabs | `analysis/crosstab.py` | ✅ Complete | Crosstabs with scipy |
| 5. Filtering | `filtering/significance.py` | ✅ Complete | P-value filtering |
| 6. PowerPoint | `reporting/powerpoint.py` | ✅ Complete | PPTX generation |
| 7. HTML Dashboard | `reporting/dashboard.py` | ✅ Complete | Interactive HTML |
| 8. Indicators | `analysis/indicators.py` | ✅ Complete | Variable grouping |
| 9. Specification | `specification/` | ✅ Complete | Schema & validator |

## Dependencies

Core dependencies:
- `pandas>=2.0.0` - Data manipulation
- `pyreadstat>=1.2.0` - SPSS file reading
- `scipy>=1.10.0` - Statistical tests
- `numpy>=1.24.0` - Numerical operations
- `python-pptx>=0.6.21` - PowerPoint generation

Optional dev dependencies:
- `pytest>=7.0.0` - Testing
- `ruff>=0.1.0` - Linting
- `mypy>=1.0.0` - Type checking

## License

MIT License - See LICENSE file for details
