---
name: analyzer-question-extraction
description: 'Stage 2: Question Extraction - Extract question codes from variable names and group variables by question. Outputs questions.json for indicator generation.'
license: Apache-2.0
---

# Analyzer Question Extraction

> **Question Extraction** - Group variables by question code for batch processing

## Overview

Extracts question codes from SPSS variable names and groups variables by question. This enables **batch processing** for indicator generation instead of single large API calls.

**Output**: `questions.json` - Ready for Stage 2 (Table Specification)

## Why This Step?

| Problem | Solution |
|---------|----------|
| Single API call with 345 variables exceeds model output limits | Split into smaller, question-based calls |
| One failure loses all progress | Each question saved individually |
| Can't resume from where processing stopped | Checkpoint after each question |

## When to Use

Use this skill when:
- Completing Stage 1 (Data Preparation) and ready for Stage 2
- Need to prepare for batch indicator generation
- Want checkpointing capability for indicator generation

## Usage

**Important**: Run commands from the project root directory (where `output/` is located).

```
User: Extract questions from filtered metadata

Assistant: [Extracting Question Codes]
           Working directory: /home/admin/workspaces/datachat
           Reading: output/filtered_metadata.json
           Found 345 variables

           Extracting question codes...
           - Q2A: Q2A_1_bin, Q2A_2_bin, Q2A_3_bin, Q2A_4_bin
           - S0: S0_cat
           - D1: D1_1_bin, D1_2_bin, D1_3_bin
           ... (45 questions total)

           Saved: output/questions.json
           ✓ Ready for batch indicator generation
```

## CLI Commands

### Working Directory

All commands should be run from the **project root directory**:

```bash
cd /home/admin/workspaces/datachat
```

### Extract Questions

```bash
# Using the survey_analyzer CLI (from project root)
python -m survey_analyzer questions extract \
  --metadata-file output/filtered_metadata.json \
  --output-file output/questions.json
```

## Input

| Input | Required | Description |
|-------|----------|-------------|
| `--metadata-file` | Yes | Path to `filtered_metadata.json` from Stage 1 |
| `--output-file` | No | Output path (default: `output/questions.json`) |

## Output

### questions.json

```jsonc
{
  "metadata": {
    "generated_at": "2025-02-25T12:00:00",
    "source_file": "output/filtered_metadata.json",
    "total_questions": 45,
    "total_variables": 345
  },
  "questions": [
    {
      "question_code": "Q2A",
      "variables": ["Q2A_1_bin", "Q2A_2_bin", "Q2A_3_bin", "Q2A_4_bin"]
    },
    {
      "question_code": "S0",
      "variables": ["S0_cat"]
    }
  ]
}
```

**Fields:**
| Field | Description | Source |
|-------|-------------|--------|
| `question_code` | Letters before `_` in variable name | Extracted from variable names |
| `variables` | List of variables belonging to this question | Grouped by question_code |

## Library Module

| Module | Purpose |
|---------|---------|
| `survey_analyzer.questions` | Question extraction and variable grouping |

## Question Code Extraction Logic

| Variable Name | Question Code | Logic |
|---------------|---------------|-------|
| `Q2A_1_bin` | `Q2A` | Split at `_`, take first part |
| `S0_cat` | `S0` | Split at `_`, take first part |
| `weight_var` | `weight_var` | No `_`, use full name |

## Updated Data Flow

```
Stage 1 (analyzer-data-prep)
    ↓
filtered_metadata.json
    ↓
*** Stage 2: Question Extraction ***
    ↓
questions.json
    ↓
Stage 2 (analyzer-tablespec-gen)
    For each question in questions.json:
        → Generate indicator → Update table_specification.jsonc
    ↓
Stage 3-5 (unchanged)
```

## Implementation Plan

**Status:** ✅ Implementation Complete

The library module has been implemented at:
```
survey_analyzer/questions/
├── __init__.py
└── questions.py
```

**Key classes:**
- `QuestionExtractor` - Extract question codes and group variables by question

**Usage:**
```python
from survey_analyzer.questions import QuestionExtractor

extractor = QuestionExtractor()
questions = extractor.extract_from_file(
    "output/filtered_metadata.json",
    "output/questions.json"
)
```

## Related Skills

| Skill | Previous/Next Stage |
|-------|---------------------|
| `analyzer-data-prep` | Previous: Produces filtered_metadata.json |
| `analyzer-tablespec-gen` | Next: Uses questions.json for batch generation |

## References

| Resource | Location |
|----------|----------|
| Data Flow Document | `docs/data-related/data-flow.md` |
| System Architecture | `docs/application-design/system-architecture.md` |

## Technology Stack

| Component | Technology |
|-----------|------------|
| **Question Extraction** | Python stdlib (json, collections, pathlib) |
| **Coordination** | Claude Code Skills |
