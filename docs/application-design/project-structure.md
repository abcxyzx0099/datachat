# Project Structure

This document defines the complete project structure, directory organization, and file locations.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Project Root Structure](#2-project-root-structure)
3. [Application Code Structure](#3-application-code-structure)
4. [Output Files](#4-output-files)
5. [Temporary Files](#5-temporary-files)
6. [Data Flow Between Directories](#6-data-flow-between-directories)

---

## 1. Overview

The project follows a clear separation between application code, configuration, input data, generated outputs, and web interface.

```
project-root/
├── agent/              # Application code
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
├── .claude/            # Claude skills configuration
├── .env                # Environment variables
├── checkpoints.db      # State persistence
├── langgraph.json      # LangGraph configuration
├── pyproject.toml      # Project metadata
├── dev-start.sh        # Development start script
├── dev-stop.sh         # Development stop script
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
| `dev-start.sh` | Development start script (Studio + API + UI) |
| `dev-stop.sh` | Development stop script |

### 2.2 Root Level Directories

| Directory | Purpose |
|-----------|---------|
| `agent/` | Application source code (LangGraph agent) |
| `data/` | Input survey files (.sav) |
| `output/` | Generated outputs and logs |
| `docs/` | Project documentation (application-design, user guides, reference materials) |
| `tests/` | Unit and integration tests |
| `temp/` | Temporary files (one-time use) |
| `utils/` | Project-wide utility functions |
| `web/` | Web interface (Agent Chat UI - Next.js) |
| `tasks/` | Task specifications and planning documents |
| `implementation/` | Implementation documentation |
| `history/` | Archived materials and legacy documents |
| `scripts/` | Shell scripts (production deployment) |
| `.claude/` | Claude Code skills configuration |
| `.venv/` | Python virtual environment |
| `htmlcov/` | Code coverage reports (generated) |

---

## 3. Application Code Structure

### 3.1 agent/ Directory

```
agent/
├── utils/                        # Module-specific utilities
├── validation/                   # Validation functions
├── llm/                          # LLM modules
└── nodes/                        # Node implementations (phase-based)
```

### 3.2 utils/ Directory (Project-Wide)

```
utils/
├── logging.py                    # Logging configuration
```

### 3.3 tests/ Directory

```
tests/
├── fixtures/                     # Test data and fixtures
├── web/                          # Web UI test files
└── playwright-mcp/               # Playwright test results
```

### 3.4 web/ Directory

The `web/` directory contains the Agent Chat UI, a Next.js-based frontend for interacting with the agent.

```
web/
└── agent-chat-ui/                # Next.js frontend application
    ├── public/                   # Static assets
    ├── src/                      # Source code
    ├── e2e/                      # E2E tests (Playwright)
    ├── tests/                    # Additional test files
    ├── .next/                    # Next.js build output (generated)
    ├── node_modules/             # Dependencies (generated)
    └── playwright-report/        # Playwright test reports (generated)
```

### 3.5 docs/ Directory

The `docs/` directory contains project documentation, including application design documents, user guides, and reference materials.

```
docs/
├── application-design/          # Application design documents
├── development/                 # Development configuration and setup
├── meta-governance/             # Meta-governance and conventions
├── methodology/                 # Methodology and process documents
└── reference/                   # External reference materials
    ├── external-official-manual/ # Official documentation
    └── knowledge/                # Knowledge base articles
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
└── test-coverage/                # Test coverage reports and AI-generated test documentation
    ├── E2E_IMPLEMENTATION_SUMMARY.md
    ├── E2E_TEST_GUIDE.md
    ├── FIXTURES.md
    ├── FIXTURE_SUMMARY.md
    ├── HUMAN_REVIEW_TEST_SUMMARY.md
    ├── INTEGRATION_TEST_SUMMARY.md
    └── LLM_PROVIDER_E2E_TEST_SUMMARY.md
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

## 6. Data Flow Between Directories

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
│  Configuration: agent/config.py         │
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
