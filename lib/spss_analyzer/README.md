# SPSS Analyzer Library

A reusable Python library for SPSS survey data analysis, extracted from the DataChat LangGraph workflow.

## Overview

This library provides standalone functions for analyzing SPSS survey data that can be called from:
- Python scripts
- CLI commands
- LangGraph nodes (via skill wrappers)
- Other applications

## Library Structure

```
lib/spss_analyzer/
├── __init__.py              # Package initialization
├── analysis/                # Core analysis functions
│   ├── __init__.py
│   ├── statistics.py        # Chi-square, Cramer's V calculator
│   └── indicators.py        # Indicator generation from variables
├── filtering/               # Statistical significance filtering
│   ├── __init__.py
│   └── significance.py      # Filter tables by p-value, Cramer's V
├── io/                      # SPSS file I/O
│   ├── __init__.py
│   ├── reader.py            # SPSS file reader (pyreadstat wrapper)
│   └── metadata.py          # Metadata transformation utilities
├── pspp/                    # PSPP integration
│   ├── __init__.py
│   ├── syntax.py            # PSPP syntax generators
│   └── executor.py          # PSPP execution wrapper
├── reporting/               # Report generation
│   ├── __init__.py
│   ├── powerpoint.py        # PowerPoint presentation generator
│   └── dashboard.py         # HTML dashboard generator
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
from spss_analyzer.analysis import StatisticsCalculator

calc = StatisticsCalculator(significance_level=0.05)
result = calc.analyze_table(
    counts=[[45, 32], [52, 28]],
    row_labels=["Male", "Female"],
    column_labels=["Yes", "No"]
)

print(f"χ² = {result.chi_square:.4f}")
print(f"p = {result.p_value:.4f}")
print(f"V = {result.cramers_v:.4f} ({result.interpretation})")
print(f"Significant: {result.is_significant}")
```

### 2. Indicator Generator (`analysis/indicators.py`)

Groups related variables into indicators for combined analysis:
- Keyword-based grouping (sat_1, sat_2 → satisfaction indicator)
- Label-based grouping (semantic similarity)
- Manual grouping (predefined groups)

```python
from spss_analyzer.analysis import IndicatorGenerator, IndicatorConfig, IndicatorType

gen = IndicatorGenerator()
config = IndicatorConfig(
    type=IndicatorType.KEYWORD,
    prefix="sat_",
    min_variables=2
)
indicators = gen.generate(metadata, config)

for ind in indicators:
    print(f"{ind.name}: {ind.variables}")
```

### 3. Significance Filter (`filtering/significance.py`)

Filters tables based on statistical significance criteria:
- P-value threshold (default: p < 0.05)
- Cramer's V threshold (default: V >= 0.1)
- Validity requirement (excludes tests with violated assumptions)

```python
from spss_analyzer.filtering import SignificanceFilter, FilterCriteria

criteria = FilterCriteria(
    significance_level=0.05,
    min_cramers_v=0.1,
    require_valid=True
)
filter_obj = SignificanceFilter(criteria)
filter_list = filter_obj.filter_tables(tables_with_stats)

print(f"Included: {filter_list.summary.included}/{filter_list.summary.total_tables}")
```

### 4. SPSS Reader (`io/reader.py`)

Reads SPSS (.sav) files using pyreadstat:
- Reads data and metadata
- Extracts variable labels
- Extracts value labels

```python
from spss_analyzer.io import SPSSReader

reader = SPSSReader()
df, metadata = reader.read("survey.sav")
```

### 5. Metadata Transformer (`io/metadata.py`)

Transforms SPSS metadata between formats:
- File-centered (pyreadstat format)
- Variable-centered (easier lookups)
- Filtered (business rules)

```python
from spss_analyzer.io import MetadataTransformer

transformer = MetadataTransformer()
new_metadata = transformer.to_variable_centered(metadata)
filtered = transformer.filter_variables(
    new_metadata,
    include_patterns=[r"^q[0-9]+"],
    min_categories=2
)
```

### 6. PSPP Syntax Generator (`pspp/syntax.py`)

Generates PSPP syntax for data transformations:

**Recoding Syntax:**
```python
from spss_analyzer.pspp import RecodingSyntaxGenerator

gen = RecodingSyntaxGenerator()
syntax = gen.generate_syntax(recoding_rules, file_label="Age Recoding")
print(syntax)
# Output:
# RECODE age (0 THRU 30 = 1) (31 THRU 50 = 2) (51 THRU HI = 3)
#     INTO age_group.
```

**CTABLES Syntax:**
```python
from spss_analyzer.pspp import CTablesSyntaxGenerator

gen = CTablesSyntaxGenerator()
syntax = gen.generate_syntax(table_specifications)
print(syntax)
# Output:
# CTABLES
#     /VLABELS VARIABLES=gender satisfaction DISPLAY=DEFAULT
#     /TABLE gender BY satisfaction
#     /STATISTICS count('n') columnpct('Column %').
```

### 7. PSPP Executor (`pspp/executor.py`)

Executes PSPP syntax files:

```python
from spss_analyzer.pspp import PSPPExecutor

executor = PSPPExecutor()
result = executor.execute_syntax(
    syntax_file="recoding.sps",
    input_file="original.sav",
    output_file="recoded.sav"
)

if result.success:
    print(f"Created {result.output_file}")
else:
    print(f"Error: {result.error_message}")
```

### 8. PowerPoint Generator (`reporting/powerpoint.py`)

Generates PowerPoint presentations:

```python
from spss_analyzer.reporting import PowerPointGenerator

gen = PowerPointGenerator()
gen.create_presentation(
    tables=filtered_tables,
    statistics=statistical_summary,
    title="Survey Analysis Results"
)
gen.save("output/report.pptx")
```

