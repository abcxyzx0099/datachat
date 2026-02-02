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

The system combines workflow orchestration (LangGraph), multi-provider AI capabilities (Kimi, DeepSeek, Zhipu GLM), statistical computing (PSPP), and data processing (Python/pandas) into an integrated analysis pipeline.

### 1.1 Technology Stack Summary

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Workflow Orchestration** | LangGraph | State graph management, conditional routing |
| **AI/LLM** | Multi-Provider LLM (Kimi, DeepSeek, Zhipu GLM) | Artifact generation |
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
| **Version** | 1.0.7+ |
| **Purpose** | State graph orchestration for workflow management |
| **Key Features** | StateGraph, conditional edges, interrupts, checkpointing |
| **Documentation** | https://langchain-ai.github.io/langgraph/ |

**Usage in System**:
- Manages 22-step workflow state
- Implements three-node pattern (Generate → Validate → Review)
- Handles human-in-the-loop interrupts
- Provides SQLite checkpointing for resumable execution

### 2.2 Multi-Provider LLM Support

The system supports multiple LLM providers through a unified integration layer. Select your preferred provider using the `LLM_PROVIDER` environment variable.

| Provider | `LLM_PROVIDER` Value | Base URL |
|----------|----------------------------|----------|
| **Kimi (Moonshot AI)** | `KIMI` | `https://api.moonshot.cn/v1` |
| **DeepSeek** | `DEEPSEEK` | `https://api.deepseek.com/v1` |
| **Zhipu GLM (BigModel)** | `ZHIPU` | `https://open.bigmodel.cn/api/coding/paas/v4` |

| Property | Value |
|----------|-------|
| **Purpose** | Generate recoding rules, indicators, table specifications |
| **Integration** | LangChain with provider-specific chat models |
| **Configuration** | `LLM_PROVIDER`, provider API keys, `temperature`, `max_tokens` |
| **Documentation** | See [Configuration](./system-configuration.md#2-llm-provider-configuration) |

**Usage in System**:
- Step 4: Generate recoding rules
- Step 9: Generate indicators
- Step 12: Generate table specifications

**Provider Selection**:
```bash
# In .env file
LLM_PROVIDER=ZHIPU  # Options: KIMI, DEEPSEEK, ZHIPU
```

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
| **pandas** | 3.0.0+ | DataFrame manipulation, data analysis |
| **pyreadstat** | 1.3.3+ | Read/write SPSS .sav files |
| **numpy** | 2.4.2+ | Numerical computing |

### 3.2 Statistical Analysis

| Library | Version | Purpose |
|---------|---------|---------|
| **scipy** | 1.17.0+ | Chi-square tests, statistical functions |
| **statsmodels** | (optional) | Advanced statistical modeling |

### 3.3 Presentation & Visualization

| Library | Version | Purpose |
|---------|---------|---------|
| **python-pptx** | 1.0.2+ | PowerPoint presentation generation |
| **matplotlib** | 3.10.8+ | Chart generation for PPT |

### 3.4 Workflow & AI

| Library | Version | Purpose |
|---------|---------|---------|
| **langgraph** | 1.0.7+ | State graph orchestration |
| **langchain-core** | 1.2.7+ | Core LangChain types and utilities |
| **langchain-openai** | 1.1.7+ | OpenAI-compatible LLM integrations |
| **langchain-community** | (optional) | Community integrations for additional LLM providers |

### 3.5 Utilities

| Library | Version | Purpose |
|---------|---------|---------|
| **python-dotenv** | 1.2.1+ | Environment variable management |
| **jsonschema** | 4.26.0+ | JSON validation for LLM outputs |
| **pydantic** | 2.12.5+ | Data validation and settings |

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

> **Note**: Package versions verified and updated as of 2026-02-01. All versions represent the latest stable releases available on PyPI.

```txt
# Core dependencies
langgraph>=1.0.7
langchain-core>=1.2.7
langchain-openai>=1.1.7

# LLM providers (install based on your chosen provider)
# For Kimi: langchain-openai (compatible with Kimi's OpenAI-like API)
# For DeepSeek: openai (DeepSeek provides OpenAI-compatible API)
# For Zhipu: zhipuai (official Zhipu SDK)
openai>=2.16.0

# Data processing
pandas>=3.0.0
pyreadstat>=1.3.3
numpy>=2.4.2

# Statistical analysis
scipy>=1.17.0

# Presentation
python-pptx>=1.0.2
matplotlib>=3.10.8

# Utilities
python-dotenv>=1.2.1
jsonschema>=4.26.0
pydantic>=2.12.5
```

### 5.2 System Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| **Python** | 3.13 | 3.13+ |
| **Memory** | 4 GB | 8 GB+ |
| **Disk** | 10 GB | 20 GB+ |
| **PSPP** | 1.6 | 2.0+ |

### 5.3 API Requirements

| Service | Requirement |
|---------|-------------|
| **LLM Provider API** | API key for your chosen provider (Kimi, DeepSeek, or Zhipu GLM) |
| **Provider Selection** | Configure via `LLM_PROVIDER` environment variable |
| **Rate Limits** | Provider-specific; consult your chosen provider's documentation |
| **Setup** | See [Configuration](./system-configuration.md#2-llm-provider-configuration) for detailed setup |

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
- **[Configuration](./system-configuration.md)** - Configuration options
- **[Product Features and Usage](./features-and-usage.md)** - Product introduction for end users
- **[Useful References](./useful-references.md)** - External documentation links
