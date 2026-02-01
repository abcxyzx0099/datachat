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

The application supports multiple LLM providers. Select your preferred provider using the `LLM_PROVIDER` environment variable.

### 2.1 Supported Providers

| Provider | `LLM_PROVIDER` Value | Base URL |
|----------|----------------------------|----------|
| **Kimi (Moonshot AI)** | `KIMI` | `https://api.moonshot.cn/v1` |
| **DeepSeek** | `DEEPSEEK` | `https://api.deepseek.com/v1` |
| **Zhipu GLM (BigModel)** | `ZHIPU` | `https://open.bigmodel.cn/api/coding/paas/v4` |

### 2.2 Provider-Specific Configuration

#### Kimi (Moonshot AI)

| Variable | Description | Example |
|----------|-------------|---------|
| `KIMI_API_KEY` | API key for Kimi | `your-kimi-api-key-here` |
| `KIMI_BASE_URL` | Base URL for Kimi API | `https://api.moonshot.cn/v1` |
| `KIMI_MODEL` | Model to use | `kimi-k2-turbo-preview` |

#### DeepSeek

| Variable | Description | Example |
|----------|-------------|---------|
| `DEEPSEEK_API_KEY` | API key for DeepSeek | `your-deepseek-api-key-here` |
| `DEEPSEEK_BASE_URL` | Base URL for DeepSeek API | `https://api.deepseek.com/v1` |
| `DEEPSEEK_MODEL` | Model to use (`deepseek-chat` or `deepseek-reasoner`) | `deepseek-chat` |

#### Zhipu GLM (BigModel)

| Variable | Description | Example |
|----------|-------------|---------|
| `ZHIPU_API_KEY` | API key for Zhipu GLM | `your-zhipu-api-key-here` |
| `ZHIPU_BASE_URL` | Base URL for Zhipu GLM API | `https://open.bigmodel.cn/api/coding/paas/v4` |
| `ZHIPU_MODEL` | Model to use | `glm-4.7` |

### 2.3 Provider Selection

```bash
# In .env file
LLM_PROVIDER=ZHIPU  # Options: KIMI, DEEPSEEK, ZHIPU
```

---

## 3. Survey Analysis Workflow Configuration

All survey analysis configuration options are specified as environment variables.