### 9. HTML Dashboard Generator (`reporting/dashboard.py`)

Generates interactive HTML dashboards:
- All tables with charts
- Sidebar navigation
- Significance highlighting
- Interactive filtering
- CSV export

```python
from spss_analyzer.reporting import HTMLDashboardGenerator

gen = HTMLDashboardGenerator()
html = gen.generate_dashboard(
    cross_tables=cross_table_data,
    statistics=statistical_summary,
    filter_list=filter_results
)
gen.save("output/dashboard.html", html)
```

## Running the Demo

```bash
cd /home/admin/workspaces/datachat/lib
python3 -m spss_analyzer.examples.demo
```

Demo output shows:
- Statistics calculation with Chi-square and Cramer's V
- Filtering by significance criteria
- PSPP syntax generation for recoding and CTABLES
- PSPP executor availability check
- PowerPoint generation capabilities
- Indicator generation (keyword, auto-detect, manual)
- HTML dashboard generation

## Design Principles

1. **Pure Python functions** - No LangGraph dependencies in library code
2. **Plain data structures** - Accepts/returns dicts, lists, not state objects
3. **Type hints** - Full type annotations for IDE support
4. **Dataclasses** - Structured result objects
5. **Convenience functions** - Both class-based and function-based APIs
6. **Comprehensive logging** - Detailed logging for debugging
7. **Error handling** - Clear error messages and validation

## Mapping: LangGraph Nodes → Library Modules

| Phase | LangGraph Nodes | Library Module | Status |
|-------|----------------|----------------|--------|
| 1. Extraction | Steps 1-3 | `io/reader.py`, `io/metadata.py` | ✅ Complete |
| 2. Recoding | Steps 4-8 | `pspp/syntax.py` (RecodingSyntaxGenerator) | ✅ Complete |
| 3. Indicators | Steps 9-11 | `analysis/indicators.py` | ✅ Complete |
| 4. Tables | Steps 12-16 | `pspp/syntax.py` (CTablesSyntaxGenerator) | ✅ Complete |
| 5. Statistics | Steps 17-18 | `analysis/statistics.py` | ✅ Complete |
| 6. Filtering | Steps 19-20 | `filtering/significance.py` | ✅ Complete |
| 7. PowerPoint | Step 21 | `reporting/powerpoint.py` | ✅ Complete |
| 8. HTML Dashboard | Step 22 | `reporting/dashboard.py` | ✅ Complete |

## Creating Skill Wrappers

Each library module can be wrapped by a skill that:
1. Calls the library function
2. Manages LangGraph state updates
3. Handles error conditions
4. Provides progress feedback

Example skill structure:
```yaml
name: spss-statistics
description: Compute Chi-square and Cramer's V for cross-tables
python_module: skills.spss_statistics
entry_point: main
```

```python
# skills/spss_statistics.py
from spss_analyzer.analysis import StatisticsCalculator

def main(state, config):
    calc = StatisticsCalculator(**config)
    result = calc.analyze_table(
        state["counts"],
        state["row_labels"],
        state["column_labels"]
    )
    return {
        "statistical_summary": result.to_dict(),
        "current_step": "statistics_complete"
    }
```

## Dependencies

```
# Core dependencies
pyreadstat          # SPSS file reading
numpy                # Statistical calculations
scipy                # Chi-square test

# PSPP integration (optional)
pspp                 # PSPP CLI (system package)

# Reporting (optional)
python-pptx          # PowerPoint generation
```

## Complete Usage Example

```python
# Complete workflow using the library
from spss_analyzer.io import SPSSReader, MetadataTransformer
from spss_analyzer.analysis import StatisticsCalculator, IndicatorGenerator
from spss_analyzer.filtering import SignificanceFilter
from spss_analyzer.pspp import RecodingSyntaxGenerator, CTablesSyntaxGenerator, PSPPExecutor
from spss_analyzer.reporting import PowerPointGenerator, HTMLDashboardGenerator

# 1. Read SPSS file
reader = SPSSReader()
df, metadata = reader.read("survey.sav")

# 2. Transform metadata
transformer = MetadataTransformer()
var_metadata = transformer.to_variable_centered(metadata)

# 3. Generate indicators
ind_gen = IndicatorGenerator()
indicators = ind_gen.generate(var_metadata)

# 4. Calculate statistics
calc = StatisticsCalculator()
result = calc.analyze_table(counts, row_labels, col_labels)

# 5. Filter by significance
filter_obj = SignificanceFilter()
filter_list = filter_obj.filter_tables(tables_with_stats)

# 6. Generate reports
ppt_gen = PowerPointGenerator()
ppt_gen.create_presentation(tables, statistics, "Survey Results")
ppt_gen.save("report.pptx")

dash_gen = HTMLDashboardGenerator()
html = dash_gen.generate_dashboard(cross_tables, statistics, filter_list)
dash_gen.save("dashboard.html", html)
```

## Benefits of Library Extraction

1. **Reusability** - Functions can be called from anywhere, not just LangGraph
2. **Testing** - Pure functions are easier to unit test
3. **Documentation** - Clear API documentation with docstrings
4. **Separation of concerns** - Business logic separate from workflow orchestration
5. **Performance** - Can optimize library code independently of LangGraph
6. **Maintenance** - Easier to update and extend functionality

## Version History

- **0.1.0** - Initial release with all 8 phases:
  - Statistics Calculator (Chi-square, Cramer's V)
  - Significance Filter
  - SPSS Reader & Metadata Transformer
  - PSPP Syntax Generators (Recoding, CTABLES)
  - PSPP Executor
  - PowerPoint Generator
  - HTML Dashboard Generator
  - Indicator Generator
