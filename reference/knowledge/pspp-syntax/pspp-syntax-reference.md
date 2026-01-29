# PSPP Syntax Reference

**Category**: Reference
**Layer**: Analysis
**Granularity**: Low
**Stage**: Development
**Runtime**: Backend

> **IMPORTANT**: This PSPP implementation is **deferred**. The current development focuses on **Python/pandas engine** only. This document is provided for future reference.

---

## Overview

PSPP (GNU SPSS) is a statistical analysis software that uses SPSS syntax for operations. This document provides a reference for PSPP syntax commands used in dataflow.

| Attribute | Value |
|-----------|-------|
| **Website** | https://www.gnu.org/software/pspp/ |
| **Version** | 2.0.1 |
| **Install** | `sudo apt-get install pspp` |
| **Execution** | `pspp -o output.txt syntax.sps` |

---

## Table of Contents

1. [Data Loading](#data-loading)
2. [Variable Analysis](#variable-analysis)
3. [Frequency Analysis](#frequency-analysis)
4. [Descriptive Statistics](#descriptive-statistics)
5. [Crosstab Analysis](#crosstab-analysis)
6. [Data Transformations](#data-transformations)

---

## Data Loading

### READ DATA from SPSS File

```spss
/* Load SPSS file */
GET FILE='data.sav'.
```

### SET Working Directory

```spss
/* Set working directory */
CD '/path/to/data'.
```

---

## Variable Analysis

### DISPLAY DICTIONARY

Display variable metadata (names, labels, types, value labels).

```spss
/* Display all variable information */
DISPLAY DICTIONARY.

/* Display specific variables */
DISPLAY DICTIONARY /VARIABLES=S0 S1 S2.
```

**Output Format**: Text or CSV

---

## Frequency Analysis

### FREQUENCIES Procedure

Generate frequency tables with statistics.

```spss
/* Basic frequency table */
FREQUENCIES VARIABLES=S0 S1 S2.

/* With statistics */
FREQUENCIES VARIABLES=S0 S1 S2
  /STATISTICS=MODE MEDIAN MEAN STDDEV MIN MAX
  /FORMAT=TABLE
  /ORDER=ANALYSIS.
```

**Available Statistics**:
- `MODE` - Most frequent value
- `MEDIAN` - Middle value (50th percentile)
- `MEAN` - Arithmetic average
- `STDDEV` - Standard deviation
- `MIN` - Minimum value
- `MAX` - Maximum value
- `VARIANCE` - Variance
- `RANGE` - Range (max - min)
- `SEMEAN` - Standard error of mean
- `KURTOSIS` - Kurtosis
- `SKEWNESS` - Skewness

**Format Options**:
- `/FORMAT=TABLE` - Table format
- `/FORMAT=NOTABLE` - Suppress table
- `/ORDER=ANALYSIS` - Variable order in file
- `/ORDER=NAME` - Alphabetical by name

---

## Descriptive Statistics

### DESCRIPTIVES Procedure

Calculate summary statistics for numeric variables.

```spss
/* Basic descriptive statistics */
DESCRIPTIVES VARIABLES=age income satisfaction_score.

/* With specific statistics */
DESCRIPTIVES VARIABLES=age income satisfaction_score
  /STATISTICS=MEAN STDDEV MIN MAX KURTOSIS SKEWNESS.
```

**Available Statistics**:
- `MEAN` - Mean
- `STDDEV` - Standard deviation
- `VARIANCE` - Variance
- `MIN` - Minimum
- `MAX` - Maximum
- `KURTOSIS` - Kurtosis
- `SKEWNESS` - Skewness
- `SEMEAN` - Standard error of mean
- `SUM` - Sum

---

## Crosstab Analysis

### CTABLES Procedure

Generate cross-tabulation tables with statistical tests.

```spss
/* Basic crosstab */
CTABLES
  /TABLE gender BY region
  /STATISTICS CHISQ PHI.

/* With weights */
DATASET NAME ViewData WINDOW=FRONT.
WEIGHT BY weight_var.
CTABLES
  /VLABELS VARIABLES=DISPLAY LABEL=DISPLAY
  /TABLE gender BY region
  /STATISTICS CHISQ PHI.

/* Multiple variables */
CTABLES
  /TABLE age_groups BY (gender region)
  /STATISTICS CHISQ PHI CRAMERSV.
```

**Available Statistics**:
- `CHISQ` - Chi-square test of independence
- `PHI` - Phi coefficient (2×2 tables only)
- `CRAMERSV` - Cramer's V (any table size)
- `BENTLER` - Bonferroni correction
- `NONE` - No statistical tests

**Table Specifications**:
- `BY` - Separates row and column variables
- `(var1 var2)` - Nested variables
- `+` - Concatenated variables

---

### CROSSTABS Procedure (Alternative)

```spss
/* Basic crosstabs */
CROSSTABS
  /TABLES=gender BY region
  /STATISTICS=CHISQ PHI.
```

---

## Data Transformations

### RECODE

Recode variable values into new categories.

```spss
/* Recode into same variable */
RECODE age (18 THRU 29=1) (30 THRU 39=2) (40 THRU 49=3) (50 THRU 65=4)
  INTO age_bracket.

/* Recode into new variable */
RECODE age (18 THRU 29=1) (30 THRU 39=2) (40 THRU 49=3) (50 THRU 65=4)
  INTO age_bracket.
VARIABLE LABELS age_bracket 'Age Bracket'.
```

**Value Ranges**:
- `LO THRU 29` - Lowest through 29
- `18 THRU 29` - 18 through 29 (inclusive)
- `30 THRU HI` - 30 through highest
- `ELSE` - All other values
- `SYSMIS` - System missing

---

### VALUE LABELS

Assign labels to numeric values.

```spss
/* Single variable */
VALUE LABELS age_bracket
  1 '18-29'
  2 '30-39'
  3 '40-49'
  4 '50-65'.

/* Multiple variables (same labels) */
VALUE LABELS gender region
  1 'Male'
  2 'Female'.
```

---

### VARIABLE LABELS

Assign descriptive labels to variables.

```spss
VARIABLE LABELS
  S0 'Gender of Respondent'
  S1 'Age in Years'
  S2 'Satisfaction Score'.
```

---

### COMPUTE

Create new variables from formulas.

```spss
/* Simple computation */
COMPUTE total_score = S1 + S2 + S3.

/* Conditional computation */
DO IF (NOT MISSING(S1)).
  COMPUTE satisfaction_group = 1.
END IF.
```

---

### IF (Conditional Assignment)

```spss
/* Simple IF */
IF (age >= 18 AND age <= 29) age_group = 1.

/* Complex IF */
IF (S1 >= 4 AND S2 <= 2) high_sat_low_cost = 1.
```

---

## Missing Values

### MISSING VALUES

Declare missing values.

```spss
/* Single missing value */
MISSING VALUES age (-1).

/* Multiple missing values */
MISSING VALUES S0 (-9, -99).

/* Range of missing values */
MISSING VALUES income (LO THRU 0).
```

---

###SYSMIS and User Missing

```spss
/* Set to system missing */
DO IF (S0 = -99).
  RECODE S0 (-99=SYSMIS).
END IF.
```

---

## Weighting

### WEIGHT BY

Apply weighting variable.

```spss
/* Apply weight */
WEIGHT BY weight_var.

/* Turn off weighting */
WEIGHT OFF.
```

---

## Output Control

### SET Output Formats

```spss
/* Set output to CSV */
SET DECIMAL=comma.
```

### EXECUTE

Execute pending commands.

```spss
EXECUTE.
```

---

## Complete Example Syntax File

```spss
/* dataflow Crosstab Analysis */
/* Generated: 2026-01-04 */

/* Load data */
GET FILE='/workspace/data.sav'.

/* Set weight variable */
WEIGHT BY weight_var.

/* Recode age into groups */
RECODE age (18 THRU 29=1) (30 THRU 39=2) (40 THRU 49=3) (50 THRU 65=4)
  INTO age_groups.
VALUE LABELS age_groups
  1 '18-29'
  2 '30-39'
  3 '40-49'
  4 '50-65'.
VARIABLE LABELS age_groups 'Age Groups'.

/* Generate crosstab */
CTABLES
  /VLABELS VARIABLES=DISPLAY LABEL=DISPLAY
  /TABLE age_groups BY gender
  /STATISTICS CHISQ PHI CRAMERSV.

/* Execute */
EXECUTE.
```

---

## PSPP Command Line

### Basic Execution

```bash
# Generate CSV output
pspp -o output.csv syntax.sps

# Generate HTML output
pspp -o output.html syntax.sps

# Generate PDF output
pspp -o output.pdf syntax.sps

# Generate text output
pspp -o output.txt syntax.sps
```

### Quiet Mode

```bash
# Suppress output messages
pspp -o output.csv -q syntax.sps
```

### Interactive Mode

```bash
# Interactive PSPP terminal
pspp
```

---

## Output File Formats

| Format | Extension | Use When |
|--------|-----------|----------|
| **CSV** | `.csv` | Machine-readable, data import |
| **HTML** | `.html` | Web viewing, reports |
| **PDF** | `.pdf` | Printable reports |
| **Text** | `.txt` | Quick inspection, logs |

---

## PSPP Procedures Quick Reference

| Procedure | Purpose | Key Keywords |
|-----------|---------|--------------|
| `DISPLAY DICTIONARY` | Variable metadata | VARIABLES |
| `FREQUENCIES` | Frequency tables | STATISTICS, FORMAT, ORDER |
| `DESCRIPTIVES` | Summary statistics | STATISTICS |
| `CTABLES` | Crosstabs with tests | TABLE, STATISTICS, VLABELS |
| `CROSSTABS` | Alternative crosstabs | TABLES, STATISTICS |
| `RECODE` | Transform values | INTO, LO, THRU, HI |
| `VALUE LABELS` | Label values | (value 'label') |
| `VARIABLE LABELS` | Label variables | (var 'label') |
| `COMPUTE` | Calculate new vars | Formulas |
| `IF` | Conditional assignment | Logical operators |
| `WEIGHT BY` | Apply weights | Variable name |
| `MISSING VALUES` | Define missing | (values) |

---

## Common Operators

| Operator | Meaning | Example |
|----------|---------|---------|
| `AND` | Logical AND | `age >= 18 AND age <= 65` |
| `OR` | Logical OR | `S1 = 1 OR S1 = 2` |
| `NOT` | Logical NOT | `NOT MISSING(S1)` |
| `=` | Equal to | `age = 25` |
| `~=` | Not equal to | `S1 ~= 99` |
| `<` | Less than | `age < 30` |
| `>` | Greater than | `age > 18` |
| `<=` | Less than or equal | `age <= 65` |
| `>=` | Greater than or equal | `age >= 18` |

---

## Related Documents

- [Two Statistical Backends](./two-statistical-backends.md) - Engine comparison and selection guide
- [Statistical Formulas Reference](./statistical-formulas-reference.md) - Math behind the statistics

---
