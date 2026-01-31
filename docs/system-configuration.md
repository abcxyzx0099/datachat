# Configuration

This document describes all configuration options for the Survey Analysis & Visualization Workflow.

---

## Table of Contents

1. [Overview](#1-overview)
2. [LLM Provider Configuration](#2-llm-provider-configuration)
3. [Survey Analysis Workflow Configuration](#3-survey-analysis-workflow-configuration)
4. [Default Configuration](#4-default-configuration)
5. [Environment Variables](#5-environment-variables)
6. [LangGraph Configuration](#6-langgraph-configuration)

---

## 1. Overview

Configuration is managed through:
- **Python dict** (`DEFAULT_CONFIG` in `agent/config.py`)
- **Environment variables** (`.env` file)
- **LangGraph JSON** (`config/langgraph.json`)

### 1.1 Configuration Priority

```
Environment Variables → DEFAULT_CONFIG
```

Environment variables override default values.

---

## 2. LLM Provider Configuration

The application supports multiple LLM providers. Select your preferred provider using the `SURVEY_LLM_PROVIDER` environment variable.

### 2.1 Supported Providers

| Provider | `SURVEY_LLM_PROVIDER` Value | Base URL |
|----------|----------------------------|----------|
| **Kimi (Moonshot AI)** | `KIMI` | `https://api.moonshot.cn/v1` |
| **DeepSeek** | `DEEPSEEK` | `https://api.deepseek.com/v1` |
| **Zhipu GLM (BigModel)** | `ZHIPU` | `https://open.bigmodel.cn/api/coding/paas/v4` |

### 2.2 Provider-Specific Configuration

#### Kimi (Moonshot AI)

| Variable | Description | Example |
|----------|-------------|---------|
| `KIMI_API_KEY` | API key for Kimi | `sk-lwXxZiXh2wEfGqgJln3zMbiOPAUDxMYBe8iinRU9OYmbvT90` |
| `KIMI_BASE_URL` | Base URL for Kimi API | `https://api.moonshot.cn/v1` |
| `KIMI_MODEL` | Model to use | `kimi-k2-turbo-preview` |

#### DeepSeek

| Variable | Description | Example |
|----------|-------------|---------|
| `DEEPSEEK_API_KEY` | API key for DeepSeek | `sk-5ac0126d2291484f8c705ca80b2897f4` |
| `DEEPSEEK_BASE_URL` | Base URL for DeepSeek API | `https://api.deepseek.com/v1` |
| `DEEPSEEK_MODEL` | Model to use (`deepseek-chat` or `deepseek-reasoner`) | `deepseek-chat` |

#### Zhipu GLM (BigModel)

| Variable | Description | Example |
|----------|-------------|---------|
| `ZHIPU_API_KEY` | API key for Zhipu GLM | `cef62fd30a0e4ddf826ccba67b7a1e78.iSRcFQPBKBt4MQ52` |
| `ZHIPU_BASE_URL` | Base URL for Zhipu GLM API | `https://open.bigmodel.cn/api/coding/paas/v4` |
| `ZHIPU_MODEL` | Model to use | `glm-4.7` |

### 2.3 Provider Selection

```bash
# In .env file
SURVEY_LLM_PROVIDER=ZHIPU  # Options: KIMI, DEEPSEEK, ZHIPU
```

---

## 3. Survey Analysis Workflow Configuration

All survey analysis configuration options use the `SURVEY_` prefix.

### 3.1 LLM Parameters

| Variable | Description | Default |
|----------|-------------|---------|
| `SURVEY_LLM_PROVIDER` | LLM provider (`KIMI`, `DEEPSEEK`, `ZHIPU`) | `ZHIPU` |
| `SURVEY_LLM_TEMPERATURE` | Temperature for LLM responses (0.0-1.0) | `0.1` |
| `SURVEY_LLM_MAX_TOKENS` | Maximum tokens per LLM response | `4000` |

### 3.2 Preliminary Filtering

| Variable | Description | Default |
|----------|-------------|---------|
| `SURVEY_CARDINALITY_THRESHOLD` | Max distinct values before filtering as high-cardinality | `30` |
| `SURVEY_FILTER_BINARY` | Filter out binary variables (exactly 2 distinct values) | `true` |
| `SURVEY_FILTER_OTHER_TEXT` | Filter out "other" text fields (open-ended feedback) | `true` |

### 3.3 Recoding Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `SURVEY_RECODING_INSTRUCTIONS` | Custom instructions for AI recoding (optional) | *(uses default)* |
| `SURVEY_AUTO_APPROVE_RECODING` | Skip human review for recoding rules | `false` |

### 3.4 Indicator Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `SURVEY_INDICATOR_INSTRUCTIONS` | Custom instructions for AI indicator grouping (optional) | *(uses default)* |
| `SURVEY_AUTO_APPROVE_INDICATORS` | Skip human review for indicators | `false` |

### 3.5 Table Specifications

| Variable | Description | Default |
|----------|-------------|---------|
| `SURVEY_TABLE_INSTRUCTIONS` | Custom instructions for table generation (optional) | *(uses default)* |
| `SURVEY_WEIGHTING_VARIABLE` | Weighting variable name (empty for auto-detection) | *(auto-detect)* |
| `SURVEY_AUTO_APPROVE_TABLE_SPECS` | Skip human review for table specifications | `false` |

### 3.6 Significance Testing

| Variable | Description | Default |
|----------|-------------|---------|
| `SURVEY_SIGNIFICANCE_ALPHA` | p-value threshold for statistical significance | `0.05` |
| `SURVEY_TEST_TYPE` | Statistical test type (`chi_square`, `fisher_exact`) | `chi_square` |

### 3.7 Human Review / Approval

| Variable | Description | Default |
|----------|-------------|---------|
| `SURVEY_ENABLE_HUMAN_REVIEW` | Enable human-in-the-loop review | `true` |
| `SURVEY_REVIEW_OUTPUT_FORMAT` | Review report format (`markdown`, `html`, `json`) | `markdown` |

### 3.8 PSPP Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `SURVEY_PSPP_PATH` | Path to PSPP executable | `pspp` |

### 3.9 Output Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `SURVEY_OUTPUT_DIR` | Output directory (relative to project root) | `output` |
| `SURVEY_CREATE_TIMESTAMP_DIR` | Create timestamped subdirectories | `true` |

### 3.10 PowerPoint Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `SURVEY_PPT_TEMPLATE` | Path to custom .pptx template (optional) | *(uses default)* |
| `SURVEY_CHART_STYLE` | Chart style (`modern`, `corporate`, `minimal`) | `modern` |
| `SURVEY_INCLUDE_CHARTS` | Include charts in PowerPoint export | `true` |

### 3.11 HTML Dashboard Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `SURVEY_HTML_TEMPLATE` | Path to custom HTML template (optional) | *(uses default)* |
| `SURVEY_CHART_LIBRARY` | Chart library (`echarts`, `plotly`, `chartjs`) | `echarts` |

---

## 4. Default Configuration

### 4.1 Complete DEFAULT_CONFIG

Located in `agent/config.py`:

```python
DEFAULT_CONFIG = {
    # ============================================
    # LLM Configuration
    # ============================================
    "model": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 2000,

    # ============================================
    # Three-Node Pattern Configuration
    # ============================================
    "max_self_correction_iterations": 3,
    "enable_human_review": True,

    # ============================================
    # Step 3: Preliminary Filtering
    # ============================================
    "cardinality_threshold": 30,     # Max distinct values before filtering as high-cardinality
    "filter_binary": True,            # Filter out binary variables (exactly 2 distinct values)
    "filter_other_text": True,        # Filter out "other" text fields (open-ended feedback)

    # ============================================
    # PSPP Configuration
    # ============================================
    "pspp_path": "/usr/bin/pspp",
    "pspp_output_path": "output/pspp_logs.txt",

    # ============================================
    # File Paths
    # ============================================
    "output_dir": "output",
    "temp_dir": "temp",

    # ============================================
    # Statistical Analysis
    # ============================================
    "significance_level": 0.05,       # p-value threshold for statistical significance
    "min_cramers_v": 0.1,             # Minimum effect size (Cramer's V)
    "min_cell_count": 10,             # Minimum expected cell count for chi-square

    # ============================================
    # Presentation
    # ============================================
    "powerpoint_template": None,      # Path to custom .pptx template (optional)
    "html_theme": "default"           # HTML dashboard theme
}
```

### 4.2 Configuration Sections

#### LLM Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `model` | string | `"gpt-4"` | OpenAI model to use |
| `temperature` | float | `0.7` | LLM temperature (0.0-1.0) |
| `max_tokens` | int | `2000` | Maximum tokens per LLM response |

#### Three-Node Pattern Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `max_self_correction_iterations` | int | `3` | Max validation retry iterations |
| `enable_human_review` | bool | `True` | Enable human review nodes |

#### Filtering Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `cardinality_threshold` | int | `30` | Max distinct values before filtering |
| `filter_binary` | bool | `True` | Filter binary variables |
| `filter_other_text` | bool | `True` | Filter "other" text fields |

#### Statistical Analysis Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `significance_level` | float | `0.05` | p-value threshold for significance |
| `min_cramers_v` | float | `0.1` | Minimum Cramer's V effect size |
| `min_cell_count` | int | `10` | Minimum expected cell count |

---

## 5. Environment Variables

### 5.1 Required Variables

You must configure at least one LLM provider. Select which provider to use with `SURVEY_LLM_PROVIDER`.

| Variable | Description | Required If |
|----------|-------------|-------------|
| `SURVEY_LLM_PROVIDER` | Selected LLM provider (`KIMI`, `DEEPSEEK`, `ZHIPU`) | Always |
| `KIMI_API_KEY` | Kimi API key | `SURVEY_LLM_PROVIDER=KIMI` |
| `DEEPSEEK_API_KEY` | DeepSeek API key | `SURVEY_LLM_PROVIDER=DEEPSEEK` |
| `ZHIPU_API_KEY` | Zhipu GLM API key | `SURVEY_LLM_PROVIDER=ZHIPU` |

### 5.2 Optional Variables

All optional variables use the `SURVEY_` prefix. See [Section 3](#3-survey-analysis-workflow-configuration) for the complete list.

### 5.3 .env File Example

```bash
# =============================================================================
# Kimi (Moonshot AI)
# =============================================================================
KIMI_API_KEY="sk-lwXxZiXh2wEfGqgJln3zMbiOPAUDxMYBe8iinRU9OYmbvT90"
KIMI_BASE_URL="https://api.moonshot.cn/v1"
KIMI_MODEL="kimi-k2-turbo-preview"

# =============================================================================
# DeepSeek
# =============================================================================
DEEPSEEK_API_KEY="sk-5ac0126d2291484f8c705ca80b2897f4"
DEEPSEEK_BASE_URL="https://api.deepseek.com/v1"
DEEPSEEK_MODEL="deepseek-chat"

# =============================================================================
# Zhipu GLM (BigModel)
# =============================================================================
ZHIPU_API_KEY=cef62fd30a0e4ddf826ccba67b7a1e78.iSRcFQPBKBt4MQ52
ZHIPU_BASE_URL=https://open.bigmodel.cn/api/coding/paas/v4
ZHIPU_MODEL=glm-4.7

# =============================================================================
# Survey Analysis Workflow Configuration
# =============================================================================

# LLM Selection
SURVEY_LLM_PROVIDER=ZHIPU

# LLM Parameters
SURVEY_LLM_TEMPERATURE=0.1
SURVEY_LLM_MAX_TOKENS=4000

# Preliminary Filtering
SURVEY_CARDINALITY_THRESHOLD=30
SURVEY_FILTER_BINARY=true
SURVEY_FILTER_OTHER_TEXT=true

# Recoding Configuration
# SURVEY_RECODING_INSTRUCTIONS="Use standard market research practices"

# Indicator Configuration
# SURVEY_INDICATOR_INSTRUCTIONS="Group semantically related variables"

# Table Specifications
# SURVEY_TABLE_INSTRUCTIONS="Place demographics in columns; identify weighting variable"
# SURVEY_WEIGHTING_VARIABLE="weight"

# Significance Testing
SURVEY_SIGNIFICANCE_ALPHA=0.05
SURVEY_TEST_TYPE=chi_square

# Human Review / Approval
SURVEY_ENABLE_HUMAN_REVIEW=true
SURVEY_AUTO_APPROVE_RECODING=false
SURVEY_AUTO_APPROVE_INDICATORS=false
SURVEY_AUTO_APPROVE_TABLE_SPECS=false
SURVEY_REVIEW_OUTPUT_FORMAT=markdown

# PSPP Configuration
SURVEY_PSPP_PATH=pspp

# Output Configuration
SURVEY_OUTPUT_DIR=output
SURVEY_CREATE_TIMESTAMP_DIR=true

# PowerPoint Configuration
# SURVEY_PPT_TEMPLATE="templates/ppt/default.pptx"
SURVEY_CHART_STYLE=modern
SURVEY_INCLUDE_CHARTS=true

# HTML Dashboard Configuration
# SURVEY_HTML_TEMPLATE="templates/html/dashboard.html"
SURVEY_CHART_LIBRARY=echarts
```

### 5.4 Loading Environment Variables

```python
from dotenv import load_dotenv
import os

load_dotenv()

config = {
    # LLM Provider
    "llm_provider": os.getenv("SURVEY_LLM_PROVIDER", "ZHIPU"),
    "model": os.getenv("ZHIPU_MODEL", "glm-4.7"),
    "temperature": float(os.getenv("SURVEY_LLM_TEMPERATURE", "0.1")),
    "max_tokens": int(os.getenv("SURVEY_LLM_MAX_TOKENS", "4000")),

    # Filtering
    "cardinality_threshold": int(os.getenv("SURVEY_CARDINALITY_THRESHOLD", "30")),
    "filter_binary": os.getenv("SURVEY_FILTER_BINARY", "true").lower() == "true",
    "filter_other_text": os.getenv("SURVEY_FILTER_OTHER_TEXT", "true").lower() == "true",

    # Human Review
    "enable_human_review": os.getenv("SURVEY_ENABLE_HUMAN_REVIEW", "true").lower() == "true",
    "auto_approve_recoding": os.getenv("SURVEY_AUTO_APPROVE_RECODING", "false").lower() == "true",
    "auto_approve_indicators": os.getenv("SURVEY_AUTO_APPROVE_INDICATORS", "false").lower() == "true",
    "auto_approve_table_specs": os.getenv("SURVEY_AUTO_APPROVE_TABLE_SPECS", "false").lower() == "true",

    # PSPP
    "pspp_path": os.getenv("SURVEY_PSPP_PATH", "pspp"),

    # Output
    "output_dir": os.getenv("SURVEY_OUTPUT_DIR", "output"),
    "create_timestamp_dir": os.getenv("SURVEY_CREATE_TIMESTAMP_DIR", "true").lower() == "true",
}
```

---

## 6. LangGraph Configuration

### 6.1 langgraph.json Structure

Located at `config/langgraph.json`:

```json
{
  "graphs": {
    "survey_analysis": {
      "nodes": {
        "extract_spss": "agent.nodes.phase1_extraction:extract_spss_node",
        "transform_metadata": "agent.nodes.phase1_extraction:transform_metadata_node",
        "filter_metadata": "agent.nodes.phase1_extraction:filter_metadata_node",
        "generate_recoding_rules": "agent.nodes.phase2_recoding:generate_recoding_rules_node",
        "validate_recoding_rules": "agent.nodes.phase2_recoding:validate_recoding_rules_node",
        "review_recoding_rules": "agent.nodes.phase2_recoding:review_recoding_rules_node",
        "generate_pspp_recoding_syntax": "agent.nodes.phase2_recoding:generate_pspp_recoding_syntax_node",
        "execute_pspp_recoding": "agent.nodes.phase2_recoding:execute_pspp_recoding_node",
        "generate_indicators": "agent.nodes.phase3_indicators:generate_indicators_node",
        "validate_indicators": "agent.nodes.phase3_indicators:validate_indicators_node",
        "review_indicators": "agent.nodes.phase3_indicators:review_indicators_node",
        "generate_table_specifications": "agent.nodes.phase4_tables:generate_table_specifications_node",
        "validate_table_specifications": "agent.nodes.phase4_tables:validate_table_specifications_node",
        "review_table_specifications": "agent.nodes.phase4_tables:review_table_specifications_node",
        "generate_pspp_table_syntax": "agent.nodes.phase4_tables:generate_pspp_table_syntax_node",
        "execute_pspp_tables": "agent.nodes.phase4_tables:execute_pspp_tables_node",
        "generate_python_statistics_script": "agent.nodes.phase5_statistics:generate_python_statistics_script_node",
        "execute_python_statistics_script": "agent.nodes.phase5_statistics:execute_python_statistics_script_node",
        "generate_filter_list": "agent.nodes.phase6_filtering:generate_filter_list_node",
        "apply_filter_to_tables": "agent.nodes.phase6_filtering:apply_filter_to_tables_node",
        "generate_powerpoint": "agent.nodes.phase7_powerpoint:generate_powerpoint_node",
        "generate_html_dashboard": "agent.nodes.phase8_html_dashboard:generate_html_dashboard_node"
      },
      "edges": {
        "extract_spss": "transform_metadata",
        "transform_metadata": "filter_metadata",
        "filter_metadata": "generate_recoding_rules"
      },
      "conditional_edges": {
        "validate_recoding_rules": "agent.edges:should_retry_recoding",
        "review_recoding_rules": "agent.edges:should_approve_recoding",
        "validate_indicators": "agent.edges:should_retry_indicators",
        "review_indicators": "agent.edges:should_approve_indicators",
        "validate_table_specifications": "agent.edges:should_retry_table_specs",
        "review_table_specifications": "agent.edges:should_approve_table_specs"
      }
    }
  }
}
```

### 6.2 Node Path Format

```
agent.nodes.{phase_file}:{node_function}
```

Examples:
- `agent.nodes.phase1_extraction:extract_spss_node`
- `agent.nodes.phase2_recoding:generate_recoding_rules_node`

---

## 7. Usage Examples

### 7.1 Custom Filtering Rules

```python
config = DEFAULT_CONFIG.copy()
config["cardinality_threshold"] = 50  # Filter fewer variables
config["filter_binary"] = False       # Keep binary variables
config["filter_other_text"] = False   # Keep "other" fields
```

### 7.2 Adjust Statistical Thresholds

```python
config = DEFAULT_CONFIG.copy()
config["significance_level"] = 0.01    # More strict (p < 0.01)
config["min_cramers_v"] = 0.2          # Larger effect size required
config["min_cell_count"] = 20          # Larger sample size required
```

### 7.3 Automatic Mode (No Human Review)

```python
config = DEFAULT_CONFIG.copy()
config["enable_human_review"] = False
```

**Use when**: Testing, batch processing, trusted surveys.

### 7.4 Apply Configuration via Environment Variables

```bash
# In .env file
SURVEY_LLM_PROVIDER=DEEPSEEK
SURVEY_ENABLE_HUMAN_REVIEW=false
SURVEY_AUTO_APPROVE_RECODING=true
SURVEY_AUTO_APPROVE_INDICATORS=true
SURVEY_AUTO_APPROVE_TABLE_SPECS=true
```

### 7.5 Apply Configuration via Command Line

```bash
# Basic analysis with default config
python -m agent.graph --input data/input/survey.sav

# Custom output directory
python -m agent.graph --input data/input/survey.sav --output-dir results/

# Disable human review (for testing)
python -m agent.graph --input data/input/survey.sav --no-human-review

# Resume from checkpoint
python -m agent.graph --thread-id survey_001 --resume
```

---

## Related Documents

- **[Deployment](./deployment.md)** - Installation, environment configuration, and operations
- **[Web Interface](./web-interface.md)** - Agent Chat UI setup and usage
- **[Project Structure](./project-structure.md)** - Complete directory structure, file paths, and output locations
- **[Data Flow](./data-flow.md)** - Workflow design and steps
- **[System Architecture](./system-architecture.md)** - System components and architecture
- **[Technology Stack](./technology-stack.md)** - Technologies and versions
- **[Product Features and Usage](./features-and-usage.md)** - Product introduction for end users
- **[Implementation Specifications](./implementation-specifications.md)** - Technical implementation details
