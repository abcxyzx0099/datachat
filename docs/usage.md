# Usage Guide

This document provides user-facing guidance for running the Survey Analysis & Visualization Workflow.

---

## Table of Contents

1. [Quick Start](#1-quick-start)
2. [Running an Analysis](#2-running-an-analysis)
3. [Human Review Process](#3-human-review-process)
4. [Understanding Outputs](#4-understanding-outputs)
5. [Common Scenarios](#5-common-scenarios)
6. [Troubleshooting](#6-troubleshooting)

---

## 1. Quick Start

### 1.1 Prerequisites

| Requirement | How to Verify |
|-------------|---------------|
| **Python 3.10+** | `python --version` |
| **PSPP installed** | `pspp --version` |
| **OpenAI API key** | Set in `.env` file |

### 1.2 Installation

```bash
# Clone repository
git clone <repository-url>
cd datachat

# Install Python dependencies
pip install -r requirements.txt

# Install PSPP (Ubuntu/Debian)
sudo apt-get install pspp

# Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 1.3 Run Your First Analysis

```bash
# Place your .sav file in data/input/
cp my_survey.sav data/input/

# Run the workflow
python -m agent.graph --input data/input/my_survey.sav
```

**Output**: Files generated in `output/` directory.

---

## 2. Running an Analysis

### 2.1 Basic Usage

```bash
python -m agent.graph --input data/input/survey.sav
```

### 2.2 Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--input` | Path to input .sav file | Required |
| `--output-dir` | Output directory | `output/` |
| `--config` | Path to config file | `config/default.py` |
| `--no-human-review` | Skip human review (auto-approve) | False |
| `--thread-id` | Thread ID for checkpointing | Auto-generated |

### 2.3 Examples

```bash
# Basic analysis
python -m agent.graph --input data/input/customer_survey.sav

# Custom output directory
python -m agent.graph --input data/input/survey.sav --output-dir results/

# Disable human review (for testing)
python -m agent.graph --input data/input/survey.sav --no-human-review

# Resume from checkpoint
python -m agent.graph --thread-id survey_001 --resume
```

### 2.4 Python API Usage

```python
from agent.graph import create_survey_analysis_graph
from agent.config import DEFAULT_CONFIG

# Create workflow
graph = create_survey_analysis_graph()

# Run analysis
result = graph.invoke({
    "spss_file_path": "data/input/survey.sav",
    "config": DEFAULT_CONFIG
})

print(f"PowerPoint: {result['powerpoint_path']}")
print(f"Dashboard: {result['html_dashboard_path']}")
```

---

## 3. Human Review Process

### 3.1 Overview

The workflow pauses for human review at three points:

| Step | What's Reviewed | Location |
|------|----------------|----------|
| **Step 6** | Recoding Rules | `output/reviews/recoding_rules_review.md` |
| **Step 11** | Indicators | `output/reviews/indicators_review.md` |
| **Step 14** | Table Specifications | `output/reviews/table_specs_review.md` |

### 3.2 Review Document Structure

Each review document contains:

```markdown
# Review: [Artifact Name]

## Validation Results
- ✅ Passed: 15 checks
- ❌ Errors: 2
- ⚠️ Warnings: 1

## Proposed Artifact
[Generated JSON/table]

## Errors
[Error messages]

## Context
[Variable metadata, survey context]
```

### 3.3 Approving or Rejecting

#### Via Command Line (Interactive)

```bash
# Workflow pauses and displays:
# ⏸️  Human review required: output/reviews/recoding_rules_review.md
# Review the document, then:
#   - Type 'approve' to continue
#   - Type 'reject' with feedback to regenerate

$ approve  # or: reject Group satisfaction by top-2-box instead

# ✅ Approved. Continuing workflow...
```

#### Via Python API

```python
# After interrupt, update state and resume
state.update({
    "recoding_approved": True,  # or False to reject
    "recoding_feedback": None   # or feedback dict
})

result = graph.invoke(None, config)
```

### 3.4 Feedback Format

When rejecting, provide specific feedback:

```python
{
    "issues": ["Grouping doesn't match survey intent"],
    "suggestions": ["Group satisfaction questions by top-2-box"],
    "specific_changes": {
        "q5_satisfaction": "Use: Low(1-2), Medium(3), High(4-5)"
    }
}
```

---

## 4. Understanding Outputs

### 4.1 Output Files

| File | Description | Use Case |
|------|-------------|----------|
| **presentation.pptx** | Executive summary with significant tables only | Stakeholder presentations |
| **dashboard.html** | Interactive dashboard with all tables | Detailed exploration |
| **statistical_summary.json** | Statistical test results | Programmatic access |
| **cross_tables.csv** | Raw cross-tabulation data | Further analysis |

### 4.2 PowerPoint Structure

```
Slide 1: Title
  - Analysis name, date, sample size

Slide 2-N: Table Results (for each significant table)
  - Chart (bar graph)
  - Table with counts and percentages
  - Statistics: Chi-square, p-value, Cramer's V

Final Slide: Summary
  - Total tables analyzed
  - Significant relationships found
```

### 4.3 HTML Dashboard Features

| Feature | Description |
|---------|-------------|
| **Navigation** | Sidebar with table list |
| **Sorting** | Click column headers to sort |
| **Filtering** | Filter by significance, effect size |
| **Charts** | Interactive bar charts for each table |
| **Statistics** | Chi-square, p-value, Cramer's V displayed |

### 4.4 Statistical Summary JSON

```json
[
    {
        "table_name": "Gender by Age",
        "chi_square": 15.23,
        "p_value": 0.002,
        "degrees_of_freedom": 4,
        "cramers_v": 0.18,
        "interpretation": "small effect",
        "significant": true
    }
]
```

---

## 5. Common Scenarios

### 5.1 Scenario: Automatic Mode (No Human Review)

```bash
# Disable all human review checkpoints
python -m agent.graph --input survey.sav --no-human-review

# Or via config
config = DEFAULT_CONFIG.copy()
config["enable_human_review"] = False
```

**Use when**: Testing, batch processing, trusted surveys.

### 5.2 Scenario: Resume After Crash

```bash
# Resume from existing checkpoint
python -m agent.graph --thread-id survey_001 --resume

# List available threads
python -m agent.graph --list-threads
```

### 5.3 Scenario: Custom Filtering Rules

```python
config = DEFAULT_CONFIG.copy()
config["cardinality_threshold"] = 50  # Filter fewer variables
config["filter_binary"] = False       # Keep binary variables
config["filter_other_text"] = False   # Keep "other" fields
```

### 5.4 Scenario: Adjust Statistical Thresholds

```python
config = DEFAULT_CONFIG.copy()
config["significance_level"] = 0.01    # More strict (p < 0.01)
config["min_cramers_v"] = 0.2          # Larger effect size required
config["min_cell_count"] = 20          # Larger sample size required
```

### 5.5 Scenario: Batch Processing Multiple Files

```bash
# Process all .sav files in a directory
for file in data/input/*.sav; do
    python -m agent.graph --input "$file" --output-dir "output/$(basename $file .sav)"
done
```

---

## 6. Troubleshooting

### 6.1 Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| **PSPP not found** | PSPP not installed or wrong path | Install PSPP or set `PSPP_PATH` |
| **API key error** | Missing/invalid OpenAI key | Check `.env` file |
| **Memory error** | Large survey file | Increase available RAM |
| **Validation loop** | LLM generates invalid output | Increase `max_self_correction_iterations` |
| **Permission denied** | Cannot write to output directory | Check directory permissions |

### 6.2 Error Messages

| Error | Meaning | Action |
|-------|---------|--------|
| `Variable not found in metadata` | LLM referenced non-existent variable | Review will catch this; approve with feedback |
| `PSPP syntax error` | Generated PSPP code is invalid | Check `output/pspp_logs.txt` |
| `Insufficient sample size` | Cell count too small for chi-square | Table marked as invalid; continues |
| `Max iterations exceeded` | Validation keeps failing | Review manually; provide guidance |

### 6.3 Getting Help

1. **Check logs**: `output/logs/` for detailed error messages
2. **Review PSPP output**: `output/pspp_logs.txt` for PSPP errors
3. **Verify input**: Ensure .sav file is valid SPSS format
4. **Check configuration**: Verify all required config values are set

### 6.4 Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python -m agent.graph --input survey.sav
```

---

## Related Documents

- **[Project Structure](./project-structure.md)** - Complete directory structure and file locations
- **[Data Flow](./data-flow.md)** - Workflow design and steps
- **[System Architecture](./system-architecture.md)** - System components and deployment
- **[Configuration](./configuration.md)** - Configuration options
- **[Technology Stack](./technology-stack.md)** - Technologies and versions
