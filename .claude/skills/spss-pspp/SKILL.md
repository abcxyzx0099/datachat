---
name: spss-pspp
description: 'Generate and execute PSPP syntax for SPSS data transformations. Supports RECODE for variable recoding and CTABLES for cross-tabulation. Use when you need to transform SPSS data or generate cross-table outputs.'
license: Apache-2.0
---

# SPSS PSPP Skill

Generate and execute PSPP syntax for SPSS data transformations.

## Features

- **Recoding syntax** - Generate RECODE commands for variable transformations
- **CTABLES syntax** - Generate cross-tabulation table specifications
- **PSPP execution** - Run syntax files and create output datasets
- **Multiple transformation types** - Range grouping, category consolidation, derived variables
- **Automatic label handling** - Variable and value labels included

## Usage

### Generate Recoding Syntax

```
User: Generate PSPP recoding syntax for age variable:
0-30 = 1 (Young), 31-50 = 2 (Middle), 51+ = 3 (Older)

Assistant: I'll generate the PSPP RECODE syntax for age grouping.

Generated syntax:
* Rule 1: age → age_group
* Age grouping
RECODE age (0 THRU 30 = 1) (31 THRU 50 = 2) (51 THRU HI = 3)
    INTO age_group.
VARIABLE LABELS age_group 'Age grouping'.
VALUE LABELS age_group
    1 'Young'
    2 'Middle'
    3 'Older'.

EXECUTE.

Syntax saved to /output/recoding.sps
```

### Generate CTABLES Syntax

```
User: Create CTABLES syntax for gender x satisfaction table

Assistant: I'll generate the PSPP CTABLES syntax.

Generated syntax:
* Table 1: gender_x_satisfaction
CTABLES
    /VLABELS VARIABLES=gender satisfaction DISPLAY=DEFAULT
    /TABLE gender BY satisfaction
    /STATISTICS count('n') columnpct('Column %') chisq('chi-square') cramersv('Cramer''s V').

EXECUTE.

Syntax saved to /output/ctables.sps
```

### Execute PSPP Syntax

```
User: Execute the recoding syntax on survey.sav

Assistant: I'll execute the PSPP syntax file.

Executing: pspp -o new_data.sav survey.sav recoding.sps

Result: Success
- Output file: new_data.sav
- Execution time: 2.3 seconds
- Variables recoded: age → age_group
```

### Batch Processing

```
User: Generate recoding rules for all these variables:
- sat_1 to sat_5: 1-3=1 (Low), 4-5=2 (High)
- q1a, q1b, q1c: Consolidate into q1_combined

Assistant: I'll generate PSPP syntax for all your recoding rules.

Generated 2 rules:
1. sat_1, sat_2, sat_3, sat_4, sat_5 → top/bottom box
2. q1a, q1b, q1c → category consolidation

Syntax saved to /output/batch_recoding.sps
```

## Transformation Types

### Range Grouping

Group numeric ranges into categories:

```python
{
    "source_variable": "age",
    "target_variable": "age_group",
    "transformation_type": "range_grouping",
    "rules": [
        {"source_min": 0, "source_max": 30, "target_value": 1, "target_label": "18-30"},
        {"source_min": 31, "source_max": 50, "target_value": 2, "target_label": "31-50"},
        {"source_min": 51, "source_max": "HI", "target_value": 3, "target_label": "51+"}
    ]
}
```

### Category Consolidation

Combine multiple categories into one:

```python
{
    "source_variable": "occupation",
    "target_variable": "occupation_grouped",
    "transformation_type": "category_consolidation",
    "rules": [
        {"source_values": ["Farmer", "Fisherman"], "target_value": 1, "target_label": "Agriculture"},
        {"source_values": ["Teacher", "Doctor"], "target_value": 2, "target_label": "Professional"}
    ]
}
```

### Derived Variables

Create computed variables:

```python
{
    "source_variable": "sat_q1, sat_q2, sat_q3",
    "target_variable": "satisfaction_index",
    "transformation_type": "derived",
    "formula": "MEAN(sat_q1, sat_q2, sat_q3)"
}
```

### Top/Bottom Box

Convert rating scales to dichotomous:

```python
{
    "source_variable": "satisfaction",
    "target_variable": "sat_topbox",
    "transformation_type": "top_bottom_box",
    "rules": [
        {"source_values": [4, 5], "target_value": 1, "target_label": "Top box"},
        {"source_values": [3], "target_value": "SYSMIS", "target_label": "Neutral"},
        {"source_values": [1, 2], "target_value": 0, "target_label": "Bottom box"}
    ]
}
```

## CTABLES Statistics

Available statistics:

| Statistic | PSPP Keyword | Description |
|-----------|--------------|-------------|
| Count | `count` | Number of cases |
| Row % | `rowpct` | Row percentages |
| Column % | `columnpct` | Column percentages |
| Total % | `totalpct` | Total percentages |
| Chi-square | `chisq` | Chi-square test |
| Cramer's V | `cramersv` | Effect size |

## Input File Format

```json
{
    "rules": [
        {
            "source_variable": "age",
            "target_variable": "age_group",
            "transformation_type": "range_grouping",
            "description": "Age grouping for analysis",
            "rules": [
                {"source_min": 0, "source_max": 30, "target_value": 1, "target_label": "18-30"}
            ]
        }
    ]
}
```

## Output

### Syntax File

PSPP syntax file (.sps) with:
- Header comments
- Variable labels
- Value labels
- RECODE/COMPUTE commands
- EXECUTE statement

### Execution Result

```python
{
    "success": true,
    "exit_code": 0,
    "output_file": "/path/to/new_data.sav",
    "execution_time": 2.3,
    "error_message": null
}
```

## Requirements

- Python 3.11+
- PSPP installed: `sudo apt-get install pspp`
- Input SPSS file (.sav)

## Example Code

```python
from spss_analyzer.pspp import RecodingSyntaxGenerator, CTablesSyntaxGenerator, PSPPExecutor

# Generate recoding syntax
gen = RecodingSyntaxGenerator()
syntax = gen.generate_syntax(recoding_rules, file_label="Data Recoding")

# Execute PSPP
executor = PSPPExecutor()
result = executor.execute_syntax("recoding.sps", "input.sav", "output.sav")
```

## Related Skills

- `spss-statistics` - Analyze generated cross-tables
- `spss-reports` - Create reports from processed data
