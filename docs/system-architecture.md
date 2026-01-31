# System Architecture

This document describes the system architecture, components, and deployment for the Survey Analysis & Visualization Workflow.

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Component Architecture](#2-component-architecture)
3. [Module Organization](#3-module-organization)
4. [Deployment Architecture](#4-deployment-architecture)
5. [Error Handling & Recovery](#5-error-handling--recovery)

---

## 1. System Overview

The system is a LangGraph-based workflow application that automates survey data analysis for market research professionals.

### 1.1 Architecture Type

| Aspect | Description |
|--------|-------------|
| **Pattern** | State-based workflow with human-in-the-loop |
| **Execution Model** | Sequential with conditional branching |
| **State Management** | TypedDict-based evolving state |
| **Persistence** | SQLite checkpointing for resumable execution |

### 1.2 System Boundaries

```mermaid
graph TB
    subgraph SYSTEM["Survey Analysis System"]
        INPUT["Input<br/>.sav file"]
        WORKFLOW["LangGraph<br/>Workflow"]
        OUTPUT["Outputs<br/>.pptx, .html"]
        SERVICES["External Services<br/>- LLM API<br/>- PSPP"]

        INPUT --> WORKFLOW
        WORKFLOW --> OUTPUT
        WORKFLOW --> SERVICES
    end

    style SYSTEM fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    style WORKFLOW fill:#fff9c4,stroke:#f57f17,stroke-width:2px
    style SERVICES fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
```

---

## 2. Component Architecture

### 2.1 Core Components

| Component | Responsibility | Technology |
|-----------|----------------|------------|
| **Workflow Engine** | Orchestrates 22-step workflow, manages state | LangGraph |
| **Node Executors** | Implements individual workflow steps | Python |
| **Validation Layer** | Validates LLM-generated artifacts | Python |
| **State Manager** | Maintains evolving workflow state | TypedDict |
| **Checkpoint Service** | Persists state for resumable execution | SQLite |
| **LLM Client** | Communicates with OpenAI API | langchain-openai |
| **PSPP Executor** | Runs statistical operations | subprocess + PSPP |

### 2.2 Component Interaction

```mermaid
flowchart LR
    USER[User] --> INPUT[.sav file]
    INPUT --> WORKFLOW[LangGraph Workflow]

    WORKFLOW --> LLM[LLM API]
    WORKFLOW --> PSPP[PSPP Executor]
    WORKFLOW --> CHECKPOINT[SQLite Checkpoint]

    WORKFLOW --> OUTPUT[Outputs]
    OUTPUT --> USER

    WORKFLOW --> HUMAN[Human Review]
    HUMAN --> WORKFLOW
```

---

## 3. Module Organization

### 3.1 Module Responsibilities

| Module | Responsibility |
|--------|---------------|
| **state.py** | Defines all TypedDict state classes and combined WorkflowState |
| **graph.py** | Constructs StateGraph, adds nodes/edges, compiles with checkpointer |
| **edges.py** | Conditional routing functions for three-node pattern feedback loops |
| **nodes/** | Implements all 22 workflow steps organized by phase |
| **utils/** | PSPP wrapper, file I/O, statistical computation helpers |
| **validation/** | Validation logic for recoding rules, indicators, table specs |
| **llm/** | Prompt templates and LLM client initialization |

> **For complete directory structure and file organization**, see [Project Structure](./project-structure.md).

---

## 4. Deployment Architecture

### 4.1 Deployment Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| **Local** | Single-machine execution | Development, small-scale analysis |
| **Containerized** | Docker container with PSPP pre-installed | Production, reproducible environments |
| **Cloud** | Cloud-based deployment with remote PSPP service | Multi-user SaaS |

### 4.2 Local Deployment Requirements

| Requirement | Specification |
|-------------|---------------|
| **Python** | 3.10+ |
| **PSPP** | 1.6+ (installed at `/usr/bin/pspp`) |
| **Memory** | 4GB+ recommended |
| **Disk** | 10GB+ for temporary files |
| **API Keys** | OpenAI API key |

### 4.3 Environment Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install PSPP (Ubuntu/Debian)
sudo apt-get install pspp

# Configure environment
export OPENAI_API_KEY="your-key-here"
export PSPP_PATH="/usr/bin/pspp"
```

> **For deployment directory structure and file locations**, see [Project Structure](./project-structure.md).

---

## 5. Error Handling & Recovery

### 5.1 Error Categories

| Category | Examples | Handling Strategy |
|----------|----------|-------------------|
| **LLM Errors** | Rate limits, API failures | Retry with exponential backoff |
| **Validation Errors** | Invalid references, syntax errors | Automatic retry up to max_iterations, then continue with warning |
| **PSPP Errors** | Syntax errors, file not found | Parse PSPP output logs, provide specific error messages |
| **File I/O Errors** | Missing files, permission errors | Validate paths before execution, fail gracefully |
| **Statistical Errors** | Insufficient sample size | Warn and continue, mark table as invalid |

### 5.2 Logging Strategy

| Log Level | Usage | Storage |
|-----------|-------|---------|
| **INFO** | Step start, completion, key outputs | `output/logs/` |
| **WARNING** | Validation failures, skipped items | `output/logs/` + state |
| **ERROR** | Exceptions, failures | `output/logs/` + state |
| **DEBUG** | Detailed execution trace | `output/logs/debug/` |

### 5.3 Recovery Mechanisms

| Mechanism | Purpose |
|-----------|---------|
| **SQLite Checkpointing** | Resume after human interrupt or crash |
| **Automatic Retry** | Validation errors trigger LLM regeneration |
| **Graceful Degradation** | Continue with warnings on non-critical failures |
| **State Snapshots** | Save state before each three-node pattern |

---

## Related Documents

- **[Project Structure](./project-structure.md)** - Complete directory structure and file locations
- **[Data Flow](./data-flow.md)** - Workflow design and step specifications
- **[Technology Stack](./technology-stack.md)** - Technologies and versions
- **[Configuration](./configuration.md)** - Configuration options and langgraph.json
- **[Usage](./usage.md)** - User guide and examples
