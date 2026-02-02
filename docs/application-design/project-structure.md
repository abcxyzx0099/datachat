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

The project follows a clear separation between application code, configuration, input data, generated outputs, and web interface.

```
project-root/
├── agent/              # Application code
├── config/             # Configuration files
├── data/               # Input data
├── output/             # Generated outputs
├── docs/               # Documentation
├── tests/              # Test files
├── temp/               # Temporary files
├── web/                # Web interface (Next.js frontend)
├── tasks/              # Task specifications and planning
├── implementation/     # Implementation documentation
├── history/            # Archived materials
├── scripts/            # Shell scripts
├── utils/              # Project-wide utilities
├── reference/          # External reference materials
├── .claude/            # Claude skills configuration
├── .env                # Environment variables
├── checkpoints.db      # State persistence
├── pyproject.toml      # Project metadata
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
| `agent/` | Application source code (LangGraph agent) |
| `config/` | Configuration files (langgraph.json) |
| `data/` | Input survey files (.sav) |
| `output/` | Generated outputs and logs |
| `docs/` | Project documentation (application-design, user guides) |
| `tests/` | Unit and integration tests |
| `temp/` | Temporary files (one-time use) |
| `utils/` | Project-wide utility functions |
| `reference/` | External reference materials |
| `web/` | Web interface (Agent Chat UI - Next.js) |
| `tasks/` | Task specifications and planning documents |
| `implementation/` | Implementation documentation |
| `history/` | Archived materials and legacy documents |
| `scripts/` | Shell scripts (start.sh, stop.sh) |
| `.claude/` | Claude Code skills configuration |
| `.venv/` | Python virtual environment |
| `htmlcov/` | Code coverage reports (generated) |

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
├── server.py                     # FastAPI server for Agent Chat UI
├── styling.py                    # Output styling utilities
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
├── conftest.py                   # Pytest configuration and shared fixtures
├── test_state.py                 # TypedDict validation tests
├── test_nodes.py                 # Individual node tests
├── test_edges.py                 # Conditional routing tests
├── test_graph.py                 # End-to-end workflow tests
├── test_*.py                     # Additional test files (29+ total)
├── fixtures/                     # Test data and fixtures
│   └── sample_data.sav           # Sample SPSS file for testing
├── web/                          # Web UI test files
└── playwright-mcp/               # Playwright test results
```

### 3.5 web/ Directory

The `web/` directory contains the Agent Chat UI, a Next.js-based frontend for interacting with the agent.

```
web/
└── agent-chat-ui/                # Next.js frontend application
    ├── public/                   # Static assets
    ├── src/                      # Source code
    │   ├── app/                  # Next.js App Router pages
    │   ├── components/           # React components
    │   └── lib/                  # Utility libraries
    ├── e2e/                      # E2E tests (Playwright)
    ├── tests/                    # Additional test files
    ├── .next/                    # Next.js build output (generated)
    ├── node_modules/             # Dependencies (generated)
    ├── playwright-report/        # Playwright test reports (generated)
    ├── test-results/             # Test results (generated)
    ├── package.json              # Node.js dependencies
    ├── pnpm-lock.yaml            # Lock file
    ├── playwright.config.ts      # Playwright configuration
    ├── next.config.mjs           # Next.js configuration
    ├── tailwind.config.js        # Tailwind CSS configuration
    ├── tsconfig.json             # TypeScript configuration
    └── start.sh                  # Start script
```

### 3.6 tasks/ Directory

The `tasks/` directory contains task specifications and planning documents for the task implementation system.

```
tasks/
├── task-specifications/          # Generated task specification documents
│   └── task-{timestamp}-{summary}.md
├── task-planning/                # Task planning documents
└── task-archive/                 # Completed/archived tasks
```

### 3.7 implementation/ Directory

The `implementation/` directory contains implementation documentation created by AI agents during development.

```
implementation/
├── setup-summaries/              # Setup and configuration documentation
├── test-coverage/                # Test coverage reports
└── *.md                          # Implementation guides and notes
```

### 3.8 history/ Directory

The `history/` directory contains archived materials from completed projects and development waves.

```
history/
├── development/                  # Archived development materials
│   └── Archive-{description}-{timestamp}/
└── documents/                    # Archived documentation
    └── Archive-{description}-{timestamp}/
```

### 3.9 .claude/ Directory

The `.claude/` directory contains Claude Code skills configuration.

```
.claude/
└── skills/                       # Custom skills
    ├── task-worker/              # Task implementation workflow skill
    ├── task-implementation/      # Task implementation module
    ├── task-planning/            # Task planning skill
    ├── task-specification-generation/  # Task spec generation
    ├── task-cleanup/             # Task cleanup skill
    └── [other skills]/
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
    # LLM Configuration (defaults for Zhipu provider)
    "llm_provider": "ZHIPU",
    "model": "glm-4.7",
    "temperature": 0.1,
    "max_tokens": 4000,
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
       ├─────────────────┐
       │                 │
       ▼                 ▼
┌──────────────────┐  ┌─────────────────┐
│  output/         │  │  web/           │
│  ├── logs/       │  │  agent-chat-ui  │
│  ├── reviews/    │  │  (FastAPI →     │
│  ├── temp/       │  │   Next.js UI)   │
│  ├── *.pptx      │  └─────────────────┘
│  └── *.html      │           │
└──────────────────┘           │
                              ▼
                    ┌─────────────────┐
                    │  User Browser   │
                    │  (Agent Chat    │
                    │   Interface)    │
                    └─────────────────┘
```

**Web Interface Communication:**

```
┌─────────────────┐      HTTP/WebSocket      ┌──────────────────┐
│  web/           │ ◄────────────────────►  │  agent/server.py │
│  agent-chat-ui  │   Port 8123 (FastAPI)   │  (FastAPI)       │
│  (Next.js)      │                         └────────┬─────────┘
└─────────────────┘                                  │
                                                     │
                                                     ▼
                                            ┌─────────────────┐
                                            │  agent/graph.py │
                                            │  (LangGraph)    │
                                            └─────────────────┘
```

---

## 9. Server Ports and URLs

### 9.1 Development Ports

| Port | Service | Command | Purpose |
|------|---------|---------|---------|
| **2024** | LangGraph Studio | `langgraph dev` | Official dev server with Studio UI |
| **8123** | FastAPI Backend | `python -m agent.server` | Project-specific API wrapper for Agent Chat UI |
| **3000** | Frontend Dev | Vite dev server | Agent Chat UI development server |

### 9.2 Reverse Proxy URLs (with SSL)

When reverse proxy is configured with domain `sysy.site`:

| Service | URL |
|---------|-----|
| Frontend | `https://sysy.site/` |
| LangGraph Studio | `https://sysy.site/studio` |
| API Backend | `https://sysy.site/api` |

---

## 10. Related Documents

| Document | Content |
|----------|---------|
| **[Testing Structure](./testing-structure.md)** | Test organization and structure recommendations |
| **[Deployment](./deployment.md)** | Installation, environment configuration, and production deployment |
| **[Configuration](./system-configuration.md)** | Configuration options and environment variables |
| **[Data Flow](./data-flow.md)** | Workflow design and steps |
| **[System Architecture](./system-architecture.md)** | System components and architecture |
| **[Web Interface](./web-interface.md)** | Agent Chat UI setup and usage |
