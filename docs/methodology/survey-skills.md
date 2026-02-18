# Survey Analysis Skills

A collection of Claude Code skills for SPSS survey analysis, based on the `survey_analyzer` Python library.

## Skill Types

| Type | Description | Examples |
|------|-------------|----------|
| **Doc-only** | Documentation showing how to use `survey_analyzer` library | `analyzer-data-prep` |
| **Implementation** | Skills with executable scripts | `analyzer-tablespec-gen`, others |

## Skills

### analyzer-data-prep (Doc-Only)

**Stage 1: Data Preparation** - Load SPSS files and extract metadata using `survey_analyzer.io` library.

**Use when:** You need to prepare survey data for analysis by extracting and filtering variables.

**Type:** Doc-only skill (references `survey_analyzer` library)

**Input:** SPSS (.sav) file
**Output:** `filtered_metadata.json`

**Library Usage:**
```python
from survey_analyzer.io import SPSSReader
from survey_analyzer.io.metadata import MetadataTransformer

# Read SPSS file
reader = SPSSReader()
df, metadata = reader.read("data/survey_data.sav")

# Transform and filter
transformer = MetadataTransformer()
variable_metadata = transformer.to_variable_centered(metadata)
filtered = transformer.filter_variables(variable_metadata, max_categories=30)
```

**See:** `analyzer-data-prep/skill.md` for complete documentation and examples.

---

### analyzer-tablespec-gen

Generates a consolidated table specification document from SPSS metadata.

**Use when:** You need to create a complete analysis specification with indicators, recoding rules, and table definitions.

**Input:** Filtered metadata from SPSS file
**Output:** `table_specification.json`

**Example:**
```
Generate a table specification for this survey.
Metadata file: output/filtered_metadata.json
Focus on: Customer satisfaction indicators and demographic crosstabs
```

---

### survey-validate

Validates a table specification document against schema, references, and business logic.

**Use when:** You need to check if a table specification is valid before processing.

**Input:** Table specification JSON, optional metadata for reference validation
**Output:** Validation report with errors and warnings

**Example:**
```
Validate this table specification:
Specification: table_specification.json
Metadata: output/filtered_metadata.json
```

---

### survey-coordinator

Orchestrates the Python library modules for the complete analysis workflow.

**Use when:** You have a valid specification and want to execute the analysis.

**Input:** Table specification, SPSS data file, metadata
**Output:** Recoded data, indicators, cross-tables, statistics, filtered tables

**Workflow:**
1. Apply recoding (PSPP)
2. Compute indicators
3. Generate cross-tables (PSPP)
4. Calculate statistics (Chi-square, Cramer's V)
5. Filter significant tables

**Example:**
```
Run the analysis workflow:
Specification: table_specification.json
Data file: survey_data.sav
Output directory: output/
```

---

### survey-output

Generates final reports (PowerPoint and HTML dashboard) from analyzed data.

**Use when:** Analysis is complete and you need to create presentation reports.

**Input:** Table specification, cross-tables, statistics, filtered tables
**Output:** `presentation.pptx`, `dashboard.html`

**Example:**
```
Generate the final reports:
Specification: table_specification.json
Cross-tables: output/cross_tables.json
Statistics: output/statistical_summary.json
Filtered tables: output/filtered_tables.json
```

---

## Complete Workflow

The typical analysis workflow is:

1. **analyzer-data-prep** → Generate `filtered_metadata.json`
2. **analyzer-tablespec-gen** → Generate `table_specification.json`
3. **survey-validate** → Validate the specification
4. **survey-coordinator** → Run analysis workflow
5. **survey-output** → Generate final reports

---

## Test Data

This project includes real survey data for testing and development of the analysis skills.

### Available Test Data

| File | Size | Description | Use For |
|------|------|-------------|---------|
| **`data/real-data.sav`** | 9.6 MB | Full production survey data | Complete workflow testing |
| **`data/simple-data.sav`** | 3.6 KB | Simplified test dataset | Quick development tests |

### Using Test Data

All examples in this documentation use `data/real-data.sav` as the default input file. Replace with your own `.sav` file path when working with actual survey data.

**Example:**
```python
# Using provided test data
df, metadata = SPSSReader().read("data/real-data.sav")

# Using your own data
df, metadata = SPSSReader().read("/path/to/your/survey.sav")
```

### Test Data Specifications

**real-data.sav:**
- Located at: `data/real-data.sav`
- Size: ~9.6 MB
- Purpose: Full-featured production survey data for comprehensive testing

**simple-data.sav:**
- Located at: `data/simple-data.sav`
- Size: ~3.6 KB
- Purpose: Lightweight dataset for quick development iteration

---

## Dependencies

All skills depend on the `survey_analyzer` Python package located at `survey_analyzer/`.

Install in development mode:
```bash
pip install -e ./survey_analyzer
```

## Library Structure

```
survey_analyzer/
├── src/survey_analyzer/
│   ├── specification/  # Schema and validator for table_specification.json
│   ├── io/             # SPSS file reading and metadata handling
│   ├── pspp/           # PSPP syntax generation and execution
│   ├── analysis/       # Statistics and indicators
│   ├── filtering/      # Significance filtering
│   └── reporting/      # PowerPoint and HTML generation
├── tests/              # Package tests
├── docs/               # Package documentation
└── pyproject.toml      # Package configuration
```

## Quick Start

```bash
# 1. Data preparation (using survey_analyzer library with test data)
python -c "
from survey_analyzer.io import SPSSReader
from survey_analyzer.io.metadata import MetadataTransformer
import json

reader = SPSSReader()
df, metadata = reader.read('data/real-data.sav')
transformer = MetadataTransformer()
variable_metadata = transformer.to_variable_centered(metadata)
filtered = transformer.filter_variables(variable_metadata, max_categories=30)

output = {
    'file_info': {'path': 'data/real-data.sav', 'case_count': len(df)},
    'variables': filtered,
    'variable_names': list(filtered.keys())
}
with open('output/filtered_metadata.json', 'w') as f:
    json.dump(output, f, indent=2)
"

# 2. Generate specification
python .claude/skills/analyzer-tablespec-gen/implementation.py \
    output/filtered_metadata.json \
    --source-file data/real-data.sav \
    --output table_specification.json

# 3. Validate specification
python .claude/skills/survey-validate/implementation.py \
    table_specification.json \
    --metadata-file output/filtered_metadata.json

# 4. Run analysis
python .claude/skills/survey-coordinator/implementation.py \
    table_specification.json \
    data/real-data.sav \
    --metadata-file output/filtered_metadata.json \
    --output-dir output/

# 5. Generate reports
python .claude/skills/survey-output/implementation.py \
    table_specification.json \
    output/cross_tables.json \
    output/statistical_summary.json \
    output/filtered_tables.json \
    --output-dir output/
```
