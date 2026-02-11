# Survey Coordinator

Orchestrates the Python library modules for the survey analysis computation workflow.

## Overview

This skill coordinates the `spss_analyzer` library modules to execute the complete analysis workflow:

1. **Apply Recoding** - Generate and execute PSPP recoding syntax
2. **Compute Indicators** - Calculate indicator values from variables
3. **Generate Cross-Tables** - Generate and execute PSPP CTABLES syntax
4. **Statistical Analysis** - Compute Chi-square and Cramer's V
5. **Filter Tables** - Filter to significant tables by p-value threshold

## When to Use

Use this skill when:
1. You have a validated table specification
2. You want to execute the analysis workflow
3. You need to generate intermediate data files

## Input Requirements

The skill requires:
1. **Table specification** - The validated `table_specification.json`
2. **SPSS data file** - The original `.sav` file
3. **Filtered metadata** - Variable metadata from the SPSS file

## Output

Produces:
- `recoded_data.sav` - Data with recoding rules applied
- `indicators.csv` - Computed indicator values
- `cross_tables.csv` - Generated cross-tabulation tables
- `statistical_summary.json` - Chi-square and Cramer's V results
- `filtered_tables.json` - Only significant tables

## Workflow Steps

### Step 1: Apply Recoding

```python
from spss_analyzer.pspp import RecodingSyntaxGenerator, PSPPExecutor

# Generate PSPP syntax from specification
gen = RecodingSyntaxGenerator()
syntax = gen.generate_syntax(spec.global_recodings)

# Execute PSPP
executor = PSPPExecutor()
executor.execute_syntax(
    syntax_file="recoding.sps",
    input_file="original.sav",
    output_file="recoded_data.sav"
)
```

### Step 2: Compute Indicators

```python
from spss_analyzer.analysis import IndicatorGenerator
from spss_analyzer.io import SPSSReader

# Read recoded data
reader = SPSSReader()
df, metadata = reader.read("recoded_data.sav")

# Generate indicators from specification
gen = IndicatorGenerator()
indicators_df = gen.compute_indicators(df, spec.indicators)

# Save indicators
indicators_df.to_csv("indicators.csv", index=False)
```

### Step 3: Generate Cross-Tables

```python
from spss_analyzer.pspp import CTablesSyntaxGenerator

# Generate CTABLES syntax from specification
gen = CTablesSyntaxGenerator()
syntax = gen.generate_syntax(spec.tables)

# Execute PSPP
executor = PSPPExecutor()
executor.execute_syntax(
    syntax_file="crosstabs.sps",
    input_file="recoded_data.sav",
    output_file="cross_tables.csv"
)
```

### Step 4: Statistical Analysis

```python
from spss_analyzer.analysis import StatisticsCalculator

# Calculate statistics for each table
calc = StatisticsCalculator()
results = []
for table in cross_tables:
    result = calc.analyze_table(
        counts=table["counts"],
        row_labels=table["row_labels"],
        column_labels=table["column_labels"]
    )
    results.append(result.to_dict())

# Save summary
with open("statistical_summary.json", "w") as f:
    json.dump(results, f, indent=2)
```

### Step 5: Filter Significant Tables

```python
from spss_analyzer.filtering import SignificanceFilter

# Create filter criteria from specification
criteria = FilterCriteria(
    significance_level=spec.output_settings.significance_threshold,
    min_cramers_v=spec.output_settings.min_cramers_v,
)

# Filter tables
filter_obj = SignificanceFilter(criteria)
filter_list = filter_obj.filter_tables(tables_with_stats)

# Save filter list
with open("filtered_tables.json", "w") as f:
    json.dump(filter_list.to_dict(), f, indent=2)
```

## Example Usage

```
Run the analysis workflow:

Specification: table_specification.json
Data file: survey_data.sav
Output directory: output/
```

## Progress Tracking

The coordinator will report progress at each step:
- ✓ Step 1: Applied 5 recoding rules
- ✓ Step 2: Computed 3 indicators
- ✓ Step 3: Generated 18 cross-tables
- ✓ Step 4: Calculated statistics for 18 tables
- ✓ Step 5: Filtered to 12 significant tables

## Error Handling

If any step fails:
1. Log the error with context
2. Save partial results if available
3. Provide clear guidance on fixing the issue
