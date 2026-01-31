# Technology Stack

This document defines the technologies, libraries, and tools used in the Survey Analysis & Visualization Workflow.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Core Technologies](#2-core-technologies)
3. [Python Libraries](#3-python-libraries)
4. [External Tools](#4-external-tools)
5. [Version Information](#5-version-information)

---

## 1. Overview

The system combines workflow orchestration (LangGraph), AI capabilities (OpenAI GPT-4), statistical computing (PSPP), and data processing (Python/pandas) into an integrated analysis pipeline.

### 1.1 Technology Stack Summary

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Workflow Orchestration** | LangGraph | State graph management, conditional routing |
| **AI/LLM** | OpenAI GPT-4 | Artifact generation |
| **Statistical Computing** | PSPP | Data recoding, cross-tabulation |
| **Data Processing** | Python, pandas | Data manipulation |
| **Statistical Tests** | scipy | Chi-square tests, effect size |
| **Presentation** | python-pptx | PowerPoint generation |
| **Visualization** | Chart.js | HTML dashboard charts |
| **Persistence** | SQLite | State checkpointing |

---

## 2. Core Technologies

### 2.1 LangGraph

| Property | Value |
|----------|-------|
| **Version** | 0.2+ |
| **Purpose** | State graph orchestration for workflow management |
| **Key Features** | StateGraph, conditional edges, interrupts, checkpointing |
| **Documentation** | https://langchain-ai.github.io/langgraph/ |

**Usage in System**:
- Manages 22-step workflow state
- Implements three-node pattern (Generate → Validate → Review)
- Handles human-in-the-loop interrupts
- Provides SQLite checkpointing for resumable execution

### 2.2 OpenAI GPT-4

| Property | Value |
|----------|-------|
| **Model** | gpt-4 or gpt-4-turbo |
| **Purpose** | Generate recoding rules, indicators, table specifications |
| **Integration** | langchain-openai |
| **Configuration** | `model`, `temperature`, `max_tokens` |

**Usage in System**:
- Step 4: Generate recoding rules
- Step 9: Generate indicators
- Step 12: Generate table specifications

### 2.3 PSPP

| Property | Value |
|----------|-------|
| **Version** | 1.6+ |
| **Purpose** | Statistical analysis (free SPSS alternative) |
| **Key Commands** | RECODE, CTABLES, EXPORT |
| **Documentation** | https://www.gnu.org/software/pspp/manual/ |

**Usage in System**:
- Step 8: Execute recoding, create new_data.sav
- Step 16: Generate cross-tabulation tables
- Compatible with SPSS .sav file format

---

## 3. Python Libraries

### 3.1 Data Processing

| Library | Version | Purpose |
|---------|---------|---------|
| **pandas** | 2.0+ | DataFrame manipulation, data analysis |
| **pyreadstat** | 1.2+ | Read/write SPSS .sav files |
| **numpy** | 1.24+ | Numerical computing |

### 3.2 Statistical Analysis

| Library | Version | Purpose |
|---------|---------|---------|
| **scipy** | 1.10+ | Chi-square tests, statistical functions |
| **statsmodels** | (optional) | Advanced statistical modeling |

### 3.3 Presentation & Visualization

| Library | Version | Purpose |
|---------|---------|---------|
| **python-pptx** | 0.6.21+ | PowerPoint presentation generation |
| **matplotlib** | 3.7+ | Chart generation for PPT |

### 3.4 Workflow & AI

| Library | Version | Purpose |
|---------|---------|---------|
| **langgraph** | 0.2+ | State graph orchestration |
| **langchain-openai** | 0.1+ | OpenAI LLM integration |
| **langchain-core** | 0.1+ | Core LangChain types and utilities |

### 3.5 Utilities

| Library | Version | Purpose |
|---------|---------|---------|
| **python-dotenv** | 1.0+ | Environment variable management |
| **jsonschema** | 4.0+ | JSON validation for LLM outputs |
| **pydantic** | 2.0+ | Data validation and settings |

---

## 4. External Tools

### 4.1 PSPP Statistical Software

| Property | Value |
|----------|-------|
| **Website** | https://www.gnu.org/software/pspp/ |
| **License** | GPL (free, open-source) |
| **Installation** | `apt-get install pspp` (Linux), `brew install pspp` (macOS) |
| **Executable** | `/usr/bin/pspp` (default) |

**Comparison with SPSS**:

| Feature | PSPP | SPSS |
|---------|------|------|
| Basic statistics | ✓ | ✓ |
| Data recoding | ✓ | ✓ |
| Cross-tabulation | ✓ | ✓ |
| Significance tests | ✓ | ✓ |
| Custom Tables | Partial | Full |
| Advanced modeling | Limited | Full |
| Cost | Free | Paid |
| License | GPL | Proprietary |

### 4.2 SQLite

| Property | Value |
|----------|-------|
| **Version** | 3.38+ (built into Python) |
| **Purpose** | Checkpoint persistence for LangGraph |
| **File** | `checkpoints.db` |

---

## 5. Version Information

### 5.1 Python Requirements

```txt
# Core dependencies
langgraph>=0.2.0
langchain-openai>=0.1.0
langchain-core>=0.1.0

# Data processing
pandas>=2.0.0
pyreadstat>=1.2.0
numpy>=1.24.0

# Statistical analysis
scipy>=1.10.0

# Presentation
python-pptx>=0.6.21
matplotlib>=3.7.0

# Utilities
python-dotenv>=1.0.0
jsonschema>=4.0.0
pydantic>=2.0.0
```

### 5.2 System Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| **Python** | 3.10 | 3.11+ |
| **Memory** | 4 GB | 8 GB+ |
| **Disk** | 10 GB | 20 GB+ |
| **PSPP** | 1.6 | 2.0+ |

### 5.3 API Requirements

| Service | Requirement |
|---------|-------------|
| **OpenAI API** | API key with GPT-4 access |
| **Rate Limits** | 10,000+ TPM recommended for production |

---

## 6. PSPP Syntax Reference

### 6.1 Key Commands Used

| Command | Purpose | Example |
|---------|---------|---------|
| **GET FILE** | Load .sav file | `GET FILE='data.sav'.` |
| **RECODE** | Transform variables | `RECODE age (18-24=1) (25-34=2).` |
| **VARIABLE LABELS** | Add variable labels | `VARIABLE LABELS age_grp 'Age Group'.` |
| **VALUE LABELS** | Add value labels | `VALUE LABELS age_grp 1 '18-24' 2 '25-34'.` |
| **CTABLES** | Cross-tabulation | `CTABLES /TABLES gender BY age_grp.` |
| **EXPORT** | Export to CSV/JSON | `EXPORT OUTFILE='output.csv'.` |
| **SAVE OUTFILE** | Save .sav file | `SAVE OUTFILE='new_data.sav'.` |

> **For complete PSPP manual**, see [reference/external-official-manual/PSPP-syntax/pspp_manual.txt](../reference/external-official-manual/PSPP-syntax/pspp_manual.txt) or https://www.gnu.org/software/pspp/manual/

---

## Related Documents

- **[Deployment](./deployment.md)** - Installation, environment configuration, and operations
- **[Web Interface](./web-interface.md)** - Agent Chat UI setup and usage
- **[Project Structure](./project-structure.md)** - Complete directory structure and file locations
- **[Data Flow](./data-flow.md)** - Workflow design and step specifications
- **[System Architecture](./system-architecture.md)** - System components and architecture
- **[Configuration](./configuration.md)** - Configuration options
- **[Product Features and Usage](./features-and-usage.md)** - Product introduction for end users
- **[Useful References](./useful-references.md)** - External documentation links
