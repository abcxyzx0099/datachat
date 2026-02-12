# Survey Analyzer

SPSS Survey Analysis Library - Extract, recode, compute indicators, cross-tables, statistics, filtering, and reports.

## Installation

```bash
pip install survey-analyzer
```

## Development

```bash
# Install in development mode
pip install -e ./survey_analyzer

# Install with dev dependencies
pip install -e "./survey_analyzer[dev]"

# Run tests
cd survey_analyzer && pytest

# Run with coverage
cd survey_analyzer && pytest --cov=src/survey_analyzer
```

## Usage

```python
from survey_analyzer.io.reader import SPSSReader
from survey_analyzer.reporting.powerpoint import PowerPointReporter

# Load SPSS file
reader = SPSSReader("data/survey.sav")
metadata, data = reader.read()

# Generate report
reporter = PowerPointReporter("output/presentation.pptx")
reporter.generate(metadata, filtered_results)
```

## CLI

```bash
survey-analyzer --help
```

## Package Structure

```
survey_analyzer/
├── src/survey_analyzer/      # Source code
│   ├── analysis/             # Statistical analysis
│   ├── filtering/            # Significance filtering
│   ├── io/                   # SPSS file I/O
│   ├── pspp/                 # PSPP integration
│   ├── reporting/            # PowerPoint & HTML reports
│   ├── specification/        # Table specification
│   └── cli.py                # Command-line interface
├── tests/                    # Package tests
├── docs/                     # Package documentation
└── pyproject.toml           # Package configuration
```