### 3.1 LLM Parameters

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_PROVIDER` | LLM provider (`KIMI`, `DEEPSEEK`, `ZHIPU`) | `ZHIPU` |
| `LLM_TEMPERATURE` | Temperature for LLM responses (0.0-1.0) | `0.1` |
| `LLM_MAX_TOKENS` | Maximum tokens per LLM response | `4000` |

### 3.2 Preliminary Filtering

| Variable | Description | Default |
|----------|-------------|---------|
| `CARDINALITY_THRESHOLD` | Max distinct values before filtering as high-cardinality | `30` |
| `FILTER_BINARY` | Filter out binary variables (exactly 2 distinct values) | `true` |
| `FILTER_OTHER_TEXT` | Filter out "other" text fields (open-ended feedback) | `true` |

### 3.3 Recoding Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `RECODING_INSTRUCTIONS` | Custom instructions for AI recoding (optional) | *(uses default)* |
| `AUTO_APPROVE_RECODING` | Skip human review for recoding rules | `false` |

### 3.4 Indicator Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `INDICATOR_INSTRUCTIONS` | Custom instructions for AI indicator grouping (optional) | *(uses default)* |
| `AUTO_APPROVE_INDICATORS` | Skip human review for indicators | `false` |

### 3.5 Table Specifications

| Variable | Description | Default |
|----------|-------------|---------|
| `TABLE_INSTRUCTIONS` | Custom instructions for table generation (optional) | *(uses default)* |
| `WEIGHTING_VARIABLE` | Weighting variable name (empty for auto-detection) | *(auto-detect)* |
| `AUTO_APPROVE_TABLE_SPECS` | Skip human review for table specifications | `false` |

### 3.6 Significance Testing

| Variable | Description | Default |
|----------|-------------|---------|
| `SIGNIFICANCE_ALPHA` | p-value threshold for statistical significance | `0.05` |
| `TEST_TYPE` | Statistical test type (`chi_square`, `fisher_exact`) | `chi_square` |

### 3.7 Human Review / Approval

| Variable | Description | Default |
|----------|-------------|---------|
| `ENABLE_HUMAN_REVIEW` | Enable human-in-the-loop review | `true` |
| `REVIEW_OUTPUT_FORMAT` | Review report format (`markdown`, `html`, `json`) | `markdown` |

### 3.8 PSPP Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `PSPP_PATH` | Path to PSPP executable | `pspp` |

### 3.9 Output Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `OUTPUT_DIR` | Output directory (relative to project root) | `output` |
| `CREATE_TIMESTAMP_DIR` | Create timestamped subdirectories | `true` |

### 3.10 PowerPoint Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `PPT_TEMPLATE` | Path to custom .pptx template (optional) | *(uses default)* |
| `CHART_STYLE` | Chart style (`modern`, `corporate`, `minimal`) | `modern` |
| `INCLUDE_CHARTS` | Include charts in PowerPoint export | `true` |

### 3.11 HTML Dashboard Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `HTML_TEMPLATE` | Path to custom HTML template (optional) | *(uses default)* |
| `CHART_LIBRARY` | Chart library (`echarts`, `plotly`, `chartjs`) | `echarts` |

---

## 4. Default Configuration

### 4.1 Complete DEFAULT_CONFIG

Located in `agent/config.py`:

```python
DEFAULT_CONFIG = {
    # ============================================
    # LLM Configuration
    # ============================================
    # LLM Provider Selection: KIMI | DEEPSEEK | ZHIPU
    "llm_provider": "ZHIPU",
    # Provider-specific model (e.g., glm-4.7 for Zhipu)
    "model": "glm-4.7",
    "temperature": 0.1,
    "max_tokens": 4000,

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
| `llm_provider` | string | `"ZHIPU"` | LLM provider (`KIMI`, `DEEPSEEK`, or `ZHIPU`) |
| `model` | string | `"glm-4.7"` | Model to use (provider-specific) |
| `temperature` | float | `0.1` | LLM temperature (0.0-1.0) |
| `max_tokens` | int | `4000` | Maximum tokens per LLM response |

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

You must configure at least one LLM provider. Select which provider to use with `LLM_PROVIDER`.

| Variable | Description | Required If |
|----------|-------------|-------------|
| `LLM_PROVIDER` | Selected LLM provider (`KIMI`, `DEEPSEEK`, `ZHIPU`) | Always |
| `KIMI_API_KEY` | Kimi API key | `LLM_PROVIDER=KIMI` |
| `DEEPSEEK_API_KEY` | DeepSeek API key | `LLM_PROVIDER=DEEPSEEK` |
| `ZHIPU_API_KEY` | Zhipu GLM API key | `LLM_PROVIDER=ZHIPU` |

### 5.2 Optional Variables

See [Section 3](#3-survey-analysis-workflow-configuration) for the complete list of optional configuration variables.

### 5.3 .env File Example

```bash
# =============================================================================
# Kimi (Moonshot AI)
# =============================================================================
KIMI_API_KEY="your-kimi-api-key-here"
KIMI_BASE_URL="https://api.moonshot.cn/v1"
KIMI_MODEL="kimi-k2-turbo-preview"

# =============================================================================
# DeepSeek
# =============================================================================
DEEPSEEK_API_KEY="your-deepseek-api-key-here"
DEEPSEEK_BASE_URL="https://api.deepseek.com/v1"
DEEPSEEK_MODEL="deepseek-chat"

# =============================================================================
# Zhipu GLM (BigModel)
# =============================================================================
ZHIPU_API_KEY=your-zhipu-api-key-here
ZHIPU_BASE_URL=https://open.bigmodel.cn/api/coding/paas/v4
ZHIPU_MODEL=glm-4.7

# =============================================================================
# Survey Analysis Workflow Configuration
# =============================================================================

# LLM Selection
LLM_PROVIDER=ZHIPU

# LLM Parameters
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=4000

# Preliminary Filtering
CARDINALITY_THRESHOLD=30
FILTER_BINARY=true
FILTER_OTHER_TEXT=true

# Recoding Configuration
# RECODING_INSTRUCTIONS="Use standard market research practices"

# Indicator Configuration
# INDICATOR_INSTRUCTIONS="Group semantically related variables"

# Table Specifications
# TABLE_INSTRUCTIONS="Place demographics in columns; identify weighting variable"
# WEIGHTING_VARIABLE="weight"

# Significance Testing
SIGNIFICANCE_ALPHA=0.05
TEST_TYPE=chi_square

# Human Review / Approval
ENABLE_HUMAN_REVIEW=true
AUTO_APPROVE_RECODING=false
AUTO_APPROVE_INDICATORS=false
AUTO_APPROVE_TABLE_SPECS=false
REVIEW_OUTPUT_FORMAT=markdown

# PSPP Configuration
PSPP_PATH=pspp

# Output Configuration
OUTPUT_DIR=output
CREATE_TIMESTAMP_DIR=true

# PowerPoint Configuration
# PPT_TEMPLATE="templates/ppt/default.pptx"
CHART_STYLE=modern
INCLUDE_CHARTS=true

# HTML Dashboard Configuration
# HTML_TEMPLATE="templates/html/dashboard.html"
CHART_LIBRARY=echarts
```

### 5.4 Loading Environment Variables

```python
from dotenv import load_dotenv
import os

load_dotenv()

# Step 1: Determine which LLM provider to use
llm_provider = os.getenv("LLM_PROVIDER", "ZHIPU")

# Step 2: Load provider-specific API key based on selected provider
# The .env file should contain API keys for all providers,
# but only the selected provider's key will be used.
if llm_provider == "KIMI":
    api_key = os.getenv("KIMI_API_KEY")
    base_url = os.getenv("KIMI_BASE_URL", "https://api.moonshot.cn/v1")
    model = os.getenv("KIMI_MODEL", "kimi-k2-turbo-preview")
elif llm_provider == "DEEPSEEK":
    api_key = os.getenv("DEEPSEEK_API_KEY")
    base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
    model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
elif llm_provider == "ZHIPU":
    api_key = os.getenv("ZHIPU_API_KEY")
    base_url = os.getenv("ZHIPU_BASE_URL", "https://open.bigmodel.cn/api/coding/paas/v4")
    model = os.getenv("ZHIPU_MODEL", "glm-4.7")
else:
    raise ValueError(f"Unsupported LLM provider: {llm_provider}")

# Step 3: Load remaining configuration
config = {
    # LLM Provider (with provider-specific values)
    "llm_provider": llm_provider,
    "api_key": api_key,
    "base_url": base_url,
    "model": model,
    "temperature": float(os.getenv("LLM_TEMPERATURE", "0.1")),
    "max_tokens": int(os.getenv("LLM_MAX_TOKENS", "4000")),

    # Filtering
    "cardinality_threshold": int(os.getenv("CARDINALITY_THRESHOLD", "30")),
    "filter_binary": os.getenv("FILTER_BINARY", "true").lower() == "true",
    "filter_other_text": os.getenv("FILTER_OTHER_TEXT", "true").lower() == "true",

    # Human Review
    "enable_human_review": os.getenv("ENABLE_HUMAN_REVIEW", "true").lower() == "true",
    "auto_approve_recoding": os.getenv("AUTO_APPROVE_RECODING", "false").lower() == "true",
    "auto_approve_indicators": os.getenv("AUTO_APPROVE_INDICATORS", "false").lower() == "true",
    "auto_approve_table_specs": os.getenv("AUTO_APPROVE_TABLE_SPECS", "false").lower() == "true",

    # PSPP
    "pspp_path": os.getenv("PSPP_PATH", "pspp"),

    # Output
    "output_dir": os.getenv("OUTPUT_DIR", "output"),
    "create_timestamp_dir": os.getenv("CREATE_TIMESTAMP_DIR", "true").lower() == "true",
}
```

**Note**: The `.env` file should contain API keys for all providers (`KIMI_API_KEY`, `DEEPSEEK_API_KEY`, `ZHIPU_API_KEY`), but only the API key corresponding to `LLM_PROVIDER` will be loaded and used at runtime. This allows you to switch providers by changing only the `LLM_PROVIDER` value.

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
LLM_PROVIDER=DEEPSEEK
ENABLE_HUMAN_REVIEW=false
AUTO_APPROVE_RECODING=true
AUTO_APPROVE_INDICATORS=true
AUTO_APPROVE_TABLE_SPECS=true
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
