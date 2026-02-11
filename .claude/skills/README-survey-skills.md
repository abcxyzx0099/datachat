# Survey Analysis Skills

A collection of Claude Code skills for SPSS survey analysis, based on the `spss_analyzer` Python library.

## Skills

### survey-spec-gen

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

1. **survey-spec-gen** → Generate `table_specification.json`
2. **survey-validate** → Validate the specification
3. **survey-coordinator** → Run analysis workflow
4. **survey-output** → Generate final reports

## Dependencies

All skills depend on the `spss_analyzer` Python library located at `lib/spss_analyzer/`.

## Library Structure

```
lib/spss_analyzer/
├── specification/  # Schema and validator for table_specification.json
├── io/            # SPSS file reading and metadata handling
├── pspp/           # PSPP syntax generation and execution
├── analysis/        # Statistics and indicators
├── filtering/        # Significance filtering
└── reporting/        # PowerPoint and HTML generation
```

## Quick Start

```bash
# 1. Generate specification
python .claude/skills/survey-spec-gen/implementation.py \
    output/filtered_metadata.json \
    --source-file survey_data.sav \
    --output table_specification.json

# 2. Validate specification
python .claude/skills/survey-validate/implementation.py \
    table_specification.json \
    --metadata-file output/filtered_metadata.json

# 3. Run analysis
python .claude/skills/survey-coordinator/implementation.py \
    table_specification.json \
    survey_data.sav \
    --metadata-file output/filtered_metadata.json \
    --output-dir output/

# 4. Generate reports
python .claude/skills/survey-output/implementation.py \
    table_specification.json \
    output/cross_tables.json \
    output/statistical_summary.json \
    output/filtered_tables.json \
    --output-dir output/
```
