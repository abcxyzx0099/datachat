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
├── temp/               # Temporary files and development artifacts
├── utils/              # Project-wide utility functions
├── reference/          # External reference materials
├── web/                # Web interface (Agent Chat UI)
├── tasks/              # Task planning and execution
├── scripts/            # Utility scripts
├── history/            # Archival storage
├── implementation/     # Implementation documentation
├── logs/               # Server logs
├── .env                # Environment variables
├── checkpoints.db      # State persistence
├── langgraph.json      # LangGraph configuration (at root)
└── requirements.txt    # Python dependencies
```

---

## 2. Project Root Structure

### 2.1 Root Level Files

| File | Purpose |
|------|---------|
| `.env` | Environment variables (API keys, paths) |
| `checkpoints.db` | LangGraph state persistence for resumable execution |
| `langgraph.json` | LangGraph node/edge configuration |
| `requirements.txt` | Python dependencies |
| `pyproject.toml` | Project metadata and dependencies |

### 2.2 Root Level Directories

| Directory | Purpose |
|-----------|---------|
| `agent/` | Application source code |
| `config/` | Configuration files |
| `data/` | Input survey files (.sav) |
| `output/` | Generated outputs and logs |
| `docs/` | Project documentation |
| `tests/` | Unit and integration tests |
| `temp/` | Temporary files and development artifacts |
| `utils/` | Project-wide utility functions |
| `reference/` | External reference materials |
| `web/` | Web interface (Agent Chat UI) |
| `tasks/` | Task planning and execution |
| `scripts/` | Utility scripts |
| `history/` | Archival storage |
| `implementation/` | Implementation documentation |
| `logs/` | Server logs |

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
├── server.py                     # FastAPI server wrapper
├── styling.py                    # Output styling utilities
│
├── utils/                        # Module-specific utilities
│   ├── __init__.py
│   ├── pspp_wrapper.py           # PSPP execution
│   ├── file_io.py                # File I/O utilities
│   ├── statistics.py             # Statistical computations
│   ├── security.py               # Security utilities
│   └── tracing.py                # Tracing utilities
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
    ├── __init__.py               # Exports all nodes
    ├── phase1_extraction.py      # Steps 1-3
    ├── phase2_recoding.py        # Steps 4-8
    ├── phase3_indicators.py      # Steps 9-11
    ├── phase4_tables.py          # Steps 12-16
    ├── phase5_statistics.py      # Steps 17-18
    ├── phase6_filtering.py       # Steps 19-20
    ├── phase7_powerpoint.py      # Step 21
    └── phase8_html_dashboard.py  # Step 22
```

### 3.2 utils/ Directory (Project-Wide)

```
utils/
├── __init__.py
└── logging.py                    # Logging configuration
```

### 3.3 config/ Directory

```
config/
├── __init__.py
└── langgraph.json                # LangGraph node/edge configuration
```

**Note:** `langgraph.json` is also symlinked or copied to the project root for LangGraph Studio compatibility.

### 3.4 tests/ Directory

```
tests/
├── __init__.py
├── conftest.py                   # Pytest fixtures and configuration
├── test_*.py                     # Unit and integration tests
├── fixtures/                     # Test fixtures and sample data
├── performance/                  # Performance and load tests
├── security/                     # Security tests
├── web/                          # Web interface tests
└── playwright-mcp/               # Playwright MCP test results
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
├── pspp_syntax/                  # Generated PSPP syntax files (dynamic)
├── scripts/                      # Generated Python scripts (dynamic)
├── filters/                      # Generated filter lists (dynamic)
├── coverage_*/                   # Coverage reports (development artifacts)
└── *.py, *.sh, *.md              # Various development scripts and reports
```

**Note**: `temp/` contains both dynamic generated files (can be deleted after workflow) and development artifacts (coverage reports, security scans, test scripts).

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

> **For complete LLM provider configuration**, see [Configuration](./system-configuration.md#2-llm-provider-configuration).

```bash
# Required - Select your LLM provider
LLM_PROVIDER=ZHIPU  # Options: KIMI, DEEPSEEK, ZHIPU

# Required - Add API key for your selected provider
ZHIPU_API_KEY=your-zhipu-api-key-here

# Optional (override defaults)
PSPP_PATH=/usr/bin/pspp
OUTPUT_DIR=output
TEMP_DIR=temp
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=4000
ENABLE_HUMAN_REVIEW=true
```

### 6.2 LangGraph Configuration

**Location:** `langgraph.json` (at project root, also in `config/`)

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
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  agent/                                │
│  (nodes → utils → validation → llm)     │
│  ↓                                     │
│  Uses config/ and langgraph.json        │
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

       ↕
┌─────────────────────────────────────────┐
│  web/ (Agent Chat UI)                   │
│  ← API via agent/server.py              │
└─────────────────────────────────────────┘
```

---

## Related Documents

| Document | Content |
|----------|---------|
| **[Deployment](./deployment.md)** | Installation, environment configuration, and production deployment |
| **[Configuration](./system-configuration.md)** | Configuration options and environment variables |
| **[Data Flow](./data-flow.md)** | Workflow design and steps |
| **[System Architecture](./system-architecture.md)** | System components and architecture |
| **[Web Interface](./web-interface.md)** | Agent Chat UI setup and usage |
