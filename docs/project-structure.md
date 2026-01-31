# Project Structure

This document defines the complete project structure, directory organization, and file locations.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Project Root Structure](#2-project-root-structure)
3. [Application Code Structure](#3-application-code-structure)
4. [Output Files](#4-output-files)
5. [Temporary Files](#5-temporary-files)
6. [Configuration Files](#6-configuration-files)
7. [File Naming Conventions](#7-file-naming-conventions)
8. [Data Flow Between Directories](#8-data-flow-between-directories)

---

## 1. Overview

The project follows a clear separation between application code, configuration, input data, and generated outputs.

```
project-root/
├── agent/              # Application code
├── config/             # Configuration files
├── data/               # Input data
├── output/             # Generated outputs
├── docs/               # Documentation
├── tests/              # Test files
├── temp/               # Temporary files
├── .env                # Environment variables
├── checkpoints.db      # State persistence
└── requirements.txt    # Python dependencies
```

---

## 2. Project Root Structure

### 2.1 Root Level Files

| File | Purpose |
|------|---------|
| `.env` | Environment variables (API keys, paths) |
| `checkpoints.db` | LangGraph state persistence for resumable execution |
| `requirements.txt` | Python dependencies |
| `pyproject.toml` | Project metadata and dependencies (optional) |

### 2.2 Root Level Directories

| Directory | Purpose |
|-----------|---------|
| `agent/` | Application source code |
| `config/` | Configuration files (langgraph.json) |
| `data/` | Input survey files (.sav) |
| `output/` | Generated outputs and logs |
| `docs/` | Project documentation |
| `tests/` | Unit and integration tests |
| `temp/` | Temporary files (one-time use) |
| `utils/` | Project-wide utility functions |
| `reference/` | External reference materials |

---

## 3. Application Code Structure

### 3.1 agent/ Directory

```
agent/
├── __init__.py                   # Package exports
├── state.py                      # TypedDict state definitions
├── config.py                     # Configuration constants
├── edges.py                      # Conditional routing logic
├── graph.py                      # LangGraph construction
│
├── utils/                        # Module-specific utilities
│   ├── __init__.py
│   ├── pspp_wrapper.py           # PSPP execution
│   ├── file_io.py                # File I/O utilities
│   └── statistics.py             # Statistical computations
│
├── validation/                   # Validation functions
│   ├── __init__.py
│   ├── recoding.py               # Recoding rule validation
│   ├── indicators.py             # Indicator validation
│   └── tables.py                 # Table specification validation
│
├── llm/                          # LLM modules
│   ├── __init__.py
│   ├── prompts.py                # Prompt templates
│   └── clients.py                # LLM client initialization
│
└── nodes/                        # Node implementations (phase-based)
    ├── __init__.py               # Exports all 22 nodes
    ├── phase1_extraction.py      # Steps 1-3   (~150 lines)
    ├── phase2_recoding.py        # Steps 4-8   (~400 lines)
    ├── phase3_indicators.py      # Steps 9-11  (~200 lines)
    ├── phase4_tables.py          # Steps 12-16 (~350 lines)
    ├── phase5_statistics.py      # Steps 17-18 (~150 lines)
    ├── phase6_filtering.py       # Steps 19-20 (~120 lines)
    ├── phase7_powerpoint.py      # Step 21     (~100 lines)
    └── phase8_html_dashboard.py  # Step 22     (~100 lines)
```

### 3.2 utils/ Directory (Project-Wide)

```
utils/
├── __init__.py
├── logging.py                    # Logging configuration
└── helpers.py                    # General helper functions
```

### 3.3 config/ Directory

```
config/
├── __init__.py
├── default.py                    # DEFAULT_CONFIG constants
└── langgraph.json                # LangGraph node/edge configuration
```

### 3.4 tests/ Directory

```
tests/
├── __init__.py
├── test_state.py                 # TypedDict validation tests
├── test_nodes.py                 # Individual node tests
├── test_edges.py                 # Conditional routing tests
├── test_graph.py                 # End-to-end workflow tests
└── fixtures/
    └── sample_data.sav           # Sample SPSS file for testing
```

---

## 4. Output Files

### 4.1 output/ Directory Structure

```
output/
├── logs/                         # Execution logs
│   └── {timestamp}.log
├── reviews/                      # Human review documents
│   ├── recoding_rules_review.md
│   ├── indicators_review.md
│   └── table_specs_review.md
└── temp/                         # Temporary generated files
    ├── {step}_syntax.sps         # PSPP syntax files
    ├── stats_script.py           # Generated Python scripts
    └── filter_list.json          # Significance filters
```

### 4.2 Generated Output Files

| File Type | Location | Description |
|-----------|----------|-------------|
| **PowerPoint** | `output/survey_analysis.pptx` | Executive summary with significant tables |
| **HTML Dashboard** | `output/dashboard.html` | Interactive dashboard with all tables |
| **Cross Tables CSV** | `output/cross_tables.csv` | Raw cross-tabulation data |
| **Cross Tables JSON** | `output/cross_tables.json` | Table metadata |
| **Statistical Summary** | `output/statistical_summary.json` | Chi-square tests, Cramer's V |
| **Filtered Tables** | `output/significant_tables.csv`, `.json` | Significant tables only |

### 4.3 Review Documents

| Artifact | Review File Location |
|----------|---------------------|
| **Recoding Rules** | `output/reviews/recoding_rules_review.md` |
| **Indicators** | `output/reviews/indicators_review.md` |
| **Table Specifications** | `output/reviews/table_specs_review.md` |

### 4.4 Execution Logs

| Log Type | Location | Content |
|----------|----------|---------|
| **Execution Log** | `output/logs/{timestamp}.log` | Step-by-step execution trace |
| **PSPP Log** | `output/pspp_logs.txt` | PSPP output and errors |
| **Debug Log** | `output/logs/debug/{timestamp}.log` | Detailed debug information |

---

## 5. Temporary Files

### 5.1 temp/ Directory

```
temp/
├── pspp_syntax/                  # Generated PSPP syntax files
├── scripts/                      # Generated Python scripts
└── filters/                      # Generated filter lists
```

**Note**: Files in `temp/` can be safely deleted after workflow completion.

### 5.2 Generated Temporary Files

| File Type | Location | Description |
|-----------|----------|-------------|
| **PSPP Recoding Syntax** | `temp/pspp_syntax/recoding.sps` | Generated recoding syntax |
| **PSPP Table Syntax** | `temp/pspp_syntax/tables.sps` | Generated table syntax |
| **Statistics Script** | `temp/scripts/stats_script.py` | Generated statistics script |
| **Filter List** | `temp/filters/filter_list.json` | Significance filter criteria |

---

## 6. Configuration Files

### 6.1 Environment Configuration (.env)

```bash
# Required
OPENAI_API_KEY=sk-your-api-key-here

# Optional (override defaults)
PSPP_PATH=/usr/bin/pspp
OUTPUT_DIR=output
TEMP_DIR=temp
MODEL=gpt-4
TEMPERATURE=0.7
ENABLE_HUMAN_REVIEW=true
```

### 6.2 LangGraph Configuration (config/langgraph.json)

```json
{
  "graphs": {
    "survey_analysis": {
      "nodes": { /* 22 node definitions */ },
      "edges": { /* Linear edges */ },
      "conditional_edges": { /* Three-node pattern routing */ }
    }
  }
}
```

### 6.3 Python Configuration (config/default.py)

```python
DEFAULT_CONFIG = {
    "model": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 2000,
    "max_self_correction_iterations": 3,
    "enable_human_review": True,
    "pspp_path": "/usr/bin/pspp",
    # ... additional config
}
```

---

## 7. File Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| **Phase files** | `phase{N}_{purpose}.py` | `phase2_recoding.py` |
| **Node functions** | `{operation}_{entity}_node` | `extract_spss_node` |
| **State classes** | `{Purpose}State` | `ExtractionState`, `RecodingState` |
| **Utility modules** | `lowercase_with_underscores` | `pspp_wrapper.py` |
| **Review documents** | `{artifact}_review.md` | `recoding_rules_review.md` |
| **Log files** | `{timestamp}.log` | `20240131_143022.log` |
| **Output files** | `{name}.{ext}` | `survey_analysis.pptx` |

---

## 8. Data Flow Between Directories

```
┌─────────────┐
│  data/      │  Input: .sav files
│  input/     │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  agent/                                │
│  (nodes → utils → validation → llm)     │
│  ↓                                     │
│  Uses config/ for configuration        │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  output/                               │
│  ├── logs/      (execution traces)      │
│  ├── reviews/   (human review docs)     │
│  ├── temp/      (generated files)       │
│  ├── *.pptx     (final presentation)    │
│  └── *.html     (dashboard)             │
└─────────────────────────────────────────┘
```

---

## Related Documents

| Document | Content |
|----------|---------|
| **[Deployment](./deployment.md)** | Installation, environment configuration, and production deployment |
| **[Configuration](./configuration.md)** | Configuration options and environment variables |
| **[Data Flow](./data-flow.md)** | Workflow design and steps |
| **[System Architecture](./system-architecture.md)** | System components and architecture |
| **[Web Interface](./web-interface.md)** | Agent Chat UI setup and usage |
